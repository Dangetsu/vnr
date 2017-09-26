# coding: utf8
# lingoesdb.py
# 1/16/2013 jichi

__all__ = 'LingoesDb',

if __name__ == '__main__':
  import sys
  sys.path.append("..")
#from sakurakit.skprof import SkProfiler

# For better performance
#try: from pysqlite2 import dbapi2 as sqlite3
#except ImportError: import sqlite3
import sqlite3

from sakurakit.skdebug import dprint, dwarn
from dictdb import dictdb

class LingoesDb(object):
  XML_DELIM = '<br class="xml"/>'

  def __init__(self, dbpath=''): # unicode
    super(LingoesDb, self).__init__()
    self.dbpath = dbpath

  def create(self, ldpath, inenc='', outenc=''): # unicode, str, str -> bool
    import lingoesparse
    try:
      with sqlite3.connect(self.dbpath) as conn:
        dictdb.createtables(conn.cursor())
        conn.commit()

        cur = conn.cursor()
        l = lingoesparse.parsefile(ldpath, inenc=inenc, outenc=outenc or inenc,
            callback=lambda word, xmls: dictdb.insertentry(cur, (
              word,
              self.XML_DELIM.join(xmls),
            )))
        ok = l != None
        conn.commit()
        return ok
    except Exception, e:
      dwarn(e)
    return False

  def _get(self, t):
    """
    @param  t  unicode
    @return  (unicode word, unicode xml) or None
    """
    try:
      with sqlite3.connect(self.dbpath) as conn:
        cur = conn.cursor()
        return dictdb.queryentry(cur, limit=1, word=t,
            select=dictdb.SELECT_WORD_CONTENT)
    except Exception, e:
      dwarn(e)

  def _search(self, t, exact=False, limit=0):
    """
    @param  t  unicode
    @param* exact  bool
    @param* limit  int
    @return  iter(unicode word, unicode xml) or None
    """
    #if self.trie:
    #  return self.trie.iteritems(t)
    #if os.path.exists(self.dbpath):
    try:
      with sqlite3.connect(self.dbpath) as conn:
        cur = conn.cursor()
        if exact:
          kwargs = {'word':t}
        else:
          kwargs = {'wordlike':t+'%'}
        return dictdb.queryentries(cur, limit=limit, select=dictdb.SELECT_WORD_CONTENT, **kwargs)
    except Exception, e:
      dwarn(e)


  _COMPLETE_TRIM_CHARS = u'ぁ', u'ぇ', u'ぃ', u'ぉ', u'ぅ', u'っ', u'ッ'
  def _complete(self, t):
    """Trim half katagana/hiragana.
    @param  t  unicode
    @return  unicode
    """
    if t:
      while len(t) > 1:
        if t[-1] in self._COMPLETE_TRIM_CHARS:
          t = t[:-1]
        else:
          break
      while len(t) > 1:
        if t[0] in self._COMPLETE_TRIM_CHARS:
          t = t[1:]
        else:
          break
    return t

  def search(self, t, limit=0, exact=False, complete=False):
    """Lookup dictionary prefix while eliminate duplicate definitions
    @param  t  unicode
    @param* exact  bool  whether do exact match
    @param* complete  bool  whether complete the word
    @param* limit  int
    @yield  (unicode word, unicode xml)
    """
    lastxml = None
    count = 0
    q = self._search(t, exact=exact, limit=limit)
    if q:
      for key, xml in q:
        if lastxml != xml:
          yield key, xml
          lastxml = xml
          count += 1
      # Only complete when failed to match any thing
      # For example, 「って」 should not search 「て」
    if complete and not count:
      s = self._complete(t)
      if s and s != t:
        for it in self.search(s, exact=exact, limit=limit):
          yield it

  lookup = search # for backward compatibility

  def get(self, t, complete=False):
    """Lookup dictionary for exact match
    @param  t  unicode
    @param* complete  bool  whether complete the word
    @return  unicode  XML
    """
    q = self._get(t)
    if q:
      return q[1]
    if complete:
      s = self._complete(t)
      if s and s != t:
        return self.get(s)

if __name__ == '__main__':
  import os
  from sakurakit.skprof import SkProfiler
  location = '/Users/jichi/Dropbox/Developer/Dictionaries/LD2/'
  #dic = 'Naver Japanese-Korean Dictionary.ld2'
  #dic = 'OVDP Japanese-Vietnamese Dictionary.ld2'
  #dic = 'Vicon Japanese-English Dictionary.ld2'
  if os.name == 'nt':
    location = 'C:' + location

  dbpath = 'test.db'
  #if os.path.exists(dbpath):
  #  os.remove(dbpath)

  print '-' * 4

  #dic = location + 'New Japanese-Chinese Dictionary.ld2'

  #HOME = os.path.expanduser('~')
  #if os.name == 'nt':
  #  from sakurakit import skpaths
  #  APPDATA = skpaths.APPDATA
  #else: # mac
  #  import getpass
  #  HOME = os.path.expanduser('~')
  #  USER = getpass.getuser() # http://stackoverflow.com/questions/842059/is-there-a-portable-way-to-get-the-current-username-in-python
  #  APPDATA = os.path.join(os., '.wine/drive_c/users/' + USER + '/Application Data')
  PWD = os.getcwd()
  dbpath = os.path.join(PWD, '../../../../../../Caches/Dictionaries/Lingoes')
  #dbpath = os.path.join(dbpath, 'ja-zh.db')
  dbpath = os.path.join(dbpath, 'ja-zh-gbk.db')
  #dbpath += 'ja-ko.db'
  #dbpath += 'ja-vi.db'

  ld = LingoesDb(dbpath)

  #if os.path.exists(dbpath):
  #  os.remove(dbpath)

  if not os.path.exists(dbpath):
    with SkProfiler():
      print ld.create(dic, 'utf16')

  print '-' * 4

  #t = u"風"
  #t = u'万歳'
  t = u'布団'
  #t = u"かわいい"
  #t = u"かわいいっ"
  #t = u"ちょっと"
  #t = u"だしゃれ"
  with SkProfiler():
    print "lookup start"
    it = ld.lookup(t, limit=6)
    if it:
      for key, xml in it:
        print key
        print xml
        #print xmls[0]
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
