# coding: utf8
# youdaofanyi.py
# 9/9/2013 jichi
#
# See: http://shared.ydstatic.com/fanyi/v2.3.3/scripts/fanyi.js
# See: http://idning.googlecode.com/svn/trunk/seo/porginal/youdao_porginal.py
#
# Coffee:
#   m = ->
#     l.translate
#       type: a("#customSelectVal").val()
#       i: u.utf8_decode(n.val())
#       doctype: "json"
#       xmlVersion: "1.6"
#       keyfrom: "fanyi.web"
#       ue: "UTF-8"
#       typoResult: not 0
#
#   u = (t) ->
#     __rl_event "translate_text"
#     n = "translate?smartresult=dict&smartresult=rule&smartresult=ugc&sessionFrom=" + r
#     o.ajax
#       type: "POST"
#       contentType: "application/x-www-form-urlencoded; charset=UTF-8"
#       url: n
#       data: t
#       dataType: "json"
#       success: (e) ->
#         s t, e
#       error: (t) ->
#         e("/tips").transRequestError t
#
#   t.fn.sel.defaults =
#     number: 13
#     hintList: [
#       val: "AUTO"
#       liText: "自动检测语言"
#       liClass: "normal"
#     ,
#       val: "ZH_CN2EN"
#       liText: "中文&nbsp; » &nbsp;英语"
#       liClass: "isfl topBorder1"
#     ,
#       val: "EN2ZH_CN"
#       liText: "英语&nbsp; » &nbsp;中文"
#       liClass: "isfl rightBorder topBorder"
#     ,
#       val: "ZH_CN2JA"
#       liText: "中文&nbsp; » &nbsp;日语"
#       liClass: "isfl"
#     ,
#       val: "JA2ZH_CN"
#       liText: "日语&nbsp; » &nbsp;中文"
#       liClass: "isfl rightBorder"
#     ,
#       val: "ZH_CN2KR"
#       liText: "中文&nbsp; » &nbsp;韩语"
#       liClass: "isfl"
#     ,
#       val: "KR2ZH_CN"
#       liText: "韩语&nbsp; » &nbsp;中文"
#       liClass: "isfl rightBorder"
#     ,
#       val: "ZH_CN2FR"
#       liText: "中文&nbsp; » &nbsp;法语"
#       liClass: "isfl"
#     ,
#       val: "FR2ZH_CN"
#       liText: "法语&nbsp; » &nbsp;中文"
#       liClass: "isfl rightBorder"
#     ,
#       val: "ZH_CN2RU"
#       liText: "中文&nbsp; » &nbsp;俄语"
#       liClass: "isfl"
#     ,
#       val: "RU2ZH_CN"
#       liText: "俄语&nbsp; » &nbsp;中文"
#       liClass: "isfl rightBorder"
#     ,
#       val: "ZH_CN2SP"
#       liText: "中文&nbsp; » &nbsp;西班牙语"
#       liClass: "isfl"
#     ,
#       val: "SP2ZH_CN"
#       liText: "西班牙语&nbsp; » &nbsp;中文"
#       liClass: "isfl rightBorder"
#     ]
#     containerId: "customSelectOption"
#     init: ->

if __name__ == '__main__':
  import sys
  sys.path.append('..')

import json
import requests
#from time import time
from sakurakit.skdebug import dwarn, derror
#from sakurakit.sknetdef import GZIP_HEADERS
import youdaodef

session = requests # global session

# Example:
#FANYI_API = "http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule&smartresult=ugc&sessionFrom=null"
FANYI_API = "http://fanyi.youdao.com/translate"

def translate(text, to='zhs', fr='ja'):
  """Translate from/into simplified Chinese.
  @param  text  unicode not None
  @param  fr  unicode not None
  @param  to  unicode not None
  @return  unicode or None
  """
  #tok = self.__d.token
  #if tok:
  try:
    r = session.post(FANYI_API,
      #headers=GZIP_HEADERS,
      # Example:
      #type=JA2ZH_CN&i=%C3%A3%C2%81%C2%93%C3%A3%C2%82%C2%93%C3%A3%C2%81%C2%AB%C3%A3%C2%81%C2%A1%C3%A3%C2%81%C2%AF&doctype=json&xmlVersion=1.6&keyfrom=fanyi.web&ue=UTF-8&typoResult=true
      data = {
        'doctype': 'json', # or json, xml, etc
        #'xmlVersion': '1.6',
        #'keyfrom': 'fanyi.web',
        #'ue': 'UTF-8',
        #'typoResult': 'true',
        'type': youdaodef.langtype(to, fr),
        'i':  text, # utf8
      }
    )
    ret = r.content
    # Example reply:
    #   errorcode=0
    #   result=hello world
    if r.ok and len(ret) > 10:
      # Example: {"type":"JA2ZH_CN","errorCode":0,"elapsedTime":3,"translateResult":[[{"src":"こんにちは？","tgt":"你好?"}]]}
      #ret = ret.decode('utf8', errors='ignore')
      ret = json.loads(ret)
      ret = '\n'.join(it['tgt'] for it in ret['translateResult'][0])
      return ret

  #except socket.error, e:
  #  dwarn("socket error", e.args)
  except requests.ConnectionError, e:
    dwarn("connection error", e.args)
  except requests.HTTPError, e:
    dwarn("http error", e.args)
  #except UnicodeDecodeError, e:
  #  dwarn("unicode decode error", e)
  except (ValueError, IndexError), e:
    dwarn("text format error", e)
  except Exception, e:
    derror(e)
  dwarn("failed")
  try: dwarn(r.url)
  except: pass

if __name__ == "__main__":
  #t = translate(u"Hello World!\nhello", to='zhs', fr='en')
  #t = translate(u"Hello World!\nhello", to='zhs', fr='ja')

  #s = u"オープニングやエンディングのアニメーションは単純に主人公を入れ替えた程度の物ではなく、タイトルロゴはもちろん金時や定春の行動や表情、登場する道具（万事屋の面々が乗る車のデザインなど）やクレジット文字など、細部に渡って変更がなされた。更に、坂田金時が『銀魂'』を最終回に追い込み新しいアニメ『まんたま』を始めようとした時にはエンディングや提供表示の煽りコメントが最終回を思わせる演出となり、『まんたま』でも専用のタイトルロゴとオープニングアニメーション（スタッフクレジット付き）が新造され、偽物の提供クレジットまで表示されるなど随所に至るまで徹底的な演出が行われた。また、テレビ欄では金魂篇終了回は『金魂'』最終回として、その翌週は新番組「銀魂'」として案内された。"
  #s = u"こんにちは？"
  s = u"本田"
  t = translate(s, to='zhs', fr='ja')
  #t = translate(u"神楽", to='zhs', fr='ja')
  print t

  #from PySide.QtGui import *
  #a = QApplication(sys.argv)
  #w = QLabel(t)
  #w.show()
  #a.exec_()

# EOF
