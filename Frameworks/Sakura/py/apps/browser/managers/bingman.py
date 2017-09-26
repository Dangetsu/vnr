# coding: utf8
# bingman.py
# 10/7/2014 jichi

from sakurakit.skclass import memoized
from sakurakit import skthreads
from microsoft import bingauth, bingtrans, bingtts

@memoized
def manager(): return BingManager()

class BingManager:

  def __init__(self):
    self.__d = _BingManager()

  def translate(self, *args, **kwargs): # -> unicode  text
    appId = self.__d.appId()
    return bingtrans.translate(appId, *args, **kwargs) if appId else ''

  def tts(self, *args, **kwargs): # -> unicode  url
    appId = self.__d.appId()
    return bingtts.url(appId, *args, **kwargs) if appId else ''

class _BingManager:
  def __init__(self):
    self._appId = None

  def appId(self):
    """
    @return  str or None
    """
    if not self._appId:
      self._appId = skthreads.runsync(bingauth.getappid)
    return self._appId

# EOF
