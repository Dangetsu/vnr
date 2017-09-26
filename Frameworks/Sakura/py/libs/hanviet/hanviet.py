# coding: utf8
# hanviet.py
# 12/22/2014: jichi
#
# See: ChinesePhienAmWords.txt in QuickTranslator_TAO
# http://www.tangthuvien.vn/forum/showthread.php?t=30151
# http://www.mediafire.com/download/ijkm32ozmti/QuickTranslator_TAO.zip

from sakurakit.skclass import memoized

HANVIET_DIC_PATHS = {
  'word': 'ChinesePhienAmWords.txt',
  'phrase': 'VietPhrase.txt',
}

def setdicpaths(paths): # {str key:unicode path}
  for k in HANVIET_DIC_PATHS:
    HANVIET_DIC_PATHS[k] = paths[k]

@memoized
def hvt():
  import os
  from pyhanviet import HanVietTranslator
  ret = HanVietTranslator()
  ret.addWordFile(HANVIET_DIC_PATHS['word'])
  ret.addPhraseFile(HANVIET_DIC_PATHS['phrase'])
  return ret

def lookupword(text):
  """
  @param  text  unicode
  @return  unicode or None
  """
  if text and len(text) == 1:
    i = ord(text[0])
    if i <= 0xffff:
      return hvt().lookupWord(i)

def lookupphrase(text):
  """
  @param  text  unicode
  @return  unicode or None
  """
  return hvt().lookupPhrase(text)

def toreading(text):
  """
  @param  text  unicode
  @return  unicode
  """
  return hvt().toReading(text)

def translate(text, mark=False, align=None):
  """
  @param  text  unicode
  @param* delim  unicode
  @param* align  list or None
  @return  unicode
  """
  if align is not None:
    ret, l = hvt().analyze(text, mark)
    align.extend(l)
    return ret
  else:
    return hvt().translate(text, mark)

# EOF
