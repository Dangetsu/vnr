# coding: utf8
# 2/9/2015 jichi

MT_LANGUAGES = frozenset((
  'ja',
  'en',

  'zhs',
  'zht',
  'ko',

  'fr',
  'de',
  'es',
  'it',
  'pt',
  'ru',
))

def mt_s_langs(online=False): return MT_LANGUAGES
def mt_t_langs(online=False): return MT_LANGUAGES

def mt_test_lang(to=None, fr=None, online=True):
  """
  @param* to  str
  @param* fr  str
  @param* online  bool  ignored
  @return  bool
  """
  return (all((
      fr in ('ja', 'en') or to in ('ja', 'en'),
      fr in MT_LANGUAGES,
      to in MT_LANGUAGES,
    )) if fr and to else
    fr in MT_LANGUAGES or
    to in MT_LANGUAGES)

# EOF
