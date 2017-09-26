# coding: utf8
# 2/9/2015 jichi
# See: http://translate.naver.com

TTS_LANGUAGES = frozenset((
  'en', 'zh', 'ja', 'ko',
))

MT_LANGUAGES = { # {str fr:[str to]}
  'ko': ('en', 'ja', 'zhs', 'zht'),
  'en': ('ko', 'pt', 'id', 'th'),
  'ja': ('ko',),
  'zhs': ('ko',),
  'zht': ('ko',),
  'es': ('en',),
  'pt': ('en',),
  'id': ('en',),
  'th': ('en',),
}

MT_SOURCE_LANGUAGES = MT_TARGET_LANGUAGES = frozenset(MT_LANGUAGES.iterkeys())

def mt_s_langs(online=True): return MT_SOURCE_LANGUAGES
def mt_t_langs(online=True): return MT_TARGET_LANGUAGES

def tts_test_lang(lang):
  """
  @param  lang  str
  @return  bool
  """
  return lang[:2] in TTS_LANGUAGES

def mt_test_lang(to=None, fr=None, online=True):
  """
  @param* to  str
  @param* fr  str
  @param* online  bool  ignored
  @return  bool  ignored
  """
  if fr and to:
    try: return to[:2] in MT_LANGUAGES[fr[:2]]
    except: return False
  else:
    return fr in MT_LANGUAGES or to in MT_LANGUAGES

# EOF
