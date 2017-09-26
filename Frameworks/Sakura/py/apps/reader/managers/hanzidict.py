# coding: utf8
# hanzidict.py
# 5/7/2015 jichi

import os
from sakurakit.skdebug import dprint, dwarn
from sakurakit.skclass import memoized, memoizedproperty
from hanjaconv import hanjaconv
import config, dicts

@memoized
def manager(): return HanziDictionary()

class HanziDictionary:
  def __init__(self):
    self.__d = _HanziDictionary()

  # Properties

  def kanjiDicLanguages(self, v): return self.__d.kanjidicLangs
  def setKanjiDicLanguages(self, v):
    dprint(v)
    self.__d.kanjidicLangs = v

  def isHanjaEnabled(self): return self.__d.hanjaEnabled
  def setHanjaEnabled(self, t): self.__d.hanjaEnabled = t

  # Queries

  def translateKanji(self, ch):
    """
    @param  ch  unicode
    @return  unicode or None
    """
    langs = self.__d.kanjidicLangs
    if langs:
      for lang in reversed(config.KANJIDIC_LANGS):
        if lang in langs:
          ret = dicts.kanjidic(lang).lookup(ch)
          if ret:
            return ret

  def translateRadical(self, ch):
    """
    @param  ch  unicode
    @return  unicode or None
    """
    return self.__d.radicals.get(ch)

  def lookupRadicals(self, ch):
    """
    @param  ch  unicode
    @return  list or None
    """
    return self.__d.decomp.lookup(ch)

  def renderRadicals(self, l):
    """
    @param  ch  unicode
    @return  list
    """
    ret = ''
    d = self.__d
    if l:
      for it in l:
        if isinstance(it, basestring):
          t = self.translateRadical(it) or self.translateKanji(it)
          hanja = hanjaconv.lookup_hanja_char(it) if d.hanjaEnabled else None
          info = filter(bool, (hanja, t))
          if info:
            it += '{%s}' % ','.join(info)
        if ret:
          ret += ', '
        if isinstance(it, basestring):
          ret += it
        else:
          ret += self.renderRadicals(it)
      ret = '(%s)' % ret
    return ret

  def lookupRadicalString(self, ch):
    """
    @param  ch  unicode
    @return  unicode
    """
    rads = self.lookupRadicals(ch)
    return self.renderRadicals(rads) if rads else ''

class _HanziDictionary:
  def __init__(self):
    self.kanjidicLangs = ''
    self.hanjaEnabled = False

  @memoizedproperty
  def decomp(self):
    from hanzicomp.hanzidecomp import HanziDecomposer
    import config
    ret = HanziDecomposer()
    ret.loadFile(config.HANZI_DECOMP_DIC_PATH)
    dprint("size = %s" % ret.size())
    return ret

  @memoizedproperty
  def radicals(self):
    from hanzicomp import hanziradic
    import config
    return hanziradic.parse(config.HANZI_RADICAL_DIC_PATH) or {}

# EOF
