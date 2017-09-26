# coding: utf8
# kanjidicp.py
# 5/7/2015 jichi
#
# Download:
# http://www.csse.monash.edu.au/~jwb/kanjidic.html
# http://ftp.monash.edu.au/pub/nihongo/00INDEX.html
#
# EUC-JP encoding:
# http://ftp.monash.edu.au/pub/nihongo/kanjidic.gz

if __name__ == '__main__':
  import sys
  sys.path.append("..")

from sakurakit.skdebug import dwarn

KANJIDIC_ENCODING = 'euc-jp'

def parsefiledef(path, encoding=KANJIDIC_ENCODING):
  """
  @param  path  unicode
  @return  {unicode word, unicode def}
  """
  import codecs
  try:
    ret = {}
    with codecs.open(path, 'r', encoding) as f:
      for i,line in enumerate(f):
        if i:
          value = parsedef(line)
          if value:
            key = line.partition(' ')[0]
            ret[key] = value
    return ret
  except Exception, e: dwarn(e)

def parsedef(line):
  """
  @param  path  str
  @return  unicode or None
  """
  from sakurakit import skstr
  return skstr.findbetween(line, '{', '}')

def parsedefs(line):
  """
  @param  path  str
  @yield  unicode def
  @raise
  """
  import re
  rx = re.compile('{([^}]+?)}')
  for m in rx.finditer(line):
    yield m.group(1)

if __name__ == '__main__':
  #def wait(timeout=5):
  #  from time import sleep
  #  print "sleep %s" % timeout
  #  sleep(timeout)

  path = '../../../../../../Caches/Dictionaries/KanjiDic/kanjidic'
  m = parsefiledef(path)
  print len(m)
  print m[u"万"]

# EOF
