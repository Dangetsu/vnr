# coding: utf8
# mdedict.py
# 11/9/2013 jichi

from sakurakit.skdebug import dwarn
from unitraits import jpchars
import mdcompile

csv2dic = mdcompile.compile

def surfacefilter(text):
  """Skip short kana phrases
  @param  text  unicode  surface
  @return  bool
  """
  return len(text) > 2 or jpchars.anykanji(text)

def db2csv(csvpath, dbpath):
  """
  @param  csvpath  unicode output
  @param  dbpath  unicode dbpath
  @return  bool
  """
  import sqlite3
  from dictdb import dictdb
  from dictp import edictp
  try:
    with sqlite3.connect(dbpath) as conn:
      cur = conn.cursor()
      q = dictdb.iterentries(cur)
      with open(csvpath, 'w') as f:
        for i,(word,content) in enumerate(q):
          id = i + 1
          entries = edictp.parseword(word)
          roles = edictp.parsetransrole(content).split(',')
          trans = edictp.parsetransdef(content).replace(',', ' ') # ',' not allowed
          lines = mdcompile.assemble(entries, roles=roles, id=id, type='edict', trans=trans, surfacefilter=surfacefilter)
          f.writelines(lines)
        return True
  except Exception, e:
    dwarn(e)
    return False

# EOF
