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

class ReviewApi(object):
  HOST = 'http://gyutto.com'
  API = HOST + '/item/item_review.php?id=%s'
  ENCODING = 'euc-jp'
  #COOKIES = {'adult_check_flag':'1'} #, 'user_agent_flag':'1'}

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
    return sknetio.getdata(url, gzip=True, allow_redirects=False, session=self.session) #, cookies=self.COOKIES)

  def query(self, id):
    """
    @param  id  str or int  softId
    @return  unicode HTML or None
    """
    url = self._makeurl(id)
    h = self._fetch(url)
    if h:
      h = h.decode(self.ENCODING, errors='ignore')
      if h and 'ReviewEach' in h: # <div class='ReviewEach'
        return self._parse(h)

  def _replacelinks(self, h):
    """
    @param  h  unicode  HTML
    @return  h  unicode
    """
    return h.replace('<img src="/', '<img src="%s/' % self.HOST)

  _rx_review_garbage = re.compile('|'.join((
    u'.*?%s' % re.escape(u'<!-- *サマリー -->'), # header
    u'%s.*?' % re.escape(u'<!-- *ソート -->'), # footer
    '.*?'.join((
      re.escape('<div class="parts_PageNavi">'), # toolbar
      re.escape('<!-- / div.parts_PageNavi --></div>'),
    )),
    '.*?'.join((
      re.escape('<div class="parts_SortNavi">'), # toolbar
      re.escape('<!-- / div.parts_SortNavi --></div>'),
    )),
  )), re.DOTALL)
  def _parse(self, h):
    """
    @param  h  unicode  HTML
    @return  unicode  HTML
    """
    ret = self._replacelinks(self._rx_review_garbage.sub('', h))
    if ret:
      ret = self._clean(ret)
    return ret

  @staticmethod
  def _clean(h):
    """
    @param  h  unicode  HTML
    @return  unicode  HTML
    """
    #START = u'<p class="Sanko">▲&nbsp;このレビューは参考になりましたか？'
    START = '<p class="Sanko">'
    STOP = '</p>'
    start = h.find(START)
    while start > 0:
      stop = h.find(STOP, start)
      if stop < 0:
        break
      h = h[:start] + h[stop+len(STOP):]
      start = h.find(START)
    return h

if __name__ == '__main__':
  api = ReviewApi()
  #k = 4524 # bad
  k = 45242
  k = 109393
  #print '-' * 10
  q = api.query(k)
  print q

# EOF
