# coding: utf8
# converter.py
# 11/29/2013 jichi
# See: http://static.clipconverter.cc/inc/min/b=js&f=converter.js

__all__ = 'YouTubeSolver',

if __name__ == '__main__': # DEBUG
  import debug
  debug.initenv()

from PySide.QtCore import Signal, QObject
from sakurakit import skstr
from sakurakit.skclass import Q_Q, memoizedproperty
from sakurakit.skdebug import dprint, dwarn
from tr import my
import growl

#ZERO_SIZE = 0, 0 # zero size would incur adblock failure on first load
#_VISIBLE_SIZE = 640, 480
#_HIDDEN_SIZE = 1, 1

class YouTubeSolver(QObject):

  def __init__(self, parent=None):
    super(YouTubeSolver, self).__init__(parent)
    self.__d = _YouTubeSolver(self)

    for sig in self.aborted, self.urlSolved:
      sig.connect(self.stop) #, Qt.QueuedConnection)

  def webView(self): return self.__d.webView
  def setWebView(self, v): self.__d.setWebView(v)

  def networkAccessManager(self): return self.__d.webView.page().networkAccessManager()
  def setNetworkAccessManager(self, v): self.__d.webView.page().setNetworkAccessManager(v)

  #def parentWidget(self): return self.__d.parentWidget
  #def setParentWidget(self, v):
  #  """
  #  @@param  v  QWidget
  #  """
  #  d = self.__d
  #  d.parentWidget = v
  #  if hasmemoizedproperty(d, 'webView'):
  #    d.webView.setParent(v)

  aborted = Signal() # unicode message
  urlSolved = Signal(unicode, unicode) # unicode URL, unicode title

  def solve(self, vid):
    """
    @param  vid  str  youtube id
    """
    d = self.__d
    url = d.makeurl(vid)
    w = d.webView
    w.load(url)

  def stop(self):
    dprint("enter")
    d = self.__d
    w = d.webView
    w.stop()
    #w.setContent("") # Not needed
    dprint("leave")

  #def isVisible(self):
  #  d = self.__d
  #  return hasmemoizedproperty(d, 'webView') and d.webView.isVisible()

  def setVisible(self, v):
    if v != self.isVisible():
      w = self.__d.webView
      #w.resize(*(_VISIBLE_SIZE if v else _HIDDEN_SIZE))
      #w.setVisible(v) # always visible

  def show(self): self.setVisible(True)
  def hide(self): self.setVisible(False)

@Q_Q
class _YouTubeSolver(object):

  def __init__(self):
    self._webView = None

  @property
  def webView(self):
    if not self._webView:
      from PySide.QtWebKit import QWebView
      self._setWebView(QWebView())
    return self._webView

  def setWebView(self, w):
    #w.setWindowFlags(Qt.Dialog) # This could crash the app?
    w.loadFinished.connect(self._onLoadFinished)
    #w.page().downloadRequested.connect(self._onDownloadRequest)
    #w.resize(*_HIDDEN_SIZE)
    self._webView = w

    ws = w.settings()
    from PySide.QtWebKit import QWebSettings
    ws.setAttribute(QWebSettings.DnsPrefetchEnabled, True) # better performance
    ws.setAttribute(QWebSettings.PluginsEnabled, False) # disable flash and quicktime
    ws.setAttribute(QWebSettings.AutoLoadImages, False) # do NOT load images

  def evaljs(self, js):
    """
    @param  js  unicode
    @return  QObject or None
    """
    # See: http://qt-project.org/doc/qt-5.0/qtwebkitexamples/webkitwidgets-fancybrowser.html
    f = self.webView.page().mainFrame()
    return f.evaluateJavaScript(js)

  def makeurl(self, vid):
    """
    @param  vid  str
    @return str
    """
    youtube_url = 'http://www.youtube.com/watch?v=%s' % vid
    dprint(youtube_url)
    #ref = 'addon'
    ref = 'bookmarklet'
    url = 'http://www.clipconverter.cc/?ref=%s&url=%s' % (ref, skstr.urlencode(youtube_url))
    return url

  # Search:
  # - addToJavaScriptWindowObject
  # - evaluateJavaScript
  def _onLoadFinished(self, ok):
    """
    @param  ok  bool
    """
    #js = "document.getElementById('converter').submit()" # Do not work well
    if not ok:
      dwarn("load failure")
      growl.warn("[solve] %s" % my.tr("waiting for the video page to be ready"))
      #self.q.aborted.emit()
    else:
      title = self.webView.title()
      if not title:
        dprint('ignore titleless empty page')
      else:
        dprint(title)
        growl.msg("[solve] %s: %s" % (my.tr("loading"), title.replace(' - ClipConverter.cc', '')))
        if title.startswith("Conversion:"):
          dprint("conversion")
        elif title == 'YouTube Video Converter and Download - ClipConverter.cc':
          js = "$('#0').attr('checked', true);$('#converter').submit(); null"
          self.evaljs(js)
        elif title.endswith(' - ClipConverter.cc'):
          name = title.replace(' - ClipConverter.cc', '')
          js = "$('#downloadbutton').attr('href')"
          url = self.evaljs(js)
          if url and isinstance(url, unicode) and url.startswith("http://"):
            dprint("solved:", url)
            self.q.urlSolved.emit(url, name)
          else:
            growl.warn("[solve] %s" % my.tr("failed to convert video format, abort"))
            growl.error("[solve] %s" % my.tr("abort"))
            self.q.aborted.emit()
        # (14%) Waiting_ [Comfort Women Song] 韓国人慰安婦の歌.mp4
        #elif title.startswith('('):
        else:
          dprint('ignored')

if __name__ == '__main__': # DEBUG
  a = debug.app()
  #vid = 'XGZ2S6pTkO8'
  vid = 'lmOZEAAEMK0'
  s = YouTubeSolver()
  s.solve(vid)
  for sig in s.urlSolved, s.aborted:
    sig.connect(a.quit)
  a.exec_()

# EOF
