# coding: utf8
# review.py
# 11/28/2013 jichi

__all__ = 'ReviewApi',

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import re
from sakurakit import sknetio
from sakurakit.skdebug import dwarn

# Example: http://www.getchu.com/review/item_review.php?action=list&id=756396
DEFAULT_HOST = "http://www.getchu.com"
_QUERY_PATH = "/review/item_review.php?action=list&id=%s"

def resethost():
  sethost(DEFAULT_HOST)
def sethost(url):
  api = ReviewApi
  api.HOST = url
  api.API = api.HOST + _QUERY_PATH

class ReviewApi(object):
  HOST = DEFAULT_HOST
  API = HOST + _QUERY_PATH
  ENCODING = 'euc-jp'
  #COOKIES = {'getchu_adalt_flag':'getchu.com'}

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
    return sknetio.getdata(url, gzip=True, session=self.session) #, cookies=self.COOKIES)

  def query(self, id):
    """
    @param  id  str or int  softId
    @return  unicode HTML or None
    """
    url = self._makeurl(id)
    h = self._fetch(url)
    if h:
      h = h.decode(self.ENCODING, errors='ignore')
      if self._nonempty(h):
        return self._parse(h)

  def _nonempty(self, h):
    """
    @param  h  unicode  HTML
    @return  bool
    """
    return 'ReviewEach' in h # <div class='ReviewEach'

  def _replacelinks(self, h):
    """
    @param  h  unicode  HTML
    @return  h  unicode
    """
    return h.replace('<img src="/', '<img src="%s/' % self.HOST)

  _rx_review_garbage = re.compile('|'.join((
    u'.*?' + re.escape(u'<!-- *サマリー -->'), # header
    '.*?'.join(( # must be above
      re.escape(u'<!-- *ソートとページ移動 -->'), # two-paged toolbar, see: http://www.getchu.com/soft.phtml?id=753262&gc=gc
      re.escape('</a>&nbsp;\n</div>'),
    )),
    '.*?'.join(( # must be below
      re.escape(u'<!-- *ソートとページ移動 -->'), # one-paged toolbar
      re.escape('&nbsp;&nbsp;\n</div>'),
    )),
  )), re.DOTALL)
  def _parse(self, h):
    """
    @param  h  unicode  HTML
    @return  unicode
    """
    ret = self._replacelinks(self._rx_review_garbage.sub('', h))
    if ret:
      ret = self._clean(ret)
    return ret

  _rx_review_btn = re.compile(ur'<button .*?レビューを投稿する.*?</button>', re.DOTALL)
  def _clean(self, h):
    """
    @param  h  unicode  HTML
    @return  unicode  HTML
    """
    #START = u'<p class="Sanko">▲&nbsp;このレビューは参考になりましたか？'
    START = '<p class="Sanko">'
    STOP = '</p>'
    while True:
      start = h.find(START)
      if start == -1:
        break
      stop = h.find(STOP, start)
      if stop == -1:
        break
      h = h[:start] + h[stop+len(STOP):]

    h = self._rx_review_btn.sub('', h)
    return h

if __name__ == '__main__':
  api = ReviewApi()
  #k = 7563960 # bad
  k = 756396
  #print '-' * 10
  q = api.query(k)
  #print type(q)
  print q

# EOF
