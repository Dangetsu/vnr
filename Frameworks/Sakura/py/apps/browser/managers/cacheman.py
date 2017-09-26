# coding: utf8
# cacheman.py
# 7/4/2012 jichi

import os
from functools import partial
from PySide.QtCore import QTimer
from sakurakit import skfileio, sknetio, skthreads
from sakurakit.skclass import memoized
from sakurakit.skdebug import dprint, dwarn
import osutil, rc

TMP_SUFFIX = '.tmp'
BAD_SUFFIX = '.bad'

@memoized
def manager(): return CacheManager()

def cache_url(url): return manager().cacheUrl(url) # cache url
#url = cache_url

cache_image = cache_url # temporarily not distinguished

class CacheApi:
  @staticmethod
  def url(url): return cache_url(url)
  @staticmethod
  def image(url): return cache_image(url)

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
  #if not data:
  #  url = _fixtwimg(url)
  #  if url:
  #    return _getdata(url, path, tmppath=tmppath, mimefilter=mimefilter, **kwargs)
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
    self.enabled = True
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
    for tmpdir in rc.DIR_CACHE_DATA,:
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

  def cacheUrl(self, url, image=False, mimefilter=None):
    """
    @param  url  unicode
    @param* image  bool
    @param* mimefilter
    @return  unicode  url to remote or local file
    """
    if not url.startswith('http'): # ignore local files
      return url

    path = rc.data_cache_path(url)
    if os.path.exists(path):
      #dprint("cache HIT")
      return osutil.path_url(path)

    # Example dmm image: http://pics.dmm.co.jp/digital/game/d_057589/d_057589pt.jpg
    bad = image and (
        url.startswith("http://pics.dmm.co.jp/")  or
        url.startswith("http://media.erogetrailers.com/img/"))
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

# EOF
