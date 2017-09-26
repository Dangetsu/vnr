# coding: utf8
# navertrans.py
# 1/22/2015 jichi
#
# Japanese and multilingual: http://livedoor-translate.naver.jp
# Korean only: http://translate.naver.com
#
# Example:
# API: http://translate.naver.com/translate.dic
# Post data: query=hello&srcLang=en&tarLang=ko&highlight=1&hurigana=1
#
# Only limited language pairs are supported.

if __name__ == '__main__':
  import sys
  sys.path.append('..')

import json
import requests
from collections import OrderedDict
from sakurakit.skdebug import dwarn, derror
from sakurakit.sknetdef import GZIP_HEADERS

session = requests # global session

NAVER_API = "http://translate.naver.com/translate.dic"

# Example highlight result for: 悠真くんを攻略すれば２１０円か。なるほどなぁ
#
# {
#   "resultCode": 0,
#   "resultData": "유진 군을 공략하면 210엔?과연..",
#   "align": [
#     {
#       "ss": 0,
#       "te": 5,
#       "ts": 0,
#       "se": 5
#     },
#     {
#       "ss": 6,
#       "te": 9,
#       "ts": 7,
#       "se": 11
#     },
#     {
#       "ss": 12,
#       "te": 25,
#       "ts": 10,
#       "se": 29
#     },
#     {
#       "ss": 30,
#       "te": 32,
#       "ts": 27,
#       "se": 41
#     },
#     {
#       "ss": 42,
#       "te": 33,
#       "ts": 33,
#       "se": 47
#     },
#     {
#       "ss": 48,
#       "te": 39,
#       "ts": 34,
#       "se": 59
#     },
#     {
#       "ss": 60,
#       "te": 41,
#       "ts": 40,
#       "se": 68
#     }
#   ],
#   "hurigana": [
#     {
#       "h": "ゆう",
#       "s": 0,
#       "z": "悠",
#       "e": 3
#     },
#     {
#       "h": "しん",
#       "s": 3,
#       "z": "真",
#       "e": 6
#     },
#     {
#       "h": "こうりゃく",
#       "s": 15,
#       "z": "攻略",
#       "e": 21
#     },
#     {
#       "h": "えん",
#       "s": 39,
#       "z": "円",
#       "e": 42
#     }
#   ],
#   "dir": "j2k"
# }
def translate(text, to='ko', fr='ja', align=None):
  """Return translated text, which is NOT in unicode format
  @param  text  unicode not None
  @param  fr  unicode not None, must be valid language code
  @param  to  unicode not None, must be valid language code
  @param* align  None or list  insert [unicode surf, unicode trans] if not None
  @return  unicode or None
  """
  #tok = self.__d.token
  #if tok:
  try:
    r = session.post(NAVER_API,
      #headers=HEADERS,
      data={
        'srcLang': fr[:2],
        'tarLang': to[:2],
        #'translateParams.langDetect': 'Y',
        'query': text,
        'highlight': 1 if align is not None else 0,
        'hurigana': 0, # turn off furigana, which seems not working though
      }
    )

    ret = r.content
    if r.ok and len(ret) > 20:
      data = json.loads(ret)
      #print json.dumps(data, indent=2, ensure_ascii=False)
      ret = data['resultData']
      if align is not None:
        align.extend(_iteralign(
            data.get('align'), text, ret))
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

def _iteralign(data, source, target, encoding='utf8'):
  """
  @param  data  list  json['align']
  @param  source  unicode  original text
  @param  target  unicode  result translation
  @param* encoding  unicoding of raw json bytes for offset
  @yield  (unicode surface, unicode translation)
  """
  try:
    # {
    #   "ss": 48 # source start
    #   "se": 59 # source end
    #   "te": 39 # target start
    #   "ts": 34 # target end
    # },
    source = source.encode(encoding)
    target = target.encode(encoding)
    if isinstance(data, list): # English -> Korean
      for align in data:
        ss = int(align['ss'])
        se = int(align['se'])
        ts = int(align['ts'])
        te = int(align['te'])

        s = source[ss:se+1].decode(encoding)
        t = target[ts:te+1].decode(encoding)
        if s:
          yield s, t
    elif isinstance(data, dict): # Japanese -> Korean
      slist = data['src']
      tlist = data['tar']
      m = OrderedDict() # {int group, ([unicode s], [unicode t])}  mapping from s to t

      for it in tlist:
        group = it['g']
        fr = it['f'] #
        to = it['t'] #
        t = target[fr:to+1].decode(encoding)
        l = m.get(group)
        if l:
          l[1].append(t)
        else:
          m[group] = [], [t]

      for it in slist:
        group = it['g']
        fr = it['f'] #
        to = it['t'] #
        s = source[fr:to+1].decode(encoding)
        l = m.get(group)
        if l:
          l[0].append(s)
        else:
          m[group] = [s], []

      #for k in sorted(m.iterkeys()):
      for s,t in m.itervalues():
        yield s, t
  except Exception, e:
    derror(e)

if __name__ == "__main__":

  def test():
    global session

    #s = u"オープニングやエンディングのアニメーションは単純に主人公を入れ替えた程度の物ではなく、タイトルロゴはもちろん金時や定春の行動や表情、登場する道具（万事屋の面々が乗る車のデザインなど）やクレジット文字など、細部に渡って変更がなされた。更に、坂田金時が『銀魂'』を最終回に追い込み新しいアニメ『まんたま』を始めようとした時にはエンディングや提供表示の煽りコメントが最終回を思わせる演出となり、『まんたま』でも専用のタイトルロゴとオープニングアニメーション（スタッフクレジット付き）が新造され、偽物の提供クレジットまで表示されるなど随所に至るまで徹底的な演出が行われた。また、テレビ欄では金魂篇終了回は『金魂'』最終回として、その翌週は新番組「銀魂'」として案内された。"
    s = u"お花の匂い"
    s = '"<html>&abcde"'
    s = u"그렇습니다"
    s = u"hello"
    s = u"悠真くんを攻略すれば２１０円か。なるほどなぁ…"
    s = u'るみちゃん、めでたい結婚を機にさ、名前変えたら'

    fr = "ja"
    fr = "zhs"
    fr = "es"
    fr = "th"

    fr = "en"
    fr = "es"
    to = "en"

    fr = "ja"
    to = "ko"

    s = "hello world"
    fr = "en"

    s = u"What are you doing for today?"
    fr = "en"

    from sakurakit.skprof import SkProfiler

    #from qtrequests import qtrequests
    #from PySide.QtNetwork import QNetworkAccessManager
    #session = qtrequests.Session(QNetworkAccessManager())
    #with SkProfiler():
    #  for i in range(1):
    #    t = translate(s, to=to, fr=fr)
    #print t

    m = []

    session = requests.Session()
    with SkProfiler():
      for i in range(1):
        t = translate(s, to=to, fr=fr, align=m)
    print s
    print t

    print json.dumps(m, indent=2, ensure_ascii=False)

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
