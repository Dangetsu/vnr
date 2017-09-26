# coding: utf8
# fresheyemt.py
# 8/21/2012 jichi
# See: http://ready.to/search/list/cs_trans.htm

if __name__ == '__main__':
  import sys
  sys.path.append('..')

import requests
from sakurakit import skstr
from sakurakit.skdebug import dwarn, derror
#from sakurakit.sknetdef import GZIP_HEADERS
from unitraits.uniconv import wide2thin

session = requests # global session

FRESHEYE_HEADERS = {
  'Accept-Encoding': 'gzip',
  'Content-Type': "application/x-www-form-urlencoded",
}

# http://ready.to/search/list/cs_trans.htm
# [both=T]で原文と訳文の両方を出力します。[both=F]で訳文のみを出力します。

FRESHEYE_API_EN = "http://mt.fresheye.com/ft_result.cgi"
FRESHEYE_API_ZH = "http://mt.fresheye.com/ft_cjresult.cgi"

FRESHEYE_PARAMS_EN = {
  'enja': {'e':'EJ'},
  'jaen': {'e':'JE'},
}

FRESHEYE_PARAMS_ZH = {
  'jazhs': {'cjjc':'jc', 'charset':'gb2312'},
  'jazht': {'cjjc':'jc', 'charset':'big5'},
  'zhsja': {'cjjc':'cj', 'charset':'gb2312'},
  'zhtja': {'cjjc':'cj', 'charset':'big5'},
}

# <TEXTAREA class="out-form" name="gen_text2" cols="25" rows="15">
FRESHEYE_AREA_BEGIN = '<TEXTAREA class="out-form"'
#FRESHEYE_AREA_BEGIN2 = ">"
FRESHEYE_AREA_END = "</TEXTAREA>"


def _lang_params(to, fr):
  """
  @param  to  unicode
  @param  fr  unicode
  @return  (unicode url, {kw}) or (None,None)
  """
  langs = fr + to
  params = FRESHEYE_PARAMS_ZH.get(langs)
  if params:
    return FRESHEYE_API_ZH, params
  params = FRESHEYE_PARAMS_EN.get(langs)
  if params:
    return FRESHEYE_API_EN, params
  return None, None

def translate(text, to='en', fr='ja'):
  """Return translated text, which is NOT in unicode format
  @param  text  unicode not None
  @param  fr  unicode not None, must be valid language code
  @param  to  unicode not None, must be valid language code
  @return  unicode or None

  Returned text is not decoded, as its encoding can be guessed.
  """
  api, params = _lang_params(to=to, fr=fr)
  if not api:
    return None
  try:
    params = dict(params)
    params['gen_text'] = text
    r = session.post(api, headers=FRESHEYE_HEADERS, data=params);

    #print r.headers['Content-Type']
    ret = r.content

    if r.ok and len(ret) > 1000:
      start = ret.find(FRESHEYE_AREA_BEGIN)
      if start > 0:
        start += len(FRESHEYE_AREA_BEGIN)
        start = ret.find('>', start )
        if start > 0:
          start += 1
          stop = ret.find(FRESHEYE_AREA_END, start)
          if stop > 0:
            return wide2thin(ret[start:stop])

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
  #t = translate(u"あのね  すもももももももものうち", 'en')
  #print type(t), t
  #t = translate(u"你好", 'en', 'zhs')
  #print type(t), t
  #t = translate(u"你好", 'en', 'zht')
  #print type(t), t
  #t = translate(u"こんにちは", 'vi', 'ja')
  #print type(t), t.decode('sjis', errors='ignore')

  def test():
    global session

    s = u"オープニングやエンディングのアニメーションは単純に主人公を入れ替えた程度の物ではなく、タイトルロゴはもちろん金時や定春の行動や表情、登場する道具（万事屋の面々が乗る車のデザインなど）やクレジット文字など、細部に渡って変更がなされた。更に、坂田金時が『銀魂'』を最終回に追い込み新しいアニメ『まんたま』を始めようとした時にはエンディングや提供表示の煽りコメントが最終回を思わせる演出となり、『まんたま』でも専用のタイトルロゴとオープニングアニメーション（スタッフクレジット付き）が新造され、偽物の提供クレジットまで表示されるなど随所に至るまで徹底的な演出が行われた。また、テレビ欄では金魂篇終了回は『金魂'』最終回として、その翌週は新番組「銀魂'」として案内された。"
    #s = "test"
    fr = "ja"
    to = "zhs"

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

    #session = requests
    #with SkProfiler():
    #  for i in range(10):
    #    t = translate(s, to=to, fr=fr)
    #print t

    #app.quit()

  #from PySide.QtCore import QCoreApplication, QTimer
  #app = QCoreApplication(sys.argv)
  #QTimer.singleShot(0, test)
  #app.exec_()

  test()

# EOF
