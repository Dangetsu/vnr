# coding: utf8
# baidudef.py
# 10/7/2014 jichi

# fanyi.coffee:
#   t.LANGUAGETYPES =
#     AUTO: "自动检测语言"
#     EN2ZH_CN: "英语 &raquo; 中文"
#     ZH_CN2EN: "中文 &raquo; 英语"
#     JA2ZH_CN: "日语 &raquo; 中文"
#     ZH_CN2JA: "中文 &raquo; 日语"
#     FR2ZH_CN: "法语 &raquo; 中文"
#     ZH_CN2FR: "中文 &raquo; 法语"
#     KR2ZH_CN: "韩语 &raquo; 中文"
#     ZH_CN2KR: "中文 &raquo; 韩语"
#     RU2ZH_CN: "俄语 &raquo; 中文"
#     ZH_CN2RU: "中文 &raquo; 俄语"
#     SP2ZH_CN: "西语 &raquo; 中文"
#     ZH_CN2SP: "中文 &raquo; 西语"
#YOUDAO_LANGS = {
#  'enzh': 'EN2ZH_CN',
#  'zhen': 'ZH_CN2EN',
#  'jazh': 'JA2ZH_CN',
#  'zhja': 'ZH_CN2JA',
#  'frzh': 'FR2ZH_CN',
#  'zhfr': 'ZH_CN2FR',
#  'kozh': 'KR2ZH_CN',
#  'zhko': 'ZH_CN2KR',
#  'ruzh': 'RU2ZH_CN',
#  'zhru': 'ZH_CN2RU',
#  'eszh': 'SP2ZH_CN',
#  'zhes': 'ZH_CN2SP',
#}

YD_LANGUAGES = {
  #'zh': 'ZH_CN',
  'zhs': 'ZH_CN',
  'zht': 'ZH_CN',
  'en': 'EN',
  'ja': 'JA',
  'fr': 'FR',
  'ko': 'KR',
  'ru': 'RU',
  'es': 'SP',
}

def langtype(to, fr):
  """
  @param  fr  str not None
  @param  to  str not None
  @return  str not None
  """
  to = YD_LANGUAGES.get(to)
  fr = YD_LANGUAGES.get(fr)
  if to and fr and 'ZH_CN' in (fr, to):
    return fr + '2' + to
  else:
    return 'AUTO'

def ydlang(lang): return YD_LANGUAGES.get(lang) or lang

YD_SOURCE_LANGUAGES = YD_TARGET_LANGUAGES = frozenset(YD_LANGUAGES.iterkeys())

def mt_s_langs(online=True): return YD_SOURCE_LANGUAGES
def mt_t_langs(online=True): return YD_TARGET_LANGUAGES

def mt_test_lang(to=None, fr=None, online=True):
  """
  @param* to  str  language
  @param* fr  str  language
  @param* online  bool  ignored
  return bool
  """
  return (all((
      to in YD_LANGUAGES,
      fr in YD_LANGUAGES,
      fr.startswith('zh') or to.startswith('zh')
    )) if fr and to else
    fr in YD_LANGUAGES or to in YD_LANGUAGES)

# EOF
