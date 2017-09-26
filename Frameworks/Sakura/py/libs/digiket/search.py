# coding: utf8
# search.py
# 6/18/2014 jichi

__all__ = 'SearchApi',

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import re
#from datetime import datetime
from sakurakit import sknetio
from sakurakit.skstr import unescapehtml
import defs

class SearchApi(object):
  #API = 'http://www.digiket.com/%s/result/_data/A=%s/limit=30/sort=new'
  HOST = "http://www.digiket.com"
  API = HOST + '/%s/result/_data/A=%s/'
  ENCODING = 'sjis'
  #COOKIES = {'adult_check':'1'}

  ALL_PATHS = '', 'material', 'soft', 'comics', 'bl', 'b', 'blgame', 'a', 'abooks', 'game', 'anime'
  GAME_PATHS = '', 'game', 'soft', 'a', 'b', 'blgame'

  session = None # requests.Session or None

  def _makereq(self, **kwargs):
    """
    @param  kw
    @return  kw
    """
    return {'url':self._makeurl(**kwargs)}

  def _makeurl(self, text, path, limit=0, sort=''):
    """
    @param  text  str
    @param  path  str
    @param  limit  int
    @param  sort  str
    @return  str
    """
    ret = self.API % (path, text)
    if limit:
      ret += 'limit=%s/' % limit
    if sort:
      ret += 'sort=%s/' % sort
    return ret

  def _fetch(self, url):
    """
    @param  url  str
    @return  str
    """
    return sknetio.getdata(url, gzip=True, session=self.session) #, cookies=self.COOKIES)

  def query(self, text, path, limit=30, sort='new'):
    """
    @param  text  unicode
    @param  path  str  such as 'game', 'b' (BL)
    @yield  {kw}
    """
    #text = text.encode(self.ENCODING, errors='ignore')
    text = sknetio.topercentencoding(text, encoding=self.ENCODING)
    if text and path:
      url = self._makeurl(text=text, path=path, limit=limit, sort=sort)
      h = self._fetch(url)
      if h:
        h = h.decode(self.ENCODING, errors='ignore')
        if h and u'<font size="2">0件</font>' not in h:
          return self._iterparse(h)

  # Example:
  # <div class="item-box" onMouseOver="this.style.backgroundColor='#FFEEBB'" onMouseOut="this.style.backgroundColor=''">
  # <span class="item-thum"><a href="/work/show/_data/ID=ITM0100413/"><img src="http://img.digiket.net/cg/100/ITM0100413_2.jpg" alt="Sleepover" width="82" height="82" border="0"></a></span>
  # <span class="item-string">■<a href="/work/show/_data/ID=ITM0100413/">Sleepover</a></span>
  # <span class="item-boder"></span>
  # <span class="item-line"><a href="/b/b_worklist/_data/ID=CIR0007283/">Black Monkey</a></span>
  # <span class="item-line">女性向同人</span>
  # <span class="item-genre"><a href="/b/link/_data/genre=%83A%83h%83x%83%93%83%60%83%83%81%5B%83Q%81%5B%83%80/">アドベンチャーゲーム</a></span>
  # <span class="item-line"><strong>1442円</strong><br><div class="item-point">(＋最大70ポイント還元)</div></span>
  # <span class="item-star"><img src="/work/img/review/00.gif" alt="未投稿" width="70" height="14"></span>
  # <span class="item-line"></span>
  # <span class="item-key"><a href="/b/link/_data/key=%90%C2%94N/">青年</a> <a href="/b/link/_data/key=%83%7B%81%5B%83C%83Y%83%89%83u/">ボーイズラブ</a> <a href="/b/link/_data/key=%83%81%83%93%83Y%83%89%83u/">メンズラブ</a> <a href="/b/link/_data/key=%90%E6%94y/">先輩</a> <a href="/b/link/_data/key=%97c%93%E9%90%F5/">幼馴染</a> <a href="/b/link/_data/key=%83p%83%93%83c/">パンツ</a> </span>
  # </div>
  _rx_id_title = re.compile(ur'■<a href="/work/show/_data/ID=ITM(\d+?)/">([^<]+?)</a>') # ■<a href="/work/show/_data/ID=ITM0100413/">Sleepover</a></span>
  _rx_price = re.compile(ur'(\d+)円')
  def _iterparse(self, h):
    """
    @param  id  str or int  softId
    @yield  {kw}
    """
    START = '<div class="item-box"'
    STOP = '\n</div>'
    start = stop = 0
    while True:
      start = h.find(START, stop)
      if start == -1:
        break
      stop = h.find(STOP, start)
      if stop == -1:
        break
      item = h[start:stop]

      m = self._rx_id_title.search(item)
      id = 0
      try: id = int(m.group(1).lstrip())
      except: pass
      if id:
        title = unescapehtml(m.group(2))

        img = ''
        key = defs.toitemkey(id)
        rx = re.compile(r"img.digiket.net/cg/(\d+?)/%s_2.jpg" % key)
        m = rx.search(item)
        if m:
          group = m.group(1)
          img = "http://img.digiket.net/cg/%s/%s_1.jpg" % (group, key)

        price = 0
        m = self._rx_price.search(item)
        try: price = int(m.group(1))
        except: pass
        yield {
          'id': id,
          'url': self.HOST + '/work/show/_data/ID=%s/' % key,
          'title': title,
          'img': img,
          'price': price,
        }

if __name__ == '__main__':
  # http://www.digiket.com/b/result/_data/A=bl/
  api = SearchApi()
  k = 'BL'
  k = u'屋根裏のラグーン'
  path = 'b'
  #print '-' * 10
  q = api.query(k, path=path)
  if q:
    for it in q:
      print '-' * 10
      for k,v in it.iteritems():
        print k,':',v

# EOF
