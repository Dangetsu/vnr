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

#def u8(s): return s.decode('utf8', errors='ignore')
u = u_from_native

# Python os.path.abspath has unicode issue
#ROOT_LOCATION = os.path.abspath(os.path.dirname(__file__) + "/../../..")
ROOT_LOCATION = os.path.dirname(__file__) + "/../../.."

# Delay loading Qt
ROOT_ABSPATH = None
def root_abspath():
  global ROOT_ABSPATH
  if not ROOT_ABSPATH:
    from PySide.QtCore import QDir
    ROOT_ABSPATH = QDir.fromNativeSeparators(os.path.abspath(ROOT_LOCATION))
  return ROOT_ABSPATH

SHARE_YAML_LOCATION = os.path.join(ROOT_LOCATION, "share.yaml")
APP_YAML_LOCATION = os.path.join(ROOT_LOCATION, "reader.yaml")

ROOT_LOCATION_U = u(ROOT_LOCATION)

def load_yaml_file(path):
  import yaml
  return yaml.load(file(path, 'r'))

SHARE_YAML = load_yaml_file(SHARE_YAML_LOCATION)
APP_YAML = load_yaml_file(APP_YAML_LOCATION)

## Property parsers ##

def parse_path(path):
  """
  @param  path  unicode
  @return  unicode  absolute path
  """
  return path.replace('$PWD', ROOT_LOCATION_U)

## Environment variables ##

ENV_PATH = map(parse_path, SHARE_YAML['env']['path']) # [unicode abspath]
ENV_PYTHONPATH = map(parse_path, SHARE_YAML['env']['pythonpath']) # [unicode abspath]

ENV_INTEGRITYPATH = map(parse_path, SHARE_YAML['env']['integritypath']) # [unicode abspath]

#ENV_MECABRC = parse_path(SHARE_YAML['env']['mecabrc'])   # unicode abspath

## Locations ##

QSS_LOCATIONS = {k: parse_path(v) # {str name:unicode abspath}
    for k,v in SHARE_YAML['qss'].iteritems()}

ICON_LOCATIONS = {k: parse_path(v) # {str name:unicode abspath}
    for k,v in SHARE_YAML['icons'].iteritems()}

IMAGE_LOCATIONS = {k: parse_path(v) # {str name:unicode abspath}
    for k,v in SHARE_YAML['images'].iteritems()}

# EOF
