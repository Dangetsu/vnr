# coding: utf8
# work.py
# 11/26/2013 jichi

__all__ = 'WorkApi',

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import re
from datetime import datetime
from sakurakit import sknetio
#from sakurakit.skdebug import dwarn
from sakurakit.skstr import unescapehtml

class WorkApi(object):
  ENCODING = 'utf8'

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
    if url:
      reviewcount = self._parsereviewcount(h)
      ret = {
        'url': url, # str or None
        'otome': '/girls/' in url, # bool not None
        'rpg': self._parserpg(h), # bool not None
        'ecchi': self._parseecchi(h), # bool not None
        'description': self._parsesec(self._rx_sec_desc, h), # unicode or None
        'characterDescription': self._parsecharasec(h), # unicode
        'title': self._parsetitle(h), # unicode or None
        'brand': self._parsebrand(h), # unicode or None
        'image': self._parseimage(h), # unicode or None
        'price': self._parseprice(h) or 0, # int not None
        'date': self._parsedate(h), # datetime or None
        'filesize': self._parsefilesize(h), # int not None
        'keywords': self._parsekeywords(h) or [], # [unicode]
        'tags': list(self._iterparsetags(h)), # [unicode]
        'sampleimages': list(self._iterparsesampleimages(h)), # [str]

        'artist': self._parsecreator(self._rx_artist, h), # unicode or None
        'writer': self._parsecreator(self._rx_writer, h), # unicode or None
        'musician': self._parsecreator(self._rx_musician, h), # unicode or None

        'reviewcount': reviewcount or 0, # int
        'review': self._parsesec(self._rx_sec_review, h) if reviewcount else None,
      }
      ret.update(self._iterparsefields(h))
      return ret

  _re_fields = (
    # Example:
    # http://www.dlsite.com/maniax/work/=/product_id/RJ107332.html
    # <tr><th>シリーズ名&nbsp;:&nbsp;</th><td><a href="http://www.dlsite.com/maniax/fsr/=/keyword/%E3%82%B3%E3%82%B9%E3%83%97%E3%83%ACRPG%20SRI0000006000/from/work.series">コスプレRPG</a></td></tr>
    ('series', re.compile(r'work\.series">([^<]+?)</a>')),
    # Example:
    # <tr><th>ホームページ&nbsp;:&nbsp;</th>
    # <td><a rel="nofollow" href="http://www.anos.jp/" target="_blank">http://www.anos.jp/</a></td>
    ('homepage', re.compile(ur'ホームページ.*?href="([^"]+?)"', re.DOTALL)),
  )
  def _iterparsefields(self, h):
    """
    @param  h  unicode
    @yield  (str key, unicode or None)
    """
    for k,rx in self._re_fields:
      m = rx.search(h)
      if m:
        yield k, unescapehtml(m.group(1))

  def _parseecchi(self, h):
    """
    @param  h  unicode
    @return  bool
    """
    return u'class="work_genre">全年齢' not in h

  def _parserpg(self, h):
    """
    @param  h  unicode
    @return  bool
    """
    return '/work_type/RPG/' in h

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

  #_rx_meta_desc = __makemetarx('name="description"')
  _rx_meta_keywords = __makemetarx('name="keywords"')
  _rx_meta_title = __makemetarx('property="og:title"')
  _rx_meta_url = __makemetarx('property="og:url"')
  _rx_meta_img = __makemetarx('property="og:image"')

  def _parseurl(self, h):
    """
    @param  h  unicode  html
    @return  str or None
    """
    return self._parsemeta(self._rx_meta_url, h)
    #if t:
    #  return unescapehtml(t)

  _rx_title = re.compile(r' \[.*')
  def _parsetitle(self, h):
    """
    @param  h  unicode  html
    @return  unicode or None
    """
    t = self._parsemeta(self._rx_meta_title, h)
    if t:
      return unescapehtml(self._rx_title.sub('', t)).strip()

  def _parsekeywords(self, h):
    """
    @param  h  unicode  html
    @return  [unicode] or None
    """
    t = self._parsemeta(self._rx_meta_keywords, h)
    if t:
      return unescapehtml(t).split(',')

  def _parsesampleimage(self, h):
    """
    @param  h  unicode  html
    @return  str or None
    """
    return self._parsemeta(self._rx_meta_img, h)

  def _parseimage(self, h):
    """
    @param  h  unicode  html
    @return  str or None
    """
    t = self._parsesampleimage(h)
    if t:
      return t.replace('_img_sam.jpg', '_img_main.jpg')

  # Example: <span itemprop="brand">HypnoLife</span>
  _rx_brand = re.compile(r'itemprop="brand">([^<]+?)<')
  def _parsebrand(self, h):
    """
    @param  h  unicode  html
    @return  unicode or None
    """
    m = self._rx_brand.search(h)
    if m:
      return unescapehtml(m.group(1)).replace(" / ", ',').replace(u"／", ',')

  # Example: <strong class="price">1,890円</strong>
  _rx_price = re.compile(r'class="price">([0-9,]+)')
  def _parseprice(self, h):
    """
    @param  h  unicode  html
    @return  int not None
    """
    m = self._rx_price.search(h)
    if m:
      try: return int(m.group(1).replace(',',''))
      except ValueError: pass

  # Example:
  # <th>販売日&nbsp;:&nbsp;</th>
  # <td><a href="http://www.dlsite.com/soft/new/=/year/2013/mon/05/day/31/cyear/2013/cmon/05">2013年05月31日</a></td></tr>
  _rx_date = re.compile(ur'(\d{4})年(\d{2})月(\d{2})日')
  def _parsedate(self, h):
    """
    @param  h  unicode  html
    @return  datetime object or None
    """
    m = self._rx_date.search(h)
    if m:
      #datetime.strptime(t, u'%Y年%m月%d日')
      try: return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
      except: pass

  # Example: 12345Byte
  _rx_filesize_gb = re.compile(r'nbsp;([0-9\.]+)GB') # 総計&nbsp;15.9GB<br />
  #_rx_filesize_mb = re.compile(r'nbsp;([0-9\.]+)MB')
  _rx_filesize_b = re.compile(r'(\d+)Byte')
  def _parsefilesize(self, h):
    """
    @param  h  unicode  html
    @return  int not None
    """
    m = self._rx_filesize_gb.search(h)
    if m:
      try: return long(float(m.group(1)) * 1024 * 1024 * 1024)
      except: pass
    #m = self._rx_filesize_mb.search(h)
    #if m:
    #  try: return long(float(m.group(1)) * 1024 * 1024)
    #  except: pass
    m = self._rx_filesize_b.search(h)
    if m:
      try: return long(m.group(1))
      except: pass
    return 0

  def __makesectionrx(name):
    """
    @param  name  str
    @return  re
    """
    return re.compile(r'.*?'.join((
      re.escape(r'<!-- %s -->' % name),
      re.escape(r'<!-- /%s -->' % name),
    )), re.DOTALL)

  def _parsesec(self, rx, h):
    """
    @param  h  unicode  html
    @return  str or None
    """
    m = rx.search(h)
    if m:
      return m.group().replace('="//', '="http://')

  _rx_sec_review = __makesectionrx('work_review_list')

  #_rx_sec_desc = __makesectionrx('work_story')
  _rx_sec_desc = re.compile(r'.*'.join(( # use .* instead of .*? to keep text as much as possible
    re.escape(r'<div itemprop="description"'),
    r'(?:<!-- spec -->|<!-- /work_story -->)', # sample game: http://www.dlsite.com/maniax/work/=/product_id/RJ143025
  )), re.DOTALL)

  # Example: www.dlsite.com/maniax/work/=/product_id/RJ079473.html
  _rx_sec_chara = re.compile(r'(.*?)'.join((
    ur'<div class="[^"]*?"><h.>キャラクター紹介</h.></div>',
    r"(?:<!--|<script)", # stop before next section or script
  )), re.DOTALL)
  def _parsecharasec(self, h):
    """
    @param  h  unicode  html
    @return  str or None
    """
    m = self._rx_sec_chara.search(h)
    if m:
      ret = m.group(1).rstrip()
      ret = ret.replace('="//', '="http://')
      return ret

  # Example
  # <p class="float_l review_count">レビュー数&nbsp;:&nbsp;<span class="review_work_count">9件</span></p>
  _rx_reviewcount = re.compile(ur'review_work_count">([0-9]+)件')
  def _parsereviewcount(self, h):
    """
    @param  h  unicode  html
    @return  int or None
    """
    m = self._rx_reviewcount.search(h)
    if m:
      try: return int(m.group(1))
      except ValueError: pass

  def __makecreatorxp(name):
    """
    @param  name  unicode
    @return  re
    """
    return re.compile(name + r'.*?>([^<]+?)</a>', re.DOTALL)

  _rx_artist = __makecreatorxp(u'原画')
  _rx_writer = __makecreatorxp(u'シナリオ')
  _rx_musician = __makecreatorxp(u'音楽')

  def _parsecreator(self, rx, h):
    """
    @param  rx  re
    @param  h  unicode  html
    @return  str or None
    """
    m = rx.search(h)
    if m:
      t = m.group(1)
      if t:
        return unescapehtml(t)

  _rx_tag = re.compile(r'>([^<]+?)</a>')
  def _iterparsetags(self, h):
    """
    @param  h  unicode  html
    @yield  uincode
    """
    g = self._parsemaingenre(h)
    if g:
      for m in self._rx_tag.finditer(g):
        for it in unescapehtml(m.group(1)).split('/'):
          yield it

  # Tags, example:
  # <div class="main_genre"><a href="http://www.dlsite.com/soft/fsr/=/genre/281/from/work.genre">同級生/同僚</a>&nbsp;<a href="http://www.dlsite.com/soft/fsr/=/genre/016/from/work.genre">ファンタジー</a></div></td></tr>
  _rx_main_genre = re.compile(r'<div class="main_genre">(.+?)</div>')
  def _parsemaingenre(self, h):
    """
    @param  h  unicode  html
    @return  unicode or None
    """
    m = self._rx_main_genre.search(h)
    if m:
      return m.group(1)

  # Emaple: http://www.dlsite.com/soft/work/=/product_id/VJ007727.html
  # href="//img.dlsite.jp/modpub/images2/work/professional/VJ008000/VJ007727_img_smpa1.jpg"
  _rx_sampleimages = re.compile(r'(//img.dlsite.jp/[a-zA-Z0-9/_]+?_img_smpa[0-9]+.jpg)"')
  def _iterparsesampleimages(self, h):
    """
    @param  h  unicode  html
    @yield  uincode
    """
    for m in self._rx_sampleimages.finditer(h):
      yield 'http:' + m.group(1)

if __name__ == '__main__':
  api = WorkApi()
  url = 'http://www.dlsite.com/soft/work/=/product_id/VJ007727.html'
  url = 'http://www.dlsite.com/soft/work/=/product_id/VJ007207.html'
  url = 'http://www.dlsite.com/maniax/work/=/product_id/RJ107332.html'
  url = 'http://www.dlsite.com/pro/work/=/product_id/VJ004288.html'
  url = 'http://www.dlsite.com/girls/work/=/product_id/RJ091967.html'
  url = 'http://www.dlsite.com/pro/work/=/product_id/VJ006763.html'
  url = 'http://www.dlsite.com/maniax/work/=/product_id/RJ079473.html' # for testing chara
  url = 'http://www.dlsite.com/maniax/work/=/product_id/RJ143025' # Rondo DUO
  url = 'http://www.dlsite.com/maniax/work/=/product_id/RJ103041.html'
  q = api.query(url)
  #print q['description']
  #print q['review'].encode('utf8')
  print q['url']
  print q['title']
  print q['image']
  print q['date']
  print q['homepage']
  print q['musician']
  print q['artist']
  print q['sampleimages']
  print q['series']
  print q['rpg']
  print q['filesize']
  print q['date']
  for it in q['tags']:
    print it
  print '-' * 10
  print q['characterDescription']
  print q['description']

# EOF
