# coding: utf8
# rc.py
# 10/8/2012 jichi
# Runtime resource locations

from PySide.QtCore import QUrl
from PySide.QtGui import QIcon
from sakurakit import skfileio
import config

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
  return skfileio.readfile(qss_path(name))

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

# EOF
