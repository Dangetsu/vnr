# coding: utf8
# title.py
# 6/20/2013 jichi

__all__ = 'TitleApi',

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import re
from sakurakit import sknetio, skstr
from sakurakit.skdebug import dwarn

class TitleApi(object):
  HOST = "http://erogame-tokuten.com"
  API = HOST + "/title.php?title_id=%s"
  ENCODING = 'utf8'

  session = None # requests.Session or None

  def _makereq(self, id):
    """
    @param  kw
    @return  kw
    """
    return {'url':self._makeurl(id)}

  def _makeurl(self, id):
    """
    @param  id  int
    @return  str
    """
    return self.API % id

  def _fetch(self, url):
    """
    @param  url  str
    @return  str
    """
    # Disable redirects for gyutto items
    return sknetio.getdata(url, gzip=True, session=self.session)

  def query(self, id=None):
    """
    @param  id  str or int  softId
    @return  {kw} or None
    """
    url = self._makeurl(id)
    h = self._fetch(url)
    if h:
      h = h.decode(self.ENCODING, errors='ignore')
      if h: # and u'エラーが発生しました。' not in h:
        ret = self._parse(h, id)
        if ret:
          ret['id'] = long(id)
          ret['url'] = url
          return ret

  def _parse(self, h, id):
    """
    @param  h  unicode  html
    @param  int  id
    @return  {kw}
    """
    return {'images': self._iterparseimages(h, id)}


  def _iterparseimages(self, h, id):
    """
    @param  h  unicode  html
    @yield  unicode or None
    """
    rx = re.compile(r"/title/%s/\d+.jpg" % id)
    for m in rx.finditer(h):
      yield self.HOST + m.group()

if __name__ == '__main__':
  api = TitleApi()
  k = 1287 # レミニセンス, http://erogame-tokuten.com/title.php?title_id=1287

  print '-' * 10
  q = api.query(k)
  for it in q['images']:
    print it

# EOF
