# coding: utf8
# article.py
# 9/27/2014 jichi

__all__ = 'ArticleApi',

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import re
from datetime import datetime
from sakurakit import sknetio
#from sakurakit.skdebug import dwarn
from sakurakit.skstr import unescapehtml

def clean_title(title): # unicode -> unicode
  return title.replace("(PC)", "")

class ArticleApi(object):
  ENCODING = 'sjis'
  COOKIES = {'afg':'0'}

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
    return sknetio.getdata(url, gzip=True, session=self.session, cookies=self.COOKIES)

  def query(self, url):
    """
    @param  url  str
    @return  {kw} or None
    """
    h = self._fetch(url)
    if h:
      h = h.decode(self.ENCODING, errors='ignore')
      if h: # and u'該当作品がありません' not in h:
        ret = self._parse(h)
        if ret and ret['title']: # return must have title
          return ret

  def _parse(self, h):
    """
    @param  h  unicode  html
    @return  {kw}
    """
    url  = self._parseurl(h)
    if not url:
      return
    id = self._parseurlid(url)
    if not id:
      return
    path = self._parseurlpath(url)
    if not path:
      return
    title = self._parsetitle(h)
    if not title:
      return

    ecchi = self._parseecchi(h)
    otome = '/bl/' in url # bool not None

    img = ('blimg' if otome else 'img')
    if ecchi:
      img += '18'

    sampleimage = self._parsesampleimage(h, id, img, path) #[str url]
    image = self._guessimage(h, id, img, path) #[str url]

    return {
      'url': url, # str not None
      'id': id, # str
      'title': clean_title(title), # unicode not None
      'date': self._parsedate(h), # datetime or None
      'ecchi': ecchi, # bool
      'otome': otome, # bool
      'doujin': self._parsedoujin(h), # bool
      'series': self._parseseries(h), # unicode or None
      'image': image if sampleimage or image in h else None,
      'sampleimage': sampleimage, # str url
      'brand': self._parsebrand(h),
      'comment': self._parsecomment(h),
      'artists': self._parseartists(h), # [unicode] or None
      'price': self._parseprice(h), # int not None
      'description': self._parsedesc(h), # unicode or None
    }

  _rx_url_id = re.compile(r"/([0-9]+)\.html")
  def _parseurlid(self, url):
    """
    @param  str
    @return  str
    """
    m = self._rx_url_id.search(url)
    if m:
      return m.group(1)

  _rx_url_path = re.compile(r"/article/(.+)/[0-9]+\.html")
  def _parseurlpath(self, url):
    """
    @param  str
    @return  str or None
    """
    m = self._rx_url_path.search(url)
    if m:
      return m.group(1)

  # <!--Twitter,Facebook-->
  # <table style="width:100%; table-layout:fixed; border-collapse:collapse;">
  #   <tr>
  #     <td style="padding:20px 0px 0px 25px;" align="left">
  #       <a href="https://twitter.com/share" class="twitter-share-button"
  #         data-url="http://www.toranoana.jp/bl/article/04/0010/24/45/040010244502.html"
  #         data-via="tora_ec_jyosei"
  #         data-text="誰ガ為に鬼は啼く"
  #         data-hashtags="同人アイテム"
  #         data-related="" data-dnt="" data-count="horizontal" data-size="medium" data-lang="ja"
  #       >ツイート</a>
  #     </td>
  #   </tr>
  # </table>

  _rx_url = re.compile('data-url="([^"]+)')
  def _parseurl(self, h):
    """
    @param  h  unicode  html
    @return  str or None
    """
    m = self._rx_url.search(h)
    if m:
      return m.group(1)

  _rx_title = re.compile('data-text="([^"]+)')
  def _parsetitle(self, h):
    """
    @param  h  unicode  html
    @return  str or None
    """
    m = self._rx_title.search(h)
    if m:
      return unescapehtml(m.group(1))

  # Example: http://www.toranoana.jp/mailorder/article/21/0006/53/25/210006532528.html
  # url: http://img.toranoana.jp/img18/21/0006/53/25/210006532528-1.jpg
  def _guessimage(self, h, id, img, path):
    """
    @param  h  unicode  html
    @param  id  int
    @param  img  str
    @param  path  str
    @return  str or None
    """
    return "http://img.toranoana.jp/%s/%s/%s-1.jpg" % (img, path, id)

  def _parsesampleimage(self, h, id, img, path):
    """
    @param  h  unicode  html
    @param  id  int
    @param  img  str
    @param  path  str
    @return  str or None
    """
    if "_popup1.html" in h:
      return "http://img.toranoana.jp/popup_%s/%s/%s-1p.jpg" % (img, path, id)

  # Sample table
  # <tr>
  #   <td class="DetailSummary_L">サークル</td>
  #   <td class="DetailData_L"><a href="/bl/cit/circle/09/42/5730303734323039/a5d7a5eaa5f3a5bba5b9a5afa5e9a5a6a5f3_01.html">プリンセスクラウン</a></td>
  #   <td class="DetailSummary_R">種別</td>
  #   <td class="DetailData_R">同人ソフト</td>
  # </tr>
  # <tr>
  #   <td class="DetailSummary_L">主な作家</td>
  #   <td class="DetailData_L">
  #     <a href="/bl/cit/author/42/a5c1a5cfa5eb_01.html">チハル</a>
  #     <a href="/bl/cit/author/25/bab0cceea4a4a4afa4a8_01.html">紺野いくえ</a>
  #   </td>
  #   <td class="DetailSummary_R">発行日</td>
  #   <td class="DetailData_R">2010/10/10</td>
  # </tr>
  # <tr>
  #   <td class="DetailSummary_L">カテゴリ</td>
  #   <td class="DetailData_L">
  #     <a href="/bl/cit/genre/4/895_01.html">薄桜鬼</a>
  #   </td>
  #   <td class="DetailSummary_R">サイズ</td>
  #   <td class="DetailData_R">CD-ROM 18p</td>
  # </tr>
  #   <td class="DetailSummary_L">メインキャラ</td>
  #   <td class="DetailData_L">斎藤一、沖田総司、土方歳三</td>
  #   <td class="DetailSummary_R">指定</td>
  #   <td class="DetailData_R"><span class="Adult">※18禁</span><span class="Ladies">[女性向]</span></td>
  # </tr>
  # <tr>
  #   <td class="DetailSummary_L">コメント</td>
  #   <td colspan="3" class="DetailData_Comment">薄桜鬼同人乙女ゲーム!時代が着物から洋装へと移り変わる中、新選組もまた激動の時を迎えていた。胸を締め付けられる切なさと頬が熱くなる甘い一時を、ここに『2人で過ごした時は、貴方にとって特別でしたか?私はとても――幸せでした』斎千・沖千・土千</td>
  # </tr>
  def __maketablerx(name):
    """
    @param  name  str
    @return  re
    """
    return re.compile(r'.*?'.join((
      r'DetailSummary[^>]*?">%s</td>' % name,
      r'DetailData[^>]*?>(.*?)</td>',
    )), re.DOTALL)

  _rx_ecchi = __maketablerx(u"指定")
  def _parseecchi(self, h):
    """
    @param  h  unicode  html
    @return  bool
    """
    m = self._rx_ecchi.search(h)
    if m:
      return u"18禁" in m.group(1)
    return False

  _rx_doujin = __maketablerx(u"種別")
  def _parsedoujin(self, h):
    """
    @param  h  unicode  html
    @return  bool
    """
    m = self._rx_doujin.search(h)
    if m:
      return u"同人" in m.group(1)
    return False

  _rx_comment = __maketablerx(u"コメント")
  def _parsecomment(self, h):
    """
    @param  h  unicode  html
    @return  unicode
    """
    m = self._rx_comment.search(h)
    if m:
      return unescapehtml(m.group(1))

  @staticmethod
  def __parsetableanchor(h, rx):
    """
    @param  h  unicode  html
    @param  rx  re
    @return  unicode or None
    """
    m = rx.search(h)
    if m:
      ret = m.group(1)
      i = ret.find('>')
      j = ret.rfind('<')
      if i != -1 and j != -1:
        return unescapehtml(ret[i+1:j])

  _rx_brand = __maketablerx(u"(?:メーカー|サークル)")
  def _parsebrand(self, h):
    """
    @param  h  unicode  html
    @return  unicode or None
    """
    return self.__parsetableanchor(h, self._rx_brand)

  _rx_series = __maketablerx(u"カテゴリ")
  def _parseseries(self, h):
    """
    @param  h  unicode  html
    @return  unicode or None
    """
    return self.__parsetableanchor(h, self._rx_series)

  # Example: 2014/09/14
  _rx_date = __maketablerx(u"発[売行]日")
  def _parsedate(self, h):
    """
    @param  h  unicode  html
    @return  datetime object or None
    """
    m = self._rx_date.search(h)
    if m:
      try: return datetime.strptime(m.group(1), u'%Y/%m/%d')
      except: pass

  _rx_href_content = re.compile('>([^<]+)</a>')

  _rx_artists = __maketablerx(u"(?:原画|主な作家)")
  def _parseartists(self, h):
    """
    @param  h  unicode  html
    @return  [unicode] or None
    """
    m = self._rx_artists.search(h)
    if m:
      h = m.group(1)
      if "<a" not in h:
        return h.split()
      else:
        return [unescapehtml(m.group(1)) for m in self._rx_href_content.finditer(h)]

  # Example: 価格：<span class="bold">1,400</span><b>円</b>（＋税）<br>
  _rx_price = re.compile(ur'価格：<span class="bold">([0-9,]+)</span><b>円</b>')
  def _parseprice(self, h):
    """
    @param  h  unicode  html
    @return  int not None
    """
    try: return int(self._rx_price.search(h).group(1).replace(',', ''))
    except: return 0

  def _parsedesc(self, h):
    """
    @param  h  unicode  html
    @return  unicode or None
    """
    i = h.find('<div class="div_tabcmt">')
    if i != -1:
      j = h.find('<table', i)
      if j != -1:
        ret = unescapehtml(h[i:j]).rstrip()
        while ret.endswith('<br>'): # remove trailing "<br>"
          ret = ret[:-5].rstrip()
        return ret

if __name__ == '__main__':
  api = ArticleApi()
  url = "http://www.toranoana.jp/mailorder/article/21/0006/54/35/210006543567.html"
  url = "http://www.toranoana.jp/mailorder/article/21/0006/53/23/210006532321.html" # レミニセンス
  url = "http://www.toranoana.jp/mailorder/article/21/0006/53/25/210006532528.html" # Steins Gate
  url = "http://sakuradite.org/proxy/toranoana/www/mailorder/article/21/0006/54/35/210006543567.html" # レミニセンス RE
  url = "http://www.toranoana.jp/bl/article/04/0010/24/45/040010244502.html"
  url = "http://www.toranoana.jp/bl/article/04/0030/24/08/040030240889.html"
  q = api.query(url)
  #print q['description']
  #print q['review'].encode('utf8')
  print q['url']
  print q['title']
  print 'image', q['image']
  print q['sampleimage']
  print q['brand']
  print q['doujin']
  print q['date']
  print q['comment']
  for i in q['artists']:
    print i
  print q['price']
  #print q['description']

# EOF
