# coding: utf8
# opencc/__init__.py
# 10/18/2014 jichi

import os
from sakurakit.skdebug import dwarn

OPENCC_DIC_PATHS = { # {(int fr,int to):str}
  's2t': "STCharacters.txt",
  't2s': "TSCharacters.txt",
  't2tw': "TWVariants.txt",
  't2hk': "HKVariants.txt",
  't2ja': "JPVariants.txt",
  't2ko': "../hanja/dic0.txt",
}

OPENCC_LANG_DELIM = '2'

def setdicpaths(paths): # {str key:unicode path}
  for k in OPENCC_DIC_PATHS:
    OPENCC_DIC_PATHS[k] = paths[k]

_CONVERTERS = {}
def getconverter(fr, to):
  """
  @param  fr  str
  @param  to  str
  @return  SimpleChineseConverter
  """
  key = OPENCC_LANG_DELIM.join((fr, to))
  ret = _CONVERTERS.get(key)
  if not ret:
    ret = _CONVERTERS[key] = makeconverter(fr, to)
  return ret

def makeconverter(fr, to):
  """
  @param  fr  str
  @param  to  str
  @return  SimpleChineseConverter or None
  """
  from pycc import SimpleChineseConverter
  ret = SimpleChineseConverter()
  reverse = False
  key = OPENCC_LANG_DELIM.join((fr, to))
  path = OPENCC_DIC_PATHS.get(key)
  if not path:
    key = OPENCC_LANG_DELIM.join((to, fr))
    path = OPENCC_DIC_PATHS.get(key)
    reverse = True
  if path:
    #print path, reverse
    if os.path.exists(path):
      #from sakurakit.skprof import SkProfiler
      #with SkProfiler(): # 10/19/2014: 0.006 seconds for zhs2zht
      ret.addFile(path, reverse)
      return ret
    else:
      from sakurakit.skdebug import derror
      derror("dic path does not exist:", path)

# Conversion

def convert(text, fr, to):
  """
  @param  text  unicode
  @param  fr  str
  @param  to  str
  @return  unicode
  """
  if text:
    try: return getconverter(fr, to).convert(text)
    except Exception, e: dwarn(e)
  return text

def zht2zhs(text): return convert(text, 't', 's')
def zht2tw(text): return convert(text, 't', 'tw')
def zht2hk(text): return convert(text, 't', 'hk')
def zht2ja(text): return convert(text, 't', 'ja')
def zht2ko(text): return convert(text, 't', 'ko')

def zhs2zht(text): return convert(text, 's', 't')
def tw2zht(text): return convert(text, 'tw', 't')
def hk2zht(text): return convert(text, 'hk', 't')
def ja2zht(text): return convert(text, 'ja', 't')
def ko2zht(text): return convert(text, 'ko', 't')

# Following are for convenient usage

def zhs2tw(text): return zht2hw(zhs2zht(text))
def zhs2hk(text): return zht2hk(zhs2zht(text))
def zhs2ja(text): return zht2ja(zhs2zht(text))
def zhs2ko(text): return zht2ko(zhs2zht(text))

def ja2zhs(text): return zht2zhs(ja2zht(text))
def ko2zhs(text): return zht2zhs(ko2zht(text))

ja2ko = zht2ko
ko2ja = ko2zht

def contains(text, fr, to='t'):
  """
  @param  text  unicode
  @param  fr  str
  @param  to  str  dummy
  @return  bool
  """
  if text:
    try: return getconverter(fr, to).needsConvert(text)
    except Exception, e: dwarn(e)
  return False

def containszhs(text): return contains(text, 's')
def containszht(text): return contains(text, 't', 's')
def containsja(text): return contains(text, 'ja')
def containsko(text): return contains(text, 'ko')

# Aliases

zh2zht = zhs2zht
zh2zhs = zht2zhs
zh2tw = zhs2tw
zh2hk = zhs2hk
zh2ja = zhs2ja
zh2ko = zhs2ko

# EOF
