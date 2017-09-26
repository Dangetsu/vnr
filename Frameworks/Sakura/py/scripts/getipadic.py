# coding: utf8
# getipadic.py
# 2/24/2014 jichi

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
TARGET_DIR = initdefs.CACHE_IPADIC_RELPATH
TMP_DIR = initdefs.TMP_RELPATH

# https://packages.macports.org/mecab-ipadic-utf8/
# https://packages.macports.org/mecab-ipadic-utf8/mecab-ipadic-utf8-2.7.0-20070801_0.darwin_13.noarch.tbz2
# Version 13 is the latest (2013)
IPADIC_URL = 'https://packages.macports.org/mecab-ipadic-utf8/mecab-ipadic-utf8-2.7.0-20070801_0.darwin_13.noarch.tbz2'
IPADIC_FILESIZE = 12561075
IPADIC_FILENAME = 'ipadic'
IPADIC_SUFFIX = '.tbz2'
IPADIC_RELPATH = '/opt/local/lib/mecab/dic/ipadic-utf8'

def init():
  for it in TMP_DIR,:
    if not os.path.exists(it):
      os.makedirs(it)

def get(): # return bool
  url = IPADIC_URL
  path = TMP_DIR + '/' + IPADIC_FILENAME + IPADIC_SUFFIX
  size = IPADIC_FILESIZE

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

  srcpath = TMP_DIR + '/' + IPADIC_FILENAME + IPADIC_SUFFIX
  tmppath = TMP_DIR + '/' + IPADIC_FILENAME
  targetpath = TARGET_DIR

  import shutil
  from sakurakit import skfileio
  with SkProfiler("extract"):
    ok = skfileio.extracttarbz2(srcpath, tmppath)
  if ok:
    if os.path.exists(targetpath):
      shutil.rmtree(targetpath)
    #child = skfileio.getfirstchilddir(tmppath)
    #child = os.path.join(tmppath, '/opt/local/lib/mecab/dic/ipadic-utf8')
    child = tmppath + IPADIC_RELPATH
    os.renames(child, targetpath)
  if os.path.exists(tmppath):
    shutil.rmtree(tmppath)
  skfileio.removefile(srcpath)

  dprint("leave: ok = %s" % ok)
  return ok

## Main ##

def msg():
  import messages
  messages.info(
    name="IPAdic",
    location="Caches/Dictionaries/IPAdic",
    size=IPADIC_FILESIZE,
    urls=[initdefs.DOWNLOAD_MAINLAND_URL],
  )
  #"https://packages.macports.org/mecab-ipadic-utf8",
  #"https://sourceforge.net/projects/mecab/files/mecab-ipadic",
  #"https://code.google.com/p/mecab/downloads",

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
  if not initrc.lock('ipadic.lock'):
    dwarn("multiple instances")
    sys.exit(1)
  msg()
  ret = main()
  sys.exit(ret)

# EOF
