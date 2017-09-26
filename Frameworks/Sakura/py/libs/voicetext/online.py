# coding: utf8
# online.py
# 10/9/2014 jichi
#
# API: http://dws.voicetext.jp/tomcat/data.xml
#
# See: http://voicetext.jp/
#
# Example:
#
# HIKARI (ja) Normal:
# Text: 憎しみは憎しみしか生まない。
# POST http://dws.voicetext.jp/tomcat/servlet/vt [HTTP/1.1 200 OK 587ms]
# - X-Requested-With: XMLHttpRequest
# - Referer: http://dws.voicetext.jp/tomcat/demonstration/top.html
# - Content-Type: application/x-www-form-urlencoded; charset=UTF-8
# - Request: text=%E6%86%8E%E3%81%97%E3%81%BF%E3%81%AF%E6%86%8E%E3%81%97%E3%81%BF%E3%81%97%E3%81%8B%E7%94%9F%E3%81%BE%E3%81%AA%E3%81%84%E3%80%82&talkID=306&volume=100&speed=100&pitch=100&dict=3
# - Response: comp=2014101001_2254_0375.mp3
#
# GET http://dws.voicetext.jp/tomcat/servlet/put_count [HTTP/1.1 200 OK 167ms]
# GET http://dws.voicetext.jp/tomcat/servlet/get_count [HTTP/1.1 200 OK 361ms]
# GET http://dis.voicetext.jp/ASLCLCLVVS/JMEJSYGDCHMSMHSRKPJL/2014101001_2254_0375.mp3 [HTTP/1.1 206 Partial Content 565ms]
# GET http://dis.voicetext.jp/ASLCLCLVVS/JMEJSYGDCHMSMHSRKPJL/2014101001_2254_0375.mp3 [HTTP/1.1 206 Partial Content 841ms]
#
# put_count/get_count are used to track visit counts and not needed.
#
# HIKARI (ja) Micro
# Text: 憎しみは憎しみしか生まない。
# POST http://dws.voicetext.jp/tomcat/servlet/vt [HTTP/1.1 200 OK 542ms]
# - Request: text=%E6%86%8E%E3%81%97%E3%81%BF%E3%81%AF%E6%86%8E%E3%81%97%E3%81%BF%E3%81%97%E3%81%8B%E7%94%9F%E3%81%BE%E3%81%AA%E3%81%84%E3%80%82&talkID=356&volume=100&speed=100&pitch=100&dict=3
#
# GET http://dws.voicetext.jp/tomcat/servlet/put_count_micro [HTTP/1.1 200 OK 155ms]
# GET http://dws.voicetext.jp/tomcat/servlet/get_count_micro [HTTP/1.1 200 OK 309ms]
# GET http://dis.voicetext.jp/ASLCLCLVVS/JMEJSYGDCHMSMHSRKPJL/2014101001_2700_0915.mp3 [HTTP/1.1 206 Partial Content 470ms]
# GET http://dis.voicetext.jp/ASLCLCLVVS/JMEJSYGDCHMSMHSRKPJL/2014101001_2700_0915.mp3 [HTTP/1.1 206 Partial Content 1052ms]
#
# HYERYUN (ko) Normal:  text=%EC%95%88%EB%85%95%ED%95%98%EC%84%B8%EC%9A%94.+%EC%A0%80%EB%8A%94+VoiceText%EC%9D%98+%ED%98%9C%EB%A0%A8%EC%9E%85%EB%8B%88%EB%8B%A4.%0A%EB%B3%B8%EC%A0%90%EC%9D%98+%EC%98%81%EC%97%85+%EC%8B%9C%EA%B0%84%EC%97%90+%EB%8C%80%ED%95%B4%EC%84%9C+%EC%95%8C%EB%A0%A4+%EB%93%9C%EB%A6%BD%EB%8B%88%EB%8B%A4.&talkID=14&volume=100&speed=100&pitch=100&dict=0
# HYERYUN (ko) Micro:   text=%EC%95%88%EB%85%95%ED%95%98%EC%84%B8%EC%9A%94.+%EC%A0%80%EB%8A%94+VoiceText%EC%9D%98+%ED%98%9C%EB%A0%A8%EC%9E%85%EB%8B%88%EB%8B%A4.%0A%EB%B3%B8%EC%A0%90%EC%9D%98+%EC%98%81%EC%97%85+%EC%8B%9C%EA%B0%84%EC%97%90+%EB%8C%80%ED%95%B4%EC%84%9C+%EC%95%8C%EB%A0%A4+%EB%93%9C%EB%A6%BD%EB%8B%88%EB%8B%A4.&talkID=64&volume=100&speed=100&pitch=100&dict=0
#
# BRIDGET (en) Normal:  text=Hello+world&talkID=500&volume=100&speed=100&pitch=100&dict=3
# BRIDGET (en) Micro:   text=Hello+world&talkID=550&volume=100&speed=100&pitch=100&dict=3
#
# HONG (小紅, zht) Normal:  text=%E6%82%A8%E5%A5%BD%EF%BC%8C%E6%88%91%E6%98%AFVoiceText%E5%B0%8F%E7%B4%85%E3%80%82%0A%E5%85%B3%E4%BA%8E%E6%9C%AC%E5%BA%97%E7%9A%84%E8%90%A5%E4%B8%9A%E6%97%B6%E9%97%B4%E5%91%8A%E7%9F%A5&talkID=204&volume=100&speed=100&pitch=100&dict=0
# HONG (小紅, zht) Micro:   text=%E6%82%A8%E5%A5%BD%EF%BC%8C%E6%88%91%E6%98%AFVoiceText%E5%B0%8F%E7%B4%85%E3%80%82%0A%E5%85%B3%E4%BA%8E%E6%9C%AC%E5%BA%97%E7%9A%84%E8%90%A5%E4%B8%9A%E6%97%B6%E9%97%B4%E5%91%8A%E7%9F%A5&talkID=254&volume=100&speed=100&pitch=100&dict=0

if __name__ == '__main__':
  import sys
  sys.path.append('..')

import requests
from collections import OrderedDict
from sakurakit.skdebug import dwarn
from sakurakit.sknetio import topercentencoding

class Voice:
  __slots__ = 'key', 'id', 'dic', 'language', 'gender', 'name'
  def __init__(self, key, id, dic, language, gender, name):
    self.id = id # int
    self.microId = id + 50 # int
    self.dic = dic # int
    self.key = key # str
    self.language = language # str
    self.gender = gender # 'f' or 'm'
    self.name = name # unicode

# See: http://dws.voicetext.jp/tomcat/data.xml
VOICES = (
  # ja
  Voice('hikari',    306, 3, 'ja', 'f', u"ヒカリ"),
  Voice('sayaka',    304, 3, 'ja', 'f', u"サヤカ"),
  Voice('haruka',    303, 3, 'ja', 'f', u"ハルカ"),
  Voice('misaki',    302, 3, 'ja', 'f', u"ミサカ"),
  Voice('takeru',    307, 3, 'ja', 'm', u"タケル"),
  Voice('ryo',       305, 3, 'ja', 'm', u"リョウ"),
  Voice('show',      301, 3, 'ja', 'm', u"ショウ"),

  # zh-TW
  Voice('hong',      202, 2, 'zh',  'f', u"小紅"),
  Voice('qiang',     203, 2, 'zh',  'm', u"小强"),

  # ko

  Voice('hyeryun',   10,  0, 'ko',  'f', u"혜련"),
  Voice('jihun',     3,   0, 'ko',  'm', u"지훈"),

  # en-US
  Voice('julie',     103, 1, 'en',  'f', u"Julie"),
  Voice('kate',      100, 1, 'en',  'f', u"Kate"),
  Voice('james',     104, 1, 'en',  'm', u"James"),
  Voice('paul',      101, 1, 'en',  'm', u"Paul"),

  # en
  Voice('bridget',   500, 1, 'en',  'f', u"Bridget"),
  Voice('hugh',      501, 2, 'en',  'm', u"Hugh"),

  # es
  Voice('violeta',   400, 4, 'es', 'f', u"Violeta"),
  Voice('francisco', 401, 4, 'es', 'm', u"Francisco"),

  # fr-CA
  Voice('chloe',     600, 4, 'fr', 'f', u"Chloé"),
)
VOICES = OrderedDict(((it.key,it) for it in VOICES))

#API = "http://dws.voicetext.jp/tomcat/servlet/vt"
API = "http://dws2.voicetext.jp/tomcat/servlet/vt"

#RESULT_URL = "http://dis.voicetext.jp/ASLCLCLVVS/JMEJSYGDCHMSMHSRKPJL/"
RESULT_URL = "http://dws2.voicetext.jp/ASLCLCLVVS/JMEJSYGDCHMSMHSRKPJL/"

HEADERS = {
  'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8', # UTF-8 is indispensable
  #'Referer': 'http://dws.voicetext.jp/tomcat/demonstration/top.html', # referrer is not needed, but used in case something is wrong
  'Referer': 'http://dws2.voicetext.jp/tomcat/demonstration/top.html',

  #'X-Requested-With': 'XMLHttpRequest',
  #'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:38.0) Gecko/20100101 Firefox/38.0',
  #'Pragma': 'no-cache',
  #'Host': 'dws2.voicetext.jp',
  #'DNT': 1,
  #'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
  #'Connection': 'keep-alive',
  #'Cache-Control': 'no-cache',
  #'Accept-Language': 'en-US,en;q=0.5',
  #'Accept-Encoding': 'gzip, deflate',
  #'Accept': 'text/plain, */*; q=0.01',
}

MAX_TEXT_LENGTH = 200

# Pitch: [0.5, 2.0], default 1.0
# Speed: [0.5, 2.0], default 1.0
def createdata(id, dic, text, encoding='utf8', pitch=100, speed=100, volume=100):
  """
  @param  id  int
  @param  dic  int
  @param  text  unicode
  @param* encoding  str
  @param* pitch  int
  @param* speed  int
  @param* volume  int
  @return  unicode  post data
  """
  if len(text) > MAX_TEXT_LENGTH:
    text = text[:MAX_TEXT_LENGTH]
  text = topercentencoding(text)
  return "talkID=%s&dict=%s&pitch=%s&speed=%s&volume=%s&text=%s" % (id, dic, pitch, speed, volume, text) if text else ''

RESPONSE_BEGIN = "comp="
def resolveurl(data, session=requests):
  """
  @param  data  str
  @param* session  requests
  @return  unicode or None  url
  """
  try:
    r = session.post(API, data=data, headers=HEADERS)
    if r and r.ok and r.content and r.content.startswith(RESPONSE_BEGIN):
      return RESULT_URL + r.content[len(RESPONSE_BEGIN):].rstrip()
  except Exception, e:
    dwarn(e)

if __name__ == '__main__':
  # HIKARI
  v = VOICES['misaki']
  text = u"こんにちは"
  data = createdata(v.id, v.dic, text, pitch=200)
  print data

  url = resolveurl(data)
  print url

# EOF
