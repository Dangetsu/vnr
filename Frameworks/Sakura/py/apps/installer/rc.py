# coding: utf8
# rc.py
# 12/13/2012 jichi
# Runtime resource locations

import config

# Image locations

def icon(name):
  """
  @param  name  str  id
  @return  QIcon
  @throw  KeyError  when unknown name
  """
  from PySide.QtGui import QIcon
  return QIcon(config.ICON_LOCATIONS[name])

def image_path(name):
  """
  @param  name  str  id
  @return  unicode
  @throw  KeyError  when unknown name
  """
  return config.IMAGE_LOCATIONS[name]

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
  return skfileio.readfile(qss_path(name))

# EOF
