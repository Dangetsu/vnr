# coding: utf8
# yahoohonyaku.py
# 8/21/2012 jichi
#
# See: http://d.hatena.ne.jp/syonbori_tech/?of=5
# See: http://developer.yahoo.co.jp/webapi/jlp/ma/v1/parse.html
# See: http://honyaku.yahoo.co.jp/lib/js/translation.js?2290
if __name__ == '__main__':
  import sys
  sys.path.append('..')

import json, re, requests
from sakurakit.skdebug import dwarn, derror
from sakurakit.sknetdef import GZIP_HEADERS

class _YahooHonyaku:

  TOKEN_RE = re.compile(r'TTcrumb" value="(.*?)"')
  TOKEN_URL = "http://honyaku.yahoo.co.jp/transtext/"
  TRANSLATE_URL = "http://honyaku.yahoo.co.jp/TranslationText"

  def __init__(self):
    self._token = None # str

  @property
  def token(self):
    if not self._token:
      self.resetToken()
    return self._token

  # See: http://d.hatena.ne.jp/syonbori_tech/?of=5
  def resetToken(self):
    try:
      r = requests.get(_YahooHonyaku.TOKEN_URL, headers=GZIP_HEADERS)
      t = r.content
      if r.ok and t:
        m = _YahooHonyaku.TOKEN_RE.search(t)
        if m:
          self._token = m.group(1)
    #except socket.error, e:
    #  dwarn("socket error", e.args)
    except requests.ConnectionError, e:
      dwarn("connection error", e.args)
    except requests.HTTPError, e:
      dwarn("http error", e.args)
    except Exception, e:
      derror(e)

class YahooHonyaku(object):

  def __init__(self):
    self.__d = _YahooHonyaku()

  def reset(self): self.__d.resetToken()

  def translate(self, text, to='en', fr='ja'):
    """Return translated text, which is NOT in unicode format
    @param  text  unicode not None
    @param  fr  unicode not None, must be valid language code
    @param  to  unicode not None, must be valid language code
    @return  unicode or None
    """
    tok = self.__d.token
    if tok:
      try:
        # See: http://honyaku.yahoo.co.jp/lib/js/translation.js?2290
        # var defaults = {
        #     'db':'T',
        #     'for':'0', //T or F
        #     'qd':'T' //T or F
        # }
        # var param = "p=" + encodeURIComponent(txt).replace(/%0A$/,'') + "&ieid=" + ieid + "&oeid="+ oeid +"&results=1000&formality=" + formality + "&_crumb="+ crumb +"&output=json"+ optionParam;
        #
        #var LANGBOX = {"en":"英語",
        #               "ko":"韓国語",
        #               "ja":"日本語",
        #               "zh":"中国語",
        #               "de":"ドイツ語",
        #               "fr":"フランス語",
        #               "it":"イタリア語",
        #               "es":"スペイン語",
        #               "pt":"ポルトガル語"};
        r = requests.post(_YahooHonyaku.TRANSLATE_URL,
          #headers=GZIP_HEADERS,
          data={
            'p': text, #.decode('utf8'),
            'oeid': to[:2],
            'ieid': fr[:2],
            '_crumb': tok,
            'output': 'json',
            'formality': 0,
            'results': 1000, # limit
          }
        )

        ret = r.content
        if r.ok and len(ret) > 20 and ret[0] == '{' and ret[-1] == '}':
          #ret = ret.decode('utf8')
          js = json.loads(ret)
          l = js['ResultSet']['ResultText']['Results']
          if len(l) == 1:
             ret = l[0]['TranslatedText']
          else:
            ret = '\n'.join(it['TranslatedText'] for it in l)
          return ret

      #except socket.error, e:
      #  dwarn("socket error", e.args)
      except requests.ConnectionError, e:
        dwarn("connection error", e.args)
      except requests.HTTPError, e:
        dwarn("http error", e.args)
      #except UnicodeDecodeError, e:
      #  dwarn("unicode decode error", e)
      except (ValueError, KeyError, IndexError, TypeError), e:
        dwarn("json format error", e)
      except Exception, e:
        derror(e)
      dwarn("failed")
      try: dwarn(r.url)
      except: pass

def create_engine(): return YahooHonyaku()

if __name__ == "__main__":
  import sys
  e = create_engine()
  t = e.translate(u'こんにちは！\nこんにちは！', to='en', fr='ja')
  #t = e.translate(u'こんにちは！\nこんにちは！', to='vi', fr='ja')
  import sys
  from PySide.QtGui import *
  a = QApplication(sys.argv)
  w = QLabel(t)
  w.show()
  a.exec_()

# EOF
