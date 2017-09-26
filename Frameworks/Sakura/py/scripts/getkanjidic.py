# coding: utf8
# getkanjidic.py
# Get the latest EDICT dictionary.
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
TARGET_DIR = initdefs.CACHE_KANJIDIC_RELPATH
TMP_DIR = initdefs.TMP_RELPATH

HP_URL = 'http://www.csse.monash.edu.au/~jwb/kanjidic.html'
MIN_DIC_SIZE = 1 * 1024 * 1024 # 1MB, actually 1.1 MB

DIC_URL = 'http://ftp.monash.edu.au/pub/nihongo/%s.gz'
DICS = {
  'en': 'kanjidic',
  'es': 'kanjidic_es',
  'fr': 'kanjidic_fr',
  'pt': 'kanjidic_pt',
}

import initdefs
TMP_DIR = initdefs.TMP_RELPATH

# Tasks

def init(): # raise
  for it in TARGET_DIR, TMP_DIR:
    if not os.path.exists(it):
      os.makedirs(it)

def get(lang): # str -> bool
  filename = DICS[lang]
  url = DIC_URL % filename
  minsize = MIN_DIC_SIZE
  path = TMP_DIR + '/' + filename + '.gz'
  targetpath = TARGET_DIR + '/' + filename

  dprint("enter: url = %s, minsize = %s" % (url, minsize))

  #from sakurakit import skfileio
  #if os.path.exists(path) and skfileio.filesize(path) == size:
  #  dprint("leave: already downloaded")
  #  return True

  ok = False
  import gzip
  from sakurakit import skfileio, sknetio
  with SkProfiler("fetch"):
    # gzip=True to automatically extract gzip
    # flush=false to use more memory to reduce disk access
    if sknetio.getfile(url, path, flush=False, gzip=False):
      # Note: gzip=True does not extract gzip, it decompresses the header ... probs? >_<
      with gzip.open(path, 'rb') as f_in, open(targetpath, 'wb') as f_out:
        f_content = f_in.read()
        f_out.write(f_content)
      ok = skfileio.filesize(targetpath) > minsize
  if ok:
    # os.renames(path, targetpath)
    skfileio.removefile(path)
  elif os.path.exists(path):
    skfileio.removefile(path)
    skfileio.removefile(targetpath)
  dprint("leave: ok = %s" % ok)
  return ok

def lock(lang): # str -> bool
  name = "kanjidic.%s.lock" % lang
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
  return lock(lang) and get(lang)

# Main process

def usage():
  print 'usage:', '|'.join(sorted(DICS.iterkeys()))

def msg(lang): # str ->
  dic = DICS[lang]
  url = DIC_URL % dic
  import messages
  messages.info(
    name="KANJIDIC (%s)" % lang,
    location="Caches/Dictionaries/KanjiDic/%s" % dic,
    size=MIN_DIC_SIZE,
    urls=[HP_URL, url],
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
        skos.open_location(os.path.abspath(TARGET_DIR))
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
