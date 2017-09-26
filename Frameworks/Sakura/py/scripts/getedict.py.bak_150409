# coding: utf8
# getedict.py
# 11/3/2013 jichi

if __name__ == '__main__':
  import initrc
  initrc.chcwd()
  initrc.initenv()

import os
from sakurakit.skdebug import dprint, dwarn
from sakurakit.skprof import SkProfiler

import initdefs
TARGET_DIR = initdefs.CACHE_EDICT_RELPATH
TMP_DIR = initdefs.TMP_RELPATH
FILENAME = 'edict.db'

MIN_EDICT_SIZE = 20 * 1024 * 1024 # 20MB

def init():
  for it in TMP_DIR,: #TARGET_DIR
    if not os.path.exists(it):
      os.makedirs(it)

def get(): # return bool
  dprint("enter")
  targetpath = TARGET_DIR + '/' + FILENAME
  tmppath = TMP_DIR + '/' + FILENAME

  from sakurakit import skfileio
  for it in targetpath, tmppath:
    if os.path.exists(it):
      skfileio.removefile(it)

  import sys
  #prefix = os.path.abspath(TMP_DIR) # relative path is OK for sqlitedb
  sys.argv.append('--prefix=' + TMP_DIR)
  #sys.argv.append('--targetPath=' + TMP_DIR) # not working
  sys.argv.append('EDICT')

  ok = False

  #from cjklib.dictionary.install import CommandLineInstaller
  from cjklibinstall import CommandLineInstaller
  inst = CommandLineInstaller()
  with SkProfiler():
    if inst.run() and skfileio.filesize(tmppath) > MIN_EDICT_SIZE:
      os.renames(tmppath, targetpath) # renames to create target directory
      ok = True
    elif os.path.exists(tmppath):
      skfileio.removefile(tmppath)
  dprint("leave: ok = %s" % ok)
  return ok

## Main ##

def main():
  """
  @param  argv  [unicode]
  @return  int
  """
  dprint("enter")
  ok = False
  try:
    init()
    ok = get()
    if ok:
      from sakurakit import skos
      skos.open_location(os.path.abspath(TARGET_DIR))
  except Exception, e:
    dwarn(e)
  ret = 0 if ok else 1
  dprint("leave: ret = %s" % ret)
  return ret

#UPDATE_INTERVAL = 86400 * 30 # a month
#def needsupdate():
#  """
#  @return  bool  whether perform update
#  """
#  import os
#  from sakurakit import skdatetime, skfileio
#  HOME = os.path.expanduser('~')
#  APPDATA = os.environ['appdata'] if 'appdata' in os.environ else os.path.join(HOME, r"AppData\Roaming")
#  edict = os.path.join(APPDATA,  'cjklib/edict.db')
#  ts = skfileio.fileupdatetime(edict)
#  now = skdatetime.current_unixtime()
#  ret = now > ts + UPDATE_INTERVAL
#  #dprint("ret = %s" % ret)
#  return ret

UPDATE_INTERVAL = 86400 * 30 # a month
def needsupdate():
  """
  @return  bool  whether perform update
  """
  #HOME = os.path.expanduser('~')
  #APPDATA = os.environ['appdata'] if 'appdata' in os.environ else os.path.join(HOME, r"AppData\Roaming")
  #edict = os.path.join(APPDATA,  'cjklib/edict.db')
  from sakurakit import skdatetime, skfileio
  targetpath = TARGET_DIR + '/' + FILENAME
  ts = skfileio.fileupdatetime(targetpath)
  now = skdatetime.current_unixtime()
  ret = now > ts + UPDATE_INTERVAL
  #dprint("ret = %s" % ret)
  return ret

if __name__ == '__main__':
  import sys
  if not initrc.lock('edict.lock'):
    dwarn("multiple instances")
    sys.exit(1)
  if needsupdate():
    #ret = main(sys.argv[1:])
    ret = main()
    sys.exit(ret)

# EOF
