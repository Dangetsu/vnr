# coding: utf8
# search.py
# 8/4/2013 jichi

__all__ = 'SearchApi',

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import re
from datetime import datetime
from sakurakit import sknetio
from sakurakit.skstr import unescapehtml

class SearchApi(object):
  # Example: http://gyutto.com/search/search_list.php?category_id=6&set_category_flag=1&search_keyword=%83%89%83%93%83X&action=display
  HOST = 'http://gyutto.com'
  API = HOST + '/search/search_list.php'

  ENCODING = 'sjis'
  COOKIES = {'adult_check_flag':'1'}

  PC_GAME_CATEGORY_ID = 6
  DOUJIN_GAME_CATEGORY_ID = 10

  GAME_CATEGORIES = PC_GAME_CATEGORY_ID, DOUJIN_GAME_CATEGORY_ID

  session = None # requests.Session or None

  def _makereq(self, text, category_id, action):
    """
    @param  text  str
    @param  category_id int
    @param  action  str
    @return  kw
    """
    text = text.encode(self.ENCODING, errors='ignore')
    ret = {'search_keyword':text}
    if category_id:
      ret['category_id'] = category_id
      ret['set_category_flag'] = 1
    if action:
      ret['action'] = action
    ret['dtype'] = 'normal'
    return ret

  def _fetch(self, **params):
    """
    @param  params  kw
    @return  str
    """
    return sknetio.getdata(self.API, gzip=True, params=params, cookies=self.COOKIES, session=self.session)

  def query(self, text, category_id=0, action='display'):
    """
    @param  id  str or int  softId
    @param* category_id  int
    @yield  {kw} or None
    """
    req = self._makereq(text, category_id=category_id, action=action)
    h = self._fetch(**req)
    if h:
      h = h.decode(self.ENCODING, errors='ignore')
      if h:
        return self._iterparse(h)

  # Example:
  # http://gyutto.com/search/search_list.php?category_id=6&sub_category_id=&set_category_flag=1&mode=search&sub_category_id=11&search_item_search_id=122&search_keyword=%83%89%83%93%83X&search.x=0&search.y=0
  #
  # action = None:
  # <li>
  # <dl class="ItemBox">
  # <dd class="DefiPhotoName">
  # <a href="http://gyutto.com/i/item125070"><span><img src="/data/item_img/1250/125070/125070_p_s2.jpg" width="100" border="0" alt="ランス9 ヘルマン革命" /></span>
  # <span class="Alert"></span>ランス9 ヘルマン革命</a></dd>
  # <dd class="DefiAuthor">[&nbsp;<a href="http://gyutto.com/search/search_list.php?mode=search&brand_id=381&category_id=6&set_category_flag=1">アリスソフト</a>&nbsp;]</dd>
  # <dd class="DefiPrice">7,344円</dd>
  # <dd class="DefiPoint">最大10%還元</dd>
  # </dl>
  # </li>
  #
  # action = display:
  # <div class="RightBox">
  # <p class="DefiDate">2010年08月13日 発売</p>
  # <p class="DefiName"><span class="Pop"></span><a href="http://gyutto.com/i/item41702">ひめごとアンバランス こころとカラダのえっちなカンケイ？！</a><span class="RankIcon"></span></p>
  # <p class="DefiAuthor">[&nbsp;<a href="http://gyutto.com/search/search_list.php?mode=search&brand_id=1311&category_id=6&set_category_flag=1">RED ZONE×DMM</a>&nbsp;]</p>
  # <p class="DefiIcon"></p>
  # <p class="DefiCategory"><a href="http://gyutto.com/search/search_list.php?mode=search&category_id=6&sub_category_id=&set_category_flag=1">PCゲーム</a><span>/</span><a href="http://gyutto.com/search/search_list.php?mode=search&category_id=6&sub_category_id=11&set_category_flag=1">美少女ゲーム</a><span class="Slash">/</span><a href="http://gyutto.com/search/search_list.php?mode=search&genre_id=15988&category_id=6&set_category_flag=1">AVG+SLG</a></p><p class="DefiPrice">価格：&nbsp;4,104円</p>
  # <p class="DefiPoint">ポイント：最大380ギュッポ(10%還元)</p>
  # <p class="DefiGenre">ジャンル：<a href="http://gyutto.com/search/search_list.php?genre_id=15988&category_id=6&set_category_flag=1">AVG+SLG</a>、<a href="http://gyutto.com/search/search_list.php?genre_id=16619&category_id=6&set_category_flag=1">ラブラブ</a>、<a href="http://gyutto.com/search/search_list.php?genre_id=16597&category_id=6&set_category_flag=1">メガネっ娘</a>、<a href="http://gyutto.com/search/search_list.php?genre_id=16576&category_id=6&set_category_flag=1">人妻</a>、<a href="http://gyutto.com/search/search_list.php?genre_id=16605&category_id=6&set_category_flag=1">幼馴染</a>、<a href="http://gyutto.com/search/search_list.php?genre_id=16585&category_id=6&set_category_flag=1">パイズリ</a>、<a href="http://gyutto.com/search/search_list.php?genre_id=16563&category_id=6&set_category_flag=1">フェラチオ</a>、<a href="http://gyutto.com/search/search_list.php?genre_id=16565&category_id=6&set_category_flag=1">巨乳・爆乳</a>、<a href="http://gyutto.com/search/search_list.php?genre_id=18753&category_id=6&set_category_flag=1">恋愛</a><br></p>
  # <p class="DefiLead">同棲中の彼女・未来と、セフレ関係にある大学准教授・楓、同じマンションに住む人妻・弥生とめくるめく愛と快楽と肉欲のセッ○スを繰り広げていく“RED-ZONE”の秘め事エロスアドベンチャー!!</p>
  # <div class="DefiStar">
  # <ul>
  # <li class="Mds">平均評価</li>
  # <li class="Icon"><img width="81" height="17" border="0" alt="" src="/imgt/icon_Reviewstar20.gif"></li>
  # <li>（<a href="https://gyutto.com/i/item41702#REVIEW_UNIT">1件</a>）</li>
  # </ul>
  # </div>
  _rx_parse = re.compile(
    r'/soft.phtml\?id=([0-9]+?)" class="blueb">([^<]+?)</A>'
    r'.*?'
    r'<!--PRICE-->'
  , re.IGNORECASE|re.DOTALL)
  _rx_id_title = re.compile(r'http://gyutto.com/i/item(\d+)">([^<]+)</a>')
  _rx_img = re.compile(r'<img src="(/data/item_img/\d+/\d+/\d+)_p_s2.jpg"')
  _rx_price = re.compile(ur'([0-9,]+)?円')
  _rx_date = re.compile(u'(\d{4})年(\d{2})月(\d{2})日 発売')
  def _iterparse(self, h):
    """
    @param  h  unicode
    @yield  {kw}
    """
    START = 'class="parts_ItemBox'
    STOP1 = '<div class="RightBox">'
    STOP2 = '</div>'
    stop = 0
    while True:
      start = h.find(START, stop)
      if start == -1:
        break
      stop = h.find(STOP1, start)
      if stop == -1:
        break
      stop = h.find(STOP2, stop) # skip two divs
      if stop == -1:
        break

      hh = h[start:stop]

      m = self._rx_id_title.search(hh)
      try: key = long(m.group(1))
      except: break

      item = {
        'id': key,
        'url': "http://gyutto.com/i/item%s" % key,
        'title': unescapehtml(m.group(2)),
      }

      m = self._rx_date.search(h)
      if m:
        try: item['date'] = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except: pass

      img = ''
      m = self._rx_img.search(hh)
      if m:
        item['image'] = self.HOST + m.group(1) + '.jpg'

      m = self._rx_price.search(hh)
      try: item['price'] = int(m.group(1).replace(',', ''))
      except: pass

      item.update(self._iterparsefields(hh))
      yield item

  _rx_fields = (
     ('brand', re.compile(r'>([^<]+?)</a>&nbsp;\]</dd>')),
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

if __name__ == '__main__':
  api = SearchApi()
  t = u"ランス"
  for it in api.query(t): # reverse order
    #print '-' * 10
    for k,v in it.iteritems():
      print k, ':', v

# EOF
