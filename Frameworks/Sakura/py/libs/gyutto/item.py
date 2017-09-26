# coding: utf8
# item.py
# 11/28/2013 jichi
# Note: the new line character is \r\n

__all__ = 'ItemApi',

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import re
from datetime import datetime
from sakurakit import sknetio
#from sakurakit.skcontainer import uniquelist
from sakurakit.skdebug import dwarn
from sakurakit.skstr import unescapehtml

class ItemApi(object):
  #HOST = "http://gyutto.me"
  HOST = "http://gyutto.com"
  IMAGE_HOST = "http://image.gyutto.com"
  API = HOST + "/i/item%s"
  ENCODING = 'sjis'
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
    # Disable redirects for gyutto items
    return sknetio.getdata(url, gzip=True, cookies=self.COOKIES, allow_redirects=True, session=self.session)

  def query(self, id=None, url=None):
    """
    @param  id  str or int  softId
    @return  {kw} or None
    """
    if not url and id:
      url = self._makeurl(id)
    if url:
      if not id:
        id = self._parseurlid(url)
      h = self._fetch(url)
      if h:
        h = h.decode(self.ENCODING, errors='ignore')
        if h and u'エラーが発生しました。' not in h:
          ret = self._parse(h)
          if ret:
            ret['id'] = long(id)
            ret['url'] = url
            ret['otome'] = u'乙女ゲーム' in h or url.startswith('http://gyutto.me')
            return ret

  _rx_urlid = re.compile('item(\d+)')
  def _parseurlid(self, url):
    """
    @param  url  str
    @return  long
    """
    try: return long(self._rx_urlid.search(url).group(1))
    except Exception, e: dwarn(e); return 0

  def _parse(self, h):
    """
    @param  h  unicode  html
    @return  {kw}
    """
    title = self._parsetitle(h)
    if title:
      return {
        'title': title,
        'doujin': u'同人' in h,
        'image': self._parseimage(h),
        'filesize': self._parsefilesize(h),
        'brand': self._parsebrand(h),
        'series': self._parseddlink(u'シリーズ', h),
        'date': self._parsedate(h),
        'theme': self._parsedd(u'作品テーマ', h),
        #'price': self._parseprice(h), # price does not exist
        'sampleImages': list(self._iterparsesampleimages(h)),
        'tags': list(self._iterparsetags(h)),
        #'genres': list(self._iterparseddlinks(u'ジャンル', h)),
        'artists': list(self._iterparseddlinks(u'原画', h)) + list(self._iterparseddlinks(u'原画家', h)),
        'writers': list(self._iterparseddlinks(u'シナリオ', h)),
        'musicians': list(self._iterparseddlinks(u'音楽', h)) + list(self._iterparseddlinks(u'音楽担当', h)),
        #'cv': list(self._iterparseddlinks(u'声優', h)),
      }

  def __makemetarx(name):
    """
    @param  name  str
    @return  re
    """
    return re.compile(r'<meta %s content="(.*?)"' % name)

  def _parsemeta(self, rx, h):
    """
    @param  rx  re
    @param  h  unicode  html
    @return  unicode or None
    """
    m = rx.search(h)
    if m:
      return m.group(1)

  _rx_meta_keyword = __makemetarx('name="keyword"')
  def _parsemetakeyword(self, h):
    """
    @param  h  unicode  html
    @return  unicode or None
    """
    return self._parsemeta(self._rx_meta_keyword, h)

  def _parsetitle(self, h):
    """
    @param  h  unicode  html
    @return  unicode or None
    """
    t = self._parsemetakeyword(h)
    if t:
      return unescapehtml(t.partition(',')[0])

  def _parsedd(self, key, h, flags=0):
    """
    @param  h  unicode  html
    @return  unicode not None
    """
    #rx = re.compile(r'<dt>%s</dt>\r\n<dd>(.+?)</dd>' % key, flags)
    start = h.find('<dt>%s</dt>' % key)
    if start >= 0:
      start = h.find('<dd>', start)
      if start > 0:
        stop = h.find('</dd>', start)
        if stop > 0:
          return unescapehtml(h[start:stop])
    return ''

  _rx_image = re.compile(r'/data/item_img/[0-9]+/([0-9]+)/\1\.jpg')
  def _parseimage(self, h):
    """
    @param  h  unicode  html
    @return  str  URL or None
    """
    m = self._rx_image.search(h)
    if m:
      return self.IMAGE_HOST + m.group()

  def _parsebrand(self, h):
    """
    @param  h  unicode  html
    @return  unicode  URL or None
    """
    ret = self._parseddlink(u'ブランド', h) or self._parseddlink(u'サークル', h)
    return ret.replace(" / ", ',').replace(u"／", ',') if ret else ''

  _rx_filesize = re.compile(r'([0-9\.]+) ([GMK]?)B')
  def _parsefilesize(self, h):
    """
    @param  h  unicode  html
    @return  int not None
    """
    dd = self._parsedd(u'ファイルサイズ', h)
    if dd:
      m = self._rx_filesize.search(dd)
      if m:
        try:
          num = float(m.group(1)) # throw
          unit = m.group(2)
          if not unit:
            return int(num)
          elif unit == 'K':
            return int(num * 1024)
          elif unit == 'M':
            return int(num * 1024 * 1024)
          elif unit == 'G':
            return int(num * 1024 * 1024 * 1024)
          else:
            dwarn("unknown size unit: %s" % unit)
        except: pass
    return 0

  # Note: There are two kinds of date: http://gyutto.com/i/item16775
  # Example:
  #  1.
  # <dt>配信開始日</dt>
  # <dd>2007年05月25日</dd>
  # 2.
  # パッケージ販売開始日
  _rx_date = re.compile(ur'(\d{4})年(\d{2})月(\d{2})日')
  def _parsedate(self, h):
    """
    @param  h  unicode  html
    @return  datetime object  such as 2007/05/25  or Non4
    """
    for k in u'パッケージ販売開始日', u'配信開始日':
      dd = self._parsedd(k, h)
      if dd:
        m = self._rx_date.search(dd)
        if m:
          try: return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
          except: pass

  # Example:
  # <!-- * -->
  # <dl class="BasicInfo clearfix">
  # <dt>ブランド</dt>
  # <dd><a href="http://gyutto.com/search/search_list.php?mode=search&brand_id=312&category_id=6&set_category_flag=1">KISS</a>
  # </dd>
  # </dl>
  _rx_link = re.compile('<a [^>]+?>([^<]+?)</a>')
  def _parseddlink(self, *args, **kwargs):
    """
    @return  unicode not None
    """
    dd = self._parsedd(*args, **kwargs);
    if dd:
      m = self._rx_link.search(dd)
      if m:
        return unescapehtml(m.group(1))
    return ''

  def _iterparseddlinks(self, *args, **kwargs):
    """
    @yield  unicode
    """
    dd = self._parsedd(*args, **kwargs);
    if dd:
      for m in self._rx_link.finditer(dd):
        yield unescapehtml(m.group(1))

  _rx_sampleimage = re.compile(r'/data/item_img/[0-9]+/[0-9]+/[0-9]+_[0-9]+.jpg')
  def _iterparsesampleimages(self, h):
    """
    @param  h  unicode  html
    @yield  str  URL
    """
    for m in self._rx_sampleimage.finditer(h):
      yield self.IMAGE_HOST + m.group()

  # Example
  # <dd><a href="http://gyutto.com/search/search_list.php?genre_id=20754&category_id=6&set_category_flag=1">メイド</a>、<a href="http://gyutto.com/search/search_list.php?genre_id=18753&category_id=6&set_category_flag=1">恋愛</a>、<a href="http://gyutto.com/search/search_list.php?genre_id=16609&category_id=6&set_category_flag=1">貧乳・微乳</a>、<a href="http://gyutto.com/search/search_list.php?genre_id=16565&category_id=6&set_category_flag=1">巨乳・爆乳</a>、<a href="http://gyutto.com/search/search_list.php?genre_id=16604&category_id=6&set_category_flag=1">妹</a>、<a href="http://gyutto.com/search/search_list.php?genre_id=16621&category_id=6&set_category_flag=1">メイド服</a>、<a href="http://gyutto.com/search/search_list.php?genre_id=16564&category_id=6&set_category_flag=1">学園</a>、<a href="http://gyutto.com/search/search_list.php?genre_id=16561&category_id=6&set_category_flag=1">コメディ</a>、<a href="http://gyutto.com/search/search_list.php?genre_id=15983&category_id=6&set_category_flag=1">アドベンチャー</a><br>
  _rx_tag = re.compile(r'genre_id=.*?>(.*?)</a>')
  _rx_tag_delims = re.compile(ur'[・+]')
  def _iterparsetags(self, h):
    """
    @param  h  unicode  html
    @yield  str
    """
    s = set()
    for m in self._rx_tag.finditer(h):
      t = unescapehtml(m.group(1))
      if t not in s:
        s.add(t)
        for it in self._rx_tag_delims.split(t):
          yield it

  # Example
  # <dt>ジャンル</dt>
  # <dd><a href="http://gyutto.com/search/search_list.php?genre_id=20754&category_id=6&set_category_flag=1">メイド</a>、<a href="http://gyutto.com/search/search_list.php?genre_id=18753&category_id=6&set_category_flag=1">恋愛</a>、<a href="http://gyutto.com/search/search_list.php?genre_id=16609&category_id=6&set_category_flag=1">貧乳・微乳</a>、<a href="http://gyutto.com/search/search_list.php?genre_id=16565&category_id=6&set_category_flag=1">巨乳・爆乳</a>、<a href="http://gyutto.com/search/search_list.php?genre_id=16604&category_id=6&set_category_flag=1">妹</a>、<a href="http://gyutto.com/search/search_list.php?genre_id=16621&category_id=6&set_category_flag=1">メイド服</a>、<a href="http://gyutto.com/search/search_list.php?genre_id=16564&category_id=6&set_category_flag=1">学園</a>、<a href="http://gyutto.com/search/search_list.php?genre_id=16561&category_id=6&set_category_flag=1">コメディ</a>、<a href="http://gyutto.com/search/search_list.php?genre_id=15983&category_id=6&set_category_flag=1">アドベンチャー</a><br>
  # </dd>
  # </dl>
  #def __maketablerx(name):
  #  return re.compile(r"<dl>%s</dl>.*?</dd>", re.DOTALL)

if __name__ == '__main__':
  api = ItemApi()
  k = 45242
  k = 16775 # AlterEgo, http://gyutto.com/i/item16775
  k = 58699 # 英雄伝説 空の軌跡SC, http://gyutto.jp/i/item58699
  k = 108434
  k = 2722
  k = 45242
  k = 130268

  print '-' * 10
  q = api.query(k)
  #print q['title']
  #print q['image']
  #print q['sampleImages']
  #print q['price']
  for it in q['tags']:
    print it
  print q['title']
  print q['theme']
  #print q['videos']
  print q['brand']
  print q['date']
  print q['sampleImages']

# EOF
