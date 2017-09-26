# coding: utf8
# mecabformat.py
# 2/24/2014 jichi
# Dictionary feature format.
# Comparison of different mecab dictionaries
# http://www.mwsoft.jp/programming/munou/mecab_dic_perform.html

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

from unitraits import unichars, jpchars
import mecabdef

class UniDicFormatter(object):
  # Dict type
  DIC_UNIDIC = 'unidic'
  DIC_EDICT = 'edict'

  SEP = ',' # column separator
  EMPTY_COL = '*' # empty column

  # Columns starts from 0

  COL_BASIC = 5 # The basic columns that are shared by are dict holding the roles of the word

  COL_SURFACE = COL_BASIC + 1
  COL_SOURCE = COL_BASIC + 2 # converted kanji
  COL_SURFACE = COL_SOURCE + 1
  COL_ORIGIN = 12 # the origination of the phrase

  COL_KATA = 17 # the original kata column without EDICT that should be checked first
  COL_DIC_KATA = COL_BASIC + 1 # kata column for EDICT

  COL_DIC_TYPE = -1 # the type such as edict
  COL_DIC_ID = -2 # the type such as edict
  COL_DIC_TRANS = -3 # translation of the entry

  def getcol(self, f, col):
    """
    @param  f  unicode or list feature
    @param  col  int  column
    @return  unicode not None
    """
    if isinstance(f, basestring):
      f = f.replace(self.EMPTY_COL, '').split(self.SEP)
    return f[col] if col < len(f) else ''

  def getkata(self, f):
    return self.getcol(f, self.COL_KATA) or self.getcol(f, self.COL_DIC_KATA)

  def getsurface(self, f): return self.getcol(f, self.COL_SURFACE)
  def getsource(self, f): return self.getcol(f, self.COL_SOURCE)
  def getorigin(self, f): return self.getcol(f, self.COL_ORIGIN)

  def getdictype(self, f): return self.getcol(f, self.COL_DIC_TYPE)
  def getdictrans(self, f): return self.getcol(f, self.COL_DIC_TRANS)
  def getdicid(self, f): # unicode -> int or 0
    try: return int(self.getcol(f, self.COL_DIC_ID))
    except: return 0

  def isdic(self, f): return bool(self.getdictype(f)) # -> bool

  def getlatin(self, f): # get English translation
    s = self.getsource(f)
    if s and '-' in s:
      s = s.partition('-')[-1]
      if s and unichars.isalpha(s[0]) and unichars.isalpha(s[-1]):
        return s
    return ''

  def getkanji(self, f): # get Chinese translation
    s = self.getsource(f)
    if s:
      if '-' in s:
        s = s.partition('-')[0]
      if s and jpchars.iskanji(s[0]) and jpchars.iskanji(s[-1]):
        return s
    return ''

  def getrole(self, f): # unicode -> str not None
    if self.getdictype(f) == self.DIC_EDICT: # probably EDICT
      for i in (0, 1):
        c = self.getcol(f, i)
        if c:
          if c == 'num':
            return mecabdef.ROLE_NUM
          if c == 'pn':
            return mecabdef.ROLE_PRONOUN
          if c == 'suf':
            return mecabdef.ROLE_SUFFIX
          if c == 'pref':
            return mecabdef.ROLE_PREFIX
          if c == 'conj':
            return mecabdef.ROLE_CONJ
          if c == 'exp':
            return mecabdef.ROLE_PHRASE
          if c == 'n' or c.startswith('n-'):
            return mecabdef.ROLE_NOUN
          if c == 'adj' or c.startswith('adj-'):
            return mecabdef.ROLE_ADJ
          if c == 'adv' or c.startswith('adv-'):
            return mecabdef.ROLE_ADV
          if c == 'aux' or c.startswith('aux-'):
            return mecabdef.ROLE_AUX
          if c in ('v', 'vi', 'vt', 'vs'):
            return mecabdef.ROLE_VERB
      return mecabdef.ROLE_PHRASE
    else:
      for i in (2, 1, 0):
        ret = mecabdef.NAME_ROLES.get(self.getcol(f, i))
        if ret:
          return ret
      return mecabdef.ROLE_PHRASE # something is wrong here

UNIDIC_FORMATTER = UniDicFormatter()

# EOF

# http://chocolapod.sakura.ne.jp/blog/entry/56
# ジョジョの奇妙な冒険,,,0,名詞,固有名詞,一般,*,*,*,ジョジョノキミョウナボウケン,ジョジョの奇妙な冒険,ジョジョの奇妙な冒険,ジョジョノキミョーナボウケン,ジョジョの奇妙な冒険,ジョジョノキミョーナボウケン,*,*,*,*
#def csv(cls, surf, cost, hira, kata): # override
#  # ジョジョの奇妙な冒険,,,0,名詞,固有名詞,一般,*,*,*,ジョジョノキミョウナボウケン,ジョジョの奇妙な冒険,ジョジョの奇妙な冒険,ジョジョノキミョーナボウケン,ジョジョの奇妙な冒険,ジョジョノキミョーナボウケン,*,*,*,*
#  #return u"%s,,,%s,名詞,固有名詞,人名,姓,*,*,%s,%s,%s,%s,%s,%s,*,*,*,*" % (surf, cost, kata, surf, surf, kata, surf, kata)
#  # FIXME: The above does not work
#  return u"%s,,,%s,名詞,固有名詞,一般,*,*,*,%s,%s,%s,%s,%s,%s,*,*,*,固" % (surf, cost, kata, surf, surf, kata, surf, kata)

# Example: 名詞,一般,*,*,*,*,憎しみ,ニクシミ,ニクシミ
#class IPADIC(DEFAULT):
#
#  @classmethod
#  def getkata(cls, f): # override, more efficient
#    i = f.rfind(',')
#    if i > 0:
#      j = f.rfind(',', 0, i)
#      if j > 0:
#        return f[j+1:i]
#
#FORMATS = {
#  'ipadic': IPADIC,
#  'unidic': UNIDIC,
#  'unidic-mlj': UNIDIC,
#}
#def getfmt(name):
#  return FORMATS.get(name) or DEFAULT
