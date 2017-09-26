# coding: utf8
# uniconv.py
# 12/30/2012 jichi

import re
import unichars

## Transpose code page ##

def _itertranspose(text, distance, range_start, range_end):
  """
  @yield  unicode  char
  """
  for c in text:
    cp = ord(c)
    if cp >= range_start and cp <= range_end:
      yield unichr(cp + distance)
    else:
      yield c

def transpose(text, *args):
  """
  @param  text  unicode  text to be transposed, codepoint-wise
  @param  distance  int  to the other side of the map
  @param  range_start  int  start of the range we're interested in, codepont-wise
  @param  range_end  int  end of the range we're interested in, codepoint-wise
  @return  unicode not None
  See: JapaneseTransliterator.transpose_codepoints_in_range
  """
  if not isinstance(text, unicode):
    try: text = text.decode('utf-8')
    except UnicodeDecodeError: return text
  return ''.join(_itertranspose(text, *args)) # joining is much faster than appending

## Instantiation

def thin2wide(text): return transpose(text, unichars.DIST_THIN_WIDE, unichars.ORD_THIN_FIRST, unichars.ORD_THIN_LAST).replace(u' ', u'\u3000')
def wide2thin(text): return transpose(text, -unichars.DIST_THIN_WIDE, unichars.ORD_WIDE_FIRST, unichars.ORD_WIDE_LAST).replace(u'\u3000', u' ')
def hira2kata(text): return transpose(text, unichars.DIST_HIRA_KATA, unichars.ORD_HIRA_FIRST, unichars.ORD_HIRA_LAST)
def kata2hira(text): return transpose(text, -unichars.DIST_HIRA_KATA, unichars.ORD_KATA_FIRST, unichars.ORD_KATA_LAST)

# re classes: http://www.gnu.org/software/grep/manual/html_node/Character-Classes-and-Bracket-Expressions.html
WIDE_DIST = ord(u'０') - ord(u'0')
RE_WIDE_CLASSES = {
  'blank': re.compile(ur'　'), # u\3000
  'digit': re.compile(ur'[０-９]'),
  'alpha': re.compile(ur'[ａ-ｚＡ-Ｚ]'),
  'alnum': re.compile(ur'[ａ-ｚＡ-Ｚ０-９]'),
}
def wide2thin_class(text, cls): # unicode, str -> unicode
  rx = RE_WIDE_CLASSES[cls]
  return rx.sub(_wide2thin_repl, text)
def _wide2thin_repl(m): # re match -> unicode
  return unichr(ord(m.group(0)) - WIDE_DIST)

def wide2thin_digit(text): return wide2thin_class(text, 'digit')
def wide2thin_alpha(text): return wide2thin_class(text, 'alpha')
def wide2thin_alnum(text): return wide2thin_class(text, 'alnum')

if __name__ == '__main__':
  t = u'、？！。'
  print wide2thin(t)

# EOF
