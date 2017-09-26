# coding: utf8
# lingoesdict.py
# 1/15/2013 jichi
#
# LD2 and LDX
# http://code.google.com/p/lingoes-extractor/source/browse/trunk/src/cn/kk/extractor/lingoes/LingoesLd2Extractor.java
# https://code.google.com/p/dict4cn/source/browse/trunk/importer/src/LingoesLd2Reader.java
# http://devchina.wordpress.com/2012/03/01/lingoes%E7%81%B5%E6%A0%BC%E6%96%AF%E7%94%B5%E5%AD%90%E8%AF%8D%E5%85%B8ld2ldf%E6%96%87%E4%BB%B6%E8%A7%A3%E6%9E%90java/
# http://www.cnblogs.com/SuperBrothers/archive/2012/11/24/2785971.html
#
# StarDict
# https://code.google.com/p/dict4cn/source/browse/trunk/importer/src/LingoesLd2Reader.java
#
# LD2
# - 0:3: string '?LD2'
# - 0x18: short version (2)
# - 0x1c: long id
#
# - 0x5c: int offset - 0x60

__all__ = 'LingoesDict',

if __name__ == '__main__':
  import sys
  sys.path.append("..")

import zlib
#from pytrie import StringTrie as Trie
#from pytrie import SortedStringTrie as Trie
from sakurakit.skdebug import dprint, dwarn
import lingoesparse, searchutil

class LingoesDict(object):
  def __init__(self, path='', inenc='', outenc=''): # unicodej
    super(LingoesDict, self).__init__()
    #self.trie = None # PyTrie prefix tree
    self.data = [] # [(unicode from, [unicode to]] lingoes dictionary data
    self.inenc = inenc
    self.outenc = outenc or inenc

    if path:
      self.initWithPath(path)
      #assert self.valid # this should never fail

  def initWithPath(self, path): # unicode
    try:
      with open(path, 'rb') as f:
        self.initWithData(f.read())
    except Exception, e:
      dwarn(e)

  def initWithData(self, data): # str
    dprint("enter")
    self.data = lingoesparse.parse(data, inenc=self.inenc, outenc=self.outenc)
    #if d:
    #  dprint("construct trie")
    #  if 'self' in d:
    #    del d['self']
    #  self.trie = Trie(**d)
    dprint("leave")

  def search(self, t): # unicode -> yield or return None
    #if self.trie:
    #  return self.trie.iteritems(t)
    if t:
      return searchutil.lookupprefix(t, self.data)

  lookup = search # for backward compatibility

  def get(self, t): # unicode key -> unicode content  exact match
    # [1] to get xmls, [0] to get the first xml
    try: return searchutil.lookup(t, self.data)[1][0]
    except: pass

if __name__ == '__main__':
  import os
  from sakurakit.skprof import SkProfiler
  location = '/Users/jichi/Dropbox/Developer/Dictionaries/LD2/'
  if os.name == 'nt':
    location = 'C:' + location

  dic = 'GBK Japanese-Chinese Dictionary.ld2'
  with SkProfiler():
    ld = LingoesDict(location + dic, 'utf8')
  print '-' * 4

  #dic = 'Monash Romanized Japanese-English Dictionary.ld2'
  #with SkProfiler():
  #  ld = LingoesDict(location + dic, 'utf8')
  #print '-' * 4

  #dic = 'New Japanese-Chinese Dictionary.ld2'
  #with SkProfiler():
  #  ld = LingoesDict(location + dic, 'utf16')
  #print '-' * 4

  #dic = 'Naver Japanese-Korean Dictionary.ld2'
  #ld = LingoesDict(location + dic, 'utf8')
  #print '-' * 4

  #dic = 'OVDP Japanese-Vietnamese Dictionary.ld2'
  #ld = LingoesDict(location + dic, 'utf16', 'utf8')
  #print '-' * 4

  #dic = 'Vicon Japanese-English Dictionary.ld2'
  #ld = LingoesDict(location + dic, 'utf16', 'utf8')
  #print '-' * 4

  #t = u"セリフ"
  #t = u'新しい'
  #t = u'記事'
  #t = u'統領'
  #t = u"名前"
  #t = u"セリフ"
  #t = u"名前"
  #t = u"神風"
  #t = u"かわいい"
  #t = u'イギリス'
  #t = u'布団'
  t = u'万歳'
  with SkProfiler():
    print "lookup start"
    it = ld.lookup(t)
    if it:
      for key, xmls in it:
        print key
        print len(xmls)
        print xmls[0]
    print "lookup finish"

  with SkProfiler():
    print "get start"
    print ld.get(t)
    print "get finish"

  # 175 MB
  # 57 MB
  #import time
  #time.sleep(10)

# EOF
