# coding: utf8
# tahscript.py
# 8/14/2014 jichi

import re
from sakurakit.skclass import memoized
from sakurakit.skdebug import dprint, dwarn

_repeat_comma = re.compile(ur'。+')
def repair_tah_text(t): # unicode -> unicode
  return _repeat_comma.sub(u'。', t)

@memoized
def manager(): return TahScriptManager()

class _TahScriptManager:

  def __init__(self):
    self.tah = {} # {str key:TahScriptManager}
    self.locks = {} # {str key:bool}

  def getTah(self, key): # str key -> TahScriptManager
    ret = self.tah.get(key)
    if not ret and not self.locks.get(key):
      self.locks[key] = True
      import os
      from pytahscript import TahScriptManager
      import config
      ret = TahScriptManager()
      path = config.TAHSCRIPT_LOCATIONS[key]
      if os.path.exists(path):
        ret.loadFile(path)
        dprint("load %s rules for %s" % (ret.size(), key))
      self.tah[key] = ret
      self.locks[key] = False
    return ret

class TahScriptManager:

  def __init__(self):
    self.__d = _TahScriptManager()

  #def reloadScripts(self): self.__d.reloadScripts() # reload scritps

  def apply(self, text, key):
    """
    @param  text  unicode
    @return  unicode
    """
    if key in ('atlas', 'nifty'):
      key = 'atlas'
    else:
      key = 'lec'
    tah = self.__d.getTah(key)
    if not tah:
      dwarn("tah locked due to thread contention, try next time")
      return text
    return repair_tah_text(tah.translate(text)) or text # totally deleting ret is NOT allowed in case of malicious rule

# EOF
