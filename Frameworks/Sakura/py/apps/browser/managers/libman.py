# coding: utf8
# libman.py
# 12/8/2012 jichi

import os
from sakurakit import skos
from sakurakit.skclass import memoized
from sakurakit.skdebug import dprint

# Cached abstract class
class Library(object):

  def __init__(self):
    self.__exists = None

  def location(self):
    """
    @return  str not None
    """
    return ""

  def refresh(self):
    self.__exists = None

  def exists(self):
    """Cached"""
    if self.__exists is None:
      self.__exists = self.verifyLocation(self.location())
    return self.__exists

  def verifyLocation(self, path):
    return bool(path) and os.path.exists(path)

class QuickTime(Library):
  URL = "http://www.apple.com/quicktime/download/"

  def location(self):
    """@reimp"""
    if not skos.WIN:
      return ""

    QT_REG_PATH   = r"SOFTWARE\Apple Computer, Inc.\QuickTime"
    QT_REG_KEY    = r"InstallDir"
    try:
      import _winreg
      with _winreg.ConnectRegistry(None, _winreg.HKEY_LOCAL_MACHINE) as reg:
        with _winreg.OpenKey(reg, QT_REG_PATH) as key:
          return _winreg.QueryValueEx(key, QT_REG_KEY)[0]
    except WindowsError, e:
      dprint(e)
      #dwarn(e) # this is always error if QuickTime is not installed, no need to warn
    return ""

@memoized
def quicktime(): return QuickTime()

# EOF
