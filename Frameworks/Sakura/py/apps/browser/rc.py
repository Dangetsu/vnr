# coding: utf8
# rc.py
# 12/13/2012 jichi
# Runtime resource locations

import os, sys
import jinja2
from PySide.QtCore import QUrl
from sakurakit import skos, skpaths
import config, cacheman

DIR_USER = (config.USER_PROFILES[skos.name]
    .replace('$HOME', skpaths.HOME)
    .replace('$APPDATA', skpaths.APPDATA))

DIR_USER_CACHE = DIR_USER + '/caches'       # $user/caches

DIR_CACHE_DATA = DIR_USER_CACHE + '/data'       # $user/caches/data
DIR_CACHE_HISTORY = DIR_USER_CACHE + '/history' # $user/caches/history
DIR_CACHE_NETMAN = DIR_USER_CACHE + '/netman'   # $user/caches/netman
DIR_CACHE_WEBKIT = DIR_USER_CACHE + '/webkit'   # $user/caches/webkit

COOKIES_LOCATION = DIR_CACHE_HISTORY + '/cookies'  # $user/caches/history/cookies
TABS_LOCATION = DIR_CACHE_HISTORY + '/tabs.txt'     # $user/caches/history/tabs.txt
VISIT_HISTORY_LOCATION = DIR_CACHE_HISTORY + '/visit.txt' # $user/caches/history/visit.txt
CLOSE_HISTORY_LOCATION = DIR_CACHE_HISTORY + '/close.txt' # $user/caches/history/close.txt

# Image locations

def icon(name):
  """
  @param  name  str  id
  @return  QIcon
  @throw  KeyError  when unknown name
  """
  from PySide.QtGui import QIcon
  return QIcon(config.ICON_LOCATIONS[name])

def standard_icon(key): # QStyle::StandardPixmap -> QIcon
  from PySide.QtCore import QCoreApplication
  return QCoreApplication.instance().style().standardIcon(key)

def image_path(name):
  """
  @param  name  str  id
  @return  unicode
  @throw  KeyError  when unknown name
  """
  return config.IMAGE_LOCATIONS[name]

def image_url(name):
  """
  @param  name  str  id
  @return  unicode
  @throw  KeyError  when unknown name
  """
  return QUrl.fromLocalFile(
      os.path.abspath(image_path(name))).toString()

NULL_IMAGE_URL = image_url('empty')

def wallpaper_url():
  import settings
  return settings.reader().wallpaperUrl() or image_url('wallpaper')

def qss_path(name):
  """
  @param  name  str  id
  @return  unicode
  @throw  KeyError  when unknown name
  """
  return config.QSS_LOCATIONS[name]

def qss(name):
  """
  @param  name  str  id
  @return  unicode
  @throw  KeyError  when unknown name
  """
  from sakurakit import skfileio
  return skfileio.readfile(qss_path(name)).replace('$PWD', config.root_abspath())

def cdn_path(name):
  """
  @param  name  str  id
  @return  unicode
  @throw  KeyError  when unknown name
  """
  return config.CDN[name].replace('$PWD', config.root_abspath())

def cdn_url(name):
  url = config.CDN[name]
  if '$PWD' in url:
    return 'file:///' + url.replace('$PWD', config.root_abspath())
  else:
    return cacheman.cache_url(url)

DMM_LOCALIZED_WELCOME_URL = cdn_url('dmm/localized_welcome')

CDN_DATA = {} # {str name:unicode data}
def cdn_data(name):
  """
  @param  name  str  id
  @return  unicode
  @throw  KeyError  when unknown name
  """
  ret = CDN_DATA.get(name)
  if not ret:
    from sakurakit import skfileio
    ret = CDN_DATA[name] = skfileio.readfile(cdn_path(name)).replace('$PWD', config.root_abspath())
  return ret

#_MAX_CACHE_NAME_LENGTH = 32
def data_cache_path(key):
  """
  @param  key  unicode
  @return  unicode  path
  @nothrow
  """
  import hashutil
  name = hashutil.urlsum(key)
  return "%s/%s" % (DIR_CACHE_DATA, name)

#js = cdn

# Webkit

from PySide.QtWebKit import QWebSettings
def url_icon(url):
  """
  @param  str|QUrl
  @return  QIcon not None
  """
  if not isinstance(url, QUrl) and '://' not in url:
    url = 'http://' + url
  return QWebSettings.iconForUrl(url) or icon('logo-browser')

# HAML Jinja

__jinja_loader = jinja2.FileSystemLoader(config.TEMPLATE_LOCATION)
JINJA = jinja2.Environment(
  loader = __jinja_loader,
  auto_reload = False,  # do not check if the template file is modified
  extensions = config.JINJA_HAML['extensions'],
)

JINJA_TEMPLATES = {} # {str name:jinja_template}
def jinja_template(name):
  """
  @param  name  str  id
  @return  jinjia2.template  path
  @throw  KeyError  when unknown name
  """
  key = 'haml/browser/' + name
  ret = JINJA_TEMPLATES.get(key)
  if not ret:
    ret = JINJA_TEMPLATES[key] = JINJA.get_template(config.TEMPLATE_ENTRIES[key])
  return ret

URL_TEMPLATE = {
  'about:blank': 'start',
  #'about:error': 'error',
  'about:help': 'help',
  'about:settings': 'settings',
  'about:version': 'about',
}
HTML_DATA = {} # {str url:unicode data}
def html_data(url): # QUrl|str -> unicode|None
  if isinstance(url, QUrl):
    url = url.toString()
  ret = HTML_DATA.get(url)
  if not ret:
    key = URL_TEMPLATE.get(url)
    if key:
      from sakurakit.sktr import tr_
      params = {
        'cache': cacheman.CacheApi,
        'tr': tr_,
        'rc': sys.modules[__name__],
      }
      if key == 'about':
        import i18nutil, settings
        t = settings.global_().version()
        params['version'] = i18nutil.timestamp2datetime(t)
      elif key == 'settings':
        import settings
        params['settings'] = settings.global_()
        params['reader'] = settings.reader()
      ret = HTML_DATA[url] = jinja_template(key).render(params) # unicode html
  return ret

# EOF
