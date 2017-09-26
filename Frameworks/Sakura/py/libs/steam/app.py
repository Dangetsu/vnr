# coding: utf8
# app.py
# 2/6/2015 jichi

__all__ = 'AppApi',

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import re
from sakurakit import sknetio
from sakurakit.skstr import unescapehtml
#from sakurakit.skdebug import dwarn

class AppApi(object):
  API = "http://store.steampowered.com/app/%s"
  ENCODING = 'utf8'
  COOKIES = {'birthtime':'500000000'}

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
    return sknetio.getdata(url, gzip=True, session=self.session, cookies=self.COOKIES)

  def query(self, id):
    """
    @param  id  str or int  appId
    @return  {kw} or None
    """
    url = self._makeurl(id)
    h = self._fetch(url)
    if h:
      h = h.decode(self.ENCODING, errors='ignore')
      if h:
        ret = self._parse(h)
        if ret:
          ret['id'] = long(id)
          ret['url'] = self.API % id # str

          img = "http://cdn.akamai.steamstatic.com/steam/apps/%s/header.jpg" % id
          ret['img'] = img if img in h else '' # str
          ret['sampleImages'] = list(self._iterparsesampleimages(h, id))
          return ret

  #def _patch(self, kw, id):
  #  """
  #  @param  kw  {kw}
  #  @param  id  long
  #  """
  #  chara = kw['characters']
  #  if chara:
  #    for it in chara:
  #      it['img'] = 'http://www.getchu.com/brandnew/%s/c%schara%s.jpg' % (id, id, it['id'])

  def _parse(self, h):
    """
    @param  h  unicode  html
    @return  {kw}
    """
    title = self._parsetitle(h)
    if title:
      ret = {
        'title': title, # unicode or None
        'price': self._parseprice(h),
        # Example: <a href="http://store.steampowered.com/tag/en/Otome/?snr=1_5_9__409" class="app_tag" style="display: none;"> Otome												</a>
        'otome': "/tag/en/Otome/?" in h, # bool
        'reviewCount': self._parsereviewcount(h),
        'ratingValue': self._parseratingvalue(h),
      }
      ret.update(self._iterparsefields(h))
      for k in ('developer', 'publisher'):
        if k in ret:
          ret[k] = self._fixbrand(ret[k])
      return ret

  _rx_brand = re.compile(r', ?inc$', re.IGNORECASE)
  def _fixbrand(self, t):
    """
    @param  unicode
    @return  unicode
    """
    t = self._rx_brand.sub('', t)
    if t[-1] == u'®':
      t = t[:-1]
    return t

  _re_fields = (
    # Example:
    # <b>Developer:</b>
    # <a href="http://store.steampowered.com/search/?developer=Idea%20Factory%2C%20Inc.&snr=1_5_9__408">Idea Factory, Inc.</a>
    ('developer', re.compile(r'<b>Developer:</b>\s*?<a [^>]+?>([^<]+?)</a>')),
    ('publisher', re.compile(r'<b>Publisher:</b>\s*?<a [^>]+?>([^<]+?)</a>')),

    # Example: Release Date: <span class="date">Jan 28, 2015</span>
    ('date', re.compile(r'Release Date: <span class="date">([0-9a-zA-Z, ]+?)</span>')),

    # Example:
    # <a class="linkbar" href="http://ideafintl.com/rebirth1/" target="_blank">
    # Visit the website <img src="http://store.akamai.steamstatic.com/public/images/v5/ico_external_link.gif" border="0" align="bottom">
    # </a>
    ('homepage', re.compile(r'href="([^"]+?)" target="_blank">\s*?Visit the website')),

    # Example:
    # <h2>About This Game</h2> When a feud with her brother gets too hot, Princess Ahri Remono, a young woman with a heart of fire, accepts a challenge that she cannot thrive in the world outside the Imperial Palace. In her first day in class, the boisterous princess finds a potential rival in the student body president.</div>
    ('description', re.compile(r'About This Game</h2>\s*(.*?)\s*</div', re.DOTALL)),
    ('review', re.compile(r'Reviews</h2>\s*(.*?)\s*</div>', re.DOTALL)),
  )
  def _iterparsefields(self, h):
    """
    @param  h  unicode
    @yield  (str key, unicode or None)
    """
    for k,rx in self._re_fields:
      m = rx.search(h)
      if m:
        yield k, unescapehtml(m.group(1))

  # Example: <div class="apphub_AppName">Hyperdimension Neptunia Re;Birth1</div>
  # Another example: <b>Title:</b> Hyperdimension Neptunia Re;Birth1<br>
  _re_title = re.compile(r'<div class="apphub_AppName">([^<]+?)</div>')
  def _parsetitle(self, h):
    """
    @param  h  unicode
    @return  unicode
    """
    m = self._re_title.search(h)
    if m:
      return unescapehtml(m.group(1))

  # Example:
  # <meta itemprop="priceCurrency" content="USD">
  # <meta itemprop="price" content="29.99">
  _re_price = re.compile(r'<meta itemprop="price" content="([^"]+?)">')
  def _parseprice(self, h):
    """
    @param  h  unicode
    @return  int cent
    """
    try: return int(float(self._re_price.search(h).group(1)) * 100)
    except: return 0

  # Example:
  # <div class="screenshot_holder">
  # <a class="highlight_screenshot_link" data-screenshotid="ss_5adedf15b87ebf4555aac094bb3551ddb9b6c189.jpg" target="_blank" href="https://steamcommunity.com/linkfilter/?url=http://cdn.akamai.steamstatic.com/steam/apps/324170/ss_5adedf15b87ebf4555aac094bb3551ddb9b6c189.1920x1080.jpg?t=1411840941"">
  # <img src="http://store.akamai.steamstatic.com/public/images/blank.gif">
  # </a>
  # </div>
  _re_ss = re.compile(r'data-screenshotid="(ss_[a-z0-9]+?.jpg)"')
  def _iterparsesampleimages(self, h, id):
    """
    @param  h  unicode
    @param  id  int
    @yield  url
    """
    for m in self._re_ss.finditer(h):
      path = m.group(1)
      yield "http://cdn.akamai.steamstatic.com/steam/apps/%s/%s" % (id, path)

  # Example:
  # <meta itemprop="reviewCount" content="435">
  # <meta itemprop="ratingValue" content="9">
  # <meta itemprop="bestRating" content="10">
  # <meta itemprop="worstRating" content="1">
  _re_reviewcount = re.compile(r'<meta itemprop="reviewCount" content="([0-9]+?)">')
  def _parsereviewcount(self, h):
    """
    @param  h  unicode
    @return 0
    """
    try: return int(self._re_reviewcount.search(h).group(1))
    except: return 0
  _re_ratingvalue = re.compile(r'<meta itemprop="ratingValue" content="([0-9]+?)">')
  def _parseratingvalue(self, h):
    """
    @param  h  unicode
    @return 0
    """
    try: return int(self._re_ratingvalue.search(h).group(1))
    except: return 0

if __name__ == '__main__':
  api = AppApi()
  k = 324170 # otome
  k = 214170 # review
  k = 282900
  print '-' * 10
  q = api.query(k)
  #for k,v in q.iteritems():
  #  print k,':',v
  print q['description']
  #print q['review']

# EOF
