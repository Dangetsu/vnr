# coding: utf8
# refman.py
# 7/21/2013 jichi

if __name__ == '__main__':
  import sys
  sys.path.append('..')
  import debug
  debug.initenv()

import re
from datetime import datetime
from functools import partial
from sakurakit import skdatetime, skthreads
from sakurakit.skclass import memoized, memoizedproperty, hasmemoizedproperty
#from sakurakit.skcontainer import uniquelist
from sakurakit.skdebug import dprint, dwarn
from sakurakit.skstr import unescapehtml
import config, proxy, rc

@memoized
def manager(): return ReferenceManager()

@memoized
def trailers(): return TrailersManager()

@memoized
def dmm(): return DmmManager()

@memoized
def tokuten(): return TokutenManager()

#@memoized
#def holyseal(): return HolysealManager()

@memoized
def gyutto(): return GyuttoManager()

@memoized
def getchu(): return GetchuManager()

@memoized
def amazon(): return AmazonManager()

#@memoized
def scape(): return ScapeManager()

_re_title = '|'.join((
  ur'\[同人PCソフト\]',
  ur'＜特価セール.*', # getchu
  ur'【..特典.*',
  ur' DVD .*',
  ur' DVD版.*',
  ur' 流通.*',
  ur'.完全生産限定.*',
  ur'.完全受注生産.*',
  ur'.豪華限定.*',
  ur'.限定特典.*',
  ur'.特別限定.*',
  ur'.特装初回.*',
  ur'.初回限定.*',
  ur'.完全限定.*',
  ur'.初回.*特典.*',
  ur'.予約.*特典.*',
  ur'.限定版.*',
  ur'.初回版.*',
  ur'.廉価版.*',
  ur'.豪華版.*',
  ur'.特装版.*',
  ur'.初回.*版.*',
  ur'.完全版.*',
  ur'.流通特典.*',
  ur'.プレミアム.*',
  ur'.DL版.*',
  ur'\-Limited.*',
  ur'.E-15指定.*',
  ur'.R-15指定.*',
  ur'.【.*|＜.*',
  ur' 特典.*',
  ur'.ダウンロード.*',
  #ur'復刻版.*',
  #ur'廉価版.*',
  #ur'通常版*',
))

## ErogeTrailers ##

class TrailersApi(object):

  def __init__(self, online=True):
    """
    @param* online  bool
    """
    self.online = online

  def setOnline(self, v):
    if self.online !=  v:
      self.online = v
      if hasmemoizedproperty(self, 'cachingApi'):
        self.cachingApi.online = v

  #@staticmethod
  #def _beautifyTitle(t):
  #  """
  #  @param  t  unicode
  #  @return  unicode not None
  #  """
  #  return t.strip() # rstrip() is enough

  @memoizedproperty
  def cachingApi(self):
    from erogetrailers.caching import CachingRestApi
    return CachingRestApi(rc.DIR_CACHE_TRAILERS,
        expiretime=config.REF_EXPIRE_TIME,
        online=self.online)

  @memoizedproperty
  def api(self):
    from erogetrailers.rest import RestApi
    return RestApi()

  @staticmethod
  def _parsekey(url):
    """
    @param  url  unicode
    @return  unicode or None
    """
    if url:
      m = re.search(r"erogetrailers.com/soft/([0-9]+)", url)
      if m:
        return m.group(1)

  def _search(self, text=None, key=None, cache=True):
    """
    @return  iter or None
    """
    dprint("key, text =", key, text)
    api = self.cachingApi if cache else self.api
    if not key and text:
      if text.isdigit():
        key = text
      elif text.startswith('http://') or text.startswith('www.'):
        k = self._parsekey(text)
        if k:
          key = k
    if key:
      return api.query(key, type=api.EROGETRAILERS_TYPE)
    elif text:
      return api.query(text)

  def cache(self, *args, **kwargs):
    dprint("enter")
    self._search(*args, **kwargs)
    dprint("leave")

  # Page limit by default is 30
  def query(self, text=None, key=None, **kwargs):
    """
    @return  iter not None
    """
    dprint("enter")
    if text and not key and (
        isinstance(text, (int, long)) or
        isinstance(text, basestring) and text.isdigit()
      ):
      key = text
      text = None
    ret = self._search(text=text, key=key, **kwargs) or []
    if ret:
      try:
        for it in ret:
          self._formatItem(it)
      except Exception, e:
        dwarn(e)
        ret = []
    dprint("leave: count = %s" % len(ret))
    return ret or []

  @classmethod
  def _formatItem(cls, kw):
    """
    @param  kw
    @raise
    """
    kw['key'] = str(kw.pop('id'))
    #kw['title'] = cls._beautifyTitle(kw['title'])
    try:
      d = datetime.strptime(str(kw['releaseDayNumber']), '%Y%m%d')
      kw['date'] = skdatetime.date2timestamp(d)
    except: kw['date'] = 0
    kw['url'] = 'http://erogetrailers.com/soft/' + kw['key']

    for k in 'title', 'romanTitle', 'brand':
      t = kw.get(k)
      if t:
        kw[k] = unescapehtml(t)

    try:
      if kw['brand'].endswith(u'（同人）'):
        kw['doujin'] = True
        kw['brand'] = kw['brand'].replace(u'（同人）', '')
    except: pass

    kw['homepage'] = kw.pop('hp')

## Scape API ##

class ScapeApi(object):

  def __init__(self, online=True):
    """
    @param* online  bool
    """
    self.online = online
    self.proxyEnabled = False
    self.session = None

    import settings
    ss = settings.global_()
    self.setProxyEnabled(ss.proxyScape())
    ss.proxyScapeChanged.connect(self.setProxyEnabled)

  def setProxyEnabled(self, t):
    if self.proxyEnabled != t:
      dprint(t)
      self.proxyEnabled = t
      session = None
      if t:
        import features
        session = features.make_proxy_session()
      self.setSession(session)

  def setOnline(self, v):
    if self.online !=  v:
      self.online = v
      if hasmemoizedproperty(self, 'cachingApi'):
        self.cachingApi.online = v

  def setSession(self, v): # requests.Session
    self.session = v
    if hasmemoizedproperty(self, 'cachingApi'):
      self.cachingApi.session = v
    if hasmemoizedproperty(self, 'api'):
      self.api.session = v

  @memoizedproperty
  def cachingApi(self):
    from erogamescape.caching import CachingGameTableApi
    ret = CachingGameTableApi(
        cachedir=rc.DIR_CACHE_SCAPE,
        expiretime=config.REF_EXPIRE_TIME,
        online=self.online)
    ret.session = self.session
    return ret

  @memoizedproperty
  def api(self):
    from erogamescape.api import GameTableApi
    ret = GameTableApi()
    ret.session = self.session
    return ret

  @staticmethod
  def _parsekey(url):
    """
    @param  url  unicode
    @return  unicode or None
    """
    if url:
      m = re.search(r"game=([0-9]+)", url)
      if m:
        return m.group(1)

  def _search(self, text=None, key=None, cache=True):
    """
    @return  iter
    """
    dprint("key, text =", key, text)
    api = self.cachingApi if cache else self.api
    if not key and text:
      if text.isdigit():
        key = text
      elif text.startswith('http://') or text.startswith('www.'):
        k = self._parsekey(text)
        if k:
          key = k
    params = {'id':key} if key else {'text':text}
    return api.query(limit=20, **params) # max number: 20

  def cache(self, *args, **kwargs):
    dprint("enter")
    self._search(*args, **kwargs)
    dprint("leave")

  # See: https://affiliate.dmm.com/api/reference/r18/pcgame/
  def query(self, **kwargs):
    """
    @return  iter not None
    """
    dprint("enter")
    ret = self._search(**kwargs) or []
    if ret:
      try:
        for it in ret:
          self._formatItem(it)
      except Exception, e:
        dwarn(e)
        ret = []
    dprint("leave: count = %s" % len(ret))
    return ret

  @staticmethod
  def _formatItem(item):
    """
    @param  item  kw
    @raise
    """
    item['key'] = str(item.pop('id'))
    d = item.pop('sellday')
    item['date'] = skdatetime.date2timestamp(d) if d else 0
    item['title'] = item['gamename']
    #if self.proxyEnabled and 'shoukai' in item:
    #  del item['shoukai']

## Holyseal API ##

class HolysealApi(object):

  def __init__(self, online=True):
    """
    @param* online  bool
    """
    self.online = online

  def setOnline(self, v):
    if self.online !=  v:
      self.online = v
      if hasmemoizedproperty(self, 'cachingProductApi'):
        self.cachingProductApi.online = v

  _rx_title = re.compile( _re_title)
  @classmethod
  def _beautifyTitle(cls, t):
    """
    @param  t  unicode
    @return  unicode
    """
    return cls._rx_title.sub('', t).strip()

  @memoizedproperty
  def cachingProductApi(self):
    from holyseal.caching import CachingProductApi
    return CachingProductApi(
        cachedir=rc.DIR_CACHE_HOLYSEAL,
        expiretime=config.REF_EXPIRE_TIME,
        online=self.online)

  @memoizedproperty
  def searchApi(self):
    from holyseal.search import SearchApi
    return SearchApi()

  def _search(self, text=None, key=None, cache=True):
    """
    @param  cache  bool  not used
    @yield  kw
    """
    dprint("key, text =", key, text)
    if key:
      kw = self.cachingProductApi.query(key)
      if kw:
        yield kw
    elif text:
      q = self.searchApi.query(text)
      if q:
        for it in q:
          yield it

  def cache(self, text=None, key=None):
    if key:
      dprint("enter")
      self.cachingProductApi.cache(key)
      dprint("leave")

  @staticmethod
  def _parsekey(url):
    """
    @param  url  unicode
    @return  unicode or None
    """
    if url:
      m = re.search(r"prdcode=([0-9]+)", url)
      if m:
        return m.group(1)

  # See: https://affiliate.dmm.com/api/reference/r18/pcgame/
  def query(self, key=None, text=None, **kwargs):
    """
    @return  iter not None
    """
    dprint("enter")
    ret = []
    if not key and text:
      if text.isdigit():
        key = text
      elif text.startswith('http://') or text.startswith('holyseal.net'):
        k = self._parsekey(text)
        if k:
          key = k
    s = self._search(key=key, text=text, **kwargs)
    try:
      for item in s:
        id = item['key'] = str(item.pop('id'))

        d = item.get('date') or 0 # int
        if d:
          try:
            d = datetime.strptime(d, '%Y/%m/%d')
            d = skdatetime.date2timestamp(d)
          except:
            dwarn("failed to parse date")
            d = 0
        item['date'] = d

        item['url'] = "http://holyseal.net/cgi-bin/mlistview.cgi?prdcode=%s" % id

        ret.append(item)
    except Exception, e: dwarn(e)
    dprint("leave: count = %s" % len(ret))
    return ret

## Steam API ##

class SteamApi(object):

  def __init__(self, online=True):
    """
    @param* online  bool
    """
    self.online = online

    import parsedatetime
    self.pdtc = parsedatetime.Calendar()

  def setOnline(self, v):
    if self.online !=  v:
      self.online = v
      if hasmemoizedproperty(self, 'cachingAppApi'):
        self.cachingAppApi.online = v

  @memoizedproperty
  def cachingAppApi(self):
    from steam.caching import CachingAppApi
    return CachingAppApi(
        cachedir=rc.DIR_CACHE_STEAM,
        expiretime=config.REF_EXPIRE_TIME,
        online=self.online)

  @memoizedproperty
  def searchApi(self):
    from steam.search import SearchApi
    return SearchApi()

  def _search(self, text=None, key=None, cache=True):
    """
    @param  cache  bool  not used
    @yield  kw
    """
    dprint("key, text =", key, text)
    if key:
      kw = self.cachingAppApi.query(key)
      if kw:
        yield kw
    elif text:
      q = self.searchApi.query(text)
      if q:
        for it in q:
          yield it

  def cache(self, text=None, key=None):
    if key:
      dprint("enter")
      self.cachingAppApi.cache(key)
      dprint("leave")

  @staticmethod
  def _parsekey(url):
    """
    @param  url  unicode
    @return  unicode or None
    """
    if url:
      m = re.search(r"/([0-9]+)", url)
      if m:
        return m.group(1)

  # See: https://affiliate.dmm.com/api/reference/r18/pcgame/
  def query(self, key=None, text=None, **kwargs):
    """
    @return  iter not None
    """
    dprint("enter")
    ret = []
    if not key and text:
      if text.isdigit():
        key = text
      elif 'steampowered.com' in text:
        k = self._parsekey(text)
        if k:
          key = k
    s = self._search(key=key, text=text, **kwargs)
    try:
      for item in s:
        k = str(item.pop('id'))
        item['key'] = k
        d = item.get('date') or 0 # int
        if d:
          try:
            d = datetime(*self.pdtc.parseDateText(d)[:6])
            d = skdatetime.date2timestamp(d)
          except:
            dwarn("failed to parse date")
            d = 0
        item['date'] = d

        if 'img' in item:
          item['image'] = item.pop('img')

        item['brand'] = item.get('developer') or item.get('publisher') or ''

        ret.append(item)
    except Exception, e: dwarn(e)
    dprint("leave: count = %s" % len(ret))
    return ret

## Freem API ##

class FreemApi(object):

  def __init__(self, online=True):
    """
    @param* online  bool
    """
    self.online = online

  def setOnline(self, v):
    if self.online !=  v:
      self.online = v
      if hasmemoizedproperty(self, 'cachingGameApi'):
        self.cachingGameApi.online = v

  @memoizedproperty
  def cachingGameApi(self):
    from freem.caching import CachingGameApi
    return CachingGameApi(
        cachedir=rc.DIR_CACHE_FREEM,
        expiretime=config.REF_EXPIRE_TIME,
        online=self.online)

  @memoizedproperty
  def searchApi(self):
    from freem.search import SearchApi
    return SearchApi()

  def _search(self, text=None, key=None, cache=True):
    """
    @param  cache  bool  not used
    @yield  kw
    """
    dprint("key, text =", key, text)
    if key:
      kw = self.cachingGameApi.query(key)
      if kw:
        yield kw
    elif text:
      q = self.searchApi.query(text)
      if q:
        for it in q:
          yield it

  def cache(self, text=None, key=None):
    if key:
      dprint("enter")
      self.cachingGameApi.cache(key)
      dprint("leave")

  @staticmethod
  def _parsekey(url):
    """
    @param  url  unicode
    @return  unicode or None
    """
    if url:
      m = re.search(r"/([0-9]+)", url)
      if m:
        return m.group(1)

  # See: https://affiliate.dmm.com/api/reference/r18/pcgame/
  def query(self, key=None, text=None, **kwargs):
    """
    @return  iter not None
    """
    dprint("enter")
    ret = []
    if not key and text:
      if text.isdigit():
        key = text
      elif text.startswith('http://') or text.startswith('www.'):
        k = self._parsekey(text)
        if k:
          key = k
    s = self._search(key=key, text=text, **kwargs)
    try:
      for item in s:
        k = str(item.pop('id'))
        item['key'] = k
        d = item.get('date') or 0 # int
        if d:
          try:
            d = datetime.strptime(d, '%Y-%m-%d')
            d = skdatetime.date2timestamp(d)
          except:
            dwarn("failed to parse date")
            d = 0
        item['date'] = d

        if 'img' in item:
          item['image'] = item.pop('img')

        ret.append(item)
    except Exception, e: dwarn(e)
    dprint("leave: count = %s" % len(ret))
    return ret

## MelonBooks API ##

class MelonApi(object):

  def __init__(self, online=True):
    """
    @param* online  bool
    """
    self.online = online

  def setOnline(self, v):
    if self.online !=  v:
      self.online = v
      if hasmemoizedproperty(self, 'cachingProductApi'):
        self.cachingProductApi.online = v

  _rx_title = re.compile( _re_title)
  @classmethod
  def _beautifyTitle(cls, t):
    """
    @param  t  unicode
    @return  unicode
    """
    return cls._rx_title.sub('', t).strip()

  @memoizedproperty
  def cachingProductApi(self):
    from melonbooks.caching import CachingProductApi
    return CachingProductApi(
        cachedir=rc.DIR_CACHE_MELON,
        expiretime=config.REF_EXPIRE_TIME,
        online=self.online)

  @memoizedproperty
  def searchApi(self):
    from melonbooks.search import SearchApi
    return SearchApi()

  def _search(self, text=None, key=None, cache=True):
    """
    @param  cache  bool  not used
    @yield  kw
    """
    dprint("key, text =", key, text)
    if key:
      kw = self.cachingProductApi.query(key)
      if kw:
        yield kw
    elif text:
      q = self.searchApi.query(text)
      if q:
        for it in q:
          yield it

  def cache(self, text=None, key=None):
    if key:
      dprint("enter")
      self.cachingProductApi.cache(key)
      dprint("leave")

  @staticmethod
  def _parsekey(url):
    """
    @param  url  unicode
    @return  unicode or None
    """
    if url:
      m = re.search(r"id=([0-9]+)", url)
      if m:
        return m.group(1)

  # See: https://affiliate.dmm.com/api/reference/r18/pcgame/
  def query(self, key=None, text=None, **kwargs):
    """
    @return  iter not None
    """
    dprint("enter")
    ret = []
    if not key and text:
      if text.isdigit():
        key = text
      elif text.startswith('http://') or text.startswith('https://') or text.startswith('www.'):
        k = self._parsekey(text)
        if k:
          key = k
    keys = set() # set of existing keys
    s = self._search(key=key, text=text, **kwargs)
    try:
      for item in s:
        k = str(item.pop('id'))
        if not key:
          if k in keys:
            continue
          else:
            keys.add(k)
        item['key'] = k

        title = self._beautifyTitle(item['title'])
        if not title:
          continue
        item['title'] = title

        d = item.get('date') or 0 # int
        if d:
          try:
            d = datetime.strptime(d, '%Y/%m/%d')
            d = skdatetime.date2timestamp(d)
          except:
            dwarn("failed to parse date")
            d = 0
        item['date'] = d

        ret.append(item)
    except Exception, e: dwarn(e)
    dprint("leave: count = %s" % len(ret))
    return ret

## Getchu API ##

class GetchuApi(object):

  def __init__(self, online=True):
    """
    @param* online  bool
    """
    self.online = online

    from getchu.search import SearchApi
    self.SEARCH_GENRES = SearchApi.PC_GAME_GENRES # [str]

  def setOnline(self, v):
    if self.online !=  v:
      self.online = v
      if hasmemoizedproperty(self, 'cachingSoftApi'):
        self.cachingSoftApi.online = v

  _rx_title = re.compile( _re_title)
  @classmethod
  def _beautifyTitle(cls, t):
    """
    @param  t  unicode
    @return  unicode
    """
    return cls._rx_title.sub('', t).strip()

  @memoizedproperty
  def cachingSoftApi(self):
    from getchu.caching import CachingSoftApi
    return CachingSoftApi(
        cachedir=rc.DIR_CACHE_GETCHU,
        expiretime=config.REF_EXPIRE_TIME,
        online=self.online)

  @memoizedproperty
  def searchApi(self):
    from getchu.search import SearchApi
    return SearchApi()

  def _search(self, text=None, key=None, cache=True):
    """
    @param  cache  bool  not used
    @yield  kw
    """
    dprint("key, text =", key, text)
    if key:
      kw = self.cachingSoftApi.query(key)
      if kw:
        yield kw
    elif text:
      for genre in self.SEARCH_GENRES:
        q = self.searchApi.query(text, genre=genre)
        if q:
          for it in q:
            yield it

  def cache(self, text=None, key=None):
    if key:
      dprint("enter")
      self.cachingSoftApi.cache(key)
      dprint("leave")

  @staticmethod
  def _parsekey(url):
    """
    @param  url  unicode
    @return  unicode or None
    """
    if url:
      m = re.search(r"id=([0-9]+)", url)
      if m:
        return m.group(1)

  # See: https://affiliate.dmm.com/api/reference/r18/pcgame/
  def query(self, key=None, text=None, **kwargs):
    """
    @return  iter not None
    """
    dprint("enter")
    ret = []
    if not key and text:
      if text.isdigit():
        key = text
      elif text.startswith('http://') or text.startswith('www.'):
        k = self._parsekey(text)
        if k:
          key = k
    keys = set() # set of existing keys
    s = self._search(key=key, text=text, **kwargs)
    try:
      for item in s:
        k = str(item.pop('id'))
        if not key:
          if k in keys:
            continue
          else:
            keys.add(k)
        item['key'] = k

        media = item.get('media')
        if media and not media.endswith('ROM') and not media.endswith('ソフト'): # "UMDソフト", etc
          continue
        title = self._beautifyTitle(item['title'])
        if not title:
          continue
        item['title'] = title

        d = item.get('date') or 0 # int
        if d:
          try:
            d = datetime.strptime(d, '%Y/%m/%d')
            d = skdatetime.date2timestamp(d)
          except:
            dwarn("failed to parse date")
            d = 0
        item['date'] = d
        item['image'] = item['img']

        ret.append(item)
    except Exception, e: dwarn(e)
    dprint("leave: count = %s" % len(ret))
    return ret

## Gyutto API ##

class GyuttoApi(object):

  def __init__(self, online=True):
    """
    @param* online  bool
    """
    self.online = online

    from gyutto.search import SearchApi
    self.SEARCH_CATEGORIES = SearchApi.GAME_CATEGORIES # [int]

  def setOnline(self, v):
    if self.online !=  v:
      self.online = v
      if hasmemoizedproperty(self, 'cachingItemApi'):
        self.cachingItemApi.online = v

  #_rx_title = re.compile( _re_title)
  #@classmethod
  #def _beautifyTitle(cls, t):
  #  """
  #  @param  t  unicode
  #  @return  unicode
  #  """
  #  return cls._rx_title.sub('', t).strip()

  @memoizedproperty
  def cachingItemApi(self):
    from gyutto.caching import CachingItemApi
    return CachingItemApi(
        cachedir=rc.DIR_CACHE_GYUTTO,
        expiretime=config.REF_EXPIRE_TIME,
        online=self.online)

  @memoizedproperty
  def searchApi(self):
    from gyutto.search import SearchApi
    return SearchApi()

  def _search(self, text=None, key=None, cache=True):
    """
    @param  cache  bool  not used
    @yield  kw
    """
    dprint("key, text =", key, text)
    if key:
      if isinstance(key, basestring) and key.startswith('http://'):
        kw = self.cachingItemApi.query(url=key)
      else:
        kw = self.cachingItemApi.query(key)
      if kw:
        yield kw
    elif text:
      for cat in self.SEARCH_CATEGORIES:
        q = self.searchApi.query(text, category_id=cat)
        if q:
          for it in q:
            yield it

  def cache(self, text=None, key=None):
    if key:
      dprint("enter")
      self.cachingItemApi.cache(key)
      dprint("leave")

  @staticmethod
  def _parsekey(url):
    """
    @param  url  unicode
    @return  unicode or None
    """
    if url:
      m = re.search(r"item([0-9]+)", url)
      if m:
        return m.group(1)

  # See: https://affiliate.dmm.com/api/reference/r18/pcgame/
  def query(self, key=None, text=None, **kwargs):
    """
    @return  iter not None
    """
    dprint("enter")
    ret = []
    if not key and text:
      if text.isdigit() or text.startswith('http://'): # use URL as key
        key = text
      elif text.startswith('gyutto.'): # gyutto.com or gyutto.me
        key = 'http://' + text
      elif text.startswith('www.gyutto.'): # gyutto.com or gyutto.me
        key = 'http://' + text[4:]
      elif 'item' in text:
        k = self._parsekey(text)
        if k:
          key = k
    s = self._search(key=key, text=text, **kwargs)
    try:
      for item in s:
        item['key'] = str(item.pop('id'))

        d = item.get('date') or 0 # int
        if d:
          d = skdatetime.date2timestamp(d)
        item['date'] = d

        ret.append(item)
    except Exception, e: dwarn(e)
    dprint("leave: count = %s" % len(ret))
    return ret

## DiGiket API ##

class DiGiketApi(object):

  def __init__(self, online=True):
    """
    @param* online  bool
    """
    self.online = online

    from digiket.search import SearchApi
    self.SEARCH_PATHS = SearchApi.GAME_PATHS # [unicode]

  def setOnline(self, v):
    if self.online !=  v:
      self.online = v
      if hasmemoizedproperty(self, 'cachingItemApi'):
        self.cachingItemApi.online = v

  #_rx_title = re.compile( _re_title)
  #@classmethod
  #def _beautifyTitle(cls, t):
  #  """
  #  @param  t  unicode
  #  @return  unicode
  #  """
  #  return cls._rx_title.sub('', t).strip()

  @memoizedproperty
  def cachingItemApi(self):
    from digiket.caching import CachingItemApi
    return CachingItemApi(
        cachedir=rc.DIR_CACHE_DIGIKET,
        expiretime=config.REF_EXPIRE_TIME,
        online=self.online)

  @memoizedproperty
  def searchApi(self):
    from digiket.search import SearchApi
    return SearchApi()

  def _search(self, text=None, key=None, cache=True):
    """
    @param  cache  bool  not used
    @yield  kw
    """
    dprint("key, text =", key, text)
    if key:
      kw = self.cachingItemApi.query(key)
      if kw:
        yield kw
    elif text:
      for path in self.SEARCH_PATHS:
        q = self.searchApi.query(text, path=path)
        if q:
          for it in q:
            yield it

  def cache(self, text=None, key=None):
    if key:
      dprint("enter")
      self.cachingItemApi.cache(key)
      dprint("leave")

  @staticmethod
  def _parsekey(url):
    """
    @param  url  unicode
    @return  unicode or None
    """
    if url:
      m = re.search(r"ITM0*([0-9]+)", url)
      if m:
        return m.group(1)

  # See: https://affiliate.dmm.com/api/reference/r18/pcgame/
  def query(self, key=None, text=None, **kwargs):
    """
    @return  iter not None
    """
    dprint("enter")
    ret = []
    if not key and text:
      if text.isdigit():
        key = text
      elif 'ITM' in text:
        k = self._parsekey(text)
        if k:
          key = k
    s = self._search(key=key, text=text, **kwargs)
    try:
      for item in s:
        item['key'] = str(item.pop('id'))

        d = item.get('date') or 0 # int
        if d:
          d = skdatetime.date2timestamp(d)
        item['date'] = d

        ret.append(item)
    except Exception, e: dwarn(e)
    dprint("leave: count = %s" % len(ret))
    return ret

## DLsite API ##

class DLsiteApi(object):

  def __init__(self, online=True):
    """
    @param* online  bool
    """
    self.online = online

  def setOnline(self, v):
    if self.online !=  v:
      self.online = v
      if hasmemoizedproperty(self, 'cachingWorkApi'):
        self.cachingWorkApi.online = v
      #for k in 'cachingSearchApi', 'cachingWorkApi':
      #  if hasmemoizedproperty(self, k):
      #    getattr(self, k).online = online

  #_rx_title = re.compile( _re_title)
  #@classmethod
  #def _beautifyTitle(cls, t):
  #  """
  #  @param  t  unicode
  #  @return  unicode
  #  """
  #  return cls._rx_title.sub('', t).strip()

  @memoizedproperty
  def cachingWorkApi(self):
    from dlsite.caching import CachingWorkApi
    return CachingWorkApi(
        cachedir=rc.DIR_CACHE_DLSITE,
        expiretime=config.REF_EXPIRE_TIME,
        online=self.online)

  @memoizedproperty
  def searchApi(self):
    from dlsite.search import SearchApi
    return SearchApi()

  #@memoizedproperty
  #def cachingSearchApi(self):
  #  from getchu.caching import CachingSearchApi
  #  return CachingSearchApi(
  #      cachedir=rc.DIR_CACHE_DLSITE,
  #      expiretime=config.REF_EXPIRE_TIME,
  #      online=self.online)

  #_rx_key = re.compile(r'[A-Z]J[0-9]+', re.IGNORECASE)
  def _search(self, text=None, key=None, cache=True):
    """
    @param* cache  bool  not used
    @param* key  str  URL
    @param* text  unicode
    @yield  kw
    """
    dprint("key, text =", key, text)
    #if not key and text and self._rx_key.match(text):
    #  key = text
    if not key and text:
      if text.startswith('www.'):
        text = 'http://' + text
      if text.startswith('http://'):
        key = text
    if key:
      key = proxy.get_dlsite_url(key)
      kw = self.cachingWorkApi.query(key)
      if kw:
        yield kw
    elif text:
      keys = set()
      for domain in self.searchApi.DOMAINS:
        q = self.searchApi.query(text, domain=domain)
        if q:
          for it in q:
            url = it['url']
            k = self._parsekey(url)
            if k and k not in keys:
              yield it
              keys.add(k)

  _rx_parsekey = re.compile(r'/([0-9A-Z]+)\.html')
  def _parsekey(self, url):
    """
    @param  url  str
    @return  str
    """
    try: return self._rx_parsekey.search(url).group(1)
    except AttributeError: pass

  def cache(self, text=None, key=None):
    if key:
      dprint("enter")
      #self.cachingSearchApi.cache(key)
      self.cachingWorkApi.cache(key)
      dprint("leave")

  def query(self, **kwargs):
    """
    @param  assume key is URL
    @return  iter not None
    """
    dprint("enter")
    ret = []
    #if not key and text and text.startswith('DJ'):
    #  key = text
    #keys = set() # set of existing keys
    s = self._search(**kwargs)
    try:
      for item in s:
        url = item['url']
        k = self._parsekey(url)
        if not k:
          dwarn("missing DJ key")
          continue
        item['key'] = k

        d = item.get('date') or 0 # int
        if d:
          d = skdatetime.date2timestamp(d)
        item['date'] = d

        ret.append(item)
    except Exception, e: dwarn(e)
    dprint("leave: count = %s" % len(ret))
    return ret

## Amazon ##

class AmazonApi(object):

  def __init__(self, online=True):
    """
    @param* online  bool
    """
    self.online = online

  def setOnline(self, v):
    if self.online !=  v:
      self.online = v
      if hasmemoizedproperty(self, 'cachingApi'):
        self.cachingApi.online = v

  _rx_title = re.compile('|'.join((
    ur'.[Aa]mazon.*',
    _re_title,
  )))
  @classmethod
  def _beautifyTitle(cls, t):
    """
    @param  t  unicode
    @return  unicode or None
    """
    #if not t or re.search(ur'廉価版|通常版', t):
    if not t or 'DVDPG' in t:
      return
    t = cls._rx_title.sub('', t).strip()
    t = re.sub(ur'\($', '', t).strip()
    return t

  @memoizedproperty
  def cachingApi(self):
    #from amazonproduct.api import API
    # See: http://docs.aws.amazon.com/AWSECommerceService/latest/DG/CHAP_MotivatingCustomerstoBuy.html
    # Review URL will expire after 24 hours!
    expireTime = 3600 * 22   # every 22 hours
    from amazon.caching import CachingRestApi
    return CachingRestApi(
        access_key_id=config.AWS_ACCESS_KEY,
        secret_access_key=config.AWS_SECRET_KEY,
        locale=config.AWS_REGION,
        associate_tag=config.AWS_ASSOCIATE_TAG,
        cachedir=rc.DIR_CACHE_AWS,
        #expiretime=config.REF_EXPIRE_TIME,
        expiretime=expireTime,
        online=self.online)

  @memoizedproperty
  def api(self):
    from amazonproduct.api import API
    return API(
        access_key_id=config.AWS_ACCESS_KEY,
        secret_access_key=config.AWS_SECRET_KEY,
        locale=config.AWS_REGION,
        associate_tag=config.AWS_ASSOCIATE_TAG)

  @staticmethod
  def _parsekey(url):
    """
    @param  url  unicode
    @return  unicode or None
    """
    if url:
      #m = re.search(r"/(B00[0-9A-Z]+)", url)
      m = re.search(r"/(B[0-9A-Z]+)", url)
      if m:
        return m.group(1)

  def _search(self, text=None, key=None, cache=True):
    """
    @return  iter
    """
    dprint("key, text =", key, text)
    api = self.cachingApi if cache else self.api
    if key: return api.item_lookup(key,
        ResponseGroup='Large')
    elif text: return api.item_search(
        'Software',
        Keywords=text,
        ResponseGroup='Large',
        limit=10) # page size
    else: return []

  def cache(self, *args, **kwargs):
    dprint("enter")
    try: self._search(*args, **kwargs)
    except Exception, e: dwarn(e)
    dprint("leave")

  def query(self, key=None, text=None, pagelimit=10, **kwargs):
    """
    @return  iter not None
    """
    dprint("enter")
    # Manually set amazon key
    #kwargs['key'] = 'B008VQ2OAY'
    #MAPPING_STR = ('title', 'Title'), ('label', 'Label'), ('brand', 'Brand')
    MAPPING_STR = ('title', 'Title'), ('brand', 'Brand')
    ret = []
    keys = set() # already queried keys
    if not key and text:
      if text.startswith('B00'):
        key = text
      elif text.startswith('http://') or text.startswith('www.'):
        k = self._parsekey(text)
        if k:
          key = k
    try:
      s = self._search(key=key, text=text, **kwargs)
      for index, root in enumerate(s):
        if index > pagelimit:
          dwarn("ignore too many pages: pageno = %s" % index)
          return ret

        # extract paging information
        #total_results = root.Items.TotalResults.pyval
        #total_pages = root.Items.TotalPages.pyval

        #try:
        #  current_page = root.Items.Request.ItemSearchRequest.ItemPage.pyval
        #except AttributeError:
        #  current_page = 1

        #print 'page %d of %d' % (current_page, total_pages)

        # from lxml import etree
        # print etree.tostring(root, pretty_print=True)

        nspace = root.nsmap.get(None, '')
        NS = {'aws':nspace}
        items = root.xpath('//aws:Items/aws:Item', namespaces=NS)

        # https://github.com/yoavaviram/python-amazon-simple-product-api/blob/master/amazon/api.py
        for item in items:
          try:
            k = item.ASIN
            if not key:
              if k in keys:
                continue
              else:
                keys.add(k)
            kw = {'key':k}
          except AttributeError: continue
          attrs = item.ItemAttributes
          try:
            if not key and (
                attrs.ProductTypeName not in ('SOFTWARE', 'ABIS_SOFTWARE', 'ABIS_DOWNLOADABLE_SOFTWARE', 'HOBBIES') or
                attrs.Binding == 'CD'):
                #attrs.Binding in ('CD', 'CD-ROM')):
              continue
          except AttributeError: continue

          # String elements are lxml.objectify.StringElement and needed to convert to str
          try:
            kw['largeImage'] = str(item.LargeImage.URL)
            kw['mediumImage'] = str(item.MediumImage.URL)
            kw['smallImage'] = str(item.SmallImage.URL)
          except AttributeError: pass

          try:
            images = []
            # There are two kinds of images: primary | variant
            imageItems = item.ImageSets.xpath('//aws:ImageSet[@Category="variant"]', namespaces=NS)
            for it in imageItems:
              # Amazon has LargeImage, MediumImage, smallImage, TinyImage, ThumbnailImage, SwatchImage
              url = getattr(it, 'LargeImage').URL or getattr(it, 'MediumImage').URL
              url = str(url)
              if url:
                images.append(url)
            if images:
              kw['sampleImages'] = images
          except AttributeError: pass

          # CHECKPOINT: skip bad descriptions with specific source
          kw['descriptions'] = []
          try:
            # EditorialReview.Source = "Product Description"
            #review = item.EditorialReviews.EditorialReview.Content
            for it in item.EditorialReviews.xpath('//aws:EditorialReview', namespaces=NS):
              #type = it.Source # 'Product Description', 'Amazonより', etc.
              #dprint(type)
              t = unicode(it.Content)
              kw['descriptions'].append(t)
          except (AttributeError, UnicodeDecodeError): pass

          try:
            if item.CustomerReviews.HasReviews == True: # force converting lxml.objectify.BoolElement to bool
              kw['review'] = str(item.CustomerReviews.IFrameURL)
          except AttributeError: pass

          try: kw['price'] = int(attrs.ListPrice.Amount)
          except (AttributeError, ValueError, TypeError): pass

          try: kw['ecchi'] = 1 == int(attrs.IsAdultProduct)
          except (AttributeError, ValueError, TypeError): pass

          try:
            d = datetime.strptime(str(attrs.ReleaseDate), '%Y-%m-%d')
            kw['date'] = skdatetime.date2timestamp(d)
            #  #ATTRS = 'Brand', 'EAN',  'Label', 'ReleaseDate', 'Title'
          except (AttributeError, TypeError, ValueError): pass

          for k, a in MAPPING_STR:
            try: kw[k] = unicode(getattr(attrs, a))
            except (AttributeError, UnicodeDecodeError): pass

          if kw.get('brand') == u"不明":
            del kw['brand']

          try:
            title = self._beautifyTitle(kw['title'])
            if title:
              kw['title'] = title
            elif not key:
              continue
          except KeyError: continue
          kw['url'] = 'http://amazon.co.jp/dp/' + kw['key']
          ret.append(kw)

    except Exception, e: dwarn(e)
    dprint("leave: count = %s" % len(ret))
    return ret

## DMM ##

class DmmApi(object):

  def __init__(self, online=True):
    """
    @param* online  bool
    """
    self.online = online

  def setOnline(self, v):
    if self.online !=  v:
      self.online = v
      if hasmemoizedproperty(self, 'cachingApi'):
        self.cachingApi.online = v

  _rx_title = re.compile('|'.join((
    _re_title,
    ur'通常版.*',
    ur'廉価版.*',
    ur' DMM.*',
    ur' ダウンロード.*',
  )))
  @classmethod
  def _beautifyTitle(cls, t):
    """
    @param  t  unicode
    @return  unicode
    """
    if not t or 'DVDPG' in t:
      return
    t = cls._rx_title.sub('', t).strip()
    t = re.sub(ur'\($', '', t).strip()
    return t

  _rx_keyword = re.compile('|'.join((
    ur'その他',
    ur'アドベンチャー',
    ur'音声付き',
    'DMM',
    'Windows',
    ur'デモ・体験版あり',
    ur'数量限定セール',
    ur'.*キャンペーン',
    ur'.*円以下',
  )))
  @classmethod
  def _isBadKeyword(cls, t):
    """
    @param  t  unicode
    @return  bool
    """
    return cls._rx_keyword.match(t)

  @memoizedproperty
  def cachingApi(self):
    from dmm.caching import CachingRestApi
    return CachingRestApi(
        api_id=config.DMM_API_ID,
        affiliate_id=config.DMM_AFFILIATE_ID,
        cachedir=rc.DIR_CACHE_DMM,
        expiretime=config.REF_EXPIRE_TIME,
        online=self.online)

  @memoizedproperty
  def api(self):
    from dmm.rest import RestApi
    return RestApi(
        api_id=config.DMM_API_ID,
        affiliate_id=config.DMM_AFFILIATE_ID)

  @staticmethod
  def _parsekey(url):
    """
    @param  url  unicode
    @return  unicode or None
    """
    if url:
      m = re.search(r"cid=([0-9a-z]+)", url)
      if m:
        return m.group(1)

  _rx_key = re.compile(r'[0-9a-z]+')
  @classmethod
  def _iskey(cls, text):
    """
    @param  text  unicode
    @return  bool
    """
    return bool(cls._rx_key.match(text))

  def _search(self, text=None, key=None, cache=True):
    """
    @return  iter
    """
    dprint("key, text =", key, text)
    if not key and text:
      if self._iskey(text):
        key = text
      elif text.startswith('http://') or text.startswith('www.'):
        k = self._parsekey(text)
        if k:
          key = k
    api = self.cachingApi if cache else self.api
    t = key or text
    return api.query(t, hits=20) if t else [] # max number: 20

  def cache(self, *args, **kwargs):
    dprint("enter")
    self._search(*args, **kwargs)
    dprint("leave")

  # See: https://affiliate.dmm.com/api/reference/r18/pcgame/
  def query(self, **kwargs):
    """
    @return  iter not None
    """
    dprint("enter")
    ret = []
    key = kwargs.get('key')
    keys = set() # set of keys
    try:
      s = self._search(**kwargs)
      if s:
        for item in s:
          kw = {}
          for el in item:
            tag = el.tag
            if tag == 'content_id':
              k = el.text
              if key:
                if key != k:
                  continue
              else:
                if k in keys:
                  continue
                else:
                  keys.add(k)
              keys.add(k)
              kw['key'] = k
            #elif tag == 'product_id':
            #  kw['productId'] = el.text
            elif tag in ('service_name', 'floor_name'):
              kw[tag] = el.text
            elif tag == 'title':
              title = self._beautifyTitle(el.text)
              if not title:
                continue
              kw['title'] = title
            elif tag == 'date':
              try:
                t = el.text.split()[0]
                d = datetime.strptime(t, '%Y-%m-%d')
                kw['date'] = skdatetime.date2timestamp(d)
              except (IndexError, AttributeError, TypeError, ValueError): pass
            elif tag == 'prices':
              x = el.find('price')
              if x is not None:
                try: kw['price'] = int(x.text)
                except (TypeError, ValueError), e: pass
            elif tag == 'URL':
            #elif el.tag == 'affiliateURL':
              kw['url'] = el.text
            elif tag == 'imageURL':
              for i in el:
                itag = i.tag
                itext = i.text
                if itag == 'large':
                   kw['largeImage'] = itext
                elif itag == 'small':
                   kw['mediumImage'] = itext
                elif itag == 'list':
                   kw['smallImage'] = itext
                else:
                  dwarn("unknown image tag", itag)
            elif tag == 'sampleImageURL':
              for i in el:
                l = []
                for j in i:
                  url = j.text.replace('js-', 'jp-')
                  l.append(url)
                if l:
                  kw['sampleImages'] = l
            elif tag == 'iteminfo':
              for i in el:
                try:
                  itag = i.tag
                  itext = i.find('name').text
                  iid = i.find('id').text
                  if iid.endswith('_ruby') or self._isBadKeyword(itext):
                    continue
                  if itag in ('maker', 'series'):
                    kw[itag] = itext
                  elif itag in ('author', 'keyword'):
                    key = itag + 's'
                    if key in kw:
                      kw[key].append(itext)
                    else:
                      kw[key] = [itext]
                except Exception, e: dwarn(e)

          if 'key' not in kw or 'title' not in kw:
            dprint("missing key cid or title")
            continue

          try: # mono, pcgame, doujin,
            if kw['service_name'] not in (u'通販', u'美少女ゲーム', u'同人'):
              continue
            if kw['floor_name'] == u'アニメ':
              continue
            if '/book/' in kw['url']:
              continue
          except Exception: continue

          maker = kw.get('maker')
          if maker:
            kw['brand'] = maker.replace(" / ", ',')

          authors = kw.get('authors')
          if authors:
            kw['authors'] = authors

          keywords = kw.get('keywords') or []
          if keywords:
            kw['ecchi'] = not (u'一般作品' in keywords or u'全年齢向け' in keywords)
            kw['otome'] = u"ボーイズラブ" in keywords or u'女性向け' in keywords

            #genres = [v for k,v in (
            #    (u'RPG', 'RPG'),
            #    (u'シミュレーション', 'SLG'),
            #    (u'アクション', 'ACT'),
            #    ('3D', '3D'),
            #    ('3DCG', '3D'),
            #    (u'アニメ', 'Anime'),
            #    (u'アニメーション', 'Anime'),
            #    (u'動画・アニメーション', 'Anime'),
            #    #(u'アドベンチャー', 'AVG'),
            #  ) if k in keywords]
            #if genres:
            #  kw['genres'] = uniquelist(genres)

            l = []
            for word in keywords:
              for it in word.split(u'・'):
                l.append(it)
            keywords = l

          kw['keywords'] = keywords

          if kw['service_name'] == u'同人':
            kw['doujin'] = True

          ret.append(kw)

    except Exception, e: dwarn(e)
    dprint("leave: count = %s" % len(ret))
    return ret

## API Wrapper ##

class AsyncApi:
  def __init__(self, api=None):
    self.api = api

  def setOnline(self, v): self.api.setOnline(v)

  def query(self, async=True, **kwargs):
    """
    @param* text  unicode  default None
    @param* key  str  default None
    @param* async  bool  default True
    @param* cache  bool  default True
    @return  [{dataman.DmmReference.kw}] not None
    """
    #if not text and not key:
    #  dwarn("missing both search text and key")
    #  return []
    return skthreads.runsync(partial(
      self.api.query, **kwargs),
    ) if async else self.api.query(**kwargs)

  def cache(self, async=True, **kwargs):
    """
    @param* text  unicode  default None
    @param* key  str  default None
    @param* async  bool  default True
    @param* cache  bool  default True
    """
    skthreads.runasync(partial( # async, not sync!
        self.api.cache, **kwargs)) if async else self.api.cache(**kwargs)

## References ##

class _ReferenceManager(object):
  # The same as dataman.Reference.TYPES
  API_TYPES = frozenset(('trailers', 'scape', 'freem', 'steam', 'holyseal', 'melon', 'getchu', 'gyutto', 'amazon', 'dmm', 'dlsite', 'digiket'))

  def __init__(self):
    self.online = True

  def _createApi(self, cls):
    return AsyncApi(api=cls(online=self.online))

  @memoizedproperty
  def amazonApi(self): return self._createApi(AmazonApi)

  @memoizedproperty
  def dmmApi(self): return self._createApi(DmmApi)

  @memoizedproperty
  def melonApi(self): return self._createApi(MelonApi)

  @memoizedproperty
  def getchuApi(self): return self._createApi(GetchuApi)

  @memoizedproperty
  def gyuttoApi(self): return self._createApi(GyuttoApi)

  @memoizedproperty
  def digiketApi(self): return self._createApi(DiGiketApi)

  @memoizedproperty
  def dlsiteApi(self): return self._createApi(DLsiteApi)

  @memoizedproperty
  def freemApi(self): return self._createApi(FreemApi)

  @memoizedproperty
  def steamApi(self): return self._createApi(SteamApi)

  @memoizedproperty
  def holysealApi(self): return self._createApi(HolysealApi)

  @memoizedproperty
  def scapeApi(self): return self._createApi(ScapeApi)

  @memoizedproperty
  def trailersApi(self): return self._createApi(TrailersApi)

  def iterApis(self):
    """
    @yield  api
    """
    for t in self.API_TYPES:
      pty = t + 'Api'
      if hasmemoizedproperty(self, pty):
        yield getattr(self, pty)

  def getApi(self, type):
    if type in self.API_TYPES:
      return getattr(self, type + 'Api')

class ReferenceManager:
  def __init__(self):
    self.__d = _ReferenceManager()

  # FIXME: parent is not broadcast to apis
  # Other wise, it will raise the following error:
  #    QObject: Cannot create children for a parent that is in a different thread.
  #
  #def parent(self): return self.__d.parent
  #def setParent(self, v):
  #  super(ReferenceManager, self).setParent(v)
  #  d = self.__d
  #  #if d.parent != v:
  #  d.parent = v
  #  for api in d.iterApis():
  #    api.parent = parent

  def isOnline(self): return self.__d.online
  def setOnline(self, v):
    d = self.__d
    if d.online != v:
      d.online = v
      for api in d.iterApis():
        api.setOnline(v)

  #@memoized # cached
  def query(self, type, **kwargs):
    """
    @param  type  'amazon' or 'dmm' or 'trailers'
    @param* text  unicode  default None
    @param* key  str  default None
    @param* async  bool  default True
    @param* cache  bool  default True
    @return  [{dataman.Reference.kw}] not None
    """
    #if not text and not key:
    #  dwarn("missing both search text and key")
    #  return []
    api = self.__d.getApi(type)
    #if not api: return []
    ret = api.query(**kwargs)
    if ret:
      for it in ret:
        it['type'] = type
    else:
      ret = []
    return ret

  def queryOne(self, **kwargs):
    """
    @param* text  unicode  default None
    @param* key  str  default None
    @param* async  bool  default True
    @param* cache  bool  default True
    @return  {kw} or None
    """
    ret = self.query(**kwargs)
    return ret[0] if ret else None

  def cache(self, type, **kwargs):
    """
    @param  type  'amazon' or 'dmm' or 'trailers'
    @param* text  unicode  default None
    @param* key  str  default None
    @param* async  bool  default True
    @param* cache  bool  default True
    """
    if self.isOnline():
      api = self.__d.getApi(type)
      #if not api: return
      api.cache(**kwargs)

## Specific to Youtube trailers ##

class _TrailersManager(object):

  def __init__(self):
    self.online = True

  @memoizedproperty
  def api(self): # Always caching
    from erogetrailers.caching import CachingSoftApi
    return CachingSoftApi(rc.DIR_CACHE_TRAILERS,
        expiretime=config.REF_EXPIRE_TIME,
        online=self.online)

  def query(self, *args, **kwargs):
    ret = self.api.query(*args, **kwargs)
    if ret and ret['videos']:
      for it in ret['videos']:
        it['vid'] = it.pop('youtube') # rename youtube to vid
    return ret

class TrailersManager:

  def __init__(self):
    self.__d = _TrailersManager()

  def isOnline(self): return self.__d.online
  def setOnline(self, v):
    d = self.__d
    if d.online != v:
      d.online = v
      if hasmemoizedproperty(d, 'api'):
        d.api.online = v

  #@memoized # cached
  def query(self, id, async=True):
    """
    @param  id  int or str  ID
    @return  {kw}
    """
    return skthreads.runsync(partial(
      self.__d.query, id),
    ) if async else self.__d.query(id)

## Getchu review manager ##

class _GetchuManager(object):

  def __init__(self):
    self.online = True

  @memoizedproperty
  def reviewApi(self): # Always caching
    from getchu.caching import CachingReviewApi
    return CachingReviewApi(rc.DIR_CACHE_GETCHU,
        expiretime=config.REF_EXPIRE_TIME,
        online=self.online)

class GetchuManager:

  def __init__(self):
    self.__d = _GetchuManager()

  def isOnline(self): return self.__d.online
  def setOnline(self, v):
    d = self.__d
    if d.online != v:
      d.online = v
      if hasmemoizedproperty(d, 'reviewApi'):
        d.reviewApi.online = v

  #@memoized # cached
  def queryReview(self, id, async=True):
    """
    @param  id  int or str  ID
    @return  unicode or None
    """
    return skthreads.runsync(partial(
      self.__d.reviewApi.query, id),
    ) if async else self.__d.reviewApi.query(id)

## Amazon review manager ##

class _AmazonManager(object):

  def __init__(self):
    self.online = True

  @memoizedproperty
  def reviewApi(self): # Always caching
    from restful.online import DataParser
    from restful.offline import DataCacher
    cls = DataCacher(DataParser, suffix='.html')
    cls.ENCODING = 'sjis'
    return cls(rc.DIR_CACHE_AWS, online=self.online) #expiretime=0,

class AmazonManager:

  def __init__(self):
    self.__d = _AmazonManager()

  def isOnline(self): return self.__d.online
  def setOnline(self, v):
    d = self.__d
    if d.online != v:
      d.online = v
      if hasmemoizedproperty(d, 'reviewApi'):
        d.reviewApi.online = v

  #@memoized # cached
  def queryReview(self, url, async=True):
    """
    @param  url  str
    @return  unicode or None
    """
    return skthreads.runsync(partial(
      self.__d.reviewApi.query, url),
    ) if async else self.__d.reviewApi.query(url)

## Gyutto review manager ##

class _GyuttoManager(object):

  def __init__(self):
    self.online = True

  @memoizedproperty
  def reviewApi(self): # Always caching
    from gyutto.caching import CachingReviewApi
    return CachingReviewApi(rc.DIR_CACHE_GYUTTO,
        expiretime=config.REF_EXPIRE_TIME,
        online=self.online)

class GyuttoManager:

  def __init__(self):
    self.__d = _GyuttoManager()

  def isOnline(self): return self.__d.online
  def setOnline(self, v):
    d = self.__d
    if d.online != v:
      d.online = v
      if hasmemoizedproperty(d, 'reviewApi'):
        d.reviewApi.online = v

  #@memoized # cached
  def queryReview(self, id, async=True):
    """
    @param  id  int or str  ID
    @return  unicode or None
    """
    return skthreads.runsync(partial(
      self.__d.reviewApi.query, id),
    ) if async else self.__d.reviewApi.query(id)

# Specific to DMM

class _DmmManager(object):

  def __init__(self):
    self.online = True

  @memoizedproperty
  def api(self): # Always caching
    from dmm.caching import CachingGameApi
    return CachingGameApi(rc.DIR_CACHE_DMM,
        expiretime=config.REF_EXPIRE_TIME,
        online=self.online)

class DmmManager:

  def __init__(self):
    self.__d = _DmmManager()

  def isOnline(self): return self.__d.online
  def setOnline(self, v):
    d = self.__d
    if d.online != v:
      d.online = v
      if hasmemoizedproperty(d, 'api'):
        d.api.online = v

  #@memoized # cached
  def query(self, url, async=True):
    """
    @param  url  str
    @return  {kw}
    """
    return skthreads.runsync(partial(
      self.__d.api.query, url),
    ) if async else self.__d.api.query(url)

  #def cache(self, url, async=True):
  #  """
  #  @param  id  int or str  Getchu soft ID
  #  """
  #  skthreads.runasync(partial(
  #    self.__d.api.cache, id),
  #  ) if async else self.__d.api.cache(id)

# Erogame Tokuten

class _TokutenManager(object):

  def __init__(self):
    self.online = True

  @memoizedproperty
  def api(self): # Always caching
    from erogametokuten.caching import CachingTitleApi
    return CachingTitleApi(rc.DIR_CACHE_TOKUTEN,
        expiretime=config.REF_EXPIRE_TIME,
        online=self.online)

  def query(self, key):
    kw = self.api.query(key)
    if kw:
      kw['key'] = kw.pop('id')
    return kw

class TokutenManager:

  def __init__(self):
    self.__d = _TokutenManager()

  def isOnline(self): return self.__d.online
  def setOnline(self, v):
    d = self.__d
    if d.online != v:
      d.online = v
      if hasmemoizedproperty(d, 'api'):
        d.api.online = v

  #@memoized # cached
  def query(self, key, async=True):
    """
    @param  key  long or str
    @return  {kw}
    """
    return skthreads.runsync(partial(
      self.__d.query, key),
    ) if async else self.__d.query(key)

  #def cache(self, url, async=True):
  #  """
  #  @param  id  int or str  Getchu soft ID
  #  """
  #  skthreads.runasync(partial(
  #    self.__d.api.cache, id),
  #  ) if async else self.__d.api.cache(id)

if __name__ == '__main__':
  #from amazonproduct.api import API
  #from amazonproduct.contrib.caching import ResponseCachingAPI as API

  def test_amazon():

    #from amazonproduct.api import API
    from amazonproduct.contrib.caching import ResponseCachingAPI as API

    # See: http://d.hatena.ne.jp/yuheiomori0718/20111212/1323697894
    api = API(
          config.AWS_ACCESS_KEY, config.AWS_SECRET_KEY, config.AWS_REGION,
          associate_tag=config.AWS_ASSOCIATE_TAG,
          cachedir=rc.DIR_CACHE_AWS)

    search = u"レミニセンス"
    search = u'マエバリ帝国の逆襲'
    #q = api.item_search(
    #    'Software',
    #    Keywords=search,
    #    ResponseGroup='Large',
    #    limit=10)

    key = 'B00DQ7BXAU'
    key = 'B00B7W8RRS'
    key = 'B00AT6K7OE'
    key = "B008VO9UZI"
    key = 'B009X6E5T4'
    key = 'B00972RTPG'
    q = api.item_lookup(key,
          ResponseGroup='Large')
    #asin = 'B00AT6K7OE'
    #asin = u'B003CEGOIS'
    #it = api.item_lookup(asin,
    #    ResponseGroup='Large')
    for root in q:

      # extract paging information
      #total_results = root.Items.TotalResults.pyval
      #total_pages = root.Items.TotalPages.pyval
      #try:
      #  current_page = root.Items.Request.ItemSearchRequest.ItemPage.pyval
      #except AttributeError:
      #  current_page = 1
      #print 'page %d of %d' % (current_page, total_pages)

      # from lxml import etree
      # print etree.tostring(root, pretty_print=True)

      nspace = root.nsmap.get(None, '')
      items = root.xpath('//aws:Items/aws:Item', namespaces={'aws':nspace})

      #attrs = 'Binding', 'Brand', 'CatalogNumberList', 'EAN', 'EANList', 'Format', 'Label', 'ListPrice', 'Manufacturer', 'OperatingSystem', 'PackageDimensions', 'PackageQuantity', 'Platform', 'ProductGroup', 'ProductTypeName', 'Publisher', 'ReleaseDate', 'Studio', 'Title'
      attrs = 'Binding', 'Brand', 'EAN', 'Format', 'Label', 'ListPrice', 'ProductGroup', 'ProductTypeName', 'ReleaseDate', 'Title'

      # Label, Publisher, Studio, Manufacturer
      # Brand

      # https://github.com/yoavaviram/python-amazon-simple-product-api/blob/master/amazon/api.py
      for item in items:
        print item.ASIN
        try:
          print item.LargeImage.URL
          print item.MediumImage.URL
          print item.SmallImage.URL
          print item.CustomerReviews.HasReviews == True

          print item.CustomerReviews.IFrameURL

          urls = []
          # There are two kinds of images: primary | variant
          images = item.ImageSets.xpath('//aws:ImageSets/aws:ImageSet[@Category="variant"]', namespaces={'aws':nspace})
          for image in images:
            url = getattr(image, 'LargeImage').URL or getattr(image, 'MediumImage').URL
            urls.append(str(url))
          print urls
        except: pass

        try:
          for it in item.EditorialReviews.xpath('//aws:EditorialReview', namespaces={'aws':nspace}):
            print unicode(it.Source)
            #print it.EditorialReview.Source # "Product Description"
            review = it.Content
            t = unicode(review)
            print t
        except (AttributeError, UnicodeDecodeError): pass
        for a in attrs:
          #try:
          #  if item.ItemAttributes.ProductTypeName != 'ABIS_SOFTWARE':
          #    continue
          #  if item.ItemAttributes.Binding != 'DVD-ROM':
          #    continue
          #except: continue
          try:
            if a == 'ListPrice':
              print "ListPrice =", unicode(item.ItemAttributes.ListPrice.FormattedPrice), ",",
            else:
              print a, "=", unicode(getattr(item.ItemAttributes, a)), ",",
          except Exception: a, "=,",
        print

  def test_dmm():
    from dmm.caching import CachingRestApi as Api

    # See: http://d.hatena.ne.jp/yuheiomori0718/20111212/1323697894
    api = Api(api_id=config.DMM_API_ID, affiliate_id=config.DMM_AFFILIATE_ID, cachedir=rc.DIR_CACHE_DMM)

    # See: https://affiliate.dmm.com/api/reference/r18/pcgame/
    t = u"レミニセンス"
    t = u"暁の護衛"
    t = u"あやかしびと"
    t = '978will213'
    t = u"ROYAL"
    t = 'ggs_0143'
    t = '1322apc10070'
    s = api.query(t, hits=20)
    if s:
      for item in s:
        for el in item:
          if el.tag == 'title':
            print "title: %s" % el.text
          elif el.tag == 'content_id':
            print "cid: %s" % el.text
          elif el.tag == 'service_name':
            print "service_name: %s" % el.text
          elif el.tag == 'date':
            print "date: %s" % el.text
          elif el.tag == 'URL':
          #elif el.tag == 'affiliateURL':
            print "url: %s" % el.text
          elif el.tag == 'prices':
            price = el.find('price')
            if price is not None:
              print "price: %s" % price.text
          elif el.tag == 'imageURL':
            url = el.find('large')
            if url is not None:
              print "thumbnail: %s" % url.text
          elif el.tag == 'sampleImageURL':
            for it in el:
              print it.tag
            small = el.find('sample_s')
            if small is not None:
              for img in small:
                url = img.text.replace('js-', 'jp-')
                print url
          elif el.tag == 'iteminfo':
            for inf in el:
              name = inf.find('name')
              if name is not None:
                print inf.tag, name.text

  def test_trailers():
    import debug
    a = debug.app()
    m = manager()
    q = m.query(key=9610, type='trailers', async=False)

  def test_amazon_review():
    url = 'http://www.amazon.co.jp/reviews/iframe?akid=AKIAJSUDXZVM3TXLJXPQ&alinkCode=xm2&asin=B00AT6K7OE&atag=sakuradite-20&exp=2014-07-05T22%3A25%3A10Z&v=2&sig=gELwW4RmIrkrZ9ImIsItypJGeirqOFHRuwQU2EtZRMw%3D'
    print amazon().queryReview(url, async=False)

  test_amazon_review()
  #test_amazon()
  #test_dmm()
  #test_trailers()

# EOF

## Specific to Holyseal
#class _HolysealManager(object):
#
#  def __init__(self):
#    self.online = True
#    self._warmed = False
#
#  @memoizedproperty
#  def api(self): # Always caching
#    from holyseal.caching import CachingProductApi
#    return CachingProductApi(rc.DIR_CACHE_HOLYSEAL,
#        expiretime=config.REF_EXPIRE_TIME,
#        online=self.online)
#
#  def warmup(self):
#    if not self._warmed:
#      self.api
#      self._warmed = True
#
#  def query(self, id):
#    """
#    @param  id  int or str  ID
#    @return  {kw}
#    """
#    ret = self.api.query(id)
#    if ret:
#      ret['key'] = ret['id']
#      del ret['id']
#    return ret
#
#class HolysealManager:
#
#  def __init__(self):
#    self.__d = _HolysealManager()
#
#  def isOnline(self): return self.__d.online
#  def setOnline(self, v):
#    d = self.__d
#    if d.online != v:
#      d.online = v
#      if hasmemoizedproperty(d, 'api'):
#        d.api.online = v
#
#  #@memoized # cached
#  def query(self, id, async=True):
#    """
#    @param  id  int or str  ID
#    @return  {kw}
#    """
#    self.__d.warmup()
#    return skthreads.runsync(partial(
#      self.__d.query, id),
#    ) if async else self.__d.query(id)

## ErogameScape review ##

class _ScapeManager(object):

  def __init__(self):
    self.online = True

  @memoizedproperty
  def reviewApi(self): # Reviews are not cached
    from erogamescape.api import ReviewTableApi
    return ReviewTableApi()

  #@memoizedproperty
  #def cachedReviewApi(self): # Always caching
  #  from erogamescape.caching import CachingReviewTableApi
  #  return CachingReviewTableApi(rc.DIR_CACHE_SCAPE,
  #      expiretime=config.REF_EXPIRE_TIME,
  #      online=self.online)

class ScapeManager:

  def __init__(self):
    self.__d = _ScapeManager()

  def isOnline(self): return self.__d.online
  def setOnline(self, v): self.__d.online = v
    #d = self.__d
    #if d.online != v:
    #  d.online = v
    #  if hasmemoizedproperty(d, 'reviewApi'):
    #    d.reviewApi.online = v

  #@memoized # cached
  def queryReviews(self, id, async=True, **kwargs):
    """
    @param  id  int or str  ID
    @param* offset  int
    @param* limit  int
    @return  [kw]
    """
    if not self.__d.online:
      return []
    return skthreads.runsync(partial(
      self.__d.reviewApi.query, id, **kwargs),
    ) if async else self.__d.reviewApi.query(id, **kwargs)

  #def cache(self, id, async=True):
  #  """
  #  @param  id  int or str  ID
  #  """
  #  skthreads.runasync(partial(
  #    self.__d.api.cache, id),
  #  ) if async else self.__d.api.cache(id)

# Specific to Getchu

#class _GetchuManager(object):
#
#  def __init__(self):
#    self.online = True
#
#  @memoizedproperty
#  def api(self): # Always caching
#    from getchu.caching import CachingSoftApi
#    return CachingSoftApi(rc.DIR_CACHE_GETCHU,
#        expiretime=config.REF_EXPIRE_TIME,
#        online=self.online)
#
#class GetchuManager:
#
#  def __init__(self):
#    self.__d = _GetchuManager()
#
#  def isOnline(self): return self.__d.online
#  def setOnline(self, v):
#    d = self.__d
#    if d.online != v:
#      d.online = v
#      if hasmemoizedproperty(d, 'api'):
#        d.api.online = v
#
#  #@memoized # cached
#  def query(self, id, async=True):
#    """
#    @param  id  int or str  Getchu soft ID
#    @return  {kw}
#    """
#    return skthreads.runsync(partial(
#      self.__d.api.query, id),
#    ) if async else self.__d.api.query(id)

  #def cache(self, id, async=True):
  #  """
  #  @param  id  int or str  Getchu soft ID
  #  """
  #  skthreads.runasync(partial(
  #    self.__d.api.cache, id),
  #  ) if async else self.__d.api.cache(id)

## Getchu ##

#class GetchuApi(object):
#
#  def __init__(self, online=True):
#    """
#    @param* online  bool
#    """
#    self.online = online
#
#  def setOnline(self, v):
#    if self.online !=  v:
#      self.online = v
#      if hasmemoizedproperty(self, 'cachingApi'):
#        self.cachingApi.online = online
#
#  _rx_title = re.compile(_re_title)
#  @classmethod
#  def _beautifyTitle(cls, t):
#    """
#    @param  t  unicode
#    @return  unicode or None
#    """
#    if not t or re.search(ur'廉価版|通常版', t):
#      return
#    t = cls._rx_title.sub('', t).strip()
#    t = re.sub(ur'\($', '', t).strip()
#    return t
#
#  @property
#  def api(self):
#    from getchu import api
#    return api
#
#  def _search(self, text=None, key=None, cache=True):
#    """
#    @return  iter
#    """
#    dprint("key, text =", key, text)
#    #api = self.cachingApi if cache else self.api
#    return self.api.query(text, genre='pc_soft') if text else []
#
#  def cache(self, **kwargs):
#    dprint("ignored")
#
#  def query(self, **kwargs):
#    """
#    @return  iter not None
#    """
#    dprint("enter")
#    ret = []
#    try:
#      s = self._search(**kwargs)
#      for kw in s:
#        try:
#          if kw.get('media') != 'DVD-ROM':
#            continue
#
#          title = self._beautifyTitle(kw['title'])
#          if not title:
#            continue
#          kw['title'] = title
#
#          try:
#            d = datetime.strptime(kw['date'], '%Y/%m/%d')
#            kw['date'] = skdatetime.date2timestamp(d)
#          except: kw['date'] = 0
#
#          try: kw['price'] = int(kw['price'])
#          except: kw['price'] = 0
#
#          kw['url'] = 'http://getchu.com/soft.phtml?id=' + kw['key']
#
#        except KeyError: continue
#        ret.append(kw)
#
#    except Exception, e: dwarn(e)
#    dprint("leave: count = %s" % len(ret))
#    return ret

