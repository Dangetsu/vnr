# coding: utf8
# caching.py
# 8/12/2013 jichi

__all__ = 'CachingSoftApi', 'CachingReviewApi'

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

#from search import SearchApi
from soft import SoftApi
from review import ReviewApi

def _htmlcacher(cls):
  from restful.offline import DataCacher
  return DataCacher(cls, suffix='.html')

#CachingSearchApi = _htmlcacher(SearchApi)
CachingSoftApi = _htmlcacher(SoftApi)
CachingReviewApi = _htmlcacher(ReviewApi)

if __name__ == '__main__':
  cachedir = 'tmp'
  api = CachingSoftApi(cachedir=cachedir, expiretime=86400)
  k = 748164
  k = 779363
  q = api.query(k)
  print q['title']
  print q['price']
  print q['date']
  #for k,v in q.iteritems():
  #  print k, ':', v

# EOF
