# coding: utf8
# ccman.py
# 10/19/2014 jichi
from sakurakit.skclass import memoized
from sakurakit.skdebug import dprint
from kanjiconv import jazh
from opencc import opencc

@memoized
def manager(): return ChineseConversionManager()

class _ChineseConversionManager: pass
class ChineseConversionManager:
  def __init__(self):
    d = self.__d = _ChineseConversionManager()
    d.variant = '' # str  Among '', 'ja', 'tw', 'hk'
    d.variantConvert = None # lambda: unicode -> unicode

  def variant(self): return self.__d.variant # -> str
  def setVariant(self, v): # str ->
    d = self.__d
    if d.variant != v:
      dprint(v)
      d.variant = v
      if v == 'tw':
        d.variantConvert = opencc.zht2tw
      elif v == 'hk':
        d.variantConvert = opencc.zht2hk
      elif v == 'ja':
        d.variantConvert = opencc.zht2ja
      elif v == 'ko':
        d.variantConvert = opencc.zht2ko
      else:
        d.variantConvert = None

  def convertTraditionalChinese(self, text):
    """zht2zhx
    @param  text  unicode
    @return  unicode
    """
    if not text:
      return text
    if self.__d.variantConvert:
      text = self.__d.variantConvert(text)
    return text

def zht2zhx(text): # unicode -> unicode
  return manager().convertTraditionalChinese(text)

def zhs2zhx(text): # unicode -> unicode
  return zht2zhx(opencc.zhs2zht(text))

def ja2zhx(text): # unicode -> unicode
  return zht2zhx(opencc.ja2zht(text))

def ja2zhs_name(text): # unicode -> unicode
  return opencc.ja2zhs(jazh.ja2zh_name(text))

def ja2zhx_name(text): # unicode -> unicode
  return jazh.ja2zht_name_fix(ja2zhx(jazh.ja2zh_name(text)))

# EOF
