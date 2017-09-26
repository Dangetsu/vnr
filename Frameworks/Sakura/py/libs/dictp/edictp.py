# coding: utf8
# edictp.py
# 4/6/2015 jichi
#
# Download:
# http://www.edrdg.org/jmdict/edict.html
# http://ftp.monash.edu.au/pub/nihongo/00INDEX.html
#
# UTF-8 encoding:
# http://ftp.monash.edu.au/pub/nihongo/edict2u.gz

if __name__ == '__main__':
  import sys
  sys.path.append("..")

# For better performance
from unitraits import jpchars
from sakurakit.skdebug import dwarn

#TABLE_NAME = 'entry'

def parsefile(path, encoding='utf8'):
  """
  @param  path  str
  @yield  (unicode word, unicode definition)
  @raise
  """
  import codecs
  try:
    with codecs.open(path, 'r', encoding) as f:
      for line in f:
        ch = ord(line[0])
        # skip the first line and letters
        if ch == 0x3000 or ch >= ord(u'Ａ') and ch <= ord(u'Ｚ') or ch >= ord(u'ａ') and ch <= ord(u'ｚ'):
          continue
        #left.strip(), sep, right = line.partition('/')
        i = line.index('/')
        yield line[:i-1], line[i:-1] # trim trailing spaces
  except Exception, e:
    dwarn(e)
    raise

# Parse word and yomigana

def _remove_word_parenthesis(text):
  """Remove parenthesis
  @param  text  unicode  surface
  @return  unicode
  """
  i = text.find('(')
  if i == -1:
    return text
  else:
    return text[:i]

# Example: 噯;噯気;噫気;噯木(iK) [おくび(噯,噯気);あいき(噯気,噫気,噯木)]
def parseword(word):
  """
  @param  path  str
  @yield  unicode surface, unicode reading
  """
  # Remove duplicate keys
  s = set()
  for k,v in _parseword(word):
    if (k and k not in s
        and ord(k[0]) > 255 # skip ascii keys
        and '(' not in k and ')' not in k): # skip illegal characters
      s.add(k)
      if not v and jpchars.allkana(k):
        v = k
      yield k,v

def _parseword(word):
  """
  @param  path  str
  @yield  unicode surface, unicode reading
  """
  if '[' not in word: # no yomi
    if ';' not in word:
      yield _remove_word_parenthesis(word), ''
    else:
      for it in word.split(';'):
        yield _remove_word_parenthesis(it), ''
  else:
    left, sep, right = word.partition(' [')
    if right[-1] == ']':
      right = right[:-1]
      if ')' in right:
        for group in right.split(';'):
          ll, sep, rr = group.partition('(')
          if rr and rr[-1] == ')':
            rr = rr[:-1]
            if ',' not in rr:
              yield rr, ll
            else:
              for it in rr.split(','):
                yield it, ll
      yomi = None
      if ';' not in right:
        yomi = right
      else:
        yomi = right.partition(';')[0]
        yomi = _remove_word_parenthesis(yomi)
      if ';' not in left:
        yield _remove_word_parenthesis(left), yomi
      else:
        for it in left.split(';'):
          yield _remove_word_parenthesis(it), yomi

# Parse translation

# Example:
# /(n) (1) (uk) curry/(2) (abbr) (uk) (See カレーライス) rice and curry/(P)/EntL1039140X/
# /(n,vs) (obsc) (嘈囃 is sometimes read むねやけ) (See 胸焼け) heartburn/sour stomach/EntL2542040/
def parsetransrole(trans, sep=None):
  """Get role out of translation
  @param  trans  unicode
  @param* sep  unicode  separator for multiple rules
  @return  unicode  separated by ','
  """
  if trans.startswith('/('):
    i = trans.find(')')
    if i != -1:
      ret = trans[2:i]
      if sep is not None:
        ret = ret.replace(',', sep)
      return ret
  return ''

def parsetransrole1(trans):
  """Get only the first role out of translation
  @param  trans  unicode
  @return  unicode
  """
  ret = parsetransrole(trans)
  if ',' in ret:
    ret = ret.partition(',')[0]
  return ret

# Get only the first translation
_REMOVE_TRANS_SUFFICES = ( # suffices to remove
  "to ", # verb prefix
  "one's ", # such One's Line of Sight (視線)
)
def parsetransdef(trans):
  """Get short definition out of translation
  @param  trans  unicode
  @return  unicode
  """
  if trans.startswith('/'):
    ret = trans[1:]
    while ret.startswith('('):
      ret = ret.partition(')')[-1].lstrip()
    if ret.startswith('{'):
      ret = ret.partition('}')[-1].lstrip()
    if '/' in ret:
      ret = ret.partition('/')[0]
    while ret.endswith(')'):
      ret = ret.rpartition('(')[0].rstrip()
    for it in _REMOVE_TRANS_SUFFICES:
      if ret.startswith(it): # skip verb prefix 'to'
        ret = ret[len(it):]
    if '(' not in ret and ')' not in ret and '.' not in ret and '"' not in ret: # skip bad definition
      return ret
  return ''

if __name__ == '__main__':
  import sqlite3
  dbpath = 'edict.db'

  def test_create():
    path = 'edict2u'
    try:
      for i,(k,v) in enumerate(iterparse(path)):
        print '|%s|' % i
        print '|%s|' % k
        print '|%s|' % v
        break
    except:
      pass

    import os
    if os.path.exists(dbpath):
      os.remove(dbpath)

    from sakurakit.skprof import SkProfiler

    from dictdb import dictdb

    with SkProfiler("create db"):
      print dictdb.createdb(dbpath)

    with SkProfiler("insert db"):
      try:
        with sqlite3.connect(dbpath) as conn:
          q = parsefile(path)
          dictdb.insertentries(conn.cursor(), q, ignore_errors=True)
          conn.commit()
      except Exception, e:
        dwarn(e)

  def test_word():
    w = u'顔(P);貌;顏(oK) [かお(P);がん(顔)(ok)]'
    for it in parseword(w):
      print it[0], it[1]

  def test_parse():
    #t = u"殺す"
    #t = u"政治"
    #t = u"声"
    #t = u"出身"
    #t = u"裁判"
    #t = u"可愛い"
    #t = u"大柴"
    #t = u"身長"
    #t = u"体重"
    #t = u"茶道"
    #t = u"結婚"
    #t = u"採集"
    #t = u"どこ"
    #t = u"佐藤"
    #t = u"雫"
    #t = u"街"
    #t = u"晴明"
    #t = u"エミリ"
    #t = u"春日"
    #t = u"石浦"
    #t = u"能力"
    #t = u"人気"
    #t = u"任せ"
    #t = u"幸せ"
    #t = u"忘れる"
    #t = u"忘れ"
    #t = u"止めっ"
    #t = u'移り住ん'
    #t = u'移り住む'
    #t = u'頼ま'
    #t = u'頼む'
    #t = u'聞く'
    #t = u'聞か'
    #t = u'討ち'
    #t = u'討つ'
    #t = u'動い'
    #t = u'動く'
    #t = u'知って'
    #t = u'言わ'
    #t = u'行きぁ'

    # prep/conj
    #t = u'しかし'

    # verb
    #t = u'行きぁ'

    # noun
    #t = u"友達"
    #t = u"ヤング"
    #t = u'私'

    # adj
    #t = u'可愛い'
    #t = u'ルージュ'
    #t = u'応える'
    t = u'視線'
    #t = u'話'

    # name
    #t = u"安倍"
    from dictdb import dictdb
    t = '%' + t + '%'
    with sqlite3.connect(dbpath) as conn:
      for i, it in enumerate(dictdb.queryentries(conn.cursor(), wordlike=t)):
        content = it[1]
        print it[0], content
        print "role:", parsetransrole(content)
        print "def:", parsetransdef(content)
        if i > 10:
          break

  #test_create()
  #test_word()
  test_parse()

# EOF

#import re
#_rx_tr1 = re.compile('|'.join((
#  r'^/\(.+?\) (?=[a-zA-Z0-9.])',
#  r'^/',
#  r'[/(].*',
#)))
#_rx_tr2 = re.compile('|'.join((
#  r'^(?:to|\.+) ', # remove leading "to" and ".."
#  r'from which.*', # remove trailing clause
#  r'[.]+$', # remove trailing dots
#)))
#def translate(text, wc=5, limit=3, complete=True):
#  """Translate Japanese word to English
#  @param  text  unicode
#  @param* wc  int  count of word -1
#  @param* limit  int  maximum tuples to look up
#  @param* complete  bool  enabled by default
#  @return  unicode or None
#
#  Return the first hitted word in the dictionary.
#  """
#  ret = _rx_tr2.sub('',
#    _rx_tr1.sub('', text).strip()
#  ).strip()
#  if ret and (not wc or ret.count(' ') <= wc):
#    return ret
