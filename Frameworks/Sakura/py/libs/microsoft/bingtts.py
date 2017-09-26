# coding: utf8
# bingtts.py
# 10/7/2014 jichi
# Example: http://api.microsofttranslator.com/v2/http.svc/speak?appId=TB2XZbIO8A_mxFGMH5k2eh4NWJiGQHYgd9cX_fLsN3MY*&language=ja&format=audio/mp3&text=憎しみは憎しみしか生まない。

#from sakurakit.sknetio import topercentencoding
API = "http://api.microsofttranslator.com/v2/http.svc/speak"

def url(appId, text, language, format='audio/mp3'):
  """
  @param  appId  str
  @param  text  unicode
  @param  language  str
  @param* format  str
  @return  unicode
  """
  return "%s?appId=%s&language=%s&format=%s&text=%s" % (API, appId, language, format, text)

# EOF
