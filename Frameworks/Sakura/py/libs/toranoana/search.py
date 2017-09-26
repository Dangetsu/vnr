# coding: utf8
# search.py
# 9/28/2014 jichi

__all__ = 'SearchApi',

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import re
from sakurakit import sknetio
#from sakurakit.skdebug import dwarn
from sakurakit.skstr import unescapehtml, urlencode
from article import clean_title

DEFAULT_HOST = "http://www.toranoana.jp"
_QUERY_PATH = "/cgi-bin/R2/allsearch.cgi"

def resethost():
  sethost(DEFAULT_HOST)
def sethost(url):
  api = SearchApi
  api.HOST = url
  api.API = api.HOST + _QUERY_PATH

class SearchApi(object):
  HOST = DEFAULT_HOST
  API = HOST + _QUERY_PATH

  ENCODING = 'sjis'
  COOKIES = {'afg':'0'}

  session = None # requests.Session or None

  PCGAME_KIND = 2103
  DOUJIN_KIND = 0401
  KINDS = PCGAME_KIND, DOUJIN_KIND

  def _makereq(self, **kwargs):
    """
    @return  kw
    """
    return {'url':self.API, 'data':kwargs}

  def _fetch(self, url, data):
    """
    @param  url  str
    @return  str
    """
    return sknetio.postdata(url, data=data, gzip=True, session=self.session, cookies=self.COOKIES)

  def query(self, text, kind=KINDS[0], otome=False, **kwargs):
    """
    @param  text  str
    @param  kind  str
    @param  otome  bool
    @yield  {kw} or None
    """
    text = text.encode(self.ENCODING, errors='ignore')
    if text:
      req = self._makereq(
          search=text,
          item_kind=kind,
          bl_fg=1 if otome else 0,
          #obj=0, # 男性向／女性向: 0=both, 1=m, 2=f
          #adl=0, # 一般／18禁: 0=both, 1=15, 2=18
          **kwargs)
      h = self._fetch(**req)
      if h:
        h = h.decode(self.ENCODING, errors='ignore')
        if h:
          return self._iterparse(h)

  # Example:
  # http://www.getchu.com/php/nsearch.phtml?genre=all&search_keyword=レミニセンス
  #
  # <A HREF="../soft.phtml?id=718587" class="blueb">レミニセンス 初回限定版</A><a href="https://order.zams.biz/comike/mypage/af_wish_list.phtml?action=add&id=718587" title="お気に入りに追加"><img class="lazy" src="/common/images/space.gif" data-original="/common/images/favorite.gif" class="favorite"></a><a href="/php/nsearch.phtml?search_reference_id=718587" title="この商品の関連を開く"><img class="lazy" src="/common/images/space.gif" data-original="/common/images/relation.gif" class="relation"></a>
  # </TD></TR>
  # <TR><TD align="left" valign="top" width="100%" style="line-height:1.35;">
  # <p><span class="orangeb">[PCゲーム・アダルト]</span><br>
  # 発売日：2013/05/31<!--発売日--><BR>
  # ブランド名： <A href="http://www.tigresoft.com/" class="blue" target="_blank" >てぃ～ぐる</A><!--BRAND--><BR>
  # メディア： DVD-ROM<!--MEDIA--><BR>
  # 定価： 税込￥9,240(税抜￥8,800)<!--PRICE--></p>
  # <p>
  # 価格：<SPAN class="redb">￥6,980</SPAN><SPAN class="black">　コムポイント：209</SPAN>
  # </p>
  #
  _rx_parse = re.compile(
    #r'class="work_border"'
    r'<td class="c0"'
    r'.*?'
    r'<td class="c7"'
  , re.DOTALL)

  # Example:
  # <td class="c1">
  #   <a href="/mailorder/article/21/0006/53/25/210006532528.html">(PC)レミニセンス 初回限定版</a>
  # </td>
  _rx_url_title = re.compile(r"\s*?".join((
    r'td class="c1">',
    r'<a href="([^"]+?)">([^<]+?)<',
  )), re.DOTALL)

  # <td class="c0">
  #   <a href="/mailorder/article/21/0006/54/35/210006543567.html">
  #     <img src=http://img.toranoana.jp/img18/21/0006/54/35/210006543567-1r.jpg border="1" alt="(PC)レミニセンス Re:collect"  height="40">
  #   </a>
  # </td>
  _rx_img = re.compile(r"\s*?".join((
    r'td class="c0">',
    r'<a [^>]*>',
    r'<img src=(\S+)', # no quotes surrounding image
  )), re.DOTALL)

  _rx_brand = re.compile(r"\s*?".join((
    r'td class="c3">',
    r'<a [^>]*>([^<]+?)<',
  )), re.DOTALL)

  # Example: <td class="c4" align="right" nowrap>7,920円(+税)</td>
  _rx_price = re.compile(ur'td class="c4"[^>]*?>([0-9,]+)円')

  def _iterparse(self, h):
    """
    @param  h  unicode
    @yield  {kw}
    """
    for m in self._rx_parse.finditer(h):
      hh = m.group()
      mm = self._rx_url_title.search(hh)
      if mm:
        url = mm.group(1)
        title = clean_title(unescapehtml(mm.group(2)))

        id = self._parseurlid(url)
        path = self._parseurlpath(url)
        if id and path:

          mm = self._rx_brand.search(hh)
          brand = unescapehtml(mm.group(1)) if mm else None

          mm = self._rx_img.search(hh)
          img = mm.group(1).replace('r.jpg', '.jpg') if mm else None

          mm = self._rx_price.search(hh)
          try: price = int(mm.group(1).replace(',', ''))
          except: price = 0

          yield {
            'url': "http://www.toranoana.jp" + url,     # str not None
            'id': id,
            'title': title, # unicode not None
            'image': img, # str or None
            'brand': brand, # unicode or None
            'price': price, # int not None
          }

  _rx_url_id = re.compile(r"/([0-9]+)\.html")
  def _parseurlid(self, url):
    """
    @param  str
    @return  str
    """
    m = self._rx_url_id.search(url)
    if m:
      return m.group(1)

  _rx_url_path = re.compile(r"/article/(.+)/[0-9]+\.html")
  def _parseurlpath(self, url):
    """
    @param  str
    @return  str or None
    """
    m = self._rx_url_path.search(url)
    if m:
      return m.group(1)

if __name__ == '__main__':
  api = SearchApi()
  t = u"レミニセンス"
  for it in api.query(t):
    print '-' * 10
    for k,v in it.iteritems():
      print k, ':', v

# EOF
