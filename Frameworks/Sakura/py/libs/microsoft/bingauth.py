# coding: utf8
# bingauth.py
# 10/7/2014 jichi
#
# Old API, see: http://www.forum-invaders.com.br/vb/showthread.php/42510-API-do-Bing-para-Traduzir-Textos
if __name__ == '__main__':
  import sys
  sys.path.append('..')

import re, requests
from sakurakit.skdebug import dwarn, derror
from sakurakit.sknetdef import GZIP_HEADERS

session = requests

APPID_RE = re.compile(r'rttAppId:"(.*?)"')
#APPID_URL = "http://www.bing.com/translator/dynamic/js/LandingPage.js"

# 12/10/2014
# See: http://hawkee.com/snippet/6925/
#APPID_URL = "http://www.bing.com/translator/dynamic/210010/js/LandingPage.js?loc=en&phenabled=&rttenabled=&v=210010"
APPID_URL = "http://www.bing.com/translator/dynamic/210010/js/LandingPage.js"

# Sample appID: TphQfI95DB7hNLTaOBJRGppiDD8NkTpAFuP3x1GNfDvxn89JVANAvwJrfSDlAPfXa
#
# The RTTAppId is found in LandingPage.js
# This is the same file containing "TranslateArray2" string
#
# Sample minimized js:
#   ,rttAppId:"TTW3CqZ9Xwce1fOTykYCtIDpQqQgUv-CHSMjp8EzMTTfn6B63_mUiA0QymMqKUpRs",
#
# CoffeeScript:
#   n.Configurations =
#     serviceName: "LP"
#     serviceURL: "http://api.microsofttranslator.com/v2/ajax.svc"
#     baseURL: "http://www.microsofttranslator.com:80/"
#     locale: j
#     referrer: b
#     appId: "TgKz3PgbCYkZ-EfOs_xE8m0y_mcnC9SCYAAYq0YHWAZ8*"
#     rttAppId: "TTW3CqZ9Xwce1fOTykYCtIDpQqQgUv-CHSMjp8EzMTTfn6B63_mUiA0QymMqKUpRs"
#     maxNumberOfChars: 5e3
#     translationLoggerUrl: "TranslationLogger.ashx"
#     rttEnabled: c
#     phraseAlignmentEnabled: c
def getappid():
  """
  @return  str or None
  """
  try:
    r = session.get(APPID_URL, headers=GZIP_HEADERS)
    t = r.content
    if r.ok and t:
      m = APPID_RE.search(t)
      if m:
        return m.group(1)
  #except socket.error, e:
  #  dwarn("socket error", e.args)
  except requests.ConnectionError, e:
    dwarn("connection error", e.args)
  except requests.HTTPError, e:
    dwarn("http error", e.args)
  except Exception, e:
    derror(e)

if __name__ == "__main__":
  print getappid()

# EOF
