# coding: utf8
# qtrequests.py
# 8/23/2014 jichi
# Python requests implemented using QtNetwork.

__all__ = 'Session', 'AsyncSession'

import json, urllib, zlib
from PySide.QtCore import QUrl, QTimer, QEventLoop, QCoreApplication
from PySide.QtNetwork import QNetworkRequest

#class EventLoop(QEventLoop):
#  def __init__(self, parent=None):
#    super(EventLoop, self).__init__(parent)
#  def __del__(self):
#    print "del: pass"

MIMETYPE_JSON = 'application/json'
MIMETYPE_FORM = 'application/x-www-form-urlencoded'

# Is this thread-safe?
_zlib_decomp = zlib.decompressobj(16 + zlib.MAX_WBITS) # The magic number is only for http
def _gunzip(data):
  """
  @param  data  str
  @return  data  str

  GZIP, see: http://rationalpie.wordpress.com/2010/06/02/python-streaming-gzip-decompression/
  """
  return _zlib_decomp.decompress(data)

class Response:
  encoding = 'utf8'

  def __init__(self, ok=True, content='', url=''):
    self.ok = ok # bool
    self.content = content # str
    self.url = url # unicode

  @property
  def text(self):
    if self.content and isinstance(self.content, str):
      return self.content.decode(self.encoding) # this might throw
    else:
      return self.content

class _Session:
  encoding = 'utf8'

  def __init__(self, nam, requestTimeout, abortSignal):
    self.nam = nam # QNetworkAccessManager
    self.requestTimeout = requestTimeout # int
    self.abortSignal = abortSignal # Signal or None

  def _waitReply(self, reply):
    """
    @param  reply  QNetworkReply
    @param* abortSignal  Signal
    """
    #loop = QEventLoop(self.nam) # prevent loop from being deleted by accident
    loop = QEventLoop()
    if self.abortSignal:
      self.abortSignal.connect(loop.quit)

    timer = None
    if self.requestTimeout:
      timer = QTimer()
      timer.setInterval(self.requestTimeout)
      timer.setSingleShot(True)
      timer.timeout.connect(loop.quit)

    qApp = QCoreApplication.instance()
    qApp.aboutToQuit.connect(loop.quit)

    reply.finished.connect(loop.quit)
    loop.exec_()

    if timer:
      timer.timeout.disconnect(loop.quit)
    if self.abortSignal:
      self.abortSignal.disconnect(loop.quit)
    qApp.aboutToQuit.disconnect(loop.quit)
    reply.finished.disconnect(loop.quit)

    #loop.setParent(None)

  def _createRequest(self, url, params=None, headers=None, verify=True):
    """
    @param  url  unicode
    @param* verify  whether check SSL, ignored
    @param* headers  {unicode key:unicode value}
    @param* params  {unicode key:unicode value}
    """
    if params:
      url = self._createUrl(url, params)
    r = QNetworkRequest(url)
    if headers:
      for k,v in headers.iteritems():
        r.setRawHeader(self._tostr(k), self._tostr(v))
    return r

  _createGetRequest = _createRequest

  def _createPostRequest(self, *args, **kwargs):
    r = self._createRequest(*args, **kwargs)
    headers = kwargs.get('headers')
    if not headers or 'Content-Type' not in headers:
      r.setRawHeader('Content-Type', MIMETYPE_FORM) # setRawHeader is faster than setHeader
    return r

  def _tostr(self, data):
    """
    @param  data  any
    @return  str not unicode not None
    """
    if isinstance(data, str):
      return data
    if isinstance(data, unicode):
      return data.encode(self.encoding, errors='ignore')
    return "%s" % data # might throw

  def _tounicode(self, data):
    """
    @param  data  any
    @return  str not unicode not None
    """
    if isinstance(data, str):
      return data
      #return data.decode(self.encoding, errors='ignore')
    if isinstance(data, unicode):
      return data
    if isinstance(data, bool):
      return 'true' if data else 'false' # use lower case
    return "%s" % data # might throw

  def _createUrl(self, url, params=None):
    """
    @param  url  unicode
    @param* params  {unicode key:unicode value}
    @return  QUrl
    """
    url = QUrl(url)
    if params:
      for k,v in params.iteritems():
        url.addQueryItem(self._tounicode(k), self._tounicode(v))
    return url

  def _encodePostFormData(self, data):
    """
    @param  data  {unicode key:unicode value}
    @return  str not unicode
    """
    data = {self._tostr(k):self._tostr(v) for k,v in data.iteritems()}
    return urllib.urlencode(data) # application/x-www-form-urlencoded

  def _encodePostJsonData(self, data):
    """
    @param  data  {unicode key:unicode value}
    @return  str not unicode
    """
    return json.dumps(data)

  def _createPostData(self, data, contentType=''):
    """
    @param  data  None str or unicode or kw
    @param  contentType  str
    @return  str
    """
    if data is None:
      return ''
    if isinstance(data, str):
      return data
    if isinstance(data, unicode):
      return self._tostr(data)
    if isinstance(data, dict):
      if contentType == MIMETYPE_JSON:
        return self._encodePostJsonData(data)
      else:
        return self._encodePostFormData(data) # application/x-www-form-urlencoded
    return "%s" % data # may throw for unknown data format

  def _readReply(self, reply):
    """
    @param  reply  QNetworkReply
    @return  str

    GZIP, see: http://rationalpie.wordpress.com/2010/06/02/python-streaming-gzip-decompression/
    """
    ret = reply.readAll().data()
    enc = reply.rawHeader('Content-Encoding').data() # QByteArray to str
    if enc and 'gzip' in enc:
      try: ret = _gunzip(ret)
      except: pass # ignore gunzip error
    return ret

  def get(self, *args, **kwargs):
    """
    @param  url  unicode
    @return  str or None
    """
    ret = None
    reply = self.nam.get(self._createGetRequest(*args, **kwargs))
    self._waitReply(reply)
    if reply.isRunning():
      reply.abort() # return None
    else:
      ret = self._readReply(reply)
    reply.deleteLater()
    return ret

  def post(self, url, data=None, **kwargs):
    """
    @param  url  unicode
    @param* data  any
    @return  str or None
    """
    ret = None
    req = self._createPostRequest(url, **kwargs)
    contentType = req.rawHeader('Content-Type')
    data = self._createPostData(data, contentType=contentType)
    reply = self.nam.post(req, data)
    self._waitReply(reply)
    if reply.isRunning():
      reply.abort()
    else:
      ret = self._readReply(reply)
    reply.deleteLater()
    return ret

class Session(object):

  def __init__(self, nam, requestTimeout=0, abortSignal=None):
    """
    @param  nam  QNetworkAccessManager
    @param* requestTimeout  int
    @param* abortSignal  Signal
    """
    self.__d = _Session(nam, requestTimeout, abortSignal) # Network access manager

  # Properties

  def requestTimeout(self): return self.__d.timeout
  def setTequestTimeout(self, v): self.__d.timeout = v # int

  def networkAccessManager(self):
    """
    @return  QNetworkAccessManager
    """
    return self.__d.nam

  def setNetworkAccessManager(self, v):
    """
    @param  QNetworkAccessManager
    """
    self.__d.nam = v

  def abortSignal(self):
    """
    @return  Signal
    """
    return self.__d.abortSignal

  def setAbortSignal(self, v):
    """
    @param  Signal
    """
    self.__d.abortSignal = v

  # Queries

  def get(self, url, *args, **kwargs):
    """Similar to requests.get.
    @param  url  unicode
    @param* headers  {unicode key:unicode value}
    @param* params  {unicode key:unicode value}
    @return  Response not None
    """
    data = self.__d.get(url, *args, **kwargs)
    ok = data is not None
    content = data or ''
    return Response(ok=ok, content=content, url=url)

  def post(self, url, *args, **kwargs):
    """Similar to requests.post.
    @param  url  unicode
    @param  data  None or str or unicode or kw
    @param* headers  {unicode key:unicode value}
    @param* params  {unicode key:unicode value}
    @return  Response not None
    """
    data = self.__d.post(url, *args, **kwargs)
    ok = data is not None
    content = data or ''
    return Response(ok=ok, content=content, url=url)

from functools import partial
from sakurakit import skthreads
class AsyncSession(object):
  def __init__(self, session):
    self.session = session

  def get(self, *args, **kwargs):
    return skthreads.runsync(partial(self.session.get, *args, **kwargs))

  def post(self, *args, **kwargs):
    return skthreads.runsync(partial(self.session.post, *args, **kwargs))

if __name__ == '__main__':
  import sys
  sys.path.append('..')

  def test():
    print "start"
    from PySide.QtNetwork import QNetworkAccessManager
    nam = QNetworkAccessManager()

    #import requests
    #s = requests
    #s = requests.Session()

    s = Session(nam)

    from sakurakit.skprof import SkProfiler
    #url = "http://www.google.com"
    url = "http://localhost:8080/json/post/create"
    data = {'lang':'ja'}
    headers = {'Content-Type':'application/json'}
    with SkProfiler():
      r = s.post(url, data=json.dumps(data), headers=headers)
      print r.ok
      print r.content

    print "quit"
    app.quit()

  from PySide.QtCore import QTimer
  app = QCoreApplication(sys.argv)
  QTimer.singleShot(0, test)
  app.exec_()

# EOF
