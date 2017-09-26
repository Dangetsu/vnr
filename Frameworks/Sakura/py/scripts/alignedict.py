# coding: utf8
# alignedict.py
# Compile EDICT into MeCab dictionary.
# 2/9/2014 jichi

if __name__ == '__main__':
  import initrc
  initrc.chcwd()
  initrc.initenv()

  import os
  title = os.path.basename(__file__)
  initrc.settitle(title)

import os
from sakurakit import skos
from sakurakit.skdebug import dprint, dwarn
from sakurakit.skprof import SkProfiler

import initdefs
TARGET_DIR = initdefs.CACHE_EDICT_RELPATH
DB_FILENAME = 'edict.db'
DIC_FILENAME = 'edict.dic'
CSV_FILENAME = 'edict.csv'

UNIDIC_DICPATH = initdefs.CACHE_UNIDIC_RELPATH
MECAB_BINPATH = initdefs.MECAB_RELPATH + '/bin'

if skos.WIN:
  MECAB_EXEPATH = MECAB_BINPATH + '/mecab-dict-index.exe'
else:
  MECAB_EXEPATH = 'mecab-dict-index'

# Tasks

def init(): pass # not defined
#  for it in TARGET_DIR, TMP_DIR:
#    if not os.path.exists(it):
#      os.makedirs(it)

def compile(): # -> bool
  dprint("enter")
  dbpath = TARGET_DIR + '/' + DB_FILENAME
  dicpath = TARGET_DIR + '/' + DIC_FILENAME
  csvpath = TARGET_DIR + '/' + CSV_FILENAME
  tmpdicpath = dicpath + '.tmp'

  from mecabdic import mdedict
  with SkProfiler("assemble csv"):
    ok = mdedict.db2csv(csvpath, dbpath)
  if ok:
    with SkProfiler("compile dic"):
      ok = mdedict.csv2dic(tmpdicpath, csvpath,
          exe=MECAB_EXEPATH,
          dicdir=UNIDIC_DICPATH)
  from sakurakit import skfileio
  if ok:
    if os.path.exists(dicpath):
      skfileio.remove(dicpath)
    os.rename(tmpdicpath, dicpath)
  elif os.path.exists(tmpdicpath):
    skfileio.removefile(tmpdicpath)
  if os.path.exists(csvpath):
    skfileio.removefile(csvpath)
  dprint("leave: ok = %s" % ok)
  return ok

# Main process

def main():
  """
  @return  int
  """
  dprint("enter")
  ok = False
  try:
    init()
    ok = compile()
    if ok:
      from sakurakit import skos
      skos.open_location(os.path.abspath(TARGET_DIR))
  except Exception, e:
    dwarn(e)
  ret = 0 if ok else 1
  dprint("leave: ret = %s" % ret)
  return ret

if __name__ == '__main__':
  import sys
  if not initrc.lock('mecab-edict.lock'):
    dwarn("multiple instances")
    sys.exit(1)
  ret = main()
  sys.exit(ret)


# EOF
