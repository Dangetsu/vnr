# coding: utf8
# mecabrender.py
# 3/29/2014 jichi

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

#import re
import MeCab
from sakurakit import skstr
from unitraits.uniconv import kata2hira
import mecabdef, mecabfmt, mecabparse
from jaconv.jaconv import hira2romaji

## Parse plain text

_PARAGRAPH_DELIM = frozenset(u"\n。!！?？♪…【】■") # missing "?", which would cause trouble when it comes to "(?)"
_PARAGRAPH_CLASSES = 'word2', 'word1', 'word4', 'word3'
def parseparagraph(text, fmt=mecabfmt.DEFAULT, parse=None, **kwargs):
  """
  @param* parse  override parsing method
  @param  kwargs  the same as parse
  @yield  [(unicode surface, unicode ruby, str className, unicode feature)]
  """
  ret = []
  i = j = 0
  className = ''
  l = parse(text, **kwargs) if parse else mecabparse.parse(text, type=True, reading=True, feature=True, **kwargs)
  if l:
    for surf, ch, yomi, feature in l:
      # Note: For cabocha, the coloring theme is needed to be changed
      feature = renderfeature(feature, fmt) if feature else ''
      if ch in (mecabdef.TYPE_VERB, mecabdef.TYPE_NOUN, mecabdef.TYPE_KATAGANA):
        i += 1
        className = _PARAGRAPH_CLASSES[i % 2]
      elif ch == mecabdef.TYPE_MODIFIER: # adj or adv
        j += 1
        className = _PARAGRAPH_CLASSES[2 + j % 2]
      entry = surf, (yomi or ''), feature, className
      ret.append(entry)
      if len(surf) == 1 and surf in _PARAGRAPH_DELIM:
        yield ret
        ret = []
  if ret:
    yield ret

## Render

def renderfeature(feature, fmt):
  """
  @param  feature  unicode
  @param  fmt  mecabfmt
  @return  unicode or None

  Example feature: 名詞,サ変接続,*,*,*,*,感謝,カンシャ,カンシャ
  Input feature:
    品詞,品詞細分類1,品詞細分類2,品詞細分類3,活用形,活用型,原形,読み,発音
  Rendered feature:
    原形,発音,品詞,品詞細分類1,品詞細分類2,品詞細分類3,活用形
  """
  l = feature.replace('*', '').split(',')
  ret = filter(bool, l[:fmt.COL_BASIC])

  try:
    surface = l[fmt.COL_SURFACE]
    kata = l[fmt.COL_KATA]
    hira = kata2hira(kata)

    if hasattr(fmt, 'COL_KANJI'):
      kanji = l[fmt.COL_KANJI]
      if kanji not in (surface, kata, hira):
        ret.insert(0, kanji)

    if hasattr(fmt, 'COL_ORIG'):
      orig = l[fmt.COL_ORIG]
      ret.append(orig)

    #if surface not in (hira, kata):
    if hira != surface:
      romaji = hira2romaji(hira)
      if hira != romaji:
        ret.insert(0, romaji)
      ret.insert(0, hira)
    ret.insert(0, surface)
  except IndexError: pass

  return ', '.join(ret)

if __name__ == '__main__':
  t = u"こんにちは！ご主人さま"
  for words in parseparagraph(t):
    for word in words:
      print word

# EOF

#def rendertable(text, features=None, rubySize='10px', colorize=False, center=True, **kwargs):
#  """
#  @param  text  unicode
#  @param* rubySize  str
#  @param* colorsize  bool
#  @param* center  bool
#  @param* features  {unicode surface:(unicode feature, fmt)} or None
#  @return  unicode  HTML table
#  """
#  l = []
#  i = j = 0
#  hasfeature = features is not None
#  color = None
#  for it in parse(text, type=True, feature=hasfeature, reading=True, **kwargs):
#    if hasfeature:
#      surface, ch, yomi, f, fmt = it
#    else:
#      surface, ch, yomi = it
#    if colorize:
#      color = None
#      if ch in (mecabdef.TYPE_VERB, mecabdef.TYPE_NOUN, mecabdef.TYPE_KATAGANA):
#          i += 1
#          color = 'rgba(255,0,0,40)' if i % 2 else 'rgba(255,255,0,40)'   # red or yellow
#      elif ch == mecabdef.TYPE_MODIFIER: # adj or adv
#        j += 1
#        #color = "rgba(0,255,0,40)" if j % 2 else "rgba(255,0,255,40)" # green or magenta
#        color = "rgba(0,255,0,40)" if j % 2 else "rgba(0,0,255,40)" # green or blue
#    l.append((surface, yomi, color))
#    if hasfeature:
#      features[surface] = f, fmt
#  return "" if not l else rc.jinja_template('html/furigana').render({
#    'tuples': l,
#    #'bgcolor': "rgba(0,0,0,5)",
#    'rubySize': rubySize,
#    'center': center,
#  })

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

