# coding: utf8
# googletrans.py
# 8/2/2013 jichi
#
# See:
# https://github.com/alexbft/chiitrans/blob/master/ChiitransLite/www/js/translators.coffee
# https://github.com/terryyin/google-translate-python/blob/master/translate.py
#
# Example 1/21/2015:
# Detailed contents are only returned with client=t instead of client=p
# The format of t is JSON5?
#
# http://translate.google.com/translate_a/t?client=t&text=かわいい女の子&sl=ja&tl=en
# [[["Pretty girl","かわいい女の子","","Kawaī on'nanoko"]],,"ja",,[["Pretty girl",[1],true,false,1000,0,2,0]],[["かわいい 女の子",1,[["Pretty girl",1000,true,false],["Cute girl",0,true,false],["Pretty girls",0,true,false],["Cute girls",0,true,false],["A pretty girl",0,true,false]],[[0,7]],"かわいい女の子"]],,,[["ja"]],19]
#
# http:translate.google.com/translate_a/t?client=t&text=私は日本人ではない&sl=ja&tl=en
# [[["I am not a Japanese","私は日本人ではない","","Watashi wa nihonjinde wanai"]],,"ja",,[["I am not a",[1],true,false,502,0,4,0],["Japanese",[2],true,false,502,4,5,0]],[["私 は ない は で",1,[["I am not a",502,true,false],["I am not the",0,true,false],["I am not",0,true,false]],[[0,2],[5,9]],"私は日本人ではない"],["日本人",2,[["Japanese",502,true,false],["the Japanese",0,true,false],["Japanese people",0,true,false],["Japan",0,true,false],["a Japanese",0,true,false]],[[2,5]],""]],,,[["ja"]],65]
#
#
# Analysis API used by Google webpage
# Request: https://translate.google.com/translate_a/single?client=t&sl=ja&tl=zh-CN&hl=ja&dt=bd&dt=ex&dt=ld&dt=md&dt=qc&dt=rw&dt=rm&dt=ss&dt=t&dt=at&ie=UTF-8&oe=UTF-8&otf=1&ssel=0&tsel=0&tk=517378|356627&q=hello
#
# 2/20/2016 API change:
# Request: https://translate.google.com/translate_a/single?client=t&sl=ja&tl=zh-CN&hl=ja&dt=at&dt=bd&dt=ex&dt=ld&dt=md&dt=qca&dt=rw&dt=rm&dt=ss&dt=t&ie=UTF-8&oe=UTF-8&pc=1&otf=1&ssel=0&tsel=0&kc=1&tco=2&tk=259734.384347&q=%E3%81%93%E3%82%93%E3%81%AB%E3%81%A1%E3%81%AF

if __name__ == '__main__':
  import sys
  sys.path.append('..')

__all__ = 'GoogleTranslator', 'GoogleHtmlTranslator', 'GoogleJsonTranslator'

import re, json
import requests
from sakurakit import sknetdef
from sakurakit.skdebug import dwarn, derror
from sakurakit.skstr import unescapehtml
import googledef

# Remove repetive comma only before "or[ and after "or].
_re_gson_comma = re.compile(r'(?<=[\]"],),+(?=[\["])')
def eval_gson_list(data):
  """
  @param  data  unicode  Google JSON5 list
  @return  list or None

  In javascript, this can be simply done using:
    new Function("return " + data)
  """
  if data[0] == '[' and data[-1] == ']':
    try:
      data = _re_gson_comma.sub('', data)
      data = '{"r":%s}' % data
      return json.loads(data)['r']
    except Exception, e:
      dwarn(e)

class GoogleTranslator(object): pass

class GoogleHtmlTranslator(GoogleTranslator):
  API = 'https://translate.google.com/m'
  #API = 'https://translate.google.co.jp/m'
  api = API
  session = requests

  headers = {'User-Agent':sknetdef.USERAGENT, 'Accept-Encoding':'gzip'} #, 'Referer':API}

  #__rx = re.compile(r'class="t0"\>(.*?)\<') #, re.DOTALL|re.IGNORECASE)
  _TEXT_BEGIN = 'class="t0">' # faster than re
  _TEXT_END = "<"
  def translate(self, t, to='auto', fr='auto'):
    """
    @param  t  unicode
    @param* to  str
    @param* fr  str
    @return  unicode or None
    """
    try:
      r = self.session.post(self.api, headers=self.headers, data={
        'hl': googledef.lang2locale(to),
        'sl': googledef.lang2locale(fr),
        'q': t,
      })

      h = r.content
      if h:
        start = h.find(self._TEXT_BEGIN)
        if start > 0:
          start += len(self._TEXT_BEGIN)
          stop = h.find(self._TEXT_END, start)
          if stop > 0:
            h = h[start:stop]
            return unescapehtml(h)

    #except socket.error, e:
    #  dwarn("socket error", e.args)
    except requests.ConnectionError, e:
      dwarn("connection error", e.args)
    except requests.HTTPError, e:
      dwarn("http error", e.args)
    #except UnicodeDecodeError, e:
    #  dwarn("unicode decode error", e)
    except (ValueError, KeyError, IndexError, TypeError), e:
      dwarn("format error", e)
    except Exception, e:
      derror(e)
    dwarn("failed")
    try: dwarn(r.url)
    except: pass


class GoogleJsonTranslator(GoogleTranslator):
  #API_TRANSLATE = "http://translate.google.com/translate_a/t"
  #API_ANALYZE = "http://translate.google.com/translate_a/single"

  #api_translate = API_TRANSLATE
  #api_analyze = API_TRANSLATE

  API = "http://translate.google.com/translate_a/t"
  api = API

  session = requests

  headers = sknetdef.USERAGENT_HEADERS

  def translate(self, t, to='auto', fr='auto', align=None):
    """
    @param  t  unicode
    @param* to  str
    @param* fr  str
    @param* align  None or list  insert [unicode surf, unicode trans] if not None
    @return  unicode or None
    """
    try:
      #client_json = align is None
      client_json = False # pure json format is no longer supported

      # http://translate.google.com/translate_a/t?client=t&text=かわいい女の子&sl=ja&tl=en

      r = self.session.post(self.api, headers=self.headers, data={
        'tl': googledef.lang2locale(to),
        'sl': googledef.lang2locale(fr),
        'text': t,
        #'ie':'UTF-8',
        #'oe':'UTF-8',

        # http://stackoverflow.com/questions/10334358/how-to-get-and-parse-json-answer-from-google-translate
        #'client': 't', # This will return a Javascript object that can be evaluated using new Function
        #'client': 'p', # return JSON
        'client': 'p' if client_json else 't',

        # 2/28/2016
        'tk':'259734.384347', # this is the app token ID
        #'hl':'ja',
        #'dt':'at',
        #'dt':'bd',
        #'dt':'ex',
        #'dt':'ld',
        #'dt':'md',
        #'dt':'qca',
        #'dt':'rw',
        #'dt':'rm',
        #'dt':'ss',
        #'dt':'t',
        #'ie':'UTF-8',
        #'oe':'UTF-8',
        #'pc':'1',
        #'otf':'1',
        #'ssel':'0',
        #'tsel':'0',
        #'kc':'1',
        #'tco':'2',
      })

      #url = 'https://translate.google.com/translate_a/single?client=t&sl=ja&tl=zh-CN&hl=ja&dt=at&dt=bd&dt=ex&dt=ld&dt=md&dt=qca&dt=rw&dt=rm&dt=ss&dt=t&ie=UTF-8&oe=UTF-8&pc=1&otf=1&ssel=0&tsel=0&kc=1&tco=2&tk=259734.384347&q=%E3%81%93%E3%82%93%E3%81%AB%E3%81%A1%E3%81%AF'
      #r = self.session.get(url)

      ret = r.content # unicode not used since json can do that
      if r.ok and ret:
        if client_json:
          # Example: {"sentences":[{"trans":"闻花朵！","orig":"お花の匂い！","translit":"Wén huāduǒ!","src_translit":"O hananonioi!"}],"src":"ja","server_time":47}
          data = json.loads(ret)
          #print json.dumps(data, indent=2, ensure_ascii=False)
          l = data['sentences']
          if len(l) == 1:
            ret = l[0]['trans']
          else:
            ret = '\n'.join(it['trans'] for it in l)
          #ret = unescapehtml(ret)
          return ret

        elif not ret.startswith('[['):
          if len(ret) > 2 and ret[0] == '"' and ret[-1] == '"':
            ret = ret.decode('utf8')
            ret = ret[1:-1]
            return ret
          dwarn("response is invalid")
          return
        else:
          data = eval_gson_list(ret)
          if data:
            #print json.dumps(data, indent=2, ensure_ascii=False)
            l = data[0]
            if len(l) == 1:
              ret = l[0][0]
            else:
              ret = '\n'.join(it[0] for it in l)
            # Google JSON5 evaluation is not reliable
            # The result could be a list
            if isinstance(ret, basestring):
              if align is not None and len(data) > 3:
                # data[-4] is the segmented translation
                # data[-5] is the segmented source text
                align.extend(self._iteralign(data[-3]))
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
      dwarn("format error", e)
    except Exception, e:
      derror(e)
    dwarn("failed")
    try: dwarn(r.url)
    except: pass

  # Sample returned json5 list (incomplete):
  # [
  #   [
  #     [
  #       "210日元或者捕捉有信坤。 ",
  #       "悠真くんを攻略すれば２１０円か。",
  #       "210 Rì yuán huòzhě bǔzhuō yǒu xìn kūn. ",
  #       "Yūma-kun o kōryaku sureba 210-en ka."
  #     ],
  #     [
  #       "NAA喔...",
  #       "なるほどなぁ…",
  #       "NAA ō...",
  #       "Naruhodo nā…"
  #     ]
  #   ],
  #   "ja",
  #   [
  #     [
  #       "210日元",
  #       [
  #         1
  #       ],
  #       false,
  #       false,
  #       1000,
  #       0,
  #       1,
  #       0
  #     ],
  #     [
  #       "或者",
  #       [
  #         2
  #       ],
  #       false,
  #       false,
  #       639,
  #       1,
  #       2,
  #       0
  #     ],
  #     [
  #       "捕捉",
  #       [
  #         3
  #       ],
  #       false,
  #       false,
  #       380,
  #       2,
  #       3,
  #       0
  #     ],
  # ...
  #
  #     [
  #       "悠真",
  #       6,
  #       [
  #         [
  #           "YuShin",
  #           406,
  #           true,
  #           false
  #         ]
  #       ],
  #       [
  #         [
  #           0,
  #           2
  #         ]
  #       ],
  #       ""
  #     ],
  def _iteralign(self, data):
    """
    @param  data  list  gson list
    @yield  (unicode surface, unicode translation)
    """
    try:
      for l in data:
        surface = l[0]
        #index = l[1]
        trans = l[2][0][0] # Actually, there are a list of possible meaning
        if '(' in surface:
          for annot in ('(aux:relc)' '(null:pronoun)'):
            surface = surface.replace(annot, '').strip() # remove annotations
        yield surface, trans
    except Exception, e:
      derror(e)

  # The following function is an alternative API
  def analyze(self, t, to='auto', fr='auto', align=None):
    """
    @param  t  unicode
    @param* to  str
    @param* fr  str
    @param* align  None or list  insert [unicode surf, unicode trans] if not None
    @return  unicode or None
    """
    try:
      r = self.session.get(self.api_analyze, headers=self.headers, params={
        'tl': googledef.lang2locale(to),
        'sl': googledef.lang2locale(fr),
        'q': t,
        'dt': ('bd', 'ex', 'ld', 'md', 'qc', 'rw', 'rm', 'ss', 't', 'at'), # this list is indispensible
        'client': 't',

        # this is translation hash: TODO: Get this session
        'tk':'259734.384347',

        #'client': 'p', # this does not work

        # Following parameters are not needed
        #'ie': 'UTF-8',
        #'oe': 'UTF-8',
        #'hl':'ja', # not needed

        #'tk':'517378|356627',
        #'otf': 1,
        #'ssel': 0,
        #'tsel': 0,
      })

      ret = r.content # unicode not used since json can do that
      if r.ok and len(ret) > 20:
        data = eval_gson_list(ret)
        if data:
          #print json.dumps(data, indent=2, ensure_ascii=False)
          l = data[0]
          if len(l) == 1:
            ret = l[0][0]
          else:
            ret = '\n'.join(it[0] for it in l)
          # Google JSON5 evaluation is not reliable
          if isinstance(ret, basestring):
            if align is not None and len(data) > 3:
              # data[-4] is the segmented translation
              # data[-5] is the segmented source text
              align.extend(self._iterparse(data[-3]))
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
      dwarn("format error", e)
    except Exception, e:
      derror(e)
    dwarn("failed")
    try: dwarn(r.url)
    except: pass

if __name__ == '__main__':
  gt = GoogleHtmlTranslator()
  #gt = GoogleJsonTranslator()

  def test():
    global session

    #s = u"""オープニングやエンディングのアニメーションは単純に主人公を入れ替えた程度の物ではなく、タイトルロゴはもちろん金時や定春の行動や表情、登場する道具（万事屋の面々が乗る車のデザインなど）やクレジット文字など、細部に渡って変更がなされた。更に、坂田金時が『銀魂'』を最終回に追い込み新しいアニメ『まんたま』を始めようとした時にはエンディングや提供表示の煽りコメントが最終回を思わせる演出となり、『まんたま』でも専用のタイトルロゴとオープニングアニメーション（スタッフクレジット付き）が新造され、偽物の提供クレジットまで表示されるなど随所に至るまで徹底的な演出が行われた。また、テレビ欄では金魂篇終了回は『金魂'』最終回として、その翌週は新番組「銀魂'」として案内された。"""
    #s = u"お花の匂い！"
    #s = u"悠真くんを攻略すれば２１０円か。なるほどなぁ…"
    s = u'こんにちは'
    #s = '"<html>&abcde"'

    #s = u'ドアノブに勢い良く手をかけ、開いたドアが路上のガードレールにぶつかるのもおかまいなしに、隙間から身を這い出した。'
    #s = u'「う、ひょおおおおお――っ」'

    fr = 'ja'
    #to = 'zhs'
    to = 'en'

    #s = u"What are you doing?"
    #fr = "en"

    from sakurakit.skprof import SkProfiler

    # Does not work because
    # 1. need GZIP
    # 2. need redirect from http:// to https://
    #from qtrequests import qtrequests
    #from PySide.QtNetwork import QNetworkAccessManager
    #gt.session = qtrequests.Session(QNetworkAccessManager())
    #with SkProfiler():
    #  for i in range(1):
    #    t = translate(s, to=to, fr=fr)
    #print t

    # Could get blocked if using the same session
    #gt.session = requests.Session()
    #with SkProfiler():
    #  for i in range(1):
    #    t = translate(s, to=to, fr=fr)
    #print t

    #from proxyrequests import proxyconfig, proxyrequests
    #config = proxyconfig.USWEBPROXY_CONFIG
    ##config = proxyconfig.WEBPROXY_CONFIG
    ##config = proxyconfig.WEBSERVER_CONFIG
    #session = proxyrequests.Session(config, allows_caching=True)

    #with SkProfiler():
    #  for i in range(1):
    #    t = translate(s, to=to, fr=fr)
    #print t

    #setapi("https://153.121.52.138/proxyssl/gg/trans/m")

    m = []
    with SkProfiler():
      #for i in range(10):
      for i in range(1):
        t = gt.translate(s, to=to, fr=fr)
        #t = gt.translate(s, to=to, fr=fr, align=m)
        #t = gt.analyze(s, to=to, fr=fr, align=m)

    print t
    print type(t)
    print json.dumps(m, indent=2, ensure_ascii=False)

    #app.quit()

  test()
  #from PySide.QtCore import QCoreApplication, QTimer
  #app = QCoreApplication(sys.argv)
  #QTimer.singleShot(0, test)
  #app.exec_()

# EOF
