# coding: utf8
# rc.py
# 10/8/2012 jichi
# Runtime resource locations

import os, plistlib
import enchant, jinja2
#from rcssmin import cssmin
from PySide.QtCore import QUrl
from PySide.QtGui import QIcon
from Qt5.QtWidgets import QFileIconProvider
from sakurakit import skfileio, skos, skpaths, sktr
from sakurakit.skdebug import dwarn
import cacheman, config, defs, hashutil

# Directories

#DIR_SAKURA      = '../../..'           # /Library/Frameworks/Sakura

#ROOT_LOCATION = os.path.join(os.path.dirname(__file__), '../../..')
RELDIR_APP = '../../../../../..'
DIR_APP = os.path.abspath(os.path.join(os.path.dirname(__file__), RELDIR_APP))
DIR_APP_LIBRARY = DIR_APP + '/Library'
DIR_APP_CACHE = DIR_APP + '/Caches'

DIR_TMP = DIR_APP_CACHE + '/tmp'# $app/Caches/tmp

DIR_APP_TMP = DIR_TMP + '/reader'

DIR_TMP_OCR = DIR_APP_TMP + '/ocr'   # $app/Caches/tmp/reader/ocr
DIR_TMP_TERM = DIR_APP_TMP + '/dict' # $app/Caches/tmp/reader/dict
DIR_TMP_TTS = DIR_APP_TMP + '/tts'   # $app/Caches/tmp/reader/tts

#DIR_TMP_TRANSCAT = DIR_APP_TMP + '/transcat' # $app/Caches/tmp/reader/transcat

#DIR_PLUGIN      = DIR_SAKURA + '/userplugin'    # Sakura/userplugin
#DIR_PLUGIN_PY   = DIR_PLUGIN + '/py/1' # userplugin/py/1
#DIR_PLUGIN_JS   = DIR_PLUGIN + '/js/1' # userplugin/js/1

DIR_USER = (config.USER_PROFILES[skos.name]
    .replace('$HOME', skpaths.HOME)
    .replace('$APPDATA', skpaths.APPDATA))

DIR_USER_DATA   = DIR_USER + '/data/1' # $user/data/1, unicode, pickle format data
DIR_USER_XML    = DIR_USER + '/xml/1'  # $user/xml/1, unicode, cached xml data

DIR_XML_VOICE = DIR_USER_XML + '/voices'        # $user/xml/1/voices, unicode
DIR_XML_REF = DIR_USER_XML + '/refs'            # $user/xml/1/refs, unicode

#DIR_USER_PY     = DIR_USER + '/py/1'   # $user/py/1, unicode, user py plugin
#DIR_USER_JS     = DIR_USER + '/js/1'   # $user/js/1, unicode, user javascript plugin

#DIR_USER_DB = DIR_USER + '/db'                  # $user/db
#DIR_DB_LINGOES = DIR_USER_DB + '/lingoes'       # $user/db/lingoes

DIR_USER_CACHE = DIR_USER + '/caches'           # $user/caches
DIR_CACHE_AVATAR = DIR_USER_CACHE + '/avatars'  # $user/caches/avatars
DIR_CACHE_WEB = DIR_USER_CACHE + '/webkit'      # $user/caches/webkit
DIR_CACHE_AWS = DIR_USER_CACHE + '/amazon'      # $user/caches/amazon
DIR_CACHE_DMM = DIR_USER_CACHE + '/dmm'         # $user/caches/dmm
DIR_CACHE_TOKUTEN = DIR_USER_CACHE + '/tokuten' # $user/caches/tokuten
DIR_CACHE_TRAILERS = DIR_USER_CACHE + '/trailers' # $user/caches/trailers
DIR_CACHE_SCAPE = DIR_USER_CACHE + '/scape'     # $user/caches/scape
DIR_CACHE_FREEM = DIR_USER_CACHE + '/freem'     # $user/caches/freem
DIR_CACHE_STEAM = DIR_USER_CACHE + '/steam'     # $user/caches/steam
DIR_CACHE_MELON = DIR_USER_CACHE + '/melon'     # $user/caches/melon
DIR_CACHE_GETCHU = DIR_USER_CACHE + '/getchu'   # $user/caches/getchu
DIR_CACHE_GYUTTO = DIR_USER_CACHE + '/gyutto'   # $user/caches/gyutto
DIR_CACHE_DIGIKET = DIR_USER_CACHE + '/digiket'   # $user/caches/digiket
DIR_CACHE_DLSITE = DIR_USER_CACHE + '/dlsite'   # $user/caches/dlsite
DIR_CACHE_HOLYSEAL = DIR_USER_CACHE + '/holyseal' # $user/caches/holyseal
DIR_CACHE_DATA = DIR_USER_CACHE + '/data'       # $user/caches/data

#DIR_CACHE_IMAGE = DIR_USER_CACHE + '/images'   # $user/caches/images
DIR_CACHE_IMAGE = DIR_APP_CACHE + '/Images'     # $app/Caches/Images

DIR_CACHE_DICT = DIR_APP_CACHE + '/Dictionaries'# $app/Caches/Dictionaries
DIR_CACHE_INST = DIR_APP_CACHE + '/Installers'# $app/Caches/Installers
#DIR_DICT_MECAB = DIR_CACHE_DICT + '/MeCab'      # $app/Caches/Dictionaries/MeCab

#DIR_XML_COMMENT = DIR_USER_XML + '/comments'   # $user/xml/1/comments, unicode

DIR_CACHE_SUB = DIR_APP_CACHE + '/Subtitles'    # $app/Caches/Subtitles

DIR_CACHE_SYNC = DIR_APP_CACHE + '/Sync'        # $app/Caches/Sync

DIR_XML_COMMENT = DIR_CACHE_SUB + '/xml'        # $app/Caches/Subtitles/xml
DIR_YAML_SUB = DIR_CACHE_SUB + '/yaml'          # $app/Caches/Subtitles/yaml

# Dictionaries

DIR_UNIDIC = DIR_CACHE_DICT + "/UniDic"

EDICT_PATH = DIR_CACHE_DICT + "/EDICT/edict.db"
MECAB_EDICT_PATH = DIR_CACHE_DICT + "/EDICT/edict.dic"

def kanjidic_path(lang):
  file = 'kanjidic' if lang == 'en' else 'kanjidic_%s' % lang
  return DIR_CACHE_DICT + "/KanjiDic/" + file

# Apps

def app_path(name):
  """
  @param  name  str  id
  @return  unicode  path
  @throw  KeyError when unknown name
  """
  return config.APP_LOCATIONS[name]

# Data

#DATA_PATHS = {
#  #'gamemd5': DIR_USER_DATA + '/gamemd5.p',    # $user/data/1/gamemd5.p
#  'gamedigest': DIR_USER_DATA + '/gamedigest.p',    # $user/data/1/gamedigest.p
#}
#
#def data_path(name):
#  """
#  @param  name  str  id
#  @return  unicode  path
#  @throw  KeyError when unknown name
#  """
#  return DATA_PATHS[name]

# YAML

def yaml_path(name):
  """
  @return  QUrl
  @throw  KeyError  when unknown name
  """
  return config.YAML_LOCATIONS[name]

# XMLs

XML_PATHS = {
  'games': DIR_USER_XML + '/games.xml',  # $user/xml/1/games.xml, game library
  'gamefiles': DIR_USER_XML + '/gamefiles.xml',  # $user/xml/1/gamefiles.xml, game summary
  'gameitems': DIR_USER_XML + '/gameitems.xml',  # $user/xml/1/gameitems.xml, game summary
  #'refdigest': DIR_USER_XML + '/refdigest.xml',  # $user/xml/1/refdigest.xml, game summary
  'users': DIR_USER_XML + '/users.xml',  # $user/xml/1/users.xml, user library

  'terms': DIR_CACHE_SYNC + '/gamedic.xml',  # Caches/Sync/gamedic.xml, term library
}

def xml_path(name, backup=False):
  """
  @param  name  str  id
  @param  backup  bool
  @return  unicode  path
  @throw  KeyError when unknown name
  """
  ret = XML_PATHS[name]
  if backup:
    ret += defs.BACKUP_FILE_SUFFIX
  return ret

def comments_xml_path(md5):
  """
  @param  md5  str
  @return  unicode  path
  @nothrow
  """
  return "%s/%s.xml" % (DIR_XML_COMMENT, md5)

def voices_xml_path(md5):
  """
  @param  md5  str
  @return  unicode  path
  @nothrow
  """
  return "%s/%s.xml" % (DIR_XML_VOICE, md5)

def refs_xml_path(gameId):
  """
  @param  gameId  long
  @return  unicode  path
  @nothrow
  """
  return "%s/%s.xml" % (DIR_XML_REF, gameId)

def subs_yaml_path(itemId, subLang, gameLang='ja', fmt='yaml'):
  """
  @param  itemId  long
  @param  subLang  str
  @param  gameLang  str
  @return  unicode  path
  @nothrow
  """
  return "%s/%s.%s-%s.%s" % (DIR_YAML_SUB, itemId, gameLang[:2], subLang[:2], fmt)

# Terms

def term_path(type, to, fr):
  """
  @param  type  str  term type
  @param  to  str  target language
  @param  fr  str  source language
  @return  unicode  path
  @nothrow
  """
  return "%s/%s-%s/%s.txt" % (DIR_TMP_TERM, fr or 'ja', to or 'ja', type or 'none')

# TTS

def tts_path(url):
  """
  @param  type  str
  @param  language  str
  @param  text  unicode
  @return  unicode  path
  @nothrow
  """
  name = hashutil.urlsum(url)
  return "%s/%s.mp3" % (DIR_TMP_TTS, name)

# CDN

def cdn_url(key):
  """
  @param  key  str
  @return  unicode  url
  """
  url = config.CDN[key]
  if '$PWD' in url:
    return 'file:///' + url.replace('$PWD', config.root_abspath())
  else:
    return cacheman.cache_url(url)

# Images

def random_avatar_path(hash):
  """
  @param  hash  int
  @return  unicode
  """
  index = (hash or 0) % config.AVATARS_COUNT
  f = "%i.jpg" % index
  return os.path.join(config.AVATARS_LOCATION, f)

def avatar_image_path(token):
  """
  @param  token  unicode
  @return  unicode  path
  @nothrow
  """
  return "%s/%s" % (DIR_CACHE_AVATAR, token)

#_MAX_CACHE_NAME_LENGTH = 32
def data_cache_path(key):
  """
  @param  key  unicode
  @return  unicode  path
  @nothrow
  """
  name = hashutil.urlsum(key)
  return "%s/%s" % (DIR_CACHE_DATA, name)

def image_cache_path(key):
  """
  @param  key  unicode
  @return  unicode  path
  @nothrow
  """
  name = hashutil.urlsum(key)
  return "%s/%s.jpg" % (DIR_CACHE_IMAGE, name)

# Templates

# This will not escape encoded value
#def finalize_none_empty(value):
#  return value if value is None else u''

# See: http://jinja.pocoo.org/docs/api/

__jinja_loader = jinja2.FileSystemLoader(config.TEMPLATE_LOCATION)

jinja = jinja2.Environment(
  loader = __jinja_loader,
  #finalize = finalize_none_empty, # render None as '' instead of 'None'
  auto_reload = False,  # do not check if the template file is modified
  line_statement_prefix = config.JINJA['line_statement_prefix'],
  line_comment_prefix = config.JINJA['line_comment_prefix'],
  extensions = config.JINJA['extensions'],
)

jinja_haml = jinja2.Environment(
  loader = __jinja_loader,
  auto_reload = False,  # do not check if the template file is modified
  extensions = config.JINJA_HAML['extensions'],
)

TEMPLATES = {} # {str name:jinja_template}
def jinja_template(name):
  """
  @param  name  str  id
  @return  jinjia2.template  path
  @throw  KeyError  when unknown name
  """
  ret = TEMPLATES.get(name)
  if not ret:
    ret = TEMPLATES[name] = jinja.get_template(config.TEMPLATE_ENTRIES[name])
  return ret

def jinja_template_write(path, template_key, **context):
  """
  @param  path  str  id
  @param  template_key  str
  @return  jinjia2.template  path
  @return  bool
  """
  t = jinja_template(template_key)
  rv = t.stream(context)
  rv.enable_buffering(100) # yield every 100 string
  return skfileio.iterwritefile(path, rv, flush=False)

def jinja_template_write_xml(key, **context):
  """
  @param  key  str  id
  @return  jinjia2.template  path
  @return  bool
  """
  xmlfile = xml_path(key)
  xmltpl = 'xml/' + key
  return jinja_template_write(xmlfile, xmltpl, **context)

HAML_TEMPLATES = {} # {str name:jinja_template}
def haml_template(name):
  """
  @param  name  str  id
  @return  jinjia2.template  path
  @throw  KeyError  when unknown name
  """
  ret = HAML_TEMPLATES.get(name)
  if not ret:
    ret = HAML_TEMPLATES[name] = jinja_haml.get_template(config.TEMPLATE_ENTRIES[name])
  return ret

# Spells

ENCHANT_DICT = {} # {str lang : enchant.Dict()}
#atexit.register(ENCHANT_DICT.clear)
def enchant_dict(lang):
  try: return ENCHANT_DICT[lang]
  except KeyError:
    try:
      locale = config.LANGUAGE_SPELLS[lang]
      ret = enchant.Dict(locale)
    except KeyError:
      ret = None
      dwarn("failed to get spell dict for language: %s" % lang)
    ENCHANT_DICT[lang] = ret
    return ret

# EB gaiji map

def gaiji_path(name):
  """
  @param  name  unicode
  @return  unicode
  @throw  KeyError  when unknown name
  """
  key = 'plist/%s' % name.lower()
  return config.GAIJI_LOCATIONS[key]

GAIJI = {} # {key:gaiji_dict}
def gaiji_dict(name):
  """
  @param  name  unicode
  @return  {str key:unicode gaiji} not None
  @throw  KeyError  when unknown name
  """
  ret = GAIJI.get(name)
  if ret is None:
    path = gaiji_path(name)
    ret = {}
    if path:
      try: ret = plistlib.readPlist(path) # may raise if there are illegal characters in gaiji
      except Exception, e: dwarn(e)
    GAIJI[name] = ret
  return ret

#def trdb_path(key, fr, to):
#  """
#  @param  key  str
#  @param  fr  str  language
#  @param  to  str  language
#  @return  unicode  path
#  """
#  return "%s/%s-%s.db" % (config.TRDB_LOCATIONS[key], fr, to)

# Lingoes
#def lingoes_path(lang):
#  """Return icon for the specific file
#  @param  lang  str  such as ja-zh
#  @return  QIcon not None
#  @nothrow
#  """
#  return "%s/%s.db" % (config.LINGOES_LOCATION, lang)

# QML scripts

def qml_url(name):
  """
  @param  name  unicode
  @return  QUrl
  @throw  KeyError  when unknown name
  """
  return QUrl.fromLocalFile(config.QML_LOCATIONS[name])

# QSS

def qss_path(name):
  """
  @param  name  unicode  id
  @return  unicode
  @throw  KeyError  when unknown name
  """
  return config.QSS_LOCATIONS[name]

def qss(name):
  """
  @param  name  unicode  id
  @return  unicode  qss file content
  @throw  KeyError  when unknown name

  The return string  is not cached.
  """
  #return cssmin(skfileio.readfile(qss_path(name)))
  return skfileio.readfile(qss_path(name)).replace('$PWD', config.root_abspath())

# Image locations

def icon(name):
  """
  @param  name  str  id
  @return  QIcon
  @throw  KeyError  when unknown name
  """
  return QIcon(config.ICON_LOCATIONS[name])

def image_path(name):
  """
  @param  name  str  id
  @return  QIcon not None
  @throw  KeyError  when unknown name
  """
  return config.IMAGE_LOCATIONS[name]

def image_url(name):
  """
  @param  name  str  id
  @return  QUrl not None
  @throw  KeyError  when unknown name
  """
  return QUrl.fromLocalFile(
      os.path.abspath(image_path(name)))

def wallpaper_url():
  """
  @return  unicode not None
  """
  import settings
  return settings.global_().springBoardWallpaperUrl() or image_url('wallpaper').toString()

FILE_ICON_PROVIDER = QFileIconProvider()
def file_icon(path):
  """Return icon for the specific file
  @param  path  unicode
  @return  QIcon not None
  @nothrow
  """
  path = defs.recover_exe_bin_suffix(path) or path
  return FILE_ICON_PROVIDER.icon(path)

# Sakuradite Wiki
def wiki_url(name, language=''):
  """
  @param  name  str
  @param* language  str
  @return  str  URL
  """
  topic = name.replace(' ', '_')
  lang2 = 'zh' if language and language.startswith('zh') else 'en'
  locale = 'zh_CN' if language == 'zhs' else 'zh_TW' if language == 'zht' else lang2
  #import features
  #host = '210.175.54.32' if features.MAINLAND_CHINA else 'sakuradite.com'
  return "http://sakuradite.com/wiki/%s/%s?locale=%s" % (lang2, topic, locale)

# EOF

# Lingoes dictionaries
#LD = {}
#def lingoes_db(lang):
#  """Return icon for the specific file
#  @param  path  unicode
#  @return  QIcon not None
#  @nothrow
#  """
#  r = LD.get(lang)
#  if not r:
#    dbpath = os.path.join(DIR_DB_LINGOES, lang + '.db')
#    if not os.path.exists(dbpath):
#      r = None
#    else:
#      from lingoes.lingoesdb import LingoesDb
#      r = LingoesDb(dbpath)
#    LD[lang] = r
#  return r

#def lingoes_dict(lang):
#  """Return icon for the specific file
#  @param  path  unicode
#  @return  QIcon not None
#  @nothrow
#  """
#  r = LD.get(lang)
#  if not r:
#    yaml = config.LINGOES_DICTS.get(lang)
#    if yaml:
#      from lingoes.lingoesdict import LingoesDict
#      r = LD[lang] = LingoesDict(
#          config.parse_path(yaml['location']),
#          inenc=yaml['inenc'],
#          outenc=yaml['outenc'])
#  return r

# MeCab

#def mecab_usercsv_path(itemId, dicname):
#  """
#  @param  itemId  long
#  @param  dicname  unicode
#  @return  unicode  path
#  @nothrow
#  """
#  return "%s/%s/%s.csv" % (DIR_DICT_MECAB, dicname, itemId)

#def mecab_userdic_path(itemId, dicname):
#  """
#  @param  itemId  long
#  @param  dicname  unicode
#  @return  unicode  path
#  @nothrow
#  """
#  return "%s/%s/%s.dic" % (DIR_DICT_MECAB, dicname, itemId)

#def mecab_dic_path(name):
#  """
#  @param  str  name
#  @return  unicode  path
#  @throw  KeyError
#  """
#  # Use relative path to eliminate intermediate spaces
#  #return config.get_rel_path(DIR_CACHE_DICT) + '/' + config.MECAB_DICS[name] if name else ''
#  return config.MECAB_DICS[name] if name else ''

#def mecab_rc_path(name):
#  """
#  @param  str  name
#  @return  unicode  path
#  @throw  KeyError
#  """
#  return config.MECAB_RCFILES[name] if name else ''

#def cabocha_rc_path(name):
#  """
#  @param  str  name
#  @return  unicode  path
#  @throw  KeyError
#  """
#  return config.CABOCHA_RCFILES[name] if name else ''
