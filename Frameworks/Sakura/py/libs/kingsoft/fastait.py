# coding: utf8
# fastait.py
# 9/17/2014 jichi

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import os
from sakurakit.skdebug import dprint, dwarn

DLLS = {
  "enzhs": "GTS/EnglishSChinese/EngSChSDK.dll",
  "enzht": "GTS/EnglishTChinese/EngTChSDK.dll",
  "jazhs": "GTS/JapaneseSChinese/JPNSCHSDK.dll",
  "jazht": "GTS/JapaneseTChinese/JPNTCHSDK.dll",
  "zhsen": "GTS/SChineseEnglish/SchEngSDK.dll",
  "zhten": "GTS/TChineseEnglish/TchEngSDK.dll",
}

class _Engine(object):
  def __init__(self, dllLoader):
    self.loader = dllLoader # gts.Loader
    self.dllLoaded = False

  def loadDll(self):
    self.loader.init()
    self.dllLoaded = self.loader.isInitialized()
    dprint("ok = %s" % self.dllLoaded)

  def destroy(self):
    if self.dllLoaded:
      self.loader.destroy()
      dprint("pass")

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
    if not d.dllLoaded:
      d.loadDll()
      #if not d.userDicLoaded:
      #  self.loadDefaultUserDic()
    return self.isLoaded()

  def translate(self, text, fr=None, to=None):
    """
    @param  text  unicode
    @param* fr  unicode  ignored
    @param* to  unicode  ignored
    @return   unicode or None
    @throw  RuntimeError
    """
    if not self.isLoaded():
      self.load()
      if not self.isLoaded():
        raise RuntimeError("Failed to load FastAIT dll")
    return self.__d.loader.translate(text)

  def warmup(self):
    #try: self.translate(u" ")
    try: self.translate(u"a")
    except Exception, e: dwarn(e)

def create_engine(fr='ja', to='zhs'):
  dllpath = DLLS.get(fr + to)
  if dllpath:
    import gts
    dllname = os.path.basename(dllpath)
    bufsize = gts.EN_BUFFER_SIZE if fr == 'en' or to == 'en' else gts.ZH_BUFFER_SIZE
    return Engine(gts.Loader(dllname, bufsize))

if __name__ == '__main__': # DEBUG
  fr = 'ja'
  to = 'zhs'
  langs = fr + to
  path = r"Z:\Local\Windows\Applications\FASTAIT_PERSONAL"
  #path = r"C:\tmp\FASTAIT_PERSONAL"
  dllpath = DLLS[langs]
  dllpath = os.path.join(path, dllpath)
  os.environ['PATH'] += os.pathsep + os.path.dirname(dllpath)

  e = create_engine(fr=fr, to=to)
  t = e.translate(u"こんにちは")
  print len(t)

  path = r"Z:\Local\Windows\Applications\FASTAIT_PERSONAL"
  #path = r"C:\tmp\FASTAIT_PERSONAL"
  dllpath = DLLS[langs]
  dllpath = os.path.join(path, dllpath)

# EOF
