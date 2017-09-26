# coding: utf8
# unichars.py
# 6/16/2014 jichi
import re
import string

# Some of the kana characters are skipped
# See: http://stackoverflow.com/questions/3826918/how-to-classify-japanese-characters-as-either-kanji-or-kana
# Here's the range used by Google Guava
# - Hiragana: \u3040-\u309f
# - Katagana: \u30a0-\u30ff

# Orders of hiragana and katagana
ORD_HIRA_FIRST = 12353
ORD_HIRA_LAST = 12438
DIST_HIRA_KATA = 96
ORD_KATA_FIRST = ORD_HIRA_FIRST + DIST_HIRA_KATA
ORD_KATA_LAST = ORD_HIRA_LAST + DIST_HIRA_KATA

# Orders of wide and thin characters
ORD_THIN_FIRST = 33
ORD_THIN_LAST = 126
DIST_THIN_WIDE = 65248
ORD_WIDE_FIRST = ORD_THIN_FIRST + DIST_THIN_WIDE
ORD_WIDE_LAST = ORD_THIN_LAST + DIST_THIN_WIDE

# The same range as Google Guava
# See: http://stackoverflow.com/questions/3826918/how-to-classify-japanese-characters-as-either-kanji-or-kana
ORD_KANJI_FIRST = 0x4e00 # = u'一'
ORD_KANJI_LAST = 0x9faf # = u'龯'

ORD_DIGIT_FIRST = ord('0')
ORD_DIGIT_LAST = ord('9')

ORD_IALPHA_FIRST = ord('a')
ORD_IALPHA_LAST = ord('z')
ORD_UALPHA_FIRST = ord('A')
ORD_UALPHA_LAST = ord('Z')

# http://stackoverflow.com/questions/10981258/how-can-i-specify-cyrillic-character-ranges-in-a-python-3-2-regex
ORD_CYRIL_FIRST = 0x400
ORD_CYRIL_LAST = 0x500

#ORD_NUM_FIRST = ord('0') # 48
#ORD_NUM_LAST = ord('9') # 57

s_ascii_punct = ',.\'"?!~'

def ordany(text, start, stop):
  """
  @param  text  unicode
  @param  start  int
  @param  stop  int
  @return  bool
  """
  for c in text:
    u8 = ord(c)
    if u8 >= start and u8 <= stop:
      return True
  return False

def ordall(text, start, stop):
  """
  @param  text  unicode
  @param  start  int
  @param  stop  int
  @return  bool
  """
  if not text:
    return False
  for c in text:
    u8 = ord(c)
    if u8 < start or u8 > stop:
      return False
  return True

def isascii(s):
  """
  @param  s  unicode
  @return  bool
  """
  if len(s) == 1:
    return ord(s) < 128
  else:
    return all(ord(c) < 128 for c in s)

def isspace(ch):
  """
  @param  ch  unicode
  @return  bool
  """
  return ch in string.whitespace or ch == u"\u3000"

_rx_allspace = re.compile(r'^\s$', re.UNICODE)
def allspace(text):
  """
  @param  text  unicode
  @return  bool
  """
  return bool(text and _rx_allspace.match(text))

_rx_space = re.compile(r'\s', re.UNICODE)
def anyspace(text):
  """
  @param  text  unicode
  @return  bool
  """
  return bool(text and _rx_space.search(text))

def isalpha(ch):
  """
  @param  ch  unicode
  @return  bool
  """
  if len(ch) == 1:
    ch = ord(ch)
    return ORD_IALPHA_FIRST <= ch and ch <= ORD_IALPHA_LAST or ORD_UALPHA_FIRST <= ch and ch <= ORD_UALPHA_LAST
  return False

def findrange(text, start, stop):
  """
  @param  text  str
  @param  start  int
  @param  stop  int
  @return  int
  """
  for i,c in enumerate(text):
    c = ord(c)
    if start <= c and c <= stop:
      return i
  return -1

def charinrange(ch, start, stop):
  """
  @param  ch  unicode
  @param  start  int
  @param  stop  int
  @return  bool
  """
  #if isinstance(ch, basestring):
  if len(ch) != 1:
    return False
  ch = ord(ch)
  return start <= ch and ch <= stop

def isdigit(ch):
  """
  @param  ch  unicode
  @return  bool
  """
  return charinrange(ch, ORD_DIGIT_FIRST, ORD_DIGIT_FIRST)

# EOF
