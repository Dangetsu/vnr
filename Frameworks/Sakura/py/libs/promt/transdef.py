# coding: utf8
# 2/9/2015 jichi
# See: http://online-translator.com
# See: http://translate.ru

MT_LANGUAGES = { # {str fr:[str to]}
  'ru': (      'en', 'de', 'fr', 'es', 'it', 'pt', 'ja', 'fi'),
  'en': ('ru',       'de', 'fr', 'es', 'it', 'pt', 'ja'),
  'de': ('ru', 'en',       'fr', 'es', 'it', 'pt'),
  'fr': ('ru', 'en', 'de',       'es'),
  'es': ('ru', 'en', 'de', 'fr'),
  'it': ('ru', 'en', 'de'),
  'pt': ('ru', 'en', 'de'),
  'ja': ('ru', 'en'),
  'fi': ('ru',), # Finn
}

MT_SOURCE_LANGUAGES = MT_TARGET_LANGUAGES = frozenset(MT_LANGUAGES.keys())

def mt_s_langs(online=True): return MT_SOURCE_LANGUAGES
def mt_t_langs(online=True): return MT_TARGET_LANGUAGES

def mt_test_lang(to=None, fr=None, online=True):
  """
  @param* to  str
  @param* fr  str
  @param* online  bool  ignored
  @return  bool
  """
  if fr and to:
    try: return to in MT_LANGUAGES[fr]
    except: return False
  else:
    return fr in MT_LANGUAGES or to in MT_LANGUAGES

# EOF
