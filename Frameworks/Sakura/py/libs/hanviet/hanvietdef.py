# coding: utf8
# 2/10/2015 jichi

MT_SOURCE_LANGUAGES = 'zhs', 'zht'
MT_TARGET_LANGUAGES = 'vi',

def mt_s_langs(online=False): return MT_SOURCE_LANGUAGES
def mt_t_langs(online=False): return MT_TARGET_LANGUAGES

def mt_test_lang(to=None, fr=None, online=False):
  """
  @param* to  str  language
  @param* fr  str  language
  @param* online  bool  ignored
  return bool
  """
  return (not fr or fr.startswith('zh')) and (not to or to == 'vi')

# EOF
