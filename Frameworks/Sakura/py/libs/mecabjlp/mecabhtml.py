# coding: utf8
# mecabhtml.py
# 10/12/2012 jichi
#
# build: http://www.freia.jp/taka/blog/759/index.html
# usage: http://d.hatena.ne.jp/fgshun/20090910/1252571625
# feature: http://mecab.googlecode.com/svn/trunk/mecab/doc/index.html?source=navbar
#     表層形\t品詞,品詞細分類1,品詞細分類2,品詞細分類3,活用形,活用型,原形,読み,発音
#
#     すもももももももものうち
#     すもも  名詞,一般,*,*,*,*,すもも,スモモ,スモモ
#     も      助詞,係助詞,*,*,*,*,も,モ,モ
#     もも    名詞,一般,*,*,*,*,もも,モモ,モモ
#     も      助詞,係助詞,*,*,*,*,も,モ,モ
#     もも    名詞,一般,*,*,*,*,もも,モモ,モモ
#     の      助詞,連体化,*,*,*,*,の,ノ,ノ
#     うち    名詞,非自立,副詞可能,*,*,*,うち,ウチ,ウチ
#     EOS

if __name__ == '__main__':
  import sys
  sys.path.append('..')

import re, weakref
from itertools import ifilter
from sakurakit import skstr
from sakurakit.skclass import memoized
from sakurakit.skdebug import dprint
import mecabdef, mecabfmt, mecabparse, mecabrender

_rx_spaces = re.compile(r'\s+')
_rx_match_spaces = re.compile(r'^\s+$')

## Render HTML ##

_WORD_CSS_CLASSES = 'word2', 'word1', 'word4', 'word3'
def _renderruby_word_iter(text, hasClass, fmt=mecabfmt.DEFAULT, **kwargs):
  """
  @yield  (str styleClass or None, unicode feature, unicode surface, unicode furigana not None)
  """
  l = []
  i = j = 0
  styleClass = None
  for surface, ch, yomi, feature in mecabparse.parse(text, type=True, reading=True, feature=True, fmt=fmt, **kwargs):
    feature = mecabrender.renderfeature(feature, fmt) if feature else ''
    if hasClass:
      styleClass = None
      if ch in (mecabdef.TYPE_VERB, mecabdef.TYPE_NOUN, mecabdef.TYPE_KATAGANA):
        i += 1
        #color = 'rgba(255,0,0,40)' if i % 2 else 'rgba(255,255,0,40)'   # red or cyan
        styleClass = _WORD_CSS_CLASSES[i % 2]
      elif ch == mecabdef.TYPE_MODIFIER: # adj or adv
        j += 1
        #color = "rgba(0,255,0,40)" if j % 2 else "rgba(0,0,255,40)" # green or blue
        styleClass = _WORD_CSS_CLASSES[2 + j % 2]
    yield styleClass, feature, surface, (yomi or '')

def _renderruby_word(text, hasClass, **kwargs):
  """
  @return  unicode  HTML
  """
  q = _renderruby_word_iter(text, hasClass=hasClass, **kwargs)
  if hasClass:
    return ''.join('<ruby class="%s" title="%s"><rb>%s</rb><rt>%s</rt></ruby>' % it for it in q)
  else:
    return ''.join('<ruby title="%s"><rb>%s</rb><rt>%s</rt></ruby>' % it[1:] for it in q)

#_rx_spaces = re.compile(r'\s+')
def _renderruby_segment(text, **kwargs):
  """
  @return  unicode  HTML
  """
  return ' '.join(_renderruby_word(it, **kwargs)
      for it in _rx_spaces.split(text) if it)

__SENTENCE_DELIM = u"\n。!！？♪…【】■" # missing "?", which would cause trouble when it comes to "(?)"
_SENTENCE_SET = frozenset(__SENTENCE_DELIM)
_SENTENCE_RE = re.compile(r"(%s)" % '|'.join(_SENTENCE_SET))
def _renderruby_sentence_iter(text, **kwargs):
  """
  @yield  unicode
  """
  for it in _SENTENCE_RE.split(text):
    if it:
      if it in _SENTENCE_SET:
        yield it
      else:
        yield _renderruby_segment(it, **kwargs)

def _renderruby_sentence(text, **kwargs):
  """
  @return  unicode  HTML
  """
  return ''.join(' ' if _rx_match_spaces.match(it) else '<span class="sentence">%s</span>' % it
      for it in _renderruby_sentence_iter(text, **kwargs) if it)

_rx_html_tags = re.compile(r"(<.+?>)")
def _renderruby_html_iter(text, **kwargs):
  """
  @yield  unicode  HTML
  """
  for it in _rx_html_tags.split(text):
    if it:
      if it[0] == '<':
        yield it
      elif _rx_match_spaces.match(text):
        yield ' '
      else:
        yield _renderruby_sentence(it, **kwargs)

def _renderruby_html(text, **kwargs):
  """
  @return  unicode  HTML
  """
  return ''.join(_renderruby_html_iter(text, **kwargs))

def renderruby(text, html=False, hasClass=True, ruby=mecabdef.RB_HIRA):
  """
  @param  text  unicode
  @param* html  bool  whether input text contains html tags
  @param* ruby  str
  @param* hasClass  bool  whether have style classes
  @return  unicode  HTML ruby list
  """
  if not text:
    return ''
  if html:
    return _renderruby_html(text, hasClass=hasClass, ruby=ruby)
  else:
    return _renderruby_segment(text, hasClass=hasClass, ruby=ruby)

def renderhtml(text, ruby=mecabdef.RB_HIRA):
  """
  @param  text  unicode
  @param* ruby  str
  """
  return renderruby(text, html=True, ruby=ruby)

if __name__ == '__main__':
  #t = u"すもももももももものうち"
  #t = u"憎しみは憎しみしか生まない"
  #t = u"童話はほとんど墓场から始まるものさ"
  t = u"Chun、ShinGura"
  t = u"レミニ、センス"
  t = u'桜小路ルナ'
  t = u'【桜小路ルナ】'
  for x,y in mecabparse.parse(t, feature=True):
    print y
    #print y.encode('sjis', errors='ignore')

  print renderhtml("<a href='hello'>%s</a>" % t)

# EOF

## Parser ##

#toyomi = _MP.toyomi
#def toyomi(text, space=True, capital=False, **kwargs):
#  """
#  @param  text  unicode
#  @param* space  bool
#  @return  unicode  plan text
#  """
#  ret = ' '.join(_MP.toyomi(it, **kwargs)
#    for it in _rx_spaces.split(text) if it
#  ) if space else _MP.toyomi(it, **kwargs)
#  if capital:
#    ret = capitalizeromaji(ret)
#  return ret

#def getfeaturesurface(feature):
#  """
#  @param  feature  unicode
#  @return  unicode
#  """
#  if feature:
#    ret = feature.split(',')[-3]
#    if ret != '*':
#      return ret
#
#def renderfeature(feature):
#  """
#  @param  feature  unicode
#  @param* surface  text
#  @return  unicode or None
#
#  Example feature: 名詞,サ変接続,*,*,*,*,感謝,カンシャ,カンシャ
#  Input feature:
#    品詞,品詞細分類1,品詞細分類2,品詞細分類3,活用形,活用型,原形,読み,発音
#  Rendered feature:
#    原形,発音,品詞,品詞細分類1,品詞細分類2,品詞細分類3,活用形
#  """
#  l = feature.replace('*', '').split(',')
#
#  l.insert(0, l[-3])
#  del l[-3] # move 原形 to l[0]
#
#  del l[-2] # delete 読み
#
#  yomi = cconv.kata2hira(l[-1])
#  del l[-1]
#  if yomi != l[0]:
#    l.insert(1, yomi) # move 発音 after 原形
#
#  l = ifilter(bool, l)
#  return ','.join(l)

#def rendertable(text, ruby=mecabdef.RB_HIRA, features=None, rubySize='10px', colorize=False, center=True):
#  """
#  @param  text  unicode
#  @param* ruby  int
#  @param* rubySize  str
#  @param* colorsize  bool
#  @param* center  bool
#  @param* features  {unicode surface:unicode feature} or None
#  @return  unicode  HTML table
#  """
#  l = []
#  i = j = 0
#  feature = features is not None
#  color = None
#  for it in parse(text, type=True, feature=feature, reading=True, ruby=ruby):
#    if feature:
#      surface, ch, yomi, f = it
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
#    if feature:
#      features[surface] = f
#  return "" if not l else rc.jinja_template('html/furigana').render({
#    'tuples': l,
#    #'bgcolor': "rgba(0,0,0,5)",
#    'rubySize': rubySize,
#    'center': center,
#  })
