# coding: utf8
# transru.py
# 3/17/2014 jichi
#
# http://sakuradite.com/topic/166
# http://en.wikipedia.org/wiki/PROMT
# http://translate.ru
# http://online-translator.com
# https://github.com/mishin/gists/blob/master/4translate_tmp.pl
# http://kbyte.ru/ru/Forums/Show.aspx?id=14948

if __name__ == '__main__':
  import sys
  sys.path.append('..')

import json
import requests
from sakurakit.skdebug import dwarn, derror
#from sakurakit.sknetdef import GZIP_HEADERS

session = requests # global session

#RU_API = "http://translation.ru/Default.aspx/Text?prmtlang=ru"
#RU_API = "http://logrus.ru" "/services/TranslationService.asmx/GetTranslateNew"
RU_API = "http://www.translate.ru" "/services/TranslationService.asmx/GetTranslateNew"

RU_HEADERS = {'Content-Type':'application/json'} # use json type

# https://github.com/mishin/gists/blob/master/4translate_tmp.pl
# $.ajax({
#    type: "POST",
#    contentType: "application/json; charset=utf-8",
#    url: "/services/TranslationService.asmx/GetTranslateNew",
#    data: "{ dirCode:'"+dir+"', template:'"+templ+"', text:'"+text+"', lang:'en', limit:"+maxlen+",useAutoDetect:false, key:'"+key+"',  ts:'"+TS+"', tid:'"+tmpID+"',IsMobile:false}",
#    dataType: "json",
#    success: function(res){
#      SetValsAfterTr(res);
#
#    //added 28.10.13
#    RefreshAdv_inRes();
#    //-----//------
#
#    },
#    error: function (XMLHttpRequest, textStatus, errorThrown) {
#      GetErrMsg("Sorry, the service is temporarily unavailable. Please try again later.");
#    }
# });

def translate(text, to='ru', fr='ja'):
  """Return translated text, which is NOT in unicode format
  @param  text  unicode not None
  @param  fr  unicode not None, must be valid language code
  @param  to  unicode not None, must be valid language code
  @return  unicode or None

  Returned text is not decoded, as its encoding can be guessed.
  """
  try:
    r = session.post(RU_API,
      headers=RU_HEADERS,
      data=json.dumps({
        'dirCode': fr[0] + to[0], # dir
        'template': 'General', # templ
        'text': text,
        'lang': to[:2],
        'limit': 3000, # maxlen
        'useAutoDetect': False,
        'key':  '',
        'ts': 'MainSite', # TS
        'tid': '', # tmpID,
        'IsMobile': False,
      })
    )

    #print r.headers['Content-Type']
    ret = r.content

    # return error message if not r.ok
    # Example: {"__type":"TranslationResult","isURL":false,"isWord":false,"ptsDirCode":"je","advise":"","autoCode":0,"result":"You see, as for the plum and the peach among peaches","resultNoTags":"","dirNames":"Translation is completed from Japanese into English","adviseParams":{"showIntime":false,"adviseText":null},"errCodeInt":0,"errCode":0,"errMessage":null}
    if r.ok and len(ret) > 20 and ret[0] == '{' and ret[-1] == '}':
      # Unicode char, see: http://schneide.wordpress.com/2009/05/18/the-perils-of-u0027/
      #ret = __repl(ret[15:-4])
      ret = json.loads(ret)['d']['result']
      return ret.replace('<br/>', '\n')

  #except socket.error, e:
  #  dwarn("socket error", e.args)
  except requests.ConnectionError, e:
    dwarn("connection error", e.args)
  except requests.HTTPError, e:
    dwarn("http error", e.args)
  except (ValueError, KeyError), e:
    dwarn("invalid response json", e.args)
  except Exception, e:
    derror(e)

  dwarn("failed")

  try: dwarn(r.url)
  except: pass

if __name__ == '__main__':
#  t = translate(u"あのね  すもももももももものうち", 'en')
#  print type(t), t
#  t = translate(u"hello", 'ja', 'en')
#  print type(t), t
#
#  t = u"""あのね
#だめなの
#><"""
#  print translate(t, 'en', 'ja')

  def test():
    global session

    s = u"オープニングやエンディングのアニメーションは単純に主人公を入れ替えた程度の物ではなく、タイトルロゴはもちろん金時や定春の行動や表情、登場する道具（万事屋の面々が乗る車のデザインなど）やクレジット文字など、細部に渡って変更がなされた。更に、坂田金時が『銀魂'』を最終回に追い込み新しいアニメ『まんたま』を始めようとした時にはエンディングや提供表示の煽りコメントが最終回を思わせる演出となり、『まんたま』でも専用のタイトルロゴとオープニングアニメーション（スタッフクレジット付き）が新造され、偽物の提供クレジットまで表示されるなど随所に至るまで徹底的な演出が行われた。また、テレビ欄では金魂篇終了回は『金魂'』最終回として、その翌週は新番組「銀魂'」として案内された。"
    #s = "test"
    fr = "ja"
    to = "en"

    #s = u"What are you doing?"
    #fr = "en"

    from sakurakit.skprof import SkProfiler

    #from qtrequests import qtrequests
    #from PySide.QtNetwork import QNetworkAccessManager
    #session = qtrequests.Session(QNetworkAccessManager())
    #with SkProfiler():
    #  for i in range(1):
    #    t = translate(s, to=to, fr=fr)
    #print t

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
