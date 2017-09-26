# coding: utf8
# caching.py
# 8/12/2013 jichi

__all__ = 'CachingRestApi', 'CachingSoftApi'

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

from restful.offline import DataCacher, FileCacher
from rest import RestApi
from soft import SoftApi

CachingSoftApi = DataCacher(SoftApi, suffix='.html')
CachingRestApi = FileCacher(RestApi, suffix='.json')

if __name__ == '__main__':
  api = CachingRestApi("s:/tmp/trailers", expiretime=86400)
  t = u"レミニセンス"
  q = api.query(t)
  print q

  t = 9610
  q = api.query(t, type=api.EROGETRAILERS_TYPE)
  print q

  api = CachingSoftApi("s:/tmp/trailers", expiretime=86400)
  k = 3424
  k = 9869
  q = api.query(k)
  for k,v in q.iteritems():
    print k, ':', v

# EOF
