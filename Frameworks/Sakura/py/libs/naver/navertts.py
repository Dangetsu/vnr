# coding: utf8
# navertts.py
# 1/22/2015 jichi
# Example:
# http://translate.naver.com/#/ja/ko/こんにちは
# http://tts.naver.com/tts/mp3ttsV1.cgi?spk_id=302&text_fmt=0&pitch=100&volume=100&speed=80&wrapper=0&enc=0&text=こんにちは

#from sakurakit.sknetio import topercentencoding
API = "http://api.microsofttranslator.com/v2/http.svc/speak"
from sakurakit.sknetio import topercentencoding

LANGUAGE_SPEAKERS = { # str language, str gender : int speakerId, str host
  ('ko', 'f'): (10, "tts.naver.com"),
  ('en', 'f'): (100, "tts.naver.com"),
  ('zh', 'f'): (251, "tts.cndic.naver.com"),
  ('ja', 'm'): (301, "tts.naver.com"),
  ('ja', 'f'): (302, "tts.naver.com"),
}

def url(text, language, gender='f', pitch=100, volume=100, speed=90, encoding=''): # disable escape by default
  """
  @param  text  unicode
  @param  language  str
  @param  gender  'f' or 'm'
  @param* pitch  int
  @param* volume  int
  @param* speed  int
  @param* encoding  str
  @return  unicode
  """
  config = LANGUAGE_SPEAKERS.get((language[:2], gender or 'f')) # female by default
  if not config:
    return ''
  speakerId, host = config
  #if rate != 1:
  #  speed = int(speed * rate)
  if encoding:
    text = topercentencoding(text, encoding)
  return "http://%s/tts/mp3ttsV1.cgi?spk_id=%s&text_fmt=0&pitch=%s&volume=%s&speed=%s&wrapper=0&enc=0&text=%s" % (host, speakerId, pitch, volume, speed, text)

# EOF
