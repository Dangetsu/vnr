# coding: utf8
# tag.py
# 11/16/2013 jichi
#
# See: dmmPartsRequest in http://www.dmm.co.jp/js/parts_request.js

__all__ = 'TagApi',

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import re
from sakurakit import sknetio, skstr
from sakurakit.skdebug import dwarn

class TagApi(object):
  HOST = "http://www.dmm.co.jp/"
  API = HOST + "tag/-/view/ajax-index?content_id=%s"
  #ENCODING = 'utf8'

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
    return sknetio.getdata(url, gzip=True, session=self.session)

  # Example:
  # http://www.dmm.co.jp/tag/-/view/ajax-index?content_id=waffle_0053
  #
  #<ul class="taglist">
  #    <li><a href="/search/=/opt=AQpVQBFZE1ZVX5TtlpfDxMTak46RhV6c3ceHx*RARJGyQR0ZTpPZl9vAwp3YgriTgUw_/sort=ranking/">ファンタジー</a></li>
  #    <li><a href="/search/=/opt=AQpVQBFZE1ZVX5TplpLDjcSPDJOPnNSYtEdEx*VFGhBNxIichZOSl9PR75zTHw__/sort=ranking/">パイズリ</a></li>
  #    <li><a href="/search/=/opt=AQpVQBFZE1ZVX5T3korD28SFDJOPnNSYtEdEx*VFGhBNxIichZOSl9PR75zTHw__/sort=ranking/">ハーレム</a></li>
  #    <li><a href="/search/=/opt=AQpVQBFZE1ZVX4HE,sZckt7AhpfmHBeYtUIaRhrAj5WGxMOcjYK,lthM/sort=ranking/">淫乱</a></li>
  #    <li><a href="/search/=/opt=AQpVQBFZE1ZVX5TtlpHD9lvAiZOAmLIcEcPgRh9FH5XdxNOclZOKhubB0RE_/sort=ranking/">フェチ</a></li>
  #    <li><a href="/search/=/opt=AQpVQBFZE1ZVX,,Ag5Bckt7AhpfmHBeYtUIaRhrAj5WGxMOcjYK,lthM/sort=ranking/">恋愛</a></li>
  #    <li><a href="/search/=/opt=AQpVQBFZE1ZVX4zPgZCr*lvAiZOAmLIcEcPgRh9FH5XdxNOclZOKhubB0RE_/sort=ranking/">女王様</a></li>
  #    <li><a href="/search/=/opt=AQpVQBFZE1ZVX5WS*oer*lvAiZOAmLIcEcPgRh9FH5XdxNOclZOKhubB0RE_/sort=ranking/">お姫様</a></li>
  #</ul>
  def query(self, id):
    """
    @param  id  str  content_id
    @return  [unicode] or None
    """
    url = self._makeurl(id)
    h = self._fetch(url)
    if h:
      #h = h.decode(self.ENCODING, errors='ignore')
      return self._parse(h)

  def _parse(self, h):
    """
    @param  h  unicode  html
    @return  [unicode]
    """
    return list(self._iterparse(h))

  _rx_tag = re.compile(r"([^>]+)</a></li>")
  def _iterparse(self, h):
    """
    @param  h  unicode  html
    @yield  str
    """
    for m in self._rx_tag.finditer(h):
      yield m.group(1)

if __name__ == '__main__':
  api = TagApi()
  cid = 'waffle_0053'
  print '-' * 10
  q = api.query(cid)
  print q[0]

# EOF
