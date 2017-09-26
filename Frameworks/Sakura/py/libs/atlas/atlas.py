# coding: utf8
# atlas.py
# 11/19/2012 jichi

import os
from sakurakit import skpaths, skos
from sakurakit.skclass import memoizedproperty
from sakurakit.skdebug import dprint, dwarn

class _Engine(object):
  def __init__(self):
    self.dllLoaded = False
    self.pathLoaded = False

  @memoizedproperty
  def atle(self):
    import atle
    return atle.Loader()

  def loadDll(self):
    self.atle.init()
    self.dllLoaded = self.atle.isInitialized()
    dprint("ok = %s" % self.dllLoaded)

  def loadPath(self):
    rpath = self.registryLocation()
    epath = self.environLocation()
    if rpath and os.path.exists(rpath):
      skpaths.append_path(rpath)
    if epath and epath != rpath and os.path.exists(epath):
      skpaths.append_path(epath)
    self.pathLoaded = True

  def destroy(self):
    if self.dllLoaded:
      self.atle.destroy()
      dprint("pass")

  @staticmethod
  def registryLocation():
    """
    @return  unicode or None
    """
    if not skos.WIN:
      return

    ATLE_REG_PATH   = r"SOFTWARE\Fujitsu\AtlEDict\V14.0\Env"
    ATLE_REG_KEY    = r"DENJI"
    import _winreg
    try:
      with _winreg.ConnectRegistry(None, _winreg.HKEY_LOCAL_MACHINE) as reg: # None = computer_name
        with _winreg.OpenKey(reg, ATLE_REG_PATH) as key:
          return _winreg.QueryValueEx(key, ATLE_REG_KEY)[0]
    except WindowsError: pass

  @staticmethod
  def environLocation():
    return os.path.join(skpaths.PROGRAMFILES, "ATLAS V14")

class Engine(object):

  def __init__(self):
    self.__d = _Engine()

  def __del__(self):
    self.destroy()

  def destroy(self): self.__d.destroy()
  def isLoaded(self): return self.__d.dllLoaded

  def load(self):
    """
    @return  bool
    """
    d = self.__d
    if not d.pathLoaded:
      d.loadPath()
    if not d.dllLoaded:
      d.loadDll()
    return self.isLoaded()

  def translate(self, text):
    """
    @param  text  unicode or str
    @return   unicode not None
    @throw  RuntimeError
    """
    if not self.isLoaded():
      self.load()
      if not self.isLoaded():
        raise RuntimeError("Failed to load ATLAS dll")
    return self.__d.atle.translate(text) #if text else ""

  def warmup(self):
    #try: self.translate(u" ") # WARNING: a pure space would crash ATLAS
    try: self.translate(u"あ")
    except Exception, e: dwarn(e)

  @staticmethod
  def location():
    """
    @return  str or None
    """
    ret = _Engine.registryLocation()
    if ret and os.path.exists(ret):
      return ret
    ret = _Engine.environLocation()
    if ret and os.path.exists(ret):
      return ret

def create_engine():
  return Engine()

location = Engine.location

# EOF
