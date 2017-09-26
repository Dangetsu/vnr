# coding: utf8
# mecabparser.py
# 10/12/2012 jichi
#
# doc: http://mecab.googlecode.com/svn/trunk/mecab/doc/index.html
# doxygen: http://mecab.googlecode.com/svn/trunk/mecab/doc/doxygen/annotated.html

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

from itertools import imap
from jaconv import jaconv
from unitraits import uniconv, jpchars
import mecabdef, mecabformat, mecablex

# Helper functions

lambda_eigen = lambda x:x

_capitalizeromaji_fix = (
  #(' Da ', ' da ',
  (' De ', ' de '),
  (' Ha ', ' ha '),
  (' Na ', ' na '),
  (' No ', ' no '),
  (' Ni ', ' ni '),
  (' To ', ' to '),
  #(' O ', ' o '),
  (' Wo ', ' wo '),
  #(' Yo ', ' yo '),
)
def capitalizeromaji(text):
  """
  @param  text  unicode
  @return  unicode
  """
  text = text.title()
  for k,v in _capitalizeromaji_fix:
    text = text.replace(k, v)
  return text

def getkataconv(ruby):
  """
  @param  ruby  str
  @return  unicode -> unicode
  """
  return (
      uniconv.kata2hira if ruby == mecabdef.RB_HIRA else
      jaconv.kata2romaji if ruby == mecabdef.RB_ROMAJI else
      jaconv.kata2ru if ruby == mecabdef.RB_RU else
      jaconv.kata2uk if ruby == mecabdef.RB_UK else
      jaconv.kata2el if ruby == mecabdef.RB_EL else
      jaconv.kata2ko if ruby == mecabdef.RB_KO else
      jaconv.kata2th if ruby == mecabdef.RB_TH else
      jaconv.kata2ar if ruby == mecabdef.RB_AR else
      #jaconv.kata2romaji if ruby == mecabdef.RB_VI else
      #lambda_eigen if ruby == mecabdef.RB_KATA else
      lambda_eigen)

def _ja2vi(text):
  """
  @param  text  unicode
  @return  unicode or None
  """
  from opencc import opencc
  from hanviet import hanviet
  #from unidecode import unidecode
  text = opencc.ja2zhs(text)
  ret = hanviet.toreading(text)
  if ret != text and not jpchars.anykanji(ret):
    ret = jaconv.kana2romaji(ret)
    #ret = unidecode(ret) # in case there are untranslated words
    return ret

def _capitalize(t):
  """Only capitalize the first letter
  @param  t  unicode
  @return  unicode
  """
  return t[0].upper() + t[1:] if t else ''

# Classes

class _MeCabParser:
  formatter = mecabformat.UNIDIC_FORMATTER

  def __init__(self, tagger):
    self._tagger = tagger

  @property
  def tagger(self):
    if not self._tagger:
      import mecabtagger
      self._tagger = mecabtagger.MeCabTagger()
    return self._tagger

  def featureTrans(self, feature):
    """
    @param  feature  unicode
    @return  unicode
    """
    return self.formatter.getdictrans(feature) if self.formatter.isdic(feature) else ''

  def iterparseToKata(self, text):
    """
    @param  text  unicode
    @yield  unicode  ruby
    """
    for surface,feature in self.tagger.iterparse(text):
      yield self.formatter.getlatin(feature) or self.formatter.getkata(feature) or surface

  def iterparseToVi(self, text):
    """
    @param  text  unicode
    @yield  unicode  vi or ruby
    """
    fmt = self.formatter
    for surface,feature in self.tagger.iterparse(text):
      ruby = fmt.getlatin(feature) # always show latin translation
      if not ruby:
        type = mecablex.getsurfacetype(surface)
        if type == mecabdef.SURFACE_KANJI:
          ruby = _ja2vi(surface)
      if not ruby:
        ruby = fmt.getkata(feature)
        if ruby:
          ruby = jaconv.kata2romaji(ruby)
      yield ruby or surface

  def iterparseToTrans(self, text):
    """
    @param  text  unicode
    @yield  unicode  trans or ruby
    """
    fmt = self.formatter
    for surface,feature in self.tagger.iterparse(text):
      if fmt.isdic(feature):
        ruby = fmt.getdictrans(feature) # always show latin translation
      else:
        ruby = fmt.getlatin(feature)
      if not ruby:
        ruby = fmt.getkata(feature)
        if ruby:
          ruby = jaconv.kata2romaji(ruby)
      yield ruby or surface

  def translate(self, tr, surface, feature):
    """
    @param  tr  unicode -> unicode
    @param  surface  unicode
    @param  feature  unicode
    @return  unicode or None
    """
    ret = tr(surface)
    if ret:
      #if ret == surface:
      #  return
      return ret
    s = self.formatter.getsource(feature)
    if s and s != surface:
      ret = tr(s)
      if ret:
        return ret

  UNKNOWN_RUBY = '?'
  def iterparseToRuby(self, text, kataconv=None, surfconv=None, featureconv=None, tr=None, show_ruby_kana=False):
    """
    @param  text  unicode
    @param* kataconv  unicode -> unicode or None
    @param* surfconv  unicode -> unicode or None
    @param* featureconv  unicode -> unicode or None
    @param* tr  unicode -> unicode or None
    @param* show_ruby_kana  bool
    @yield  (unicode surface, unicode ruby or None, unicode feature, unicode surface_type)
    """
    fmt = self.formatter
    for surface, feature in self.tagger.iterparse(text):
      ruby = None
      type = mecablex.getsurfacetype(surface)
      if type in (mecabdef.SURFACE_KANJI, mecabdef.SURFACE_KANA):
        if tr and not (len(surface) == 1 and type == mecabdef.SURFACE_KANA): # do not translate single kana
          ruby = self.translate(tr, surface, feature)
        if not ruby:
          ruby = fmt.getlatin(feature) # always show latin translation
        if not ruby and featureconv:
          ruby = featureconv(feature)
        if not ruby and (show_ruby_kana or type == mecabdef.SURFACE_KANJI):
          if not ruby and surfconv:
            ruby = surfconv(surface)
          if not ruby:
            kata = fmt.getkata(feature)
            if kata and kataconv:
              ruby = kataconv(kata)
              if ruby == surface:
                ruby = None
        if not ruby and type == mecabdef.SURFACE_KANJI:
          ruby = self.UNKNOWN_RUBY
      yield surface, ruby, feature, type

class MeCabParser(object):
  def __init__(self, tagger=None):
    self.__d = _MeCabParser(tagger)

  def tagger(self): return self.__d.tagger # -> MeCabTagger
  def setTagger(self, v): self.__d.tagger = v

  def iterparseToRuby(self, text, ruby=mecabdef.RB_HIRA, tr=None, show_ruby_kana=False):
    """
    @param  text  unicode
    @param  ruby  str  type
    @param* tr  unicode -> unicode  translate function
    @param* show_ruby_kana  bool  show ruby for kana as well  by default, only for kanji
    @yield  (unicode surface, unicode ruby, unicode surface)
    """
    kwargs = {}
    if ruby == mecabdef.RB_VI:
      kwargs['surfconv'] = _ja2vi
      kwargs['kataconv'] = jaconv.kata2romaji
    elif ruby == mecabdef.RB_TR:
      kwargs['featureconv'] = self.__d.featureTrans
      kwargs['kataconv'] = jaconv.kata2romaji
    else:
      kwargs['kataconv'] = getkataconv(ruby)
    return self.__d.iterparseToRuby(text, tr=tr, show_ruby_kana=show_ruby_kana, **kwargs)

  def toRuby(self, text, ruby=mecabdef.RB_HIRA, sep=None):
    """
    @param  text  unicode
    @param* ruby  unicode
    @param* sep  unicode or None
    @return  unicode
    """
    if sep is None:
      sep = ' ' if mecabdef.rb_has_space(ruby) else ''
    if ruby == mecabdef.RB_VI:
      q = self.__d.iterparseToVi(text)
    elif ruby == mecabdef.RB_TR:
      q = self.__d.iterparseToTrans(text)
    else:
      q = self.__d.iterparseToKata(text)
      conv = getkataconv(ruby)
      q = imap(conv, q)
    ret = sep.join(q)
    if mecabdef.rb_is_thin(ruby):
      ret = uniconv.wide2thin(ret)
    if mecabdef.rb_is_thin(ruby):
      ret = jpchars.wide2thin_punct(ret)
    return ret

  def toRomaji(self, text, capital=True):
    """
    @param  text  unicode
    @param* space  bool
    @return  unicode  plain text
    """
    ret = self.toRuby(text, sep=' ', ruby=mecabdef.RB_ROMAJI)
    if capital:
      ret = capitalizeromaji(ret)
    return ret

if __name__ == '__main__':
  dicdir = '/opt/local/lib/mecab/dic/ipadic-utf8'
  dicdir = '/Users/jichi/opt/Visual Novel Reader/Library/Dictionaries/ipadic'
  dicdir = '/Users/jichi/src/unidic'
  dicdir = '/opt/local/lib/mecab/dic/naist-jdic-utf8'

  #rcfile = '/Users/jichi/stream/Library/Dictionaries/mecabrc/ipadic.rc'
  rcfile = '/Users/jichi/stream/Library/Dictionaries/mecabrc/unidic.rc'

  #userdic = '/Users/jichi/stream/Caches/Dictionaries/EDICT/edict.dic'
  userdic = '/Users/jichi/stream/Library/Frameworks/Sakura/py/libs/mecabdic/edict.dic'

  import mecabtagger
  mecabtagger.setenvrc(rcfile)

  mp = MeCabParser()
  if userdic:
    mp.tagger().setUserdic(userdic)

  #t = u"可愛いよ"
  #t = u'今日はいい天気ですね'
  #t = u'すもももももももものうち'
  #t = u'しようぜ'
  #t = u'思ってる'
  #t = u'オリジナル'
  #t += u'巨乳'
  #t += u"。"
  #t = '勝てば官軍'
  t = u'足僕話わたし顔ちらりと流し目、含み笑い、呆れた顔。しょんぼり肩をすくめた。'
  #print mp.toRuby(t, mecabdef.RB_TR)
  #print mp.toRomaji(t)

  #tr = lambda t: t

  for it in mp.iterparseToRuby(t, mecabdef.RB_TR):
    print it[0], it[1] #, it[2]

# EOF

#def tolou(self, text, termEnabled=False, ruby=mecabdef.RB_TR):
#  """
#  @param  text  unicode
#  @param* termEnabled  bool  whether query terms
#  @param* type  bool  whether return type
#  @param* ruby  unicode
#  @return  unicode
#  """
#  # Add space between words
#  return ' '.join(furigana or surface for surface,furigana in
#      self.parse(text, termEnabled=termEnabled, reading=True, lougo=True, ruby=ruby))
