# coding: utf8
# transcat.py
# 3/1/2015 jichi
# Warning: TransCAT conflicts with JBeijing. Its dll must be loaded before JBeijing!

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import os
from sakurakit import skpaths, skos
from sakurakit.skclass import memoizedproperty
from sakurakit.skdebug import dprint, dwarn

class _Engine(object):
  def __init__(self, tmpdir):
    self.tmpdir = tmpdir # unicode
    self.dllLoaded = False
    self.pathLoaded = False

  @memoizedproperty
  def loader(self):
    import djk
    return djk.Loader(tmpdir=self.tmpdir)

  def loadDll(self):
    self.loader.init()
    self.dllLoaded = self.loader.isInitialized()
    dprint("ok = %s" % self.dllLoaded)

  def loadPath(self):
    path = self.registryLocation()
    if path and os.path.exists(path):
      skpaths.append_path(path)
    self.pathLoaded = True

  def destroy(self):
    if self.dllLoaded:
      self.loader.destroy()
      dprint("pass")

  @staticmethod
  def registryLocation():
    """Default is: $PROGRAMFILES/DICO SYSTEM/TransCAT KJJK
    @return  unicode or None
    """
    if not skos.WIN:
      return
    REG_PATH   = r"Software\DICO\TransCAT KJJK\Install Directory" # There is also a TRANSCAT/kj key
    REG_KEY    = r"Install Directory"
    import _winreg
    try:
      with _winreg.ConnectRegistry(None, _winreg.HKEY_CURRENT_USER) as reg: # computer_name = None
        with _winreg.OpenKey(reg, REG_PATH) as key:
          return _winreg.QueryValueEx(key, REG_KEY)[0]
    except WindowsError: pass

class Engine(object):

  def __init__(self, tmpdir=''):
    """
    @param* tmpdir  unicode
    """
    self.__d = _Engine(tmpdir=tmpdir)

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
    @param  text  unicode
    @return   unicode
    @throw  RuntimeError
    """
    if not self.isLoaded():
      self.load()
      if not self.isLoaded():
        raise RuntimeError("Failed to load TransCAT dll")
    return self.__d.loader.translate(text)

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
    if ret and os.path.exists(ret):
      return ret

def create_engine(*args, **kwargs): return Engine(*args, **kwargs)

location = Engine.location # return unicode

if __name__ == '__main__': # DEBUG
  print location()
  print len(create_engine().translate(u"こんにちは"))

# EOF
