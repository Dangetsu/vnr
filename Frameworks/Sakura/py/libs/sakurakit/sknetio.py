# coding: utf8
# sknetio.py
# 7/4/2013 jichi
import os, re, urllib
import requests
from skdebug import dwarn, derror
import skcontainer, skfileio
from sknetdef import *

IMAGE_MIME_FILTER = r'^image/'

## Parsing URL ##

def basename(url):
  """
  @param  url  unicode
  @return  unicode
  Example: "www.google.com/search?q=abc" will return "search?q=abc"
  """
  return url.rsplit('/', 1)[-1]

def reqname(url):
  """
  @param  url  unicode
  @return  unicode
  Example: "www.google.com/search?q=abc" will return "search"
  """
  return basename(url).split('?', 1)[0]

def urleq(x, y):
  """
  @param  x  str url
  @param  y  str  url
  @return  bool
  """
  if x == y:
    return True
  if not x or not y:
    return False
  return x.lower().replace('http://www.', 'http://') == y.lower().replace('http://www.', 'http://')

def urlne(x, y):
  """
  @param  x  str url
  @param  y  str  url
  @return  bool
  """
  return not urleq(x, y)

def topercentencoding(text, encoding='utf8', safe='', errors='ignore'):
  """
  @param  text  unicode or str
  @param* encoding  str or None
  @param* safe  str
  @return  unicode
  """
  if encoding and isinstance(text, unicode):
    text = text.encode(encoding, errors=errors)
  return urllib.quote(text, safe=safe) if text else ''

def frompercentencoding(text, encoding=None):
  """
  @param  text  unicode or str
  @param* encoding  str or None
  @return  unicode
  """
  text = urllib.unquote(text)
  if encoding:
    text = text.decode(encoding, errors='ignore')
  return text

## Get and post ##

def _mimematch(r, pattern):
  """
  @param  r request
  @param  pattern  str
  @return  None or not None
  """
  try: return re.search(pattern, r.headers['Content-Type'], re.IGNORECASE)
  except: pass

def postdata(url, headers=None, gzip=True, useragent=False, mimefilter=None, session=None, verify=False, **kwargs):
  """
  @param  url  str
  @param* headers  kw
  @param* gzip  bool
  @param* useragent  bool
  @param* path  str
  @param* mode  str  'w' or 'wb'
  @param* verify  bool  disable SSH certificate verification by default
  @param  session  requests.Session
  @return  data or None
  """
  try:
    if gzip:
      headers = skcontainer.mergedicts(headers,  GZIP_HEADERS) if headers else GZIP_HEADERS
    if useragent:
      headers = skcontainer.mergedicts(headers,  USERAGENT_HEADERS) if headers else USERAGENT_HEADERS
    r = (session or requests).post(url, headers=headers, verify=verify, **kwargs)
    if r.ok and (not mimefilter or _mimematch(r, mimefilter)):
      return r.content
  except Exception, e: derror(e)
  dwarn("failed URL: %s" % url)

  #except socket.error, e:
  #  dwarn("socket error", e.args)
  #except requests.ConnectionError, e:
  #  dwarn("connection error", e.args)
  #except requests.HTTPError, e:
  #  dwarn("http error", e.args)

  #try: dwarn(r.url)
  #except: pass

def _getres(url, headers=None, gzip=True, useragent=False, mimefilter=None, session=None, verify=False, **kwargs):
  """
  @param  url  str
  @param* headers  kw
  @param* gzip  bool
  @param* useragent  bool
  @param* path  str
  @param* mode  str  'w' or 'wb'
  @param* verify  bool  disable SSH certificate verification by default
  @param* session  requests.Session
  @return  response or None
  @raise
  """
  if gzip:
    headers = skcontainer.mergedicts(headers,  GZIP_HEADERS) if headers else GZIP_HEADERS
  if useragent:
    headers = skcontainer.mergedicts(headers,  USERAGENT_HEADERS) if headers else USERAGENT_HEADERS
  r = (session or requests).get(url, headers=headers, verify=verify, **kwargs)
  if r.ok and (not mimefilter or _mimematch(r, mimefilter)):
    return r

def getdata(url, **kwargs):
  """
  @param  url  str
  @return  str data or None
  """
  try:
    res = _getres(url, **kwargs)
    if res:
      return res.content
  except Exception, e: derror(e)
  dwarn("failed URL: %s" % url)

  #except socket.error, e:
  #  dwarn("socket error", e.args)
  #except requests.ConnectionError, e:
  #  dwarn("connection error", e.args)
  #except requests.HTTPError, e:
  #  dwarn("http error", e.args)

  #try: dwarn(r.url)
  #except: pass

# Stream with requests: http://stackoverflow.com/questions/16694907/how-to-download-large-file-in-python-with-requests-py
def itergetdata(url, chunksize=1024, **kwargs):
  """
  @param  url  str
  @param  path  str
  @param  mode  str  'w' or 'wb'
  @return  iter(str) or None
  """
  try:
    res = _getres(url, stream=True, **kwargs)
    if res:
      return res.iter_content(chunk_size=chunksize)
  except Exception, e: derror(e)
  dwarn("failed URL: %s" % url)

def getfile(url, path, mode='wb', stream=True, flush=True, **kwargs):
  """
  @param  url  str
  @param  path  str
  @param  stream  bool
  @param  flush  bool
  @param  mode  str  'w' or 'wb'
  @return  bool
  """
  if stream:
    it = itergetdata(url, **kwargs)
    return bool(it) and skfileio.iterwritefile(path, it, mode=mode, flush=flush)
  else:
    d = getdata(url, **kwargs)
    return bool(d) and skfileio.writefile(path, d, mode=mode)

if __name__ == '__main__':
  d = getdata("http://avatars.io/AQKI6jsmz?size=large", mimefilter="^image/")
  print "ok", len(d)
  d = getdata("http://avatars.io/what?size=large", mimefilter="^image/")
  print "failed", len(d)


  d = getdata("http://gyutto.com/i/item2537", allow_redirects=False)
  print "noredirect", len(d)

  d = getdata("http://gyutto.com/i/item115299", allow_redirects=False)
  print "noredirect", len(d)

  print getfile('http://www.google.com', 'hello.tmp')

# EOF
