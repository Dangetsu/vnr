# coding: utf8
# item.py
# 6/18/2014 jichi

__all__ = 'ItemApi',

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import re
from datetime import datetime
from sakurakit import sknetio
#from sakurakit.skdebug import dwarn
from sakurakit.skstr import unescapehtml
import defs

class ItemApi(object):
  HOST = "http://www.digiket.com"
  API = HOST + '/work/show/_data/ID=%s/'
  ENCODING = 'sjis'
  COOKIES = {'adult_check':'1'}

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
    return self.API % defs.toitemkey(id)

  def _fetch(self, url):
    """
    @param  url  str
    @return  str not int
    """
    return sknetio.getdata(url, gzip=True, cookies=self.COOKIES, session=self.session)

  def query(self, id):
    """
    @param  id  str or int  item ID
    @return  {kw} or None
    """
    id = defs.fromitemkey(id)
    key = defs.toitemkey(id)
    if id and key:
      url = self._makeurl(id)
      h = self._fetch(url)
      if h:
        h = h.decode(self.ENCODING, errors='ignore')
        if h and u'入力頂いた作品IDは既に販売を終了しているか' not in h:
          #print h
          #import sys
          #sys.exit(0)
          ret = self._parse(h, key)
          if ret:
            ret['id'] = id
            ret['url'] = url
            return ret

  def _parse(self, h, key):
    """
    @param  h  unicode  html
    @param  key  str
    @return  {kw}
    """
    ret = self._parsemetadesc(h)
    if ret:
      ret['otome'] = u"成人女性向" in h # bool
      ret['ecchi'] = u"18歳未満" in h # bool
      ret['brand'] = self._parsebrand(h) # unicode or None
      ret['date'] = self._parsedate(h) # datetime object or None
      ret['filesize'] = self._parsefilesize(h) # long not None

      ret['genre'] = self._parsetablecell(u"ジャンル", h)
      ret['anime'] = self._hastablecell(u"アニメ", h)

      ret['artists'] = list(self._iterparsetablelinks(u'原画', h))
      ret['writers'] = list(self._iterparsetablelinks(u'シナリオ', h))
      ret['musicians'] = list(self._iterparsetablelinks(u'音楽', h))
      ret['cv'] = list(self._iterparsetablelinks(u'声優', h))

      ret['keywords'] = list(self._iterparsetablelinks(u'キー', h))

      ret['description'] = self._parsedescription(h) # unicode or None
      ret['characterDescription'] = self._parsecharadesc(h) # unicode or None
      ret['review'] = self._parsereview(h) # unicode or None

      #ret['characters'] = list(self._iterparsecharacters(h)) # [kw]
      ret['characters'] = [] # disabled

      for it in list(self._iterparsetablelinks(u'イベント', h)):
        ret['event'] = it

      m = self._parseevimages(h)
      if m:
        ret.update(m)

      m = self._parsetopimages(h, key)
      if m:
        ret.update(m)
      return ret

  #def _fixtitle(self, t):
  #  """
  #  @param  t  unicode
  #  @return  unicode
  #  """
  #  # http://www.getchu.com/soft.phtml?id=721680
  #  return t.replace(u'＜特価セール', '').strip()

  #def _fixbrand(self, t):
  #  """
  #  @param  t  unicode
  #  @return  unicode
  #  """
  #  if t:
  #    return t.replace(" / ", ',')

  #def _fixcreators(self, t):
  #  """
  #  @param  unicode
  #  @return  unicode or None
  #  """
  #  if t:
  #    return t.replace(u"、他", '')

  # Example: <span itemprop="title">屋根裏のラグーン</span>
  #_rx_titlebrand = re.compile(ur'<TITLE>【 ([^】]+?) 】のご購入\s*\[([^\]]+?)\] ', re.IGNORECASE)
  #def _parsetitlebrand(self, h):
  #  """
  #  @param  h  unicode  html
  #  @return  (unicode title, unicode brand) or None
  #  """
  #  m = self._rx_titlebrand.search(h)
  #  if m:
  #    return unescapehtml(m.group(1)).strip(), unescapehtml(m.group(2)).strip()

  # <meta name="description" content="かいじゅう【屋根裏のラグーン】のダウンロード購入。デジケット特価:1,236 円。同人ソフト、美少年CG集、同人誌、乙女ゲー、ＢＬアニメがあります。">
  # <meta name="脳内彼女の『女装山脈』のダウンロード購入。デジケット特価:3,811 円。美少女ゲーム、アダルトゲーム、同人ソフト、萌えCG集、同人誌があります。">
  _rx_meta_desc = re.compile(r'<meta name="description" content="([^"]*?)"')
  _rx_desc_title = re.compile(ur'[【『]([^】]*)[】』]')
  #_rx_desc_brand = re.compile(ur'^([^【『]*)[【『]')
  _rx_desc_price = re.compile(ur'([0-9,]+) 円') # 3,811 円
  def _parsemetadesc(self, h):
    """
    @param  h  unicode  html
    @return  kw
    """
    ret = {}
    m = self._rx_meta_desc.search(h)
    if m:
      desc = m.group(1)
      m = self._rx_desc_title.search(desc)
      if m:
        ret['title'] = unescapehtml(m.group(1))

      #m = self._rx_desc_brand.search(desc)
      #if m:
      #  brand = unescapehtml(m.group(1))
      #  if brand[-1] == u'の':
      #    brand = brand[:-1]
      #  ret['brand'] = brand

      m = self._rx_desc_price.search(desc)
      if m:
        price = m.group(1).replace(',', '')
        try: ret['price'] = int(price)
        except: pass
    return ret

  # Example >ブランド名：[ <a href="http://www.digiket.com/game/g_worklist/_data/ID=CIR0005680/">脳内彼女</a>
  # Either ブランド or サークル名
  _rx_brand = re.compile(r'_worklist/_data/ID=[^"]*?">([^<]*?)</a>')
  def _parsebrand(self, h):
    """
    @param  h  unicode  html
    @return  unicode or None
    """
    m = self._rx_brand.search(h)
    if m:
      return unescapehtml(m.group(1)).replace(" / ", ',').replace(u"／", ',')

  # <tr>
  #   <td width="15%" bgcolor="#CCCCFF"><div align="right"><font size="2">登録日</font></div></td>
  #   <td width="85%"><div align="left"><font size="2">
  #     2013年05月31日                                </font></div></td>
  # </tr>
  _rx_date = re.compile(ur'(\d{4})年(\d{2})月(\d{2})日')
  def _parsedate(self, h):
    """
    @param  h  unicode  html
    @return  datetime object or None
    """
    start = h.find(u"登録日</font>")
    if start > 0:
      h = h[start:]
      stop = h.find("</tr>")
      if stop > 0:
        h = h[:stop]
        m = self._rx_date.search(h)
        if m:
          try: return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
          except: pass

  # Example:
  # 981,064,258  byte　[ <a href="#" onClick="return open_math('981064258');">ダウンロード時間</a> ]
  _rx_filesize = re.compile(r"return open_math\('(\d+)'\)")
  def _parsefilesize(self, h):
    """
    @param  h  unicode  html
    @return  int or 0 not None  unit is in in byte
    """
    m = self._rx_filesize.search(h)
    if m:
      try: return long(m.group(1))
      except: pass
    return 0

  def _parsetopimages(self, h, key):
    """
    @param  h  unicode  html
    @param  key  str
    @return  kw or None
    """
    rx = re.compile(r"img.digiket.net/cg/(\d+?)/%s_1.jpg" % key)
    m = rx.search(h)
    if m:
      group = m.group(1)
      ret = {
        'img': "http://img.digiket.net/cg/%s/%s_1.jpg" % (group, key),
      }

      urls = [] # [unicode url]
      for i in 1,2,3:
        url = "http://img.digiket.net/cg/%s/%s_s%s.jpg" % (group, key, i)
        if url in h:
          urls.append(url)

      if urls:
        ret['screenshots'] = urls
      return ret

  # Example: http://www.digiket.com/game/sp/n/nounai_kanojyo/josou_kaikyou/img/ev01.jpg
  _rx_image = re.compile(r"/game/sp/[a-z]/[a-z_]+?/[a-z_]+?/img/")
  def _parseevimages(self, h):
    """
    @param  h  unicode  html
    @return  str or None
    """
    m = self._rx_image.search(h)
    if m:
      prefix = m.group()
      ret = {}
      ev = prefix + 'ev01.jpg'
      if ev in h:
        ret['ev'] = self.HOST + ev
      chara = prefix + 'c01.jpg'
      if chara in h:
        ret['chara'] = self.HOST + chara
      return ret

  _rx_link = re.compile('>([^<]+?)</a>', re.I)
  def _iterparsetablelinks(self, key, h):
    """
    @param  key  unicode
    @param  h  unicode  html
    @yield  unicode  name
    """
    start = h.find('%s</font></div></td>' % key)
    if start > 0:
      h = h[start:]
      stop = h.find('</tr>')
      if stop > 0:
        h = h[:stop]
        for m in self._rx_link.finditer(h):
          yield unescapehtml(m.group(1).strip())

  _rx_cell = re.compile('>([^<]+?)</font></div></td>', re.I)
  def _parsetablecell(self, key, h):
    """
    @param  key  unicode
    @param  h  unicode  html
    @return  unicode  name
    """
    start = h.find('%s</font></div></td>' % key)
    if start > 0:
      h = h[start:]
      stop = h.find('</tr>')
      if stop > 0:
        h = h[:stop]
        m = self._rx_cell.search(h)
        if m:
          return unescapehtml(m.group(1).strip())

  def _hastablecell(self, key, h):
    """
    @param  key  unicode
    @param  h  unicode  html
    @return  bool
    """
    t = self._parsetablecell(key, h)
    return t == u'○'

  def _parsedescription(self, h):
    """
    @param  h  unicode  html
    @return  unicode or None
    """
    start = h.find(u"の説明</font></strong></div></td>")
    if start > 0:
      stop = h.find(u"</font></div>", start)
      if stop > 0:
        h = h[start:stop].rstrip()
        DIV = u'<font size="2">'
        i = h.find(DIV)
        if i > 0:
          h = h[i + len(DIV):].lstrip()
          return self._replacelinks(h)

  def _parsecharadesc(self, h):
    """
    @param  h  unicode  html
    @return  unicode or None
    """
    start = h.find(u"キャラクター紹介</strong></font></td>")
    if start > 0:
      TABLE = '<table width="800"'
      start = h.find(TABLE, start)
      if start > 0:
        stop = h.find(TABLE, start + len(TABLE))
        if stop > 0:
          h = h[start:stop]
          return self._replacelinks(h).replace('table width="800"', 'table') # remove table width

  def _parsereview(self, h):
    """
    @param  h  unicode  html
    @return  unicode or None
    """
    if u'本作品の最初のレビューを募集中' in h:
      return
    start = h.find(u"ユーザーレビュー</font></strong></div></td>")
    if start > 0:
      h = h[start:]
      stop = h.find(u'<div id="item_history"')
      if stop > 0:
        h = h[:stop]
        DIV = u'<div align="left">'
        i = h.find(DIV)
        if i > 0:
          h = h[i + len(DIV):].lstrip()

          DIV = u'</table>'
          i = h.rfind(DIV)
          if i > 0:
            h = h[:i]

            DIV = u'</table>'
            i = h.rfind(DIV)
            if i > 0:
              h = h[:i + len(DIV)].rstrip()
              return self._replacelinks(self._cleanreview(h))

  @staticmethod
  def _cleanreview(h):
    """
    @param  h  unicode
    @return  unicode
    """
    # Remove the header
    DIV = u'</table>'
    i = h.find(DIV)
    if i > 0:
      h = h[i + len(DIV):].lstrip()

    # Remove <div class="review_footer">
    BEGIN = '<div class="review_footer'
    END = '</div>'
    while True:
      start = h.find(BEGIN)
      if start == -1:
        break
      stop = h.find(END, start)
      if stop == -1:
        break
      stop = h.find(END, stop)
      if stop == -1:
        break
      stop += len(END)
      h = h[:start] + h[stop:]
    return h

  def _replacelinks(self, h):
    """
    @param  h  unicode  HTML
    @return  h  unicode
    """
    return h.replace('<img src="/', '<img src="%s/' % self.HOST)

  _rx_label = re.compile(ur"【([^】]+?)】</font>") # <td align="left"><strong><font color="#FF6600">【一人称が僕の女装っ娘】</font></strong><br>
  _rx_cv = re.compile(ur"CV：([^）]+?)）")
  _rx_chara = re.compile(ur"<strong>●([^<]+?)</strong>") # <strong>●羽馬 紫織（はば・しおり）</strong>
  def _iterparsecharacters(self, h):
    """
    @param  h  unicode
    @yield  kw
    """
    m = self._rx_image.search(h)
    if m:
      prefix = m.group()
      for i in xrange(1,100):
        img = "%sc%02d.jpg" % (prefix, i)
        start = h.find(img)
        if start < 0:
          break
        stop = h.find('</table>', start)
        if start < 0:
          break
        desc = h[start:stop]

        m = self._rx_label.search(desc)
        label = unescapehtml(m.group(1)) if m else ''

        m = self._rx_cv.search(desc)
        cv = unescapehtml(m.group(1)) if m else ''

        name = yomi = ''
        m = self._rx_chara.search(desc)
        if m:
          name = unescapehtml(m.group(1)).replace(u'　', ' ') # u3000
          # ●羽馬 紫織（はば・しおり）
          beg = name.find(u'（')
          if beg > 0:
            end = name.rfind(u'）')
            if end > 0:
              yomi = name[beg+1:end].replace(u'・', ' ')
              name = name[:beg]

        yield {
          'id': i, # int
          'img': self.HOST + img,
          'label': label,
          'name': name.strip(),
          'yomi': yomi.strip(),
          'cv': cv, # unicode
        }

if __name__ == '__main__':
  # http://www.digiket.com/work/show/_data/ID=ITM0080219/
  api = ItemApi()
  k = 97794 # http://www.digiket.com/work/show/_data/ID=ITM0097794/
  k = 99455 # http://www.digiket.com/work/show/_data/ID=ITM0099455/
  k = 83422 # 女装海峡, http://www.digiket.com/work/show/_data/ID=ITM0083422/
  k = 99460 # 仮・想・侵・蝕, http://www.digiket.com/work/show/_data/ID=ITM0099460/
  k = 100413 # http://www.digiket.com/work/show/_data/ID=ITM0100413/
  k = 80219 # 屋根裏のラグーン, http://www.digiket.com/work/show/_data/ID=ITM0080219/
  k = 53791 # 女装山脈, http://www.digiket.com/work/show/_data/ID=ITM0053791/
  #print '-' * 10
  q = api.query(k)
  #for k,v in q.iteritems():
  #  print k,':',v
  #print q['review']
  #print q['ev']
  print q['img']
  print q['brand']
  print q['keywords']
  print q['price']
  print q['description']
  print q['characterDescription']

#  for it in q['characters']:
#    for k,v in it.iteritems():
#      print k,':',v
#
# EOF
