# coding: utf8
# babylondef.py
# 4/11/2015 jichi

# See: http://translation.babylon.com/japanese/to-english/
# <option value="0">English</option><option value="1">French</option><option value="2">Italian</option><option value="6">German</option><option value="5">Portuguese</option><option value="3">Spanish</option><option value="SEPERATOR" disabled="disabled">--------------</option><option value="15">Arabic</option><option value="99">Catalan</option><option value="344">Castilian</option><option value="31">Czech</option><option value="10">Chinese (s)</option><option value="9">Chinese (t)</option><option value="43">Danish</option><option value="11">Greek</option><option value="14">Hebrew</option><option value="60">Hindi</option><option value="30">Hungarian</option><option value="51">Persian</option><option value="8" selected="selected" >Japanese</option><option value="12">Korean</option><option value="4">Dutch</option><option value="46">Norwegian</option><option value="29">Polish</option><option value="47">Romanian</option><option value="7">Russian</option><option value="48">Swedish</option><option value="13">Turkish</option><option value="16">Thai</option><option value="49">Ukrainian</option><option value="39">Urdu</option>                        </select>

LANGUAGES = {
  'en': 0,  # English
  'fr': 1,  # French
  'it': 2,  # Italian
  'es': 3,  # Spanish
  'nl': 4,  # Dutch
  'pt': 5,  # Portuguese
  'de': 6,  # German
  'ru': 7,  # Russian
  'ja': 8,  # Japanese
  'zht': 9, # Translational Chinese
  'zhs': 10, # Simplified Chinese
  'el': 11, # Greek
  'ko': 12, # Korean
  'tr': 13, # Turkish
  'he': 14, # Hebrew
  'ar': 15, # Arabic
  'th': 16, # Thai
  'pl': 29, # Polish
  'hu': 30, # Hungarian
  'cs': 31, # Czech
  'ur': 39, # Urdu
  'da': 43, # Danish
  'no': 46, # Norwegian
  'ro': 47, # Romanian
  'sv': 48, # Swedish
  'uk': 49, # Ukrainian
  'fa': 51, # Persian
  'hi': 60, # Hindi
  'ca': 99, # Catalan
}
def langid(lang):
  """
  @param  lang  str
  @return  int
  """
  return LANGUAGES.get(lang) or 0 # default to 0=English

MT_SOURCE_LANGUAGES = MT_TARGET_LANGUAGES = frozenset(LANGUAGES.iterkeys())
def mt_s_langs(online=True): return MT_SOURCE_LANGUAGES
def mt_t_langs(online=True): return MT_TARGET_LANGUAGES

def langpair(to, fr):
  """
  @param  to  str
  @param  fr  str
  @return  str  such as "8|0"
  """
  return "%s|%s" % (langid(fr), langid(to))

def mt_test_lang(to=None, fr=None, online=True):
  return fr in LANGUAGES and to in LANGUAGES if fr and to else fr in LANGUAGES or to in LANGUAGES

# EOF
