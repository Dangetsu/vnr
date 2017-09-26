# coding: utf8
# soft.py
# 10/20/2013 jichi

__all__ = 'SoftApi',

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import re
from sakurakit import sknetio
from sakurakit.skcontainer import uniquelist
from sakurakit.skstr import multireplacer, unescapehtml
#from sakurakit.skdebug import dwarn

DEFAULT_HOST = "http://www.getchu.com"
_QUERY_PATH = "soft.phtml?id=%s"

def resethost():
  sethost(DEFAULT_HOST)
def sethost(url):
  api = SoftApi
  api.HOST = url + '/'
  api.API = api.HOST + _QUERY_PATH

class SoftApi(object):
  HOST = DEFAULT_HOST + '/'
  API = HOST + _QUERY_PATH
  ENCODING = 'euc-jp'
  COOKIES = {'getchu_adalt_flag':'getchu.com'}

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
          ret['url'] = "http://getchu.com/soft.phtml?id=%s" % id # str
          img = "brandnew/%s/c%spackage.jpg" % (id, id)    # str, example: www.getchu.com/brandnew/756396/c756396package.jpg
          ret['img'] = self.HOST + img if img in h else '' # str
          #self._patch(ret, id)
          return ret

  #def _patch(self, kw, id):
  #  """
  #  @param  kw  {kw}
  #  @param  id  long
  #  """
  #  chara = kw['characters']
  #  if chara:
  #    for it in chara:
  #      it['img'] = 'http://www.getchu.com/brandnew/%s/c%schara%s.jpg' % (id, id, it['id'])

  def _parse(self, h):
    """
    @param  h  unicode  html
    @return  {kw}
    """
    meta = self._parsemetadesc(h)
    if meta:
      title = meta.get(u"タイトル")
      if not title:
        title = self._parsetitle(h)
      if title:
        title = self._fixtitle(title)
        try: price = int(self._parseprice(h))
        except (ValueError, TypeError): price = 0

        # Use fillter.bool to remove empty scenario
        try: writers = filter(bool, meta[u"シナリオ"].replace(u"、他", '').split(u'、'))
        except Exception: writers = []

        artists = []
        sdartists = []
        t = meta.get(u"原画")
        if t:
          sd1 = u"（SD原画）"
          sd2 = u"（アバター）"
          for it in t.split(u'、'):
            if it and it != u"他":
              if it.endswith(sd1):
                it = it.replace(sd1, '')
                sdartists.append(it)
              elif it.endswith(sd2):
                it = it.replace(sd2, '')
                sdartists.append(it)
              else:
                artists.append(it)

        # See: http://www.getchu.com/pc/genre.html
        subgenres = uniquelist(self._iterparsesubgenres(h))
        categories = uniquelist(self._iterparsecateories(h))
        ret = {
          'title': title, # unicode or None
          'writers': writers, # [unicode]
          'artists': artists, # [unicode]
          'sdartists': sdartists, # [unicode]
          'musicians': list(self._iterparsemusicians(h)), # [unicode]
          'brand': self._fixbrand(meta.get(u"ブランド") or meta.get(u"サークル")), # unicode or None
          'subgenres': subgenres, # [unicode]
          'categories': categories, # [unicode]
          'otome': u"乙女ゲー" in categories, # bool
          'price': price,                     # int
          #'imageCount': self._parseimagecount(h),
          'sampleImages': list(self._iterparsesampleimages(h)), # [kw]
          'descriptions': list(self._iterparsedescriptions(h)), # [unicode]
          'characterDescription': self._parsecharadesc(h), # unicode
          #'comics': list(self._iterparsecomics(h)),   # [kw]
          'banners': list(self._iterparsebanners(h)), # [kw]
          'videos': uniquelist(self._iterparsevideos(h)),   # [kw]

          # Disabled
          'characters': list(self._iterparsecharacters(h)) or list(self._iterparsecharacters2(h)), # [kw]
          #'characters': [],
        }
        ret.update(self._iterparsefields(h))
        return ret

  def _fixtitle(self, t):
    """
    @param  t  unicode
    @return  unicode
    """
    # http://www.getchu.com/soft.phtml?id=721680
    return t.replace(u'＜特価セール', '').strip()

  def _fixbrand(self, t):
    """
    @param  t  unicode
    @return  unicode
    """
    if t:
      return t.replace(" / ", ',')

  #def _fixcreators(self, t):
  #  """
  #  @param  unicode
  #  @return  unicode or None
  #  """
  #  if t:
  #    return t.replace(u"、他", '')

  _re_fields = (
    # Example:
    # <b>Developer:</b>
    # <a href="http://store.steampowered.com/search/?developer=Idea%20Factory%2C%20Inc.&snr=1_5_9__408">Idea Factory, Inc.</a>
    ('genre', re.compile(ur'ジャンル：.+?>([^><]+?)<')),

    # Example: title="同じ発売日の同ジャンル商品を開く">2013/10/25</a>
    # str or None, such as 2013/10/25
    ('date', re.compile(ur'同じ発売日の同ジャンル商品を開く">([0-9/]+?)</a>')),
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

  # Example:
  # <TR><TD valign="top" align="right">カテゴリ：</TD><TD align="top">シミュレーションRPG、<a href='php/search.phtml?category[0]=C3_F003'>ポリゴン・3D</a>、<a href='php/search.phtml?category[0]=C3_F026'>バトル</a>、<a href='php/search.phtml?category[0]=C3_F004'>アニメーション</a> <a href="/pc/genre.html">[一覧]</a></TD></TR>
  def __maketdrx(name, *args):
    return re.compile(name + ur'：</TD><TD align="top">(.+?)</TD>', *args)

  def _parsetd(self, rx, h):
    """
    @param  h  unicode  html
    @return  unicode or None
    """
    m = rx.search(h)
    if m:
      return unescapehtml(m.group(1))

  _rx_td_musician = __maketdrx(u'音楽')
  #_rx_musician = re.compile(r'>([^><]+?)<')
  def _iterparsemusicians(self, h):
    """
    @param  h  unicode  html
    @yield  unicode
    """
    line = self._parsetd(self._rx_td_musician, h)
    if line:
      for it in line.split(u'、'):
        yield it

  _rx_td_category = __maketdrx(u'カテゴリ')
  _rx_category = re.compile(r'>([^><]+?)<')
  def _iterparsecateories(self, h):
    """
    @param  h  unicode  html
    @yield  unicode
    """
    line = self._parsetd(self._rx_td_category, h)
    if line:
      for m in self._rx_category.finditer(line):
        word = m.group(1)
        t = word.replace(u'、', '').strip()
        if t and t != u'[一覧]':
          for it in t.split(u'・'):
            yield it

  _rx_td_subgenre = __maketdrx(u'サブジャンル\s*', re.DOTALL)
  _rx_subgenre = re.compile(r'>([^><]+?)<')
  def _iterparsesubgenres(self, h):
    """
    @param  h  unicode  html
    @yield  unicode
    """
    line = self._parsetd(self._rx_td_subgenre, h)
    if line:
      for m in self._rx_subgenre.finditer(line):
        word = m.group(1)
        t = word.replace(u'、', '').strip()
        # See: http://www.getchu.com/php/sub_genre.phtml
        if t and t != u'[一覧]' and t != u"アドベンチャー" and t != u"廉価版・新装版" and t != u"その他":
          for it in t.split(u'・'):
            yield it

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

  _rx_meta_desc = __makemetarx('name="description"')
  def _parsemetadesc(self, h):
    """
    @param  h  unicode  html
    @return  kw
    """
    ret = {}
    desc = self._parsemeta(self._rx_meta_desc, h)
    if desc:
      desc = unescapehtml(desc)
      for item in desc.split(','):
        l = item.split(u"：")
        if len(l) >= 2:
          ret[l[0]] = l[1]
    return ret

  _rx_meta_kw = __makemetarx('name="keywords"')
  def _parsemetakw(self, h):
    """
    @param  h  unicode  html
    @return  [unicode]
    """
    t = self._parsemeta(self._rx_meta_kw, h)
    if t:
      return t.split(',')

  def _parsetitle(self, h):
    """
    @param  h  unicode  html
    @return  unicode
    """
    kw = self._parsemetakw(h)
    if kw:
      return unescapehtml(kw[0])

  # Example: 価格：	￥7,140 (税抜￥6,800)
  #_rx_price = re.compile(ur'￥([0-9,]+?) \(税抜')
  # ￥7,500 (税込￥8,100)
  _rx_price = re.compile(ur'税込￥([0-9,]+)')
  def _parseprice(self, h):
    """
    @param  h  unicode  html
    @return  unicode or None
    """
    # http://stackoverflow.com/questions/2802168/find-last-match-with-python-regular-expression
    m = self._rx_price.search(h)
    if m:
      try: return int(m.group(1).replace(',',''))
      except (ValueError, TypeError): pass

  #_rx_title = re.compile(ur'タイトル：([^"]+?)[,"]')
  #def _parsetitle(self, h):
  #  """
  #  @param  h  unicode  html
  #  @return  unicode or None
  #  """
  #  # http://stackoverflow.com/questions/2802168/find-last-match-with-python-regular-expression
  #  m = self._rx_title.search(h)
  #  if m:
  #    return unescapehtml(m.group(1).strip())

  #_rx_sample = re.compile(r'SAMPLE([0-9]+)')
  #def _parseimagecount(self, h):
  #  """
  #  @param  h  unicode  html
  #  @return  int not None
  #  """
  #  # http://stackoverflow.com/questions/2802168/find-last-match-with-python-regular-expression
  #  m = None
  #  for m in self._rx_sample.finditer(h): pass
  #  return int(m.group(1)) if m else 0

  _rx_video = re.compile(r"(?<=www\.youtube\.com/v/)[a-zA-Z0-9_-]+")
  def _iterparsevideos(self, h):
    """
    @param  h  unicode  html
    @yield  str
    """
    for m in self._rx_video.finditer(h):
      vid = m.group()
      yield vid

  _rx_sampleimage = re.compile(r'brandnew/[^"]*?sample([0-9]+).jpg')
  def _iterparsesampleimages(self, h):
    """
    @param  h  unicode  html
    @yield  str
    """
    # http://stackoverflow.com/questions/2802168/find-last-match-with-python-regular-expression
    for m in self._rx_sampleimage.finditer(h):
      yield self.HOST + m.group()

  def __maketablerx(name):
    """
    @param  name  unicode
    @return  re
    """
    return re.compile(
        #r'<div class="tabletitle">&nbsp;%s</div>.*?<BR clear="all"></div>' % name,
        r'<div class="tabletitle">%s</div>.*?<BR clear="all"></div>' % name,
        re.IGNORECASE|re.DOTALL)

  def __maketablesrx(names):
    """
    @param  names  [unicode]
    @return  re
    """
    #return __maketablerx(r"[^>]*?(?:%s)[^<]*?" % '|'.join(names))
    pat = r"[^>]*?(?:%s)[^<]*?" % '|'.join(names)
    return re.compile(
        #r'<div class="tabletitle">&nbsp;%s</div>.*?<BR clear="all"></div>' % name,
        r'<div class="tabletitle">%s</div>.*?<BR clear="all"></div>' % pat,
        re.IGNORECASE|re.DOTALL)
  #_rx_intro = __maketablerx(u"商品紹介")
  #_rx_story = __maketablerx(u"ストーリー")
  #def _parsetable(self, h, rx):
  #  """
  #  @param  h  unicode  html
  #  @return  unicode or None
  #  """
  #  m = rx.search(h)
  #  if m:
  #    return unescapehtml(
  #        self._removescripts(
  #          self._replacelinks(
  #            m.group())))

  _rx_desc = __maketablesrx((
    u"商品紹介", u"ストーリー", u"システム紹介",
    u"美少女ゲーム大賞", #r"Getchu\.com",
    #u"げっちゅ屋特典", u"キャンペーン", u"応援バナー",
    #u"キャラクター",
  ))
  def _iterparsedescriptions(self, h):
    """
    @param  h  unicode  html
    @yield  unicode
    """
    for m in self._rx_desc.finditer(h):
      yield unescapehtml(
          self._removescripts(
            self._replacelinks(
              m.group())))

  def _parsecharadesc(self, h):
    """
    @param  h  unicode  html
    @return  unicode
    """
    START = u'<div class="tabletitle">&nbsp;キャラクター</div>'
    STOP1 = '<a name="sample" id="sample">'
    STOP2 = u'<!-- ▼recommend▼ -->'
    start = h.find(START)
    if start > 0:
      stop = h.find(STOP1, start)
      if stop == -1:
        stop = h.find(STOP2, start)
      if stop != -1:
        return unescapehtml(
            self._removescripts(
              self._replacelinks(
                h[start:stop])))

  _rx_comics = __maketablesrx((
    u"コミックス",
  ))
  def _iterparsecomics(self, h):
    """
    @param  h  unicode  html
    @yield  str
    """
    for m in self._rx_comics.finditer(h):
      for it in self._iterparseimages(m.group()):
        yield it

  _rx_banner = __maketablesrx((
    u"バナー",
    u"キャンペーン",
    #u"コミックス",
  ))
  def _iterparsebanners(self, h):
    """
    @param  h  unicode  html
    @yield  str
    """
    for m in self._rx_banner.finditer(h):
      for it in self._iterparseimages(m.group()):
        yield it

  _rx_image = re.compile(r'src="\.?/?([^"]*?jpg)"', re.IGNORECASE)
  def _iterparseimages(self, h):
    """
    @param  h  unicode  html
    @yield  str
    """
    s = set()
    for m in self._rx_image.finditer(h):
      img = m.group(1)
      if ':' not in img:
        img = self.HOST + img.replace('_s.jpg', '.jpg')
      if img not in s:
        s.add(img)
        yield img

  _repl_links = staticmethod(multireplacer({
    r'<a href="./': r'<a href="#{h}', r'<A href="./': r'<a href="#{h}',
    r'<a href="/': r'<a href="#{h}', r'<A href="/': r'<a href="#{h}',
    r'<a href="': r'<a href="#{h}', r'<A href="': r'<a href="#{h}',
    r'<img src="./': r'<img src="#{h}', r'<IMG src="./': r'<img src="#{h}',
    r'<img src="/': r'<img src="#{h}', r'<IMG src="/': r'<img src="#{h}',
    r'<img src="': r'<img src="#{h}', r'<IMG src="': r'<img src="#{h}',
  })) #, flags=re.IGNORECASE)
  def _replacelinks(self, h):
    """
    @param  h  unicode  html
    @return  unicode or None
    """
    return self._repl_links(h).replace("#{h}http", "http").replace("#{h}", self.HOST)

  _rx_scripts = re.compile(r'|'.join((
    ' onclick=".+?"',
    ' onkeypress=".+?"',
  )), flags=re.IGNORECASE|re.DOTALL)
  def _removescripts(self, h):
    """
    @param  h  unicode  html
    @return  unicode or None
    """
    return self._rx_scripts.sub('', h)

  # Latest game
  # Example:
  # <a name="chara1" id="chara1"></a>
  # <IMG src="./brandnew/748164/c748164chara1.jpg" alt="キャラ1" width="250" height="300" style="border:none;">
  # </TD>
  # <TD valign="middle" align="left" class="chara-text">
  # <DL style="line-height:150%"><DT><STRONG><h2 class="chara-name">主人公<br><charalist>エドワード</charalist> （エド）　CV：和音</h2></STRONG>
  _rx_characters = re.compile(r'id="chara([0-9]+)"(.+?)<charalist>(.+?)</charalist>(.*?)<', re.DOTALL)
  _rx_characters_img = re.compile(r'img src=".?/?(.+?)"', re.IGNORECASE) # ignore leading ./, './brandnew/%s/c%schara%s.jpg'
  _rx_characters_label = re.compile(r'class="chara-name">([^<]*)')
  _rx_characters_yomi1 = re.compile(ur'）.*')
  _rx_characters_yomi2 = re.compile(ur'.*（')
  _rx_characters_cv = re.compile(ur'.*：')      # remove leading CV
  def _iterparsecharacters(self, h):
    """
    @param  h  unicode  html
    @yield  {kw}
    """
    BAD_NAME = u"その他"
    for m in self._rx_characters.finditer(h):
      name = m.group(3)
      if name and name != BAD_NAME:
        before = unescapehtml(m.group(2))
        mm = self._rx_characters_img.search(before)
        img = self.HOST + mm.group(1) if mm else ''
        #img = 'http://www.getchu.com/brandnew/%s/c%schara%s.jpg' % (id, id, it['id'])
        mm = self._rx_characters_label.search(before)
        label = mm.group(1) if mm else ''
        yomi = cv = ''
        after = unescapehtml(m.group(4)).strip()
        if after:
          l = after.split("CV")
          if len(l) == 1:
            yomi = self._rx_characters_yomi1.sub('', after)
            yomi = self._rx_characters_yomi2.sub('', yomi)
          else:
            yomi = self._rx_characters_yomi1.sub('', l[0])
            yomi = self._rx_characters_yomi2.sub('', yomi)
            cv = self._rx_characters_cv.sub('', l[1])
        yield {
          'id': int(m.group(1)),  # int, character number, starting from 1
          'img': img, # twitter str key
          'label': unescapehtml(label), # str
          'name': unescapehtml(name).replace(u'　', ''), # unicode, \u3000
          'yomi': unescapehtml(yomi).replace(u'　', '') if yomi else '', # unicode
          'cv': unescapehtml(cv), # unicode
        }
      #h = h[m.end(0):]

  # Some old games such as Dies irae: http://www.getchu.com/soft.phtml?id=666077
  # It is not using charalist tag. Example:
  # <h2 class="chara-name">日常の象徴。剣道部所属。<br>綾瀬 香純 （あやせ かすみ）　CV：佐本二厘</h2></STRONG></DT>
  # <DD><b>身長：161cm　スリーサイズ：B86/ W60/ H85</b><br>
  # <br>
  _rx_characters2 = re.compile(r'id="chara([0-9]+)"(.+?)<h2 class="chara-name">(.+?)</h2>', re.DOTALL)
  def _iterparsecharacters2(self, h):
    """
    @param  h  unicode  html
    @yield  {kw}
    """
    BAD_NAME = u"その他"
    for m in self._rx_characters2.finditer(h):
      before = unescapehtml(m.group(2))
      mm = self._rx_characters_img.search(before)
      img = self.HOST + mm.group(1) if mm else ''
      #img = 'http://www.getchu.com/brandnew/%s/c%schara%s.jpg' % (id, id, it['id'])
      after = unescapehtml(m.group(3)).strip()
      l = filter(bool, after.split('<br>'))
      if len(l) == 1:
        label = ''
      elif l:
        label = l[0].strip()
        after = l[1].strip()
      else:
        continue
      l = after.split(u'（')
      if len(l) > 1:
        name = l[0]
        after = l[1]
      else:
        name = ''
      l = after.split("CV")
      if len(l) == 1:
        cv = ''
        yomi = self._rx_characters_yomi1.sub('', after)
        yomi = self._rx_characters_yomi2.sub('', yomi)
      else:
        cv = self._rx_characters_cv.sub('', l[1])
        yomi = self._rx_characters_yomi1.sub('', l[0])
        yomi = self._rx_characters_yomi2.sub('', yomi)
      if not name:
        name = yomi
        yomi = ''
      if name:
        # Example: http://www.getchu.com/soft.phtml?id=837244
        name = name.replace('<charalist>', '').strip()
      if name and name != BAD_NAME:
        yield {
          'id': int(m.group(1)),  # character number, starting from 1
          'img': img, # twitter img key
          'label': unescapehtml(label), # unicode
          'name': unescapehtml(name).replace(u'　', ''), # unicode, \u3000
          'yomi': unescapehtml(yomi).replace(u'　', '') if yomi else '', # unicode
          'cv': unescapehtml(cv), # unicode
        }
      #h = h[m.end(0):]

if __name__ == '__main__':
  api = SoftApi()
  k = 666077 # dies irae
  k = 748164 # baldrsky zero
  k = 634685
  k = 748164
  k = 747720
  k = 775493
  k = 651965 # コミュ
  k = 627665 # AlterEgo
  k = 771638 # 相州戦神館學園 八命陣
  k = 789990 # 女王蜂の王房 めのう編
  k = 774400
  k = 804521
  k = 718587 # レミニセンス
  k = 798624
  k = 809466 # ちぇ～んじ！
  k = 837244
  print '-' * 10
  q = api.query(k)
  for it in q['characters']:
    for k,v in it.iteritems():
      print k,':',v

  #for it in q['descriptions']:
  #  print it
  #print q['characterDescription']
  #for it in q['sampleImages']:
  #  print it

  #print q['price']
  #print q['otome']
  #print q['title']
  #print q['genre']
  ##print q['videos']
  #for it in q['categories']:
  #  print it
  #for it in q['subgenres']:
  #  print it
  ##for it in q['artists']:
  ##  print it
  #for it in q['sdartists']:
  #  print it
  #for it in q['musicians']:
  #  print it

# EOF
