# coding: utf8
# browserui.py
# 12/13/2012 jichi

__all__ = 'WebBrowser',

import re, weakref
from functools import partial
from itertools import imap
from PySide.QtCore import Qt, Signal, QUrl
from PySide import QtGui
from Qt5 import QtWidgets
from sakurakit import skevents, skfileio, skqss, skos
from sakurakit.skclass import memoizedproperty, Q_Q
from sakurakit.skdebug import dprint
from sakurakit.skwidgets import SkTitlelessDockWidget, SkDraggableMainWindow, shortcut
from sakurakit.sktr import tr_
from addressui import *
from network import *
from tabui import *
from webkit import *
from i18n import i18n
import config, defs, proxy, rc, settings, siteman, textutil, ui

BLANK_URL = "about:blank"

def _urltext(url): # unicode|QUrl -> unicode
  if isinstance(url, QUrl):
    url = proxy.fromproxyurl(url) or url
    url = url.toString()
  return textutil.simplifyurl(url) if url else ''

#class WebBrowser(QtWidgets.QMainWindow):
class WebBrowser(SkDraggableMainWindow):

  quitRequested = Signal()
  messageReceived = Signal(unicode)

  def __init__(self, parent=None):
    #WINDOW_FLAGS = (
    #  Qt.Window
    #  | Qt.CustomizeWindowHint
    #  | Qt.WindowTitleHint
    #  | Qt.WindowSystemMenuHint
    #  | Qt.WindowMinMaxButtonsHint
    #  | Qt.WindowCloseButtonHint
    #)
    super(WebBrowser, self).__init__(parent)
    self.__d = _WebBrowser(self)
    skqss.class_(self, 'webkit')

  def showStatusMessage(self, t, type='message'):
    """
    @param  t  unicode
    @param  type  'message', 'warning', or 'error'
    """
    self.statusBar().showMessage(text)

  def openDefaultPage(self):
    self.__d.newTabAfterCurrentWithBlankPage()

  def openUrls(self, urls): # [unicode url]
    for url in urls:
      self.__d.openUnknownAfterCurrent(url)
      #self.__d.openUrl(url)

  def loadTabs(self): # -> bool
    return self.__d.loadTabs()

  def closeEvent(self, e):
    ss = settings.global_()
    ss.setWindowWidth(self.width())
    ss.setWindowHeight(self.height())

    super(WebBrowser, self).closeEvent(e)

@Q_Q
class _WebBrowser(object):
  def __init__(self, q):
    ss = settings.global_()
    self._rubyEnabled = ss.isRubyEnabled()
    self._ttsEnabled = ss.isTtsEnabled() # cached
    self._fullTranslationEnabled = ss.isFullTranslationEnabled() # cached
    self._translationTipEnabled = ss.isTranslationTipEnabled() # cached

    self.loadProgress = 100 # int [0,100]

    self.visitedUrls = [] # [str url]
    self.closedUrls = [] # [str url]

    import jlpman, trman, ttsman
    self._jlpAvailable = jlpman.manager().isAvailable() # bool
    self._ttsAvailable = ttsman.manager().isAvailable() # bool
    self._translatorAvailable = trman.manager().isAvailable() # bool

    #layout = QtWidgets.QVBoxLayout()
    #layout.addWidget(self.addressWidget)
    #layout.addWidget(self.tabWidget)

    #w = QtWidgets.QWidget()
    #w.setLayout(layout)
    #layout.setContentsMargins(0, 0, 0, 0)
    #q.setCentralWidget(w)

    q.setCentralWidget(self.tabWidget)
    dock = SkTitlelessDockWidget(self.addressWidget)
    dock.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
    dock.setAllowedAreas(Qt.TopDockWidgetArea)
    q.addDockWidget(Qt.TopDockWidgetArea, dock)

    self._createShortcuts(q)
    self._createGestures()

    from PySide.QtCore import QCoreApplication
    qApp = QCoreApplication.instance()
    qApp.aboutToQuit.connect(self._onQuit)

    #self.newTabAfterCurrentWithBlankPage()

    self.loadVisitedUrls()
    self.loadClosedUrls()

  def _onQuit(self):
    dprint("enter")
    self.saveTabs()
    self.saveVisitedUrls()
    self.saveClosedUrls()
    dprint("exit")

  def _createShortcuts(self, q):
    shortcut(QtGui.QKeySequence.AddTab, self.newTabAfterCurrentWithBlankPage, parent=q)

    shortcut('ctrl+w', self.closeCurrentTab, parent=q)

    shortcut('ctrl+shift+t', self.undoCloseTab, parent=q)

    for k in 'ctrl+l', 'alt+d':
      shortcut(k, self.addressEdit.focus, parent=q)

    for k in 'ctrl+{', 'ctrl+shift+tab':
      shortcut(k, self.previousTab, parent=q)
    for k in 'ctrl+}', 'ctrl+tab':
      shortcut(k, self.nextTab, parent=q)

    for i in range(1, 10):
      shortcut('ctrl+%i' % i, partial(self.focusTab, i-1), parent=q)
    #shortcut('ctrl+0', partial(self.focusTab, 10-9), parent=q) # ctrl+ 0 used by zoom reset

  def _createGestures(self):
    from qtgesture.gesture import MouseGesture as G
    self._addGesture((G.NoMatch,), None, i18n.tr("No match"))

    self._addGesture((G.Down, G.Right),
        partial(skevents.runlater, self.closeCurrentTab), # close after existing the event loop
        i18n.tr("Close tab"))

    self._addGesture((G.Right, G.Left), self.newTabAfterCurrentWithBlankPage, i18n.tr("New tab"))
    self._addGesture((G.Left, G.Right), self.undoCloseTab, i18n.tr("Undo close tab"))
    self._addGesture((G.Up, G.Left), self.previousTab, i18n.tr("Previous tab"))
    self._addGesture((G.Up, G.Right), self.nextTab, i18n.tr("Next bab"))
    self._addGesture((G.Up, G.Down), self.refresh, i18n.tr("Refresh"))
    self._addGesture((G.Left,), self.back, i18n.tr("Back"))
    self._addGesture((G.Right,), self.forward, i18n.tr("Forward"))
    self._addGesture((G.Down,), self.openHoveredLinkAfterCurrent, i18n.tr("Open link in background tab"))

  def _addGesture(self, directions, callback, name):
    """
    @param  directions  [int gesture const]
    @param  callback  function or None
    @param  name  unicode
    """
    from qtgesture.gesture import MouseGesture
    g = MouseGesture(directions=directions, parent=self.q)
    g.name = name # unicode
    if callback:
      g.triggered.connect(callback)
    g.triggered.connect(partial(self._showGesture, g))
    self.gestureFilter.add(g)

  def _showGesture(self, gesture):
    """
    @param  gesture  gesture.MouseGesture with name
    """
    msg = ''.join(imap(self.gestureDirectionNames.get, gesture.directions))
    msg += ' | ' + gesture.name
    self.showMessage(msg)

  @memoizedproperty
  def gestureDirectionNames(self):
    from qtgesture.gesture import MouseGesture
    return {
      MouseGesture.NoMatch: u"Φ", # ふぁい
      MouseGesture.Up: u"↑", # うえ
      MouseGesture.Down: u"↓", # した
      MouseGesture.Left: u"←", # ひだり
      MouseGesture.Right: u"→", # みぎ
      MouseGesture.Horizontal: "-",
      MouseGesture.Vertical: "|",
    }

  ## Properties ##

  @memoizedproperty
  def networkAccessManager(self):
    ret = WbNetworkAccessManager(self.q)
    return ret

  @memoizedproperty
  def gestureFilter(self):
    from qtgesture.gesturefilter import MouseGestureFilter
    buttons = Qt.MiddleButton
    if not skos.MAC:
      buttons |= Qt.RightButton
    #buttons |= Qt.LeftButton # for debugging only
    return MouseGestureFilter(buttons=buttons, modifiers=Qt.NoModifier, parent=self.q)

  @memoizedproperty
  def tabWidget(self):
    ret = WbTabWidget()
    skqss.class_(ret, 'webkit')
    ret.setTabBar(self.tabBar)
    if skos.MAC:
      ret.setDocumentMode(True) # only useful on mac, must comes after tabbar is set. This will disable double-click event on tabbar
    ret.setCornerWidget(self.newTabButton)
    ret.tabCloseRequested.connect(self.closeTab)
    ret.currentChanged.connect(self.loadAddress)
    ret.currentChanged.connect(self.refreshLoadProgress)
    ret.currentChanged.connect(self.refreshWindowTitle)
    ret.currentChanged.connect(self.refreshWindowIcon)
    ret.doubleClicked.connect(self.newTabAtLastWithBlankPage)

    ret.currentChanged.connect(self.refreshSiteStatus)
    return ret

  @memoizedproperty
  def tabBar(self):
    ret = WbTabBar()
    skqss.class_(ret, 'webkit')
    # FIXME: Enable glowing effect will cause issue for Flash
    #ret.setGraphicsEffect(ui.createGlowEffect(ret))
    #ret.doubleClickedAt.connect(self.newTabAfter)
    return ret

  @memoizedproperty
  def addressWidget(self):
    row = QtWidgets.QHBoxLayout()
    row.addWidget(self.navigationToolBar)
    row.addWidget(self.addressEdit, 1)
    row.addWidget(self.optionToolBar)
    row.setContentsMargins(4, 5, 4, 2)
    ret = QtWidgets.QWidget()
    ret.setLayout(row)
    return ret

  @memoizedproperty
  def addressEdit(self):
    ret = WbAddressEdit()
    ret.setGraphicsEffect(ui.createGlowEffect(ret))
    skqss.class_(ret, 'webkit address')
    # Not sure why that global shortcut does not work
    ret.textEntered.connect(self.openUnknown)
    ret.editTextChanged.connect(self.highlightText)
    return ret

  @memoizedproperty
  def newTabButton(self):
    ret = QtWidgets.QPushButton()
    ret.setGraphicsEffect(ui.createGlowEffect(ret))
    skqss.class_(ret, 'webkit btn-tab-corner')
    ret.setText("+")
    #ret.setToolTip(tr_("New Tab"))
    ret.setToolTip(u"%s (%s, %s, %s: →←)" % (i18n.tr("New Tab"), "Ctrl+T", tr_("Double-click"), i18n.tr("Gesture")))
    ret.clicked.connect(self.newTabAtLastWithBlankPage)
    return ret

  @memoizedproperty
  def navigationToolBar(self):
    ret = QtWidgets.QToolBar()
    ret.setGraphicsEffect(ui.createGlowEffect(ret))
    skqss.class_(ret, 'webkit toolbar toolbar-nav')

    a = ret.addAction(u"\u25c0") # left triangle
    a.triggered.connect(self.back)
    a.setToolTip(u"%s (Ctrl+[, Alt+←, %s: ←)" % (tr_("Back"), i18n.tr("Gesture")))

    a = ret.addAction(u"\u25B6") # right triangle
    a.triggered.connect(self.forward)
    a.setToolTip(u"%s (Ctrl+], Alt+→, %s: →)" % (tr_("Forward"), i18n.tr("Gesture")))

    #a = ret.addAction(u'\u27f3') # circle
    a = ret.addAction(u"◯") # まる
    a.triggered.connect(self.refresh)
    a.setToolTip(u"%s (Ctrl+R, %s: ↑↓)" % (tr_("Refresh"), i18n.tr("Gesture")))

    #a = ret.addAction(u"\u238c")
    a = ret.addAction(u"←") # ひだり
    a.triggered.connect(self.undoCloseTab)
    a.setToolTip(u"%s (Ctrl+Shift+T, %s: ←→)" % (i18n.tr("Undo close tab"), i18n.tr("Gesture")))

    a = ret.addAction(u"＋") # fullwidth +
    a.triggered.connect(self.zoomIn)
    a.setToolTip(u"%s (Ctrl+=)" % tr_("Zoom In"))

    a = ret.addAction(u"ー") # fullwidth -
    a.triggered.connect(self.zoomIn)
    a.setToolTip(u"%s (Ctrl+-)" % tr_("Zoom Out"))
    return ret

  @memoizedproperty
  def optionToolBar(self):
    ret = QtWidgets.QToolBar()
    ret.setGraphicsEffect(ui.createGlowEffect(ret))
    skqss.class_(ret, 'webkit toolbar toolbar-opt')

    a = self.siteAct = ret.addAction(u"遊")
    a.setCheckable(True)
    a.setEnabled(False) # disable on startup
    a.setToolTip(i18n.tr("Display subtitles for the game site"))
    #a.setMenu(self.siteMenu)
    a.triggered.connect(self._injectSite)
    btn = ret.widgetForAction(a)
    btn.setPopupMode(QtWidgets.QToolButton.InstantPopup)

    a = self.annotAct = ret.addAction(u"訳")
    a.setCheckable(True)
    a.setToolTip(i18n.tr("Settings for all sites"))
    a.setMenu(self.annotMenu)
    btn = ret.widgetForAction(a)
    btn.setPopupMode(QtWidgets.QToolButton.InstantPopup)
    a.setChecked(self.isAnnotEnabled())

    a = ret.addAction(u"≡") # U+226, three lines; alternative: "⌘", U+2318 コマンド記号
    a.setToolTip(i18n.tr("Global settings"))
    a.setMenu(self.optionMenu)
    #a.triggered.connect(a.menu().exec_)
    # https://bugreports.qt-project.org/browse/QTBUG-1453
    btn = ret.widgetForAction(a)
    btn.setPopupMode(QtWidgets.QToolButton.InstantPopup)
    return ret

  @memoizedproperty
  def optionMenu(self):
    ret = QtWidgets.QMenu(self.q)

    #a = ret.addAction(rc.standard_icon(QtWidgets.QStyle.SP_DialogHelpButton), tr_("Help"))
    a = ret.addAction(tr_("Preferences"))
    a.triggered.connect(self._openSettingsPage)
    a.setToolTip("about:settings")

    #a = ret.addAction(rc.standard_icon(QtWidgets.QStyle.SP_DialogHelpButton), tr_("Help"))
    a = ret.addAction(tr_("Help"))
    a.triggered.connect(self._openHelpPage)
    a.setToolTip("about:help")

    a = ret.addAction(tr_("About"))
    a.triggered.connect(self._openAboutPage)
    a.setToolTip("about:version")
    return ret

  @memoizedproperty
  def annotMenu(self):
    ret = QtWidgets.QMenu(self.q)

    ss = settings.global_()

    a = ret.addAction(i18n.tr("Display furigana"))
    a.setCheckable(True)
    a.setEnabled(self._jlpAvailable)
    a.setChecked(self._rubyEnabled)
    a.triggered[bool].connect(ss.setRubyEnabled)
    a.triggered[bool].connect(self._setRubyEnabled)
    a.triggered.connect(self._refreshAnnotAct)

    a = self.fullTranslationAct = ret.addAction(i18n.tr("Display translation"))
    a.setCheckable(True)
    a.setEnabled(self._translatorAvailable)
    a.setChecked(self._fullTranslationEnabled)
    a.triggered[bool].connect(ss.setFullTranslationEnabled)
    a.triggered[bool].connect(self._setFullTranslationEnabled)
    a.triggered.connect(self._refreshAnnotAct)

    a = self.translationTipAct = ret.addAction(i18n.tr("Popup translation when hover"))
    a.setCheckable(True)
    a.setEnabled(self._translatorAvailable)
    a.setChecked(self._translationTipEnabled)
    a.triggered[bool].connect(ss.setTranslationTipEnabled)
    a.triggered[bool].connect(self._setTranslationTipEnabled)
    a.triggered.connect(self._refreshAnnotAct)

    ret.addSeparator()

    a = self.ttsAct = ret.addAction(i18n.tr("Text-to-speech when click")) # おんぷ
    a.setCheckable(True)
    a.setEnabled(self._ttsAvailable)
    a.setChecked(self._ttsEnabled)
    a.triggered[bool].connect(ss.setTtsEnabled)
    a.triggered[bool].connect(self._setTtsEnabled)
    a.setVisible(skos.WIN) # only enabled on Windows
    a.triggered.connect(self._refreshAnnotAct)

    return ret

  #@memoizedproperty
  #def siteMenu(self):
  #  ret = QtWidgets.QMenu(self.q)

  #  ss = settings.global_()

  #  a = self.siteSubtitleAct = ret.addAction(i18n.tr("Display subtitles"))
  #  a.setCheckable(True)
  #  a.triggered.connect(self._injectSite)

  #  return ret

  ## Site-specific inject ##

  def refreshSiteStatus(self):
    enabled = False
    checked = False
    v = self.tabWidget.currentWidget()
    if v:
      checked = v.isSiteEnabled()
      url = v.url()
      if not url.isEmpty():
        site = siteman.manager().matchSite(url)
        if site:
          enabled = True
    self.siteAct.setEnabled(enabled)
    self.siteAct.setChecked(enabled and checked)

  def _injectSite(self):
    t = self.siteAct.isChecked()
    v = self.tabWidget.currentWidget()
    if v:
      dprint(t)
      v.setSiteEnabled(t)
      v.injectSite()

  ## Inject ##

  # Combinations:
  # trtip, tts, trtip+tts
  # trful, trful+tts, trful+tts, trful+ruby+tts
  # ruby, ruby+tts, ruby+trtip, ruby+trtip+tts

  def isAnnotEnabled(self):
    return self._fullTranslationEnabled or self._translationTipEnabled or self._rubyEnabled or self._ttsEnabled

  def _refreshAnnotAct(self):
    self.annotAct.setChecked(self.isAnnotEnabled())

  def _setRubyEnabled(self, t): # bool ->
    if self._rubyEnabled != t:
      self._rubyEnabled = t
      self._reinjectAnnot()

  def _setTtsEnabled(self, t): # bool ->
    if self._ttsEnabled != t:
      self._ttsEnabled = t
      self._reinjectAnnot()

  def _setFullTranslationEnabled(self, t): # bool ->
    if self._fullTranslationEnabled != t:
      self._fullTranslationEnabled = t
      self._reinjectAnnot()

  def _setTranslationTipEnabled(self, t): # bool ->
    if self._translationTipEnabled != t:
      self._translationTipEnabled = t
      self._reinjectAnnot()

  def _reinjectAnnot(self):
    t = self.isAnnotEnabled()
    for w in self._iterTabWidgets():
      w.setAnnotEnabled(t)
      w.injectAnnot()

  ## Load/save ##

  def loadTabs(self): # -> bool
    ret = False
    data = skfileio.readfile(rc.TABS_LOCATION)
    if data:
      #urls = data.split('\n')
      urls = [it for it in data.split('\n') if it and len(it) < defs.MAX_HISTORY_URL_SIZE]
      for url in urls:
        self.openUnknownAfterCurrent(url)
      ret = True
    dprint("pass: ret = %s" % ret)
    return ret

  def saveTabs(self): # -> bool
    ret = False
    urls = [] # [unicode url]
    for w in self._iterTabWidgets():
      url = w.url().toString()
      if url != BLANK_URL:
        urls.append(url)
    path = rc.TABS_LOCATION
    if urls:
      data = '\n'.join(urls)
      ret = skfileio.writefile(path, data)
    else:
      skfileio.removefile(path)
    dprint("pass: ret = %s" % ret)
    return ret

  def loadVisitedUrls(self):
    data = skfileio.readfile(rc.VISIT_HISTORY_LOCATION)
    if data:
      #self.visitedUrls = data.split('\n')
      self.visitedUrls = [it for it in data.split('\n') if it and len(it) < defs.MAX_HISTORY_URL_SIZE]
      for url in reversed(self.visitedUrls):
        icon = rc.url_icon(url)
        self.addressEdit.addItem(icon, url)
    dprint("pass")

  def saveVisitedUrls(self):
    path = rc.VISIT_HISTORY_LOCATION
    if self.visitedUrls:
      from sakurakit import skcontainer
      l = skcontainer.uniquelist(reversed(self.visitedUrls))
      if len(l) > config.VISIT_HISTORY_SIZE:
        del l[config.VISIT_HISTORY_SIZE:]
      l.reverse()
      data = '\n'.join(l)
      skfileio.writefile(path, data)
    #else: # never not remove old history
    #  skfileio.removefile(path)
    dprint("pass")

  def loadClosedUrls(self):
    data = skfileio.readfile(rc.CLOSE_HISTORY_LOCATION)
    if data:
      #self.closedUrls = data.split('\n')
      self.closedUrls = [it for it in data.split('\n') if it and len(it) < defs.MAX_HISTORY_URL_SIZE]
    dprint("pass")

  def saveClosedUrls(self):
    path = rc.CLOSE_HISTORY_LOCATION
    if self.closedUrls:
      l = self.closedUrls
      if len(l) > config.CLOSE_HISTORY_SIZE:
        l = l[len(l) - config.CLOSE_HISTORY_SIZE:]
      data = '\n'.join(l)
      skfileio.writefile(path, data)
    else:
      skfileio.removefile(path)
    dprint("pass")

  ## Actions ##

  def _iterTabWidgets(self): # yield QWebView
    w = self.tabWidget
    for i in xrange(w.count()):
      yield w.widget(i)


  def highlightText(self, t):
    t = t.strip()
    if t:
      w = self.tabWidget.currentWidget()
      if w:
        w.rehighlight(t)

  def _openSettingsPage(self): self.openUrlAfterCurrent('about:settings', focus=True)
  def _openHelpPage(self): self.openUrlAfterCurrent('about:help', focus=True)
  def _openAboutPage(self): self.openUrlAfterCurrent('about:version', focus=True)

  def openUnknown(self, text): # string ->
    """
    @param  text  unicode
    """
    url = textutil.completeurl(text)
    self.openUrl(url)

  def openUnknownBeforeCurrent(self, text): # string ->
    """
    @param  text  unicode
    """
    url = textutil.completeurl(text)
    self.openUrlBeforeCurrent(url)

  def openUnknownAfterCurrent(self, text): # string ->
    """
    @param  text  unicode
    """
    url = textutil.completeurl(text)
    self.openUrlAfterCurrent(url)

  def openUrl(self, url, focus=True): # string ->
    """
    @param  url  unicode
    """
    self.addRecentUrl(url)
    if self.tabWidget.isEmpty():
      self.newTabAfterCurrent(focus=focus)
      v = self.tabWidget.currentWidget()
    else:
      v = self.tabWidget.currentWidget()
      v.stop()
    v.load(url)

  def openUrlBeforeCurrent(self, url, focus=True): # string ->
    """
    @param  url  unicode
    """
    self.addRecentUrl(url)
    v = self.newTabBeforeCurrent(focus=focus)
    v.load(url)

  def openUrlAfterCurrent(self, url, focus=False): # string ->
    """
    @param  url  unicode
    @param* focus  bool
    """
    self.addRecentUrl(url)
    v = self.newTabAfterCurrent(focus=focus)
    v.load(url)

  def openHoveredLinkAfterCurrent(self, focus=False): # default to open at the background
    """
    @param* focus  bool
    """
    w = self.tabWidget.currentWidget()
    if w:
      url = w.page().hoveredLink()
      if url:
        self.openUrlAfterCurrent(url, focus=focus)

  def addRecentUrl(self, url): # string|QUrl ->
    text = _urltext(url)
    if text:
      if text != BLANK_URL:
        self.visitedUrls.append(text)
      self.addressEdit.addText(text)

      #urltext = url.toString() if isinstance(url, QUrl) else url
      #self.visitedUrls.append(urltext)

  def openBlankPage(self):
    if self.tabWidget.isEmpty():
      self.newTabAtLast()
    v = self.tabWidget.currentWidget()
    #assert v
    if v:
      v.load(BLANK_URL)
      #v.setHtml(START_HTML)
      #self.tabWidget.setTabText(self.currentIndex(), tr("Start Page"));
      #int i = ui->addressEdit->findText(WB_BLANK_PAGE);
      #if (i >= 0)
      #  ui->addressEdit->setCurrentIndex(i);
      #ui->addressEdit->setIcon(WBRC_IMAGE_APP);

  def undoCloseTab(self):
    if self.closedUrls:
      url = self.closedUrls[-1]
      del self.closedUrls[-1]
      self.openUnknownBeforeCurrent(url)

  def focusTab(self, index): # int ->
    if index >=0 and index < self.tabWidget.count():
      self.tabWidget.setCurrentIndex(index)

  def previousTab(self):
    self.focusTab(self.tabWidget.currentIndex() - 1)
  def nextTab(self):
    self.focusTab(self.tabWidget.currentIndex() + 1)

  def newTabAfterCurrentWithBlankPage(self):
    self.newTabAfterCurrent()
    self.openBlankPage()

  def newTabAtLastWithBlankPage(self):
    self.newTabAtLast()
    self.openBlankPage()

  def newTabBeforeCurrent(self, focus=True): # -> webview
    return self.newTabBefore(index=self.tabWidget.currentIndex(), focus=focus)

  def newTabAfterCurrent(self, focus=True): # -> webview
    return self.newTabAfter(index=self.tabWidget.currentIndex(), focus=focus)

  def newTabAtLast(self, focus=True): # -> webview
    return self.newTabAfter(index=self.tabWidget.count() -1, focus=focus)

  def newTabAfter(self, index, focus=True): # -> webview
    return self.newTabBefore(index + 1, focus=focus)

  def newTabBefore(self, index, focus=True): # -> webview

    index = min(max(0, index), self.tabWidget.count())
    w = self.createWebView()
    #title = w.title() or w.url().toString()
    #icon = w.icon() or rc.url_icon(w.url())
    self.tabWidget.newTab(w, index=index, focus=focus) #, title=title, icon=icon)
    return w

  def _createWindow(self, type): # QWebPage::WebWindowType -> QWebView
    return self.newTabAfterCurrent()

  def createWebView(self):
    ret = WbWebView()
    ret.onCreateWindow = self._createWindow

    page = ret.page()
    page.setNetworkAccessManager(self.networkAccessManager)
    page.linkHovered.connect(self.showLink)
    page.linkClickedWithModifiers.connect(self.openUrlAfterCurrent)

    ret.messageReceived.connect(self.q.messageReceived)

    ret.linkClicked.connect(self.addRecentUrl)
    ret.linkClicked.connect(lambda url:
        url.isEmpty() or self.setDisplayAddress(url))

    ret.urlChanged.connect(self.refreshSiteStatus)

    ref = weakref.ref(ret)

    ret.urlChanged.connect(partial(lambda ref, value:
        self._updateTabTitleIcon(ref()),
        ref))

    ret.urlChanged.connect(self.refreshAddress)

    ret.titleChanged.connect(partial(lambda ref, value:
        self._updateTabTitle(ref()),
        ref))

    ret.titleChanged.connect(partial(lambda ref, value:
        ref() == self.tabWidget.currentWidget() and self.refreshWindowTitle(),
        ref))

    ret.iconChanged.connect(partial(lambda ref:
        self._updateTabIcon(ref()),
        ref))

    ret.iconChanged.connect(partial(lambda ref:
        ref() == self.tabWidget.currentWidget() and self.refreshWindowIcon(),
        ref))

    page.loadProgress.connect(partial(lambda ref, value:
        ref() == self.tabWidget.currentWidget() and self.refreshLoadProgress(),
        ref))

    ret.setAnnotEnabled(self.isAnnotEnabled())

    ret.installEventFilter(self.gestureFilter)

    return ret

  def showMessage(self, t): # unicode ->
      self.q.messageReceived.emit(t)

  def showLink(self, url, content): # unicode, unicode
    text = _urltext(url)
    if text:
      self.showMessage(text)

  def forward(self):
    w = self.tabWidget.currentWidget()
    if w:
      w.forward()
  def back(self):
    w = self.tabWidget.currentWidget()
    if w:
      w.back()
  def refresh(self):
    w = self.tabWidget.currentWidget()
    if w:
      w.reload()
  def zoomIn(self):
    w = self.tabWidget.currentWidget()
    if w:
      w.zoomIn()
  def zoomOut(self):
    w = self.tabWidget.currentWidget()
    if w:
      w.zoomOut()

  def currentTabTitle(self): # -> unicode
    w = self.tabWidget.currentWidget()
    if w:
      return w.title() or _urltext(w.url())
    else:
      return ''

  def currentTabIcon(self): # int -> unicode
    w = self.tabWidget.currentWidget()
    if w:
      return w.icon() or rc.url_icon(w.url())

  def refreshWindowTitle(self):
    t = self.currentTabTitle()
    if not t:
      t = u"Website Reader (α)"
    self.q.setWindowTitle(t)

  def refreshWindowIcon(self):
    icon = self.currentTabIcon()
    self.addressEdit.setItemIcon(0, icon)
    self.q.setWindowIcon(icon)

  def refreshLoadProgress(self):
    v = self.loadProgress
    w = self.tabWidget.currentWidget()
    if w:
      v = w.page().progress()
    if self.loadProgress != v:
      self.loadProgress = v
      self.showProgressMessage()
      self.addressEdit.setProgress(v)

  def showProgressMessage(self):
    if self.loadProgress == 0:
      t = "%s ..." % i18n.tr("Loading")
    elif self.loadProgress == 100:
      t = i18n.tr("Loading complete")
    else:
      t = "%s ... %i/100" % (i18n.tr("Loading"), self.loadProgress)
    self.showMessage(t)

  def setDisplayAddress(self, url):
    text = _urltext(url)
    #if text:
    #self.addressEdit.setEditText(text)
    self.addressEdit.setText(text)

  def refreshAddress(self):
    v = self.tabWidget.currentWidget()
    if v:
      self.setDisplayAddress(v.url())

  def loadAddress(self):
    w = self.tabWidget.currentWidget()
    url = w.url() if w else ''
    self.setDisplayAddress(url)

  def closeTab(self, index):
    if self.tabWidget.count() <= 1:
      self.q.quitRequested.emit()
    else:
      if index >= 0 and index < self.tabWidget.count():
        w = self.tabWidget.widget(index)
        url = w.url()
        self.tabWidget.removeTab(index)

        w.clear() # enforce clear flash
        w.setParent(None) # only needed in PySide, otherwise the parent is QStackWidget

        #url = url.toString()
        url = _urltext(url)
        if url != BLANK_URL:
          self.closedUrls.append(url)

  def closeCurrentTab(self):
    self.closeTab(self.tabWidget.currentIndex())

  def _updateTabTitleIcon(self, w): # QWebView
    self._updateTabTitle(w)
    self._updateTabIcon(w)

  def _updateTabIcon(self, w): # QWebView
    index = self.tabWidget.indexOf(w)
    if index >= 0:
      icon = w.icon() or rc.url_icon(w.url())
      self.tabWidget.setTabIcon(index, icon)

  def _updateTabTitle(self, w): # QWebView
    tw = self.tabWidget
    index = tw.indexOf(w)
    if index >= 0:
      title = w.title() or _urltext(w.url()) or tr_("Empty")
      tw.setTabText(index, title)
      url = _urltext(w.url())
      if url:
        tip = "%s - %s" % (title,
            textutil.elidetext(url, 30))
      else:
        tip = title
      tw.setTabToolTip(index, tip)

  #def setTabTitle(self, tab, title):
  #  """
  #  @param  tab  index or QWidget
  #  @param  title  unicode
  #  """
  #  tw = self.tabWidget
  #  if not isinstance(tab, (int, long)):
  #    tab = tw.indexOf(tab)
  #  if not title:
  #    title = tr_("Empty")
  #  if tab >= 0 and tab < self.tabWidget.count():
  #    tw.setTabToolTip(tab, title)
  #    tw.setTabText(tab, title)
  #    #tw.setTabText(tab, self.shortenTitle(title))

# EOF
