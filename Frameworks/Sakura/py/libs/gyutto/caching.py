# coding: utf8
# caching.py
# 11/28/2013 jichi

__all__ = 'CachingBuyApi', 'CachingItemApi', 'CachingReviewApi'

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

#from search import SearchApi
from buy import BuyApi
from item import ItemApi
from review import ReviewApi

def _htmlcacher(cls):
  from restful.offline import DataCacher
  return DataCacher(cls, suffix='.html')

#CachingSearchApi =_htmlcacher(SearchApi)
CachingBuyApi = _htmlcacher(BuyApi)
CachingItemApi = _htmlcacher(ItemApi)
CachingReviewApi = _htmlcacher(ReviewApi)

if __name__ == '__main__':
  from search import SearchApi
  CachingSearchApi =_htmlcacher(SearchApi)

  cachedir = 'tmp'
  api = CachingSearchApi(cachedir=cachedir, expiretime=86400)
  #k = 45242
  #k = 16775
  #q = api.query(k)
  #print q['title']
  #print q['image']
  #print q['brand']
  #print q['date']
  #print q['filesize']
  #for it in q['tags']:
  #  print it
  ##for k,v in q.iteritems():
  ##  print k, ':', v

  t = u"ランス"
  for it in api.query(t): # reverse order
    #print '-' * 10
    for k,v in it.iteritems():
      print k, ':', v

# EOF
