# coding: utf8
# pinyinconv.py
# 1/6/2015 jichi

from sakurakit.skclass import memoized

PINYIN_DIC_PATH = './Mandarin.dat' # to be set

def setdicpath(path):
  global PINYIN_DIC_PATH
  PINYIN_DIC_PATH = path

@memoized
def converter():
  import os
  from pypinyin import PinyinConverter
  ret = PinyinConverter()
  path = PINYIN_DIC_PATH
  if os.path.exists(path):
    ret.addFile(path)
  else:
    from sakurakit.skdebug import derror
    derror("dic path does not exist:", path)
  return ret

def lookup(text, tone=True):
  """
  @param  text  unicode
  @param* tone  bool
  @return  unicode or None
  """
  if text and len(text) == 1:
    i = ord(text[0])
    if i <= 0xffff:
      return converter().lookup(i, tone)

def to_pinyin(text, delim=' ', tone=True, capital=True):
  """
  @param  text  unicode
  @param* delim  unicode
  @param* tone  bool
  @param* capital  bool
  @return  unicode
  """
  return converter().convert(text, delim, tone, capital)

# EOF
