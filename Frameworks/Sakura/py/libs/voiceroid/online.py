# coding: utf8
# online.py
# 10/8/2014 jichi
#
# See: http://www.ah-soft.com/voiceroid/index.html
# See: http://www.ah-soft.com/product/index.html
#
# 東北ずん子: http://www.ah-soft.com/voiceroid/zunko/
#
# Text: 憎しみは憎しみしか生まない。
#
# 1. POST http://voice.ai-j.jp/aitalk_2webapi.php [HTTP/1.1 200 OK 1549ms]
# Referer: http://voice.ai-j.jp/voiceroid2demo_zunko.swf
# Content-type: application/x-www-form-urlencoded
# Content-length: 232
# Request: gain=&delay=&speaker%5Fid=994&pitch=1%2E0&speed=1%2E0&text=%E6%8I6%8E%E3%81%97%E3%81%BF%E3%81%AF%E6%86%8E%E3%81%97%E3%81%BF%E3%81%97%E3%81%8B%E7%94%9F%E3%81%BE%E3%81%AA%E3%81%84%E3%80%82&password=aidemo&username=AIHPDemo&reqid=create
# Response: voiceFile=http://182.48.0.54/aitalk-ajax/php/tmp/994_20141009112906855325490.mp3
#
# 2. GET http://182.48.0.54/aitalk-ajax/php/tmp/994_20141009112906855325490.mp3 [HTTP/1.1 200 OK 854ms]
# Referer: http://182.48.0.54/aitalk-ajax/php/tmp/994_20141009112906855325490.mp3
# Response: empty
#
# 3. POST http://voice.ai-j.jp/aitalk_2webapi.php [HTTP/1.1 200 OK 187ms]
# Referer: http://voice.ai-j.jp/voiceroid2demo_zunko.swf
# Content-type: application/x-www-form-urlencoded
# Content-length: 118
# Request: filename=http%3A%2F%2F182%2E48%2E0%2E54%2Faitalk%2Dajax%2Fphp%2Ftmp%2F994%5F20141009112906855325490%2Emp3&reqid=delete
# Response: empty
#
# 結月ゆかり: http://www.ah-soft.com/voiceroid/yukari/index.html
#
# Text: 憎しみは憎しみしか生まない。
#
# 1. POST http://voice.ai-j.jp/aitalk_2webapi.php [HTTP/1.1 200 OK 2625ms]
# Referer: http://voice.ai-j.jp/voiceroid2demo_yukari.swf
# Content-type: application/x-www-form-urlencoded
# Content-length: 230
# Request: gain=&delay=&speaker%5Fid=2&pitch=1%2E0&speed=1%2E0&text=%E6%86%8E%E3%81%97%E3%81%BF%E3%81%AF%E6%86%8E%E3%81%97%E3%81%BF%E3%81%97%E3%81%8B%E7%94%9F%E3%81%BE%E3%81%AA%E3%81%84%E3%80%82&password=aidemo&username=AIHPDemo&reqid=create
# Response: voiceFile=http://182.48.0.54/aitalk-ajax/php/tmp/2_201410091136361167072195.mp3
#
# 2. GET http://182.48.0.54/aitalk-ajax/php/tmp/2_201410091136361167072195.mp3 [HTTP/1.1 200 OK 2381ms]
#
# 3. POST http://voice.ai-j.jp/aitalk_2webapi.php [HTTP/1.1 200 OK 560ms]

if __name__ == '__main__':
  import sys
  sys.path.append('..')

import requests
from collections import OrderedDict
from sakurakit.skdebug import dwarn
from sakurakit.skstr import urlencode

class Voice:
  __slots__ = 'id', 'key', 'gender', 'name', 'url'
  def __init__(self, id, key, gender, name, url):
    self.id = id # int
    self.key = key # str
    self.gender = gender # 'f' or 'm'
    self.name = name # unicode
    self.url = url # str

VOICES = ( # unicode key -> int id
  Voice(1202, 'zunko',  'f', u"東北ずん子", "http://www.ah-soft.com/voiceroid/zunko/"),
  #Voice(994, 'zunko',  'f', u"東北ずん子", "http://www.ah-soft.com/voiceroid/zunko/"),
  Voice(1206,   'yukari', 'f', u"結月ゆかり", "http://www.ah-soft.com/voiceroid/yukari/"),
  #Voice(2,   'yukari', 'f', u"結月ゆかり", "http://www.ah-soft.com/voiceroid/yukari/"),
  Voice(3,   'maki',    'f', u"民安ともえ", "http://www.ah-soft.com/voiceroid/maki/"),
  Voice(1001, 'aoi',    'f', u"琴葉 葵",    "http://www.ah-soft.com/voiceroid/kotonoha/"),
  #Voice(992, 'aoi',    'f', u"琴葉 葵",    "http://www.ah-soft.com/voiceroid/kotonoha/"),
  Voice(203, 'akane',   'f', u"琴葉 茜",    "http://www.ah-soft.com/voiceroid/kotonoha/"),
  #Voice(999, 'akane',  'f', u"琴葉 茜",    "http://www.ah-soft.com/voiceroid/kotonoha/"),
  Voice(1203, 'ai',     'f', u"月読アイ",   "http://www.ah-soft.com/voiceroid/ai/"),
  #Voice(995, 'ai',     'f', u"月読アイ",   "http://www.ah-soft.com/voiceroid/ai/"),
  Voice(1204, 'shota',  'm', u"月読ショタ", "http://www.ah-soft.com/voiceroid/shota/"),
  #Voice(996, 'shota',  'm', u"月読ショタ", "http://www.ah-soft.com/voiceroid/shota/"),
  Voice(1207, 'kou',    'm', u"水無瀬コウ", "http://www.ah-soft.com/voiceroid/kou/"),
  Voice(1201, 'taka',   'm', u"鷹の爪 吉田くん", "http://www.ah-soft.com/voiceroid/taka/"),
  #Voice(993, 'taka',   'm', u"鷹の爪 吉田くん", "http://www.ah-soft.com/voiceroid/taka/"),
)
VOICES = OrderedDict(((it.key,it) for it in VOICES))

API = "http://cloud.ai-j.jp/demo/aitalk2webapi.php"

HEADERS = {
  'Content-Type':'application/x-www-form-urlencoded',
  'Referer': 'http://voice.ai-j.jp', # referrer is not needed, but used in case something is wrong
  #'Referer': 'http://voice.ai-j.jp/voiceroid2demo_kou.swf',
}

def _urlencodefloat(v):
  return ("%s" % v).replace('.', '%2E') if isinstance(v, float) else "%s" % v

# Example request:
# Referer: http://voice.ai-j.jp/voiceroid2demo_kou.swf Content-type: application/x-www-form-urlencoded Content-length: 170 gain=&delay=&speaker%5Fpass=ai&speaker%5Fid=1207&pitch=1%2E0&speed=1%2E0&text=%E3%81%93%E3%82%93%E3%81%AB%E3%81%A1%E3%81%AF&password=aidemo&username=AIHPDemo&reqid=create

# Pitch: [0.5, 2.0], default 1.0
# Speed: [0.5, 2.0], default 1.0
def createdata(id, text, encoding='utf8', pitch=1, speed=1, gain=None, delay=None):
  """
  @param  id  int
  @param  text  unicode
  @param* encoding  str
  @param* pitch  float  [0.5, 2.0]
  @param* speed  float  [0.5, 2.0]
  @param* gain  unknown
  @param* delay  unknown
  @return  unicode  post data
  """
  if encoding and isinstance(text, unicode):
    text = text.encode(encoding, errors='ignore')
  if not text:
    return ''
  # %5F is '_', see: http://www.w3schools.com/tags/ref_urlencode.asp
  ret = "speaker%%5Fpass=ai&password=aidemo&username=AIHPDemo&reqid=create&speaker%%5Fid=%s" % id
  if pitch is not None:
    ret += "&pitch=" + _urlencodefloat(pitch)
  if speed is not None:
    ret += "&speed=" + _urlencodefloat(speed)
  if gain is not None:
    ret += "&gain=" + _urlencodefloat(gain)
  if delay is not None:
    ret += "&delay=" + _urlencodefloat(delay)
  ret += "&text=" + urlencode(text)
  return ret

RESPONSE_BEGIN = "voiceFile="
def resolveurl(data, session=requests):
  """
  @param  data  str
  @param* session  requests
  @return  unicode or None  url
  """
  try:
    r = session.post(API, data=data, headers=HEADERS)
    if r and r.ok and r.content and r.content.startswith(RESPONSE_BEGIN):
      return r.content[len(RESPONSE_BEGIN):]
  except Exception, e:
    dwarn(e)

if __name__ == '__main__':
  text = u"こんにちは"
  id = VOICES['aoi'].id
  #id = VOICES['kou'].id
  data = createdata(id, text)
  print data

  url = resolveurl(data)
  print url

# EOF
