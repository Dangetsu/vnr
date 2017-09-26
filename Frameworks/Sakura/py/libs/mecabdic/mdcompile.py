# coding: utf8
# mdcompile.py
# 11/9/2013 jichi
#
# See:
# http://tseiya.hatenablog.com/entry/2012/09/19/191114
# http://mecab.googlecode.com/svn/trunk/mecab/doc/dic.html
#
# Example:
# mecab-dict-index -d /usr/local/Cellar/mecab/0.993/lib/mecab/dic/ipadic -u original.dic -f utf8 -t utf8 out.csv

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import os, subprocess
from sakurakit.skdebug import dwarn
from sakurakit import skfileio
from unitraits.uniconv import hira2kata, kata2hira

def costofsize(size):
  """
  @param  size  int  surface size
  @return  int  negative  the smaller the more important
  """
  # Ruby: http://qiita.com/ynakayama/items/388c82cbe14c65827769
  # Python:
  # - http://tseiya.hatenablog.com/entry/2012/09/19/191114
  # - http://yukihir0.hatenablog.jp/entry/20110201/1296565687
  return -min(36000, int(400*size**1.5))

def costofrole(role):
  """
  @param  role  unicode
  @return  int  negative  the smaller the more important
  """
  if 'pn' in role: # pronoun is more important
    return -1
  if 'ctr' in role: # counter, less happen
    return 2
  if 'suf' in role: # suffix, less happen
    return 1
  return 0

# Example  きす,5131,5131,887,名詞,普通名詞,サ変可能,*,*,*,キス,キス-kiss,キス,キス,キス,キス,外,*,*,*,*
UNIDIC_FMT = '{surf},0,0,{cost},{roles},{kata},{source},{surf},*,*,*,{content},*,{trans},{id},{type}\n'

# 名詞,普通名詞,一般,*,*,*,ゴメン,御免,御免,ゴメン,御免,ゴメン,漢,*,*,*,*,ゴメン,ゴメン,ゴメン,ゴメン,*,*,0,C2,*
# 動詞,非自立可能,*,*,五段-ラ行,命令形,ナサル,為さる,なさい,ナサイ,なさる,ナサル,和,*,*,*,*,ナサイ,ナサル,ナサイ,ナサル,*,*,2,C1,*
ROLE_COUNT = 6
ROLE_UNKNOWN = '*'
def assemble(entries, fmt=UNIDIC_FMT, id=None, roles=None, type=None, trans=None, surfacefilter=None):
  """
  @param  id  long  sql role id
  @param  entries  [unicode surface, unicode reading]
  @param* fmt  unicode
  @param* trans  unicode  translation of the entries
  @param* roles  list
  @param* surfacefilter  unicode -> bool  whether keep certain surface
  @yield  unicode
  """
  if roles is None:
    roles = ['*'] * ROLE_COUNT
  elif len(roles) > ROLE_COUNT:
    roles = roles[:ROLE_COUNT]
  else:
    while len(roles) < ROLE_COUNT:
      roles.append(ROLE_UNKNOWN)
  roles = ','.join(roles)
  kwargs = {
    'type': type or ROLE_UNKNOWN,
    'id': id or ROLE_UNKNOWN,
    'trans': trans or ROLE_UNKNOWN,
    'source': ROLE_UNKNOWN, # not implemented supposed to be original chinese/english definition
    'roles': roles,
  }
  surfaces = set()
  rolecost = costofrole(roles)
  for surf, yomi in entries:
    if ',' not in surf and surf not in surfaces:
      surfaces.add(surf)
      if not surfacefilter or surfacefilter(surf):
        hira = kata2hira(yomi) if yomi else ''
        kata = hira2kata(yomi) if yomi else ''
        content = surf
        cost = costofsize(len(surf)) + rolecost
        yield fmt.format(surf=surf, kata=kata, cost=cost, content=content, **kwargs)
        for kana in (yomi, hira, kata):
          if kana and kana not in surfaces:
            surfaces.add(kana)
            if not surfacefilter or surfacefilter(kana):
              cost = costofsize(len(kana)) + rolecost
              yield fmt.format(surf=kana, kata=kata, cost=cost, content=content, **kwargs)

MIN_CSV_SIZE = 10 # minimum CSV file size
def compile(dic, csv, exe='mecab-dict-index', dicdir='', call=subprocess.call):
  """csv2dic. This process would take several seconds
  @param  dic  unicode  path
  @param  csv  unicode  path
  @param* exe  unicode  path
  @param* dicdir  unicode
  @param* call  launcher function
  @return  bool
  """
  # MeCab would crash for empty sized csv
  if skfileio.filesize(csv) < MIN_CSV_SIZE:
    dwarn("insufficient input csv size", csv)
    return False
  args = [
    exe,
    '-f', 'utf8', # from utf8
    '-t', 'utf8', # to utf8
    '-u', dic,
    csv,
  ]
  if dicdir:
    args.extend((
      '-d', dicdir
    ))
  return call(args) in (0, True) and os.path.exists(dic)

if __name__ == '__main__':
  from sakurakit.skprof import SkProfiler

  os.environ['PATH'] += os.path.pathsep + '../../../../MeCab/bin'

  csvpath = 'edict.csv'

  def test_assemble():
    with SkProfiler("assemble"):
      #dbpath = '../dictp/edict.db'
      dbpath = '/Users/jichi/stream/Caches/Dictionaries/EDICT/edict.db'
      import mdedict
      mdedict.db2csv(csvpath, dbpath)

  def test_compile():
    with SkProfiler("compile"):
      dicdir = "../../../../../../Caches/Dictionaries/UniDic"
      #dicdir = "/opt/local/lib/mecab/dic/unidic-utf8"
      print compile('edict.dic', csvpath, dicdir=dicdir)
      #print compile('test.dic', 'test.csv', dicdir=dicdir)

  test_assemble()
  test_compile()

# EOF
