# coding: utf8
# webkit.py
# 12/13/2012 jichi

__all__ = 'WbWebView', 'WbWebPage'

import re
from PySide.QtCore import Qt, Signal, QEvent, QUrl
from PySide.QtWebKit import QWebPage
from Qt5 import QtWidgets
from sakurakit import skwebkit
from sakurakit.skclass import Q_Q
from sakurakit.skdebug import dprint
from sakurakit.sktr import tr_
import beans, config, rc

## WebFrame injectors ##

class AnnotInjector:
  def __init__(self, frame):
    self.frame = frame # QWebFrame
    self.enabled = False # bool
    self.injected = False # bool  whether beans have been injected

  def isEnabled(self): return self.enabled

  def injectJavaScript(self):
    self.injectBeans()
    self.frame.evaluateJavaScript(rc.cdn_data('inject-annot'))

  def injectBeans(self):
    if self.enabled and not self.injected: # and not self.q.parent().url().isEmpty():
      self.injected = True
      for name,obj in self.iterBeans():
        self.frame.addToJavaScriptWindowObject(name, obj)

  @staticmethod
  def iterBeans():
    """
    return  [(unicode name, QObject bean)]
    """
    import beans
    m = beans.manager()
    return (
      ('cdnBean', m.cdnBean),
      ('clipBean', m.clipBean),
      ('jlpBean', m.jlpBean),
      ('settingsBean', m.settingsBean),
      ('trBean', m.trBean),
      ('ttsBean', m.ttsBean),
    )

class SiteInjector:
  def __init__(self, frame):
    self.frame = frame # QWebFrame
    self.enabled = False # bool
    self.injected = False # bool  whether beans have been injected

  def isEnabled(self): return self.enabled

  def injectJavaScript(self):
    self.injectBeans()
    self.frame.evaluateJavaScript(rc.cdn_data('inject-site'))

  def injectBeans(self):
    if self.enabled and not self.injected: # and not self.q.parent().url().isEmpty():
      self.injected = True
      for name,obj in self.iterBeans():
        self.frame.addToJavaScriptWindowObject(name, obj)

  @staticmethod
  def iterBeans():
    """
    return  [(unicode name, QObject bean)]
    """
    import beans
    m = beans.manager()
    return (
      ('cdnBean', m.cdnBean),
      ('trBean', m.trBean),
    )

## WbWebView ##

class WbWebView(skwebkit.SkWebView):
  messageReceived = Signal(unicode)

  def __init__(self, parent=None):
    super(WbWebView, self).__init__(parent, page=WbWebPage())
    self.__d = _WbWebView(self)
    self.enableHighlight()

    self.titleChanged.connect(self.setWindowTitle)
    self.onCreateWindow = None # -> QWebView

    #l = self.findChildren(QtWidgets.QScrollBar) # does not exist
    #background-color: transparent
    #&::sub-page,
    #&::add-page
    #  background-color: transparent

  def __del__(self):
    dprint("pass") # For debug usage

  # QWebView * QWebView::createWindow ( QWebPage::WebWindowType type ) [virtual protected]
  def createWindow(self, type): # override
    if self.onCreateWindow:
      return self.onCreateWindow(type)

  def _onLoadStarted(self):
    self.setCursor(Qt.BusyCursor)
  def _onLoadFinished(self, success): # bool ->
    self.setCursor(Qt.ArrowCursor)

  def zoomIn(self): # override
    super(WbWebView, self).zoomIn()
    self.__d.showZoomMessage()

  def zoomOut(self): # override
    super(WbWebView, self).zoomOut()
    self.__d.showZoomMessage()

  def zoomReset(self): # override
    super(WbWebView, self).zoomReset()
    self.__d.showZoomMessage()

  # Injection

  def load(self, url): # QUrl ->
    t = url.toString() if isinstance(url, QUrl) else url
    if t.startswith('about:'):
      data = rc.html_data(t)
      if data:
        self.setHtml(data)
        if t == 'about:settings':
          import beans
          self.page().mainFrame().addToJavaScriptWindowObject('settingsBean', beans.manager().settingsBean)
        return
    super(WbWebView, self).load(url)

  def injectAnnot(self): self.page().injectAnnot()
  def isAnnotEnabled(self): return self.page().isAnnotEnabled()
  def setAnnotEnabled(self, t): self.page().setAnnotEnabled(t)

  def injectSite(self): self.page().injectSite()
  def isSiteEnabled(self): return self.page().isSiteEnabled()
  def setSiteEnabled(self, t): self.page().setSiteEnabled(t)

@Q_Q
class _WbWebView(object):

  def __init__(self, q):
    page = q.page()
    page.loadStarted.connect(self._onLoadStarted)
    page.loadFinished.connect(self._onLoadFinished)

  def _showMessage(self, t): # unicode ->
    self.q.messageReceived.emit(t)

  def showZoomMessage(self):
    z = self.q.zoomFactor()
    t = "%s %i%%" % (tr_("Zoom"), int(z * 100))
    self._showMessage(t)

  def _onLoadStarted(self):
    self.q.setCursor(Qt.BusyCursor)
  def _onLoadFinished(self, success): # bool ->
    self.q.setCursor(Qt.ArrowCursor)

## WbWebPage ##

class WbWebPage(skwebkit.SkWebPage):
  def __init__(self, parent=None):
    super(WbWebPage, self).__init__(parent)
    self.__d = _WbWebPage(self)

    # 3/22/2014: FIXME
    # If I use DelegateNoLinks, linkClicked will not emit
    # Otherwise when disabled, createWindow will not be called
    #self.setLinkDelegationPolicy(QWebPage.DelegateAllLinks) # handle all links
    self.setLinkDelegationPolicy(QWebPage.DelegateAllLinks)

    self.linkClicked.connect(self.openUrl)

    self.linkHovered.connect(self.setHoveredLink)

  linkClickedWithModifiers = Signal(unicode)

  def hoveredLink(self): return self.__d.hoveredLink
  def setHoveredLink(self, v): self.__d.hoveredLink = v

  def progress(self): return self.__d.progress # -> int [0,100]
  def isLoading(self): return self.__d.progress < 100
  def isFinished(self): return self.__d.progress == 100

  def event(self, ev): # override
    if (ev.type() == QEvent.MouseButtonRelease and
        ev.button() == Qt.LeftButton and ev.modifiers() == Qt.ControlModifier and
        self.__d.hoveredLink):
      self.linkClickedWithModifiers.emit(self.__d.hoveredLink)
      ev.accept()
      return True
    return super(WbWebPage, self).event(ev)

  def openUrl(self, url): # QUrl
    self.mainFrame().load(url)

  # Inject

  def injectAnnot(self):
    if self.__d.canInject(): self.__d.annot.injectJavaScript()
  def isAnnotEnabled(self): return self.__d.annot.enabled
  def setAnnotEnabled(self, t): self.__d.annot.enabled = t

  def injectSite(self):
    if self.__d.canInject(): self.__d.site.injectJavaScript()
  def isSiteEnabled(self): return self.__d.site.enabled
  def setSiteEnabled(self, t): self.__d.site.enabled = t

  ## Extensions

  # bool supportsExtension(Extension extension) const
  def supportsExtension(self, extension): # override
    if extension == QWebPage.ErrorPageExtension:
      return True
    return super(WbWebPage, self).supportsExtension(extension)

  #bool extension(Extension extension, const ExtensionOption *option, ExtensionReturn *output)
  def extension(self, extension, option, output): # override
    if extension == QWebPage.ErrorPageExtension and self.errorPageExtension(option, output):
      return True
    return super(WbWebPage, self).extension(extension, option, output)

  #bool errorPageExtension(const ErrorPageExtensionOption *option, ErrorPageExtensionReturn *output) # override
  def errorPageExtension(self, option, output): # override
    if not option or not output:
      return False
    dprint("enter: error = %s, message = %s" % (option.error, option.errorString))
    output.encoding = "UTF-8" # force UTF-8
    #output.baseUrl = option.url # local url
    #output.contentType = "text/html" # already automaticly detected
    output.content = rc.jinja_template('error').render({
      'code': self.extensionErrorCode(option.error),
      'message': option.errorString,
      'url': option.url.toString(),
      'tr': tr_,
      'rc': rc,
    }).encode('utf8', 'ignore')
    return True

  @staticmethod
  def extensionErrorCode(error): # int -> int
    if error == 3:
      return 404
    else:
      return error

  # See: WebKit/qt/Api/qwebpage.cpp
  # Example: Mozilla/5.0 (Windows NT 6.1) AppleWebKit/534.34 (KHTML, like Gecko) MYAPP/MYVERSION Safari/534.34
  # QString userAgentForUrl(const QUrl &url) const
  def userAgentForUrl(self, url):
    """@override"""
    return config.USER_AGENT
    # Get rid of app name from user agent
    #ret = super(WbWebPage, self).userAgentForUrl(url)
    #return re.sub(r" \\S+ Safari/", " Safari/", ret)

@Q_Q
class _WbWebPage(object):

  def __init__(self, q):
    self.hoveredLink = ''

    self.progress = 100 # int [0,100]

    frame = q.mainFrame()
    self.annot = AnnotInjector(frame)
    self.site = SiteInjector(frame)

    frame.javaScriptWindowObjectCleared.connect(self._onJavaScriptCleared)

    q.loadProgress.connect(self._onLoadProgress)
    q.loadStarted.connect(self._onLoadStarted)
    q.loadFinished.connect(self._onLoadFinished)

  def _iterInjectors(self):
    yield self.site
    yield self.annot

  ## Progress

  def _onLoadProgress(self, value):
    self.progress = value # int ->
  def _onLoadStarted(self):
    self.progress = 0
  def _onLoadFinished(self, success): # bool ->
    self.progress = 100
    if success and self.canInject():
      for it in self._iterInjectors():
        if it.isEnabled():
          it.injectJavaScript()

  ## JavaScript

  def canInject(self):
    url = self.q.mainFrame().url()
    return not (url.isEmpty() or url.toString().startswith('about:'))

  def _onJavaScriptCleared(self):
    for it in self._iterInjectors():
      it.injected = False
      if it.isEnabled():
        it.injectBeans()

# EOF
