# coding: utf8
# config.py
# 11/1/2012 jichi
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

#def get_relpath(path): # unicode -> unicode
#  return os.path.relpath(os.path.abspath(path), os.getcwd())

#def u8(s): return s.decode('utf8', errors='ignore')
u = u_from_native

# Python os.path.abspath has unicode issue
#ROOT_LOCATION = os.path.abspath(os.path.dirname(__file__) + "/../../..")
ROOT_LOCATION = os.path.join(os.path.dirname(__file__), "../../..")

SHARE_YAML_LOCATION = os.path.join(ROOT_LOCATION, "share.yaml")
APP_YAML_LOCATION = os.path.join(ROOT_LOCATION, "reader.yaml")
BLACKLIST_YAML_LOCATION = os.path.join(ROOT_LOCATION, "yaml/blacklist.yaml")
BRANDS_YAML_LOCATION = os.path.join(ROOT_LOCATION, "yaml/brands.yaml")
ENGINES_YAML_LOCATION = os.path.join(ROOT_LOCATION, "yaml/engines.yaml")
#ZUNKO_YAML_LOCATION = os.path.join(ROOT_LOCATION, "yaml/zunko.yaml")

ROOT_LOCATION_U = u(ROOT_LOCATION)

def load_yaml_file(path):
  import yaml
  return yaml.load(file(path, 'r'))

SHARE_YAML = load_yaml_file(SHARE_YAML_LOCATION)
APP_YAML = load_yaml_file(APP_YAML_LOCATION)
BLACKLIST_YAML = load_yaml_file(BLACKLIST_YAML_LOCATION)
BRANDS_YAML = load_yaml_file(BRANDS_YAML_LOCATION)
ENGINES_YAML = load_yaml_file(ENGINES_YAML_LOCATION)

# Delay loading Qt
ROOT_ABSPATH = None
def root_abspath():
  global ROOT_ABSPATH
  if not ROOT_ABSPATH:
    from PySide.QtCore import QDir
    ROOT_ABSPATH = QDir.fromNativeSeparators(os.path.abspath(ROOT_LOCATION))
  return ROOT_ABSPATH

## Property parsers ##

def parse_path(path):
  """
  @param  path  unicode
  @return  unicode  absolute path
  """
  return path.replace('$PWD', ROOT_LOCATION_U)

#def parse_abspath(path):
#  """
#  @param  path  unicode
#  @return  unicode  absolute path
#  """
#  return os.path.abspath(parse_path(path))

def parse_int(s):
  """
  @param  s  str or unicode
  @return  int
  @throw  Exception by eval()
  """
  try: return int(s)
  except ValueError: return int(eval(str(s)))

def parse_float(s):
  """
  @param  s  str or unicode
  @return  float
  @throw  Exception by eval()
  """
  try: return float(s)
  except ValueError: return float(eval(str(s)))

## Blacklists ##

PROCESS_BLACKLIST = frozenset(BLACKLIST_YAML['processes'])
HCODE_BLACKLIST = frozenset(BLACKLIST_YAML['hcode'])
HCODE_FILE_BLACKLIST = frozenset(BLACKLIST_YAML['hcodefile'])

## Game engine ##

CHAR_TEXT_THREADS = frozenset(ENGINES_YAML['char']) # [str name]
WCHAR_TEXT_THREADS = frozenset(ENGINES_YAML['wchar']) # [str name]
UTF8_TEXT_THREADS = frozenset(ENGINES_YAML['utf8']) # [str name]

PSP_ALL_TEXT_THREADS = frozenset(ENGINES_YAML['psp']['all']) # [str name]
PSP_098_TEXT_THREADS = frozenset(ENGINES_YAML['psp']['0.9.8']) # [str name]
PSP_099_TEXT_THREADS = frozenset(ENGINES_YAML['psp']['0.9.9']) # [str name]

GUI_TEXT_THREADS = frozenset(ENGINES_YAML['gui']) # [str name]
OPT_GUI_TEXT_THREADS = frozenset(ENGINES_YAML['optgui']) # [str name]
NON_GUI_TEXT_THREADS = frozenset(ENGINES_YAML['nongui']) # [str name]

SLOW_GAME_ENGINES = frozenset(ENGINES_YAML['slow']) # [str name]
FAST_GAME_ENGINES = frozenset(ENGINES_YAML['fast']) # [str name]
DELAY_GAME_ENGINES = frozenset(ENGINES_YAML['delay']) # [str name]

REPEAT_GAME_ENGINES = frozenset(ENGINES_YAML['repeat']) # [str name]

FOCUS_GAME_ENGINES = frozenset(ENGINES_YAML['focus']) # [str name]

NOREPEAT_GAME_ENGINES = frozenset(ENGINES_YAML['simple'] + ENGINES_YAML['norepeat']) # [str name]
NOFLOAT_GAME_ENGINES = frozenset(
    ENGINES_YAML['simple'] + ENGINES_YAML['nofloat'] +
    ENGINES_YAML['gui'] + ENGINES_YAML['nongui']) # [str name]

RENAMED_GAME_ENGINES = ENGINES_YAML['rename']  # {str name:str name}

EMBEDDED_EN_GAME_ENGINES = ENGINES_YAML['embed_en'] # [str name]
EMBEDDED_GAME_ENGINES = ENGINES_YAML['embed'] + ENGINES_YAML['embed_en'] # [str name]

def game_thread_embeddable(name):
  """
  @param  name  str
  @return  bool
  """
  return bool(name) and (name in EMBEDDED_GAME_ENGINES or 'Embed' in name)

def guess_thread_encoding(name): # str -> str or None
  if name in CHAR_TEXT_THREADS:
    return 'SHIFT-JIS'
  if name in WCHAR_TEXT_THREADS:
    return 'UTF-16'
  if name in UTF8_TEXT_THREADS:
    return 'UTF-8'

## Game info ##

JUNAI_BRANDS = frozenset(BRANDS_YAML['junai'])
NUKI_BRANDS = frozenset(BRANDS_YAML['nuki'] + BRANDS_YAML['seminuki'])
OTOME_BRANDS = frozenset(BRANDS_YAML['otome'])

## Application version ##

APP_DEBUG = APP_YAML['app']['debug']

_VERSION = APP_YAML['version']
VERSION_ID = parse_int(_VERSION['id'])
VERSION_NAME = _VERSION['name']
VERSION_ORGANIZATION = _VERSION['organization']
VERSION_DOMAIN = _VERSION['domain']
VERSION_TIMESTAMP = int(_VERSION['timestamp'])

_APP = APP_YAML['app']

APP_GAME_QUERY_TIMEOUT = parse_int(_APP['gameQueryTimeout'])
APP_GAME_UPDATE_TIMEOUT = parse_int(_APP['gameUpdateTimeout'])
APP_ONLINE_TRANSLATION_TIMEOUT = parse_int(_APP['onlineTranslationTimeout'])

APP_UPDATE_INTERVAL = parse_int(_APP['updateInterval'])
APP_GREETING_INTERVAL = parse_int(_APP['greetingInterval'])
APP_SAVE_SETTINGS_INTERVAL = parse_int(_APP['saveSettingsInterval'])
APP_UPDATE_COMMENTS_INTERVAL = parse_int(_APP['updateCommentsInterval'])
APP_UPDATE_REFS_INTERVAL = parse_int(_APP['updateRefsInterval'])
APP_UPDATE_SUBS_INTERVAL = parse_int(_APP['updateSubsInterval'])
APP_UPDATE_TERMS_INTERVAL = parse_int(_APP['updateTermsInterval'])
APP_UPDATE_GAMES_INTERVAL = parse_int(_APP['updateGamesInterval'])
#APP_UPDATE_TAH_INTERVAL = parse_int(_APP['updateTAHInterval'])

APP_SOCKET_TYPE = _APP['socketType'] # str
APP_SOCKET_NAME = _APP['socketName'] # str
APP_SOCKET_PORT = parse_int(_APP['socketPort']) # int

VNRAGENT_MEMORY_KEY = APP_YAML['vnragent']['memoryKey']

REF_EXPIRE_TIME = parse_int(_APP['refExpireTime'])
NAME_EXPIRE_TIME = parse_int(_APP['nameExpireTime'])

_SETTINGS = APP_YAML['settings']
SETTINGS_TEXT_CAPACITY = parse_float(_SETTINGS['textCapacity'])

SETTINGS_ZOOM_FACTOR = parse_float(_SETTINGS['zoomFactor'])
SETTINGS_WIDTH_FACTOR = parse_float(_SETTINGS['widthFactor'])
SETTINGS_SHADOW_OPACITY = parse_float(_SETTINGS['shadowOpacity'])

SETTINGS_DICT_POPUP_WIDTH = parse_int(_SETTINGS['dictionaryPopupWidth'])

SETTINGS_FONT_COLOR = _SETTINGS['fontColor']
SETTINGS_SHADOW_COLOR = _SETTINGS['shadowColor']
SETTINGS_TEXT_COLOR = _SETTINGS['textColor']
SETTINGS_SUBTITLE_COLOR = _SETTINGS['subtitleColor']
SETTINGS_COMMENT_COLOR = _SETTINGS['commentColor']
SETTINGS_DANMAKU_COLOR = _SETTINGS['danmakuColor']

#SETTINGS_TRANSLATION_COLOR = _SETTINGS['translationColor']
SETTINGS_INFOSEEK_COLOR = _SETTINGS['infoseekColor']
SETTINGS_BABYLON_COLOR = _SETTINGS['babylonColor']
SETTINGS_EXCITE_COLOR = _SETTINGS['exciteColor']
SETTINGS_SYSTRAN_COLOR = _SETTINGS['systranColor']
SETTINGS_NIFTY_COLOR = _SETTINGS['niftyColor']
SETTINGS_BING_COLOR = _SETTINGS['bingColor']
SETTINGS_GOOGLE_COLOR = _SETTINGS['googleColor']
SETTINGS_NAVER_COLOR = _SETTINGS['naverColor']
SETTINGS_BAIDU_COLOR = _SETTINGS['baiduColor']
SETTINGS_YOUDAO_COLOR = _SETTINGS['youdaoColor']
SETTINGS_HANVIET_COLOR = _SETTINGS['hanVietColor']
SETTINGS_TRANSRU_COLOR = _SETTINGS['transruColor']
SETTINGS_VTRANS_COLOR = _SETTINGS['vtransColor']
SETTINGS_ROMAJI_COLOR = _SETTINGS['romajiColor']
SETTINGS_JBEIJING_COLOR = _SETTINGS['jbeijingColor']
SETTINGS_FASTAIT_COLOR = _SETTINGS['fastaitColor']
SETTINGS_DREYE_COLOR = _SETTINGS['dreyeColor']
SETTINGS_EZTRANS_COLOR = _SETTINGS['ezTransColor']
SETTINGS_TRANSCAT_COLOR = _SETTINGS['transcatColor']
SETTINGS_ATLAS_COLOR = _SETTINGS['atlasColor']
SETTINGS_LEC_COLOR = _SETTINGS['lecColor']
SETTINGS_LECONLINE_COLOR = _SETTINGS['lecOnlineColor']

## Environment variables ##

ENV_PATH = map(parse_path, SHARE_YAML['env']['path']) # [unicode abspath]
ENV_PYTHONPATH = map(parse_path, SHARE_YAML['env']['pythonpath']) # [unicode abspath]
#ENV_PYTHONPATH_XP = map(parse_path, SHARE_YAML['env']['xp']['pythonpath']) # [unicode abspath]

ENV_INTEGRITYPATH = map(parse_path, SHARE_YAML['env']['integritypath']) # [unicode abspath]

ENV_MECABRC = parse_path(SHARE_YAML['env']['mecabrc']) # unicode abspath

#APP_PATH = map(parse_path, APP_YAML['env']['path']) # [unicode abspath]
APP_PYTHONPATH = map(parse_path, APP_YAML['env']['pythonpath']) # [unicode abspath]

## URLs ##
API_HOST = SHARE_YAML['apis']['host']
API_REST = SHARE_YAML['apis']['rest']
API_PUSH = SHARE_YAML['apis']['push']
API_AJAX = SHARE_YAML['apis']['ajax']
API_CACHE = SHARE_YAML['apis']['cache']

URL_READER_DEMO = SHARE_YAML['urls']['reader_demo']

EMAIL_HELP = SHARE_YAML['emails']['help']

_PROXY = SHARE_YAML['proxies']

PROXY_HOST = _PROXY['host']

PROXY_JPWEBPROXY = _PROXY['jpwebproxy']
PROXY_USWEBPROXY = _PROXY['uswebproxy']

PROXY_BAIDU_FANYI = _PROXY['baidufanyi']
PROXY_BAIDU_TTS = _PROXY['baidutts']
PROXY_ICIBA = _PROXY['iciba']

PROXY_TWITTER_SEARCH = _PROXY['twittersearch']
PROXY_GOOGLE_SEARCH = _PROXY['googlesearch']
PROXY_GOOGLE_TRANS = _PROXY['googletrans']
PROXY_GOOGLE_TTS = _PROXY['googletts']
PROXY_GOOGLE_SR = _PROXY['googlesr']
PROXY_YTIMG_I = _PROXY['ytimg']['i']
PROXY_YTIMG_S = _PROXY['ytimg']['s']
PROXY_TWIMG_A = _PROXY['twimg']['a']
PROXY_TWIMG_PBS = _PROXY['twimg']['pbs']

PROXY_EROGAMESCAPE = _PROXY['erogamescape']
PROXY_DMM_JP = _PROXY['dmm_jp']
#PROXY_DMM_COM = _PROXY['dmm_com']
PROXY_GETCHU = _PROXY['getchu']
#PROXY_GETCHU_IP = _PROXY['getchu_ip']

PROXY_DLSITE = _PROXY['dlsite']
PROXY_DLSITE_IMG = _PROXY['dlsite_img']

PROXY_SITES = {v:k for k,v in _PROXY['sites'].iteritems()} # {string host url:string proxy key}
PROXY_DOMAINS = frozenset((it.replace('www.', '') for it in PROXY_SITES))

GOOGLE = SHARE_YAML['google']
GOOGLE_SEARCH = GOOGLE['search']
GOOGLE_YTIMG_I = GOOGLE['ytimg']['i']
GOOGLE_YTIMG_S = GOOGLE['ytimg']['s']

TWITTER = SHARE_YAML['twitter']
TWITTER_TWIMG_A = TWITTER['twimg']['a']
TWITTER_TWIMG_PBS = TWITTER['twimg']['pbs']
TWITTER_SEARCH = TWITTER['search']

#CDN = {k: parse_url(v) # {str name:unicode abspath}
#    for k,v in SHARE_YAML['cdn'].iteritems()}
CDN = SHARE_YAML['cdn']

## Keys ##

AWS_ACCESS_KEY = SHARE_YAML['amazon']['accessKey']
AWS_SECRET_KEY = SHARE_YAML['amazon']['secretKey']
AWS_ASSOCIATE_TAG = SHARE_YAML['amazon']['associateTag']
AWS_REGION = SHARE_YAML['amazon']['region']

DMM_API_ID = SHARE_YAML['dmm']['apiId']
DMM_AFFILIATE_ID = SHARE_YAML['dmm']['affiliateId']

## Settings ##

_QT = APP_YAML['qt']
QT_THREAD_COUNT = parse_int(_QT['threadCount'])
QT_THREAD_TIMEOUT = parse_int(_QT['threadTimeout'])

QT_STYLESHEETS = _QT['css'] # [str name]

#QT_QUIT_TIMEOUT = parse_int(_QT['quitTimeout'])

_PY = APP_YAML['py']
PY_SOCKET_TIMEOUT = parse_int(_PY['socketTimeout'])
PY_RECURSION_LIMIT = parse_int(_PY['recursionLimit'])
#PY_STACK_SIZE = parse_int(_PY['stackSize'])

## User profile ##

# Paths are in str, but will be converted to unicode in rc.py as DIR_USER.
USER_PROFILES = APP_YAML['user']['profiles']

## Translations ##

QT_TRANSLATIONS_LOCATION = parse_path(SHARE_YAML['qt']['tr'])  # unicode abspath

#TR_LOCALES = APP_YAML['tr']['locales'] # [str locale_name]
TR_LOCATIONS = map(parse_path, APP_YAML['tr']) # [unicode abspath]

## Fonts ##

#IMAGE_FONT_MAC_EN = SHARE_YAML['image_fonts']['mac']['en']    # str relpath
#IMAGE_FONT_MAC_JA = SHARE_YAML['image_fonts']['mac']['ja']    # str relpath
#IMAGE_FONT_WIN_EN = SHARE_YAML['image_fonts']['win']['en']    # str relpath
#IMAGE_FONT_WIN_JA = SHARE_YAML['image_fonts']['win']['ja']    # str relpath

#FONT_DEFAULT = SHARE_YAML['fonts']['default']

TEXT_FONTS = SHARE_YAML['fonts']['text']
def text_font(lang): # str -> str
  return TEXT_FONTS.get(lang) or TEXT_FONTS['*']

UI_FONTS = SHARE_YAML['fonts']['ui']
def ui_font(lang): # str -> str
  return UI_FONTS.get(lang) or ''

## Options ##

JINJA = SHARE_YAML['jinja']
JINJA_HAML = SHARE_YAML['jinja_haml']

## Languages ##

ENCODINGS = SHARE_YAML['encodings']   # [str enc]

ENCODING_SET = frozenset(ENCODINGS)
def is_valid_encoding(enc): return enc in ENCODING_SET

def check_valid_encoding(enc):
  if not is_valid_encoding(enc):
    raise ValueError("invalid encoding %s" % enc)

lANGUAGE_NAMES = SHARE_YAML['languages']['names']  # {str lang:str name}
def language_name(lang): return lANGUAGE_NAMES.get(lang)

LANGUAGES = SHARE_YAML['languages']['all']# [str lang]
LANGUAGE_LOCALES = SHARE_YAML['locales']  # {str lang : str locale}
LANGUAGE_SPELLS = SHARE_YAML['spells']    # {str lang : str locale}

LANGUAGES2 = [it[:2] for it in LANGUAGES if it != 'zhs'] # [str lang]

LATIN_LANGUAGES = SHARE_YAML['languages']['latin']  # [str lang]
LATIN_LANGUAGE_SET = frozenset(LATIN_LANGUAGES)
def is_latin_language(lang): return lang in LATIN_LANGUAGE_SET

CYRILLIC_LANGUAGES = SHARE_YAML['languages']['cyril']  # [str lang]
CYRILLIC_LANGUAGE_SET = frozenset(CYRILLIC_LANGUAGES)
def is_cyrillic_language(lang): return lang in CYRILLIC_LANGUAGE_SET

SPACE_LANGUAGE_SET = frozenset(LATIN_LANGUAGES +
    SHARE_YAML['languages']['space']) # [str lang]
def language_has_space(lang): return lang in SPACE_LANGUAGE_SET

WORD_SPACE_LANGUAGE_SET = frozenset(LATIN_LANGUAGES +
    SHARE_YAML['languages']['wordspace']) # [str lang]
def language_word_has_space(lang): return lang in SPACE_LANGUAGE_SET

# Never used
ASIAN_LANGUAGES = SHARE_YAML['languages']['asian']  # [str lang]
ASIAN_LANGUAGE_SET = frozenset(ASIAN_LANGUAGES)
def is_asian_language(lang): return lang in ASIAN_LANGUAGE_SET

KANJI_LANGUAGES = SHARE_YAML['languages']['kanji']  # [str lang]
KANJI_LANGUAGE_SET = frozenset(KANJI_LANGUAGES)
def is_kanji_language(lang): return lang in KANJI_LANGUAGE_SET

OCR_LANGUAGES = SHARE_YAML['languages']['ocr']  # [str lang]

REVERSED_LANGUAGES = SHARE_YAML['languages']['reversed']  # [str lang]
def is_reversed_language(lang): return lang in REVERSED_LANGUAGES

LANGUAGE_SET = frozenset(LANGUAGES)
def is_valid_language(lang):
  return lang in LANGUAGE_SET

def check_valid_language(lang):
  if not is_valid_language(lang):
    raise ValueError("invalid language %s" % lang)

def language2locale(lang): # str -> str
  return LANGUAGE_LOCALES.get(lang) or "%s_%s" % (lang, lang.upper()) if lang else ''

def language2htmllocale(lang): # str -> str
  if lang == 'zhs':
    return 'zh-CN'
  if lang == 'zht':
    return 'zh-TW'
  return lang or ""

def htmllocale2language(lang): # str -> str
  if lang == 'zh-CN':
    return 'zhs'
  if lang == 'zh-TW':
    return 'zht'
  return lang or ""

def language2lcid(lang): # str -> long
  loc = language2locale(lang)
  from windefs import winlocale
  return winlocale.locale2lcid(loc)

def language2codepage(lang): # str -> long
  loc = language2locale(lang)
  from windefs import winlocale
  return winlocale.locale2codepage(loc)

ALPHABET_LANGUAGES = SHARE_YAML['languages']['alphabet']  # [str lang]
ALPHABET_LANGUAGE_SET = frozenset(ALPHABET_LANGUAGES)

YOMIGANA_LANGUAGES = SHARE_YAML['languages']['yomi']  # [str lang]
YOMIGANA_LANGUAGE_SET = frozenset(YOMIGANA_LANGUAGES)

LINGOES_LANGS = SHARE_YAML['lingoes'] # [str lang]
JMDICT_LANGS = SHARE_YAML['jmdict'] # [str lang]
KANJIDIC_LANGS = SHARE_YAML['kanjidic'] # [str lang]
STARDICT_LANGS = [it.partition('-')[2] for it in SHARE_YAML['stardict'].iterkeys() if '-' in it] # [str lang]

# Forum

GLOBAL_SUBJECT_ID = SHARE_YAML['forum']['subjects']['global']
GLOBAL_TOPIC_ID = SHARE_YAML['forum']['topics']['global']
TERM_TOPIC_ID = SHARE_YAML['forum']['topics']['term']

## Locations ##

AVATARS_LOCATION = os.path.abspath(parse_path(SHARE_YAML['avatars']['location'])) # unicode abspath
AVATARS_COUNT = parse_int(SHARE_YAML['avatars']['count'])
#AVATARS_FORMAT = SHARE_YAML['avatars']['format']

HANJA_DIC_PATH = parse_path(SHARE_YAML['hanja']['path']) # unicode abspath

PINYIN_DIC_PATH = parse_path(SHARE_YAML['pinyin']['path']) # unicode abspath

HANZI_DECOMP_DIC_PATH = os.path.abspath(parse_path(SHARE_YAML['hanzi']['decomp'])) # unicode abspath
HANZI_RADICAL_DIC_PATH = os.path.abspath(parse_path(SHARE_YAML['hanzi']['radical'])) # unicode abspath

#IPADIC_LOCATION = parse_path(SHARE_YAML['dictionaries']['ipadic']) # unicode abspath
#EDICT_LOCATION = parse_path(SHARE_YAML['dictionaries']['edict']) # unicode abspath
#LINGOES_LOCATION = parse_path(SHARE_YAML['dictionaries']['lingoes']) # unicode abspath
#USER_EDICT_LOCATION = parse_path(SHARE_YAML['dictionaries']['user_edict']) # unicode abspath
#ENAMDICT_LOCATION = parse_path(SHARE_YAML['dictionaries']['enamdict']) # unicode abspath

NTLEA_LOCATION = parse_path(SHARE_YAML['ntlea']['location']) # unicode abspath

LSC_LOCATION = parse_path(SHARE_YAML['lsc']['location']) # unicode abspath

VNRAGENT_DLLS = map(parse_path, SHARE_YAML['dlls']['vnragent']) # [unicode abspath]
VNRHOOK_DLLS = map(parse_path, SHARE_YAML['dlls']['vnrhook']) # [unicode abspath]
VNRBOOT_DLLS = map(parse_path, SHARE_YAML['dlls']['vnrboot']) # [unicode abspath]

TEMPLATE_LOCATION = parse_path(SHARE_YAML['templates']['location']) # unicode abspath
TEMPLATE_ENTRIES = SHARE_YAML['templates']['entries'] # {str name:unicode relpath}

JCUSERDIC_LOCATIONS = map(parse_path, SHARE_YAML['jcuserdic']) # [unicode abspath]

FONT_LOCATIONS = {k: parse_path(v) # {str key:unicode relpath}
    for k,v in SHARE_YAML['font-family'].iteritems()}

TAHSCRIPT_LOCATIONS = {k: parse_path(v) # {str key:unicode relpath}
    for k,v in SHARE_YAML['tahscript'].iteritems()}

OPENCC_DICS = {k: parse_path(v) # {str key:unicode relpath}
    for k,v in SHARE_YAML['opencc'].iteritems()}

HANVIET_DICS = {k: parse_path(v) # {str key:unicode relpath}
    for k,v in SHARE_YAML['hanviet'].iteritems()}
HANVIET_DIC_LOCATION = os.path.dirname(HANVIET_DICS.itervalues().next())

STARDICT_LOCATIONS = {k: parse_path(v) # {str lang:unicode relpath}
    for k,v in SHARE_YAML['stardict'].iteritems()}

#MECAB_DIC_LOCATION = SHARE_YAML['mecab']['dicdir']
#MECAB_RCFILE_LOCATION = SHARE_YAML['mecab']['rcfile']

#CABOCHA_DICS = {k: parse_path(v) # {str name:unicode relpath}
#    for k,v in SHARE_YAML['cabocha']['dicdir'].iteritems()}
#
#CABOCHA_RCFILES = {k: parse_path(v) # {str name:unicode abspath}
#    for k,v in SHARE_YAML['cabocha']['rcfile'].iteritems()}

GAIJI_LOCATIONS = {k: parse_path(v) # {str name:unicode abspath}
    for k,v in SHARE_YAML['gaiji'].iteritems()}

APP_LOCATIONS = {k: parse_path(v) # {str name:unicode abspath}
    for k,v in SHARE_YAML['apps'].iteritems()}

QML_LOCATIONS = {k: parse_path(v) # {str name:unicode abspath}
    for k,v in SHARE_YAML['qml'].iteritems()}

QSS_LOCATIONS = {k: parse_path(v) # {str name:unicode abspath}
    for k,v in SHARE_YAML['qss'].iteritems()}

ICON_LOCATIONS = {k: parse_path(v) # {str name:unicode abspath}
    for k,v in SHARE_YAML['icons'].iteritems()}

IMAGE_LOCATIONS = {k: parse_path(v) # {str name:unicode abspath}
    for k,v in SHARE_YAML['images'].iteritems()}

YAML_LOCATIONS = {k: parse_path(v) # {str name:unicode abspath}
    for k,v in SHARE_YAML['yaml'].iteritems()}

CURSOR_LOCATIONS = {k: parse_path(v) # {str name:unicode apspath}
    for k,v in SHARE_YAML['cursors'].iteritems()}

#TRDB_LOCATIONS = {k: parse_path(v) # {str name:unicode abspath}
#    for k,v in SHARE_YAML['trdb'].iteritems()}

# EOF
