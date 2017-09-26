# coding: utf8
# dreyemt.py
# 5/20/2013 jichi

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import os
from sakurakit import skpaths, skos
from sakurakit.skclass import memoizedproperty
from sakurakit.skdebug import dprint, dwarn

class _Engine(object):
  def __init__(self, dllLoader):
    self._dllLoader = dllLoader # transcom.JCLoader or ECLoader
    self.dllLoaded = False
    self.pathLoaded = False
    #self.userDicLoaded = False
    #self.userDicPaths = set() # [unicode path]

  @memoizedproperty
  def loader(self): return self._dllLoader()

  def loadDll(self):
    self.loader.init()
    self.dllLoaded = self.loader.isInitialized()
    dprint("ok = %s" % self.dllLoaded)

  def loadPath(self):
    path = self.registryLocation()
    if path and os.path.exists(path):
      path = os.path.join(path, r"DreyeMT\SDK\bin")
      skpaths.append_path(path)
    self.pathLoaded = True

  def destroy(self):
    if self.dllLoaded:
      self.loader.destroy()
      dprint("pass")

  @staticmethod
  def registryLocation():
    """
    @yield  unicode  the userdic prefix without ".dic"
    """
    if not skos.WIN:
      return

    REG_PATH   = r"SOFTWARE\Inventec\Dreye\9.0\System\InstallInfo"
    REG_KEY    = r"BasePath"
    import _winreg
    hk = _winreg.HKEY_LOCAL_MACHINE
    try:
      with _winreg.ConnectRegistry(None, hk) as reg: # computer_name = None
        with _winreg.OpenKey(reg, REG_PATH) as key:
          path = _winreg.QueryValueEx(key, REG_KEY)[0]
          return path
    except (WindowsError, TypeError, AttributeError): pass

class Engine(object):

  def __init__(self, loader):
    """
    @param  loader  transcom.JCLoader or transcom.ECLoader
    """
    self.__d = _Engine(loader)

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

  def translate(self, text, to, fr):
    """
    @param  text  unicode
    @param  fr  unicode
    @param  to  unicode
    @return   unicode or None
    @throw  RuntimeError
    """
    if not self.isLoaded():
      self.load()
      if not self.isLoaded():
        raise RuntimeError("Failed to load Dr.eye dll")
    return self.__d.loader.translate(text, to, fr)

  def warmup(self):
    #try: self.translate(u" ")
    try: self.translate(u"あ")
    except Exception, e: dwarn(e)

  @staticmethod
  def location():
    """
    @return  str or None
    """
    ret = _Engine.registryLocation()
    if ret and os.path.exists(os.path.join(ret, r"DreyeMT\SDK\bin")):
      return ret

def create_engine(lang='ja'):
  import transcom
  if lang == 'ja':
    return Engine(transcom.JCLoader)
  elif lang == 'en':
    return Engine(transcom.ECLoader)

location = Engine.location # return unicode

if __name__ == '__main__': # DEBUG
  print location()
  e = create_engine('ja')
  t = e.translate(u"こんにちは")
  print len(t)

# EOF
