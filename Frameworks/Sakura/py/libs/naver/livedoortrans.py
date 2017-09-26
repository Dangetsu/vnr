# coding: utf8
# livedoortrans.py
# 1/22/2015 jichi
# The service will be shutdown on 1/29/2015
#
# Japanese and multilingual: http://livedoor-translate.naver.jp
# Korean only: http://translate.naver.com
#
# Example:
# API: http://livedoor-translate.naver.jp/text/
# Request: m=ajaxExecute&translateParams.slang=ja&translateParams.tlang=ko&translateParams.originalText=%E3%81%93%E3%82%93%E3%81%AB%E3%81%A1%E3%81%AF&translateParams.langDetect=Y
# Response: {"translateStatus":true,"errorMsg":"","translateJsonResult":"[{\"langList\":[\"ja\"],\"tLang\":\"ko\",\"sLang\":\"ja\",\"originalText\":\"こんにちは\",\"locationInfor\":[{\"transTextLen\":5,\"orgTextLen\":5,\"orgTextPos\":0,\"transTextPos\":0}],\"translatedText\":\"안녕하세요\"},{\"tLang\":\"ja\",\"sLang\":\"ko\",\"originalText\":\"안녕하세요\",\"locationInfor\":[{\"transTextLen\":5,\"orgTextLen\":5,\"orgTextPos\":0,\"transTextPos\":0}],\"translatedText\":\"こんにちは\"}]"}

if __name__ == '__main__':
  import sys
  sys.path.append('..')

import json
import requests
from sakurakit.skdebug import dwarn, derror
from sakurakit.sknetdef import GZIP_HEADERS

session = requests # global session

NAVER_API = "http://livedoor-translate.naver.jp/text/"

def translate(text, to='zhs', fr='ja'):
  """Return translated text, which is NOT in unicode format
  @param  text  unicode not None
  @param  fr  unicode not None, must be valid language code
  @param  to  unicode not None, must be valid language code
  @return  unicode or None
  """
  #tok = self.__d.token
  #if tok:
  try:
    r = session.post(NAVER_API,
      #headers=HEADERS,
      data={
        'm': 'ajaxExecute',
        'translateParams.slang': fr[:2],
        'translateParams.tlang': to[:2],
        #'translateParams.langDetect': 'Y',
        'translateParams.originalText': text,
      }
    )

    ret = r.content
    if r.ok and len(ret) > 20 and ret[0] == '{' and ret[-1] == '}':
      #ret = ret.decode('utf8')
      data = json.loads(ret)
      #if data.get('translateStatus'): # supposed to be true
      data = data['translateJsonResult']
      l = json.loads(data)
      #print json.dumps(data, sort_keys=True, indent=4)
      #if len(l) == 1:
      ret = l[0]['translatedText']
      #else:
      #  ret = '\n'.join(it['translatedText'] for it in l)
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

if __name__ == "__main__":

  def test():
    global session

    #s = u"オープニングやエンディングのアニメーションは単純に主人公を入れ替えた程度の物ではなく、タイトルロゴはもちろん金時や定春の行動や表情、登場する道具（万事屋の面々が乗る車のデザインなど）やクレジット文字など、細部に渡って変更がなされた。更に、坂田金時が『銀魂'』を最終回に追い込み新しいアニメ『まんたま』を始めようとした時にはエンディングや提供表示の煽りコメントが最終回を思わせる演出となり、『まんたま』でも専用のタイトルロゴとオープニングアニメーション（スタッフクレジット付き）が新造され、偽物の提供クレジットまで表示されるなど随所に至るまで徹底的な演出が行われた。また、テレビ欄では金魂篇終了回は『金魂'』最終回として、その翌週は新番組「銀魂'」として案内された。"
    s = u"お花の匂い"
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
