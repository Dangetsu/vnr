# coding: utf8
# jaconv.py
# 12/30/2012 jichi

if __name__ == '__main__':
  import sys
  sys.path.append("..")

import re
from sakurakit.skdebug import dprint
from sakurakit.skstr import multireplacer
from unitraits.uniconv import hira2kata
import kanadef

# Global settings

OPT_NAME_MACRON = True # enable macron for English

def setopt(**kwargs):
  dprint(kwargs)
  v = kwargs.get('macron')
  if v is not None:
    global OPT_NAME_MACRON
    OPT_NAME_MACRON = v

def _lang_has_capital(lang): # str -> bool
  return lang not in ('ar', 'ko', 'th')
def _lang_is_latin(lang): # str -> bool
  return lang not in ('ko', 'th', 'ar', 'ru', 'uk', 'el')

# Cached converters

def _makeconverter(fr, to):
  """
  @param  fr  int
  @param  to  int
  @return  function or None
  """
  s = kanadef.TABLES[to]
  if fr == 'kata':
    s = hira2kata(s)
  elif fr == 'kana':
    s += '\n' + hira2kata(s)

  t = kanadef.parse(s)
  return multireplacer(t)

_CONVERTERS = {}
def _convert(text, fr, to):
  """
  @param  text  unicode
  @param  fr  int
  @param  to  int
  @return  unicode
  """
  conv = _CONVERTERS.get(fr + to)
  if not conv:
    conv = _CONVERTERS[fr + to] = _makeconverter(fr, to)
  text = conv(text)
  text = text.replace(u'ッ', u'っ')
  return text

# unicode -> unicode

def hira2en(text): return _repair_reading(_repair_en(_convert(text, 'hira', 'en')))
def kata2en(text): return _repair_reading(_repair_en(_convert(text, 'kata', 'en')))
def kana2en(text): return _repair_reading(_repair_en(_convert(text, 'kana', 'en')))

def hira2ru(text): return _repair_reading(_repair_ru(_convert(text, 'hira', 'ru')))
def kata2ru(text): return _repair_reading(_repair_ru(_convert(text, 'kata', 'ru')))
def kana2ru(text): return _repair_reading(_repair_ru(_convert(text, 'kana', 'ru')))

def hira2uk(text): return _repair_reading(_repair_uk(_convert(text, 'hira', 'uk')))
def kata2uk(text): return _repair_reading(_repair_uk(_convert(text, 'kata', 'uk')))
def kana2uk(text): return _repair_reading(_repair_uk(_convert(text, 'kana', 'uk')))

def hira2el(text): return _repair_reading(_repair_el(_convert(text, 'hira', 'el')))
def kata2el(text): return _repair_reading(_repair_el(_convert(text, 'kata', 'el')))
def kana2el(text): return _repair_reading(_repair_el(_convert(text, 'kana', 'el')))

def hira2th(text): return _repair_reading(_repair_th(_convert(text, 'hira', 'th')))
def kata2th(text): return _repair_reading(_repair_th(_convert(text, 'kata', 'th')))
def kana2th(text): return _repair_reading(_repair_th(_convert(text, 'kana', 'th')))

def hira2ko(text): return _repair_reading(_repair_ko(_convert(text, 'hira', 'ko')))
def kata2ko(text): return _repair_reading(_repair_ko(_convert(text, 'kata', 'ko')))
def kana2ko(text): return _repair_reading(_repair_ko(_convert(text, 'kana', 'ko')))

def hira2ar(text): return _repair_reading(_convert(text, 'hira', 'ar'))
def kata2ar(text): return _repair_reading(_convert(text, 'kata', 'ar'))
def kana2ar(text): return _repair_reading(_convert(text, 'kana', 'ar'))

hira2romaji = hira2en
kata2romaji = kata2en
kana2romaji = kana2en

def _repair_reading(text):
  """
  @param  text
  @return  unicode
  """
  text = text.replace(u'ー', '-')
  text = text.replace(u'っ', '-')
  return text

_re_en_tsu = re.compile(ur"っ([bcdfghjklmnprstvxz])")
def _repair_en(text): # unicode -> unicode  repair xtu
  """
  @param  text
  @return  unicode
  """
  if u'っ' in text:
    text = _re_en_tsu.sub(r'\1\1', text).replace(u'っ', u'-')
  return text

# http://en.wikipedia.org/wiki/Russian_alphabet
_ru_i_vowel = u"ауэояё" # vowel except "и"
_ru_consonant = u"бвгдзклмнпрстфхцчшщъыь"
_re_ru_i = re.compile(ur"(?<=[%s])и" % _ru_i_vowel)
_re_ru_ii = re.compile(ur"[ий](и+)")
_re_ru_z = re.compile(ur'\bз', re.UNICODE)
_re_ru_tsu = re.compile(ur"っ([%s])" % _ru_consonant)
def _repair_ru(text): # unicode -> unicode  repair xtu
  """
  @param  text
  @return  unicode
  """
  if u'っ' in text:
    text = _re_ru_tsu.sub(r'\1\1', text)
  if u'и' in text:
    text = _re_ru_i.sub(u'й', text)
    text = _re_ru_ii.sub(ur'\1й', text) # push i to the end
  if u'з' in text:
    text = _re_ru_z.sub(u'дз', text)
  return text

# http://en.wikipedia.org/wiki/Ukrainian_alphabet
_uk_i_vowel = _ru_i_vowel + u'еї' # vowel except "і"
_uk_consonant = _ru_consonant + u'ґ'
_re_macron_uk_tsu = re.compile(ur"っ([%s])" % _uk_consonant)
_re_macron_uk_i = re.compile(ur"(?<=[%s])і" % _uk_i_vowel)
_re_macron_uk_ii = re.compile(ur"[ії](і+)")
def _repair_uk(text): # unicode -> unicode  repair xtu
  """
  @param  text
  @return  unicode
  """
  if u'っ' in text:
    text = _re_macron_uk_tsu.sub(r'\1\1', text)
  if u'і' in text:
    text = _re_macron_uk_i.sub(u'ї', text)
    text = _re_macron_uk_ii.sub(ur'\1ї', text) # push i to the end
  return text

# http://en.wikipedia.org/wiki/Greek_alphabet
_el_consonant = u'βγδζθκλμνξπρτφχψω'
_re_el_tsu = re.compile(ur"っ([%s])" % _el_consonant)
def _repair_el(text): # unicode -> unicode  repair xtu
  """
  @param  text
  @return  unicode
  """
  if u'っ' in text:
    text = _re_el_tsu.sub(r'\1\1', text)
  return text

# http://en.wikipedia.org/wiki/Thai_alphabet
# Thai unicode range: U+0E00–U+0E7F
_th_b = u'(?:^|(?<![\u0e00-\u0e7f]))' # \b at the beginning
_th_e = u'(?:$|(?![\u0e00-\u0e7f]))' # \e at the beginning
_re_th = (
  (re.compile(_th_b + u'ก'), u'ค'), # k
  #(re.compile(_th_b + u'จิ'), u'ชิ'), # chi
  (re.compile(_th_b + u'ตา'), u'ทา'), # ta
  #(re.compile(_th_b + ur"ย์"), u'อิ'), # i => yi
  (re.compile(_th_b + ur"ย์"), u'อี'), # i => yi
  (re.compile(ur"คุ" + _th_e), u'ขุ'), # ku
  (re.compile(ur"า" + _th_e), u'ะ'),  # a
  (re.compile(u"คะ" + _th_e), u'กะ'), # ka (after applying a)
  (re.compile(ur"([โเ][กรตน])" + _th_e), ur'\1ะ'), # oe
)
def _repair_th(text):
  """
  @param  text
  @return  unicode
  """
  #return text
  for pat, repl in _re_th:
    text = pat.sub(repl, text)
  return text

# http://en.wikipedia.org/wiki/Hangul_Syllables
#_re_ko_tsu2 = re.compile(_ko_hangul + u'っ' + _ko_hangul)
#def _ko_tsu2_repl(m): # match -> unicode
#  t = m.group()
#  left = t[0]
#  right = t[-1]
#  from hangulconv import hangulconv
#  left_l = hangulconv.split_char(left)
#  right_l = hangulconv.split_char(right)
#
#  if left_l and right_l and len(left_l) == 2:
#    left_l = left_l[0], left_l[1], right_l[0]
#    left = hangulconv.join_char(left_l)
#    if left:
#      t = left + right
#  return t
#_re_ko_tsu1 = re.compile(u'っ' + _ko_hangul)
#def _ko_tsu1_repl(m): # match -> unicode
#  t = m.group()
#  left = t[0]
#  right = t[-1]
#  from hangulconv import hangulconv
#  right_l = hangulconv.split_char(right)
#
#  if right_l:
#    right_ch = right_l[0]
#    right_ch = hangulconv.join_consonant((right_ch, right_ch))
#    if right_ch:
#      right_l = list(right_l)
#      right_l[0] = right_ch
#      right = hangulconv.join_char(right_l)
#      t = right
#  return t
# http://en.wikipedia.org/wiki/Template:Unicode_chart_Hangul_Syllables
# http://en.wikipedia.org/wiki/Hangul_consonant_and_vowel_tables
_ko_hangul = u'[\uac00-\ud7a3]' # all 2~3 hangul syllables
_re_ko_tsu = re.compile(_ko_hangul + u'っ')
def _ko_tsu_repl(m): # match -> unicode
  t = m.group()
  left = ord(t[0])
  if (left - 0xac00) % 28 == 0:
    t = unichr(left + 19) # 19 is ㅅ
  #from hangulconv import hangulconv
  #left_l = hangulconv.split_char(left)
  #if left_l and len(left_l) == 2:
  #  left_l = left_l[0], left_l[1], u'ㅅ' #right_l[0]
  #  left = hangulconv.join_char(left_l)
  #  if left:
  #    t = left
  return t
def _repair_ko(text):
  """
  @param  text
  @return  unicode
  """
  if u'っ' in text:
    text = _re_ko_tsu.sub(_ko_tsu_repl, text)
  text = text.replace(u'っ', u'ㅅ')
  # Disabled as not quite useful
  #if u'っ' in text:
  #  text = _re_ko_tsu1.sub(_ko_tsu1_repl, text)
  return text

# Names

def kana2reading(text, lang, capital=True):
  """
  @param  text  unicode
  @param  lang  str
  @param* capital  bool
  @return  unicode or None
  """
  if lang == 'ko':
    text = kana2ko(text)
    text = text.replace(u'っ', '')
    text = text.replace(u'ッ', '')
    return text
  elif lang == 'th':
    text = text.replace(u'っ', '')
    text = text.replace(u'ッ', '')
    text = text.replace(u'おお', u'お')
    return kana2th(text)
  elif lang == 'ar':
    if u'ゆ' in text:
      text = text.replace(u'ゆう', u'ゆ')
      text = text.replace(u'ゆぅ', u'ゆ')
    return kana2ar(text)
  elif lang == 'ru':
    text = kana2ru(text)
  elif lang == 'uk':
    text = kana2uk(text)
  elif lang == 'el':
    text = kana2el(text)
  else:
    text = kana2romaji(text)
  if capital:
    text = capitalizeromaji(text)
  return text

def kana2name(text, lang, macron=None):
  """
  @param  text  unicode
  @param  lang  str
  @param* macron  bool
  @return  unicode
  """
  macron = _lang_is_latin(lang) and (OPT_NAME_MACRON if macron is None else macron)
  if macron:
    text = _convert_macron_before(text)
  text = _remove_macron(text)
  text = kana2reading(text, lang, capital=False)
  if macron:
    text = _convert_macron_after(text)
  if _lang_has_capital(lang):
    text = capitalizeromaji(text)
  return text

_re_capitalize = multireplacer({
  #' Da ': ' da ',
  ' De ': ' de ',
  ' Ha ': ' ha ',
  ' Na ': ' na ',
  ' No ': ' no ',
  ' Ni ': ' ni ',
  ' To ': ' to ',
  #' O ': ' o ',
  ' Wo ': ' wo ',
})
def capitalizeromaji(text):
  """
  @param  text  unicode
  @return  unicode
  """
  return _re_capitalize(text.title())

_macron_u_prefix = u"\
おこそとのほもよろを\
ごぞどぼぽ\
ょ\
ゅ\
"
_re_macron_u = re.compile(ur"(?<=[%s])う" % _macron_u_prefix)
_macron_o_prefix = u"とど"
_re_macron_o = re.compile(ur"(?<=[%s])お" % _macron_o_prefix)
def _remove_macron(text):
  """
  @param  text  unicode
  @return  unicode
  """
  text = text.replace(u"ー", '')
  if text and len(text) > 3 and u'う' in text:
    text = _re_macron_u.sub('', text)
  if text and len(text) > 3 and u'お' in text:
    text = _re_macron_o.sub('', text)
  return text

# http://en.wikipedia.org/wiki/Romanization_of_Japanese
# http://en.wikipedia.org/wiki/Hepburn_romanization
# http://en.wikipedia.org/wiki/Macron
#
# Use '〜' as intermediate character for long sound
def _convert_macron_before(text):
  """
  @param  text  unicode
  @return  unicode
  """
  if len(text) <= 2:
    return text
  text = text.replace(u"ー", u'〜') or text
  if u'う' in text:
    text = _re_macron_u.sub(u'〜', text)
  if u'お' in text:
    text = _re_macron_o.sub(u'〜', text)
  return text

def _make_latin_macrons():
  ret = {
    'a': u'ā',
    'e': u'ē',
    'i': u'ī',
    'o': u'ō',
    'u': u'ū',
  }
  for k,v in ret.items():
    ret[k.upper()] = v.upper()
  return ret
LATIN_MACRONS = _make_latin_macrons()
_re_macron_vowel = re.compile(u'[aeiouAEIOU]〜')
def _re_macron_vowel_repl(m):
  return LATIN_MACRONS[m.group()[0]]
def _convert_macron_after(text):
  """
  @param  text  unicode
  @return  unicode
  """
  if u'〜' not in text:
    return text
  text = _re_macron_vowel.sub(_re_macron_vowel_repl, text)
  return text.replace(u'〜', '') or text

if __name__ == '__main__':
  #t = u"ウェブサイトツール"
  #t = u"うぇぶさいとつーる"
  #t = u"わかってる"
  t = u'さくらこうじ'
  print hira2romaji(t)
  #print kata2romaji(t)
  #print kata2hira(t)
  #print hira2kata(t)
  #print kata2ko(t)
  print kana2ko(t)
  print kana2th(t)

  from jTransliterate import JapaneseTransliterator
  def test(text):
    return JapaneseTransliterator(text).transliterate_from_hrkt_to_latn()
  print test(t)

  t = u'イイズミ-ちゃん'
  print kana2ru(t) # ийдзуми-чан, supposed to be Иизуми-чан
  t = u'ぱっつぁん'
  print hira2ko(t)
  print hira2romaji(t)
  print hira2ru(t)

  t = u'みなとそふと'
  print hira2ru(t)
  t = u'ソフトクリーム'
  print kata2ru(t) # correct translation is Софуто-куриму

  # Romaji
  l = [
    (u'かわいい', u'kawaii'),
    (u'いぇす', u'yesu'),
    (u'ジャケット', u'jaketto'),
    (u'せんせい', u'sensei'),
    (u'ちゃん', u'chan'),
    (u'ちょうきょう', u'choukyou'),
    (u'ぐりぐり', u'guriguri'),
  ]
  for k,v in l:
    print k, kana2en(k), v
    assert kana2en(k) == v

  # Romaji with Macron
  l = [
    (u'さとう', u'Satō'),
    (u'りゅうくん', u'Ryūkun'),
    (u'ゆうま', u'Yuuma'),
    (u'そう', u'Sou'),
    (u'そう', u'Sou'),
  ]
  for k,v in l:
    t = kana2name(k, 'en')
    print k, t, v
    assert t == v

  # Russian
  l = [
    (u'かわいい', u'каваий'), # http://ru.wikipedia.org/wiki/каваий
    (u'じい', u'дзий'), # not sure
    (u'いぇす', u'иэсу'), # not sure
    (u'ジャケット', u'дзякэтто'),
    (u'せんせい', u'сэнсэй'),
    (u'ちゃん', u'чан'),
    (u'いえやす', u'иэясу'),
    #(u'サシャ', u'саша'), # wrong, got сася
    #(u'ちょうきょう', u'чоукёу'), # not sure
  ]
  for k,v in l:
    print k, kana2ru(k), v
    assert kana2ru(k) == v

  # Ukrainian
  l = [
    (u'くん', u'кун'),
    (u'いえやす', u'іеясу'),
    (u'ほのか', u'гонока'),
    (u'ほのっか', u'гонокка'),
    (u'かわいい', u'каваії'),
    (u'せんせい', u'сенсеї'),
    (u'れん', u'рен'),
  ]
  for k,v in l:
    print k, kana2uk(k), v
    assert kana2uk(k) == v

  # Greek
  l = [
    (u'かわいい', u'καωαιι'), # not sure how to say it
    #(u'こんと', u'κόντο'), # failed
    #(u'たろ', u'ταρό'), # failed
    #(u'やまた', u'γιαμάντα'), # failed
    # http://el.wikipedia.org/wiki/Ιαπωνική_γραφή
    (u'イロハニホヘト', u'ιροχανιχοχετο'),  # 色は匂へと
    #(u'チリヌルヲ',  u'τσιρινουρουβο'),     # 散りぬるを failed since を is translated to ωο instead of βο
    #(u'ワカヨタレソ', u'βακαγιοταρεσο'),    # 我が世誰そ failed
    (u'ツネナラム', u'τσουνεναραμου'),      # 常ならむ
    #(u'ウヰノオクヤマ', u'ουβινοοκουγιαμα'), # 有為の奥山
    (u'ケフコエテ', u'κεφουκοετε'),         # 今日越えて
    (u'アサキユメミシ', u'ασακιγιουμεμισι'), # 浅き夢見し
    #(u'ヱヒモセス', u'βεχιμοσεσου'),        # 酔ひもせす
  ]
  for k,v in l:
    print k, kana2el(k), v
    assert kana2el(k) == v

  # Korean
  l = [
    (u'しおり', u'시오리'),
    (u'いぇす', u'예스'),
    (u'しっば', u'싯바'),
    (u'ゆっき', u'윳키'),
    (u'ゆっさ', u'윳사'),
    (u'かって', u'캇테'),
    (u'って', u'ㅅ테'),
    (u'ゆりっぺ', u'유릿페'),
    (u'ゆりっっぺ', '유릿ㅅ페'),
    #(u'っさ', u'싸'), # disabled as not quite useful
  ]
  for k,v in l:
    print k, kana2ko(k), v
    assert kana2ko(k) == v
    assert kana2name(k, 'ko') == v

  # Thai
  l = [
    #(u'すず', u'ซูซุ'), fail
    #(u'すすら', u'ซึซึระ'), # fail
    #(u'すずしろ', u'ซุสึชิโระ'), # fail
    #(u'すずかけ', u'สุซึคาเคะ'), # fail because すす => すず
    #(u'いすず', u'อีซูซุ'),
    (u'ちはや', u'จิฮายะ'),
    (u'すかもり', u'สึคาโมริ'),
    (u'たにゃ', u'ทาเนีย'),
    (u'みかづき', u'มิคาซึกิ'),
    (u'つぐみ', u'สึกุมิ'),
    (u'かなり', u'คานาริ'),
    (u'ましろ', u'มาชิโระ'),
    (u'まどか', u'มาโดกะ'),
    (u'かのん', u'คาน่อน'),
    (u'まゆ', u'มายุ'),
    (u'けせん', u'เคเซน'),
    #(u'ちばな', u'ชิบานะ'), # fail because of chi
    (u'きさき', u'คิซากิ'),
    (u'みやこ', u'มิยาโกะ'),
    (u'ふじな', u'ฟุจินะ'),
    (u'ひろはら', u'ฮิโรฮาระ'),
    (u'さぎばら', u'ซาคิบาระ'),
    (u'まる', u'มารุ'),
    (u'おてんた', u'โอเท็นตะ'),
    (u'むねちか', u'มุเนะจิกะ'),
    (u'くろば', u'คุโรบะ'),
    (u'けい', u'เคย์'),
    (u'さねあき', u'ซาเนะอากิ'),
    (u'はるかぜ', u'ฮารุคาเซะ'),
    (u'きぬむら',u'คินุมุระ'),
    (u'れんな', u'เร็นนะ'),
    #(u'はさくら', u'ฮาซากุระ'), # fail because of ku
    (u'れんか', u'เร็นกะ'),
    (u'りん', u'ริน'),
    (u'みなもり', u'มินาโมริ'),
    (u'ほのか', u'โฮโนกะ'),
    (u'あやめ', u'อายาเมะ'),
    (u'たくや', u'ทาคุยะ'),
    (u'みうら', u'มิอุระ'), # http://th.wikipedia.org/wiki/เดป้าเปเป้
    (u'よしなり', u'โยชินาริ'),
    (u'とくおか', u'โทคุโอกะ'),
    (u'まえだ', u'มาเอดะ'),
    (u'ふうちゃん', u'ฟูจัง'), # http://th.wikipedia.org/wiki/รักลวงป่วนใจ
    (u'ゆうま', u'ยูมะ'),
    (u'とうこ', u'โทวโกะ'),
    #(u'つきの', u'สึคิโนะ'), # fail because of ki
    #(u'てんまく', u'เทนมาขุ'), # fail because of te
    #(u'えんにし', u'เอนิชิ'), # fail because ennishi => enishi
    #美愛: u'มิจิกะ
    #かがみ: คางามิ
    #幸和: ซาจิคาซุ
    #一悟: อิจิโกะ
    #左京: ซาเคียว
    #みずのみや: มิซุโนะมิยะ
    #冬馬: โทวมะ
  ]
  for k,v in l:
    print k, hira2th(k), v
    assert kana2th(k) == v

  # Arabic
  l = [
    (u'さくら', u'ساكورا'),
    (u'さと', u'ساتو'),
    (u'かがみ', u'كاغامي'),
    (u'かおる', u'كاورو'),
    (u'さい', u'ساي'),
    (u'さいと', u'سايتو'),
    (u'やまだ', u'يامادا'),
    (u'やまもと', u'ياماموتو'),
    (u'なかむら', u'ناكامورا'),
    (u'ふくだ', u'فوكودا'),
    (u'さと', u'ساتو'),
    (u'まつもと', u'ماتسوموتو'),
    (u'かよ', u'كايو'),
    (u'ぐれん', u'غورين'),
    (u'しんご', u'شينغو'),
    (u'すざく', u'سوزاكو'),
    (u'となり の ととろ', u'توناري نو توتورو'),
    (u'さおり', u'ساوري'),
    (u'ゆうま', u'يوما'),
    (u'かわいい', u'كاوايي'),
    (u'ちゃん', u'تشان'),
    (u'さま', u'ساما'),
    (u'シャナ', u'شانا'),
    (u'ぴこ', u'بيكو'),
    (u'ぺこ', u'بيكو'),
    (u'べこ', u'بيكو'),
    (u'ボコ', u'بوكو'),
    (u'さど', u'سادو'),
    (u'ぱぴ', u'بابي'),
    (u'かぶと', u'كابوتو'),
    (u'つばさ', u'تسوباسا'),
    (u'さすけ', u'ساسوكي'),
    (u'あゆみ', u'ايومي'),
    (u'めぐみ', u'ميغومي'),
    (u'かおる', u'كاورو'),
    (u'わだ', u'وادا'),
    (u'あべ', u'ابي'),
    #(u'えいじ', u'إيجي'), # failed, totally wrong
    #(u'ぜん', u'زن'), # failed because zen is not handled
    #(u'かな', u'قانا'), # failed because of wrong ka
  ]
  for k,v in l:
    print k, kana2name(k, 'ar'), v
    assert kana2name(k, 'ar') == v

# EOF

## See: http://pypi.python.org/pypi/jTransliterate
#
#kata2romaji = kana2romaji
#hira2romaji = kana2romaji
