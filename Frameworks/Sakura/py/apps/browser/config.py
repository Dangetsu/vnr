# coding: utf8
# config.py
# 12/13/2012 jichi
#
# This file must be self-contained.
# Be careful of unicode requirement for locations

import os

## YAML parsing ##

def u_from_native(s):
  # Following contents are copied from sakurakit.skunicode
  import locale
  lc, enc = locale.getdefaultlocale()
  return s.decode(enc, errors='ignore')

#def u8(s): return s.decode('utf8', errors='ignore')
u = u_from_native

# Python os.path.abspath has unicode issue
#ROOT_LOCATION = os.path.abspath(os.path.dirname(__file__) + "/../../..")
ROOT_LOCATION = os.path.dirname(__file__) + "/../../.."

# Delay loading Qt
def root_abspath():
  from PySide.QtCore import QDir
  return QDir.fromNativeSeparators(os.path.abspath(ROOT_LOCATION))

SHARE_YAML_LOCATION = os.path.join(ROOT_LOCATION, "share.yaml")
APP_YAML_LOCATION = os.path.join(ROOT_LOCATION, "browser.yaml")

ROOT_LOCATION_U = u(ROOT_LOCATION)

def load_yaml_file(path):
  import yaml
  return yaml.load(file(path, 'r'))

SHARE_YAML = load_yaml_file(SHARE_YAML_LOCATION)
APP_YAML = load_yaml_file(APP_YAML_LOCATION)

## Property parsing ##

def parse_path(p): return p.replace('$PWD', ROOT_LOCATION_U) # unicode path

def parse_int(s):
  """
  @param  s  str or unicode
  @return  int
  @throw  Exception by eval()
  """
  try: return int(s)
  except ValueError: return int(eval(str(s)))

##  Application version ##

APP_DEBUG = APP_YAML['app']['debug']

VERSION_ID = parse_int(APP_YAML['version']['id'])
VERSION_NAME = APP_YAML['version']['name']
VERSION_ORGANIZATION = APP_YAML['version']['organization']
VERSION_DOMAIN = APP_YAML['version']['domain']
VERSION_TIMESTAMP = long(APP_YAML['version']['timestamp'])

## Environment variables ##

ENV_PATH = map(parse_path, SHARE_YAML['env']['path']) # [unicode path]
ENV_PYTHONPATH = map(parse_path, SHARE_YAML['env']['pythonpath']) # [str path]

APP_PYTHONPATH = map(parse_path, APP_YAML['env']['pythonpath']) # [unicode abspath]

ENV_MECABRC = parse_path(SHARE_YAML['env']['mecabrc']) # unicode abspath

## Settings ##

QT_THREAD_COUNT = parse_int(APP_YAML['qt']['threadCount'])
QT_THREAD_TIMEOUT = parse_int(APP_YAML['qt']['threadTimeout'])

QT_STYLESHEETS = APP_YAML['qt']['css'] # [str name]

#QT_QUIT_TIMEOUT = parse_int(APP_YAML['qt']['quitTimeout'])

## History ##

VISIT_HISTORY_SIZE = APP_YAML['app']['visitHistorySize'] # int
CLOSE_HISTORY_SIZE = APP_YAML['app']['closeHistorySize'] # int
ADDRESS_HISTORY_SIZE = APP_YAML['app']['addressHistorySize'] # int

## User profile ##

# Paths are in str, but will be converted to unicode in rc.py as DIR_USER.
USER_PROFILES = APP_YAML['user']['profiles']

## WebKit ##

USER_AGENT = SHARE_YAML['webkit']['useragent']

## Translations ##

TR_LOCALES = APP_YAML['tr']['locales'] # [str locale_name]
TR_LOCATIONS = map(parse_path, APP_YAML['tr']['locations']) # [unicode path]

QT_TRANSLATIONS_LOCATION = parse_path(SHARE_YAML['qt']['tr'])  # unicode path

JCUSERDIC_LOCATIONS = map(parse_path, SHARE_YAML['jcuserdic']) # [unicode abspath]

## Languages ##

ENCODINGS = SHARE_YAML['encodings']   # [str enc]

ENCODING_SET = frozenset(ENCODINGS)
def is_valid_encoding(enc):
  return enc in ENCODING_SET

def check_valid_encoding(enc):
  if not is_valid_encoding(enc):
    raise ValueError("invalid encoding %s" % enc)

LANGUAGES = SHARE_YAML['languages']['all']# [str lang]
LANGUAGE_LOCALES = SHARE_YAML['locales']  # {str lang : str locale}

LANGUAGE_SET = frozenset(LANGUAGES)
def is_valid_language(lang): return lang in LANGUAGE_SET

def check_valid_language(lang):
  if not is_valid_language(lang):
    raise ValueError("invalid language %s" % lang)

def language2locale(lang):
  return LANGUAGE_LOCALES.get(lang) or ""

## Locations ##

OPENCC_DICS = {k: parse_path(v)  # {str name:unicode path}
    for k,v in SHARE_YAML['opencc'].iteritems()}

APP_LOCATIONS = {k: parse_path(v)   # {str name:unicode path}
    for k,v in SHARE_YAML['apps'].iteritems()}

QSS_LOCATIONS = {k: parse_path(v) # {str name:unicode path}
    for k,v in SHARE_YAML['qss'].iteritems()}

ICON_LOCATIONS = {k: parse_path(v)  # {str name:unicode path}
    for k,v in SHARE_YAML['icons'].iteritems()}

IMAGE_LOCATIONS = {k: parse_path(v) # {str name:unicode path}
    for k,v in SHARE_YAML['images'].iteritems()}

CURSOR_LOCATIONS = {k: parse_path(v) # {str name:unicode apspath}
    for k,v in SHARE_YAML['cursors'].iteritems()}

CDN = SHARE_YAML['cdn']
#CDN_LOCATIONS = {k: parse_path(v) # {str name:unicode apspath}
#    for k,v in SHARE_YAML['cdn'].iteritems()}

#MECAB_RCFILES = {k: parse_path(v) # {str name:unicode abspath}
#    for k,v in SHARE_YAML['mecab']['rcfile'].iteritems()}

## Jinja ##

JINJA_HAML = SHARE_YAML['jinja_haml']

TEMPLATE_LOCATION = parse_path(SHARE_YAML['templates']['location']) # unicode abspath
TEMPLATE_ENTRIES = SHARE_YAML['templates']['entries'] # {str name:unicode relpath}

## Proxy ##

PROXY_HOST = SHARE_YAML['proxies']['host']
PROXY_SITES = SHARE_YAML['proxies']['sites'] # {string key:string host}
PROXY_DOMAINS = SHARE_YAML['proxies']['domains'] # {string host:string ip}

GETCHU_HOST = SHARE_YAML['proxies']['getchu'].replace('http://', '')

PROXY_GETCHU_URL = SHARE_YAML['proxies']['getchu']
PROXY_KANCOLLE_URL = SHARE_YAML['proxies']['kancolle']

PROXY_DMM_JP_URL = SHARE_YAML['proxies']['dmm_jp']
PROXY_DMM_COM_URL = SHARE_YAML['proxies']['dmm_com']
#PROXY_DMM_COM_P_URL = SHARE_YAML['proxies']['dmm_com_p']


PROXY_DLSITE_URL = SHARE_YAML['proxies']['dlsite']
PROXY_DLSITE_IMG_URL = SHARE_YAML['proxies']['dlsite_img']

PROXY_TORANOANA_URL = SHARE_YAML['proxies']['toranoana']
PROXY_TORANOANA_IMG_URL = SHARE_YAML['proxies']['toranoana_img']

#PROXY_GOOGLE_SEARCH = _PROXY['googlesearch']
PROXY_GOOGLE_TRANS = SHARE_YAML['proxies']['googletrans']
PROXY_GOOGLE_TTS = SHARE_YAML['proxies']['googletts']

# EOF
