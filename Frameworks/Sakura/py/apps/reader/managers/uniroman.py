# coding: utf8
# uniroman.py
# 1/5/2014 jichi
import re
from unidecode import unidecode
from unitraits import jpchars
from hanjaconv import hanjaconv
from pinyinconv import pinyinconv
#from opencc.opencc import ja2zht
from convutil import zht2zhs
from hanviet import hanviet
import defs, rc

__other_punct = u'《》“”‘’"\'，,? 　' # Chinese/English punctuations
_s_punct = jpchars.s_punct + __other_punct + '.()'
_re_punct = re.compile(ur"([%s\.\(\)])" % (''.join(jpchars.s_punct) + __other_punct))
def _splittext(text, language):
  """
  @param  text  unicode
  @param  text  str
  @yield  unicode
  """
  if language.startswith('zh'):
    return text
  else:
    return filter(bool, _re_punct.split(text)) # split by space and punctuation

def _toroman(text, language='', type=''):
  """
  @param  text  unicode
  @param* language  str
  @param* type  str
  """
  if not text or not isinstance(text, unicode):
    return text
  if language.startswith('zh'):
    #text = ja2zht(text)
    #text = ko2zht(text)
    t = text
    if type == defs.PINYIN_VI:
      if language == 'zht':
        t = zht2zhs(t)
      if len(t) == 1:
        t = hanviet.lookupword(t) # faster
      else:
        t = hanviet.toreading(t)
    elif type == defs.PINYIN_TONE:
      if len(t) == 1:
        t = pinyinconv.lookup(t, tone=True)
      else:
        t = pinyinconv.to_pinyin(t, delim='', tone=True, capital=False)
    if not t or t == text:
      t = unidecode(text)
    if t:
      text = t
      #text = t.title() # always title
  else:
    text = unidecode(text)
    if text and language == 'ko':
      text = text.title()
  return text

def _iterparseruby_ko(text, romajaRubyEnabled=True, hanjaRubyEnabled=True, **kwargs):
  """
  @param  text  unicode
  @param* romajaRubyEnabled  bool
  @param* hanjaRubyEnabled  bool
  @yield  (unicode surface, unicode yomi or None, int groupId or None)
  """
  for group, l in enumerate(hanjaconv.to_hanja_list(text)):
    for surface,yomi in l:
      if len(surface) == 1 and surface in _s_punct:
        group = None
        yomi = None
      else:
        if hanjaRubyEnabled and romajaRubyEnabled:
          if not yomi:
            yomi = _toroman(surface, 'ko')
        elif romajaRubyEnabled:
          yomi = _toroman(surface, 'ko')
        elif hanjaRubyEnabled:
          pass
        else: # none is enabled
          yomi = None
        if yomi and yomi == surface:
          yomi = None
      if group is not None:
        group /= 2
      yield surface, yomi, group

def _iterparseruby_zh(text, language, chineseRubyType='', **kwargs):
  """
  @param  text  unicode
  @param  language  str
  @yield  (unicode surface, unicode yomi or None, int groupId or None)
  """
  for group, surface in enumerate(_splittext(text, language)):
    if len(surface) == 1 and surface in _s_punct:
      group = None
      yomi = None
    else:
      yomi = _toroman(surface, language, chineseRubyType)
      if yomi == surface:
        yomi = None
    yield surface, yomi, group

def _iterparseruby_default(text, language):
  """
  @param  text  unicode
  @param  language  str
  @yield  (unicode surface, unicode yomi or None, int groupId or None)
  """
  for group, surface in enumerate(_splittext(text, language)):
    if len(surface) == 1 and surface in _s_punct:
      group = None
      yomi = None
    else:
      yomi = _toroman(surface, language)
      if yomi == surface:
        yomi = None
    yield surface, yomi, group

def _iterparseruby(text, language, **kwargs):
  """
  @param  text  unicode
  @param  language  str
  @param* kwargs  passed to Korean
  @yield  (unicode surface, unicode yomi or None, int groupId or None)
  """
  if language == 'ko':
    return _iterparseruby_ko(text, **kwargs)
  if language.startswith('zh'):
    return _iterparseruby_zh(text, language, **kwargs)
  return _iterparseruby_default(text, language)

def _iterrendertable(text, language, charPerLine=100, rubySize=10, colorize=False, center=True, invertRuby=False, **kwargs):
  """
  @param  text  unicode
  @param  language  unicode
  @param* charPerLine  int  maximum number of characters per line
  @param* rubySize  float
  @param* colorsize  bool
  @param* center  bool
  @param* invertRuby  bool
  @param* features  {unicode surface:(unicode feature, fmt)} or None
  @param* kwargs  passed to Korean
  @yield  unicode  HTML table
  """
  render = rc.jinja_template('html/furigana').render

  i = j = 0

  line = []
  lineCount = 0 # int  estimated line width, assume ruby has half width
  color = None
  groupColor = None if language.startswith('zh') else '#ff8' # yellow

  COLORS = (
    'rgba(255,0,0,40)', # red
    'rgba(0,255,0,40)',  # green
    'rgba(255,255,0,40)', # yellow
    "rgba(0,0,255,40)", # blue
  )

  PADDING_FACTOR = 0.1
  LATIN_YOMI_WIDTH = 0.45 # 2/6 ~ 1/2 # tuned for Vietnamese
  KANJI_YOMI_WIDTH = 0.55 # = 1/2 + 0.05
  # yomi size / surface size

  romajiRuby = language.startswith('zh') # use romaji width only for pinyin

  roundRubySize = int(round(rubySize)) or 1
  paddingSize = int(round(rubySize * PADDING_FACTOR)) or 1 # at least 1 pixel

  yomiWidth = LATIN_YOMI_WIDTH if romajiRuby else KANJI_YOMI_WIDTH
  if invertRuby:
    paddingSize *= 2 # increase padding size when invert
    yomiWidth *= 1.2 # increase yomi font size when invert

  #if paddingSize and language == 'ko' and not kwargs.get('romajaRubyEnabled'):
  #  paddingSize = 0
  rubyExists = False

  RUBY_FONT = 'Tahoma'

  for paragraph in text.split('\n'):
    for surface, yomi, group in _iterparseruby(paragraph, language, **kwargs):

      if colorize:
        color = COLORS[group % len(COLORS)] if group is not None else None
        #if ch == cabochadef.TYPE_KANJI:
        #  i += 1
        #  color = 'rgba(255,0,0,40)' if i % 2 else 'rgba(255,255,0,40)' # red or yellow
        #elif ch == cabochadef.TYPE_RUBY:
        #  j += 1
        #  #color = "rgba(0,255,0,40)" if j % 2 else "rgba(255,0,255,40)" # green or magenta
        #  color = "rgba(0,255,0,40)" if j % 2 else "rgba(0,0,255,40)" # green or blue
        #else:
        #  color = None

      width = max(
        len(surface),
        (len(yomi)*yomiWidth + (1 if invertRuby else 0)) if yomi else 0,
      )
      if width + lineCount <= charPerLine:
        pass
      elif line:
        yield render({
          'tuples': line,
          'rubySize': roundRubySize,
          'paddingSize': paddingSize,
          'center': center,
          'groupColor': groupColor,
          'rubyExists': rubyExists,
          'rubyFont': RUBY_FONT,
        })
        line = []
        lineCount = 0
        rubyExists = False
      if invertRuby and yomi:
        #if surface:
        #  surface = wide2thin(surface)
        #if romaji and len(yomi) > 2:
        #  yomi = yomi.title()
        t = yomi, surface, color, group
      else:
        t = surface, yomi, color, group
      line.append(t)
      lineCount += width
      if yomi:
        rubyExists = True

  if line:
    yield render({
      'tuples': line,
      'rubySize': roundRubySize,
      'paddingSize': paddingSize,
      'center': center,
      'groupColor': groupColor,
      'rubyExists': rubyExists,
      'rubyFont': RUBY_FONT,
    })
    rubyExists = False

def rendertable(*args, **kwargs):
  return ''.join(_iterrendertable(*args, **kwargs))

# EOF
