# coding: utf8
# worldtrans.py
# 7/5/2012 jichi
#
# URLs
if __name__ == '__main__':
  import sys
  sys.path.append('..')

import re, requests
from sakurakit.skdebug import dwarn, derror
from sakurakit.sknetdef import GZIP_HEADERS
from sakurakit.skstr import unescapehtml

session = requests # global session

def _LANG(lang):
  """
  @param  lang  str
  @return  str
  """
  return 'CH' if lang == 'ZH' else lang

EXCITE_API =  "http://www.excite.co.jp/world/"
def api(to='en', fr='ja'):
  """
  @return  str
  @raise  KeyError
  """
  FR, TO = fr.upper(), to.upper()
  langs = fr, to
  if 'en' in langs:
    return ''.join((EXCITE_API, "english/?wb_lp=", FR, TO)) # http://www.excite.co.jp/world/english/?wb_lp=jaen
  elif 'zhs' in langs:
    return ''.join((EXCITE_API, "chinese/?wb_lp=", _LANG(FR[:2]), _LANG(TO[:2])))
  elif 'zht' in langs:
    return ''.join((EXCITE_API, "chinese/?big5=yes&wb_lp=", _LANG(FR[:2]), _LANG(TO[:2])))
  elif 'ko' in langs:
    return ''.join((EXCITE_API, "korean/?wb_lp=", FR, TO))
  elif 'fr' in langs:
    return ''.join((EXCITE_API, "french/?wb_lp=", FR, TO))
  elif 'de' in langs:
    return ''.join((EXCITE_API, "german/?wb_lp=", FR, TO))
  elif 'it' in langs:
    return ''.join((EXCITE_API, "italian/?wb_lp=", FR, TO))
  elif 'es' in langs:
    return ''.join((EXCITE_API, "spanish/?wb_lp=", FR, TO))
  elif 'pt' in langs:
    return ''.join((EXCITE_API, "portuguese/?wb_lp=", FR, TO))
  elif 'ru' in langs:
    return ''.join((EXCITE_API, "russian/?wb_lp=", FR, TO))
  else:
    #raise KeyError(langs) # English by default
    return ''.join((EXCITE_API, "english/?wb_lp=", FR, TO))

__re_search = re.compile(r"%s%s%s" % (
  re.escape(' name="after">'),
  r'(.*?)',
  re.escape('</textarea>')
), re.DOTALL|re.IGNORECASE)
def translate(text, to='en', fr='ja'):
  """Return translated text, which is NOT in unicode format
  @param  text  unicode not None
  @param  fr  unicode not None, must be valid language code
  @param  to  unicode not None, must be valid language code
  @return  unicode or None
  """
  try:
    r = session.get(api(to, fr),
      headers=GZIP_HEADERS, # disabled since not supported by qt
      params={
        'before': text
      }
    )

    #print r.headers['Content-Type']
    ret = r.content

    if r.ok and len(ret) > 1000:
      # Extract text within '<textarea .*name="after">' and '</textarea>'
      m = __re_search.search(ret)
      if m:
        ret = m.group(1)
        ret = ret.decode('utf8', errors='ignore')
        ret = unescapehtml(ret)
      else:
        dwarn("content not matched: %s" % ret)
    return ret

  #except socket.error, e:
  #  dwarn("socket error", e.args)
  except requests.ConnectionError, e:
    dwarn("connection error", e.args)
  except requests.HTTPError, e:
    dwarn("http error", e.args)
  #except UnicodeDecodeError, e:
  #  dwarn("unicode decode error", e)
  except KeyError, e:
    dwarn("language error", e)
  #except KeyError, e:
  #  dwarn("invalid response header", e.args)
  except Exception, e:
    derror(e)

  dwarn("failed")

  try: dwarn(r.url)
  except: pass

  return ""

if __name__ == '__main__':
  #s = u"あのね\nすもももももももものうち！"
  #s = u"こんにちは"
  #t = translate(s, 'zhs')
  #print t
  #import sys
  #from PySide.QtGui import *
  #a = QApplication(sys.argv)
  #w = QLabel(t)
  #w.show()
  #a.exec_()

  def test():
    global session

    s = u"オープニングやエンディングのアニメーションは単純に主人公を入れ替えた程度の物ではなく、タイトルロゴはもちろん金時や定春の行動や表情、登場する道具（万事屋の面々が乗る車のデザインなど）やクレジット文字など、細部に渡って変更がなされた。更に、坂田金時が『銀魂'』を最終回に追い込み新しいアニメ『まんたま』を始めようとした時にはエンディングや提供表示の煽りコメントが最終回を思わせる演出となり、『まんたま』でも専用のタイトルロゴとオープニングアニメーション（スタッフクレジット付き）が新造され、偽物の提供クレジットまで表示されるなど随所に至るまで徹底的な演出が行われた。また、テレビ欄では金魂篇終了回は『金魂'』最終回として、その翌週は新番組「銀魂'」として案内された。"
    #s = "test"
    fr = "ja"
    to = "zhs"

    #s = u"What are you doing?"
    #fr = "en"

    from sakurakit.skprof import SkProfiler

    from qtrequests import qtrequests
    from PySide.QtNetwork import QNetworkAccessManager
    session = qtrequests.Session(QNetworkAccessManager())
    with SkProfiler():
      for i in range(1):
        t = translate(s, to=to, fr=fr)
    print t

    session = requests.Session()
    with SkProfiler():
      for i in range(1):
        t = translate(s, to=to, fr=fr)
    print t
    print type(t)

    #session = requests
    #with SkProfiler():
    #  for i in range(10):
    #    t = translate(s, to=to, fr=fr)
    #print t

    app.quit()

  from PySide.QtCore import QCoreApplication, QTimer
  app = QCoreApplication(sys.argv)
  QTimer.singleShot(0, test)
  app.exec_()

# EOF
