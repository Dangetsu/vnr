# coding: utf8
# offline.py
# 11/16/2013 jichi

__all__ = (
  'CacherPrototype',
  'CacherBase',
  'DataCacher',
  'FileCacher',
)

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import os
from time import time
from hashlib import md5 # pylint: disable-msg=E0611
from sakurakit.skdebug import dprint, dwarn

#DEFAULT_CACHE_DIR = tempfile.mkdtemp(prefix='dmm_')

class CacherPrototype(object):
  """An example of base restful class"""
  def _fetch(self, *args, **kwargs):
    """
    @return  Either file object or data
    """
    pass
  def _makereq(self, *args, **kwargs):
    """
    @return  kw  request parameter to fetch
    """
    return {}

class CacherBase(object):

  def __init__(self, cachedir=None, caching=True, expiretime=0, online=True, *args, **kwargs):
    """
    @param  cachedir  str
    @param* expiretime  int
    @param* online  bool
    """
    self.online = online # bool
    self.caching = caching # bool
    self.cachedir = cachedir # unicode
    self.expiretime = expiretime # int, interval in seconds
    #try:
    #  if cachedir and not os.path.exists(cachedir):
    #    #os.mkdir(cachedir)
    #    dprint("mkdirs: %s" % cachedir)
    #    os.makedirs(cachedir)
    #except IOError, e:
    #  dwarn(e)
    #  self.cachedir = None

  ## API ##

  def cache(self, *args, **kwargs):
    req = self._makereq(*args, **kwargs)
    self._fetch(**req)

  ## Utilities ##

  def _digest(self, expire, *args, **kwargs):
    """
    @param  expire  bool
    @return  str
    Calculate hash value for request based on URL.
    """
    url = ''
    if args:
      url += '&'.join('%s' % it for it in args)
    if kwargs:
      url += '&'.join("%s=%s" % it for it in sorted(kwargs.iteritems()))
    if expire and self.expiretime:
      now = int(time())
      url += '&__expire=' + str(now/self.expiretime)
    return md5(url).hexdigest()

  @staticmethod
  def _writecache(data, path):
    """
    @param  data  str
    @param  path  unicode
    """
    try: open(path, 'w+').write(data) # write and update
    except IOError, e: dwarn(e)

  @staticmethod
  def _readcache(path):
    """
    @param  path  unicode
    @return  str
    """
    if os.path.isfile(path):
      #dprint('cache HIT')
      try: return open(path).read()
      except IOError, e: dwarn(e)

  @staticmethod
  def _opencache(path):
    """
    @param  path  unicode
    @return  fp or None
    """
    if os.path.isfile(path):
      #dprint('cache HIT')
      try: return open(path)
      except IOError, e: dwarn(e)

def DataCacher(Prototype, Base=CacherBase, suffix=''):
  """
  @param  Prototype  CacherPrototype
  @param* Base  CacherBase
  @param* suffix  str
  """
  class Cacher(Prototype, Base):
    def __init__(self,
        cachedir=None, expiretime=0, online=True, caching=True,
        *args, **kwargs):
      """
      @param  cachedir  str
      @param* expiretime  int
      @param* caching  bool
      @param* online  bool
      """
      super(Cacher, self).__init__(*args, **kwargs)
      Base.__init__(self,
          cachedir=cachedir,
          expiretime=expiretime,
          online=online,
          caching=caching)
    def _fetch(self, *args, **kwargs):
      """@reimp
      @return  str
      """
      caching = self.cachedir and self.caching
      if caching:
        if self.expiretime:
          expirepath = os.path.join(self.cachedir,
            self._digest(True, *args, **kwargs) + suffix)
          data = self._readcache(expirepath)
          if data:
            return data
        path = os.path.join(self.cachedir,
            self._digest(False, *args, **kwargs) + suffix)
        if not self.expiretime:
          data = self._readcache(path)
          if data:
            return data
      dprint('cache MISS')
      # fetch original response from Amazon
      data = super(Cacher, self)._fetch(*args, **kwargs) if self.online else None
      if caching:
        if data:
          if self.expiretime:
            self._writecache(data, expirepath)
          self._writecache(data, path)
        else:
          if self.expiretime:
            data = self._readcache(path)
      return data

  return Cacher

def FileCacher(Prototype, Base=CacherBase, suffix=''):
  """
  @param  Prototype  CacherPrototype
  @param* Base  CacherBase
  @param* suffix  str
  """
  class Cacher(Prototype, Base):
    def __init__(self,
        cachedir=None, expiretime=0, online=True, caching=True,
        *args, **kwargs):
      """
      @param  cachedir  str
      @param* expiretime  int
      @param* caching  bool
      @param* online  bool
      """
      super(Cacher, self).__init__(*args, **kwargs)
      Base.__init__(self,
          cachedir=cachedir,
          expiretime=expiretime,
          online=online,
          caching=caching)
    def _fetch(self, *args, **kwargs):
      """@reimp
      @return  file object
      """
      caching = self.cachedir and self.caching
      if caching:
        if self.expiretime:
          expirepath = os.path.join(self.cachedir,
              self._digest(True, *args, **kwargs) + suffix)
          fp = self._opencache(expirepath)
          if fp:
            return fp
        path = os.path.join(self.cachedir,
            self._digest(False, *args, **kwargs) + suffix)
        if not self.expiretime:
          fp = self._opencache(path)
          if fp:
            return fp
      dprint('cache MISS')
      # fetch original response from Amazon
      resp = super(Cacher, self)._fetch(*args, **kwargs) if self.online else None
      if not caching:
        return resp
      else:
        data = resp.read() if resp else None
        if data:
          if self.expiretime:
            self._writecache(data, expirepath)
          try:
            fp = open(path, 'w+') # write and update
            #fp.write(etree.tostring(etree.parse(resp), pretty_print=True))
            fp.write(data)
            fp.seek(0)
            return fp
          except IOError, e: dwarn(e)
        else:
          if self.expiretime:
            fp = self._opencache(path)
            if fp:
              return fp

  return Cacher

if __name__ == '__main__':

  from online import DataParser

  cls = DataCacher(DataParser, suffix='.html')
  cachedir = 'tmp'
  api = cls(cachedir=cachedir, expiretime=0)

  #url = 'http://ja.wikipedia.org/wiki/'
  url = 'http://www.amazon.co.jp/reviews/iframe?akid=AKIAJSUDXZVM3TXLJXPQ&alinkCode=xm2&asin=B00AT6K7OE&atag=sakuradite-20&exp=2014-07-05T22%3A25%3A10Z&v=2&sig=gELwW4RmIrkrZ9ImIsItypJGeirqOFHRuwQU2EtZRMw%3D'
  data = api.query(url)
  print data

# EOF
