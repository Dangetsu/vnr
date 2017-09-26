# coding: utf8
# caching.py
# 8/12/2013 jichi

__all__ = 'CachingAppApi'

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

#from search import SearchApi
from app import AppApi

def _htmlcacher(cls):
  from restful.offline import DataCacher
  return DataCacher(cls, suffix='.html')

#CachingSearchApi = _htmlcacher(SearchApi)
CachingAppApi = _htmlcacher(AppApi)

if __name__ == '__main__':
  cachedir = 'tmp'
  api = CachingAppApi(cachedir=cachedir, expiretime=86400)
  k = 282900
  q = api.query(k)
  print q['title']
  print q['price']
  print q['date']
  #for k,v in q.iteritems():
  #  print k, ':', v

# EOF
