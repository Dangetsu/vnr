# coding: utf8
# caching.py
# 11/26/2013 jichi

__all__ = 'CachingSearchApi', 'CachingWorkApi'

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

from search import SearchApi
from work import WorkApi

def _htmlcacher(cls):
  from restful.offline import DataCacher
  return DataCacher(cls, suffix='.html')

CachingSearchApi = _htmlcacher(SearchApi)
CachingWorkApi = _htmlcacher(WorkApi)

if __name__ == '__main__':
  cachedir = 'tmp'
  api = CachingWorkApi(cachedir=cachedir, expiretime=86400)
  url = 'http://www.dlsite.com/home/work/=/product_id/RJ125584.html'
  q = api.query(url)
  print q['title']
  print q['price']
  print q['date']
  #for k,v in q.iteritems():
  #  print k, ':', v

# EOF
