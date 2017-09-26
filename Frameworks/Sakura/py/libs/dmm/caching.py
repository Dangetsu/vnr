# coding: utf8
# caching.py
# 7/25/2013 jichi

__all__ = 'CachingRestApi',
if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

from time import time
from hashlib import md5 # pylint: disable-msg=E0611
import restful.offline
from rest import RestApi
from game import GameApi
from tag import TagApi

def _htmlcacher(cls):
  from restful.offline import DataCacher
  return DataCacher(cls, suffix='.html')

CachingGameApi = _htmlcacher(GameApi)
CachingTagApi = _htmlcacher(TagApi)

class RestCacherBase(restful.offline.CacherBase):
  def __init__(self, *args, **kwargs):
    super(RestCacherBase, self).__init__(*args, **kwargs)

  def _digest(self, expire, url):
    """@reimp
    @param  expire  bool
    @param  url  str
    @return  str
    Calculate hash value for request based on URL.
    """
    url = '&'.join(sorted((# Sort to make it unique
      it for it in url.split('&') if it and not it.startswith('timestamp'))))
    if expire and self.expiretime:
      now = int(time())
      url += '&__expire=' + str(now/self.expiretime)
    return md5(url).hexdigest()

CachingRestApi = restful.offline.FileCacher(RestApi, Base=RestCacherBase, suffix='.xml')

if __name__ == '__main__':
  cachedir = "s:/tmp/dmm"
  cachedir = 'tmp'

  api = CachingTagApi(expiretime=86400, cachedir=cachedir)
  cid = 'waffle_0053'
  print '-' * 10
  q = api.query(cid)
  print q[0]

  dmm = CachingRestApi(api_id='ezuc1BvgM0f74KV4ZMmS', affiliate_id='sakuradite-999',
      cachedir=cachedir, expiretime=86400)
  t = '1653apc10393'
  t = u"幻創のイデア "
  t = u"神咒神威神楽"
  t = u"528lih5035" # product_id
  t = u"000_029pcg" # content_id
  # https://affiliate.dmm.com/api/reference/com/iroiro/
  for item in dmm.query(t, hits=20):
    for it in item:
      print it.tag, it.text

# EOF
