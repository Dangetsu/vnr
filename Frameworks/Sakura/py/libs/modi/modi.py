# coding: utf8
# modi.py
# 8/13/2013 jichi

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import os

# This file must be consistent with modiocr.h
# enum modiocr_lang : unsigned long
#modiocr_lang_null = 0 # failed

LANG_JA = 1 << 0 # miLANG_JAPANESE = 17,

LANG_ZHS = 1 << 1 # miLANG_CHINESE_SIMPLIFIED = 2052
LANG_ZHT = 1 << 2 # miLANG_CHINESE_TRADITIONAL = 1028

LANG_KO = 1 << 3  # miLANG_KOREAN = 18,

LANG_CS = 1 << 4  # miLANG_CZECH = 5,
LANG_DA = 1 << 5  # miLANG_DANISH = 6,
LANG_NL = 1 << 6  # miLANG_DUTCH = 19,
LANG_FI = 1 << 7  # miLANG_FINNISH = 11,
LANG_FR = 1 << 8  # miLANG_FRENCH = 12,
LANG_DE = 1 << 9  # miLANG_GERMAN = 7,
LANG_EL = 1 << 10 # miLANG_GREEK = 8,
LANG_HU = 1 << 11 # miLANG_HUNGARIAN = 14,
LANG_IT = 1 << 12 # miLANG_ITALIAN = 16,
LANG_NO = 1 << 13 # miLANG_NORWEGIAN = 20,
LANG_PL = 1 << 14 # miLANG_POLISH = 21,
LANG_PT = 1 << 15 # miLANG_PORTUGUESE = 22,
LANG_RU = 1 << 16 # miLANG_RUSSIAN = 25,
LANG_ES = 1 << 17 # miLANG_SPANISH = 10,
LANG_SV = 1 << 18 # miLANG_SWEDISH = 29,
LANG_TR = 1 << 19 # miLANG_TURKISH = 31,

LANG_EN = 1 << 20 # miLANG_ENGLISH = 9,

LANG_DEFAULT = 1 << 21 # miLANG_SYSDEFAULT = 2048

LOCALE_LANG = {
 'ja': LANG_JA,
 'zh': LANG_ZHS, # use zhs as GBK covers both ja and zht
 'zhs': LANG_ZHS, 'zh-CN': LANG_ZHS,
 'zht': LANG_ZHT, 'zh-TW': LANG_ZHT,
 'ko': LANG_KO,
 'cs': LANG_CS,
 'da': LANG_DA,
 'nl': LANG_NL,
 'fi': LANG_FI,
 'fr': LANG_FR,
 'de': LANG_DE,
 'el': LANG_EL,
 'hu': LANG_HU,
 'it': LANG_IT,
 'no': LANG_NO,
 'pl': LANG_PL,
 'pt': LANG_PT,
 'ru': LANG_RU,
 'es': LANG_ES,
 'sv': LANG_SV,
 'tr': LANG_TR,
 'en': LANG_EN,
}

def locale2lang(v): # str -> int
  return LOCALE_LANG.get(v) or 0

def locales2lang(v): # [str] -> int
  ret = 0
  for it in v:
    ret |= LOCALE_LANG.get(it) or 0
  return ret

from sakurakit import skpaths
MODI_PATH = os.path.join(skpaths.COMMONPROGRAMFILESx86, r'Microsoft Shared\MODI')
#MODI_PATH = os.path.join(skpaths.COMMONPROGRAMFILESx86, r'Microsoft Shared\MODI\11.0')
#MODI_PATH = os.path.join(skpaths.COMMONPROGRAMFILESx86, r'Microsoft Shared\MODI\12.0')
#MODI_DLLS = [os.path.join(MODI_PATH, dll) for dll in (
#  'MDIVWCTL.DLL',
#  'MSPCORE.DLL',
#)]

from sakurakit import skos
if skos.WIN:
  from  pymodi import ModiReader
  available = ModiReader.isValid # -> bool
  readtext = ModiReader.readText # (unicode path, int lang) -> unicode
  readtexts = ModiReader.readTextList # (unicode path, int lang) -> [unicode]

else:
  def available(): return False
  def readtext(): return ''
  def readtexts(): return []

if __name__ == '__main__':
  import os, sys
  os.environ['PATH'] += os.path.pathsep + "../../../bin"
  sys.path.append("../../../bin")
  sys.path.append("..")

  import pythoncom

  if not available():
    print "not available"
  else:
    path = "./wiki.tiff"
    print readtext(path, LANG_JA)

# EOF
