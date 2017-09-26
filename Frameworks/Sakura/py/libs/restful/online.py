# coding: utf8
# online.py
# 8/12/2013 jichi
#
# See: http://ymotongpoo.hatenablog.com/entry/20081123/1227430671

__all__ = 'DataParser', 'FileParser', 'JsonFileParser'

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import json, urllib2
from sakurakit import sknetio
from sakurakit.skdebug import dwarn

class ParserBase(object):
  ENCODING = 'utf8'

class DataParser(ParserBase):

  session = None # requests.Session or None

  def _makereq(self, *args, **kwargs):
    """
    @param  kw
    @return  kw
    """
    return {'url':self._makeurl(*args, **kwargs)}

  def _makeurl(self, *args, **kwargs):
    """
    @return  str
    """
    if args:
      return args[0]
    if kwargs:
      return kwargs.itervalues().next()

  def _fetch(self, url):
    """
    @param  url  str
    @return  str
    """
    return sknetio.getdata(url, gzip=True, session=self.session)

  def query(self, *args, **kwargs):
    """
    @return  {kw} or None
    """
    req = self._makereq(*args, **kwargs)
    h = self._fetch(**req)
    if h:
      h = h.decode(self.ENCODING, errors='ignore')
      if h:
        return self._parse(h)

  def _parse(self, h):
    """
    @param  h  unicode  html
    @return  {kw}
    """
    return h

# API is stateless
# Make this class so that _fetch could be overridden
class FileParser(ParserBase):

  #METHOD = 'GET'
  URL = '' # str

  def query(self, *args, **kwargs):
    """
    @param  text  unicode
    @param  type  str
    @return  list or None
    """
    try: return self._dispatch(*args, **kwargs)
    except Exception, e: dwarn(e)

  def _parse(self, fp):
    """
    @param  fp  file pointer
    @return  string
    @raise
    """
    return fp.read()

  def _makeparams(self, **kwargs):
    """
    @param  kw
    @return  kw
    """
    return kwargs

  def _dispatch(self, *args, **kwargs):
    """
    @return  list or None
    @raise
    """
    params = self._makeparams(*args, **kwargs)
    req = self._makereq(**params)
    r = self._fetch(**req)
    return self._parse(r)

  def _fetch(self, url):
    """
    @param  url  str
    @return  file object
    @raise
    """
    req = urllib2.Request(url)
    #handler = urllib2.HTTPHandler(debuglevel=self.debug)
    handler = urllib2.HTTPHandler()
    opener = urllib2.build_opener(handler)
    return opener.open(req)

  def _makereq(self, **kw):
    """
    @param  kw
    @return  kw
    """
    return {'url':self._makeurl(**kw)}

  def _makeurl(self, **params):
    """
    @param  params  request params
    @return  str

    See: http://ymotongpoo.hatenablog.com/entry/20081123/1227430671
    See: http://ketsuage.seesaa.net/article/263754550.html
    """
    # paramsのハッシュを展開
    request = ["%s=%s" % (k, urllib2.quote(self._encodeparam(v)))
        for k,v in sorted(params.iteritems())]

    #urllib.encodeparams

    # GET
    ret = self.URL + "?" + "&".join(request)
    #if self.debug:
    #  dprint(ret)
    return ret

  def _encodeparam(self, v):
    """
    @param  v  any
    @return  str
    """
    if isinstance(v, str):
      return v
    elif isinstance(v, unicode):
      return v.encode(self.ENCODING, errors='ignore')
    elif v is None:
      return ''
    elif v is bool:
      return 'true' if v else 'false'
    else:
      return str(v) # May throw

class JsonFileParser(FileParser):

  def _parse(self, fp):
    """@reimp
    @param  fp  file pointer
    @return  string
    @raise
    """
    return self._parsejson(json.load(fp))

  def _parsejson(self, data):
    """
    @param  data  object
    @return  object
    @raise
    """
    return data

# EOF
