# coding: utf8
# googledef.py
# 11/2/2014 jichi

# See: http://msdn.microsoft.com/en-us/library/hh456380.aspx
LANG_LOCALES = {
  'zht': 'zh-TW',
  'zhs': 'zh-CN',
}
def lang2locale(lang):
  """
  @param  lang  unicode
  @return  unicode
  """
  return LANG_LOCALES.get(lang) or lang

def mt_test_lang(to, fr, online=True): return True # str, str -> bool # all languages are supported
def tts_test_lang(lang): return True # str -> bool # all languages are supported

# EOF
