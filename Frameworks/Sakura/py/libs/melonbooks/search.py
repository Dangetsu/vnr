# coding: utf8
# search.py
# 8/4/2013 jichi

__all__ = 'SearchApi',

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import re
from sakurakit import sknetio, skstr
#from sakurakit.skdebug import dwarn
from sakurakit.skstr import unescapehtml

class SearchApi(object):
  API = "https://www.melonbooks.co.jp/search/search.php"
  ENCODING = 'utf8'
  COOKIES = {'AUTH_ADULT':'1'}

  session = None # requests.Session or None

  def _makereq(self, text):
    """
    @param  kw
    @return  kw
    """
    return {'name':text}

  def _fetch(self, **params):
    """
    @param  params  kw
    @return  str
    """
    return sknetio.getdata(self.API, gzip=True, params=params, session=self.session, cookies=self.COOKIES)

  def query(self, text):
    """
    @param  text  unicode
    @yield  {kw} or None
    """
    req = self._makereq(text)
    h = self._fetch(**req)
    if h:
      h = h.decode(self.ENCODING, errors='ignore')
      if h:
        return self._iterparse(h)

  # Example:
  # https://www.melonbooks.co.jp/search/search.php?name=姉小路直
  #
  #  <div class="product clearfix">
  #      <div class="relative">
  #          <div class="thumb">
  #              <a href="/detail/detail.php?product_id=114240" title="姉小路直子と銀色の死神 初回限定版" target="_blank"><img src="/resize_image.php?image=214000005312.jpg&amp;width=151&amp;height=151&amp;c=1&amp;aa=1" alt="姉小路直子と銀色の死神 初回限定版" /></a>
  #          </div>
  #          <div class="group clearfix">
  #              <div class="meta">                <p class="price"><em>&yen;7,452</em><span>345</span></p>                <p class="stock">在庫：好評受付中</p>
  #              </div>
  #              <div class="buy clearfix">
  #                  <form name="form_2_product" id="form_2_product" method="post" action="/detail/detail.php?product_id=114240" target="_blank">
  #                  <input type="hidden" name="mode" value="cart" />
  #                  <input type="hidden" name="product_id" value="114240" />
  #                  <input type="hidden" name="product_class_id" value="104241" />
  #                  <input type="hidden" name="transactionid" value="284e0451ae6972ff74ee8af00dfb7891d2ff9127" />
  #                              <select name="quantity" >
  #                  <option value="1">1</option><option value="2">2</option><option value="3">3</option><option value="4">4</option><option value="5">5</option><option value="6">6</option><option value="7">7</option><option value="8">8</option><option value="9">9</option><option value="10">10</option>
  #              </select>
  #                  <input type="submit" class="submit reserve" value="予約する" />
  #                  </form>
  #              </div>
  #              <div class="tag clearfix">
  #                  <span class="tag gunre leader"><span class="blue">PCソフト</span></span>
  #                  <span class="tag type"><span class="orange">R18</span></span>
  #                  <span class="tag monopoly"><span class="special">特典</span></span>
  #              </div>
  #              <div class="title"><p class="circle"><a href="/search/search.php?mode=search&text_type=maker&name=みなとカーニバル" title="みなとカーニバル">みなとカーニバル</a></p>                <p class="title"><a href="/detail/detail.php?product_id=114240" title="姉小路直子と銀色の死神 初回限定版" target="_blank">姉小路直子と銀色の死神 初回限定版</a></p>
  #              </div>
  _rx_parse = re.compile(r'<p class="circle"><a[^>]+?>([^<]+?)</a></p>\s*?<p class="title"><a href="/detail/detail\.php\?product_id=([0-9]+?)" title="([^"]+?)"')
  def _iterparse(self, h):
    """
    @param  h  unicode
    @yield  {kw}
    """
    h = skstr.findbetween(h, '<div class="relative">', u'<!-- ▲メイン -->')
    if h:
      for m in self._rx_parse.finditer(h):
        brand = m.group(1)
        key = m.group(2)
        title = m.group(3)
        if key and title:
          try: key = int(key)
          except: key = 0
          if key:
            yield {
              'id': key,
              'url': "https://www.melonbooks.co.jp/detail/detail.php?product_id=%s" % key,
              'title': unescapehtml(title),
              'brand': unescapehtml(brand),
              #'price': price, # price is not parsed here
            }

if __name__ == '__main__':
  api = SearchApi()
  t = u'姉小路'
  for it in api.query(t):
    print '-' * 10
    for k,v in it.iteritems():
      print k, ':', v

# EOF
