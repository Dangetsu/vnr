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

SHARE_YAML_LOCATION = os.path.join(ROOT_LOCATION, "share.yaml")
APP_YAML_LOCATION = os.path.join(ROOT_LOCATION, "installer.yaml")

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

## Settings ##

QT_THREAD_COUNT = parse_int(APP_YAML['qt']['threadCount'])
QT_THREAD_TIMEOUT = parse_int(APP_YAML['qt']['threadTimeout'])

QT_QUIT_TIMEOUT = parse_int(APP_YAML['qt']['quitTimeout'])

## Translations ##

TR_LOCALES = APP_YAML['tr']['locales'] # [str locale_name]
TR_LOCATIONS = map(parse_path, APP_YAML['tr']['locations']) # [unicode path]

QT_TRANSLATIONS_LOCATION = parse_path(SHARE_YAML['qt']['tr'])  # unicode path

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
LANGUAGE_SPELLS = SHARE_YAML['spells']    # {str lang : str locale}

LANGUAGE_SET = frozenset(LANGUAGES)
def is_valid_language(lang): return lang in LANGUAGE_SET

def check_valid_language(lang):
  if not is_valid_language(lang):
    raise ValueError("invalid language %s" % lang)

def language2locale(lang):
  return LANGUAGE_LOCALES.get(lang) or ""

## Locations ##

APP_LOCATIONS = {k: parse_path(v)   # {str name:unicode path}
    for k,v in SHARE_YAML['apps'].iteritems()}

QSS_LOCATIONS = {k: parse_path(v) # {str name:unicode path}
    for k,v in SHARE_YAML['qss'].iteritems()}

ICON_LOCATIONS = {k: parse_path(v)  # {str name:unicode path}
    for k,v in SHARE_YAML['icons'].iteritems()}

IMAGE_LOCATIONS = {k: parse_path(v) # {str name:unicode path}
    for k,v in SHARE_YAML['images'].iteritems()}

SCRIPT_READER_UPDATE = parse_path(APP_YAML['scripts']['reader']['update']) # unicode path
SCRIPT_READER_REMOVE = parse_path(APP_YAML['scripts']['reader']['remove']) # unicode path
SCRIPT_PLAYER_UPDATE = parse_path(APP_YAML['scripts']['player']['update']) # unicode path
SCRIPT_PLAYER_REMOVE = parse_path(APP_YAML['scripts']['player']['remove']) # unicode path
TRACE_READER = parse_path(APP_YAML['traces']['reader']) # unicode path
TRACE_PLAYER = parse_path(APP_YAML['traces']['player']) # unicode path

# EOF
