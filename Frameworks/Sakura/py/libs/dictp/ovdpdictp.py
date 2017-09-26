# coding: utf8
# ovdpdictp.py
# 4/27/2015 jichi

if __name__ == '__main__':
  import sys
  sys.path.append("..")

from unitraits import jpchars, unichars
from sakurakit import skstr

def parseyomi(t):
  """Get first yomigana out of translation
  @param  t  unicode
  @return  unicode or None
  """
  if t.startswith('@'):
    return skstr.findbetween(t, '@', '\n')
  if t.startswith('- {'):
    t = skstr.findbetween(t, '- {', '}')
    if t and jpchars.iskana(t[0]):
      return t

def parsedef(text, english=False):
  """Get short definition out of translation
  @param  t  unicode
  @param* english  bool  English only
  @return  unicode or None
  """
  ret = None
  # When the text is in {}
  START = '- {'
  start = text.find(START)
  while start != -1:
    if start + len(START) < len(text) and unichars.isalpha(text[start + len(START)]):
      break
    start = text.find(START, start+len(START))
  if start != -1:
    start += len(START)
    stop = text.find('}', start)
    if stop != -1:
      ret = text[start:stop]

  # When the text is after -
  if not ret and not english:
    i = text.find('- ')
    if i != -1:
      ret = text[i+2:]

  if ret:
    for ch in '\n,;.-':
      i = ret.find(ch)
      if i != -1:
        ret = ret[:i]
    if ret.startswith('('):
      i = ret.find(')')
      if i != -1:
        ret = ret[i+1:]
    if ret.endswith(')'):
      i = ret.find('(')
      if i != -1:
        ret = ret[:i]
  if ret:
    for it in '@-{}()':
      if it in ret:
        return
    return ret.strip()

#def iterparsedef(text):
#  """Get short definition out of translation
#  @param  t  unicode
#  @yield  unicode
#  """
#  for m in _rx_def.finditer(text):
#    yield m.group(1)
#
#def parsedefs(text, sep=','):
#  """Get short definition out of translation
#  @param  t  unicode
#  @param* sep  unicode
#  @return  unicode not None
#  """
#  return sep.join(iterparsedef(text))

if __name__ == '__main__':
  path = '../../../../../../Caches/Dictionaries/OVDP/NhatViet/star_nhatviet'

  #t = u"殺す"
  #t = u"政治"
  #t = u"声"
  #t = u"出身"
  #t = u"裁判"
  t = u"可愛い"
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
  t = u"忘れ"
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
  #t = u'ふとん'
  #t = u'目'
  #t = u'中'
  t = u'合う'
  #t = u'意図'
  #t = u'足'

  # adj
  #t = u'可愛い'
  #t = u'かわいい'
  #t = u'ルージュ'
  #t = u'応える'
  #t = u'視線'
  #t = u'話'

  # name
  #t = u"安倍"
  #t = u'でしょう'
  #t = u'です'
  #t = u'ついぞ'
  #t = u'そんな'
  #t = u'ちゃ'
  #t = u'中'
  #t = u'そして'
  #t = u'まま'
  #t = u'逃す'
  #t = u'商店'
  #t = u'永遠'
  from stardict import stardict
  dic = stardict.StarDict(path)
  print dic.init()
  q = dic.query(t)
  if q:
    for i, it in enumerate(q):
      print t
      print i
      print it
      print "yomi:", parseyomi(it)
      print "def:", parsedef(it)
      print "def_en:", parsedef(it, english=True)

# EOF
