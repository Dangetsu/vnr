# coding: utf8
# 2/9/2015 jichi

MT_SOURCE_LANGUAGES = 'ja',
MT_TARGET_LANGUAGES = 'zht', 'zhs', 'en', 'ko' #, 'vi', 'th', 'fr', 'es', 'ru'

def mt_s_langs(online=True): return MT_SOURCE_LANGUAGES
def mt_t_langs(online=True): return MT_TARGET_LANGUAGES

def mt_test_lang(to=None, fr=None, online=True):
  """
  @param* to  str
  @param* fr  str
  @param* online  bool  ignored
  @return  bool
  """
  return (not fr or fr in MT_SOURCE_LANGUAGES) and not to or to in MT_TARGET_LANGUAGES

# EOF
