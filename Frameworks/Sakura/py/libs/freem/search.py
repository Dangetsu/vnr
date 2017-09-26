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
  API = "http://www.freem.ne.jp/search"
  ENCODING = 'utf8'

  session = None # requests.Session or None

  def _makereq(self, text):
    """
    @param  text  str
    @param  genre  str
    @param  sort  str
    @param  sort2  str
    @return  kw
    """
    text = text.encode(self.ENCODING, errors='ignore')
    return {'keyword':text}

  def _fetch(self, **params):
    """
    @param  params  kw
    @return  str
    """
    return sknetio.getdata(self.API, gzip=True, params=params, session=self.session) #, cookies=self.COOKIES)

  def query(self, text):
    """
    @param  text  unicode
    """
    req = self._makereq(text)
    h = self._fetch(**req)
    if h:
      h = h.decode(self.ENCODING, errors='ignore')
      if h:
        return self._iterparse(h)

  # Example:
  # http://www.freem.ne.jp/search/?keyword=冒険
  #
  # <div class="section01"> <h4><a href="/win/game/8371">ロボネコの冒険2</a></h4> <div class="photo"><a href="/win/game/8371"><img src="http://pic.freem.ne.jp/win/8371s.jpg" alt="ロボネコの冒険2" /></a></div> <div class="text"> <p class="">忘れ物、届けます。</p> <p class="">【容量】6,962KB<br /> 【制作者】<a href="/brand/4754">モコネコ</a><br /> 【公開日】2015-01-18<br /> <img src="/img/addtomylist.gif" style="width:7px;height:10px;"> <a href="/mypage/wishlist_add/8371">マイリストへ保存</a></p> </div> </div><!--End of .section01--><div class="section02"> <h4><a href="/win/game/5919">&quot;Tkl Online&quot; Demo version</a></h4> <div class="photo"><a href="/win/game/5919"><img src="http://pic.freem.ne.jp/win/5919s.jpg" alt="&quot;Tkl Online&quot; Demo version" /></a></div> <div class="text"> <p class="">RPGツクールVXで制作した、MMO風RPGです。</p> <p class="">【容量】113,243KB<br /> 【制作者】<a href="/brand/3487">takapi</a><br /> 【公開日】2013-12-04<br /> <img src="/img/addtomylist.gif" style="width:7px;height:10px;"> <a href="/mypage/wishlist_add/5919">マイリストへ保存</a></p> </div> </div><!--End of .section02--><div class="section01"> <h4><a href="/win/game/7621">RPGを初めて遊ぶ人のためのRPG ver1.32</a></h4> <div class="photo"><a href="/win/game/7621"><img src="http://pic.freem.ne.jp/win/7621s.jpg" alt="RPGを初めて遊ぶ人のためのRPG ver1.32" /></a></div> <div class="text"> <p class="">妖精ペックがご案内！初心者対応ゆるさくRPG。</p> <p class="">【容量】31,401KB<br /> 【制作者】<a href="/brand/4394">えあてき</a><br /> 【公開日】2014-10-03<br /> <img src="/img/addtomylist.gif" style="width:7px;height:10px;"> <a href="/mypage/wishlist_add/7621">マイリストへ保存</a></p> </div> </div><!--End of .section01--><div class="section02">
  #
  # Single item:
  # <img src="http://pic.freem.ne.jp/win/8371s.jpg" alt="ロボネコの冒険2" /></a></div> <div class="text"> <p class="">忘れ物、届けます。</p> <p class="">【容量】6,962KB<br /> 【制作者】<a href="/brand/4754">モコネコ</a><br /> 【公開日】2015-01-18<br /> <img src="/img/addtomylist.gif"
  _rx_parse = re.compile(
    r'src="http://pic.freem.ne.jp/win/(\d+)s.jpg" alt="([^"]*)"'
    r'.*?'
    r'/img/addtomylist.gif'
  )
  def _iterparse(self, h):
    """
    @param  h  unicode
    @yield  {kw}
    """
    for m in self._rx_parse.finditer(h):
      id = m.group(1)
      title = m.group(2)
      if id and title:
        url = "http://freem.ne.jp/win/game/%s" % id
        img = 'http://pic.freem.ne.jp/win/%s.jpg' % id

        item = {
          'id': id,
          'url': url,
          'img': img,
          'title': unescapehtml(title),
        }

        item.update(self._iterparsefields(m.group()))
        yield item

  _rx_fields = (
    ('brand', re.compile(r'"/brand/\d+">([^<]+)<')),
    ('date', re.compile(ur'【公開日】([0-9-]+)')),
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

  # Example: RPGを初めて遊ぶ人のためのRPG ver1.32
  _re_fixtitle = re.compile(' ver[0-9. ]+$')
  def _fixtitle(self, t):
    """
    @param  t  unicode
    @return  unicode
    """
    return self._re_fixtitle.sub('', t)

if __name__ == '__main__':
  api = SearchApi()
  t = u'あなたが呪われて'
  t = u'冒険'
  for it in api.query(t):
    print '-' * 10
    for k,v in it.iteritems():
      print k, ':', v

# EOF
