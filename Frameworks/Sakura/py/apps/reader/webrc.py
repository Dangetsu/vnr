# coding: utf8
# webrc.py
# 7/10/2013 jichi

from sakurakit.skdebug import dprint
import config

def update_web_settings(settings=None):
  """
  @param  settings  QWebSettings or None
  """
  # FIXME: This has no effect!
  # 9/6/2014: I have to modify bool SecurityOrigin::canRequest(const KURL& url) const in order to disable it.
  # See: http://qt-project.org/forums/viewthread/31888
  #
  # When combined with QWebSettings.LocalContentCanAccess*, it will by pass same-domain constraints
  #from PySide.QtWebKit import QWebSecurityOrigin
  #for scheme in 'http', 'https':
  #  QWebSecurityOrigin.addLocalScheme(scheme)
  #dprint("local security origin schemes:", QWebSecurityOrigin.localSchemes())

  from PySide.QtWebKit import QWebSettings
  import rc
  ws = settings or QWebSettings.globalSettings()
  ws.setAttribute(QWebSettings.PluginsEnabled, True)
  ws.setAttribute(QWebSettings.JavaEnabled, True)
  ws.setAttribute(QWebSettings.DnsPrefetchEnabled, True) # better performance

  ws.setAttribute(QWebSettings.JavascriptCanOpenWindows, True)
  ws.setAttribute(QWebSettings.JavascriptCanAccessClipboard, True)

  # Only enable this when debugging
  if config.APP_DEBUG:
    ws.setAttribute(QWebSettings.DeveloperExtrasEnabled, True)

  ws.setAttribute(QWebSettings.OfflineStorageDatabaseEnabled, True)
  ws.setAttribute(QWebSettings.OfflineWebApplicationCacheEnabled, True)

  ws.setAttribute(QWebSettings.LocalStorageEnabled, True)
  ws.setAttribute(QWebSettings.LocalContentCanAccessRemoteUrls, True)
  ws.setAttribute(QWebSettings.LocalContentCanAccessFileUrls, True)
  #ws.setAttribute(QWebSettings.LocalContentCanAccessFileUrls, False) # needed by same-origin-policy

  ws.setAttribute(QWebSettings.ZoomTextOnly, False)

  #ws.setDefaultTextEncoding("SHIFT-JIS")

  cachedir = rc.DIR_CACHE_WEB # Qt will automaticaly create this folder if not exist

  ws.setLocalStoragePath(cachedir)
  ws.setIconDatabasePath(cachedir)
  ws.setOfflineStoragePath(cachedir)
  ws.setOfflineWebApplicationCachePath(cachedir)

  # See: http://webkit.org/blog/427/webkit-page-cache-i-the-basics/
  #QWebSettings.setMaximumPagesInCache(30) # default is 0

  dprint("pass")

INIT = False
def init():
  global INIT
  if not INIT:
    update_web_settings()
    INIT = True

# EOF
