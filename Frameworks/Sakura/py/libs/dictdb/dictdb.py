# coding: utf8
# dictdb.py
# 1/16/2014
# See: http://zetcode.com/db/sqlitepythontutorial/

if __name__ == '__main__':
  import sys
  sys.path.append("..")

# For better performance
#try: from pysqlite2 import dbapi2 as sqlite3
#except ImportError: import sqlite3
import os, sqlite3
from sakurakit.skdebug import dwarn
import dbutil

#TABLE_NAME = 'entry'

# Queries

SELECT_ID = 'id'
SELECT_WORD = 'word'
SELECT_CONTENT = 'content'
SELECT_WORD_CONTENT = 'word,content'
SELECT_ID_WORD_CONTENT = 'id,word,content'
SELECT_ALL = '*'

def getentry(cur, id, select=SELECT_ALL):
  """
  @param  cursor
  @param* select  str
  @return  (unicode word, unicode content)
  @raise
  """
  sql = "SELECT %s FROM entry where id = ?" % select
  params = id,
  cur.execute(sql, params)
  return cur.fetchone()

def queryentry(cur, word='', wordlike='', limit=1, select=SELECT_ALL):
  """
  @param  cursor
  @param* word  unicode
  @param* wordlike  unicode
  @param* select  str
  @param* limit  int
  @return  (unicode word, unicode content)
  @raise
  """
  params = []
  sql = "SELECT %s FROM entry" % select
  if word:
    sql += ' where word = ?'
    params.append(word)
  elif wordlike:
    sql += ' where word like ?'
    params.append(wordlike)
  if limit:
    sql += ' limit ?'
    params.append(limit)
  cur.execute(sql, params)
  return cur.fetchone()

def queryentries(cur, word='', wordlike='', limit=0, select=SELECT_WORD_CONTENT):
  """
  @param  cursor
  @param* word  unicode
  @param* wordlike  unicode
  @param* select  str
  @param* limit  int
  @return  [unicode word, unicode content]
  @raise
  """
  params = []
  sql = "SELECT %s FROM entry" % select
  if word:
    sql += ' where word = ?'
    params.append(word)
  elif wordlike:
    sql += ' where word like ?'
    params.append(wordlike)
  if limit:
    sql += ' limit ?'
    params.append(limit)
  cur.execute(sql, params)
  return cur.fetchall()

# http://stackoverflow.com/questions/3785294/best-way-to-iterate-through-all-rows-in-a-db-table
def iterentries(cur, select=SELECT_WORD_CONTENT, chunk=100):
  """
  @param  cursor
  @yield  unicode word, unicode content
  @raise
  """
  sql = "SELECT %s FROM entry" % select
  cur.execute(sql)
  return dbutil.fetchsome(cur, chunk)

def iterwords(cur, chunk=100, order=True):
  """
  @param  cursor
  @yield  unicode
  @raise
  """
  sql = "SELECT word FROM entry" # order by id is needed since there is index on word
  if order:
    sql += " order by id"
  cur.execute(sql)
  for it, in dbutil.fetchsome(cur, chunk):
    yield it

# Construction

def insertentry(cur, entry, ignore_errors=False): # cursor, entry; raise
  """
  @param  cursor
  @param  entry  (unicode word, unicode content)
  @param* ignore_errors  whether ignore exceptions
  @raise
  """
  sql = "INSERT INTO entry(word,content) VALUES(?,?)"
  if ignore_errors:
    try: cur.execute(sql, entry)
    except Exception, e: dwarn(e)
  else:
    cur.execute(sql, entry)

def insertentries(cur, entries, ignore_errors=False): # cursor, [entry]; raise
  """
  @param  cursor
  @param  entries  [unicode word, unicode content]
  @param* ignore_errors  whether ignore exceptions
  @raise
  """
  for it in entries:
    insertentry(cur, it, ignore_errors=ignore_errors)

def createtables(cur): # cursor -> bool
  """
  @param  cursor
  @return  bool
  @raise
  """
  cur.execute('''\
CREATE TABLE entry(
id INTEGER PRIMARY KEY AUTOINCREMENT,
word TEXT NOT NULL UNIQUE,
content TEXT NOT NULL)
''').execute('''\
CREATE UNIQUE INDEX idx_word ON entry(word ASC)
''')
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

def makedb(dbpath, entries): # unicode path -> bool
  """
  @param  dbpath  unicode  target db path
  @param  entries  source entries
  @return  bool
  """
  try:
    if os.path.exists(dbpath):
      os.remove(dbpath)
    with sqlite3.connect(dbpath) as conn:
      dictdb.createtables(conn.cursor())
      conn.commit()

      insertentries(conn.cursor(), entries)
      conn.commit()
      return True
  except Exception, e:
    dwarn(e)
  return False

if __name__ == '__main__':
  path = 'test.db'
  if os.path.exists(path):
    os.remove(path)
  print createdb(path)

  with sqlite3.connect(path) as conn:
    cur = conn.cursor()
    insertentry(cur, ('a', 'b'))
    insertentry(cur, ('ab', 'b'))
    conn.commit()

    print queryentry(cur, wordlike='a')

    for it in queryentries(cur, wordlike='%a%'):
      print it

# EOF
