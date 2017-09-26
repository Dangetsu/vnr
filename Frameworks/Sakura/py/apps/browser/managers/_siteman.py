# coding: utf8
# siteman.py
# 11/15/2014 jichi

class Site: # Abstract
  def match(self, url): return False # QUrl -> bool

class DmmSite(Site):
  def match(self, url):
    """@override"""
    host = url.host()
    if host:
      path = url.path()
      if path:
        return "dmm.co.jp" in host and path.startswith("/netgame/social/")
    return False

SITES = DmmSite,

# EOF
