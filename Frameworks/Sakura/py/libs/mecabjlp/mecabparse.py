# coding: utf8
# mecabparse.py
# 10/12/2012 jichi
#
# doc: http://mecab.googlecode.com/svn/trunk/mecab/doc/index.html
# doxygen: http://mecab.googlecode.com/svn/trunk/mecab/doc/doxygen/annotated.html

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

#import re
import MeCab
from sakurakit import skos, skstr
from jaconv import jaconv
from unitraits import jpchars, uniconv
import mecabdef, mecabfmt

if skos.WIN:
  from msime import msime
  HAS_MSIME = msime.ja_valid() # cached
else:
  HAS_MSIME = False

## Parser ##

#_rx_cypher = re.compile(ur"(?<=["
#  u"ルユュムフブプヌツヅスク"
#  u"ロヨョモホボポノトドソゾコォ"
#u"])ー")
#def _repairkatagana(text):
#  """
#  @param  text  unicode
#  @return  unicode
#  """
#  return _rx_cypher.sub(u'ウ', text)

def parse(text, tagger=None, type=False, fmt=mecabfmt.DEFAULT, reading=False, wordtr=None, feature=False, ruby=mecabdef.RB_HIRA, readingTypes=(mecabdef.TYPE_VERB, mecabdef.TYPE_NOUN)):
  """
  @param  text  unicode
  @param  tagger  MeCabTagger
  @param  fmt  mecabfmt
  @param* wordtr  (unicode)->unicode
  @param* type  bool  whether return type
  @param* reading  bool   whether return yomigana
  @param* feature  bool   whether return feature
  @param* ruby  unicode
  @param* readingTypes  (int type) or [int type]
  @yield  (unicode surface, int type, unicode yomigana or None, unicode feature or None)
  """
  if not tagger:
    import mecabtag
    tagger = mecabtag.gettagger()
  if reading:
    #if ruby == mecabdef.RB_TR:
    #  wordtr = None
    katatrans = (uniconv.kata2hira if ruby == mecabdef.RB_HIRA else
                 jaconv.kata2ko if ruby == mecabdef.RB_HANGUL else
                 jaconv.kata2th if ruby == mecabdef.RB_THAI else
                 jaconv.kata2ar if ruby == mecabdef.RB_AR else
                 #jaconv.kata2kanji if ruby == mecabdef.RB_KANJI else
                 jaconv.kata2romaji if ruby in (mecabdef.RB_ROMAJI, mecabdef.RB_ROMAJI_RU, mecabdef.RB_TR) else
                 None)
    if ruby in (mecabdef.RB_ROMAJI, mecabdef.RB_ROMAJI_RU, mecabdef.RB_HANGUL, mecabdef.RB_THAI, mecabdef.RB_AR): # , mecabdef.RB_KANJI
      readingTypes = None
  encoding = mecabdef.DICT_ENCODING
  feature2kata = fmt.getkata
  node = tagger.parseToNode(text.encode(encoding))
  while node:
    if node.stat not in (MeCab.MECAB_BOS_NODE, MeCab.MECAB_EOS_NODE):
      surface = node.surface[:node.length];
      surface = surface.decode(encoding, errors='ignore')
      #surface = surface.encode('sjis')

      if len(surface) == 1 and surface in jpchars.set_punct:
        char_type = mecabdef.TYPE_PUNCT
      else:
        char_type = node.char_type

      if reading:
        yomigana = None
        #if node.char_type in (mecabdef.TYPE_VERB, mecabdef.TYPE_NOUN, mecabdef.TYPE_KATAGANA, mecabdef.TYPE_MODIFIER):
        f = None
        if feature:
          f = node.feature.decode(encoding, errors='ignore')
        #f = node.feature.decode(encoding, errors='ignore')
        if not readingTypes or char_type in readingTypes or char_type == mecabdef.TYPE_KATAGANA and wordtr: # always translate katagana
          if wordtr:
            if not yomigana:
              yomigana = wordtr(surface)
          if not yomigana:
            if not feature:
              f = node.feature.decode(encoding, errors='ignore')
            katagana = feature2kata(f)
            if katagana:
              furigana = None
              if katagana == '*':
                # Use MSIME as fallback
                unknownYomi = True
                if HAS_MSIME and len(surface) < msime.IME_MAX_SIZE:
                  if ruby == mecabdef.RB_HIRA:
                    yomigana = msime.to_hira(surface)
                  else:
                    yomigana = msime.to_kata(surface)
                    if yomigana:
                      if ruby == mecabdef.RB_HIRA:
                        pass
                      elif ruby in (mecabdef.RB_ROMAJI, mecabdef.RB_ROMAJI_RU):
                        if ruby == mecabdef.RB_ROMAJI_RU:
                          conv = jaconv.kata2ru
                        else:
                          conv = jaconv.kata2romaji
                        yomigana = uniconv.wide2thin(conv(yomigana))
                        if yomigana == surface:
                          yomigana = None
                          unknownYomi = False
                      elif ruby == mecabdef.RB_HANGUL:
                        yomigana = jaconv.kata2ko(yomigana)
                      #elif ruby == mecabdef.RB_KANJI:
                      #  yomigana = jaconv.kata2kanji(yomigana)
                if not yomigana and unknownYomi and readingTypes:
                  yomigana = '?'
              else:
                #katagana = _repairkatagana(katagana)
                yomigana = katatrans(katagana) if katatrans else katagana
                if yomigana == surface:
                  yomigana = None
        if not type and not feature:
          yield surface, yomigana
        elif type and not feature:
          yield surface, char_type, yomigana
        elif not type and feature:
          yield surface, yomigana, f
        else: # render all
          yield surface, char_type, yomigana, f
      elif not type and not feature:
        yield surface
      elif type and not feature: # and type
        yield surface, char_type
      elif not type and feature:
        f = node.feature.decode(encoding, errors='ignore')
        yield surface, f
      elif type and feature:
        f = node.feature.decode(encoding, errors='ignore')
        yield surface, char_type, f
      #else:
      #  assert False, "unreachable"

    node = node.next

def toyomi(text, ruby=mecabdef.RB_HIRA, sep='', **kwargs):
  """
  @param  text  unicode
  @param* ruby  unicode
  @param* sep  unicode
  @return  unicode
  """
  furitrans = (uniconv.kata2hira if ruby == mecabdef.RB_HIRA else
               uniconv.hira2kata if ruby == mecabdef.RB_KATA else
               jaconv.kana2romaji if ruby == mecabdef.RB_ROMAJI else
               jaconv.kana2ko if ruby == mecabdef.RB_HANGUL else
               jaconv.kana2th if ruby == mecabdef.RB_THAI else
               jaconv.kana2ar if ruby == mecabdef.RB_AR else
               #jaconv.kana2kanji if ruby == mecabdef.RB_KANJI else
               uniconv.kata2hira)
  # Add space between words
  return sep.join(furigana or furitrans(surface) for surface,furigana in
      parse(text, reading=True, ruby=ruby, **kwargs))

_repl_capitalize = skstr.multireplacer({
  #' Da ': ' da ',
  ' De ': ' de ',
  ' Ha ': ' ha ',
  ' Na ': ' na ',
  ' No ': ' no ',
  ' Ni ': ' ni ',
  ' To ': ' to ',
  #' O ': ' o ',
  ' Wo ': ' wo ',
  #' Yo ': ' yo ',
})
def capitalizeromaji(text):
  """
  @param  text  unicode
  @return  unicode
  """
  return _repl_capitalize(text.title())

def toromaji(text, capitalize=True, **kwargs):
  """
  @param  text  unicode
  @param* space  bool
  @return  unicode  plain text
  """
  ret = toyomi(text, sep=' ', ruby=mecabdef.RB_ROMAJI, **kwargs)
  if capitalize:
    ret = capitalizeromaji(ret)
  return ret

if __name__ == '__main__':
  dicdir = '/opt/local/lib/mecab/dic/ipadic-utf8'
  dicdir = '/Users/jichi/opt/Visual Novel Reader/Library/Dictionaries/ipadic'
  dicdir = '/Users/jichi/src/unidic'
  dicdir = '/opt/local/lib/mecab/dic/naist-jdic-utf8'

  #rcfile = '/Users/jichi/stream/Library/Dictionaries/mecabrc/ipadic.rc'
  rcfile = '/Users/jichi/stream/Library/Dictionaries/mecabrc/unidic.rc'

  import mecabtag
  mecabtag.setenvrc(rcfile)
  tagger = mecabtag.gettagger(dicdir=dicdir)

  t = u"可愛いよ"
  t = u'今日はいい天気ですね'
  t = u'すもももももももものうち'
  t = u'しようぜ'
  t = u'思ってる'
  t = u'巨乳'
  print toyomi(t)
  print toromaji(t)

  print toyomi(t)

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

