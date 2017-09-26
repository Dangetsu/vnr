# coding: utf8
# powertrans.py
# 1/19/2013 jichi

import os
from sakurakit import skpaths, skos
from sakurakit.skclass import memoizedproperty
from sakurakit.skdebug import dprint, dwarn

class _Engine(object):
  def __init__(self):
    self.pathLoaded = False

    self.engines = {} # {key, Loader}

  def getEngine(self, key):
    """
    @param  key  str
    @return  Loader
    """
    ret = self.engines.get(key)
    if not ret:
      if key == 'nova':
        import nova
        ret = nova.Loader()
      elif key == 'pars':
        import pars
        ret = pars.Loader()
      dprint("key = %s" % key)
      if ret and ret.init():
        self.engines[key] = ret
      else:
        dwarn("failed to load key = %s" % key)
        ret = None
    return ret

  def getEngines(self, to, fr):
    """
    @param  to  str
    @param  fr  str
    @return  [Loader]
    """
    if fr == 'en' and to == 'ru':
      pars = self.getEngine('pars')
      if pars:
        return pars,
    elif fr == 'ja' and to == 'en':
      nova = self.getEngine('nova')
      if nova:
        return nova,
    elif fr == 'ja' and to == 'ru':
      nova = self.getEngine('nova')
      if nova:
        pars = self.getEngine('pars')
        if pars:
          return nova, pars
        else:
          return nova,

  def loadPath(self):
    paths = { # use set for uniqueness
      self.registryLocation(),
      self.environLocation(),
    }
    l = []
    for path in paths:
      if path:
        for k in (r"Nova\JaEn", r"PARS\EnRu"):
          v = os.path.join(path, k)
          if os.path.exists(v):
            l.append(v)
    if l:
      skpaths.append_paths(l)
    self.pathLoaded = True

  def destroy(self):
    if self.engines:
      for eng in self.engines.itervalues():
        ret.destroy()
      self.engines.clear()
    dprint("pass")

  @staticmethod
  def registryLocation():
    """
    @return  unicode or None
    """
    if not skos.WIN:
      return

    REG_PATH   = r"SOFTWARE\LogoMedia\LEC Power Translator 15\Configuration"
    REG_KEY    = r"ApplicationPath"
    import _winreg
    try:
      with _winreg.ConnectRegistry(None, _winreg.HKEY_LOCAL_MACHINE) as reg: # computer_name = None
        with _winreg.OpenKey(reg, REG_PATH) as key:
          path = _winreg.QueryValueEx(key, REG_KEY)[0]
          path = path.rstrip(os.path.sep)
          return os.path.dirname(path)
    except (WindowsError, TypeError, AttributeError): pass

  @staticmethod
  def environLocation():
    return os.path.join(skpaths.PROGRAMFILES, "Power Translator 15")

class Engine(object):

  def __init__(self):
    self.__d = _Engine()

  def __del__(self):
    self.destroy()

  def destroy(self): self.__d.destroy()
  def isLoaded(self): return bool(self.__d.engines)

  def load(self, to='en', fr='ja'):
    """
    @param* to  str
    @param* fr  str
    @return  bool
    """
    d = self.__d
    if not d.pathLoaded:
      d.loadPath()
    if not d.engines:
      d.getEngine('nova')
      if to == 'ru':
        d.getEngine('pars')
    return bool(d.engines)

  def translate(self, text, to='en', fr='ja'):
    """
    @param  text  unicode or str
    @param* to  str
    @param* fr  str
    @return   unicode not None
    @throw  RuntimeError
    """
    l = self.__d.getEngines(to, fr)
    if not l:
      raise RuntimeError("Failed to load Power Translator dll")
    for eng in l:
      text = eng.translate(text)
      if not text:
        break
    return text

  def retranslate(self, text, to='en', fr='ja'):
    """
    @param  text  unicode or str
    @param* to  str
    @param* fr  str
    @yield  unicode
    @throw  RuntimeError
    """
    l = self.__d.getEngines(to, fr)
    if not l:
      raise RuntimeError("Failed to load Power Translator dll")
    for eng in l:
      text = eng.translate(text)
      if not text:
        break
      yield text

  def warmup(self, to='en', fr='ja'):
    #try: self.translate(u" ")
    try: self.translate(u"あ", to=to, fr=fr)
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
