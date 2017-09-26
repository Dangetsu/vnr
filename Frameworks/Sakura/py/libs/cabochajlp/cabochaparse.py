# coding: utf8
# cabochaparse.py
# 6/13/2014 jichi
#
# See: cabocha/src/tree.cpp
#   void write_tree(const Tree &tree, StringBuffer *os, int output_layer, int charset)
#    const size_t size = tree.token_size();
#    for (size_t i = 0; i < size;) {
#      size_t cid = i;
#      chunks.resize(chunks.size() + 1);
#      std::string surface;
#      for (; i < size; ++i) {
#        const Token *token = tree.token(i);
#        if (in && token->ne &&
#            (token->ne[0] == 'B' || token->ne[0] == 'O')) {
#          surface += "</";
#          surface += ne;
#          surface += ">";
#          in = false;
#        }
#
#        if (i != cid && token->chunk) {
#          break;
#        }
#
#        if (token->ne && token->ne[0] == 'B') {
#          ne = std::string(token->ne + 2);
#          surface += "<";
#          surface += ne;
#          surface += ">";
#          in = true;
#        }
#       surface += std::string(token->surface);

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

#import re
import MeCab
from sakurakit import skos
from jaconv import jaconv
from unitraits import uniconv
from mecabjlp import mecabdef, mecabfmt
import cabochadef

if skos.WIN:
  from msime import msime
  HAS_MSIME = msime.ja_valid() # cached
else:
  HAS_MSIME = False

#DEBUG = True
DEBUG = False

## Parser ##

def parse(text, parser=None, type=False, fmt=mecabfmt.DEFAULT, wordtr=None, group=False, reading=False, feature=False, ruby=mecabdef.RB_HIRA, readingTypes=(cabochadef.TYPE_KANJI,)):
  """
  @param  text  unicode
  @param  parser  CaboCha.Parser
  @param  fmt  mecabfmt
  @param* wordtr  (unicode)->unicode
  @param* type  bool  whether return type
  @param* group  bool   whether return group id
  @param* reading  bool   whether return yomigana
  @param* feature  bool   whether return feature
  @param* ruby  unicode
  @param* readingTypes  (int type) or [int type]
  @yield  (unicode surface, int type, unicode yomigana or None, unicode feature or None)
  """
  if not parser:
    import cabocharc
    parser = cabocharc.parser()
  if reading:
    #if ruby == mecabdef.RB_TR:
    #  wordtr = None
    katatrans = (uniconv.kata2hira if ruby == mecabdef.RB_HIRA else
                 jaconv.kata2ko if ruby == mecabdef.RB_HANGUL else
                 jaconv.kata2th if ruby == mecabdef.RB_THAI else
                 #jaconv.kata2kanji if ruby == mecabdef.RB_KANJI else
                 jaconv.kata2romaji if ruby in (mecabdef.RB_ROMAJI, mecabdef.RB_ROMAJI_RU, mecabdef.RB_TR) else
                 None)
    if ruby in (mecabdef.RB_ROMAJI, mecabdef.RB_ROMAJI_RU, mecabdef.RB_HANGUL, mecabdef.RB_THAI): # , mecabdef.RB_KANJI
      readingTypes = None
  encoding = cabochadef.DICT_ENCODING
  feature2kata = fmt.getkata

  tree = parser.parse(text.encode(encoding))
  size = tree.token_size()
  newgroup = True
  group_id = 0
  if DEBUG:
     group_surface = ''
  for i in xrange(tree.token_size()):
    token = tree.token(i)
    surface = token.surface.decode(encoding, errors='ignore')

    if newgroup and token.chunk:
      group_id += 1
      if DEBUG:
        print "group surface %s:" % group_id, group_surface
        group_surface = ''
      newgroup = False
    if DEBUG:
      group_surface += surface
    newgroup = True

    char_type = cabochadef.surface_type(surface)

    if reading:
      yomigana = None
      #if node.char_type in (mecabdef.TYPE_VERB, mecabdef.TYPE_NOUN, mecabdef.TYPE_KATAGANA, mecabdef.TYPE_MODIFIER):
      f = None
      if feature:
        f = token.feature.decode(encoding, errors='ignore')
      if not readingTypes or char_type in readingTypes or char_type == cabochadef.TYPE_RUBY and wordtr: # always translate katagana
        if wordtr:
          if not yomigana:
            yomigana = wordtr(surface)
        if not yomigana: #and not lougo:
          if not feature:
            f = token.feature.decode(encoding, errors='ignore')
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
      if group:
        if not type and not feature:
          yield surface, yomigana, group_id
        elif type and not feature:
          yield surface, char_type, yomigana, group_id
        elif not type and feature:
          yield surface, yomigana, f, group_id
        else: # render all
          yield surface, char_type, yomigana, f, group_id
      else:
        if not type and not feature:
          yield surface, yomigana
        elif type and not feature:
          yield surface, char_type, yomigana
        elif not type and feature:
          yield surface, yomigana, f
        else: # render all
          yield surface, char_type, yomigana, f
    elif group:
      if not type and not feature:
        yield surface, group_id
      elif type and not feature: # and type
        yield surface, char_type, group_id
      elif not type and feature:
        f = token.feature.decode(encoding, errors='ignore')
        yield surface, f, group_id
      elif type and feature:
        f = token.feature.decode(encoding, errors='ignore')
        yield surface, char_type, f, group_id
      #else:
      #  assert False, "unreachable"
    else:
      if not type and not feature:
        yield surface
      elif type and not feature: # and type
        yield surface, char_type
      elif not type and feature:
        f = token.feature.decode(encoding, errors='ignore')
        yield surface, f
      elif type and feature:
        f = token.feature.decode(encoding, errors='ignore')
        yield surface, char_type, f
      #else:
      #  assert False, "unreachable"

if __name__ == '__main__':
  import CaboCha
  c = CaboCha.Parser()

  #t = u"太郎はこの本を二郎を見た女性に渡した。"
  t = u"「どれだけ必死に働こうとも、所詮、安月給の臨時教師ですけどね」"

  if True:
    for it in parse(t, parser=c, reading=True, group=True):
      print it[0], it[1], it[-1]


  if False:
    sentence = t.encode('utf8')
    print c.parseToString(sentence)

    tree =  c.parse(sentence)

    print tree.toString(CaboCha.FORMAT_TREE)
    #print tree.toString(CaboCha.FORMAT_LATTICE)

    print '#', type(c)
    print dir(c)
    print
    print '#', type(tree)
    print dir(tree)

    print tree.chunk_size()
    print tree.empty()
    print tree.output_layer()
    print tree.posset()
    #print tree.read()
    print tree.sentence()
    print tree.sentence_size()

    # This is the original logic
    size = tree.token_size()
    i = 0
    while i < size:
      cid = i
      surface = ''
      while i < size:
        token = tree.token(i)
        if i != cid and token.chunk:
          break
        surface += token.surface
        i += 1
      print cid, surface

    # This is my logic
    print '-' * 5

    surf = ''
    for i in range(tree.token_size()):
      tok = tree.token(i)
      if surf and tok.chunk:
        print surf
        surf = ''
      surf += tok.surface
    if surf:
      print surf
      surf = ''

    print '-' * 5

    tok = tree.token(0)
    print
    print '#', type(tok)
    print dir(tok)
    print tok.surface
    print tok.feature
    print tok.ne
    print tok.additional_info
    print tok.feature_list_size
    #print tok.feature_list(0)
    #print tok.feature_list(1)

# EOF
