# coding: utf8
# getunidic.py
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
TARGET_DIR = initdefs.CACHE_UNIDIC_RELPATH
TMP_DIR = initdefs.TMP_RELPATH

# Note: The original unidic is missing def. Need to get the Debian package.
# http://http.us.debian.org/debian/pool/main/u/unidic-mecab/unidic-mecab_2.1.2~dfsg-2_all.deb
#
# http://sakuradite.com/topic/167
#
# http://sourceforge.jp/projects/unidic/
# http://jaist.dl.sourceforge.jp/unidic/58338/unidic-mecab-2.1.2_bin.zip
# ftp://ftp.jaist.ac.jp/pub/sourceforge.jp/unidic/58338/unidic-mecab-2.1.2_bin.zip
#UNIDIC_URL = 'http://jaist.dl.sourceforge.jp/unidic/58338/unidic-mecab-2.1.2_bin.zip'
#UNIDIC_URL = 'http://ftp.jaist.ac.jp/pub/sourceforge.jp/unidic/58338/unidic-mecab-2.1.2_bin.zip'
#UNIDIC_URL = 'http://osdn.dl.sourceforge.jp/unidic/58338/unidic-mecab-2.1.2_bin.zip'
#UNIDIC_URL = 'http://mse.uk.distfiles.macports.org/sites/distfiles.macports.org/mecab/unidic-mecab-2.1.2_bin.zip'
#UNIDIC_URL = 'http://distfiles.macports.org/mecab/unidic-mecab-2.1.2_bin.zip'
#UNIDIC_URL = 'http://sakuradite.org/pub/unidic/unidic-2.1.2.tar.bz2'
UNIDIC_URL = 'http://%s/pub/unidic/unidic-2.1.2.tar.bz2' % initdefs.DOMAIN_ORG
UNIDIC_MIN_FILESIZE = 25000000
UNIDIC_FILENAME = 'unidic'
UNIDIC_SUFFIX = '.tbz2'

def init():
  for it in TMP_DIR,:
    if not os.path.exists(it):
      os.makedirs(it)

def get(): # return bool
  url = UNIDIC_URL
  path = TMP_DIR + '/' + UNIDIC_FILENAME + UNIDIC_SUFFIX
  size = UNIDIC_MIN_FILESIZE

  dprint("enter: size = %s, url = %s" % (size, url))

  from sakurakit import skfileio
  if os.path.exists(path) and skfileio.filesize(path) > size:
    dprint("leave: already downloaded")
    return True

  from sakurakit import sknetio
  ok = False
  with SkProfiler("fetch"):
    if sknetio.getfile(url, path, flush=False): # flush=false to use more memory to reduce disk access
      ok = skfileio.filesize(path) > size
  if not ok and os.path.exists(path):
    skfileio.removefile(path)
  dprint("leave: ok = %s" % ok)
  return ok

def extract():
  dprint("enter")

  srcpath = TMP_DIR + '/' + UNIDIC_FILENAME + UNIDIC_SUFFIX
  tmppath = TMP_DIR + '/' + UNIDIC_FILENAME
  targetpath = TARGET_DIR

  import shutil
  from sakurakit import skfileio
  with SkProfiler("extract"):
    ok = skfileio.extracttarbz2(srcpath, tmppath)
  if ok:
    if os.path.exists(targetpath):
      shutil.rmtree(targetpath)
    child = skfileio.getfirstchilddir(tmppath)
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
    name="UniDic",
    location="Caches/Dictionaries/UniDic",
    size=UNIDIC_MIN_FILESIZE,
    urls=[
      #'http://sourceforge.jp/projects/unidic',
      #'http://jaist.dl.sourceforge.jp/unidic/58338/unidic-mecab-2.1.2_bin.zip',
      #'http://osdn.dl.sourceforge.jp/unidic/58338/unidic-mecab-2.1.2_bin.zip',
      #'http://distfiles.macports.org/mecab/unidic-mecab-2.1.2_bin.zip',
      #'http://mse.uk.distfiles.macports.org/sites/distfiles.macports.org/mecab/unidic-mecab-2.1.2_bin.zip',
      initdefs.DOWNLOAD_MAINLAND_URL,
      'http://sakuradite.org/pub/unidic/unidic-2.1.2.tar.xz',
    ]
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
  if not initrc.lock('unidic.lock'):
    dwarn("multiple instances")
    sys.exit(1)
  msg()
  ret = main()
  sys.exit(ret)

# EOF
