# coding: utf8
# search.py
# 2/6/2015 jichi

__all__ = 'SearchApi',

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import re
from sakurakit import sknetio
#from sakurakit.skdebug import dwarn
from sakurakit.skstr import unescapehtml

class SearchApi(object):
  # Example: http://store.steampowered.com/search?term=Hyperdimension&sort_by=_ASC&category1=998
  API = "http://store.steampowered.com/search" #?term=Hyperdimension&sort_by=_ASC&category1=998
  ENCODING = 'utf8'

  session = None # requests.Session or None

  CATEGORY_GAME = 998
  SORT_ASC = '_ASC'

  def _makereq(self, text, sort, category=CATEGORY_GAME):
    """
    @param  text  str
    @param  sort  str
    @param  category  str
    @return  kw
    """
    return {'term':text, 'sort_by':sort, 'category1':category}

  def _fetch(self, **params):
    """
    @param  params  kw
    @return  str
    """
    return sknetio.getdata(self.API, gzip=True, params=params, session=self.session) #, cookies=self.COOKIES)

  def query(self, text, sort=SORT_ASC, category=CATEGORY_GAME):
    """
    @param  id  str or int  softId
    @param  sort  str
    @param  category  int
    @yield  {kw} or None
    """
    req = self._makereq(text, sort=sort, category=category)
    h = self._fetch(**req)
    if h:
      h = h.decode(self.ENCODING, errors='ignore')
      if h:
        return self._iterparse(h)

  # Example:
  # http://store.steampowered.com/search?term=Birth&sort_by=_ASC&category1=998
  #
  # <a href="http://store.steampowered.com/app/282900/?snr=1_7_7_151_150_1"  data-ds-appid="282900" onmouseover="GameHover( this, event, 'global_hover', {&quot;type&quot;:&quot;app&quot;,&quot;id&quot;:282900,&quot;public&quot;:1,&quot;v6&quot;:1} );" onmouseout="HideGameHover( this, event, 'global_hover' )" class="search_result_row ds_collapse_flag" >
  # <div class="col search_capsule"><img src="http://cdn.akamai.steamstatic.com/steam/apps/282900/capsule_sm_120.jpg?t=1422919039" alt="Buy Hyperdimension Neptunia Re;Birth1" width="120" height="45"></div>
  # <div class="col search_name ellipsis">
  # <span class="title">Hyperdimension Neptunia Re;Birth1</span>
  # <p>
  # <span class="platform_img win"></span></p>
  # </div>
  # <div class="col search_released">Jan 29, 2015</div>
  # <div class="col search_reviewscore">
  # <span class="search_review_summary positive" data-store-tooltip="Very Positive&lt;br&gt;94% of the 1,093 user reviews for this game are positive.">
  # </span>
  # </div>
  #
  # <div class="col search_discount">
  #
  # </div>
  # <div class="col search_price ">
  # &#36;29.99</div>
  #
  # </a>
  _rx_parse = re.compile(
    r'data-ds-appid="([0-9]+?)"'
    r'.*?'
    r'<div class="col search_reviewscore">'
  , re.IGNORECASE|re.DOTALL)
  def _iterparse(self, h):
    """
    @param  h  unicode
    @yield  {kw}
    """
    for m in self._rx_parse.finditer(h):
      id = 0
      try: id = int(m.group(1))
      except: pass
      if id:
        url = "http://store.steampowered.com/app/%s" % id
        item = {
          'id': id,
          'url': url,
        }

        item.update(self._iterparsefields(m.group()))
        yield item

  _rx_fields = (
      # Example: <span class="title">Hyperdimension Neptunia Re;Birth1</span>
    ('title', re.compile('class="title">([^<]+?)<')),
    # Example: <div class="col search_released">Jan 29, 2015</div>
    ('date', re.compile(r'col search_released">([a-zA-Z0-9, ]+?)</div>')),
    # Example: <div class="col search_price "> &#36;29.99</div>
    #('price', re.compile(r'(&#36;[0-9.]+?)<')),
  )
  def _iterparsefields(self, h):
    """
    @param  h  unicode
    @yield  (str key, unicode or None)
    """
    for k,rx in self._rx_fields:
      m = rx.search(h)
      if m:
        yield k, unescapehtml(m.group(1))

if __name__ == '__main__':
  api = SearchApi()
  t = "birth"
  for it in api.query(t):
    print '-' * 10
    for k,v in it.iteritems():
      print k, ':', v

# EOF
