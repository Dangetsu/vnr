# coding: utf8
# gameview.py
# 7/10/2013 jichi

__all__ = 'GameViewManager',

import json, os
from functools import partial
from PySide.QtCore import Qt, Slot, QObject
from Qt5 import QtWidgets
from sakurakit import skdatetime, skevents, skthreads, skqss
from sakurakit.skclass import Q_Q, memoized, memoizedproperty
from sakurakit.skdebug import dprint, dwarn
from sakurakit.sktr import tr_
from sakurakit.skwebkit import SkWebView, SkWebViewBean
from sakurakit.skwidgets import SkTitlelessDockWidget, SkStyleView, shortcut
#from sakurakit.skqml import QmlObject
from mytr import my, mytr_
import cacheman, config, dataman, defs, features, growl, i18n, jsonutil, main, netman, osutil, prompt, proxy, py, rc

def _getimage(url, path):
  """
  @param  url  str
  @param  location  unicode
  """
  dprint(url)
  if url.startswith('file:///'):
    url = url.replace('file:///', '')
    import shutil
    try: shutil.copy(url, path)
    except Exception, e: dwarn(e)
  else:
    noredirects = url.startswith("http://pics.dmm.co.jp/") #or url.startswith("http://media.erogetrailers.com/img/")
    from sakurakit import sknetio
    #skthreads.runasync(partial(sknetio.getfile, url, path))
    sknetio.getfile(url, path,
        allow_redirects=not noredirects,
        mimefilter=sknetio.IMAGE_MIME_FILTER)

def _getimages(l, path=None):
  """
  @param  l  [(url, path)]
  @param* path  unicode
  """
  for args in l:
    _getimage(*args)
  if path:
    osutil.open_location(path)

class GameCoffeeBean(QObject):
  def __init__(self, parent=None, info=None):
    super(GameCoffeeBean, self).__init__(parent)
    self.info = info # GameItemInfo or None

  # Queries

  @Slot(result=unicode)
  def getTwitterWidgets(self): # return list of long using ',' as sep
    if self.info and self.info.hasTwitterWidgets():
      return ','.join((str(id) for id in self.info.iterTwitterWidgets()))
    else:
      return ''

  @Slot(result=unicode)
  def getVideos(self): # return json list
    if self.info and self.info.hasVideos():
      return json.dumps(list(self.info.iterVideos()))
    else:
      return ''

  @Slot(unicode, result=unicode)
  def getDescription(self, type): # return html for the reference type
    if self.info:
      for r in self.info.iterDescriptionReferences():
        if r.type == type:
          return ''.join(r.iterDescriptions())
    return ''

  @Slot(unicode, result=unicode)
  def getCharacterDescription(self, type): # return html for the reference type
    if self.info:
      for r in self.info.iterCharacterDescriptionReferences():
        if r.type == type:
          return r.renderCharacterDescription()
    return ''

  @Slot(unicode, result=unicode)
  def getReview(self, type): # return html for the reference type
    if type != 'scape' and self.info:
      for r in self.info.iterReviewReferences():
        if r.type == type:
          return r.renderReview()
    return ''

  @Slot(int, int, result=unicode)
  def getScapeReviews(self, offset, limit): # return json list
    if self.info and self.info.scape:
      l = self.info.scape.queryReviews(offset=offset, limit=limit)
      if l:
        return json.dumps(l, default=jsonutil.default_datetime)
    return ''

  #@Slot(result=unicode)
  #def getSampleImages(self): # return list of urls using ',' as sep
  #  if self.info and self.info.hasSampleImages():
  #    return ','.join(self.info.iterSampleImageUrls())
  #  else:
  #    return ''

  @Slot(unicode, result=unicode)
  def getSampleImages(self, type): # return urls for the reference type
    if self.info:
      for r in self.info.iterSampleImageReferences():
        if r.type == type:
          return ','.join(r.iterSampleImageUrls())
    return ''

  #@Slot(unicode, result=unicode)
  #def getCharacters(self, type): # return json for the reference type
  #  if self.info and self.info.hasCharacters():
  #    for r in self.info.iterCharacterReferences():
  #      if r.type == type:
  #        return json.dumps(r.characters)
  #  return ''

  # Actions

  @Slot()
  def saveVideos(self): # prompt and save all youtube videos to the desktop
    if not self.info or not self.info.hasVideos():
      growl.warn(my.tr("Please try updating game database first"))
    elif prompt.confirmDownloadGameVideos():
      growl.msg(my.tr("Downloading YouTube videos") + " ...")
      from sakurakit import skfileio, skpaths
      name = u"%s (動画)" % skfileio.escape(self.info.title)
      path = os.path.join(skpaths.DESKTOP, name)
      videos = list(self.info.iterVideoIds())

      import procutil
      procutil.getyoutube(videos, path=path)

  @Slot()
  def saveImages(self): # prompt and save all images to the desktop
    if not self.info:
      growl.warn(my.tr("Please try updating game database first"))
    elif prompt.confirmDownloadGameImages():
      growl.msg(my.tr("Saving game images") + " ...")
      from sakurakit import skfileio, skpaths
      name = u"%s (画像)" % skfileio.escape(self.info.title)
      path = os.path.join(skpaths.DESKTOP, name)
      try:
        skfileio.makedirs(path)
        images = [(url, os.path.join(path, name + '.jpg'))
            for url,name in self.info.iterImageUrlsWithName()]
        skthreads.runasync(partial(_getimages, images, path=path))
      except Exception, e:
        growl.warn(my.tr("Failed to save all images"))
        dwarn(e)

  # Static actions

  #@staticmethod
  @Slot(unicode)
  def search(_, text):
    if text:
      main.manager().searchGameBoard(text)

  @Slot(unicode, bool, result=unicode)
  def getYouTubeImageUrl(_, vid, large): # -> url
    ret = cacheman.cache_image_url(proxy.make_ytimg_url(vid, large=large))
    if not ret and large:
      ret = cacheman.cache_image_url(proxy.make_ytimg_url(vid, large=False))
    return ret

@Q_Q
class _GameView(object):

  def __init__(self, q):
    self.clear()
    self._locked = False

    self._gameBean = GameCoffeeBean(parent=q)
    self._viewBean = SkWebViewBean(self.webView)

    self._createUi(q)

    shortcut('alt+e', self._edit, parent=q)

  def _createUi(self, q):
    q.setCentralWidget(self.webView)

    dock = SkTitlelessDockWidget(self.inspector)
    dock.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
    #dock.setAllowedAreas(Qt.BottomDockWidgetArea)
    q.addDockWidget(Qt.BottomDockWidgetArea, dock)

  def clear(self):
    self.gameInfo = None # gameInfo
    self.gameId = 0 # long
    self.itemId = 0 # long

  def _injectBeans(self):
    h = self.webView.page().mainFrame()
    #h.addToJavaScriptWindowObject('bean', self._webBean)
    for name,obj in self._beans:
      h.addToJavaScriptWindowObject(name, obj)

  @memoizedproperty
  def _beans(self):
    """
    return  [(unicode name, QObject bean)]
    """
    import coffeebean
    m = coffeebean.manager()
    return (
      ('cacheBean', m.cacheBean),
      ('clipBean', m.clipBean),
      ('i18nBean', m.i18nBean),
      ('mainBean', m.mainBean),
      #('jlpBean', m.jlpBean), # temporarily disabled
      ('trBean', m.trBean),
      ('ttsBean', m.ttsBean),
      ('viewBean', self._viewBean),
      ('youtubeBean', m.youtubeBean),

      ('gameBean', self._gameBean), # do it at last

      #('shioriBean', m.shioriBean), # temporarily not used
    )

  @memoizedproperty
  def webView(self):
    from PySide.QtWebKit import QWebPage
    ret = SkWebView()
    #ret.titleChanged.connect(self.q.setWindowTitle)
    ret.enableHighlight() # highlight selected text
    ret.ignoreSslErrors() # needed to access Twitter

    ret.pageAction(QWebPage.Reload).triggered.connect(
        self.updateAndRefresh, Qt.QueuedConnection)

    ret.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks) # Since there are local images
    #ret.page().setLinkDelegationPolicy(QWebPage.DelegateExternalLinks)
    ret.linkClicked.connect(osutil.open_url)
    return ret

  def updateAndRefresh(self):
    if self._locked:
      dwarn("locked")
      return
    gameId = self.gameId
    if not gameId:
      #growl.notify(my.tr("Unknown game. Please try updating the database."))
      return

    if netman.manager().isOnline():
      if self.itemId and self.itemId < defs.MIN_NORMAL_GAME_ITEM_ID:
        dprint("found non-normal game, ignore refs")
      else:
        self._locked = True # lock before online access
        #growl.msg(my.tr("Updating game information"))
        ok = dataman.manager().updateReferences(gameId)
        #dm.touchGames()
        if not ok:
          growl.notify(my.tr("The game title it not specified. You can click the Edit button to add one."))
        #else:
          #growl.msg(my.tr("Found game information"))

    self._locked = False # always unlock no matter what happened

    self.refresh()
    #skevents.runlater(partial(
    #    dm.updateReferences, g.id),
    #    200)

  def refresh(self):
    """@reimp"""
    q = self.q
    dm = dataman.manager()
    info = self.gameInfo = dm.queryGameInfo(itemId=self.itemId, id=self.gameId, cache=False)
    self._gameBean.info = info
    if info:
      if not self.gameId:
        self.gameId = info.gameId
      if not self.itemId:
        self.itemId = info.itemId

    title = info.title if info else ""
    if not title and self.gameId:
      title = dm.queryGameName(id=self.gameId)

    t = title or tr_("Game")
    if info and info.itemId:
      t += " #%s" % info.itemId
    if info:
      if info.upcoming:
        t += u" (未発売)"
      elif info.recent:
        t += u" (新作)"
    q.setWindowTitle(t)

    icon = info.icon if info else None
    q.setWindowIcon(icon or rc.icon('window-gameview'))

    online = netman.manager().isOnline()
    self.editButton.setEnabled(bool(self.gameId))
    self.launchButton.setEnabled(bool(info and info.local))
    self.browseButton.setEnabled(online and bool(info and info.itemId))
    self.topicButton.setEnabled(online and bool(info and info.itemId))
    self.nameButton.setEnabled(bool(info) and info.hasCharacters())

    # Fake base addr that twitter javascript can access document.cookie
    #baseUrl = ''
    #baseUrl = "http://localhost:6100"
    #baseUrl = "http://www.amazon.co.jp" # cross domain so that amazon iframe works
    #baseUrl = 'qrc://'     # would crash QByteArray when refresh
    #baseUrl = 'qrc://any'  # would crash QByteArray when refresh
    #baseUrl = 'file:///'    # would crash QByteArray when refresh
    #baseUrl = 'file:///any' # any place that is local
    needsPost = info and info.gameItem and (info.gameItem.overallScoreCount or info.gameItem.ecchiScoreCount)
    if online and needsPost:
      baseUrl = config.API_HOST # must be the same as rest.coffee for the same origin policy, but this would break getchu
    else:
      baseUrl = 'qrc:///_'    # any place is fine

    user = dataman.manager().user()

    w = self.webView
    w.setHtml(rc.haml_template('haml/reader/gameview').render({
      'host': config.API_HOST,
      'userName': user.name,
      'userPassword': user.password,
      'title': title,
      'game': info,
      'cache': cacheman.CacheJinjaUtil,
      'rc': rc,
      'py': py,
      'tr': tr_,
      'i18n': i18n,
      #'jlp': mecabman.manager(), # temporarily disabled
      #'settings', settings.global_(),
      'online': online,
      'proxy': proxy.manager(),
      'mainland': features.MAINLAND_CHINA,
    }), baseUrl)

    self._injectBeans()

  @memoizedproperty
  def inspector(self):
    ret = SkStyleView()
    skqss.class_(ret, 'texture')
    layout = QtWidgets.QHBoxLayout()
    layout.addWidget(self.launchButton)
    layout.addWidget(self.subButton)
    layout.addWidget(self.topicButton)
    layout.addWidget(self.nameButton)
    layout.addStretch()
    layout.addWidget(self.helpButton)
    layout.addWidget(self.browseButton)
    layout.addWidget(self.editButton)
    layout.addWidget(self.refreshButton) # disabled
    ret.setLayout(layout)
    layout.setContentsMargins(4, 4, 4, 4)
    return ret

  @memoizedproperty
  def launchButton(self):
    ret = QtWidgets.QPushButton(tr_("Launch"))
    skqss.class_(ret, 'btn btn-primary')
    ret.setToolTip(tr_("Launch"))
    #ret.setStatusTip(ret.toolTip())
    ret.setEnabled(False)
    ret.clicked.connect(lambda:
        main.manager().openGame(gameId=self.gameId))
    return ret

  @memoizedproperty
  def browseButton(self):
    ret = QtWidgets.QPushButton(tr_("Browse"))
    skqss.class_(ret, 'btn btn-default')
    ret.setToolTip(tr_("Browse"))
    #ret.setStatusTip(ret.toolTip())
    ret.setEnabled(False)
    ret.clicked.connect(lambda:
        self.itemId and osutil.open_url("http://sakuradite.com/game/%s" % self.itemId))
    return ret

  @memoizedproperty
  def topicButton(self):
    ret = QtWidgets.QPushButton(tr_("Topic"))
    skqss.class_(ret, 'btn btn-inverse')
    ret.setToolTip(tr_("Topic"))
    ret.setEnabled(False)
    ret.clicked.connect(lambda:
        self.itemId and main.manager().showGameTopics(itemId=self.itemId))
    return ret

  @memoizedproperty
  def subButton(self):
    ret = QtWidgets.QPushButton(tr_("Subtitle"))
    skqss.class_(ret, 'btn btn-success')
    ret.setToolTip(tr_("Subtitles"))
    #ret.setStatusTip(ret.toolTip())
    #ret.setEnabled(False)
    ret.clicked.connect(lambda:
        main.manager().showSubtitleView(gameId=self.gameId))
    return ret

  @memoizedproperty
  def editButton(self):
    ret = QtWidgets.QPushButton(tr_("Edit"))
    skqss.class_(ret, 'btn btn-success')
    ret.setToolTip(tr_("Edit") + " (Alt+E)")
    ret.setEnabled(False)
    #ret.setStatusTip(ret.toolTip())
    ret.clicked.connect(self._edit)
    return ret

  def _edit(self): main.manager().showReferenceView(gameId=self.gameId)

  @memoizedproperty
  def nameButton(self):
    ret = QtWidgets.QPushButton(my.tr("Import Name"))
    #skqss.class_(ret, 'btn btn-inverse')
    skqss.class_(ret, 'btn btn-warning')
    ret.setToolTip(my.tr("Import Japanese names to Shared Dictionary"))
    ret.setEnabled(False)
    #ret.setStatusTip(ret.toolTip())
    ret.clicked.connect(self._importName)
    return ret

  def _importName(self):
    if self.gameInfo:
      main.manager().showGameNames(tokenId=self.gameId, itemId=self.itemId, info=self.gameInfo)

  @memoizedproperty
  def refreshButton(self):
    ret = QtWidgets.QPushButton(tr_("Refresh"))
    skqss.class_(ret, 'btn btn-primary')
    ret.setToolTip(tr_("Refresh") + " (Ctrl+R)")
    #ret.setStatusTip(ret.toolTip())
    ret.clicked.connect(self.updateAndRefresh)
    nm = netman.manager()
    ret.setEnabled(nm.isOnline())
    nm.onlineChanged.connect(ret.setEnabled)
    return ret

  @memoizedproperty
  def helpButton(self):
    ret = QtWidgets.QPushButton(tr_("Help"))
    skqss.class_(ret, 'btn btn-default')
    ret.setToolTip(tr_("Help"))
    #ret.setStatusTip(ret.toolTip())
    ret.clicked.connect(main.manager().showReferenceHelp)
    return ret

class GameView(QtWidgets.QMainWindow):
  def __init__(self, parent=None):
    WINDOW_FLAGS = Qt.Dialog|Qt.WindowMinMaxButtonsHint
    super(GameView, self).__init__(parent, WINDOW_FLAGS)
    #self.setWindowIcon(rc.icon('window-game'))
    self.__d = _GameView(self)

  def refresh(self): self.__d.refresh()
  def clear(self): self.__d.clear()

  def itemId(self): return self.__d.itemId
  def setItemId(self, itemId): self.__d.itemId = itemId

  def gameId(self): return self.__d.gameId
  def setGameId(self, gameId): self.__d.gameId = gameId

  def setVisible(self, value):
    """@reimp @public"""
    d = self.__d
    if value and not self.isVisible():
      d.refresh()
      gameId = d.gameId
      if gameId and netman.manager().isOnline():
        g = dataman.manager().queryGame(id=gameId)
        #if not g:
        #  skevents.runlater(d.updateAndRefresh, 2000) # 2 seconds
        #else:
        if g:
          t = g.refsUpdateTime
          now = skdatetime.current_unixtime()
          if t + config.APP_UPDATE_REFS_INTERVAL < now:
            g.refsUpdateTime = now
            skevents.runlater(d.updateAndRefresh, 2000) # 2 seconds
    super(GameView, self).setVisible(value)
    if not value:
      d.webView.clear()

class _GameViewManager:
  def __init__(self):
    self.dialogs = []

  def _createDialog(self):
    import windows
    parent = windows.normal()
    ret = GameView(parent=parent)
    ret.resize(550, 580)
    return ret

  def getDialog(self, gameId=0, itemId=0):
    """
    @param* itemId  long
    @param* gameId  long
    """
    if gameId or itemId:
      for w in self.dialogs:
        if w.isVisible() and (itemId and itemId == w.itemId() or gameId == w.gameId()):
          return w
    for w in self.dialogs:
      if not w.isVisible():
        return w
    ret = self._createDialog()
    self.dialogs.append(ret)
    return ret

class GameViewManager:
  def __init__(self):
    self.__d = _GameViewManager()

  #def clear(self): self.hide()

  def hide(self):
    if self.__d.dialogs:
      for w in self.__d.dialogs:
        if w.isVisible():
          w.hide()

  def showGame(self, gameId):
    """
    @param  gameId  long
    """
    if not gameId:
      growl.notify(my.tr("Unknown game. Please try updating the database."))
    else:
      w = self.__d.getDialog(gameId=gameId)
      if w.gameId() == gameId:
        w.refresh()
      else:
        w.clear()
        w.setGameId(gameId)
      w.show()
      w.raise_()

  def showItem(self, itemId):
    """
    @param  itemId  long
    """
    if not itemId:
      growl.notify(my.tr("Unknown game. Please try updating the database."))
    else:
      w = self.__d.getDialog(itemId=itemId)
      if w.itemId() == itemId:
        w.refresh()
      else:
        w.clear()
        w.setItemId(itemId)
      w.show()
      w.raise_()

@memoized
def manager():
  import webrc
  webrc.init()
  return GameViewManager()

# Disabled to reduce the number of qml plugins
#@QmlObject
#class GameViewManagerProxy(QObject):
#  def __init__(self, parent=None):
#    super(GameViewManagerProxy, self).__init__(parent)
#
#  @Slot(int)
#  def showGame(self, id):
#    manager().showGame(id)

# EOF
