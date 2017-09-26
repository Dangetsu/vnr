# coding: utf8
# product.py
# 4/9/2014 jichi

__all__ = 'ProductApi',

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import re
from sakurakit import sknetio
from sakurakit.skstr import unescapehtml

class ProductApi(object):

  QUERY_HOST = "http://holyseal.net"
  #QUERY_HOST = "http://holyseal.homeip.net"
  QUERY_PATH = "/cgi-bin/mlistview.cgi?prdcode=%s"
  API = QUERY_HOST + QUERY_PATH
  ENCODING = 'sjis'

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

  def query(self, id):
    """
    @param  id  str or int  prdcode
    @return  {kw} or None
    """
    url = self._makeurl(id)
    h = self._fetch(url)
    if h:
      h = h.decode(self.ENCODING, errors='ignore')
      if h and u'≫  ≫ </title>' not in h: # empty page
        ret = self._parse(h)
        if ret:
          ret['id'] = long(id)
          url = "http://holyseal.net/cgi-bin/mlistview.cgi?prdcode=%s" % id # reset url
          ret['url'] = url
          return ret

  def _parse(self, h):
    """
    @param  h  unicode  html
    @return  {kw}
    """
    return {
      'title': self._parsetitle(h),     # unicode
      'brand': self._parsebrand(h),     # unicode
      'banner': self._parsebanner(h),   # str url or None
      'ecchi': self._parseecchi(h),     # bool
      'otome': self._parseotome(h),     # bool
      'date': self._parsedate(h),       # str or None  such as 2013/08/23, or 2014/夏
      'genre': self._parsegenre(h),     # unicode or None  slogan
      'artists': list(self._iterparseartists(h)), # [unicode]
      'writers': list(self._iterparsewriters(h)), # [unicode]
    }

  # u"td>15 歳以上" or u"td>18 歳以上"
  def _parseecchi(self, h):
    """
    @param  h  unicode  html
    @return  bool
    """
    return u">15 歳以上" not in h
    #return u">18 歳以上" in h

  def _parseotome(self, h):
    """
    @param  h  unicode  html
    @return  bool
    """
    return u"女性向</td>" in h

  # <title>[Holyseal ～聖封～] ミラー／転載 ≫ CUBE ≫ your diary</title>
  _rx_title = re.compile(ur'≫([^≫<]*?)</title>')
  def _parsetitle(self, h):
    """
    @param  h  unicode  html
    @return  unicode or None
    """
    m = self._rx_title.search(h)
    if m:
      return unescapehtml(m.group(1)).strip() # there is a space in the beginning

  # <title>[Holyseal ～聖封～] ミラー／転載 ≫ CUBE ≫ your diary</title>
  _rx_brand = re.compile(ur' ≫ ([^≫<]*?) ≫ ')
  def _parsebrand(self, h):
    """
    @param  h  unicode  html
    @return  unicode or None
    """
    m = self._rx_brand.search(h)
    if m:
      return unescapehtml(m.group(1)).strip() # there is a space in the beginning

  # The height is always 550
  # <p align="center"><img src="http://www.cuffs-cube.jp/products/yourdiary_h/download/banner/bn_600x160_kanade.jpg" width="550" height="146" border="0" alt=""></p>
  _rx_banner = re.compile(r'<p align="center"><img src="(.*?)" width="550"')
  def _parsebanner(self, h):
    """
    @param  h  unicode  html
    @return  unicode or None
    """
    m = self._rx_banner.search(h)
    if m:
      return unescapehtml(m.group(1))

  # Example:
  # <tr class="minfo">
  #  <th class="idx" width="55">発売日</th>
  #  <td colspan="2" width="495">2013/08/23</td>
  # </tr>
  def __makeinforx(key):
    pat = r'\s*'.join((
      r'<tr class="minfo">',
      r'<th [^>]*>%s</th>' % key,
      r'<td [^>]*>(.*?)</td>',
    ))
    return re.compile(pat, re.DOTALL)

  _rx_info_genre = __makeinforx(u"ジャンル")
  def _parsegenre(self, h):
    """
    @param  h  unicode  html
    @return  unicode or None
    """
    m = self._rx_info_genre.search(h)
    if m:
      return unescapehtml(m.group(1))

  _rx_info_date = __makeinforx(u"発売日")
  def _parsedate(self, h):
    """
    @param  h  unicode  html
    @return  unicode or None
    """
    m = self._rx_info_date.search(h)
    if m:
      ret = unescapehtml(m.group(1))
      if ret != '----/--/--':
        return ret

  # Such as: <a href="staffview.cgi?staffcode=2508&amp;refpc=9550">鈴田美夜子</a>
  _rx_staff = re.compile(ur">([^<]*?)</a>")

  _rx_info_artists = __makeinforx(u"原画")
  def _iterparseartists(self, h):
    """
    @param  h  unicode  html
    @yield  unicode
    """
    m = self._rx_info_artists.search(h)
    if m:
      line = unescapehtml(m.group(1))
      for m in self._rx_staff.finditer(line):
        yield unescapehtml(m.group(1))

  _rx_info_writers = __makeinforx(u"シナリオ")
  def _iterparsewriters(self, h):
    """
    @param  h  unicode  html
    @yield  unicode
    """
    m = self._rx_info_writers.search(h)
    if m:
      line = unescapehtml(m.group(1))
      for m in self._rx_staff.finditer(line):
        yield unescapehtml(m.group(1))

if __name__ == '__main__':
  api = ProductApi()
  k = 12517 # http://holyseal.net/cgi-bin/mlistview.cgi?prdcode=12517
  k = 1234567 # wrong
  k = 9550
  k = 12942
  q = api.query(k)
  print q['title']
  print q['brand']
  print q['banner']
  print q['ecchi']
  print q['date']
  print q['genre']
  print q['otome']
  #print q['artists']
  for it in q['artists']:
    print it

# EOF
