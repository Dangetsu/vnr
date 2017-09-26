# coding: utf8
# search.py
# 8/4/2013 jichi

__all__ = 'SearchApi',

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import re
from sakurakit import sknetio
#from sakurakit.skdebug import dwarn
from sakurakit.skstr import unescapehtml

DEFAULT_HOST = "http://www.getchu.com"
_QUERY_PATH = "/php/search.phtml"

def resethost():
  sethost(DEFAULT_HOST)
def sethost(url):
  api = SearchApi
  api.HOST = url
  api.API = api.HOST + _QUERY_PATH

class SearchApi(object):
  HOST = DEFAULT_HOST
  API = HOST + _QUERY_PATH  # contains picture
  #API = HOST + "/php/nsearch.phtml" # no picture

  ENCODING = 'euc-jp'
  #COOKIES = {'getchu_adalt_flag': 'getchu.com'}

  #GENRES = 'all', 'pc_soft', 'doujin', 'all_lady'
  PC_GAME_GENRES = 'pc_soft', 'doujin', 'all_lady'

  session = None # requests.Session or None

  def _makereq(self, text, genre, sort, sort2):
    """
    @param  text  str
    @param  genre  str
    @param  sort  str
    @param  sort2  str
    @return  kw
    """
    text = text.encode(self.ENCODING, errors='ignore')
    return {'search_keyword':text, 'genre':genre, 'sort':sort, 'sort2':sort2}

  def _fetch(self, **params):
    """
    @param  params  kw
    @return  str
    """
    return sknetio.getdata(self.API, gzip=True, params=params, session=self.session) #, cookies=self.COOKIES)

  def query(self, text, genre='all', sort='release_date', sort2='down'):
    """
    @param  id  str or int  softId
    @param  genre  str  such as 'all', 'pc_soft', 'doujin', 'all_lady'
    @param  sort  str  such as 'release_date'
    @param  sort2  str  such as 'up' or 'down'
    @yield  {kw} or None
    """
    req = self._makereq(text, genre=genre, sort=sort, sort2=sort2)
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
    r'/soft.phtml\?id=([0-9]+?)" class="blueb">([^<]+?)</A>'
    r'.*?'
    r'<!--PRICE-->'
  , re.IGNORECASE|re.DOTALL)
  _rx_price = re.compile(ur'定価：\s*￥([0-9,]+)')
  _rx_brand = re.compile(ur'ブランド名：(.*?)<!--BRAND-->')
  _rx_brand2 = re.compile(r'>([^<]+)<')
  def _iterparse(self, h):
    """
    @param  h  unicode
    @yield  {kw}
    """
    for m in self._rx_parse.finditer(h):
      key = m.group(1)
      title = m.group(2)
      if key and title:
        url = "http://getchu.com/soft.phtml?id=%s" % key
        img = '/brandnew/%s/c%spackage' % (key, key)
        img = self.HOST + img + '.jpg' if img in h else ''

        item = {
          'id': key,
          'url': url,
          'img': img,
          'title': unescapehtml(title),
        }

        hh = m.group()

        mm = self._rx_price.search(hh)
        try: item['price'] = int(mm.group(1).replace(',', ''))
        except: item['price'] = 0

        mm = self._rx_brand.search(hh)
        brand = mm.group(1) if mm else ''
        if brand:
          mm = self._rx_brand2.search(brand)
          if mm:
            brand = mm.group(1)
        item['brand'] = unescapehtml(brand).strip() if brand else '' # strip

        item.update(self._iterparsefields(hh))
        yield item

  _rx_fields = (
    ('date', re.compile(ur'発売日：([0-9/]+)<!--発売日-->')),
    ('media', re.compile(ur'メディア：([^<]+?)<!--MEDIA-->')),
  )
  def _iterparsefields(self, h):
    """
    @param  h  unicode
    @yield  (str key, unicode or None)
    """
    for k,rx in self._rx_fields:
      m = rx.search(h)
      if m:
        yield k, unescapehtml(m.group(1)).strip()

if __name__ == '__main__':
  api = SearchApi()
  t = u"幻創のイデア"
  t = 'id=718587'
  t = u"暁の護衛"
  t = u"レミニセンス"
  genre = 'all_lady'
  genre = 'doujin'
  genre = 'pc_soft'
  for it in api.query(t, genre=genre, sort2='down'): # reverse order
    print '-' * 10
    for k,v in it.iteritems():
      print k, ':', v

# EOF
