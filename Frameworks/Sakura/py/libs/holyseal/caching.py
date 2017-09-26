# coding: utf8
# caching.py
# 4/9/2014 jichi

__all__ = 'CachingProductApi',

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

from restful.offline import DataCacher
from product import ProductApi
#from search import SearchApi

def _htmlcacher(cls):
  from restful.offline import DataCacher
  return DataCacher(cls, suffix='.html')

CachingProductApi = _htmlcacher(ProductApi)
#CachingSearchApi = _htmlcacher(SearchApi)

if __name__ == '__main__':
  api = CachingProductApi("s:/tmp/holyseal", expiretime=86400)
  k = 9550 # http://holyseal.net/cgi-bin/mlistview.cgi?prdcode=9550
  q = api.query(k)
  for k,v in q.iteritems():
    print k, ':', v

# EOF
