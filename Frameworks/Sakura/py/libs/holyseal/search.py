# coding: utf8
# search.py
# 6/18/2014 jichi

__all__ = 'SearchApi',

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import re
from sakurakit import sknetio
from sakurakit.skdebug import dwarn
from sakurakit.skstr import unescapehtml

class SearchApi(object):

  QUERY_HOST = "http://holyseal.net"
  #QUERY_HOST = "http://holyseal.homeip.net"
  QUERY_PATH = "/cgi-bin/mlistview.cgi?word=%s"
  API = QUERY_HOST + QUERY_PATH
  ENCODING = 'sjis'

  session = None # requests.Session or None

  def _makereq(self, text):
    """
    @param  kw
    @return  kw
    """
    return {'url':self._makeurl(text)}

  def _makeurl(self, text):
    """
    @param  text  unicode
    @return  unicode
    """
    return self.API % text

  def _fetch(self, url):
    """
    @param  url  str
    @return  str
    """
    return sknetio.getdata(url, gzip=True, session=self.session)

  def query(self, text):
    """
    @param  text  unicode
    @return  {kw} or None
    """
    #text = text.encode(self.ENCODING, errors='ignore')
    text = sknetio.topercentencoding(text, encoding=self.ENCODING)
    if text:
      url = self._makeurl(text)
      h = self._fetch(url)
      if h:
        h = h.decode(self.ENCODING, errors='ignore')
        if h:
          return self._iterparse(h)

  # Example:  http://holyseal.net/cgi-bin/mlistview.cgi?word=dive
  #
  # 検索結果（タイトル）</strong> [<a href="mlistview.cgi?prdcode=10890">消す</a>]</p>
  # <p class="selc"><strong>2012 年</strong></p><p class="sellst3">･<strong>Dolphin Divers</strong></p>
  # <p class="selc"><strong>2010 年</strong></p><p class="sellst1">･<a href="mlistview.cgi?prdcode=9457&amp;word=dive" target="_self"><span class="prd">BALDR SKY DiveX “DREAM WORLD”</span></a></p>
  # <p class="selc"><strong>2009 年</strong></p><p class="sellst1">･<a href="mlistview.cgi?prdcode=8797&amp;word=dive" target="_self"><span class="prd">BALDR SKY Dive2 “RECORDARE”</span></a></p>
  # <p class="sellst1">･<a href="mlistview.cgi?prdcode=7158&amp;word=dive" target="_self"><span class="prd">BALDR SKY Dive1 “LostMemory”</span></a></p>
  # </div><br><div class="fr"><p class="idx"><strong>

  _rx_first_title = re.compile(ur'<p class="sellst3">･<strong>([^<]*?)</strong></p>')
  _rx_first_id = re.compile(ur'prdcode=([0-9]+?)">消す</a>')
  _rx_year = re.compile(ur'<strong>([0-9]{4}) 年</strong>')
  _rx_product = re.compile(r'prdcode=([0-9]+)[^>]*?><span class="prd">([^<]*?)</span>')
  def _iterparse(self, h):
    """
    @param  h  unicode
    @yield  {kw}
    """
    try:
      start = h.find(u"検索結果（タイトル）") # int
      stop = h.find(u"ブランド別製品リスト") # int
      if start > 0 and stop > start:
        hh = h[start:stop]

        years = [] # [int year, int start]
        for m in self._rx_year.finditer(hh):
          years.append((
            int(m.group(1)),
            m.start(),
          ))
        if not years:
          dwarn("cannot find release years, maybe, unknown years")

        id0 = title0 = None

        # first, yield the matched game
        m = self._rx_first_id.search(hh)
        if m:
          id0 = int(m.group(1))
          if id0:
            m = self._rx_first_title.search(hh)
            if m:
              title0 = unescapehtml(m.group(1))

        if id0 and title0:
          year0 = years[0][0] if years else None
          brand0 = self._parsebrand(h)
          yield {
            'id': id0,
            'title': title0,
            'date': self._parsedate(h),
            'brand': brand0,
            'year': year0,
          }

          # then, parse index of years
          # iterparse and compare index against year index
          for m in self._rx_product.finditer(hh):
            id = int(m.group(1))
            title = unescapehtml(m.group(2))
            year = None
            if years:
              for y,start in years:
                if start > m.start():
                  break
                year = y
            yield {
              'id': id,
              'title': title,
              'year': year
            }

    except ValueError: # raised by int()
      dwarn("failed to convert to int")

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

  _rx_info_date = __makeinforx(u"発売日")
  def _parsedate(self, h):
    """
    @param  h  unicode  html
    @return  unicode or None
    """
    m = self._rx_info_date.search(h)
    if m:
      return unescapehtml(m.group(1))

if __name__ == '__main__':
  api = SearchApi()
  k = 'dive' # http://holyseal.net/cgi-bin/mlistview.cgi?word=dive
  k = u'レミニ'
  q = api.query(k)
  if q:
    for it in q:
      print it

# EOF
