# coding: utf8
# siteman.py
# 11/15/2014 jichi

from sakurakit.skclass import memoized
import _siteman

@memoized
def manager(): return SiteManager()

class SiteManager:
  def __init__(self):
    self.sites = [cls() for cls in _siteman.SITES]

  def matchSite(self, url):
    """
    @param  url  QUrl
    return  Site or None
    """
    for site in self.sites:
      if site.match(url):
        return site

# EOF
