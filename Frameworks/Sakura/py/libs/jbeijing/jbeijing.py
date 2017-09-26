# coding: utf8
# jbeijing.py
# 1/3/2013 jichi

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import os
from sakurakit import skpaths, skos
from sakurakit.skclass import memoizedproperty
from sakurakit.skdebug import dprint, dwarn

MAX_USERDIC_COUNT = 3 # max number of user-defined dic

class _Engine(object):
  def __init__(self):
    self.dllLoaded = False
    self.pathLoaded = False
    #self.userDicLoaded = False
    #self.userDicPaths = set() # [unicode path]

  @memoizedproperty
  def jbjct(self):
    import jbjct
    return jbjct.Loader()

  def loadDll(self):
    self.jbjct.init()
    self.dllLoaded = self.jbjct.isInitialized()
    dprint("ok = %s" % self.dllLoaded)

  def loadPath(self):
    path = self.registryLocation()
    if path and os.path.exists(path):
      skpaths.append_path(path)
    self.pathLoaded = True

  def destroy(self):
    if self.dllLoaded:
      self.jbjct.destroy()
      dprint("pass")

  @classmethod
  def registryLocation(cls):
    """
    @return  unicode or None
    """
    for path in cls.iterRegistryUserDic():
      try:
        path = os.path.dirname(path)
        path = path.rstrip(os.path.sep)
        base = os.path.basename(path)
        path = os.path.dirname(path)
        if path and os.path.exists(os.path.join(path, 'JBJCT.dll')):
          return path
      except (TypeError, AttributeError): pass

  @staticmethod
  def iterRegistryUserDic():
    """
    @yield  unicode  the userdic prefix without ".dic"
    """
    if not skos.WIN:
      return

    USERDIC_REG_PATH   = r"SOFTWARE\Kodensha\jBeijing7\TransPad\JcUserDic"
    USERDIC_REG_KEY_I  = r"User Dic%i"
    import _winreg
    for hk in _winreg.HKEY_CURRENT_USER, _winreg.HKEY_LOCAL_MACHINE:
      try:
        with _winreg.ConnectRegistry(None, hk) as reg: # computer_name = None
          with _winreg.OpenKey(reg, USERDIC_REG_PATH) as key:
            for i in 1,2,3:
              path = _winreg.QueryValueEx(key, USERDIC_REG_KEY_I % i)[0]
              if path:
                yield path
      except (WindowsError, TypeError, AttributeError): pass

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
      #if not d.userDicLoaded:
      #  self.loadDefaultUserDic()
    return self.isLoaded()

  def translate(self, text, simplified=False):
    """
    @param  text  unicode
    @param  simplified  bool
    @return   unicode or None
    @throw  RuntimeError
    """
    if not self.isLoaded():
      self.load()
      if not self.isLoaded():
        raise RuntimeError("Failed to load JBeijng dll")
    return self.__d.jbjct.translate(text, simplified)

  def warmup(self):
    #try: self.translate(u" ", simplified=True)
    try: self.translate(u"あ", simplified=True)
    except Exception, e: dwarn(e)

  @staticmethod
  def location():
    """
    @return  str or None
    """
    ret = _Engine.registryLocation()
    if ret and os.path.exists(ret):
      return ret

  def setUserDic(self, paths):
    """
    @param  paths  [unicode path]  at most 3 elements
    @return   bool
    """
    if not self.isLoaded():
      self.load()
    dprint("loaded = %s" % self.isLoaded())
    dprint(paths)
    ret = self.isLoaded() and self.__d.jbjct.setUserDic(paths)
    dprint("ret = %s" % ret)
    return ret

  def clearUserDic(self):
    #self.__d.userDicPaths.clear()
    if self.isLoaded():
      self.__d.jbjct.clearUserDic()

  #def userDicLocations(self):
  #  """
  #  @return  [unicode path]
  #  """
  #  return self.__d.userDicPaths

def create_engine(): return Engine()

location = Engine.location # return unicode

def userdic():
  """
  @return  [unicode path]  The path does not contain .dic
  """
  return list(_Engine.iterRegistryUserDic())

if __name__ == '__main__': # DEBUG
  print location()
  print userdic()

# EOF
