# coding: utf8
# 10/12/2012 jichi
# VNR's interactive machine translation online.
#
# See: http://transer.com/sdk/rest_api_function.html
# See (auth): http://translation.infoseek.ne.jp/js/translation-text.js
# See (lang): http://translation.infoseek.ne.jp/js/userinfo.js

if __name__ == '__main__':
  import sys
  sys.path.append('..')

import json
import requests
from sakurakit.skdebug import dwarn, derror

session = requests # global session

API = "http://api.tranzz.com/api/translate"

APP_KEY = 'vnr' # str
APP_VERSION = 0 # int
APP_DOMAIN = 'game' # str

LANG_MAP = {
  'zhs': 'zh-CN',
  'zht': 'zh-TW',
}

def translate(text, to='zhs', fr='ja', domain=APP_DOMAIN):
  """Return translated text, which is NOT in unicode format
  @param  text  unicode not None
  @param* fr  unicode not None, must be valid language code
  @param* to  unicode not None, must be valid language code
  @param* domain  str
  @return  unicode or None

  Returned text is not decoded, as its encoding can be guessed.
  """
  try:
    fr = LANG_MAP.get(fr) or fr
    to = LANG_MAP.get(to) or to
    r = session.post(API, # both post and get work
      data={
        'fr': fr, # host language
        'to': to, # source languaeg
        'q': text, # query
        'domain': domain,
        'app': APP_KEY,
        'version': APP_VERSION,
      }
    )

    #print r.headers['Content-Type']
    ret = r.content

    # return error message if not r.ok
    # example response: {"t":[{"text":"hello"}]}
    if r.ok and ret:
      data = json.loads(ret)
      if data.get('status') == 0:
        ret = data['data']['t']
        return ret

  #except socket.error, e:
  #  dwarn("socket error", e.args)
  except requests.ConnectionError, e:
    dwarn("connection error", e.args)
  except requests.HTTPError, e:
    dwarn("http error", e.args)
  #except KeyError, e:
  #  dwarn("invalid response header", e.args)
  except Exception, e:
    derror(e)

  dwarn("failed")

  try: dwarn(r.url)
  except: pass

if __name__ == '__main__':

  def test():
    global session

    #s = u"オープニングやエンディングのアニメーションは単純に主人公を入れ替えた程度の物ではなく、タイトルロゴはもちろん金時や定春の行動や表情、登場する道具（万事屋の面々が乗る車のデザインなど）やクレジット文字など、細部に渡って変更がなされた。更に、坂田金時が『銀魂'』を最終回に追い込み新しいアニメ『まんたま』を始めようとした時にはエンディングや提供表示の煽りコメントが最終回を思わせる演出となり、『まんたま』でも専用のタイトルロゴとオープニングアニメーション（スタッフクレジット付き）が新造され、偽物の提供クレジットまで表示されるなど随所に至るまで徹底的な演出が行われた。また、テレビ欄では金魂篇終了回は『金魂'』最終回として、その翌週は新番組「銀魂'」として案内された。"
    #s = "test"
    s = u"悠真くんを攻略すれば２１０円か。なるほどなぁ…"
    #s = u"悠真くんを攻略すれば２１０円か。"
    #s = u"なるほどなぁ…"
    fr = "ja"
    #to = "zhs"
    to = "ko"
    #to = "en"

    #s = u"What are you doing?"
    #fr = "en"

    from sakurakit.skprof import SkProfiler

    #from qtrequests import qtrequests
    #from PySide.QtNetwork import QNetworkAccessManager
    #session = qtrequests.Session(QNetworkAccessManager())
    #with SkProfiler():
    #  for i in range(10):
    #    t = translate(s, to=to, fr=fr)
    #print t

    session = requests.Session()
    with SkProfiler():
      for i in range(1):
        t = translate(s, to=to, fr=fr)
    print t
    print type(t)

    #print json.dumps(m, indent=2, ensure_ascii=False)

    #session = requests
    #with SkProfiler():
    #  for i in range(10):
    #    t = translate(s, to=to, fr=fr)
    #print t

    #app.quit()

  test()
  #from PySide.QtCore import QCoreApplication, QTimer
  #app = QCoreApplication(sys.argv)
  #QTimer.singleShot(0, test)
  #app.exec_()

# EOF
