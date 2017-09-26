# coding: utf8
# webrc.py
# 7/10/2013 jichi

from sakurakit.skdebug import dprint

def update_web_settings(settings=None):
  """
  @param  settings  QWebSettings or None
  """
  from PySide.QtWebKit import QWebSettings, QWebSecurityOrigin
  import rc

  # When combined with QWebSettings.LocalContentCanAccess*, it will by pass same-domain constraints
  dprint("disable same origin principal")
  for scheme in 'http', 'https':
    QWebSecurityOrigin.addLocalScheme(scheme)
  #QWebSecurityOrigin.removeLocalScheme('qrc')
  #dprint("local security origin schemes:", QWebSecurityOrigin.localSchemes())

  ws = settings or QWebSettings.globalSettings()
  ws.setAttribute(QWebSettings.PluginsEnabled, True)
  ws.setAttribute(QWebSettings.JavaEnabled, True)
  ws.setAttribute(QWebSettings.DnsPrefetchEnabled, True) # better performance

  ws.setAttribute(QWebSettings.JavascriptCanOpenWindows, True)
  ws.setAttribute(QWebSettings.JavascriptCanAccessClipboard, True)

  # Always enabled
  #if config.APP_DEBUG:
  ws.setAttribute(QWebSettings.DeveloperExtrasEnabled, True)

  ws.setAttribute(QWebSettings.OfflineStorageDatabaseEnabled, True)
  ws.setAttribute(QWebSettings.OfflineWebApplicationCacheEnabled, True)

  ws.setAttribute(QWebSettings.LocalStorageEnabled, True)
  ws.setAttribute(QWebSettings.LocalContentCanAccessRemoteUrls, True)

  ws.setAttribute(QWebSettings.ZoomTextOnly, False)

  #ws.setDefaultTextEncoding("SHIFT-JIS")

  cachedir = rc.DIR_CACHE_WEBKIT # Qt will automatically create this folder if not exist

  ws.setLocalStoragePath(cachedir)
  ws.setIconDatabasePath(cachedir)
  ws.setOfflineStoragePath(cachedir)
  ws.setOfflineWebApplicationCachePath(cachedir)

  # See: http://webkit.org/blog/427/webkit-page-cache-i-the-basics/
  #QWebSettings.setMaximumPagesInCache(100) # default is 0

  dprint("pass")

INIT = False
def init():
  global INIT
  if not INIT:
    update_web_settings()
    INIT = True

# EOF
