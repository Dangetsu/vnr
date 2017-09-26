# coding: utf8
# vichars.py
# 7/12/2015 jichi
from functools import partial
import unichars

# http://vietunicode.sourceforge.net/charset/
# https://en.wikipedia.org/wiki/Vietnamese_alphabet
VIET_TONE_CHARS = u"ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯư"
def isviet(ch):
  """
  @param  ch  str
  @return  bool
  """
  if len(ch) != 1:
    return False
  if ch in VIET_TONE_CHARS:
    return True
  ch = ord(ch[0])
  return 0x1ea0 <= ch and ch <= 0x1ef9

def anyviet(text):
  """
  @param  text  unicode
  @return  bool
  """
  for c in text:
    if isviet(c):
      return True
  return False

def allviet(text):
  """
  @param  text  unicode
  @return  bool
  """
  if not text:
    return False
  for c in text:
    if ord(c) >= 128 and not isviet(c):
      return False
  return True

# EOF
