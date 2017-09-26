# coding: utf8
# mecablex.py
# 2/24/2014 jichi

import re
from unitraits import jpchars
import mecabdef

ORD_THIN_DIGIT_FIRST = ord('0')
ORD_THIN_DIGIT_LAST = ord('9')
ORD_WIDE_DIGIT_FIRST = ord(u'０')
ORD_WIDE_DIGIT_LAST = ord(u'９')
def alldigit(text):
  """
  @param  text  unicode
  @return  bool
  """
  if not text:
    return False
  for ch in text:
    ch = ord(ch)
    if not (ch >= ORD_THIN_DIGIT_FIRST and ch <= ORD_THIN_DIGIT_LAST or ch >= ORD_WIDE_DIGIT_FIRST and ch <= ORD_WIDE_DIGIT_LAST):
      return False
  return True

def getsurfacetype(text): # unicode -> int
  if jpchars.allpunct(text):
    return mecabdef.SURFACE_PUNCT
  if jpchars.anykanji(text):
    return mecabdef.SURFACE_KANJI
  if alldigit(text):
    return mecabdef.SURFACE_NUMBER
  if jpchars.anykana(text):
    return mecabdef.SURFACE_KANA
  return mecabdef.SURFACE_UNKNOWN

# EOF

