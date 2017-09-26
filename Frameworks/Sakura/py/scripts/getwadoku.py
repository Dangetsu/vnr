# coding: utf8
# getwadoku.py
# 2/14/2014 jichi

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
TARGET_DIR = initdefs.CACHE_WADOKU_RELPATH
TMP_DIR = initdefs.TMP_RELPATH

# http://www.wadoku.de/wiki/display/WAD/Downloads+und+Links
WADOKU_URL = 'http://www.wadoku.de/downloads/epwing/wadoku_epwing_jan2012.zip'
WADOKU_FILESIZE = 37103191
WADOKU_FILENAME = 'wadoku'
WADOKU_SUFFIX = '.zip'

def init():
  for it in TMP_DIR,:
    if not os.path.exists(it):
      os.makedirs(it)

def get(): # return bool
  url = WADOKU_URL
  path = TMP_DIR + '/' + WADOKU_FILENAME + WADOKU_SUFFIX
  size = WADOKU_FILESIZE

  dprint("enter: size = %s, url = %s" % (size, url))

  from sakurakit import skfileio
  if os.path.exists(path) and skfileio.filesize(path) == size:
    dprint("leave: already downloaded")
    return True

  from sakurakit import sknetio
  ok = False
  with SkProfiler("fetch"):
    if sknetio.getfile(url, path, flush=False): # flush=false to use more memory to reduce disk access
      ok = skfileio.filesize(path) == size
  if not ok and os.path.exists(path):
    skfileio.removefile(path)
  dprint("leave: ok = %s" % ok)
  return ok

def extract():
  dprint("enter")

  srcpath = TMP_DIR + '/' + WADOKU_FILENAME + WADOKU_SUFFIX
  tmppath = TMP_DIR + '/' + WADOKU_FILENAME
  targetpath = TARGET_DIR

  import shutil
  from sakurakit import skfileio
  with SkProfiler("extract"):
    ok = skfileio.extractzip(srcpath, tmppath)
  if ok:
    if os.path.exists(targetpath):
      shutil.rmtree(targetpath)
    os.renames(tmppath, targetpath)
  if os.path.exists(tmppath):
    shutil.rmtree(tmppath)
  skfileio.removefile(srcpath)

  dprint("leave: ok = %s" % ok)
  return ok

## Main ##

def msg():
  import messages
  messages.info(
    name="Wadoku",
    location="Caches/Dictionaries/Wadoku",
    size=WADOKU_FILESIZE,
    urls=[
      'http://www.wadoku.de/wiki/display/WAD/Downloads+und+Links',
      WADOKU_URL,
    ],
  )

def main():
  """
  @param  argv  [unicode]
  @return  int
  """
  dprint("enter")
  ok = False
  try:
    init()
    ok = get() and extract()
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
  if not initrc.lock('wadoku.lock'):
    dwarn("multiple instances")
    sys.exit(1)
  msg()
  ret = main()
  sys.exit(ret)

# EOF
