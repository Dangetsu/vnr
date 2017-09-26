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

# http://www.lingoes.net/en/dictionary/dict_search.php
DICS = {
  # en: Vicon Japanese-English Dictionary
  # http://www.lingoes.net/en/dictionary/dict_down.php?id=4535B54974B7CB4B9F5AC8B61D1D6E8A
  'ja-en': {'inenc':'utf16', 'outenc':'utf8', 'size':12649440},

  # 新日汉大辞典
  # zh: New Japanese-Chinese Dictionary.ld2
  # http://www.lingoes.net/en/dictionary/dict_down.php?id=054A857FF8D2F3458F849148F6BE5CE9
  'ja-zh': {'inenc':'utf16', 'outenc':'utf16', 'size':5490752},

  # Naver 일본어사전
  # ko: Naver Japanese-Korean Dictionary.ld2
  # http://www.lingoes.net/en/dictionary/dict_down.php?id=63332AAFE6159C448748FF073FAA1157
  'ja-ko': {'inenc':'utf8', 'outenc':'utf8', 'size':11852800},

  # OVDP Japanese-Vietnamese Dictionary.ld2
  # http://www.lingoes.net/en/dictionary/dict_down.php?id=D2B4817958C3E644B3B2B6788B9B9E1C
  'ja-vi': {'inenc':'utf16', 'outenc':'utf8', 'size':20358360},

  # GBK和汉字典
  # zh: GBK Japanese-Chinese Dictionary.ld2
  # http://www.lingoes.net/en/dictionary/dict_down.php?id=212A6B5BC3D5634FB00E9BCC30F08C62
  'ja-zh-gbk': {'inenc':'utf8', 'outenc':'utf8', 'size':412280},
}

LANGS = frozenset(DICS.iterkeys())

import initdefs
DB_DIR = initdefs.CACHE_LINGOES_RELPATH
TMP_DIR = initdefs.TMP_RELPATH
LD_DIR = TMP_DIR

LD_SUFFIX = '.ld2'
DB_SUFFIX = '.db'

# Tasks

def init(): # raise
  for it in LD_DIR, TMP_DIR: # DB_DIR,
    if not os.path.exists(it):
      os.makedirs(it)

def getld(lang): # str -> bool
  url = DICS[lang].get('url') or "http://%s/pub/lingoes/%s.ld2" % (initdefs.DOMAIN_ORG, lang)
  size = DICS[lang]['size']
  path = LD_DIR + '/' + lang + LD_SUFFIX

  dprint("enter: lang = %s, size = %s" % (lang, size))

  from sakurakit import skfileio
  if os.path.exists(path) and skfileio.filesize(path) == size:
    dprint("leave: already downloaded")
    return True

  ok = False
  from sakurakit import sknetio
  with SkProfiler("fetch"):
    if sknetio.getfile(url, path, flush=False): # flush=false to use more memory to reduce disk access
      ok = skfileio.filesize(path) == size
  if not ok and os.path.exists(path):
    skfileio.removefile(path)
  dprint("leave: ok = %s" % ok)
  return ok

def makedb(lang): # str -> bool
  dprint("enter: lang = %s" % lang)
  dic = DICS[lang]

  ldpath = LD_DIR + '/' + lang + LD_SUFFIX
  dbpath = DB_DIR + '/' + lang + DB_SUFFIX
  tmppath = TMP_DIR + '/' + lang + DB_SUFFIX

  from sakurakit import skfileio
  for it in dbpath, tmppath:
    if os.path.exists(it):
      skfileio.removefile(it)

  if not os.path.exists(ldpath):
    dwarn("leave: ld does not exist: %s" % ldpath)
    return False

  ok = False
  from lingoes.lingoesdb import LingoesDb
  with SkProfiler("extract"):
    if LingoesDb(tmppath).create(ldpath, dic['inenc'], dic['outenc']):
      os.renames(tmppath, dbpath) # renames to create DB_DIR
      ok = True
    elif os.path.exists(tmppath):
      skfileio.removefile(tmppath)

  if os.path.exists(ldpath):
    skfileio.removefile(ldpath)
  dprint("leave: ok = %s" % ok)
  return ok

def lock(lang): # str
  name = "lingoes.%s.lock" % lang
  import initrc
  if initrc.lock(name):
    return True
  else:
    dwarn("multiple instances")
    return False

def get(lang): # str -> bool
  if lang not in LANGS:
    dwarn("unknown lang: %s" % lang)
    return False
  return lock(lang) and getld(lang) and makedb(lang)

# Main process

def usage():
  print 'usage:', '|'.join(LANGS)

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
      init()
      ok = get(lang)
      if ok:
        from sakurakit import skos
        skos.open_location(os.path.abspath(DB_DIR))
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
