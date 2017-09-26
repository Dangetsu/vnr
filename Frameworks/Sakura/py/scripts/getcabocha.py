# coding: utf8
# getcabocha.py
# Get CaboCha model for MeCab dictionaries
# 2/14/2014 jichi

if __name__ == '__main__':
  import initrc
  initrc.chcwd()
  initrc.initenv()

  import os
  title = os.path.basename(__file__)
  initrc.settitle(title)

import os
from sakurakit import skos
from sakurakit.skdebug import dprint, dwarn
from sakurakit.skprof import SkProfiler

# http://ftp.monash.edu.au/pub/nihongo/UPDATES
# ftp://ftp.monash.edu.au/pub/nihongo/

# CaboCha (cabocha-model-index) does NOT work on Windows XP orz
#CABOCHA_URL = 'http://cabocha.googlecode.com/files/cabocha-0.68.tar.bz2' # use http over ftp since requests do not support ftp
#CABOCHA_FILESIZE = 84520669

import initdefs
URL_TPL = 'http://{}/pub/cabocha/%s.models.tar.bz2'.format(initdefs.DOMAIN_ORG)
MIN_FILESIZE = 4000000 # at least 39MB

#CABOCHA_FILENAME = 'caboch'
#CABOCHA_SUFFIX = '.tbz2'
FILENAME_TPL = 'cabocha.%s.tbz2'

DICS = 'ipadic', 'unidic', 'junman'
MODELS = 'chunk', 'dep', 'ne' #

DIC_DIR = initdefs.CACHE_CABOCHA_RELPATH
TMP_DIR = initdefs.TMP_RELPATH

# Tasks

def init(): # raise
  for it in TMP_DIR,: # DIC_DIR,
    if not os.path.exists(it):
      os.makedirs(it)

def extract(dic): # str -> bool
  dprint("enter: dic = %s" % dic)

  srcpath = TMP_DIR + '/' + FILENAME_TPL % dic
  tmppath = TMP_DIR + '/cabocha.' + dic
  targetpath = DIC_DIR + '/' + dic

  import shutil
  from sakurakit import skfileio
  with SkProfiler("extract"):
    ok = skfileio.extracttarbz2(srcpath, tmppath)
  if ok:
    dickey = 'ipa' if dic == 'ipadic' else dic
    for it in MODELS:
      model = "%s.%s.model" % (it , dickey)
      if not os.path.exists(tmppath + '/' + model):
        ok = False
        dwarn("missing model: %s" % model)
    if os.path.exists(targetpath): # alway remove old path even if not ok
      shutil.rmtree(targetpath)
    if ok:
      os.renames(tmppath, targetpath)
    #child = skfileio.getfirstchilddir(tmppath)
    #modeldir = child + '/model'
    #if not os.path.exists(modeldir):
    #  dwarn("model dir does not exist")
    #else:
    #  from cabochajlp import cabochamodel
    #  if os.path.exists(targetpath):
    #    shutil.rmtree(targetpath)
    #  os.makedirs(targetpath)
    #  dickey = 'ipa' if dic == 'ipadic' else dic
    #  for model in MODELS:
    #    with SkProfiler():
    #      dprint("process model: %s" % model)
    #      input = "%s.%s.txt" % (model , dickey)
    #      output = "%s.%s.model" % (model , dickey)
    #      inputpath = os.path.abspath(modeldir + '/' + input)
    #      outputpath = os.path.abspath(modeldir + '/' + output)
    #      if cabochamodel.modelindex(outputpath, inputpath):
    #        os.renames(outputpath, targetpath + '/' + output)
    #      else:
    #        dwarn("failed to process model %s" % model)
  if os.path.exists(tmppath):
    shutil.rmtree(tmppath)
  skfileio.removefile(srcpath)

  dprint("leave: ok = %s" % ok)
  return ok

def get(dic): # str -> bool
  url = URL_TPL % dic
  minsize = MIN_FILESIZE
  path = TMP_DIR + '/' + FILENAME_TPL % dic

  dprint("enter: url = %s, minsize = %s" % (url, minsize))

  #from sakurakit import skfileio
  #if os.path.exists(path) and skfileio.filesize(path) == size:
  #  dprint("leave: already downloaded")
  #  return True

  ok = False
  from sakurakit import skfileio, sknetio
  with SkProfiler("fetch"):
    if sknetio.getfile(url, path, flush=False): # flush=false to use more memory to reduce disk access
      ok = skfileio.filesize(path) > minsize
  if not ok and os.path.exists(path):
    skfileio.removefile(path)
  dprint("leave: ok = %s" % ok)
  return ok

def lock(dic): # str
  name = "cabocha.%s.lock" % dic
  import initrc
  if initrc.lock(name):
    return True
  else:
    dwarn("multiple instances")
    return False

def run(dic): # str -> bool
  if dic not in DICS:
    dwarn("unknown dic: %s" % dic)
    return False
  return lock(dic) and get(dic) and extract(dic)

# Main process

def usage():
  print 'usage:', '|'.join(DICS)

def msg(dic): # str ->
  import messages
  messages.info(
    name="CaboCha (%s)" % dic,
    location="Caches/Dictionaries/CaboCha/%s" % dic,
    size=MIN_FILESIZE,
    urls=[URL_TPL % dic],
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
    if dic == 'ipa':
      dic = 'ipadic'
    try:
      msg(dic)
      init()
      ok = run(dic)
      if ok:
        from sakurakit import skos
        dicdir = os.path.join(DIC_DIR, dic)
        skos.open_location(os.path.abspath(dicdir))
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
