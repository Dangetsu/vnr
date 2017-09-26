# coding: utf8
# youtube.py
# 10/27/2013 jichi

if __name__ == '__main__':
  import sys
  reload(sys)
  sys.setdefaultencoding('utf-8')
  import initrc
  initrc.initenv()

  import os
  title = os.path.basename(__file__)
  initrc.settitle(title)

import os
from sakurakit.skdebug import dprint, dwarn
from google import googletrans

USAGE = "to.ts from.ts"

#GT = googletrans.GoogleJsonTranslator() # this might get my IP blocked
GT = googletrans.GoogleHtmlTranslator()
translate = GT.translate

def getcfg(fname): # unicode -> unicode
  return os.path.join(os.path.dirname(__file__), '../../tr/%s' % fname)

def loadcfg(name): # unicode -> {unicode:unicode}
  ret = {}
  with open(name, 'r') as f:
    for line in f:
      t = line.strip()
      if t and t[0] != '#':
        fr , delim, to = t.partition('=')
        ret[fr.rstrip()] = to.lstrip()
  return ret

CORRECTIONS = {
  'enko': loadcfg(getcfg('ko_KR.cfg')),
}

ESCAPE = frozenset((
  'en',
  'ja',
  'zh', 'zht', 'zhs',
  'ko',
  'vi',
  'th',
  'id',
  'tl',
  'ms',
  'he',
  'ar',
  'be',
  'bg',
  'cs',
  'da',
  'de',
  'el',
  'es',
  'et',
  'fi',
  'fr',
  'hu',
  'it',
  'lt',
  'lv',
  'nl',
  #'no',
  'nb',
  'pl',
  'pt',
  'ro',
  'ru',
  'sk',
  'sl',
  'sv',
  'tr',
  'uk',

  'he', # Hebrew

  'UI',
  'Asc', 'Desc',
  'Python', 'BBCode', 'Javascript',
))
def tr(text, escape=ESCAPE, corrections=CORRECTIONS, fr='', to=''):
  """
  @param  tr  function
  @param  text  unicode  text
  @param* to  str  language
  @param* fr  str  language
  @return  unicode or None
  """
  d = corrections.get(fr+to)
  if d:
    t = d.get(text)
    if t:
      return t
  if text in escape:
    return text
  return translate(text,  fr=fr, to=to)

def locale2lang(t):
  """
  @param  t  str
  @return  str
  """
  if t == 'zh_CN':
    return 'zhs'
  if t == 'zh_TW':
    return 'zht'
  return t[:2]

def translatefile(fout, fin):
  """
  @param  fout  ts path
  @param  fin  ts path
  @return  bool
  """
  import os
  dprint("enter")
  flocale = os.path.basename(fin).split('.')[0]
  tlocale = os.path.basename(fout).split('.')[0]
  dprint("processing: %s < %s" % (tlocale, flocale))
  from trio import trts
  ok = trts.trfile(tr, fout, fin, locale=tlocale)
  dprint("leave: ok = %s" % ok)
  return ok

def main(argv):
  """
  @param  argv  [unicode]
  @return  int
  """
  dprint("enter")
  ret = 0
  if len(argv) != 2:
    dwarn("usage: %s" % USAGE)
  else:
    # Enable this could cause translation to be blocked by Google
    #import requests
    #from google import googletrans
    #googletrans.session = requests.Session() # speed up network access
    try:
      ok = translatefile(fout=argv[0], fin=argv[1])
      ret = 0 if ok else 1
    except Exception, e:
      dwarn(e)
      ret = 1
  dprint("leave: ret = %s" % ret)
  return ret

if __name__ == '__main__':
  import sys
  ret = main(sys.argv[1:])
  sys.exit(ret)

# EOF
