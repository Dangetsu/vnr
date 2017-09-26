# coding: utf8
# trxml.py
# 12/28/2013 jichi
if __name__ == '__main__':
  import sys
  reload(sys)
  sys.setdefaultencoding('utf-8')
  sys.path.append('..')

import re
#from sakurakit import skfileio
from sakurakit.skdebug import dwarn

def trtext(tr, text, **kwargs):
  """
  @param  tr  function
  @param  text  unicode  text
  @param* to  str  language
  @param* fr  str  language
  @return  unicode or None
  """
  rx_spaces = re.compile(r"[\s\n]+", re.DOTALL)
  rx_tag = re.compile(r"(<.+?>)")
  #rx_latin = re.compile(r"[a-zA-Z0-9 ]+")
  def _iter():
    for it in rx_tag.split(text):
      if not it or rx_spaces.match(it) or it[0] == '<': #or rx_latin.match(it):
        yield it
      else:
        yield tr(it,  **kwargs)
  return ''.join(_iter())

def trfile(tr, fout, fin, **kwargs):
  """
  @param  fout  unicode  path
  @param  fin  unicode  path
  @param* encoding  str  file encoding
  @param* errors  str  encode error policy
  @param* to  str  language
  @param* fr  str  language
  @return  bool
  """
  try:
    with open(fin, 'r') as inputFile:
      with open(fout, 'w') as outputFile:
        t = inputFile.read()
        t = trtext(tr, t, **kwargs)
        if t:
          outputFile.write(t)
          return True
  except Exception, e:
    dwarn(e)
  return False

if __name__ == '__main__':
  from sakurakit import skfileio
  from baidu import baidufanyi
  tr = baidufanyi.translate

  fout = 'ja_JP.ts'
  to = 'ja'
  fin = "../sakurakit/tr/zh_CN.ts"
  fr = 'zhs'
  skfileio.removefile(fout)
  ok = trfile(tr, fout, fin, to=to, fr=fr)
  print ok

  fout = 'zh_CN.ts'
  to = 'zhs'
  fin = "../sakurakit/tr/ja_JP.ts"
  fr = 'ja'
  skfileio.removefile(fout)
  ok = trfile(tr, fout, fin, to=to, fr=fr)
  print ok

# EOF
