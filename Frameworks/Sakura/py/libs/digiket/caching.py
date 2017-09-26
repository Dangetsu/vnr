# coding: utf8
# caching.py
# 8/12/2013 jichi

__all__ = 'CachingItemApi',

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

from item import ItemApi
#from search import SearchApi

def _htmlcacher(cls):
  from restful.offline import DataCacher
  return DataCacher(cls, suffix='.html')

CachingItemApi = _htmlcacher(ItemApi)
#CachingSearchApi = _htmlcacher(SearchApi)

if __name__ == '__main__':
  cachedir = 'tmp'
  api = CachingItemApi(cachedir=cachedir, expiretime=86400)
  k = 'ITM0080219'
  q = api.query(k)
  print q['title']
  print q['price']
  print q['date']
  #for k,v in q.iteritems():
  #  print k, ':', v

# EOF
