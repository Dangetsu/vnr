# coding: utf8
# systrandef.py
# 4/11/2015 jichi
#
# See: http://www.systranet.com/translate/

LANGUAGE_PAIRS = { # {str fr:[str to]}
  'ar': ('en',),
  'zh': ('en',),
  'nl': ('en', 'fr'),
  'en': ('ar', 'zh', 'nl', 'fr', 'de', 'el', 'it', 'ja', 'ko', 'pl', 'pt', 'ru', 'es', 'sv'),
  'fr': ('nl', 'en', 'de', 'el', 'it', 'pt', 'es'),
  'de': ('nl', 'fr', 'it', 'pt', 'es'),
  'el': ('en', 'fr'),
  'it': ('en', 'fr', 'de', 'pt', 'es'),
  'ja': ('en',),
  'ko': ('en',),
  'pl': ('en',),
  'pt': ('en', 'fr', 'de', 'it', 'es'),
  'ru': ('en',),
  'es': ('en', 'fr', 'de', 'it', 'pt'),
  'es': ('en',),
}

def langpair(to, fr):
  """
  @param  fr  str
  @param  to  str
  @return  str  such as ja_en
  """
  return fr[:2] + "_" + to[:2]

def mt_test_lang(to=None, fr=None, online=True):
  if fr and to:
    try: return to[:2] in LANGUAGE_PAIRS[fr[:2]]
    except: return False
  else:
    return fr and fr[:2] in LANGUAGE_PAIRS or to and to[:2] in LANGUAGE_PAIRS

# EOF
