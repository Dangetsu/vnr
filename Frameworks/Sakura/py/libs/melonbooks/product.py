# coding: utf8
# product.py
# 10/20/2013 jichi

__all__ = 'ProductApi',

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import re
from sakurakit import sknetio, skstr
from sakurakit.skcontainer import uniquelist
from sakurakit.skstr import unescapehtml
#from sakurakit.skdebug import dwarn

class ProductApi(object):
  QUERY_HOST = "https://www.melonbooks.co.jp"
  QUERY_PATH = "/detail/detail.php?product_id=%s"
  API = QUERY_HOST + QUERY_PATH
  ENCODING = 'utf8'
  COOKIES = {'AUTH_ADULT':'1'}

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
    @param  id  str or int  softId
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
          ret['url'] = url
          return ret

  def _parse(self, h):
    """
    @param  h  unicode  html
    @return  {kw}
    """
    title = self._parsetitle(h)
    if title:
      ret = {
        'title': title, # unicode
        'brand': self._parsebrand(h), # unicode
        'price': self._parseprice(h), # int or None
        # Example: <span class="tag type"><span class="coterie">同人</span></span><span class="tag type"><span class="orange">一般</span></span>
        'doujin': u'<span class="coterie">同人</span>' in h,
        'ecchi': u'一般向け' not in h and u'18禁' in h,
        'intro': self._parseintro(h),
      }
      desc = self._parsedesc(h)
      if desc:
        ret['date'] = self._parsedesctable(desc, u'発行日')
        ret['event'] = self._parsedesctable(desc, u'イベント')

        writers = self._parsecreator(h, u'シナリオ')
        for it in self._iterparsedesctable(desc, u'シナリオ'):
          if it not in writers:
            writers.append(it)
        ret['writers'] = writers # [unicode]

        artists = self._parsecreator(h, u'原画')
        for it in self._iterparsedesctable(desc, u'作家名'):
          if it not in artists:
            artists.append(it)
        ret['artists'] = artists


      ret['image'] = self._parseimage(h)
      ret['sampleImages'] = list(self._iterparsesampleimages(h))
      return ret

  # Example: <br>原画:克/月杜尋<br>シナリオ:御影/溝淵涼<br>
  def _parsecreator(self, h, key):
    """
    @param  h  unicode  html
    @param  key  unicode
    @return  [unicode] not None
    """
    ret = skstr.findbetween(h, '<br>%s:' % key, '<br>')
    if ret and '<' not in ret:
      return unescapehtml(ret).split('/')
    return []

  # Example: ="/resize_image.php?image=214000005276.jpg&amp;width=450&amp;height=450"
  # Example: <a class="opacity pop" style="display:inline;" href="/resize_image.php?image=11261400_54755e534b1ce.jpg" title=""><img src="/resize_image.php?image=11261400_54755e534b1ce.jpg&amp;width=450&amp;height=450" alt="クロノクロック" /></a>
  # Example: <a class="opacity pop" style="min-width:320px;max-width:320px;" href="/resize_image.php?image=213001007232.jpg" title=""><img src="/resize_image.php?image=213001007232.jpg&amp;width=320&amp;height=320" alt="魔理沙と6つのキノコ" /></a>
  def _parseimage(self, h):
    """
    @param  h  unicode  html
    @return  string
    """
    for width in (450, 320):
      img = skstr.rfindbetween(h, "/resize_image.php?image=", ".jpg&amp;width=%s&amp;height=%s" % (width, width))
      if img and '"' not in img:
        return "%s/resize_image.php?image=%s.jpg" % (self.QUERY_HOST, img)

  # Example: <a class="opacity pop" href="/special/a/4/214000005276o.jpg" title=""><img src="/special/a/4/214000005276o.jpg" alt="サンプル" width="161" height="91" vspace="2"></a>
  # Example: <a class="opacity pop" href="https://www.melonbooks.co.jp/resize_image.php?image=213001007232a.jpg" title=""><img src="https://www.melonbooks.co.jp/resize_image.php?image=213001007232a.jpg&amp;width=144&amp;height=144" alt="魔理沙と6つのキノコ" /></a>
  _rx_imgid_special = re.compile(r'/special/a/4/([0-9]+?)a\.jpg"')
  _rx_imgid_resize = re.compile(r'/resize_image.php\?image=([0-9]+)a\.jpg"')
  def _iterparsesampleimages(self, h):
    """
    @param  h  unicode  html
    @yield  unicode
    """
    try:
      for rx,pattern in (
          (self._rx_imgid_special, r'href="(/special/a/4/%s[a-z0-9]+?\.jpg)"'),
          (self._rx_imgid_resize, r'href="[^"]+?(/resize_image\.php\?image=%s[a-z0-9]+\.jpg)"'),
        ):
        m = rx.search(h)
        if m:
          imgid = int(m.group(1))
          pattern = pattern % imgid
          rx = re.compile(pattern) # only use special/a/4, which are large images
          for m in rx.finditer(h):
            url = m.group(1)
            if url[0] == '/':
              url = self.QUERY_HOST + url
            yield url
    except: pass

  # Example description:
  # <!-- description -->
  # <div id="description" class="mb20">
  #     <div class="headline head_m mb10">
  #         <div class="head head_green"><h1 class="str">姉小路直子と銀色の死神 初回限定版</h1></div>
  #     </div>
  #     <h2>作品詳細</h2>
  #     <p>
  #
  #     </p>
  #     <table class="stripe">
  #         <tr class="odd">
  #             <th>タイトル</th>
  #             <td>姉小路直子と銀色の死神 初回限定版</td>
  #         </tr>
  #         <tr class="odd">
  #             <th>メーカー</th>
  #                         <td>
  #                 <a href="https://www.melonbooks.co.jp/search/search.php?name=%E3%81%BF%E3%81%AA%E3%81%A8%E3%82%AB%E3%83%BC%E3%83%8B%E3%83%90%E3%83%AB&text_type=maker">みなとカーニバル</a>
  #             </td>
  #                     </tr>
  #                             <tr class="odd">
  #                 <th>ジャンル</th>
  #                 <td>
  #                                             <a href="https://www.melonbooks.co.jp/tags/index.php?genre=ADV">ADV</a>
  #                                                     ,
  #                                                                     <a href="https://www.melonbooks.co.jp/tags/index.php?genre=年上">年上</a>
  #                                                             </td>
  #             </tr>
  #                             <tr class="odd">
  #                 <th>発行日</th>
  #                 <td>2015/03/27</td>
  #             </tr>
  #                                 <tr class="odd">
  #             <th>作品種別</th>
  #             <td>18禁</td>
  #         </tr>
  #                                     <tr class="odd">
  #                 <th>動作環境</th>
  #                 <td>対応OS:WindowsVista/7/8/8.1<br>推奨CPU:<br>メモリ:<br>HDD容量:<br>メディア:DVD-ROM<br>解像度:<br>原画:みこしまつり/白猫参謀<br>シナリオ:王雀孫/タカヒロ<br>ボイス:あり<br></td>
  #             </tr>
  #                     </table>
  # </div>
  # <!-- /description -->
  def _parsedesc(self, h):
    """
    @param  h  unicode  html
    @return  unicode
    """
    return skstr.findbetween(h, '<!-- description -->', '<!-- /description -->')

  # Example:
  # <th>イベント</th>
  # <td><a href="https://www.melonbooks.co.jp/search/search.php?name=%E3%82%B3%E3%83%9F%E3%83%83%E3%82%AF%E3%83%9E%E3%83%BC%E3%82%B1%E3%83%83%E3%83%8887&text_type=event">コミックマーケット87</a></td>
  def _parsedesctable(self, h, th):
    """
    @param  h  unicode  html
    @param  h  th  unicode
    @return  unicode
    """
    tag = '<th>%s</th>' % th
    start = h.find(tag)
    if start != -1:
      start += len(tag)
      tag = '<td>'
      start = h.find(tag, start)
      if start != -1:
        start += len(tag)
        stop = h.find('</td>', start)
        if stop != -1:
          ret = h[start:stop]
          if '</a>' in ret:
            ret = skstr.rfindbetween(ret, '>', '</a>')
          if '>' not in ret:
            return unescapehtml(ret.strip())

  # Example:
  #
  #  <th>作家名</th>
  #  <td>
  #   <a href="https://www.melonbooks.co.jp/search/search.php?name=%E3%81%82%E3%81%8D%E3%82%84%E3%81%BE%E3%81%86%E3%81%AB&text_type=author">あきやまうに</a>
  #   &nbsp; &#44; &nbsp;
  #                       <a href="https://www.melonbooks.co.jp/search/search.php?name=HALT&text_type=author">HALT</a>
  #   &nbsp; &#44; &nbsp;
  #                       <a href="https://www.melonbooks.co.jp/search/search.php?name=ziki_7&text_type=author">ziki_7</a>
  #   &nbsp; &#44; &nbsp;
  #                       <a href="https://www.melonbooks.co.jp/search/search.php?name=%E3%83%A2%E3%82%BF&text_type=author">モタ</a>
  #  </td>
  def _iterparsedesctable(self, h, th):
    """
    @param  h  unicode  html
    @param  h  th  unicode
    @return  unicode
    """
    tag = '<th>%s</th>' % th
    start = h.find(tag)
    if start != -1:
      start += len(tag)
      tag = '<td>'
      start = h.find(tag, start)
      if start != -1:
        start += len(tag)
        stop = h.find('</td>', start)
        if stop != -1:
          ret = h[start:stop]
          if '>' not in ret:
            yield unescapehtml(ret.strip())
          elif '</a>' in ret:
            for it in skstr.riterfindbetween(ret, '>', '</a>'):
              if '>' not in it:
                yield unescapehtml(it.strip())

  # Example: <title>姉小路直子と銀色の死神 初回限定版の通販・購入（みなとカーニバル）はメロンブックス | メロンブックス</title>
  # Example:   <strong class="str" style="max-width:88%;margin-right:0;float:left;width:auto;">クロノクロック</strong>
  def _parsetitle(self, h):
    """
    @param  h  unicode  html
    @return  unicode
    """
    r = skstr.findbetween(h, 'width:auto;">', '</strong>')
    if r and '<' not in r:
      return unescapehtml(r)

  # Example: <title>姉小路直子と銀色の死神 初回限定版の通販・購入（みなとカーニバル）はメロンブックス | メロンブックス</title>
  # Example: <a href="https://www.melonbooks.co.jp/search/search.php?name=Purple%20Software&text_type=maker">Purple Software</a>
  # Example: <td><a href="https://www.melonbooks.co.jp/circle/index.php?circle_id=17433">黄昏フロンティア</a>
  _rx_brand_circle = re.compile(r'circle_id=[0-9]+">([^<>]+)</a>')
  def _parsebrand(self, h):
    """
    @param  h  unicode  html
    @return  unicode
    """
    r = skstr.findbetween(h, u'の通販・購入（', u'）')
    if not r:
      m = self._rx_brand_circle.search(h)
      if m:
        r = m.group(1)
    if r and '<' not in r:
      return unescapehtml(r)

  def _parseintro(self, h):
    """
    @param  h  unicode  html
    @return  unicode
    """
    ret = skstr.findbetween(h, '<div class="richeditor">', u'<!--')
    if ret:
      ret = ret.strip()
    return ret

  # Example: <td class="price">¥1,080 <br>
  def _parseprice(self, h):
    """
    @param  h  unicode  html
    @return  int
    """
    try: return int(skstr.findbetween(h, u'<td class="price">¥', '<').strip().replace(',', ''))
    except: return 0

if __name__ == '__main__':
  api = ProductApi()
  k = 114240 # ecchi
  k = 117934 # non-ecchi, event
  k = 113958 # 神のラプソディ
  k = 110968 # クロノクロック
  #k = 32000 # 魔理沙と6つのキノコ
  print '-' * 10
  q = api.query(k)
  for k,v in q.iteritems():
    print k,':',v

# EOF
