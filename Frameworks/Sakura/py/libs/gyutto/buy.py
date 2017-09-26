# coding: utf8
# buy.py
# 11/28/2013 jichi

__all__ = 'BuyApi',

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import re
from sakurakit import sknetio
from sakurakit.skdebug import dwarn

class BuyApi(object):
  HOST = 'http://gyutto.com'
  API = HOST + '/item/item_buy.php?id=%s'
  ENCODING = 'euc-jp'
  COOKIES = {'adult_check_flag':'1'} #, 'user_agent_flag':'1'}

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
    # Disable redirects
    return sknetio.getdata(url, gzip=True, allow_redirects=False, cookies=self.COOKIES, session=self.session)

  def query(self, id):
    """
    @param  id  str or int  softId
    @return  unicode HTML or None
    """
    url = self._makeurl(id)
    h = self._fetch(url)
    if h:
      h = h.decode(self.ENCODING, errors='ignore')
      if h and 'DemoOnly' not in h: # <p class="DemoOnly">この作品はデモ･体験版のみの配信となっております。</p>
        return self._parse(h)

  def _parse(self, h):
    """
    @param  h  unicode  HTML
    @return  kw
    """
    return {
      'price':self._parseprice(h),
      #'filesize':self._parsefilesize(h),
    }

  # Example: <p class="DefiPrice">&nbsp;2,366</p>
  _rx_price = re.compile('<p class="DefiPrice">&nbsp;([0-9,]+?)</p>')
  def _parseprice(self, h):
    """
    @param  h  unicode  HTML
    @return  int not None
    """
    m = self._rx_price.search(h)
    if m:
      try: return int(m.group(1).replace(',',''))
      except: pass
    return 0

if __name__ == '__main__':
  api = BuyApi()
  #k = 4524 # bad
  k = 46396
  #print '-' * 10
  q = api.query(k)
  print q['price']

# EOF
