# coding: utf8
# cacheman.py
# 7/4/2012 jichi

__all__ = 'CacheJinjaUtil', 'CacheCoffeeBean'

import os, re
from functools import partial
from PySide.QtCore import QObject, QTimer, Slot
from sakurakit import skfileio, sknetio, skstr, skthreads
from sakurakit.skclass import memoized
from sakurakit.skdebug import dprint, dwarn
import osutil, rc

TMP_SUFFIX = '.tmp'
BAD_SUFFIX = '.bad'

IMAGE_SUFFICES = frozenset(('.jpg', '.jpeg', '.png', '.gif'))

#def _avatarurl(token, size=128):
def _avatarurl(token): # string -> string
  """
  @param  token  unicode
  @return  unicode
  """
  return "http://media.getchute.com/media/%s" % token
  #return "http://media.getchute.com/media/%s/128x128" % token
  #return "http://avatars.io/%s?size=large" % token

avatarurl = _avatarurl

def _getavatar(token):
  """
  @param  token  unicode
  @return  image data or None
  """
  url = _avatarurl(token)
  data = sknetio.getdata(url, mimefilter=sknetio.IMAGE_MIME_FILTER)
  # len 4071 is the bad avatar ><
  if data and len(data) != 4071:
    return data

def _saveavatar(token, path):
  """
  @param  token  unicode
  @param  path  unicode
  @return  bool
  """
  data = _getavatar(token)
  return bool(data) and skfileio.writedata(path, data)

def _fixtwimg(url):
  """
  @param  url  str
  @return  str or None
  """
  if '_normal.' not in url and ('.twimg.com' in url or '/twimg/' in url):
    i = url.rfind('.') # insert '_normal' before the last '.;
    if i > 0:
      return '_normal'.join((url[:i], url[i:]))

def _getdata(url, path, tmppath=None, touchbad=False, mimefilter=None, **kwargs):
  """
  @param  token  unicode
  @param  path  unicode
  @param* tmppath  unicode
  @param* touchbad  bool
  @param* mimefilter  str
  @return  bool
  """
  if not tmppath:
    tmppath = path + TMP_SUFFIX
  data = sknetio.getdata(url, mimefilter=mimefilter, **kwargs)
  if not data:
    url = _fixtwimg(url)
    if url:
      return _getdata(url, path, tmppath=tmppath, mimefilter=mimefilter, **kwargs)
  ok = bool(data) and skfileio.writedata(tmppath, data)
  if ok and skfileio.rename(tmppath, path):
    return True
  else:
    skfileio.removefile(tmppath)
    if touchbad:
      badpath = path + BAD_SUFFIX
      skfileio.touchfile(badpath)
    return False

#@Q_Q
class _CacheManager:
  def __init__(self):
    self.enabled = False # bool
    self._tasks = [] # [function] not None

    #@memoizedproperty
    #def taskTimer
    t = self.taskTimer = QTimer()
    t.setSingleShot(True)
    t.timeout.connect(self._doTasks)
    t.setInterval(500)

  def _doTasks(self):
    t = self._tasks
    if t:
      self._tasks = []
      sz = len(t)
      if sz < 5:
        skthreads.runasync(partial(map, apply, t))
      elif sz < 15:
        chunk = sz / 2
        skthreads.runasync(partial(map, apply, t[:chunk]))
        skthreads.runasync(partial(map, apply, t[chunk:]))
      else:
        chunk = sz / 3
        skthreads.runasync(partial(map, apply, t[:chunk]))
        skthreads.runasync(partial(map, apply, t[chunk:chunk*2]))
        skthreads.runasync(partial(map, apply, t[chunk*2:]))

  def schedule(self, func):
    """
    @param  func  function
    """
    self._tasks.append(func)
    self.taskTimer.start()

class CacheManager:
  def __init__(self):
    self.__d = _CacheManager()

  @staticmethod
  def clearTemporaryFiles():
    from sakurakit import skfileio
    for tmpdir in rc.DIR_CACHE_AVATAR, rc.DIR_CACHE_DATA, rc.DIR_CACHE_IMAGE:
      try:
        for root, dirs, files in os.walk(tmpdir):
          for f in files:
            if f.endswith(TMP_SUFFIX):
              p = os.path.join(root, f)
              skfileio.removefile(p)
      except Exception, e: dwarn(e)
    dprint("pass")

  def isEnabled(self): return self.__d.enabled
  def setEnabled(self, v): self.__d.enabled = v

  def updateAvatar(self, token):
    """
    @param  token  unicode
    @return  bool  whether succeeded
    """
    path = rc.avatar_image_path(token)
    if os.path.exists(path):
      return True
    if not self.__d.enabled:
      return False
    path_tmp = path + TMP_SUFFIX
    if os.path.exists(path_tmp):
      return False
    skfileio.touchfile(path_tmp)
    ok = skthreads.runsync(partial(
        _saveavatar, token, path_tmp))
    if ok and skfileio.rename(path_tmp, path):
      return True
    else:
      skfileio.removefile(path_tmp)
      return False

  def cacheAvatar(self, token):
    """
    @param  token  unicode
    """
    path = rc.avatar_image_path(token)
    if os.path.exists(path):
      return
    d = self.__d
    if not d.enabled:
      return
    path_tmp = path + TMP_SUFFIX
    if os.path.exists(path_tmp):
      return
    skfileio.touchfile(path_tmp)
    url = _avatarurl(token)
    d.schedule(partial(
        _getdata, url, path, path_tmp, mimefilter=sknetio.IMAGE_MIME_FILTER))

  def cachePath(self, url, image=False):
    """
    @param  url  unicode
    @param* img  bool
    @return  unicode  path to local file
    """
    return rc.image_cache_path(url) if image else rc.data_cache_path(url)

  def cacheUrl(self, url, image=False, mimefilter=None):
    """
    @param  url  unicode
    @param* image  bool
    @param* mimefilter
    @return  unicode  url to remote or local file
    """
    if not url.startswith('http'): # ignore local files
      return url
    path = self.cachePath(url, image=image)
    if os.path.exists(path):
      #dprint("cache HIT")
      return osutil.path_url(path)

    # Example dmm image: http://pics.dmm.co.jp/digital/game/d_057589/d_057589pt.jpg
    bad = image and (
        url.startswith("http://pics.dmm.co.jp/")  or
        url.startswith("http://media.erogetrailers.com/img/") or
        url.endswith("/maxresdefault.jpg"))
    if bad and os.path.exists(path + BAD_SUFFIX):
      #dwarn("cache BAD")
      return ''

    d = self.__d
    if not d.enabled:
      return url
    path_tmp = path + TMP_SUFFIX
    if os.path.exists(path_tmp):
      return url

    dprint("cache MISS: %s" % url)
    skfileio.touchfile(path_tmp)
    d.schedule(partial(
        _getdata, url, path, path_tmp,
        mimefilter=mimefilter,
        touchbad=bad, allow_redirects=not bad))
    return url

  def cacheImageUrl(self, url):
    """
    @param  url  unicode
    @return  unicode  url to remote or local file
    """
    return self.cacheUrl(url, image=True, mimefilter=sknetio.IMAGE_MIME_FILTER)

  def cacheImagePath(self, url):
    return self.cachePath(url, image=True)

  def cacheHtmlText(self, html):
    """
    @param  html  unicode
    @return  unicode
    """
    ret = skstr.replaceimgurls(skstr.replacelinks(
        html, self._cacheHtmlImageUrl), self._cacheHtmlImageUrl)
    return ret

  def _cacheHtmlImageUrl(self, url):
    """
    @param  url  str
    @return  str  url
    """
    return self.cacheImageUrl(url) if url.startswith('http') and self.isImageUrl(url) else url


  def cacheAnyUrl(self, url):
    """
    @param  url  str
    @return  str  url
    """
    return self.cacheImageUrl(url) if self.isImageUrl(url) else self.cacheUrl(url)

  def isImageUrl(self, url):
    """
    @param  url  str
    @return  bool
    """
    i = url.rfind('.')
    if i != -1:
      suf = url[i:].lower()
      return suf in IMAGE_SUFFICES
    return False

@memoized
def manager(): return CacheManager()

def cache_any_url(url): return manager().cacheAnyUrl(url) # cache url
def cache_url(url): return manager().cacheUrl(url) # cache url
def cache_path(url): return manager().cachePath(url) # return cached path for url without caching it
def cache_image_url(url): return manager().cacheImageUrl(url)
def cache_image_path(url): return manager().cacheImagePath(url)

def cache_html(text): return manager().cacheHtmlText(text)

class CacheJinjaUtil:
  @staticmethod
  def url(url): return cache_url(url)
  @staticmethod
  def image(url): return cache_image_url(url)
  @staticmethod
  def html(text): return cache_html(text)

class CacheCoffeeBean(QObject):

  def __init__(self, parent=None):
    super(CacheCoffeeBean, self).__init__(parent)

  @Slot(unicode, result=unicode)
  def cacheUrl(self, url): return cache_url(url)
  @Slot(unicode, result=unicode)
  def cacheImage(self, url): return cache_image_url(url)

# EOF
