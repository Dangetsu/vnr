# coding: utf8
# mecabfmt.py
# 2/24/2014 jichi
#
# Comparison of different mecab dictionaries
# http://www.mwsoft.jp/programming/munou/mecab_dic_perform.html

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

class DEFAULT(object):

  SPLIT = ','

  # Columns starts from 0

  COL_BASIC = 5 # The basic columns that are shared by are dict

  COL_SURFACE = COL_BASIC + 1
  COL_KATA = COL_SURFACE + 1
  #COL_YOMI = COL_KATA + 1 # not used

  @classmethod
  def getcol(cls, f, col): # unicode, int -> unicode
    l = f.split(cls.SPLIT)
    if len(l) >= col + 1:
      return l[col]

  @classmethod
  def getkata(cls, f): # unicode feature -> unicode or None
    return cls.getcol(f, cls.COL_KATA)

  @classmethod
  def getsurface(cls, f): # unicode feature -> unicode or None
    return cls.getcol(f, cls.COL_SURFACE)

  @classmethod
  def csv(cls, surf, cost, hira, kata): # unicode* -> unicode
    #u"工藤,1223,1223,6058,名詞,固有名詞,人名,名,*,*,くどう,クドウ,クドウ"
    return u"%s,,,%s,名詞,固有名詞,人名,名,*,*,%s,%s,%s" % (surf, cost, hira, kata, kata)

# Example: 名詞,一般,*,*,*,*,憎しみ,ニクシミ,ニクシミ
class IPADIC(DEFAULT):

  @classmethod
  def getkata(cls, f): # override, more efficient
    i = f.rfind(',')
    if i > 0:
      j = f.rfind(',', 0, i)
      if j > 0:
        return f[j+1:i]

class UNIDIC(DEFAULT):
  COL_KANJI = DEFAULT.COL_BASIC + 2
  COL_SURFACE = COL_KANJI + 1
  COL_ORIG = 12 # Columns starts from 0

  COL_KATA = 17 # override
  #COL_KATA = DEFAULT.COL_BASIC + 1 # override

  @classmethod
  def getkanji(cls, f): # unicode feature -> unicode or None
    return cls.getcol(f, cls.COL_KANJI)

  @classmethod
  def getorig(cls, f): # unicode feature -> unicode or None
    return cls.getcol(f, cls.COL_ORIG)

  # http://chocolapod.sakura.ne.jp/blog/entry/56
  @classmethod
  def csv(cls, surf, cost, hira, kata): # override
    # ジョジョの奇妙な冒険,,,0,名詞,固有名詞,一般,*,*,*,ジョジョノキミョウナボウケン,ジョジョの奇妙な冒険,ジョジョの奇妙な冒険,ジョジョノキミョーナボウケン,ジョジョの奇妙な冒険,ジョジョノキミョーナボウケン,*,*,*,*
    #return u"%s,,,%s,名詞,固有名詞,人名,姓,*,*,%s,%s,%s,%s,%s,%s,*,*,*,*" % (surf, cost, kata, surf, surf, kata, surf, kata)
    # FIXME: The above does not work
    return u"%s,,,%s,名詞,固有名詞,一般,*,*,*,%s,%s,%s,%s,%s,%s,*,*,*,固" % (surf, cost, kata, surf, surf, kata, surf, kata)

# ジョジョの奇妙な冒険,,,0,名詞,固有名詞,一般,*,*,*,ジョジョノキミョウナボウケン,ジョジョの奇妙な冒険,ジョジョの奇妙な冒険,ジョジョノキミョーナボウケン,ジョジョの奇妙な冒険,ジョジョノキミョーナボウケン,*,*,*,*

FORMATS = {
  'ipadic': IPADIC,
  'unidic': UNIDIC,
  'unidic-mlj': UNIDIC,
}
def getfmt(name):
  return FORMATS.get(name) or DEFAULT

DEFAULT = UNIDIC

# EOF
