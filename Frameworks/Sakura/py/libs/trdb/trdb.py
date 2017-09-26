# coding: utf8
# trdb.py
# 8/21/2014
# See: http://zetcode.com/db/sqlitepythontutorial/

if __name__ == '__main__':
  import sys
  sys.path.append("..")
import sqlite3
from sakurakit.skdebug import dwarn

#TABLE_NAME = 'entry'

from time import time
def current_timestamp(): return int(time())

from sakurakit import skhash
hashtext = skhash.djb2_64

def queryvalue(cur, key):
  """
  @param  cursor
  @param* key  unicode
  @return  unicode or None
  @raise
  """
  sql = "SELECT value FROM entry where id = %s" % hashtext(key)
  cur.execute(sql)
  row = cur.fetchone()
  if row:
    return row[0]

def insertentry(cur, key, value): # cursor, string, string; raise
  """
  @param  cursor
  @param  key  unicode
  @param* value  unicode
  @raise
  """
  cur.execute("INSERT INTO entry VALUES(?,?,?,?)",
      (hashtext(key), key, value, current_timestamp()))

# The uniqueness of text is not checked
def createtables(cur): # cursor -> bool
  """
  @param  cursor
  @return  bool
  @raise
  """
  cur.execute('''\
CREATE TABLE entry(
id BIGINT PRIMARY KEY,
key TEXT NOT NULL,
value TEXT NOT NULL,
timestamp INTEGER DEFAULT 0)
''')
#.execute('''\
#CREATE UNIQUE INDEX idx_source ON entry(source ASC)
#''')
  return True

def createdb(dbpath): # unicode path -> bool
  """
  @param  dbpath  unicode
  @return  bool
  """
  try:
    with sqlite3.connect(dbpath) as conn:
      createtables(conn.cursor())
      conn.commit()
      return True
  except Exception, e:
    dwarn(e)
  return False

if __name__ == '__main__':
  from sakurakit.skprof import SkProfiler
  import os
  path = 'test.db'
  if os.path.exists(path):
    os.remove(path)
  ok = createdb(path)
  print ok

  with SkProfiler():
    with sqlite3.connect(path) as conn:
      pass

  with sqlite3.connect(path) as conn:
    cur = conn.cursor()
    with SkProfiler():
      insertentry(cur, u'こんにちは', 'hello')
      conn.commit()

    with SkProfiler():
      print queryvalue(cur, u'こんにちは')

    with sqlite3.connect(path) as conn2:
      cur2 = conn2.cursor()
      print queryvalue(cur2, u'こんにちは')

# EOF
