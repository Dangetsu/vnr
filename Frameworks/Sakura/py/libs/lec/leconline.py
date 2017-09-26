# coding: utf8
# leconline.py
# 12/27/2012 jichi
#
# See: http://www.lec.com/translate-demos.asp

if __name__ == '__main__':
  import sys
  sys.path.append('..')

import requests
from sakurakit.skdebug import dwarn, derror
from sakurakit.sknetdef import GZIP_HEADERS
#from sakurakit.skstr import escapehtml

session = requests # global session

LEC_API = "http://www.lec.com/translate-demos.asp"

def _make_post(text, to, fr):
  """
  @param  text  unicode
  @param  to  unicode
  @param  fr  unicode
  @return  dict
  """
  # See source code: http://www.lec.com/translate-demos.asp
  ret = {
    'DoTransText': 'go',
    #'SourceText': escapehtml(text), # FIXME: escapehtml cannot fix the illegal characters
    'SourceText': text,
    'selectTargetLang': to[:2],
    'selectSourceLang': fr[:2],
  }
  if to == 'zhs':
    ret['simplifiedChinese'] = 0
  return ret

# Example:
# <textarea ReadOnly class="inputtext" cols="30" id="TranslationText" name="TranslationText" rows="6"  style="width: 323px""wrap="soft">
# Teclear su texto aquí ><
# </textarea>
def _parse(text): # html -> html
  """
  @param  text  unicode
  @return  unicode
  """
  pos = text.find(' id="TranslationText" ')
  if pos > 0:
    text = text[pos+1:]
    pos = text.find('>')
    if pos > 0:
      text = text[pos+1:]
      pos = text.find("</textarea>")
      if pos > 0:
        text = text[:pos]
        return text.strip()
  dwarn("failed to parse text")
  return ""

def translate(text, to='en', fr='ja'):
  """Return translated text, which is NOT in unicode format
  @param  text  unicode not None
  @param  fr  unicode not None, must be valid language code
  @param  to  unicode not None, must be valid language code
  @return  unicode or None
  """
  try:
    r = session.post(LEC_API,
        headers=GZIP_HEADERS, # disabled as qtrequests does not support it
        data=_make_post(text, to, fr))

    #print r.headers['Content-Type']
    ret = r.content

    # return error message if not r.ok
    # example response: {"t":[{"text":"hello"}]}
    if r.ok and len(ret) > 100:
      ret = _parse(ret)
    else:
      dwarn("return content too short")
    return ret.decode('utf8', errors='ignore')

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

  return ""

if __name__ == '__main__':
  #t = u"あのね  すもももももももものうち><" # Fixme: illegal html characters does not work
  #t = u"あのね  すもももももももものうち"
  #print translate(t, fr='ja', to='ar')

  #print translate(t, 'ko')

  #print translate(t, 'zh')
  #print translate(t, 'zhs')

  def test():
    global session

    #s = u"オープニングやエンディングのアニメーションは単純に主人公を入れ替えた程度の物ではなく、タイトルロゴはもちろん金時や定春の行動や表情、登場する道具（万事屋の面々が乗る車のデザインなど）やクレジット文字など、細部に渡って変更がなされた。更に、坂田金時が『銀魂'』を最終回に追い込み新しいアニメ『まんたま』を始めようとした時にはエンディングや提供表示の煽りコメントが最終回を思わせる演出となり、『まんたま』でも専用のタイトルロゴとオープニングアニメーション（スタッフクレジット付き）が新造され、偽物の提供クレジットまで表示されるなど随所に至るまで徹底的な演出が行われた。また、テレビ欄では金魂篇終了回は『金魂'』最終回として、その翌週は新番組「銀魂'」として案内された。"
    s = "test"
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

#import urllib, urllib2
#url = createUrl(text, to=INFOSEEK_LCODE[to], fr=INFOSEEK_LCODE[fr])
#try:
#  # See: http://stackoverflow.com/questions/3465704/python-urllib2-urlerror-http-status-code
#  response = urllib2.urlopen(url)
#  ret = response.read()
#except urllib2.HTTPError, e:
#  dwarn("http error code =", e.code)
#  return ""
#except urllib2.URLError, e:
#  dwarn("url error args =", e.args)
#  return ""
#finally:
#  try: response.close()
#  except NameError: pass
