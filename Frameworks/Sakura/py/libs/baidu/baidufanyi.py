# coding: utf8
# baidufanyi.py
# 5/19/2013 jichi
#
# Official: http://developer.baidu.com/wiki/index.php?title=帮助文档首页/百度翻译/翻译API
# Unofficial: https://gist.github.com/binux/1446348
#
# See: http://fanyi.baidu.com/static/i18n/zh/widget/translate/main/translateio/translateio.js
# See: http://fanyi.baidu.com/static/mobile/widget/translate-mobile/main/translateout/translateout.js
if __name__ == '__main__':
  import sys
  sys.path.append('..')

import json
import requests
#from time import time
from sakurakit.skdebug import dwarn, derror
#from sakurakit.sknetdef import GZIP_HEADERS
import baidudef

from sakurakit import skdatetime
def _rand(): return str(skdatetime.current_unixtime())

session = requests # global session

# Example:
# window['common'] = {server: {token: 'a379632293d590555a989af5e34e80c1',lang_list: {'zh': '中文','jp': '日语','th': '泰语','fra': '法语','en': '英语','spa': '西班牙语','ko': '韩语','tr': '土耳其语','vi': '越南语','ms': '马来语','de': '德语','ru': '俄语','ir': '伊朗语','ara': '阿拉伯语','et': '爱沙尼亚语','be': '白俄罗斯语','bg': '保加利亚语','hi': '印地语','is': '冰岛语','pl': '波兰语','fa': '波斯语','da': '丹麦语','tl': '菲律宾语','fi': '芬兰语','nl': '荷兰语','ca': '加泰罗尼亚语','cs': '捷克语','hr': '克罗地亚语','lv': '拉脱维亚语','lt': '立陶宛语','ro': '罗马尼亚语','af': '南非语','no': '挪威语','pt_BR': '巴西语','pt': '葡萄牙语','sv': '瑞典语','sr': '塞尔维亚语','eo': '世界语','sk': '斯洛伐克语','sl': '斯洛文尼亚语','sw': '斯瓦希里语','uk': '乌克兰语','iw': '希伯来语','el': '希腊语','hu': '匈牙利语','hy': '亚美尼亚语','it': '意大利语','id': '印尼语','sq': '阿尔巴尼亚语','am': '阿姆哈拉语','as': '阿萨姆语','az': '阿塞拜疆语','eu': '巴斯克语','bn': '孟加拉语','bs': '波斯尼亚语','gl': '加利西亚语','ka': '格鲁吉亚语','gu': '古吉拉特语','ha': '豪萨语','ig': '伊博语','iu': '因纽特语','ga': '爱尔兰语','zu': '祖鲁语','kn': '卡纳达语','kk': '哈萨克语','ky': '吉尔吉斯语','lb': '卢森堡语','mk': '马其顿语','mt': '马耳他语','mi': '毛利语','mr': '马拉提语','ne': '尼泊尔语','or': '奥利亚语','pa': '旁遮普语','qu': '凯楚亚语','tn': '塞茨瓦纳语','si': '僧加罗语','ta': '泰米尔语','tt': '塔塔尔语','te': '泰卢固语','ur': '乌尔都语','uz': '乌兹别克语','cy': '威尔士语','yo': '约鲁巴语' },account: {user_id: '65199631',add_name: true}
#TOKEN_RE = re.compile(r'mis\.CONST\.TOKEN="(\w+)";', re.I)
FANYI_API = "http://fanyi.baidu.com/transapi"

# If the original API does not work, use v2transapi instead.
# See: https://gist.github.com/gongstar/7983300
#FANYI_API = "http://fanyi.baidu.com/v2transapi"

#HEADERS = {
#  'User-Agent':"Mozilla/5.0 (Windows NT 6.1; rv:23.0) Gecko/20100101 Firefox/23.0",
#  'Referer':"http://fanyi.baidu.com/",
#  'Pragma':"no-cache",
#  'Host':"fanyi.baidu.com",
#  #Content-Type:application/x-www-form-urlencoded; charset=UTF-8
#  #Content-Length: 65
#  #Connection:keep-alive
#  #Cache-Control:no-cache
#  #Accept-Language:en-us,ja;q=0.7,en;q=0.3
#  #Accept-Encoding:gzip, deflate
#}

# Example json:
# {
#   "status": 0,
#   "domain": "all",
#   "from": "jp",
#   "type": 2,
#   "to": "zh",
#   "data": [
#     {
#       "src": "悠真くんを攻略すれば２１０円か。なるほどなぁ…",
#       "dst": "原悠君攻略的话210日元？。原来如此啊…",
#       "relation": [],
#       "result": [
#         [
#           0,
#           "原悠",
#           [
#             "0|6"
#           ],
#           [],
#           [
#             "0|6"
#           ],
#           [
#             "0|6"
#           ]
#         ],
#         [
#           1,
#           "君",
#           [
#             "6|9"
#           ],
#           [],
#           [
#             "6|9"
#           ],
#           [
#             "6|3"
#           ]
#         ],
#         [
#           2,
#           "攻略",
#           [
#             "15|6"
#           ],
#           [],
#           [
#             "15|6"
#           ],
#           [
#             "9|6"
#           ]
#         ],
#         [
#           3,
#           "的话",
#           [
#             "21|9"
#           ],
#           [],
#           [
#             "21|9"
#           ],
#           [
#             "15|6"
#           ]
#         ],
#         [
#           4,
#           "210",
#           [
#             "30|9"
#           ],
#           [],
#           [
#             "30|9"
#           ],
#           [
#             "21|3"
#           ]
#         ],
#         [
#           5,
#           "日元？",
#           [
#             "39|6"
#           ],
#           [],
#           [
#             "39|6"
#           ],
#           [
#             "24|9"
#           ]
#         ],
#         [
#           6,
#           "。",
#           [
#             "45|3"
#           ],
#           [],
#           [
#             "45|3"
#           ],
#           [
#             "33|3"
#           ]
#         ],
#         [
#           7,
#           "原来如此",
#           [
#             "48|12"
#           ],
#           [],
#           [
#             "48|12"
#           ],
#           [
#             "36|12"
#           ]
#         ],
#         [
#           8,
#           "啊",
#           [
#             "60|6"
#           ],
#           [],
#           [
#             "60|6"
#           ],
#           [
#             "48|3"
#           ]
#         ],
#         [
#           9,
#           "…",
#           [
#             "66|3"
#           ],
#           [],
#           [
#             "66|3"
#           ],
#           [
#             "51|3"
#           ]
#         ]
#       ]
#     }
#   ]
# }

def translate(text, to='zhs', fr='ja', align=None):
  """Return translated text, which is NOT in unicode format
  @param  text  unicode not None
  @param* fr  unicode not None, must be valid language code
  @param* to  unicode not None, must be valid language code
  @param* align  None or list  insert [unicode surf, unicode trans] if not None
  @return  unicode or None
  """
  #tok = self.__d.token
  #if tok:
  try:
    api = FANYI_API + '?' + _rand() # prevent from being blocked by baidu ><
    #api = FANYI_API
    r = session.post(api,
      #headers=HEADERS,
      data={
        'query': text, #.decode('utf8'),
        'from': baidudef.bdlang(fr),
        'to': baidudef.bdlang(to),
        #'ie': 'utf-8',
        #'source': 'txt',
        #'t': _BaiduFanyi.timestamp(),
        #'token': tok,
        #'token': 'a379632293d590555a989af5e34e80c1',
      }
    )

    ret = r.content
    if r.ok and len(ret) > 20 and ret[0] == '{' and ret[-1] == '}':
      #ret = ret.decode('utf8')
      js = json.loads(ret)
      #print json.dumps(js, indent=2, ensure_ascii=False)
      l = js['data']
      if len(l) == 1:
        ret = l[0]['dst']
      else:
        ret = '\n'.join(it['dst'] for it in l)
      if align is not None:
        align.extend(_iteralign(l))
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

def _iteralign(data, encoding='utf8'):
  """
  @param  data  list  json['data']
  @param* encoding  unicoding of raw json bytes for offset
  @yield  (unicode surface, unicode translation)
  """
  try:
    for sentence in data:
      src = sentence['src'].encode(encoding) #, errors='ignore') # get raw bytes
      for res in sentence['result']:
        #index = res[0] # int
        trans = res[1] # unicode
        offset = res[2][0] # such as "0|6"
        left, mid, right = offset.partition('|')
        left = int(left)
        right = int(right)
        surf = src[left:left+right].decode(encoding) #, errors='ignore')
        if surf:
          yield surf, trans
  except Exception, e:
    derror(e)

if __name__ == "__main__":

  def test():
    s = u"悠真くんを攻略すれば２１０円か。なるほどなぁ…"
    t = translate(s, to='sv', fr='ja')
    print t

  def test_align():
    m = []
    s = u"悠真くんを攻略すれば２１０円か。なるほどなぁ…"
    #s = u"hello"
    t = translate(s, to='zh', fr='ja', align=m)
    print t
    print json.dumps(m, indent=2, ensure_ascii=False)

  def test_yue():
    s = u"你在说什么？"
    t = translate(s, to='yue', fr='zh')
    print t

  def test_qt():
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

    #session = requests
    #with SkProfiler():
    #  for i in range(10):
    #    t = translate(s, to=to, fr=fr)
    #print t

    app.quit()

  test()

  #from PySide.QtCore import QCoreApplication, QTimer
  #app = QCoreApplication(sys.argv)
  #QTimer.singleShot(0, test)
  #app.exec_()

# EOF

#class _BaiduFanyi:
#
#  # Example:
#  # window['common'] = {server: {token: 'a379632293d590555a989af5e34e80c1',lang_list: {'zh': '中文','jp': '日语','th': '泰语','fra': '法语','en': '英语','spa': '西班牙语','ko': '韩语','tr': '土耳其语','vi': '越南语','ms': '马来语','de': '德语','ru': '俄语','ir': '伊朗语','ara': '阿拉伯语','et': '爱沙尼亚语','be': '白俄罗斯语','bg': '保加利亚语','hi': '印地语','is': '冰岛语','pl': '波兰语','fa': '波斯语','da': '丹麦语','tl': '菲律宾语','fi': '芬兰语','nl': '荷兰语','ca': '加泰罗尼亚语','cs': '捷克语','hr': '克罗地亚语','lv': '拉脱维亚语','lt': '立陶宛语','ro': '罗马尼亚语','af': '南非语','no': '挪威语','pt_BR': '巴西语','pt': '葡萄牙语','sv': '瑞典语','sr': '塞尔维亚语','eo': '世界语','sk': '斯洛伐克语','sl': '斯洛文尼亚语','sw': '斯瓦希里语','uk': '乌克兰语','iw': '希伯来语','el': '希腊语','hu': '匈牙利语','hy': '亚美尼亚语','it': '意大利语','id': '印尼语','sq': '阿尔巴尼亚语','am': '阿姆哈拉语','as': '阿萨姆语','az': '阿塞拜疆语','eu': '巴斯克语','bn': '孟加拉语','bs': '波斯尼亚语','gl': '加利西亚语','ka': '格鲁吉亚语','gu': '古吉拉特语','ha': '豪萨语','ig': '伊博语','iu': '因纽特语','ga': '爱尔兰语','zu': '祖鲁语','kn': '卡纳达语','kk': '哈萨克语','ky': '吉尔吉斯语','lb': '卢森堡语','mk': '马其顿语','mt': '马耳他语','mi': '毛利语','mr': '马拉提语','ne': '尼泊尔语','or': '奥利亚语','pa': '旁遮普语','qu': '凯楚亚语','tn': '塞茨瓦纳语','si': '僧加罗语','ta': '泰米尔语','tt': '塔塔尔语','te': '泰卢固语','ur': '乌尔都语','uz': '乌兹别克语','cy': '威尔士语','yo': '约鲁巴语' },account: {user_id: '65199631',add_name: true}
#  #TOKEN_RE = re.compile(r'mis\.CONST\.TOKEN="(\w+)";', re.I)
#  TOKEN_RE = re.compile(r"token: '([a-z0-9]+?)'")
#  TOKEN_URL = "http://fanyi.baidu.com/"
#  #TRANSLATE_URL = "http://fanyi.baidu.com/transcontent"
#  TRANSLATE_URL = "http://fanyi.baidu.com/transapi"
#
#  def __init__(self):
#    self._token = None # str
#
#  @staticmethod
#  def timestamp(): return long(time() * 1000)
#
#  @property
#  def token(self):
#    if not self._token:
#      self.resetToken()
#    return self._token
#
#  def resetToken(self):
#    try:
#      r = requests.get(_BaiduFanyi.TOKEN_URL, headers=GZIP_HEADERS)
#      t = r.content
#      if r.ok and t:
#        m = _BaiduFanyi.TOKEN_RE.search(t)
#        if m:
#          self._token = m.group(1)
#    except socket.error, e:
#      dwarn("socket error", e.args)
#    except requests.ConnectionError, e:
#      dwarn("connection error", e.args)
#    except requests.HTTPError, e:
#      dwarn("http error", e.args)
#    except Exception, e:
#      derror(e)
#
#  LANGUAGES = {
#    'en': 'en',
#    'ja': 'jp',
#    'zhs': 'zh',
#    'zht': 'zh',
#    'ko': 'ko',
#    'vi': 'vi',
#    'th': 'th',
#    'fr': 'fra',
#    'id': 'id',
#    'de': 'de',
#    'it': 'it',
#    'es': 'spa',
#    'pt': 'pt',
#    'ru': 'ru',
#  }
#  @classmethod
#  def langOf(cls, lang):
#    return cls.LANGUAGES.get(lang) or 'en'
#
#class BaiduFanyi(object):
#
#  def __init__(self):
#    self.__d = _BaiduFanyi()
#
#  def reset(self): self.__d.resetToken()
#
#  def translate(self, text, to='zhs', fr='ja'):
#    """Return translated text, which is NOT in unicode format
#    @param  text  unicode not None
#    @param  fr  unicode not None, must be valid language code
#    @param  to  unicode not None, must be valid language code
#    @return  unicode or None
#    """
#    #tok = self.__d.token
#    #if tok:
#    try:
#      r = requests.post(_BaiduFanyi.TRANSLATE_URL,
#        #headers=GZIP_HEADERS,
#        data={
#          'query': text, #.decode('utf8'),
#          'from': _BaiduFanyi.langOf(fr),
#          'to': _BaiduFanyi.langOf(to),
#          #'ie': 'utf-8',
#          #'source': 'txt',
#          #'t': _BaiduFanyi.timestamp(),
#          #'token': tok,
#        }
#      )
#
#      ret = r.content
#      if r.ok and len(ret) > 20:
#        #ret = ret.decode('utf8')
#        js = json.loads(ret)
#        l = js['data']
#        if len(l) == 1:
#          ret = l[0]['dst']
#        else:
#          ret = '\n'.join(it['dst'] for it in l)
#      return ret
#
#    except socket.error, e:
#      dwarn("socket error", e.args)
#    except requests.ConnectionError, e:
#      dwarn("connection error", e.args)
#    except requests.HTTPError, e:
#      dwarn("http error", e.args)
#    #except UnicodeDecodeError, e:
#    #  dwarn("unicode decode error", e)
#    except (ValueError, KeyError, IndexError, TypeError), e:
#      dwarn("json format error", e)
#    except Exception, e:
#      derror(e)
#    dwarn("failed")
#    try: dwarn(r.url)
#    except: pass
