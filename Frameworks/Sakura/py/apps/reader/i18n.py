# coding: utf8
# i18n.py
# 12/14/2012 jichi

from datetime import datetime
from itertools import imap
from sakurakit.sktr import tr_, utr_
from windefs import winlocale
from mecabparser import mecabdef
from mytr import my, mytr_
import config, defs

## Translation

def autotr_(t):
  """
  @param  t  unicode or str
  @return  unicode
  """
  if isinstance(t, unicode):
    t = t.encode('utf8', errors='ignore')
  r = tr_(t)
  if r == t:
    r = mytr_(t)
  return r

## Names ##

LANGUAGE_NAMES = {
  'ja': "Japanese",
  'en': "English",
  'zh': "Chinese", # normalized
  'zht': "Chinese",
  'zhs': "Simplified Chinese",
  'ko': "Korean",
  'th': "Thai",
  'vi': "Vietnamese",
  'ms': "Malaysian",
  'id': "Indonesian",
  'he': "Hebrew",
  'bg': "Bulgarian",
  'sl': "Slovenian",
  #'tl': "Filipino",
  'tl': "Tagalog",
  'be': "Belarusian",
  'et': "Estonian",
  'lv': "Latvian",
  'lt': "Lithuanian",
  'ar': "Arabic",
  'cs': "Czech",
  'da': "Danish",
  'de': "German",
  'el': "Greek",
  'fi': "Finnish",
  'fr': "French",
  'hu': "Hungarian",
  'it': "Italian",
  'es': "Spanish",
  'no': "Norwegian",
  'nl': "Dutch",
  'pl': "Polish",
  'pt': "Portuguese",
  'ro': "Romanian",
  'ru': "Russian",
  'sk': "Slovak",
  'sv': "Swedish",
  'tr': "Turkish",
  'uk': "Ukrainian",
}
def language_name(lang):
  """
  @param  lang  str
  @return  unicode
  """
  return tr_(LANGUAGE_NAMES.get(lang) or "English")

def ruby_type_name(rb):
  """
  @param  rb  str
  @return  unicode
  """
  if rb in (mecabdef.RB_ROMAJI, mecabdef.RB_HIRA, mecabdef.RB_KATA):
    return utr_(rb.capitalize())
  if rb == mecabdef.RB_TR:
    return tr_("English")
  else:
    return language_name(rb)

def language_name2(lang):
  """
  @param  lang  str
  @return  unicode
  """
  if lang == 'no':
    lang = 'nb' # change Norwegian language name
  if isinstance(lang, str):
    return tr_(lang)
  if isinstance(lang, unicode):
    return utr_(lang)
  return ''

ENCODING_DESCS = {
  'shift-jis':    "%s (CP932, Shift-JIS)" % tr_("Japanese"),
  'utf-16':       u"UTF-16",
  'utf-8':        u"UTF-8",
  'big5':         "%s (CP950, Big5)" % tr_("Traditional Chinese"),
  'gbk':          "%s (CP936, GBK)" % tr_("Simplified Chinese"),
  'euc-kr':       "%s (CP949, EUC-KR)" % tr_("Korean"),
  'windows-1258': "%s (CP1258)" % tr_("Vietnamese"),
  'tis-620':      "%s (CP874, TIS-620)" % tr_("Thai"),
  'windows-1256': "%s (CP1256, ISO-8859-6)" % tr_("Arabic"),
  'windows-1255': "%s (CP1255, ISO-8859-8)" % tr_("Hebrew"),
  'windows-1254': "%s (CP1254, ISO-8859-9)" % tr_("Turkish"),
  'windows-1253': "%s (CP1253, ISO-8859-7)" % tr_("Greek"),
  'windows-1250': "%s (CP1250, ISO-8859-2)" % my.tr("Central and Eastern Europe"),
  'windows-1257': "%s (CP1257, ISO-8859-4)" % my.tr("North Europe"), # Baltic
  'windows-1251': "%s (CP1251, ISO-8859-5)" % tr_("Cyrillic"),
  'latin1':       "%s (CP1252, ISO-8859-1)" % tr_("Latin"),
}
def encoding_desc(enc):
  """
  @param  lang  str
  @return  unicode
  """
  return ENCODING_DESCS.get(enc) or enc.upper()

WIN_CHARSET_DESCS = {
  winlocale.SHIFTJIS_CHARSET:   tr_("Japanese"),
  winlocale.GB2312_CHARSET:     tr_("Simplified Chinese"),
  winlocale.CHINESEBIG5_CHARSET: tr_("Traditional Chinese"),
  winlocale.HANGUL_CHARSET:     tr_("Korean"),
  winlocale.VIETNAMESE_CHARSET: tr_("Vietnamese"),
  winlocale.THAI_CHARSET:       tr_("Thai"),
  winlocale.GREEK_CHARSET:      tr_("Greek"),
  winlocale.ARABIC_CHARSET:     tr_("Arabic"),
  winlocale.HEBREW_CHARSET:     tr_("Hebrew"),
  winlocale.TURKISH_CHARSET:    tr_("Turkish"),
  winlocale.BALTIC_CHARSET:     my.tr("North Europe"),
  winlocale.EASTEUROPE_CHARSET: my.tr("Central and Eastern Europe"),
  winlocale.RUSSIAN_CHARSET:    tr_("Cyrillic"),
  winlocale.DEFAULT_CHARSET:    "(%s)" % tr_("System default"),
}
def win_charset_desc(charset):
  """
  @param  charset  int
  @return  unicode
  """
  desc = WIN_CHARSET_DESCS.get(charset) or "(%s)" % my.tr("Unknown charSet")
  return "%s (0x%x)" % (desc, charset)

# https://msdn.microsoft.com/en-us/library/windows/desktop/dd145037%28v=vs.85%29.aspx
FONT_WEIGHT_DESCS = (
  "0. %s" % tr_("Default"), # FW_DONTCARE
  "1. Ultralight",  # FW_THIN
  "2. Light",       # FW_EXTRALIGHT, FW_ULTRALIGHT
  "3. Semilight",   # FW_LIGHT
  "4. Regular",     # FW_REGULAR, FW_NORMAL
  "5. Medium",      # FW_MEDIUM
  "6. Semibold",    # FW_SEMIBOLD, FW_DEMIBOLD
  "7. Bold",        # FW_BOLD
  "8. Ultrabold",   # FW_EXTRABOLD, FW_ULTRABOLD
  "9. Black",       # FW_HEAVY, FW_BLACK
)

def topic_type_name(type):
  """
  @param  type  str
  @return  unicode
  """
  if isinstance(type, str):
    return tr_(type)
  if isinstance(type, unicode):
    return utr_(type)
  return ''

def term_type_name(type):
  """
  @param  type  str
  @return  unicode
  """
  import dataman
  return dataman.Term.typeName(type)

TRANSLATOR_NAMES = { # [TranslatorTraits]
  'romaji': mytr_("Yomigana"),
  'bing': "Bing.com",
  'google': "Google.com",
  'lecol': mytr_("LEC Online"),
  'infoseek': "Infoseek.co.jp",
  'excite': "Excite.co.jp",
  'nifty': "@nifty.com",
  'systran': "SYSTRANet.com",
  'babylon': "Babylon.com",
  'transru': "Translate.Ru",
  'naver': "Naver.com",
  'baidu': mytr_("Baidu") + ".com",
  'youdao': mytr_("Youdao") + ".com",
  'jbeijing': mytr_("JBeijing"),
  'fastait': mytr_("FastAIT"),
  'dreye': "Dr.eye",
  'eztrans': "ezTrans XP",
  'transcat': 'TransCAT',
  'atlas': "ATLAS",
  'lec': "LEC",
  'hanviet': u"Hán Việt",
  'vtrans': "vTrans",
}
def translator_name(key): return TRANSLATOR_NAMES.get(key) or ''

GAME_CONTEXT_NAMES = {
  'scene': mytr_("Dialog"),
  'name': mytr_("Name"),
  'other': tr_("Other"),
  'window': tr_("Window"),
}
def game_context_name(key): return GAME_CONTEXT_NAMES.get(key) or ''

GENDER_NAMES = {
  'm': tr_("Male"),
  'f': tr_("Female"),
  '':  tr_("Not specified"),
}
def gender_name(g): return GENDER_NAMES.get(g) or ''

SITE_NAMES = {
  'amazon': "Amazon", #u"アマゾン",
  'digiket': "DiGiket",
  'dmm': "DMM",
  'freem': "FreeM",
  'steam': "Steam",
  'getchu': "Getchu", #u"げっちゅ屋",
  'melon': "Melon", #u"めろん",
  'gyutto': "Gyutto", #u"ギュット!",
  'dlsite': "DLsite",
  'trailers': "Trailers",
  'tokuten': "特典", #u"エロゲーム特典",
  'scape': u"批評空間",
  'erogamescape': u"批評空間",
  'holyseal': u"聖封",
  'homepage': u"公式HP",
  'wiki': tr_("Wiki"), #u"ウィキ"
}
def site_name(t): return SITE_NAMES.get(t) or ''

SCORE_NAMES = {
  'overall': mytr_("Overall"),
  'ecchi': mytr_("Ecchi"),
  'easy': mytr_("Easy"),
}
def score_name(t): return SCORE_NAMES.get(t) or ''

KEY_NAMES = {
  'mouse left': tr_("Left-click"),
  'mouse middle': tr_("Middle-click"),
  'mouse right': tr_("Right-click"),
  'Space': tr_("Space"),
  'Back': u'←', # ひだり
  'Left': u'←', # ひだり
  'Right': u'→', # みぎ
  'Up': u'↑', # うえ
  'Down': u'↓', # した
  'Prior': 'PageUp',
  'Next': 'PageDown',
  'Capital': 'Cap', #'CapsLock',
  'Escape': 'Esc',
}
def key_name(t): # str -> unicode
  return KEY_NAMES.get(t) or t.capitalize() if t else ''

def combined_key_name(t, delim='+'): # str -> unicode
  from hkman import unpackhotkey
  return delim.join(imap(key_name, unpackhotkey(t)))

#def key_from_name(t): # unicode -> str
#  for k,v in KEY_NAMES.iteritems():
#    if v == t:
#      return k
#  return t

#INV_LANGUAGE_NAMES = {v:k for k, v in LANGUAGE_NAMES.iteritems()}
#
#def language_from_name(name):
#  return INV_LANGUAGE_NAMES.get(name) or ""

def language_compatible_to(termLanguage, language):
  """
  @param  termLanguage  str  lang
  @param  language  str  lang
  """
  if termLanguage == 'ja':
    return True
  if termLanguage[:2] == language[:2]:
    return True
  if termLanguage == 'en' and config.is_latin_language(language):
    return True
  if termLanguage == 'ru' and config.is_cyrillic_language(language):
    return True
  return False

## Date time ##

WEEK_NAMES = [
  u"日",
  u"月",
  u"火",
  u"水",
  u"木",
  u"金",
  u"土",
]

def unparsedatetime(d):
  #return d.strftime("%m/%d/%Y {0} %H:%M").format(
  #    WEEK_NAMES[d.weekday()]).lstrip('0')
  return "%s/%s/%s %s %s:%s" % (
    d.month, d.day, d.year,
    WEEK_NAMES[d.weekday()],
    d.hour, #d.hour if d.hour >= 10 else '0%s' % d.hour,
    d.minute if d.minute >= 10 else '0%s' % d.minute, # pad leading zeros
  )

def unparsedate(d):
  """
  @param  sec  long
  @return  str
  """
  return "%s/%s/%s %s" % (
      d.month, d.day, d.year,
      WEEK_NAMES[d.weekday()])

def timestamp2datetime(sec):
  """
  @param  sec  long
  @return  str
  """
  return unparsedatetime(datetime.fromtimestamp(sec)) if sec else ''

def timestamp2date(sec):
  """
  @param  sec  long
  @return  str
  """
  return unparsedate(datetime.fromtimestamp(sec)) if sec else ''

def timestamp2datetimeobj(sec):
  """
  @param  sec  long
  @return  datetime
  """
  return datetime.fromtimestamp(sec)

## Threads ##

THREAD_TIPS = {
  defs.HOOK_THREAD_TYPE: my.tr("Text thread from user-defined H-code"),
  defs.CUI_THREAD_TYPE: my.tr("Text thread from Windows Non-GUI function"),
  defs.GUI_THREAD_TYPE: my.tr("Text thread from Windows GUI function"),
  defs.ENGINE_THREAD_TYPE: my.tr("Text thread from game-specific engine"),
}
def threadtip(tt):
  """
  @param  tt  int  thread type
  @return  unicode not None
  """
  return THREAD_TIPS.get(tt) or ''

## Keywords ##

TIPS = {
  u"アドベンチャー": "Adventure",
  u"シミュレーション": "Simulation",
  u"デジタルノベル": "Digital Novel",
  u"アクション": "Action",
  u"バトル": "Battle",
  u"ファンタジー": "Fantasy",
  u"ラブコメ": "Love Comedy",
  u"コメディ": "Comedy",
  u"レズ": "Lesbian",
  u"ハーレム": "Harem",
  u"ショタ": "Shota",
  u"アニメ": "Anime",
  u"アニメーション": "Animation",
  u"アンドロイド": "Android",
  u"アンソロジー": "Anthology",
  u"ウェイトレス": "Waitress",
  u"チャイナドレス": "China Dress",
  u"アイドル": "Idol",
  u"アクセサリー": "Accessories",
  u"スポーツ": "Sports",
  u"動画・アニメーション": "Animation",
  u"ミステリー": "Mystery",
  u"オリジナル": "Original",
  u"ボーイズラブ": "Boys Love",
  u"コスプレ": "Cosplay",
  u"ダンジョン": "Dungeon",
  u"ホラー": "Horror",
  u"サスペンス": "Suspense",
  u"寝取り・寝取られ": "NTR",
  u"イチオシ作品": u"一番のお勧め",
  u"けもの娘": u"獣人娘",
  u"ふたなり": u"両性具有",
}
def tip(t):
  """
  @param  t  unicode
  @return  unicode
  """
  return TIPS.get(t) #or t.replace(u"コミケ", "Comiket")

TAGS = {
  "director":   u"企画・監督",
  "writer":     u"脚本", #u"シナリオ"
  "artist":     u"原画",
  "sdartist":   u"SD原画",
  "musician":   u"音楽",
  "singer":     u"うた",
  "lyrics":     u"作詞",
  "composer":   u"作曲",
  "arranger":   u"編曲",
}
def tag(t):
  """
  @param  t  unicode
  @return  unicode
  """
  return TAGS.get(t) or t

# EOF

## Translations ##
#
#TR_TITLES_EN = {
#  '' : '', # default item
#
#  u"さん" : "-san",
#  u"さぁん" : "-san",
#  u"さーん" : "-san",
#  u"さ～ん" : "-san",
#
#  u"様" : "-sama",
#  u"さま" : "-sama",
#  u"さーま" : "-sama",
#  u"さーまー" : "-sama",
#  u"さ～ま" : "-sama",
#
#  u"殿" : "-dono",
#
#  u"君" : "-kun",
#  u"くん" : "-kun",
#  u"くーん" : "-kun",
#  u"く～ん" : "-kun",
#
#  u"ちゃん" : "-chan",
#  u"ちゃーん" : "-chan",
#  u"ちゃ～ん" : "-chan",
#
#  u"ん" : "-chan",
#
#  u"しゃん" : "-shan",
#  u"ちん" : "-chin",
#  u"ち" : "-chi",
#  u"っち" : "-chi",
#
#  u"たん" : "-tan",
#  u"たぁん" : "-tan",
#  u"たーん" : "-tan",
#  u"た～ん" : "-tan",
#
#  u"先生" : "-sensei",
#  u"せんせい" : "-sensei",
#  u"せんせ" : "-sensei",
#  u"せんせー" : "-sensei",
#  u"せんせ～" : "-sensei",
#  u"センセイ" : "-sensei",
#  u"センセ" : "-sensei",
#  u"センセー" : "-sensei",
#  u"センセ～" : "-sensei",
#
#  u"先輩" : "-senpai",
#  u"せんぱい" : "-senpai",
#  #u"せんぱーい" : "-senpai",
#  #u"せんぱ～い" : "-senpai",
#  u"センパイ" : "-senpai",
#  #u"センパーイ" : "-senpai",
#  #u"センパ～イ" : "-senpai",
#
#  u"兄" : "-nii",
#  u"にい" : "-nii",
#  u"兄ちゃん" : "-niichan",
#  u"兄様" : "-niisama",
#  u"兄さま" : "-niisama",
#  u"兄さん" : "-niisan",
#
#  u"兄貴" : "-aniki",
#  u"の兄貴" : "-aniki",
#
#  u"姉" : "-nee",
#  u"ねえ" : "-nee",
#  u"姉ちゃん" : "-neechan",
#  u"姉様" : "-neesama",
#  u"姉さま" : "-neesama",
#  u"姉さん" : "-neesan",
#  u"お姉さま" : "-oneesama",
#  u"お姉さん" : "-oneesan",
#
#  u"お嬢様" : "-sama",
#  u"お嬢さま" : "-sama",
#}
#
#TR_TITLES_ZH = {
#  '' : '', # default item
#
#  u"さん" : u"桑",
#  u"さぁん" : u"桑",
#  u"さーん" : u"桑",
#  u"さ～ん" : u"桑",
#
#  u"様" : u"撒嘛",
#  u"さま" : u"撒嘛",
#  u"さーま" : u"撒嘛",
#  u"さーまー" : u"撒嘛",
#  u"さ～ま" : u"撒嘛",
#
#  u"殿" : u"殿下",
#
#  u"君" : u"君",
#  u"くん" : u"君",
#  u"くーん" : u"君",
#  u"く～ん" : u"君",
#
#  u"ちゃん" : u"酱",
#  u"ちゃーん" : u"酱",
#  u"ちゃ～ん" : u"酱",
#
#  u"ん" : u"酱",
#
#  u"しゃん" : u"香",
#  u"ちん" : u"亲",
#  u"ち" : u"亲",
#  u"っち" : u"亲",
#
#  u"たん" : u"糖",
#  u"たぁん" : u"糖",
#  u"たーん" : u"糖",
#  u"た～ん" : u"糖",
#
#  u"先生" : u"森賽",
#  u"せんせい" : u"森賽",
#  u"せんせ" : u"森賽",
#  u"せんせー" : u"森賽",
#  u"せんせ～" : u"森賽",
#  u"センセイ" : u"森賽",
#  u"センセ" : u"森賽",
#  u"センセー" : u"森賽",
#  u"センセ～" : u"森賽",
#
#  u"先輩" : u"先輩",
#  u"せんぱい" : u"先輩",
#  #u"せんぱーい" : u"先輩",
#  #u"せんぱ～い" : u"先輩",
#  u"センパイ" : u"先輩",
#  #u"センパーイ" : u"先輩",
#  #u"センパ～イ" : u"先輩",
#
#  u"兄" : u"哥哥",
#  u"にい" : u"哥哥",
#  u"兄ちゃん" : u"泥酱",
#  u"兄さん" : u"泥桑",
#  u"兄様" : u"泥撒嘛",
#  u"兄さま" : u"泥撒嘛",
#
#  u"兄貴" : u"大哥",
#  u"の兄貴" : u"大哥",
#
#  u"姉" : u"姐",
#  u"姉ちゃん" : u"捏酱",
#  u"姉さん" :  u"捏桑",
#  u"姉様" :  u"捏撒嘛",
#  u"姉さま" : u"捏撒嘛",
#  u"お姉様" :  u"哦捏撒嘛",
#  u"お姉さま" : u"哦捏撒嘛",
#
#  u"お嬢様" : u"大小姐",
#  u"お嬢さま" : u"大小姐",
#}
#
#def tr_titles(lang):
#  if lang and lang.startswith('zh'):
#    return TR_TITLES_ZH
#  else:
#    return TR_TITLES_EN
#
