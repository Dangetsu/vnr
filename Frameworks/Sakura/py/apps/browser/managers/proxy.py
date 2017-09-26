# coding: utf8
# proxy.py
# 3/25/2014 jichi

import re
from PySide.QtCore import QUrl
import config

import settings
_MAINLAND = settings.reader().isMainlandChina()
#_MAINLAND = True

def _normalize_host(url): # str -> str
  url = url.lower()
  if not url.startswith('www.'):
    url = 'www.' + url
  return url

_PROXY_DOMAINS = {
  _normalize_host(host):ip
  for host,ip in config.PROXY_DOMAINS.iteritems()
} # {string host: string ip}

_PROXY_IPS = {
  ip:host
  for host,ip in config.PROXY_DOMAINS.iteritems()
} # {string ip: string host}

_PROXY_SITES = {
  _normalize_host(host):key
  for key,host in config.PROXY_SITES.iteritems()
} # {string host: string key}

_DLSITE_PROXY_SITES = {
  _normalize_host(host):key
  for host,key in (
    ('www.dlsite.com', 'dlsite/www'),
    ('img.dlsite.jp', 'dlsite/img'),
  )
} # {string host: string key}

_TORANOANA_PROXY_SITES = {
  _normalize_host(host):key
  for host,key in (
    ('www.toranoana.jp', 'toranoana/www'),
    ('img.toranoana.jp', 'toranoana/img'),
  )
} # {string host: string key}

## Functions ##

_SCHEME_PROXY = {
  'http': '/proxy/',
  #'https': '/proxyssl/',
}

def toproxyurl(url): # QUrl -> QUrl or None
  proxy = _SCHEME_PROXY.get(url.scheme())
  if proxy:
    url = QUrl(url) # Avoid modifying the original URL
    host = _normalize_host(url.host())
    ip = _PROXY_DOMAINS.get(host) if _MAINLAND else None
    if ip:
      url.setHost(ip)
    else:
      key = _PROXY_SITES.get(host)
      if not key and _MAINLAND:
        key = _DLSITE_PROXY_SITES.get(host) or _TORANOANA_PROXY_SITES.get(host)
      if key:
        url.setHost(config.PROXY_HOST)
        path = proxy + key + url.path()
        url.setPath(path)
    #print url
    return url

_re_proxy_key = re.compile(r'/proxy/([^/]+)(.*)')
_re_proxy_key2 = re.compile(r'/proxy/([^/]+/[^/]+)(.*)') # up to two levels of regex
def fromproxyurl(url): # QUrl -> QUrl or None
  if not isinstance(url, QUrl):
    url = QUrl(url)
  if url.scheme() in ('http', 'https'):
    host = url.host()
    if host == config.PROXY_HOST:
      path = url.path()
      for rx in _re_proxy_key, _re_proxy_key2:
        m = rx.match(path)
        if m:
          key = m.group(1)
          if key:
            host = config.PROXY_SITES.get(key)
            if host:
              url = QUrl(url)
              url.setHost(host)
              path = m.group(2) or '/'
              if path[0] != '/':
                path = '/' + path
              url.setPath(path)
              return url
          #elif _MAINLAND and key == 'dlsite':
          #  host = None
          #  path = m.group(2) or '/'
          #  if path.startswith('/www'):
          #    host = _DLSITE_PROXY_SITES['/dlsite/www']
          #    path = path[4:] or '/'
          #  elif path.startswith('/img'):
          #    host = _DLSITE_PROXY_SITES['/dlsite/img']
          #    path = path[4:] or '/'
          #  if host:
          #    url = QUrl(url)
          #    url.setHost(host)
          #    url.setPath(path)
          #    return url
    elif _MAINLAND:
      host = _PROXY_IPS.get(host)
      if host:
        url = QUrl(url)
        url.setHost(host)
        return url

# EOF
