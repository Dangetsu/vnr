# coding: utf8
# caching.py
# 8/12/2013 jichi

__all__ = 'CachingGameTableApi', 'CachingReviewTableApi'

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

from restful.offline import DataCacher
from api import GameTableApi, ReviewTableApi

CachingGameTableApi = DataCacher(GameTableApi, suffix='.html')
CachingReviewTableApi = DataCacher(ReviewTableApi, suffix='.html')

if __name__ == '__main__':
  api = CachingGameApi("s:/tmp/scape", expiretime=86400)
  t = 15986
  q = api.query(t)
  print q

# EOF
