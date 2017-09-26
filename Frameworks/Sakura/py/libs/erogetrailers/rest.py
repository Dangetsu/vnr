# coding: utf8
# rest.py
# 8/12/2013 jichi
#
# See: http://ketsuage.seesaa.net/article/263754550.html
# Example: http://erogetrailers.com/api?md=search_game&sw=%E3%83%AC%E3%83%9F%E3%83%8B%E3%82%BB%E3%83%B3%E3%82%B9&gameid=7998
# {
#  "searchWord":"レミニセンス",
#  "searchMode":"search",
#  "totalItems":2,
#  "items": [{
#   "id":7998,
#   "title":"レミニセンス ",
#   "romanTitle":"Reminiscence ",
#   "ecchi":true,
#   "brand":"てぃ～ぐる",
#   "platform":"PC",
#   "releaseDay":"2013年5月31日",
#   "releaseDayNumber":20130531,
#   "totalVideos":3,
#   "hp":"http://www.tigresoft.com/reminiscence/index.html",
#   "holyseal":"10548",
#   "erogamescape":"15986",
#   "amazon":"B00AT6K7OE",
#   "getchu":"718587",
#   "dmm":"",               # DL
#   "dmm2":"1781tig001",    # 通販
#   "gyutto":""
#  }

__all__ = 'RestApi',

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

from restful.online import JsonFileParser
from sakurakit.skstr import unescapehtml

_PATCHES = { # {long id:kw}
  2220:  {'brand': u"CORE-DUSK"},   # メサイア (MESSIAH)
  2309:  {'erogamescape': '6102'},  # カスタム隷奴III
  4143:  {'title': u"Blaze of Destiny II The beginning of the fate"},
  9952:  {'erogamescape': '17943'}, # 学☆王 -THE ROYAL SEVEN STARS- +METEOR(P
  9981:  {'brand' :u"美蕾"},        # 星の王女
  #10489: {'dmm2': '543ka0066'},     # プレスタ！ ～Precious☆Star'sフェスティバル～
  10839: {'brand':u"Mink"},         # 夜勤病棟 復刻版+
  11992: {'amazon': ''}, # 廻る娼館街のリィナ -- delete wrong amazon
  12712: {'releaseDayNumber': 20141128},
  13081: {'romanTitle': 'Natsuiro Recipe'}, # なついろレシピ
}

# API is stateless
# Make this class so that _fetch could be overridden
class RestApi(JsonFileParser):
  URL = 'http://erogetrailers.com/api' # str  override

  EROGAMESCAPE_TYPE = 'erogamescape' # にするとエロゲー批評空間のゲームIDで検索
  HOLYSEAL_TYPE = 'holyseal' # にすると聖封のゲームIDで検索
  EROGETRAILERS_TYPE = 'erogetrailers' # にするとエロトレのゲームIDで検索

  def _makeparams(self, text, type=None):
    """@reimp
    @param  kw
    @return  kw

    See: http://ymotongpoo.hatenablog.com/entry/20081123/1227430671
    See: http://ketsuage.seesaa.net/article/263754550.html
    """
    return {'sw':text, 'pg':type, 'md':'search_game'}

  def _parsejson(self, data):
    """@reimp
    @param  data
    @return  {kw}
    @raise
    """
    items = data['items']
    for item in items:
      if item['romanTitle'] == '::inedited:: ':
        item['romanTitle'] = ''
      f = _PATCHES.get(item['id'])
      if f:
        for k,v in f.iteritems():
          item[k] = v

      for k in 'title', 'romanTitle', 'brand':
        t = item[k]
        if t:
          item[k] = unescapehtml(t).rstrip() # remove right most space

      t = item.get('releaseDayNumber')
      if t and isinstance(t, int):
        s = "%s" % t
        if s.endswith('44'): # date number should not ends with > 31
          t -= 44 - 28 # change to 28
          item['releaseDayNumber'] = t
    return items

if __name__ == '__main__':
  api = RestApi()
  t = u"レミニセンス"
  t = u"diaborosu"
  t = "2309" # カスタム隷奴III
  t = '415' # ::inedited::
  t = 8458
  t = 12436 # 箱庭の学園
  q = api.query(t, type=api.EROGETRAILERS_TYPE)
  print q

  #t = 9610
  #q = api.query(t, type=api.EROGETRAILERS_TYPE)
  #for it in q:
  #  print it['title']

# EOF
