# coding: utf8
# lecdef.py
# 1/20/2015 jichi

DLL_BUFFER_SIZE = 0x2000 # output buffer size

LEC_LANGUAGES = frozenset((
  'ja',
  'en',
  'zhs', 'zht',
  'ko',
  'id',
  'ar',
  'de',
  'es',
  'fr',
  'it',
  'nl',
  'pl',
  'pt',
  'ru',
  'tr', # Turkish
  'uk', # Ukrainian
  'he', # Hebrew
  'fa', # Persian
  'tl', # Tagalog in Philippine
  'ps', # Pashto in Afghanistan
))

POWERTRANS_LANGUAGES = ( # [(str fr, str to)]
  ('ja', 'en'),
  ('en', 'ru'),
  ('ja', 'ru'),
)
POWERTRANS_SOURCE_LANGUAGES = 'en', 'ja'
POWERTRANS_TARGET_LANGUAGES = 'en', 'ru'

def mt_s_langs(online=True): return LEC_LANGUAGES if online else POWERTRANS_SOURCE_LANGUAGES
def mt_t_langs(online=True): return LEC_LANGUAGES if online else POWERTRANS_TARGET_LANGUAGES

def mt_test_lang(to=None, fr=None, online=True):
  """
  @param* to  str
  @param* fr  str
  @param* online  bool
  @return  bool
  """
  if online:
    return (not fr or fr in LEC_LANGUAGES) and (not to or to in LEC_LANGUAGES)
  else: # Offline
    return ((fr, to) in POWERTRANS_LANGUAGES if fr and to else
        fr in POWERTRANS_SOURCE_LANGUAGES or
        to in POWERTRANS_TARGET_LANGUAGES)

# EOF
