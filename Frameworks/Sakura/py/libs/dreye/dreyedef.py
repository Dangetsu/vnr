# coding: utf8
# 2/9/2015

MT_LANGUAGES = 'en', 'zhs', 'zht', 'ja'

def mt_s_langs(online=False): return MT_LANGUAGES
def mt_t_langs(online=False): return MT_LANGUAGES

def mt_test_lang(to=None, fr=None, online=False):
  """
  @param* to  str  language
  @param* fr  str  language
  @param* online  bool  ignored
  @return  bool
  """
  return (not fr or fr in MT_LANGUAGES) and (not to or to in MT_LANGUAGES)

# EOF
