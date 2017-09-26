# coding: utf8
# cabochadef.py
# 6/13/2014 jichi

from unitraits import jpchars, unichars

# ipadic encoding, either SHIFT-JIS or UTF-8
DICT_ENCODING = 'utf8'

# Reading type
TYPE_KANJI = 1
TYPE_RUBY = 2
TYPE_PUNCT = 3
TYPE_LATIN = 4
#TYPE_NUM = 5

def _ordall2(text, start1, stop1, start2, stop2):
  """
  @param  text  unicode
  @param  start1  int
  @param  stop1  int
  @param  start2  int
  @param  stop2  int
  @return  bool
  """
  for c in text:
    u8 = ord(c)
    if not (u8 >= start1 and u8 <= stop1 or u8 >= start2 and u8 <= stop2):
      return False
  return True

def is_ruby_surface(text):
  """
  @param  text  unicode
  @param  start  int
  @param  stop  int
  @return  bool
  """
  return _ordall2(text, unichars.ORD_HIRA_FIRST, unichars.ORD_HIRA_LAST, unichars.ORD_KATA_FIRST, unichars.ORD_KATA_LAST)

def is_latin_surface(text):
  """
  @param  text  unicode
  @param  start  int
  @param  stop  int
  @return  bool
  """
  return _ordall2(text, 32, unichars.ORD_THIN_LAST, unichars.ORD_WIDE_FIRST, unichars.ORD_WIDE_LAST) # 32 is space

def surface_type(text):
  """
  @param  text  unicode
  @return  int
  """
  if len(text) == 1 and text in jpchars.set_punct:
    return TYPE_PUNCT
  elif is_ruby_surface(text):
    return TYPE_RUBY
  elif is_latin_surface(text):
    return TYPE_LATIN
  else:
    return TYPE_KANJI

# EOF
