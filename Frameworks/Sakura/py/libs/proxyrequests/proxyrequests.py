# coding: utf8
# proxyrequests.py
# 1/2/2015 jichi
# See: https://groups.google.com/forum/#!forum/pxuu

__all__ = 'Session'

import requests

class Session(object):
  def __init__(self, config, session=None,
      allows_session=True, allows_caching=False):
    """
    @param  config  {'host': str, 'postkey': str, 'referer': str}
    @param* session  requests.Session
    @param* allows_caching  bool
    @param* allows_session  bool
    """
    self.config = config
    self.session = session or requests.Session()
    self.allows_session = allows_session
    self.allows_caching = allows_caching
    self._proxyUrlCache = {}

  def _getsession(self):
    """
    @return  requests.Session
    """
    return self.session if self.allows_session else requests.Session()

  def _proxyurl(self, url, session=None):
    """
    @param  url  str
    @param* session  requests.Session
    @return  str or None
    """
    if self.allows_caching:
      ret = self._proxyUrlCache.get(url)
      if ret:
        return ret
    host = self.config['host']
    data = {self.config['postkey']: url}
    headers = {'Referer': self.config.get('referer') or self.config['host']}
    if not session:
      session or self.session
    r = session.post(host, data=data, headers=headers, allow_redirects=False)
    ret = r.headers.get('location')
    if self.allows_caching and ret:
      self._proxyUrlCache[url] = ret
    return ret

  def get(self, url, *args, **kwargs):
    session = self._getsession()
    url = self._proxyurl(url, session)
    if not url:
      return requests.Response()

    #print url
    referer = self.config.get('referer') or self.config['host']
    headers = kwargs.get('headers')
    if not headers:
      kwargs['headers'] = {'Referer':referer}
    else:
      headers = kwargs['headers'] = dict(headers)
      headers['Referer'] = referer
    return session.get(url, *args, **kwargs)

  def post(self, url, *args, **kwargs):
    session = self._getsession()
    url = self._proxyurl(url, session)
    if not url:
      return requests.Response()
    #print url
    headers = kwargs.get('headers') or {}
    headers['referer'] = self.config.get('referer') or self.config['host']
    return session.post(url, *args, **kwargs)

if __name__ == '__main__':
  import sys
  sys.path.append('..')
  from sakurakit.skprof import SkProfiler

  import proxyconfig
  url = "http://erogamescape.dyndns.org/~ap2/ero/toukei_kaiseki/select.php"
  #config = proxyconfig.USWEBPROXY_CONFIG
  #config['host'] = 'http://153.121.52.138/proxy/uswebproxy'
  config = proxyconfig.WEBSERVER_CONFIG
  s = Session(config)
  with SkProfiler():
    for i in range(10):
      r = s.get(url)
  #print r.content

# EOF
