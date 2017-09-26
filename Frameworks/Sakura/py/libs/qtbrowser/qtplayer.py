# coding: utf8
# qtplayer.py
# 10/1/2014 jichi

__all__ = 'HiddenPlayer',

from PySide.QtCore import QUrl
from sakurakit.skdebug import dprint

class _HiddenPlayer:
  def __init__(self, parent):
    self.parent = parent # QWidget
    self._webView = None # QWebView

  @property
  def webView(self):
    if not self._webView:
      dprint("create web view")
      from PySide.QtWebKit import QWebView
      self._webView = QWebView(self.parent)
      update_web_settings(self._webView.settings())
      self._webView.resize(0, 0) # zero size
    return self._webView

  def setParent(self, value):
    self.parent = value
    if self._webView:
      self._webView.setParent(value)

  def stop(self):
    if self._webView:
      self._webView.stop()

class HiddenPlayer(object):
  def __init__(self, parent=None):
    self.__d = _HiddenPlayer(parent)

  def parentWidget(self): return self.__d.parent
  def setParentWidget(self, value): self.__d.setParent(value)

  def webView(self): return self.__d.webView

  def stop(self):
    self.__d.stop()

  def play(self, url, **kwargs):
    """
    @param  url  str or QUrl
    """
    if not isinstance(url, QUrl):
      url = QUrl(url)
    for k,v in kwargs.iteritems():
      #url.addQueryItem(k, v)
      if not isinstance(v, basestring):
        v = "%s" % v
      url.addEncodedQueryItem(k, QUrl.toPercentEncoding(v))
    self.__d.webView.load(url)

def update_web_settings(settings=None):
  """
  @param  settings  QWebSettings or None
  """
  from PySide.QtWebKit import QWebSettings
  ws = settings or QWebSettings.globalSettings()
  ws.setAttribute(QWebSettings.PluginsEnabled, True)
  ws.setAttribute(QWebSettings.JavaEnabled, True)
  ws.setAttribute(QWebSettings.DnsPrefetchEnabled, True) # better performance

  ws.setAttribute(QWebSettings.AutoLoadImages, False) # do NOT load images

  #ws.setAttribute(QWebSettings.JavascriptCanOpenWindows, True)
  #ws.setAttribute(QWebSettings.JavascriptCanAccessClipboard, True)
  #ws.setAttribute(QWebSettings.DeveloperExtrasEnabled, True)

  #ws.setAttribute(QWebSettings.OfflineStorageDatabaseEnabled, True)
  #ws.setAttribute(QWebSettings.OfflineWebApplicationCacheEnabled, True)

  #ws.setAttribute(QWebSettings.LocalStorageEnabled, True)
  #ws.setAttribute(QWebSettings.LocalContentCanAccessRemoteUrls, True)

  #ws.setAttribute(QWebSettings.ZoomTextOnly, False)

  #ws.setDefaultTextEncoding("SHIFT-JIS")
  #ws.setDefaultTextEncoding("EUC-JP")

  #ws.setLocalStoragePath(G_PATH_CACHES)
  #QWebSettings.setIconDatabasePath(G_PATH_CACHES)
  #QWebSettings.setOfflineStoragePath(G_PATH_CACHES)
  #QWebSettings.setOfflineWebApplicationCachePath(G_PATH_CACHES)

  # See: http://webkit.org/blog/427/webkit-page-cache-i-the-basics/
  ws.setMaximumPagesInCache(10) # do not cache lots of pages

# EOF
