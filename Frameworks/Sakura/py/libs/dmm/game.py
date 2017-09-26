# coding: utf8
# game.py
# 11/23/2013 jichi

__all__ = 'GameApi',

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import re
from sakurakit import sknetio, skstr
from sakurakit.skdebug import dwarn

DEFAULT_HOST = "http://www.dmm.co.jp"

def resethost(): sethost(DEFAULT_HOST)
def sethost(url): GameApi.HOST = url

class GameApi(object):
  HOST = DEFAULT_HOST

  session = None # requests.Session or None

  def _makereq(self, url):
    """
    @param  kw
    @return  kw
    """
    return {'url':url}

  def _fetch(self, url):
    """
    @param  url  str
    @return  str
    """
    return sknetio.getdata(url, gzip=True, session=self.session)

  def query(self, url):
    """
    @param  id  str  content_id
    @return  [unicode] or None
    """
    if self.HOST != DEFAULT_HOST:
      url = url.replace(DEFAULT_HOST, self.HOST).replace('/digital/', '/dc/') # suppress redirect
    h = self._fetch(url)
    if h:
      encoding = self._parsecharset(h)
      if encoding:
        try: h = h.decode(encoding, errors='ignore')
        except LookupError: h = None
        if h and not self._errorhtml(h):
          ret = self._parse(h)
          if ret:
            ret['url'] = url # str
          return ret

  # Example:
  # <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
  _rx_charset = re.compile(r"charset=([a-zA-Z0-9-]+)")
  def _parsecharset(self, h):
    """
    @param  h  unicode  html
    @return  unicode
    """
    m = self._rx_charset.search(h)
    if m:
      return m.group(1)

  _rx_title = re.compile(r"<title>.*?</title>", re.IGNORECASE)
  def _parsetitle(self, h):
    """
    @param  h  unicode  html
    @return  unicode
    """
    m = self._rx_title.search(h)
    if m:
      return m.group()

  def _errorhtml(self, h):
    """
    @param  h  unicode  html
    @return  bool
    """
    title = self._parsetitle(h)
    return not title or u"ページ" in title

  def _parse(self, h):
    """
    @param  h  unicode  html
    @return  kw
    """
    return {
      'description': self._parsedesc(h), # unicode html or None
      'review': self._parsereview(h) if self._hasreview(h) else None, # unicode html or None
    }

  #_rx_desc = re.compile(
  #  r'<div class="mg-b20 lh4">'
  #  r'.+?'
  #  r'</div>'
  #, re.DOTALL)
  def _parsedesc(self, h):
    """
    @param  h  unicode  html
    @return  unicode
    """
    #m = self._rx_desc.search(h)
    #if m:
    #  return self._replacelinks(m.group())
    START = '<div class="mg-b20 lh4">'
    STOP1 = '</div>'
    STOP2 = '<div id="sample-image'
    start = h.find(START)
    if start != -1:
      stop = h.find(STOP2, start)
      if stop == -1:
        stop = h.find(STOP1, start)
        if stop != -1:
          stop += len(STOP1)
      if stop != -1:
        h = h[start:stop]
        return self._replacelinks(h)

  # Example:
  # http://www.dmm.co.jp/dc/doujin/-/detail/=/cid=d_048634/
  #
  # <div class="sect"><div class="item">
  # <ul class="review-list">
  # <!-- /review-list --></ul>
  #_rx_review = re.compile(
  #  r'<ul class="review-list">'
  #  r'.+?'
  #  r'<!-- /review-list --></ul>'
  #, re.DOTALL)
  _rx_review = re.compile(
    r'<div id="review"'
    r'.+?'
    r'<!-- #review --></div>'
  , re.DOTALL)
  def _parsereview(self, h):
    """
    @param  h  unicode  html
    @return  unicode
    """
    if u"この作品に最初のレビューを書いてみませんか" not in h:
      m = self._rx_review.search(h)
      if m:
        return self._replacelinks(m.group())

  def _hasreview(self, h):
    """
    @param  h  unicode  html
    @return  bool
    """
    return "review-list" in h
    #return u"この作品に最初のレビューを書いてみませんか" in h

  #_repl_links = staticmethod(skstr.multireplacer({
  #  r'<a href="/': r'<a href="/#{h}',
  #})) #, flags=re.IGNORECASE)
  def _replacelinks(self, h):
    """
    @param  h  unicode  html
    @return  unicode or None
    """
    return h.replace('<a href="/', '<a href="%s/' % self.HOST)

if __name__ == '__main__':
  api = GameApi()
  url = "http://www.dmm.co.jp/dc/doujin/-/detail/=/cid=d_048634/"
  url = "http://www.dmm.co.jp/top/-/error/area/"
  url = "http://www.dmm.co.jp/top/-/error/area/404"
  url = "http://www.dmm.co.jp/mono/pcgame/-/detail/=/cid=1326aw007/"
  url = "http://www.dmm.co.jp/mono/pcgame/-/detail/=/cid=587apc10370/"
  url = "http://www.dmm.co.jp/dc/doujin/-/detail/=/cid=d_063678/"
  q = api.query(url)
  print q['description']
  print q['review']

# EOF
