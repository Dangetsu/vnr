# coding: utf8
# getlingoes.py
# Get the latest lingoes dictionaries
# 2/9/2014 jichi

if __name__ == '__main__':
  import initrc
  #initrc.chcwd()
  initrc.initenv()

  import os
  title = os.path.basename(__file__)
  initrc.settitle(title)

import os
from sakurakit.skdebug import dprint, dwarn
from sakurakit.skprof import SkProfiler

LD_SUFFIX = '.ld2'
DB_SUFFIX = '.db'
TMP_SUFFIX = '.tmp'

# Tasks

def ld2db(ldpath, dbpath=None, inenc=None, outenc=None):
  """
  @param  ldpath  unicode
  @param* dbpath  unicode
  @param* inenc  str
  @param* outenc  str
  """
  if not inenc:
    inenc = 'utf8'
  if not outenc:
    outenc = inenc
  dprint("enter: inenc = %s, outenc = %s" % (inenc, outenc))

  if not dbpath or os.path.isdir(dbpath):
    basename = os.path.basename(ldpath)
    if ldpath.endswith(LD_SUFFIX):
      path = os.path.splitext(basename)[0] + DB_SUFFIX
    else:
      path = basename
    if dbpath:
      dbpath = os.path.join(dbpath, path)
    else:
      dbpath = path

  if not os.path.exists(ldpath):
    dwarn("ld file does not exist: %s" % ldpath)
    return False

  if os.path.exists(dbpath):
    dwarn("db file already exist: %s" % dbpath)
    return False

  tmppath = dbpath + TMP_SUFFIX
  from sakurakit import skfileio
  if os.path.exists(tmppath):
    skfileio.removefile(tmppath)

  ok = False
  from lingoes.lingoesdb import LingoesDb
  with SkProfiler():
    if LingoesDb(tmppath).create(ldpath, inenc, outenc):
      os.renames(tmppath, dbpath) # renames to create DB_DIR
      ok = True
    elif os.path.exists(tmppath):
      skfileio.removefile(tmppath)

  dprint("leave: ok = %s" % ok)
  return ok

def usage():
  print '''usage: ld-path [sl-enc] [hl-enc] [db-path]
Convert Lingoes dictionary to SQLite database.
Assume UTF-8 encoding if not specified.'''

def main(argv):
  """
  @param  in-enc out-enc ld-path
  @return  int
  """
  #dprint("enter")
  ok = False
  if not argv or len(argv) == 1 and argv[0] in ('-h', '--help'):
    usage()
  elif len(argv) not in (1,2,3, 4):
    dwarn("invalid number of parameters")
    usage()
  else:
    while len(argv) < 4:
      argv.append(None)
    ldpath, inenc, outenc, dbpath = argv
    try: ok = ld2db(ldpath, dbpath, inenc, outenc)
    except Exception, e: dwarn(e)
  ret = 0 if ok else 1
  #dprint("leave: ret = %s" % ret)
  return ret

if __name__ == '__main__':
  import sys
  ret = main(sys.argv[1:])
  sys.exit(ret)

# EOF
