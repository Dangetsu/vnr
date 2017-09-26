# coding: utf8
# getstardict.py
# Get the StarDict for different languages
# 4/26/2015 jichi

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

# http://ftp.monash.edu.au/pub/nihongo/UPDATES
# ftp://ftp.monash.edu.au/pub/nihongo/

# http://ftp-archive.freebsd.org/pub/FreeBSD-Archive/ports/distfiles/stardict/
# http://abloz.com/huzheng/stardict-dic/ko/
DIC_URL = "http://ftp-archive.freebsd.org/pub/FreeBSD-Archive/ports/distfiles/stardict/"

DICS = {
  'hanja': {'file':'stardict-Hanja_KoreanHanzi_Dic-2.4.2.tar.bz2', 'size':2500031, 'path':'hanja'},
  'hangul': {'file':'stardict-KoreanDic-2.4.2.tar.bz2', 'size':8498547, 'path':'hangul'},
}

DIC_NAMES = frozenset(DICS.iterkeys())

import initdefs
DIC_DIR = initdefs.CACHE_STARDICT_RELPATH
TMP_DIR = initdefs.TMP_RELPATH

# Tasks

def init(): # raise
  for it in TMP_DIR,: # DIC_DIR,
    if not os.path.exists(it):
      os.makedirs(it)

def extract(dic): # str -> bool
  dprint("enter: dic = %s" % dic)

  srcpath = TMP_DIR + '/' + DICS[dic]['file']
  tmppath = TMP_DIR + '/stardic-' + dic
  targetpath = DIC_DIR + '/' + DICS[dic]['path']

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

def get(dic): # str -> bool
  url = DIC_URL + DICS[dic]['file']
  path = TMP_DIR + '/' + DICS[dic]['file']

  dprint("enter: dic = %s, url = %s" % (dic, url))

  #from sakurakit import skfileio
  #if os.path.exists(path) and skfileio.filesize(path) == size:
  #  dprint("leave: already downloaded")
  #  return True

  ok = False
  from sakurakit import skfileio, sknetio
  with SkProfiler("fetch"):
    if sknetio.getfile(url, path, flush=False): # flush=false to use more memory to reduce disk access
      ok = skfileio.filesize(path) == DICS[dic]['size']
  if not ok and os.path.exists(path):
    skfileio.removefile(path)
  dprint("leave: ok = %s" % ok)
  return ok

def lock(dic): # str
  name = "stardict.%s.lock" % dic
  import initrc
  if initrc.lock(name):
    return True
  else:
    dwarn("multiple instances")
    return False

def run(dic): # str -> bool
  if dic not in DIC_NAMES:
    dwarn("unknown dic: %s" % dic)
    return False
  return lock(dic) and get(dic) and extract(dic)

# Main process

def usage():
  print 'usage:', '|'.join(DIC_NAMES)

def msg(dic): # str ->
  d = DICS[dic]
  import messages
  messages.info(
    name="StarDict (%s)" % dic,
    location="Caches/Dictionaries/" + d['path'],
    size=d['size'],
    urls=[DIC_URL],
  )

def main(argv):
  """
  @param  argv  [unicode]
  @return  int
  """
  dprint("enter")
  ok = False
  if not argv or len(argv) == 1 and argv[0] in ('-h', '--help'):
    usage()
  elif len(argv) != 1:
    dwarn("invalid number of parameters")
    usage()
  else:
    dic, = argv
    try:
      msg(dic)
      init()
      ok = run(dic)
      if ok:
        from sakurakit import skos
        path = os.path.join(DIC_DIR, DICS[dic]['path'])
        skos.open_location(os.path.abspath(path))
    except Exception, e:
      dwarn(e)
  ret = 0 if ok else 1
  dprint("leave: ret = %s" % ret)
  return ret

if __name__ == '__main__':
  import sys
  ret = main(sys.argv[1:])
  sys.exit(ret)

# EOF
