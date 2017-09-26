# coding: utf8
# baidudef.py
# 10/7/2014 jichi

# On the page of http://fanyi.baidu.com
# window['common'] = {server: {token: 'a379632293d590555a989af5e34e80c1',lang_list: {'zh': '中文','jp': '日语','th': '泰语','fra': '法语','en': '英语','spa': '西班牙语','ko': '韩语','tr': '土耳其语','vi': '越南语','ms': '马来语','de': '德语','ru': '俄语','ir': '伊朗语','ara': '阿拉伯语','et': '爱沙尼亚语','be': '白俄罗斯语','bg': '保加利亚语','hi': '印地语','is': '冰岛语','pl': '波兰语','fa': '波斯语','da': '丹麦语','tl': '菲律宾语','fi': '芬兰语','nl': '荷兰语','ca': '加泰罗尼亚语','cs': '捷克语','hr': '克罗地亚语','lv': '拉脱维亚语','lt': '立陶宛语','ro': '罗马尼亚语','af': '南非语','no': '挪威语','pt_BR': '巴西语','pt': '葡萄牙语','sv': '瑞典语','sr': '塞尔维亚语','eo': '世界语','sk': '斯洛伐克语','sl': '斯洛文尼亚语','sw': '斯瓦希里语','uk': '乌克兰语','iw': '希伯来语','el': '希腊语','hu': '匈牙利语','hy': '亚美尼亚语','it': '意大利语','id': '印尼语','sq': '阿尔巴尼亚语','am': '阿姆哈拉语','as': '阿萨姆语','az': '阿塞拜疆语','eu': '巴斯克语','bn': '孟加拉语','bs': '波斯尼亚语','gl': '加利西亚语','ka': '格鲁吉亚语','gu': '古吉拉特语','ha': '豪萨语','ig': '伊博语','iu': '因纽特语','ga': '爱尔兰语','zu': '祖鲁语','kn': '卡纳达语','kk': '哈萨克语','ky': '吉尔吉斯语','lb': '卢森堡语','mk': '马其顿语','mt': '马耳他语','mi': '毛利语','mr': '马拉提语','ne': '尼泊尔语','or': '奥利亚语','pa': '旁遮普语','qu': '凯楚亚语','tn': '塞茨瓦纳语','si': '僧加罗语','ta': '泰米尔语','tt': '塔塔尔语','te': '泰卢固语','ur': '乌尔都语','uz': '乌兹别克语','cy': '威尔士语','yo': '约鲁巴语' },account: {user_id: '65199631',add_name: true}
# 'zh': '中文'
# 'jp': '日语'
# 'th': '泰语'
# 'fra': '法语'
# 'en': '英语'
# 'spa': '西班牙语'
# 'ko': '韩语'
# 'tr': '土耳其语'
# 'vi': '越南语'
# 'ms': '马来语'
# 'de': '德语'
# 'ru': '俄语'
# 'ir': '伊朗语'
# 'ara': '阿拉伯语'
# 'et': '爱沙尼亚语'
# 'be': '白俄罗斯语'
# 'bg': '保加利亚语'
# 'hi': '印地语'
# 'is': '冰岛语'
# 'pl': '波兰语'
# 'fa': '波斯语'
# 'da': '丹麦语'
# 'tl': '菲律宾语'
# 'fi': '芬兰语'
# 'nl': '荷兰语'
# 'ca': '加泰罗尼亚语'
# 'cs': '捷克语'
# 'hr': '克罗地亚语'
# 'lv': '拉脱维亚语'
# 'lt': '立陶宛语'
# 'ro': '罗马尼亚语'
# 'af': '南非语'
# 'no': '挪威语'
# 'pt_BR': '巴西语'
# 'pt': '葡萄牙语'
# 'sv': '瑞典语'
# 'sr': '塞尔维亚语'
# 'eo': '世界语'
# 'sk': '斯洛伐克语'
# 'sl': '斯洛文尼亚语'
# 'sw': '斯瓦希里语'
# 'uk': '乌克兰语'
# 'iw': '希伯来语'
# 'el': '希腊语'
# 'hu': '匈牙利语'
# 'hy': '亚美尼亚语'
# 'it': '意大利语'
# 'id': '印尼语'
# 'sq': '阿尔巴尼亚语'
# 'am': '阿姆哈拉语'
# 'as': '阿萨姆语'
# 'az': '阿塞拜疆语'
# 'eu': '巴斯克语'
# 'bn': '孟加拉语'
# 'bs': '波斯尼亚语'
# 'gl': '加利西亚语'
# 'ka': '格鲁吉亚语'
# 'gu': '古吉拉特语'
# 'ha': '豪萨语'
# 'ig': '伊博语'
# 'iu': '因纽特语'
# 'ga': '爱尔兰语'
# 'zu': '祖鲁语'
# 'kn': '卡纳达语'
# 'kk': '哈萨克语'
# 'ky': '吉尔吉斯语'
# 'lb': '卢森堡语'
# 'mk': '马其顿语'
# 'mt': '马耳他语'
# 'mi': '毛利语'
# 'mr': '马拉提语'
# 'ne': '尼泊尔语'
# 'or': '奥利亚语'
# 'pa': '旁遮普语'
# 'qu': '凯楚亚语'
# 'tn': '塞茨瓦纳语'
# 'si': '僧加罗语'
# 'ta': '泰米尔语'
# 'tt': '塔塔尔语'
# 'te': '泰卢固语'
# 'ur': '乌尔都语'
# 'uz': '乌兹别克语'
# 'cy': '威尔士语'
# 'yo': '约鲁巴语'
#
# Translation language pairs:
#  'zh': [
#    'en'
#    'jp'
#    'spa'
#    'fra'
#    'th'
#    'ara'
#    'kor'
#    'yue'
#    'ru'
#    'wyw'
#    'pt'
#    'de'
#    'it'
#    'nl'
#    'el'
#  ]
#  'en': [
#    'zh'
#    'jp'
#    'spa'
#    'fra'
#    'th'
#    'ara'
#    'kor'
#    'ru'
#    'pt'
#    'de'
#    'it'
#    'nl'
#    'el'
#  ]
#  'jp': [
#    'zh'
#    'en'
#    'spa'
#    'fra'
#    'th'
#    'ara'
#    'kor'
#    'ru'
#    'pt'
#    'de'
#    'it'
#    'nl'
#    'el'
#    'jpka'
#  ]
#  'th': [
#    'zh'
#    'en'
#    'jp'
#    'spa'
#    'fra'
#    'ara'
#    'kor'
#    'ru'
#    'pt'
#    'de'
#    'it'
#    'nl'
#    'el'
#  ]
#  'ara': [
#    'zh'
#    'en'
#    'jp'
#    'spa'
#    'fra'
#    'th'
#    'kor'
#    'ru'
#    'pt'
#    'de'
#    'it'
#    'nl'
#    'el'
#  ]
#  'fra': [
#    'zh'
#    'en'
#    'jp'
#    'spa'
#    'th'
#    'ara'
#    'kor'
#    'ru'
#    'pt'
#    'de'
#    'it'
#    'nl'
#    'el'
#  ]
#  'spa': [
#    'zh'
#    'en'
#    'jp'
#    'fra'
#    'th'
#    'ara'
#    'kor'
#    'ru'
#    'pt'
#    'de'
#    'it'
#    'nl'
#    'el'
#  ]
#  'kor': [
#    'zh'
#    'en'
#    'jp'
#    'spa'
#    'fra'
#    'th'
#    'ara'
#    'ru'
#    'pt'
#    'de'
#    'it'
#    'nl'
#    'el'
#  ]
#  'yue': [ 'zh' ]
#  'wyw': [ 'zh' ]
#  'ru': [
#    'zh'
#    'en'
#    'jp'
#    'spa'
#    'fra'
#    'th'
#    'ara'
#    'kor'
#    'pt'
#    'de'
#    'it'
#    'nl'
#    'el'
#  ]
#  'pt': [
#    'zh'
#    'en'
#    'jp'
#    'spa'
#    'fra'
#    'th'
#    'ara'
#    'kor'
#    'ru'
#    'de'
#    'it'
#    'nl'
#    'el'
#  ]
#  'de': [
#    'zh'
#    'en'
#    'jp'
#    'spa'
#    'fra'
#    'th'
#    'ara'
#    'kor'
#    'ru'
#    'pt'
#    'it'
#    'nl'
#    'el'
#  ]
#  'it': [
#    'zh'
#    'en'
#    'jp'
#    'spa'
#    'fra'
#    'th'
#    'ara'
#    'kor'
#    'ru'
#    'pt'
#    'de'
#    'nl'
#    'el'
#  ]
#  'el': [
#    'zh'
#    'en'
#    'jp'
#    'spa'
#    'fra'
#    'th'
#    'ara'
#    'kor'
#    'ru'
#    'pt'
#    'de'
#    'it'
#    'nl'
#  ]
#  'nl': [
#    'zh'
#    'en'
#    'jp'
#    'spa'
#    'fra'
#    'th'
#    'ara'
#    'kor'
#    'ru'
#    'pt'
#    'de'
#    'it'
#    'el'
#  ]

BD_LANGUAGES = {
  'ar': 'ara',
  'ja': 'jp',
  'ko': 'kor',
  'fr': 'fra',
  'es': 'spa',

  'zhs': 'zh',
  'zht': 'cht',
  #'zh': 'zh',

  # The same
  'en': 'en',
  'th': 'th',

  'de': 'de',
  'el': 'el', # Greek
  'it': 'it',
  'nl': 'nl',
  'pl': 'pl',
  'pt': 'pt',
  'ru': 'ru',

  'bg': 'bul', # Bulgarian
  'cs': 'cs',
  'da': 'dan',
  'et': 'est', # Estonian
  'fi': 'fin',
  'hu': 'hu',
  'ro': 'rom',
  'sl': 'slo', # Slovenian
  'sv': 'swe', # Swedish

  # Chinese variants
  'yue': 'yue', # 粤语
  'wyw': 'wyw', # 文言文

  # Japanese variants
  'kana': 'jpka', # 仮名
}
def bdlang(lang): return BD_LANGUAGES.get(lang) or lang

BD_SOURCE_LANGUAGES = BD_TARGET_LANGUAGES = frozenset(BD_LANGUAGES.iterkeys())

def mt_s_langs(online=False): return BD_SOURCE_LANGUAGES
def mt_t_langs(online=False): return BD_TARGET_LANGUAGES

def mt_test_lang(to=None, fr=None, online=True):
  """
  @param* to  str  language
  @param* fr  str  language
  @param* online  bool  ignored
  return bool
  """
  return (all((
      to in BD_LANGUAGES,
      fr in BD_LANGUAGES,
      to not in ('yue', 'wyw') or fr.startswith('zh'),
      fr not in ('yue', 'wyw') or to.startswith('zh'),
    )) if fr and to else
    fr in BD_LANGUAGES or to in BD_LANGUAGES)

def tts_test_lang(lang):
  """
  @param  lang
  return bool
  """
  return lang in BD_LANGUAGES

# EOF
