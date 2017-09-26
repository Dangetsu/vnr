# coding: utf8
# getjmdict.py
# Get the JMDict for different languages
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

# http://ftp.monash.edu.au/pub/nihongo/UPDATES
# ftp://ftp.monash.edu.au/pub/nihongo/

URL = 'http://ftp.monash.edu.au/pub/nihongo/' # use http over ftp since requests do not support ftp

# Note These files are automatically decompressed when accessed using requests
MIN_FILESIZE = 2000000
DICS = {
  'fr': {'file':'edict_fr.fpw.tar.gz', 'size':9144320}, # 2010, out dated
  'ru': {'file':'jr-edict.fpw.tar.gz', 'size':3614720}, # 2010, out dated
  'nl': {'file':'edict_nl.fpw.tar.gz', 'size':22323200}, # 2014, still update
}

FILENAME_TPL = 'jmdict.%s.tar'

import initdefs
DIC_DIR = initdefs.CACHE_JMDICT_RELPATH
TMP_DIR = initdefs.TMP_RELPATH

# Tasks

def init(): # raise
  for it in TMP_DIR,: # DIC_DIR,
    if not os.path.exists(it):
      os.makedirs(it)

def extract(lang): # str -> bool
  dprint("enter: lang = %s" % lang)

  srcpath = TMP_DIR + '/' + FILENAME_TPL % lang
  tmppath = TMP_DIR + '/JMDict-' + lang
  targetpath = DIC_DIR + '/%s.fpw' % lang

  import shutil
  from sakurakit import skfileio
  with SkProfiler("extract"):
    ok = skfileio.extracttar(srcpath, tmppath)
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

def get(lang): # str -> bool
  dprint("enter: lang = %s" % lang)
  url = URL + DICS[lang]['file']
  path = TMP_DIR + '/' + FILENAME_TPL % lang

  dprint("enter: url = %s" % url)

  #from sakurakit import skfileio
  #if os.path.exists(path) and skfileio.filesize(path) == size:
  #  dprint("leave: already downloaded")
  #  return True

  ok = False
  from sakurakit import skfileio, sknetio
  with SkProfiler("fetch"):
    if sknetio.getfile(url, path, flush=False): # flush=false to use more memory to reduce disk access
      ok = skfileio.filesize(path) > MIN_FILESIZE
  if not ok and os.path.exists(path):
    skfileio.removefile(path)
  dprint("leave: ok = %s" % ok)
  return ok

def lock(lang): # str -> bool
  name = "jmdict.%s.lock" % lang
  import initrc
  if initrc.lock(name):
    return True
  else:
    dwarn("multiple instances")
    return False

def run(lang): # str -> bool
  if lang not in DICS:
    dwarn("unknown lang: %s" % lang)
    return False
  return lock(lang) and get(lang) and extract(lang)

# Main process

def usage():
  print 'usage:', '|'.join(sorted(DICS.iterkeys()))

def msg(lang): # str ->
  dic = DICS[lang]
  import messages
  messages.info(
    name="JMDict (%s)" % lang,
    location="Caches/Dictionaries/JMDict/%s.fpw" % lang,
    size=dic['size'],
    urls=["http://ftp.monash.edu.au/pub/nihongo/" + dic['file']],
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
    lang, = argv
    try:
      msg(lang)
      init()
      ok = run(lang)
      if ok:
        from sakurakit import skos
        skos.open_location(os.path.abspath(DIC_DIR))
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
