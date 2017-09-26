# coding: utf8
# caching.py
# 11/28/2013 jichi

__all__ = 'CachingTitleApi',

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

#from search import SearchApi
from title import TitleApi

def _htmlcacher(cls):
  from restful.offline import DataCacher
  return DataCacher(cls, suffix='.html')

#CachingSearchApi =_htmlcacher(SearchApi)
CachingTitleApi =_htmlcacher(TitleApi)

if __name__ == '__main__':
  cachedir = 'tmp'
  api = CachingSearchApi(cachedir=cachedir, expiretime=86400)

  k = 1287
  for it in api.query(t):
    for k,v in it.iteritems():
      print k, ':', v

# EOF
