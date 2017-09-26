# coding: utf8
# skwebkit.py
# 11/9/2011 jichi

__all__ = 'SkNetworkCookieJar',

from skdebug import dprint
from PySide.QtNetwork import QNetworkCookie, QNetworkCookieJar

## Cookies ##

# http://stackoverflow.com/questions/13971787/how-do-i-save-cookies-with-qt
# http://qt.gitorious.org/qt/qt/trees/4.8/demos/browser

class SkNetworkCookieJar(QNetworkCookieJar):

  def __init__(self, parent=None):
    super(SkNetworkCookieJar, self).__init__(parent)
    # Control characters (\x00 to \x1F plus \x7F) aren't allowed,
    # http://stackoverflow.com/questions/1969232/allowed-characters-in-cookies
    self.marshalSeparator = '\0' # illegal in cookie

  def marshal(self): # -> str
    l = self.allCookies()
    dprint("cookie count = %i" % len(l))
    return self.marshalSeparator.join((
      cookie.toRawForm().data() for cookie in l
    ))

  def unmarshal(self, data):  # str ->
    l = ([] if not data else [cookie
      for it in data.split(self.marshalSeparator)
      for cookie in QNetworkCookie.parseCookies(it)
    ])
    dprint("cookie count = %i" % len(l))
    self.setAllCookies(l)

# EOF
