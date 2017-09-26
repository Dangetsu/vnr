# coding: utf8
# trscriptman.py
# 8/14/2014 jichi

from sakurakit.skclass import memoized
from sakurakit.skdebug import dprint
import config

@memoized
def manager(): return TranslationScriptManager()

class _TranslationScriptManager:

  def __init__(self):
    self.enabled = { # disabled by default as tah is empty
      'ja': False ,
      'en': False ,
    }
    from pytahscript import TahScriptManager
    self.tah = {
      'ja': TahScriptManager(),
      'en': TahScriptManager(),
    }

  def reloadScripts(self, lang=None):
    """
    @param* lang  str
    """
    import os
    paths = config.TAHSCRIPT_LOCATIONS
    if not lang:
      for lang,path in paths.iteritems():
        if os.path.exists(path):
          self.tah[lang].loadFile(path)
          dprint("load (%s) %s rules from %s" % (lang, self.tah[lang].size(), path))
    else:
      path = paths.get(lang)
      if path and os.path.exists(path):
        self.tah[lang].loadFile(path)
        dprint("load (%s) %s rules from %s" % (lang, self.tah[lang].size(), path))

class TranslationScriptManager:

  def __init__(self):
    self.__d = _TranslationScriptManager()

  def isLanguageEnabled(self, lang):
    """
    @param  lang  str
    @return  bool
    """
    return self.__d.enabled.get(lang) or False

  def setLanguageEnabled(self, lang, t):
    """
    @param  lang  str
    @param  t  bool
    @return  bool
    """
    d = self.__d
    if d.enabled[lang] != t:
      if d.tah[lang].isEmpty():
        d.reloadScripts(lang)
      d.enabled[lang] = t

  def isEmpty(self):
    return all(it.isEmpty() for it in self.__d.tah.itervalues())
  def scriptCount(self):
    return sum(it.size() for it in self.__d.tah.itervalues())

  def reloadScripts(self): self.__d.reloadScripts() # reload scritps

  def normalizeText(self, text, fr='ja', to='ja'):
    """
    @param  text  unicode
    @param*  fr  str  language
    @param*  to  str  language
    @return  unicode
    """
    if fr != 'ja':
      return text
    ret = text
    d = self.__d
    if d.enabled['ja']:
      ret = d.tah['ja'].translate(ret) or ret # totally deleting ret is NOT allowed in case of malicious rule
    if config.is_latin_language(to) and d.enabled['en']:
      ret = d.tah['en'].translate(ret) or ret # totally deleting ret is NOT allowed in case of malicious rule
    return ret

# EOF
