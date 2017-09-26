# coding: utf8
# trts.py
# 12/28/2013 jichi
if __name__ == '__main__':
  import sys
  reload(sys)
  sys.setdefaultencoding('utf-8')
  sys.path.append('..')

import re
#from sakurakit import skfileio
from sakurakit.skdebug import dprint, dwarn

# Sample XML:
#    <message>
#        <location filename="sktr.py" line="30"/>
#        <source>English</source>
#        <translation>英語</translation>
#    </message>
def trtext(tr, text, locale):
  """
  @param  tr  function
  @param  text  unicode  text
  @param* to  str  language
  @param* fr  str  language
  @return  unicode or None
  """
  outer = {'count':0}
  def _iter():
    rx_spaces = re.compile(r"[\s\n]+", re.DOTALL)
    rx_tag = re.compile(r"(<.+?>)")
    tag = '' # current tag
    source = '' # previous source
    fr = 'en'
    to = locale[:2]
    for it in rx_tag.split(text):
      if not it or rx_spaces.match(it):
        tag = ''
        yield it
      elif it[0] == '<':
        tag = it
        if tag.startswith('<TS '):
          yield re.sub(r'language="[a-zA-Z_]+"',
                        'language="%s"' % locale, tag)
        else:
          yield tag
      elif tag == '<source>':
        tag = ''
        source = it
        yield it
      elif tag == '<translation>':
        tag = ''
        if not source:
          yield ''
        else:
          outer['count'] += 1
          t = tr(source, to=to, fr=fr)
          dprint(outer['count'])
          if t:
            yield t
          else:
            dwarn("translation failed: '%s'" % source)
            yield source
      else:
        tag = ''
        yield it
  return ''.join(_iter())

def trfile(tr, fout, fin, locale):
  """
  @param  fout  unicode  path
  @param  fin  unicode  path
  @param* locale  str
  @return  bool
  """
  try:
    with open(fin, 'r') as inputFile:
      with open(fout, 'w') as outputFile:
        t = inputFile.read()
        t = trtext(tr, t, locale)
        if t:
          outputFile.write(t)
          return True
  except Exception, e:
    dwarn(e)
  return False

if __name__ == '__main__':
  from sakurakit import skfileio
  from google import googletrans
  tr = googletrans.translate

  fin = "../sakurakit/tr/zh_CN.ts"
  locale = 'zh_CN'
  #fr = 'zhs'
  skfileio.removefile(fout)
  ok = trfile(tr, fout, locale=locale)
  print ok

  fin = "../sakurakit/tr/ja_JP.ts"
  locale = 'ja_JP'
  #fr = 'ja'
  skfileio.removefile(fout)
  ok = trfile(tr, fout, locale='locale')
  print ok

# EOF
