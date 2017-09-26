# coding: utf8
# parse.py
# 8/18/2013 jichi
#
# See: http://erogamescape.dyndns.org/~ap2/ero/toukei_kaiseki/select.php
# See: http://erogamescape.dyndns.org/~ap2/ero/toukei_kaiseki/tablelist.php
# See (characters from twitter): http://erogamescape.dyndns.org/~ap2/ero/toukei_kaiseki/doc/erogamescape_er_20110723.pdf
#
# FIXME: Why csv does not work?!
# http://erogamescape.dyndns.org/~ap2/ero/toukei_kaiseki/create_csv.php?SQL=SELECT+gamename+from+gamelist+limit+100
__all__ = 'TableApi', 'GameTableApi', 'ReviewTableApi'

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import re
from datetime import datetime
from sakurakit import sknetio
from sakurakit.skstr import unescapehtml
import table

DEFAULT_HOST = "http://erogamescape.dyndns.org/~ap2/ero/toukei_kaiseki"

def resethost(): sethost(DEFAULT_HOST)
def sethost(url): TableApi.HOST = url

class TableApi(object):
  HOST = DEFAULT_HOST

  SELECT_URL = "/select.php"

  TABLE_NAME = '' # str
  TABLE = {} # {str key:function}

  session = None # requests.Session or None

  def query(self, *args, **kwargs):
    """
    @param* id  int or str
    @param* offset  int
    @param* limit  int
    @return  [kw] or None
    """
    req = self._makereq(*args, **kwargs)
    h = self._fetch(**req)
    if h:
      ret = self._parse(h)
      if ret:
        for it in list(ret):
          if 'gamename' in it:
            self._format(it)
            self._finalize(it)
          else:
            ret.remove(it)
        return ret

  def _fetch(self, **kwargs):
    """
    @return  str
    """
    return sknetio.postdata(self.HOST + self.SELECT_URL, gzip=True, data=kwargs, session=self.session)

  def _makereq(self, *args, **kwargs):
    """
    @return  kw
    """
    return {'SQL':self._makesql(*args, **kwargs)}

  def _makesql(self, offset=0, limit=30):
    """
    @param* id  int or str
    @param* offset  int
    @param* limit  int
    @return  str
    """
    ret =  ','.join(sorted(self.TABLE)) # use sorted to enforce order
    ret += " from %s" % self.TABLE_NAME
    if offset:
      ret += " offset %s" % offset
    if limit:
      ret += " limit %s" % limit
    return ''

  def _format(self, kw):
    """
    @param  kw
    """
    for k,v in self.TABLE.iteritems(): # sorted is not needed here
      kw[k] = v(kw[k])

  def _finalize(self, kw):
    """
    @param  kw
    """
    pass

  def _parse(self, h):
    """
    @param  h  unicode  html
    @return  kw or None
    """
    return [{k:v for k,v in zip(sorted(self.TABLE), self._iterparsetd(tr))}
        for index,tr in enumerate(self._iterparsetr(h)) if index > 0] # skip the first element which is the header

  def __maketagrx(name):
    """
    @param  name  str
    @return  re
    """
    return re.compile(r"<%s>(.*?)</%s>" % (name, name), re.IGNORECASE|re.DOTALL)

  _rx_td = __maketagrx('td')
  _rx_tr = __maketagrx('tr')

  def __iterparse(self, rx, h):
    """
    @param  rx  re
    @param  h  unicode
    @yield  unicode
    """
    for m in rx.finditer(h):
      yield m.group(1)

  def _iterparsetd(self, h): return self.__iterparse(self._rx_td, h)
  def _iterparsetr(self, h): return self.__iterparse(self._rx_tr, h)

class GameTableApi(TableApi):
  TABLE_NAME = 'gamelist'
  TABLE = table.gamelist # override

  def _makesql(self, id=None, text=None, limit=30):
    """@reimp
    @param* id  int or str
    @param* text  int or str
    @param* limit  int
    @return  str
    """
    fields =  ','.join(sorted(self.TABLE)) # use sorted to enforce order
    if id:
      return "%s from gamelist where id=%s" %(fields, id) # limit is ignored
    if text:
      text = self._escapetext(text)
      return "%s from gamelist where gamename like '%s' limit %s" %(fields, text, limit)
    return ''

  _rx_escapetext = re.compile(ur'[ ,～〜~‐-]')
  def _escapetext(self, text):
    return '%' + self._rx_escapetext.sub('%', text) + '%'

  def _finalize(self, kw):
    """@reimp
    @param  kw
    """
    count = kw['count'] = kw['count2']
    median = kw['median']
    if median and (not count or (count < 3 and median > 70)): # ignore median if the count is too small
      kw['median'] = None
    #elif not kw['median'] and kw['average2']:
    #  kw['median'] = kw['average2']
    kw['playtime'] = kw['total_play_time_median']
    kw['funtime'] = kw['time_before_understanding_fun_median']
    kw['url'] = 'http://erogamescape.dyndns.org/~ap2/ero/toukei_kaiseki/game.php?game=%s' % kw['id']

class ReviewTableApi(TableApi):
  TABLE_NAME = 'userreview'
  TABLE = table.userreview # override

  def _makesql(self, game=None, order='timestamp', desc=True, offset=0, limit=30):
    """
    @param* game  int or str
    @param* order  str  column name
    @param* desc  bool
    @param* offset  int
    @param* limit  int
    @return  str
    """
    ret =  ','.join(sorted(self.TABLE))
    ret += " from userreview where (memo is not null or hitokoto is not null)"
    if game:
      ret += " and game=%s" % game
    if order:
      ret += " order by %s" % order
    if desc:
      ret += " desc"
    if offset:
      ret += " offset %s" % offset
    if limit:
      ret += " limit %s" % limit
    return ret

if __name__ == '__main__':
  api = GameTableApi()
  t = 20042
  t = 11825
  t = 22083
  def test_game():
    q = api.query(t)
    #print q
    for it in q:
      print it['sellday']
      print it['dmm']
      print it['furigana']
      print it['digiket']
      print it['erogametokuten']
      print it['gyutto_id']
      print it['dlsite_domain']
      #print it['twitter_data_widget_id_before']

  def test_review():
    api = ReviewTableApi()
    #q = api.query(t, limit=10)
    q = api.query(t, limit=1)
    for it in q:
      print '-' * 5
      print it['uid']
      print it['hitokoto']
      print it['memo']
      print it['timestamp']

  def enable_proxy():
    import requests
    s = requests.Session()
    from proxyrequests import proxyconfig, proxyrequests
    site = proxyconfig.JPWEBPROXY_CONFIG
    #site = proxyconfig.WEBSERVER_CONFIG
    s = proxyrequests.Session(site, session=s, allows_caching=True)
    GameTableApi.session = s

  #enable_proxy()
  test_game()

# EOF
