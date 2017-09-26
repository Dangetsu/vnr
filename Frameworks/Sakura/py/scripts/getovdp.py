# coding: utf8
# getovdp.py
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

HP_URL = "http://sourceforge.net/projects/ovdp/files/Stardict/Japanese/"
DL_URL = "http://tcpdiag.dl.sourceforge.net/project/ovdp/Stardict/Japanese/"

DICS = {
  'ja-vi': {'file':'NhatViet.zip', 'size':12392678, 'path':'OVDP/NhatViet'},
  'vi-ja': {'file':'VietNhat.zip', 'size':852519, 'path':'OVDP/VietNhat'},
}

LANGS = frozenset(DICS.iterkeys())

import initdefs
DIC_DIR = initdefs.CACHE_DIC_RELPATH
TMP_DIR = initdefs.TMP_RELPATH

# Tasks

def init(): # raise
  for it in TMP_DIR,: # DIC_DIR,
    if not os.path.exists(it):
      os.makedirs(it)

def extract(lang): # str -> bool
  dprint("enter: lang = %s" % lang)

  srcpath = TMP_DIR + '/' + DICS[lang]['file']
  tmppath = TMP_DIR + '/ovdp-' + lang
  targetpath = DIC_DIR + '/' + DICS[lang]['path']

  import shutil
  from sakurakit import skfileio
  with SkProfiler("extract"):
    ok = skfileio.extractzip(srcpath, tmppath)
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
  url = DL_URL + DICS[lang]['file']
  path = TMP_DIR + '/' + DICS[lang]['file']

  dprint("enter: lang = %s, url = %s" % (lang, url))

  #from sakurakit import skfileio
  #if os.path.exists(path) and skfileio.filesize(path) == size:
  #  dprint("leave: already downloaded")
  #  return True

  ok = False
  from sakurakit import skfileio, sknetio
  with SkProfiler("fetch"):
    if sknetio.getfile(url, path, flush=False): # flush=false to use more memory to reduce disk access
      ok = skfileio.filesize(path) == DICS[lang]['size']
  if not ok and os.path.exists(path):
    skfileio.removefile(path)
  dprint("leave: ok = %s" % ok)
  return ok

def lock(lang): # str
  name = "stardict.%s.lock" % lang
  import initrc
  if initrc.lock(name):
    return True
  else:
    dwarn("multiple instances")
    return False

def run(lang): # str -> bool
  if lang not in LANGS:
    dwarn("unknown lang: %s" % lang)
    return False
  return lock(lang) and get(lang) and extract(lang)

# Main process

def usage():
  print 'usage:', '|'.join(LANGS)

def msg(lang): # str ->
  dic = DICS[lang]
  import messages
  messages.info(
    name="OVDP (%s)" % lang,
    location="Caches/Dictionaries/" + dic['path'],
    size=dic['size'],
    urls=[HP_URL],
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
        path = os.path.join(DIC_DIR, DICS[lang]['path'])
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
