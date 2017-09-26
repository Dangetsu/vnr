# coding: utf8
# soft.py
# 8/14/2013 jichi

__all__ = 'SoftApi',

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import re
from restful.online import DataParser
from sakurakit.skdebug import dwarn
from sakurakit.skstr import unescapehtml

# http://stackoverflow.com/questions/38987/how-can-i-merge-union-two-python-dictionaries-in-a-single-expression
def _mergedictwith(x, y):
  """
  @param[inout]  x  dict
  @param[in]  y  dict
  """
  for k,v in y.iteritems():
    if not x.get(k): #== None:
      x[k] = v

class SoftApi(DataParser):

  API = "http://erogetrailers.com/soft/%s"

  def _makeurl(self, id):
    """@reimp
    @param  id  int
    @return  str
    """
    return self.API % id

  # Example:
  # http://erogetrailers.com/soft/3424
  #
  # <section>
  # <h5>
  # <a class="title" href="http://erogetrailers.com/video/1447">オープニングムービー</a>
  # <br/>
  # <a href="http://erogetrailers.com/video/1447" class="subttl">2010-01-15</a>
  # </h5>
  # <p class="img">
  # <a href="http://erogetrailers.com/video/1447"><img src="http://i2.ytimg.com/vi/JF0TvDZlzsY/0.jpg" alt="" /></a>
  # </p>
  # <p class="desc"><span>02:13</span></p>
  # </section>
  def _parse(self, h):
    """@reimp
    @param  h  unicode  html
    @return  {kw}
    """
    ret = {
      'banner': self._parsebanner(h),   # str url or None
      'otome': self._parseotome(h),     # bool
      'taiken': self._parselink(h, self._rx_taiken), # str URL
      'series': self._parseseries(h),   # str url or None
      'brands': list(self._iterparsebrands(h)), # kw
      'videos': list(self._iterparsevideos(h)), # kw
      #'creators': self._parsecreators(h), # [kw]
    }

    for role in 'writer', 'artist', 'sdartist':
      rx = self._rx_creators[role]
      ret[role + 's'] = list(self._iterparsemakers(h, rx))
    ret['musicians'] = list(self._iterparsemakers(h, self._rx_creators['musician'])) + list(self._iterparsemakers(h, self._rx_creators['musician2']))
    return ret

  # <div style="text-align: center; padding-top:10px;"><img src="http://www.noukano.com/koisen/banner/koisen-600x120-5.jpg" /></div>
  _rx_banner = re.compile(r'"><img src="(.+?)"')
  def _parsebanner(self, h):
    """
    @param  h  unicode  html
    @return  unicode or None
    """
    m = self._rx_banner.search(h)
    if m:
      return unescapehtml(m.group(1))

  def _parseotome(self, h):
    """
    @param  h  unicode  html
    @return  bool
    """
    return u"女性向" in h
    #return u"女性向）</small></td></tr>" in h

  #_rx_series = re.compile(ur'series -->.*?>([^>]+?)シリーズ', re.DOTALL)
  _rx_series = re.compile(ur'>([^>]+?)シリーズ')
  def _parseseries(self, h):
    """
    @param  h  unicode  html
    @return  unicode or None
    """
    m = self._rx_series.search(h)
    if m:
      return unescapehtml(m.group(1))

  _rx_videos = re.compile(r'.*?'.join((
    r'<section>',
    r'<a class="title" href="http://erogetrailers\.com/video/([0-9]+?)">(.*?)</a>',
    r'class="subttl">([0-9-].*?)</a>',
    r'"http://i2\.ytimg\.com/vi/([0-9a-zA-Z_-]+?)/[a-zA-Z0-9_-]+.jpg"',
    r'</section>',
  )), re.IGNORECASE|re.DOTALL)
  def _iterparsevideos(self, h):
    """
    @param  h  unicode  html
    @yield  {kw}
    """
    for m in self._rx_videos.finditer(h):
      yield {
        'video': m.group(1),    # str video ID
        'title': unescapehtml(m.group(2)),    # unicode
        'date': m.group(3),     # str like 2010-01-15
        'youtube': m.group(4),  # str youtube ID
      }
      #h = h[m.end(0):]

  _rx_brands = re.compile(ur'<th>ブランド</th><td>(.*?)</td>', re.IGNORECASE)
  _rx_brands_id = re.compile(r'http://erogetrailers\.com/brand/([0-9]+)')
  _rx_brands_name = re.compile(r'>([^>]+?)</a>')
  def _iterparsebrands(self, h):
    """
    @param  h  unicode  html
    @yield  {kw}
    """
    try:
      m = self._rx_brands.search(h)
      if m:
        line = m.group(1)
        for hh in line.split(u'、'):
          id = int(self._rx_brands_id.search(hh).group(1))
          name = unescapehtml(self._rx_brands_name.search(hh).group(1))
          yield {
            'id': id, # int
            'name': name, # unicode
            'img': "http://media.erogetrailers.com/img/brand/%i.png" % id, # str
            #'url': "http://erogetrailers.com/brand/%i" % id, # not used
          }
    except Exception, e: dwarn(e)

  #def _parsecreators(self, h):
  #  """
  #  @param  h  unicode  html
  #  @return  {kw}
  #  """
  #  ret = [] # [{maker}], preserve order
  #  makers = {} # {name:maker}
  #  for role,rx in self._rx_creators:
  #    for it in self._iterparsemakers(h, rx):
  #      name = it['name']
  #      maker = makers.get(name)
  #      if maker:
  #        _mergedictwith(maker, it)
  #        maker['roles'].append(role)
  #      else:
  #        it['roles'] = [role]
  #        makers[name] = it
  #        ret.append(it)
  #  return ret

  def __makelinkrx(key):
    return re.compile('''["']([^"']+?)["']>%s''' % key)

  # Example: <span class='yaku_composer'><a href='http://www.noctovision.jp/start/html/down.html'>体験</a></span>
  _rx_taiken = __makelinkrx(u'体験')
  def _parselink(self, h, rx):
    """
    @param  h  unicode  html
    @param  rx  re
    @return  str
    """
    m = rx.search(h)
    if m:
      return unescapehtml(m.group(1))
    return ''

  def __makecreatorsrx(key):
    pat = r'<th>%s</th><td>(.*?)</td>' % key
    return re.compile(pat, re.IGNORECASE)
  _rx_creators = {    # [(str role, rx))
    'director': __makecreatorsrx(u"企画・監督"),
    'writer':   __makecreatorsrx(u"シナリオ"),
    'artist':   __makecreatorsrx(u"原画"),
    'sdartist': __makecreatorsrx(u"ＳＤ原画"),
    'musician': __makecreatorsrx(u"BGM"),
    'musician2':__makecreatorsrx(u"♫"),
    'singer':   __makecreatorsrx(u"歌唱"),
    'lyrics':   __makecreatorsrx(u"作詞"),
    'composer': __makecreatorsrx(u"作曲"),
    'arranger': __makecreatorsrx(u"編曲"),
  }

  _rx_makers = re.compile(r'>([^<]+?)<') # anything between > and <
  _rx_makers_id = re.compile(r'http://erogetrailers\.com/hito/([0-9]+)')
  #_rx_makers_tw = re.compile(r"""\.twimg\.com/profile_images/(.+?)['"]""") # ends with "'"
  #_rx_makers_img = re.compile(r"<img src='(.*?)'") # ends with "'"
  def _iterparsemakers(self, h, rx):
    """
    @param  h  unicode  html
    @param  rx  re
    @yield  {kw}
    """
    names= set() # {unicode name}, used to eliminate repetition
    try:
      for m in rx.finditer(h):
        #h = h[m.end(0):]
        line = m.group(1)
        for hh in line.split(u'、'):
          while hh:
            mm = self._rx_makers.search(hh)
            if not mm:
              break
            t = mm.group(1).strip()
            if t and t not in (u"他", u"不明"):
              name = unescapehtml(t)
              if name not in names:
                names.add(name)
                hhh = hh[:mm.start(0)]
                mmm = self._rx_makers_id.search(hhh)
                hito = mmm.group(1) if mmm else ''
                if hito:
                  #hhh = hhh[mmm.end(0):]
                  #mmm = self._rx_makers_img.search(hhh)
                  #img = mmm.group(1) if mmm else ''
                  #mmm = self._rx_makers_tw.search(hhh)
                  #twimg = mmm.group(1).replace('_normal', '') if mmm else ''
                  yield {
                    'name': name,   # unicode
                    'id': int(hito),# int not 0, might throw
                    #'img': img,     # str url or ''
                    #'twimg': twimg, # str id or ''
                  }
            hh = hh[mm.end(0):]
    except ValueError, e: dwarn(e)

if __name__ == '__main__':
  api = SoftApi()
  k = 8710
  k = 8680
  k = 11503
  print '-' * 10
  q = api.query(k)
  print q['otome']
  print q['artists']
  print q['musicians']
  print q['taiken']

# EOF
