# coding: utf8
# caching.py
# 9/27/2014 jichi

__all__ = 'CachingArticleApi',

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

#from search import SearchApi
from article import ArticleApi

def _htmlcacher(cls):
  from restful.offline import DataCacher
  return DataCacher(cls, suffix='.html')

#CachingSearchApi = _htmlcacher(SearchApi) # Search with post cannot be cached
CachingArticleApi = _htmlcacher(ArticleApi)

if __name__ == '__main__':
  cachedir = 'tmp'
  api = CachingArticleApi(cachedir=cachedir, expiretime=86400)
  url = "http://www.toranoana.jp/mailorder/article/21/0006/54/35/210006543567.html"
  q = api.query(url)
  print q['title']
  print q['price']
  print q['date']
  #for k,v in q.iteritems():
  #  print k, ':', v

# EOF
