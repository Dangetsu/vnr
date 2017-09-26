# coding: utf8
# systran.py
# 4/11/2015 jichi
# See: https://github.com/gmateo/apache-cxf-example/blob/master/src/main/java/org/anotes/services/translator/infrastructure/SystranTranslator.java

if __name__ == '__main__':
  import sys
  sys.path.append('..')

import requests
from sakurakit.skdebug import dwarn, derror
from sakurakit.sknetdef import GZIP_HEADERS
from sakurakit.skstr import escapehtml, unescapehtml
import systrandef

session = requests # global session

# Example:
# URL: http://www.systranet.com/sai?gui=WebUI&lp=ja_en&sessionid=14287950017275746&service=systranettranslate
# Request: <html><body>こんにちは</body></html>
# Response: body= <html><body><span class="systran_seg" id="Sp1.s2_o"><span class="systran_token_word" value="1010/noun:common" id="token_1">こんにち</span><span class="systran_token_word" value="500d/prep" id="token_2">は</span></span></body></html>;<html> <meta http-equiv="Content-Type" content="text/html\; charset=UTF-8"> <body><span class="systran_seg" id="Sp1.s2_o"><span class="systran_token_word" value="1010/noun:common" id="token_1">Today</span></span></body></html>;

# http://www.systranet.com/sai?gui=WebUI&lp=ja_en&sessionid=14287950017275746&service=systranettranslate
SYSTRAN_API = "http://www.systranet.com/sai"
#SYSTRAN_API = "http://www.systranet.com/sai?lp=ja_en&service=translate"

SYSTRAN_TEXT_START = 'body=\n'
def translate(text, to='en', fr='ja'):
  """Return translated text, which is NOT in unicode format
  @param  text  unicode not None
  @param* fr  unicode not None, must be valid language code
  @param* to  unicode not None, must be valid language code
  @param* align  None or list  insert [unicode surf, unicode trans] if not None
  @return  unicode or None

  Returned text is not decoded, as its encoding can be guessed.
  """
  try:
    align = None # alignment is too 面倒くさい to implement and hence ignored
    if align is not None:
      text = "<html><body>%s</body></html>" % escapehtml(text).replace('\n', '<br>')
    r = session.post(SYSTRAN_API, # both post and get work
      headers=GZIP_HEADERS,
      params={
        #'gui': 'WebUI', # not really needed
        #'gui': 'text',
        'lp': systrandef.langpair(to=to, fr=fr),
        'service': 'translate' if align is None else 'systranettranslate',
        #'service': 'urlmarkuptranslate',
      },
      data=text.encode('utf8', errors='ignore'),
    )

    ret = r.content
    if r.ok and ret.startswith(SYSTRAN_TEXT_START):
      ret = ret[len(SYSTRAN_TEXT_START):]
      ret = ret.decode('utf8', errors='ignore')
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
    #s = u"オープニングやエンディングのアニメーションは単純に主人公を入れ替えた程度の物ではなく"
    #s = "test"
    s = u"悠真くんを攻略すれば２１０円か。"
    s += u"なるほどなぁ…"
    #s = u"こんにちは"
    fr = "ja"
    to = "en"

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

    #m = []
    #m = None

    session = requests.Session()
    with SkProfiler():
      for i in range(1):
        t = translate(s, to=to, fr=fr)
    print t
    print type(t)

  test()

  #from PySide.QtCore import QCoreApplication, QTimer
  #app = QCoreApplication(sys.argv)
  #QTimer.singleShot(0, test)
  #app.exec_()

# EOF
