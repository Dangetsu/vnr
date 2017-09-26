# coding: utf8
# network.py
# 12/13/2012 jichi

__all__ = 'WbNetworkAccessManager',

import os
from PySide.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkDiskCache
from sakurakit import skfileio, sknetwork
from sakurakit.skdebug import dprint
import proxy, rc

## Cookie ##

class WbNetworkCookieJar(sknetwork.SkNetworkCookieJar):
  def __init__(self, path, parent=None): # unicode
    super(WbNetworkCookieJar, self).__init__(parent)
    self.path = path
    self.load()
    self._injectCookies()

    # Automatically save cookies using timer
    from PySide.QtCore import QCoreApplication
    qApp = QCoreApplication.instance()
    qApp.aboutToQuit.connect(self.save)

  # Persistent storage

  def load(self): # unicode ->
    path = self.path
    if path and os.path.exists(path):
      self.unmarshal(skfileio.readdata(path))

  def save(self): # unicode -> bool
    return bool(self.path) and skfileio.writedata(self.path, self.marshal())

  def _injectCookies(self):
    #from PySide.QtCore import QUrl
    from PySide.QtNetwork import QNetworkCookie
    import cookies

    # Use parent cookie
    setCookiesFromUrl = super(WbNetworkCookieJar, self).setCookiesFromUrl

    for kvdict,urls in cookies.itercookies():
      cookies = [QNetworkCookie(k,v) for k,v in kvdict.iteritems()]
      for url in urls:
        l = cookies
        if url.startswith("http://www."):
          domain = url.replace("http://www", '') # such as .dmm.co.jp
          l = [QNetworkCookie(it) for it in l] # copy l
          for c in l:
            c.setDomain(domain)
        self.setCookiesFromOriginalUrl(l, url)

    # See: http://kancolle.wikia.com/wiki/Tutorial:_Proxy_Connection
    #c = QNetworkCookie('ckcy', '1')
    #c.setDomain("http://www.dmm.com")
    #c.setPath("/netgame")
    #self.setCookiesFromUrl([c], "http://www.dmm.com/netgame")
    #c.setPath("/netgame_s")
    #self.setCookiesFromUrl([c], "http://www.dmm.com/netgame_s")

  # Proxy

  def cookiesForUrl(self, url): # override
    """@reimp"""
    url = proxy.fromproxyurl(url) or url
    return super(WbNetworkCookieJar, self).cookiesForUrl(url)

  def setCookiesFromUrl(self, cookies, url):
    """@reimp"""
    url = proxy.fromproxyurl(url) or url
    return super(WbNetworkCookieJar, self).setCookiesFromUrl(cookies, url)

  # Expose API to set cookies without proxy
  def setCookiesFromOriginalUrl(self, cookies, url):
    return super(WbNetworkCookieJar, self).setCookiesFromUrl(cookies, url)

## Network ##

REQ_PROXY_URL = 'proxy'

class WbNetworkAccessManager(QNetworkAccessManager):
  def __init__(self, parent=None):
    super(WbNetworkAccessManager, self).__init__(parent)
    self.sslErrors.connect(_WbNetworkAccessManager.onSslErrors)
    self.finished.connect(_WbNetworkAccessManager.onReplyFinished)

    # Enable offline cache
    cache = QNetworkDiskCache(self)
    cache.setCacheDirectory(rc.DIR_CACHE_NETMAN) # QNetworkDiskCache will create this directory if it does not exists.
    self.setCache(cache)

    # Load cookies
    jar = WbNetworkCookieJar(rc.COOKIES_LOCATION)
    self.setCookieJar(jar)

  # QNetworkReply *createRequest(Operation op, const QNetworkRequest &req, QIODevice *outgoingData = nullptr) override;
  def createRequest(self, op, req, outgoingData=None): # override
    url = req.url()
    #print url
    #if url.scheme() == 'https' and url.host() in ('www.dmm.com', 'dmm.com'):
    #  path = url.path()
    #  if path.startswith('/js/') or path.startswith('/css/'):
    #    url.setScheme('http') # downgrade to http
    #    req.setUrl(url)
    #    dprint("downgrade https to http:", url)
    #print url
    newurl = _WbNetworkAccessManager.getBlockedUrl(url)
    if newurl:
      req = QNetworkRequest(newurl)
    else:
      newurl = proxy.toproxyurl(url)
      if newurl and newurl != url:
        req = QNetworkRequest(req) # since request tis constent
        req.setUrl(newurl)
        _WbNetworkAccessManager.setRequestHeaders(req)
        reply = super(WbNetworkAccessManager, self).createRequest(op, req, outgoingData)
        #if url.host().lower().endswith('dmm.co.jp'):
        reply.setUrl(url) # restore the old url
        reply.setProperty(REQ_PROXY_URL, url)
        #print newurl
        return reply
      #else:
      #  print url

    _WbNetworkAccessManager.setRequestHeaders(req)
    return super(WbNetworkAccessManager, self).createRequest(op, req, outgoingData)

class _WbNetworkAccessManager:

  @staticmethod
  def setRequestHeaders(req):
    """Set the http header
    @param  req  QNetworkRequest
    """
    if req.hasRawHeader('Referer'): # Delete Referer so that it will not get tracked
      req.setRawHeader('Referer', '')
    #req.setRawHeader('User-Agent', config.USER_AGENT) # handled in WebKit
    #IP = '153.121.52.138'
    #keys = 'X-Forwarded-For', 'Client-IP', 'X-Client-IP', 'Real-IP', 'X-Real-IP'
    #for k in keys:
    #  req.setRawHeader(k, IP)

  @staticmethod
  def onReplyFinished(reply):
    """Fix the redirect URL
    @param  reply  QNetworkReply
    """
    proxyUrl = reply.property(REQ_PROXY_URL)
    if proxyUrl:
      #statusCode = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
      redirectUrl = reply.attribute(QNetworkRequest.RedirectionTargetAttribute)
      if redirectUrl:
        if not redirectUrl.host() and redirectUrl != reply.url() and redirectUrl != proxyUrl:
          redirectUrl.setHost(proxyUrl.host())
        else:
          redirectUrl = proxy.fromproxyurl(redirectUrl)
        if redirectUrl:
          reply.setAttribute(QNetworkRequest.RedirectionTargetAttribute, redirectUrl)

  @staticmethod
  def getBlockedUrl(url):
    """
    @param  url  QUrl
    @return  unicode or QUrl or None
    """
    if url.path() == '/js/localize_welcome.js': # for DMM
      dprint("block dmm localize welcome")
      return rc.DMM_LOCALIZED_WELCOME_URL

  # http://stackoverflow.com/questions/8362506/qwebview-qt-webkit-wont-open-some-ssl-pages-redirects-not-allowed
  @staticmethod
  def onSslErrors(reply, errors): # QNetworkReply, [QSslError] ->
    reply.ignoreSslErrors()
    #dprint("ignore ssl error")
    #print errors

# EOF
