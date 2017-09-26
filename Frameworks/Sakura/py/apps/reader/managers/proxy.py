# coding: utf8
# proxy.py
# 8/14/2013 jichi

import re
from sakurakit.skclass import memoized
#from sakurakit.skdebug import dprint
import config

_RX_HOST = re.compile(r'http://([^/]*)')
def _hostof(url): # unicode -> unicode
  m = _RX_HOST.match(url.lower())
  return m.group(1) if m else ''

class ProxyManager:

  def __init__(self):
    self.setEnabled(False)

  def isEnabled(self): return self.enabled

  def setEnabled(self, t):
    self.enabled = t
    self.twitter_search = config.PROXY_TWITTER_SEARCH if t else config.TWITTER_SEARCH
    self.google_search = config.PROXY_GOOGLE_SEARCH if t else config.GOOGLE_SEARCH
    self.ytimg_i = config.PROXY_YTIMG_I if t else config.GOOGLE_YTIMG_I
    self.ytimg_s = config.PROXY_YTIMG_S if t else config.GOOGLE_YTIMG_S
    self.twimg_a = config.PROXY_TWIMG_A if t else config.TWITTER_TWIMG_A
    self.twimg_pbs = config.PROXY_TWIMG_PBS if t else config.TWITTER_TWIMG_PBS
    #self.getchu = config.PROXY_GETCHU if t else 'http://www.getchu.com'

  def isBlockedUrl(self, url): # unicode -> bool
    host = _hostof(url)
    if host:
      host = host.replace('www.', '')
      return self.isEnabled() and host == 'getchu.com' or host in config.PROXY_DOMAINS
    return False

  def makeYouTubeImageUrl(self, vid, large=True):
    """
    @param  vid  str
    @return  str
    """
    return "%s/vi/%s/%s.jpg" % (self.ytimg_i, vid, 'maxresdefault' if large else '0') # large, but not always available
    #return "%s/vi/%s/0.jpg" % (self.ytimg_i,  vid)

  def getGetchuUrl(self, url):
    """
    @param  url  str
    @return  str
    """
    return url.replace("http://www.getchu.com", config.PROXY_GETCHU) if self.enabled else url

  #def getGetchuIp(self, url):
  #  """
  #  @param  url  str
  #  @return  str
  #  """
  #  return url.replace("http://www.getchu.com", config.PROXY_GETCHU_IP) if self.enabled else url

  def getDLsiteUrl(self, url):
    """
    @param  url  str
    @return  str
    """
    return url.replace("http://www.dlsite.com", config.PROXY_DLSITE).replace("http://img.dlsite.jp", config.PROXY_DLSITE_IMG) if self.enabled else url

  #def isEnabled(self): return self.enabled

  _RX_HOST = re.compile(r'\/\/([^\/]+)\/')
  def getImageUrl(self, url):
    def repl(m):
      key = config.PROXY_SITES.get(m.group(1))
      if key:
        return "//%s/proxy/%s/" % (config.PROXY_HOST, key)
      else:
        return m.group(0)
    return self._RX_HOST.sub(repl, url)

@memoized
def manager(): return ProxyManager()

enabled = manager().isEnabled
#get_getchu_ip = manager().getGetchuIp
get_getchu_url = manager().getGetchuUrl
get_dlsite_url = manager().getDLsiteUrl
get_image_url = manager().getImageUrl
make_ytimg_url = manager().makeYouTubeImageUrl

replace_getchu_html = get_getchu_url
replace_dlsite_html = get_dlsite_url

# EOF
