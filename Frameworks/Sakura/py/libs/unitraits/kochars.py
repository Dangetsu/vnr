# coding: utf8
# kochars.py
# 4/25/2015 jichi
from functools import partial
import unichars

def ishangul(ch):
  """
  @param  ch  str
  @return  bool
  """
  if len(ch) != 1:
    return False
  ch = ord(ch[0])
  return ch > 127 and (
    0xac00 <= ch and ch <= 0xd7a3    # Hangul Syllables (AC00-D7A3) which corresponds to (가-힣)
    or 0x1100 <= ch and ch <= 0x11ff # Hangul Jamo (1100–11FF)
    or 0x3130 <= ch and ch <= 0x318f # Hangul Compatibility Jamo (3130-318F)
    or 0xa960 <= ch and ch <= 0xa97f # Hangul Jamo Extended-A (A960-A97F)
    or 0xd7b0 <= ch and ch <= 0xd7ff # Hangul Jamo Extended-B (D7B0-D7FF)
  )

def anyhangul(text):
  """
  @param  text  unicode
  @return  bool
  """
  for c in text:
    if ishangul(c):
      return True
  return False

def allhangul(text):
  """
  @param  text  unicode
  @return  bool
  """
  if not text:
    return False
  for c in text:
    #if ord(c) >= 128 and not ishangul(c):
    if c != ' ' and not ishangul(c):
      return False
  return True

# http://en.wikipedia.org/wiki/Template:Unicode_chart_Hangul_Syllables
# http://en.wikipedia.org/wiki/Hangul_consonant_and_vowel_tables
ORD_SYLLABLE_FIRST = 0xac00
ORD_SYLLABLE_LAST = 0xd7a3
issyllable = partial(unichars.charinrange, start=ORD_SYLLABLE_FIRST, stop=ORD_SYLLABLE_LAST)

HANGUL_FINALS = (
  '',   # 0
  u'ᆨ', # 1
  u'ᆩ', # 2
  u'ᆪ', # 3
  u'ᆫ', # 4
  u'ᆬ', # 5
  u'ᆭ', # 6
  u'ᆮ', # 7
  u'ᆯ', # 8
  u'ᆰ', # 9
  u'ᆱ', # 10
  u'ᆲ', # 11
  u'ᆳ', # 12
  u'ᆴ', # 13
  u'ᆵ', # 14
  u'ᆶ', # 15
  u'ᆷ', # 16
  u'ᆸ', # 17
  u'ᆹ', # 18
  u'ᆺ', # 19
  u'ᆻ', # 20
  u'ᆼ', # 21
  u'ᆽ', # 22
  u'ᆾ', # 23
  u'ᆿ', # 24
  u'ᇀ', # 25
  u'ᇁ', # 26
  u'ᇂ', # 27
)
# http://www.verbix.com/languages/korean.php?verb=%EB%AA%A8%EB%A5%B4%EB%8B%A4
HANGUL_FINALS_ROMAJA = (
  '',  # 0
  'g', # 1 'ᆨ'
  'gg', # 2 'ᆩ'
  'gs', # 3 'ᆪ'
  'n', # 4 'ᆫ'
  'nj', # 5 'ᆬ'
  'nh', # 6 'ᆭ'
  'd', # 7 'ᆮ'
  'l', # 8 'ᆯ'
  'lg', # 9 'ᆰ'
  'lm', # 10 'ᆱ'
  'lb', # 11 'ᆲ'
  'ls', # 12 'ᆳ'
  'lt', # 13 'ᆴ'
  'lp', # 14 'ᆵ'
  'lh', # 15 'ᆶ'
  'm', # 16 'ᆷ'
  'b', # 17 'ᆸ'
  'bs', # 18 'ᆹ'
  's', # 19 'ᆺ'
  'ss', # 20 'ᆻ'
  'ng', # 21 'ᆼ'
  'j', # 22 'ᆽ'
  'c', # 23 'ᆾ'
  'k', # 24 'ᆿ'
  't', # 25 'ᇀ'
  'p', # 26 'ᇁ'
  'h', # 27 'ᇂ'
)
HANGUL_FINAL_COUNT = 28
def gethangulfinal(ch):
  """Get the final character of the 2~3 characters
  @param  ch
  @return  str or None
  """
  if ch and len(ch) == 1:
    ch = ord(ch)
    if ch >= ORD_SYLLABLE_FIRST and ch <= ORD_SYLLABLE_LAST:
      return HANGUL_FINALS[(ch - ORD_SYLLABLE_FIRST) % HANGUL_FINAL_COUNT]

HANGUL_FINAL_COUNT = 28
def gethangulfinal_en(ch):
  """Get the final character of the 2~3 characters
  @param  ch
  @return  str or None
  """
  if ch and len(ch) == 1:
    ch = ord(ch)
    if ch >= ORD_SYLLABLE_FIRST and ch <= ORD_SYLLABLE_LAST:
      return HANGUL_FINALS_ROMAJA[(ch - ORD_SYLLABLE_FIRST) % HANGUL_FINAL_COUNT]

# EOF
