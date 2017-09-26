# coding: utf8
# topicsview.py
# 8/27/2014 jichi

if __name__ == '__main__':
  import sys
  sys.path.append('..')
  import debug
  debug.initenv()

import json
from functools import partial
from PySide.QtCore import Qt, QObject
from Qt5 import QtWidgets
from sakurakit import skevents, skqss
from sakurakit.skclass import Q_Q, memoized, memoizedproperty
from sakurakit.skdebug import dprint, dwarn
from sakurakit.sktr import tr_
from sakurakit.skwebkit import SkWebView #, SkWebViewBean
from sakurakit.skwidgets import SkTitlelessDockWidget, SkStyleView
#from sakurakit.skqml import QmlObject
from mytr import mytr_
import comets, config, dataman, netman, osutil, rc

@Q_Q
class _TopicsView(object):

  def __init__(self, q):
    #self.clear()
    self.subjectId = None # long
    self.topicId = None # long

    self.topicComet = None
    self.subjectComet = None

    #self._viewBean = SkWebViewBean(self.webView)

    self._createUi(q)

    #shortcut('ctrl+n', self._new, parent=q)

  def _createUi(self, q):
    q.setCentralWidget(self.webView)

    dock = SkTitlelessDockWidget(self.inspector)
    dock.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
    #dock.setAllowedAreas(Qt.BottomDockWidgetArea)
    q.addDockWidget(Qt.BottomDockWidgetArea, dock)

  def clear(self):
    self.setSubjectId(0)
    self.setTopicId(0)

  def setSubjectId(self, subjectId): # long ->
    if self.subjectId != subjectId:
      self.subjectId = subjectId

      if not subjectId:
        if self.subjectComet:
          self.subjectComet.setActive(False)
      else:
        if not self.subjectComet:
          self.subjectComet = comets.createPostComet()
          qml = self.subjectComet.q
          qml.topicDataReceived.connect(self._onTopicReceived)
          qml.topicDataUpdated.connect(self._onTopicUpdated)
        path = 'game/%s' % subjectId
        self.subjectComet.setPath(path)
        if netman.manager().isOnline():
          self.subjectComet.setActive(True)

  def setTopicId(self, topicId): # long ->
    if self.topicId != topicId:
      if topicId:
        if not self.topicComet:
          self.topicComet = comets.globalComet()
        if not self.topicId:
          self.topicComet.postDataReceived.connect(self._onPostReceived)
          self.topicComet.postDataUpdated.connect(self._onPostUpdated)
        if netman.manager().isOnline():
          self.topicComet.setProperty('active', True)
      elif self.topicComet:
        self.topicComet.postDataReceived.disconnect(self._onPostReceived)
        self.topicComet.postDataUpdated.disconnect(self._onPostUpdated)
      self.topicId = topicId

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
      ('i18nBean', m.i18nBean),
      ('mainBean', m.mainBean),
      ('topicEditBean', self.topicEditBean),
      ('topicInputBean', self.topicInputBean),
      ('postEditBean', self.postEditBean),
      ('postInputBean', self.postInputBean),
    )

  @memoizedproperty
  def postEditBean(self):
    import postedit
    return postedit.PostEditorManagerBean(parent=self.q, manager=self.postEditorManager)

  @memoizedproperty
  def postInputBean(self):
    import postinput
    return postinput.PostInputManagerBean(parent=self.q, manager=self.postInputManager)

  @memoizedproperty
  def topicEditBean(self):
    import topicedit
    return topicedit.TopicEditorManagerBean(parent=self.q, manager=self.topicEditorManager)

  @memoizedproperty
  def topicInputBean(self):
    import topicinput
    return topicinput.TopicInputManagerBean(parent=self.q, manager=self.topicInputManager)

  @memoizedproperty
  def postEditorManager(self):
    import postedit
    ret = postedit.PostEditorManager(self.q)
    ret.postChanged.connect(self._updatePost)
    return ret

  @memoizedproperty
  def postInputManager(self):
    import postinput
    ret = postinput.PostInputManager(self.q)
    ret.postReceived.connect(self._submitPost)
    return ret

  @memoizedproperty
  def topicEditorManager(self):
    import topicedit
    ret = topicedit.TopicEditorManager(self.q)
    ret.topicChanged.connect(self._updateTopic)
    return ret

  @memoizedproperty
  def topicInputManager(self):
    import topicinput
    ret = topicinput.TopicInputManager(self.q)
    ret.topicReceived.connect(self._submitTopic)
    return ret

  def _submitPost(self, postData, imageData):
    if self.topicId and netman.manager().isOnline():
      import forumapi
      skevents.runlater(partial(forumapi.manager().submitPost,
          postData, imageData,
          topicId=self.topicId))

  def _updatePost(self, postData, imageData):
    if self.topicId and netman.manager().isOnline():
      import forumapi
      skevents.runlater(partial(forumapi.manager().updatePost,
          postData, imageData))

  def _submitTopic(self, topicData, imageData, ticketData):
    if netman.manager().isOnline():
      import forumapi
      skevents.runlater(partial(forumapi.manager().submitTopic,
          topicData, imageData, ticketData))

  def _updateTopic(self, topicData, imageData, ticketData):
    if netman.manager().isOnline():
      import forumapi
      skevents.runlater(partial(forumapi.manager().updateTopic,
          topicData, imageData, ticketData))

  def _onPostReceived(self, data): # str ->
    try:
      obj = json.loads(data)
      topicId = obj['topicId']
      if topicId == self.topicId and self.q.isVisible():
        self.addPost(data)
      dprint("pass")
    except Exception, e:
      dwarn(e)

  def _onPostUpdated(self, data): # str ->
    try:
      obj = json.loads(data)
      topicId = obj['topicId']
      if topicId == self.topicId and self.q.isVisible():
        self.updatePost(data)
      dprint("pass")
    except Exception, e:
      dwarn(e)

  def _onTopicReceived(self, data): # str ->
    try:
      obj = json.loads(data)
      subjectId = obj['subjectId']
      if subjectId == self.subjectId and self.q.isVisible():
        self.addTopic(data)
      dprint("pass")
    except Exception, e:
      dwarn(e)

  def _onTopicUpdated(self, data): # str ->
    try:
      obj = json.loads(data)
      subjectId = obj['subjectId']
      if subjectId == self.subjectId and self.q.isVisible():
        self.updateTopic(data)
      dprint("pass")
    except Exception, e:
      dwarn(e)

  @memoizedproperty
  def webView(self):
    from PySide.QtWebKit import QWebPage
    ret = SkWebView()
    ret.titleChanged.connect(self.q.setWindowTitle)
    ret.enableHighlight() # highlight selected text
    ret.ignoreSslErrors() # needed to access Twitter

    ret.pageAction(QWebPage.Reload).triggered.connect(
        self.refresh, Qt.QueuedConnection)

    ret.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks) # Since there are local images
    ret.page().mainFrame().setScrollBarPolicy(Qt.Horizontal, Qt.ScrollBarAlwaysOff) # disable horizontal scroll

    #ret.page().setLinkDelegationPolicy(QWebPage.DelegateExternalLinks)
    ret.linkClicked.connect(osutil.open_url)
    return ret

  def refresh(self):
    """@reimp"""
    self.newPostButton.setVisible(bool(self.topicId))
    self.gameButton.setVisible(bool(self.subjectId))

    host = config.API_HOST # must be the same as rest.coffee for the same origin policy

    user = dataman.manager().user()

    w = self.webView
    w.setHtml(rc.haml_template('haml/reader/topicsview').render({
      'host': host,
      'locale': config.language2htmllocale(user.language),
      'title': mytr_("Messages"),
      'subjectId': self.subjectId,
      #'subjectType': self.subjectType,
      'topicId': self.topicId,
      'userName': user.name if not user.isGuest() else '',
      'userPassword': user.password,
      'rc': rc,
      'tr': tr_,
    }), host)
    self._injectBeans()

  @memoizedproperty
  def inspector(self):
    ret = SkStyleView()
    skqss.class_(ret, 'texture')
    layout = QtWidgets.QHBoxLayout()
    layout.addWidget(self.newPostButton)
    layout.addWidget(self.newTopicButton)
    layout.addStretch()
    layout.addWidget(self.browseButton)
    layout.addWidget(self.gameButton)
    layout.addWidget(self.refreshButton)
    ret.setLayout(layout)
    layout.setContentsMargins(4, 4, 4, 4)
    return ret

  @memoizedproperty
  def refreshButton(self):
    ret = QtWidgets.QPushButton(tr_("Refresh"))
    skqss.class_(ret, 'btn btn-primary')
    ret.setToolTip(tr_("Refresh") + " (Ctrl+R)")
    #ret.setStatusTip(ret.toolTip())
    ret.clicked.connect(self.refresh)
    #nm = netman.manager()
    #ret.setEnabled(nm.isOnline())
    #nm.onlineChanged.connect(ret.setEnabled)
    return ret

  @memoizedproperty
  def gameButton(self):
    ret = QtWidgets.QPushButton(tr_("Game"))
    skqss.class_(ret, 'btn btn-info')
    ret.setToolTip(tr_("Game"))
    #ret.setStatusTip(ret.toolTip())
    ret.clicked.connect(self._showGame)
    return ret

  def _showGame(self):
    import main
    main.manager().showGameView(itemId=self.subjectId)

  @memoizedproperty
  def browseButton(self):
    ret = QtWidgets.QPushButton(tr_("Browse"))
    skqss.class_(ret, 'btn btn-default')
    ret.setToolTip(tr_("Browse"))
    #ret.setStatusTip(ret.toolTip())
    ret.clicked.connect(self._browse)
    return ret

  def _browse(self):
    host = "http://sakuradite.com"
    if self.topicId:
      url = host + "/topic/%s" % self.topicId
      osutil.open_url(url)
    elif self.subjectId:
      url = host + "/game/%s" % self.subjectId
      osutil.open_url(url)

  @memoizedproperty
  def newPostButton(self):
    ret = QtWidgets.QPushButton("+ " + tr_("Chat"))
    skqss.class_(ret, 'btn btn-info')
    ret.setToolTip(tr_("New"))
    #ret.setStatusTip(ret.toolTip())
    ret.clicked.connect(self._newPost)
    return ret

  @memoizedproperty
  def newTopicButton(self):
    ret = QtWidgets.QPushButton("+ " + tr_("Topic"))
    skqss.class_(ret, 'btn btn-success')
    ret.setToolTip(tr_("New"))
    #ret.setStatusTip(ret.toolTip())
    ret.clicked.connect(self._newTopic)
    return ret

  def _newPost(self):
    self.postInputManager.newPost(self.topicId)
  def _newTopic(self):
    subjectId = self.subjectId
    if subjectId:
      subjectType = 'game'
    else:
      subjectId = config.GLOBAL_SUBJECT_ID
      subjectType = 'subject'
    self.topicInputManager.newTopic(subjectId=subjectId, subjectType=subjectType)

  # append ;null for better performance
  def addPost(self, data): # unicode json ->
    js = 'if (window.READY) addPost(%s); null' % data
    self.webView.evaljs(js)

  # append ;null for better performance
  def updatePost(self, data): # unicode json ->
    js = 'if (window.READY) updatePost(%s); null' % data
    self.webView.evaljs(js)

  # append ;null for better performance
  def addTopic(self, data): # unicode json ->
    js = 'if (window.READY) addTopic(%s); null' % data
    self.webView.evaljs(js)

  # append ;null for better performance
  def updateTopic(self, data): # unicode json ->
    js = 'if (window.READY) updateTopic(%s); null' % data
    self.webView.evaljs(js)

class TopicsView(QtWidgets.QMainWindow):
  def __init__(self, parent=None):
    WINDOW_FLAGS = Qt.Dialog|Qt.WindowMinMaxButtonsHint
    super(TopicsView, self).__init__(parent, WINDOW_FLAGS)
    self.setWindowIcon(rc.icon('window-forum'))
    self.setWindowTitle(mytr_("Messages"))
    self.__d = _TopicsView(self)

  def refresh(self): self.__d.refresh()
  def clear(self): self.__d.clear()

  def subjectId(self): return self.__d.subjectId
  def setSubjectId(self, subjectId): self.__d.setSubjectId(subjectId)

  def topicId(self): return self.__d.topicId
  def setTopicId(self, topicId): self.__d.setTopicId(topicId)

  def setVisible(self, value):
    """@reimp @public"""
    if value and not self.isVisible():
      self.__d.refresh()
    super(TopicsView, self).setVisible(value)
    if not value:
      self.__d.webView.clear()
      self.__d.clear()

class _TopicsViewManager:
  def __init__(self):
    self.dialogs = []

  def _createDialog(self):
    import windows
    parent = windows.normal()
    ret = TopicsView(parent=parent)
    ret.resize(550, 580)
    return ret

  def getDialog(self, subjectId=0, topicId=0):
    """
    @param* subjectId  long
    @param* topicId  long
    @return  TopicsView or None
    """
    for w in self.dialogs:
      if w.isVisible() and (subjectId, topicId) == (w.subjectId(), w.topicId()):
        return w

  def createDialog(self, subjectId=0, topicId=0):
    """
    @param* subjectId  long
    @param* topicId  long
    @return  TopicsView
    """
    w = self.getDialog(subjectId, topicId)
    if w:
      w.refresh()
      return w
    for w in self.dialogs:
      if not w.isVisible():
        w.clear()
        w.setSubjectId(subjectId)
        w.setTopicId(topicId)
        return w
    w = self._createDialog()
    w.setSubjectId(subjectId)
    w.setTopicId(topicId)

    self.dialogs.append(w)
    return w

class TopicsViewManager:
  def __init__(self):
    self.__d = _TopicsViewManager()

  #def clear(self): self.hide()

  def isViewVisible(self, *args, **kwargs):
    return bool(self.__d.getDialog(*args, **kwargs))

  def isVisible(self):
    if self.__d.dialogs:
      for w in self.__d.dialogs:
        if w.isVisible():
          return True
    return False

  def hide(self):
    if self.__d.dialogs:
      for w in self.__d.dialogs:
        if w.isVisible():
          w.hide()

  def show(self, subjectId=0, topicId=0):
    """
    @param* subjectId  long  subject ID
    @param* topicId  long  chatroom topicId
    """
    w = self.__d.createDialog(subjectId, topicId)
    w.show()
    w.raise_()

@memoized
def manager():
  import webrc
  webrc.init()
  return TopicsViewManager()

#@QmlObject
#class TopicsViewManagerProxy(QObject):
#  def __init__(self, parent=None):
#    super(TopicsViewManagerProxy, self).__init__(parent)
#
#  @Slot(int)
#  def showTopic(self, id):
#    manager().showTopic(id)

if __name__ == '__main__':
  a = debug.app()
  #manager().showTopic('global')
  manager().showTopic(config.GLOBAL_TOPIC_ID)
  a.exec_()

# EOF
