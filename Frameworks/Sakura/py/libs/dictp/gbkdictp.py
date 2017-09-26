# coding: utf8
# gbkdictp.py
# 4/27/2015 jichi

if __name__ == '__main__':
  import sys
  sys.path.append("..")

# For better performance
from unitraits import jpchars
from sakurakit import skstr

# Parse translation

# Example:
# /(n) (1) (uk) curry/(2) (abbr) (uk) (See カレーライス) rice and curry/(P)/EntL1039140X/
# /(n,vs) (obsc) (嘈囃 is sometimes read むねやけ) (See 胸焼け) heartburn/sour stomach/EntL2542040/
def parserole(t, sep=None):
  """Get first role out of translation
  @param  t  unicode
  @param* sep  unicode  separator for multiple rules
  @return  unicode  separated by ','
  """
  return skstr.findbetween(t, '[', ']') or '' # sep is not implemented

def parseyomi(t, sep=None):
  """Get first yomigana out of translation
  @param  t  unicode
  @param* sep  unicode  separator for multiple rules
  @return  unicode  separated by ','
  """
  return skstr.findbetween(t, u'【', u'】') or '' # sep is not implemented

def parsedef(t):
  """Get short definition out of translation
  @param  t  unicode
  @return  unicode
  """
  t = skstr.findbetween(t, '<N>', '</N>')
  if t:
    for c in u'，；(':
      i = t.find(c)
      if i != -1:
        t = t[:i]
    for c in u']>)】~':
      i = t.find(c)
      if i != -1:
        t = t[i+1:]
    if '...' in t or u'“' in t:
      return ''
    t = t.strip()
  return t or ''

if __name__ == '__main__':
  dbpath = '../../../../../../Caches/Dictionaries/Lingoes/ja-zh-gbk.db'

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
    #t = u'視線'
    #t = u'話'

    #t = u'ふとん'
    #t = u'目'
    #t = u'中'
    #t = u'合う'
    t = u'意図'

    # name
    #t = u"安倍"
    import sqlite3
    from dictdb import dictdb
    with sqlite3.connect(dbpath) as conn:
      for i, it in enumerate(dictdb.queryentries(conn.cursor(), word=t)):
        content = it[1]
        print it[0], content
        print "role:", parserole(content)
        print "yomi:", parseyomi(content)
        print "def:", parsedef(content)
        if i > 10:
          break

  #test_create()
  #test_word()
  test_parse()

# EOF
