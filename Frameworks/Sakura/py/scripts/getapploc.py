# coding: utf8
# getlingoes.py
# Get the latest lingoes dictionaries
# 2/9/2014 jichi

if __name__ == '__main__':
  import initrc
  initrc.chcwd()
  initrc.initenv()

  import os
  title = os.path.basename(__file__)
  initrc.settitle(title)

import os
from sakurakit.skdebug import dprint, dwarn
from sakurakit.skprof import SkProfiler

import initdefs
INST_DIR = initdefs.INST_RELPATH + '/AppLocale'
TMP_DIR = initdefs.TMP_RELPATH

# http://ntu.csie.org/~piaip
APPLOC_URL = 'http://ntu.csie.org/~piaip/papploc.msi'
APPLOC_FILENAME = 'papploc.msi'
APPLOC_FILESIZE = 1392640 # file size

# Tasks

def init(): # raise
  for it in TMP_DIR, INST_DIR:
    if not os.path.exists(it):
      os.makedirs(it)

def get(): # -> bool

  targetpath = INST_DIR + '/' + APPLOC_FILENAME
  tmppath = TMP_DIR + '/' + APPLOC_FILENAME
  url = APPLOC_URL
  size = APPLOC_FILESIZE

  dprint("enter: size = %s, url = %s" % (size, url))

  from sakurakit import skfileio
  if os.path.exists(targetpath) and skfileio.filesize(targetpath) == size:
    dprint("leave: already downloaded")
    return True

  from sakurakit import sknetio
  ok = False
  with SkProfiler("fetch"):
    if sknetio.getfile(url, tmppath, flush=False): # flush=false to use more memory to reduce disk access
      ok = skfileio.filesize(tmppath) == size
      if ok:
        os.rename(tmppath, targetpath)
  if not ok and os.path.exists(tmppath):
    skfileio.removefile(tmppath)
  dprint("leave: ok = %s" % ok)
  return ok

def run(): # -> bool
  dprint("enter")
  path = INST_DIR + '/' + APPLOC_FILENAME
  ok = False
  if os.path.exists(path):
    try:
      path = os.path.abspath(path)
      from sakurakit import skwin
      ok = skwin.install_msi(path, admin=True)
    except Exception, e:
      dwarn(e)
  dprint("leave: ok = %s" % ok)
  return ok

## Main ##

def msg():
  import messages
  messages.info(
    name="pAppLocale",
    location="Caches/Installers/AppLocale",
    size=APPLOC_FILESIZE,
    urls=[APPLOC_URL],
  )

def main(argv):
  """
  @param  argv  [unicode]
  @return  int
  """
  dprint("enter")
  ok = False
  try:
    init()
    ok = get() and run()
    if ok:
      from sakurakit import skos
      skos.open_location(os.path.abspath(INST_DIR))
  except Exception, e:
    dwarn(e)
  ret = 0 if ok else 1
  dprint("leave: ret = %s" % ret)
  return ret

if __name__ == '__main__':
  import sys
  if not initrc.lock('apploc.lock'):
    dwarn("multiple instances")
    sys.exit(1)

  msg()
  ret = main(sys.argv[1:])
  sys.exit(ret)

# EOF
