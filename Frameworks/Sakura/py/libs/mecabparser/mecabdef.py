# coding: utf8
# mecabdef.py
# 11/9/2013 jichi

# ipadic encoding, either SHIFT-JIS or UTF-8
DICT_ENCODING = 'utf8'

# MeCab definitions
MECAB_BOS_NODE = 2 # MeCab.MECAB_BOS_NODE
MECAB_EOS_NODE = 3 # MeCab.MECAB_EOS_NODE

# CHAR_TYPE

CH_VERB = 2
CH_NOUN = 8
CH_MODIFIER = 6
CH_PUNCT = 3
CH_KATAGANA = 7
CH_MARK = 4
CH_MARK2 = 5
CH_GREEK = 9

# Ruby yomigana type
RB_KATA = 'kata'
RB_HIRA = 'hira'
RB_ROMAJI = 'romaji'
RB_RU = 'ru'
RB_UK = 'uk'
RB_EL = 'el'
RB_KO = 'ko'
RB_TH = 'th'
RB_AR = 'ar'

RB_VI = 'vi' # not implemented yet
RB_TR = 'tr' # not implemented yet

def rb_lang(ruby): # str -> str
  if ruby in (RB_KATA, RB_HIRA):
    return 'ja'
  if ruby in (RB_ROMAJI, RB_TR):
    return 'en'
  return ruby

def rb_has_space(ruby): # str -> bool
  return ruby not in (RB_HIRA, RB_KATA)
def rb_has_case(ruby): # str -> bool
  return ruby in (RB_ROMAJI, RB_RU, RB_UK, RB_EL)
def rb_is_wide(ruby): # str -> bool
  return ruby in (RB_HIRA, RB_KATA, RB_KO)
def rb_is_thin(ruby): # str -> bool
  return not rb_is_wide(ruby)
def rb_is_wide_punct(ruby): # str -> bool
  return ruby in (RB_HIRA, RB_KATA)
def rb_is_thin_punct(ruby): # str -> bool
  return not rb_is_wide_punct(ruby)

# Surface type

SURFACE_UNKNOWN = 0
SURFACE_PUNCT = 1
SURFACE_KANJI = 2
SURFACE_NUMBER = 3
SURFACE_KANA = 4

# Role type
# See: https://answers.yahoo.com/question/index?qid=20110805070212AAdpWZf
# See: https://gist.github.com/neubig/2555399
ROLE_PHRASE = 'x'
ROLE_NAME = 'm' # name
ROLE_PLACE = 'mp' # place
ROLE_NUM = 'num' # number
ROLE_NOUN = 'n' # noun
ROLE_PRONOUN = 'pn' # pronoun
ROLE_VERB = 'v' # verb
ROLE_A = 'a' # http://d.hatena.ne.jp/taos/20090701/p1
ROLE_ADN = 'adn' # adnominal, http://en.wiktionary.org/wiki/連体詞
ROLE_ADJ = 'adj' # adjective
ROLE_ADV = 'adv' # adverb
ROLE_PART = 'p' # 動詞 = particle
ROLE_AUX = 'aux' # 助動詞 = auxiliary verb
ROLE_SUFFIX = 'suf' # suffix
ROLE_PREFIX = 'pref' # prefix
ROLE_INTERJ = 'int' # interjection
ROLE_PUNCT = 'punct' # punctuation
ROLE_CONJ = 'conj' # conjunction
ROLE_MARK = 'w' # letters

ROLE_NAMES = {
  ROLE_NAME: u'人名',
  ROLE_PLACE: u'地名',
  ROLE_NOUN: u'名詞',
  ROLE_NUM: u"数詞",
  ROLE_PRONOUN: u'代名詞',
  ROLE_VERB: u'動詞',
  ROLE_A: u'形状詞',
  ROLE_ADN: u'連体詞',
  ROLE_ADJ: u'形容詞',
  ROLE_ADV: u'副詞',
  ROLE_PART: u'助詞',
  ROLE_AUX: u'助動詞',
  ROLE_SUFFIX: u'接尾辞',
  ROLE_PREFIX: u'接頭辞',
  ROLE_INTERJ: u'感動詞',
  ROLE_CONJ: u'接続詞',
  ROLE_PUNCT: u'補助記号',
  ROLE_MARK: u'記号',
}
NAME_ROLES = {v:k for k,v in ROLE_NAMES.iteritems()}
#def get_role_by_name(v):  # unicode -> unicode or None
#  return NAME_ROLES.get(v)

ROLE_NAMES_EN = {
  ROLE_NAME: "name",
  ROLE_PLACE: "place",
  ROLE_NUM: "number",
  ROLE_NOUN: "noun",
  ROLE_PRONOUN: "pronoun",
  ROLE_VERB: "verb",
  ROLE_A: "ad stem",
  ROLE_ADN: "adnominal",
  ROLE_ADJ: "adjective",
  ROLE_ADV: "adverb",
  ROLE_PART: "particle",
  ROLE_AUX: "auxiliary",
  ROLE_SUFFIX: "suffix",
  ROLE_PREFIX: "prefix",
  ROLE_INTERJ: "interjection",
  ROLE_CONJ: "conjunctions",
  ROLE_PUNCT: "punctuation",
  ROLE_MARK: "word",
}

# http://sakuradite.com/topic/816
ROLE_NAMES_KO = {
  ROLE_NAME: u"이름",
  ROLE_PLACE: u"지명",
  ROLE_NUM: u"수사",
  ROLE_NOUN: u"명사",
  ROLE_PRONOUN: u"대명사",
  ROLE_VERB: u"동사",
  ROLE_A: u"형상사",
  ROLE_ADN: u"연체사",
  ROLE_ADJ: u"형용사",
  ROLE_ADV: u"부사",
  ROLE_PART: u"조사",
  ROLE_AUX: u"조동사",
  ROLE_SUFFIX: u"접미사",
  ROLE_PREFIX: u"접두사",
  ROLE_INTERJ: u"감동사",
  ROLE_CONJ: u"접속사",
  ROLE_PUNCT: u"문장부호",
  ROLE_MARK: u"기호",
}

def role_name(v): return ROLE_NAMES.get(v) # str -> unicode or None
def role_name_en(v): return ROLE_NAMES_EN.get(v) # str -> unicode or None
def role_name_ko(v): return ROLE_NAMES_KO.get(v) # str -> unicode or None

# EOF
