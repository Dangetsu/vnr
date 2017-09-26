# coding: utf8
# caching.py
# 8/12/2013 jichi

__all__ = 'CachingGameApi',

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

#from search import SearchApi
from game import GameApi

def _htmlcacher(cls):
  from restful.offline import DataCacher
  return DataCacher(cls, suffix='.html')

#CachingSearchApi = _htmlcacher(SearchApi)
CachingGameApi = _htmlcacher(GameApi)

if __name__ == '__main__':
  cachedir = 'tmp'
  api = CachingGameApi(cachedir=cachedir, expiretime=86400)
  k = 8329 # http://www.freem.ne.jp/win/game/8329
  k = 3055 # http://www.freem.ne.jp/win/game/3055
  k = 7190 # http://www.freem.ne.jp/win/game/7190
  q = api.query(k)
  print q['title']
  print q['date']
  #for k,v in q.iteritems():
  #  print k, ':', v

# EOF
