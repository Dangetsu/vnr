# coding: utf8
# niftydef.py
# 4/11/2015 jichi

NIFTY_LANGUAGES = {
  'zhs': 'zh',
  'zht': 'tw',
  'ja': 'ja',
  'en': 'en',
  'ko': 'ko',
}

def nifty_lang(lang):
  """
  @param  lang  unicode
  @return  unicode
  """
  return NIFTY_LANGUAGES.get(lang) or 'ja'

MT_LANGUAGES = NIFTY_LANGUAGES.keys()
def mt_s_langs(online=True): return MT_LANGUAGES
def mt_t_langs(online=True): return MT_LANGUAGES

def mt_test_lang(to=None, fr=None, online=False):
  """
  @param* to  str  language
  @param* fr  str  language
  @param* online  bool  ignored
  @return  bool
  """
  if fr and to:
    return fr in NIFTY_LANGUAGES and to in NIFTY_LANGUAGES and 'ja' in (fr, to)
  else:
    return fr in NIFTY_LANGUAGES or to in NIFTY_LANGUAGES

# EOF
