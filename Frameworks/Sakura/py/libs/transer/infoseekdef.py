# coding: utf8
# 2/9/2015 jichi

# According to userinfo.js:
# ja-zhs => JC
# zhs-ja => CJ
# ja-zht => JCT
# zht-ja => CJT, not CTJ!
#INFOSEEK_ENGINES = {
#  'en' : 'E',
#  'ja' : 'J',
#  'zht': 'CT',
#  'zhs': 'C',
#  'ko' : 'K',
#  'fr' : 'F',
#  'de' : 'G',
#  'it' : 'I',
#  'es' : 'S',
#  'pt' : 'P',
#  'th' : 'ATHMS',   # thai
#  'vi' : 'AVIMS',   # vietnam
#  'id' : 'AIDMS',   # indonesia
#
#  'ru' : 'E', # Russia is not supported, use English instead
#}
INFOSEEK_ENGINES = {
  'jade': 'JG',
  'jaen': 'JE',
  'jaes': 'JS',
  'jafr': 'JF',
  'jait': 'JI',
  'jako': 'JK',
  'japt': 'JP',
  'jazhs': 'JC',
  'jazht': 'JCT',

  'jath': 'JATHMS',
  'javi': 'JAVIMS',
  'jaid': 'JAIDMS',
  'thja': 'THJAMS',
  'vija': 'VIJAMS',
  'idja': 'IDJAMS',

  'deen': 'GE',
  'dees': 'GS',
  'defr': 'GF',
  'deit': 'GI',
  'deja': 'GJ',
  'deko': 'GK',
  'dept': 'GP',
  'dezhs': 'GC',
  'dezht': 'GCT',

  'ende': 'EG',
  'enes': 'ES',
  'enfr': 'EF',
  'enit': 'EI',
  'enja': 'EJ',
  'enko': 'EK',
  'enpt': 'EP',
  'enzhs': 'EC',
  'enzht': 'ECT',

  'esde': 'SG',
  'esen': 'SE',
  'esfr': 'SF',
  'esit': 'SI',
  'esja': 'SJ',
  'esko': 'SK',
  'espt': 'SP',
  'eszhs': 'SC',
  'eszht': 'SCT',

  'frde': 'FG',
  'fren': 'FE',
  'fres': 'FS',
  'frit': 'FI',
  'frja': 'FJ',
  'frko': 'FK',
  'frpt': 'FP',
  'frzhs': 'FC',
  'frzht': 'FCT',

  'itde': 'IG',
  'iten': 'IE',
  'ites': 'IS',
  'itfr': 'IF',
  'itja': 'IJ',
  'itko': 'IK',
  'itpt': 'IP',
  'itzhs': 'IC',
  'itzht': 'ICT',

  'kode': 'KG',
  'koen': 'KE',
  'koes': 'KS',
  'kofr': 'KF',
  'koit': 'KI',
  'koja': 'KJ',
  'kopt': 'KP',
  'kozhs': 'KC',
  'kozht': 'KCT',

  'ptde': 'PG',
  'pten': 'PE',
  'ptes': 'PS',
  'ptfr': 'PF',
  'ptit': 'PI',
  'ptja': 'PJ',
  'ptko': 'PK',
  'ptzhs': 'PC',
  'ptzht': 'PCT',

  'zhsde': 'CG',
  'zhsen': 'CE',
  'zhses': 'CS',
  'zhsfr': 'CF',
  'zhsit': 'CI',
  'zhsja': 'CJ',
  'zhsko': 'CK',
  'zhspt': 'CP',

  'zhtde': 'CGT',
  'zhten': 'CET',
  'zhtes': 'CST',
  'zhtfr': 'CFT',
  'zhtit': 'CIT',
  'zhtja': 'CJT',
  'zhtko': 'CKT',
  'zhtpt': 'CPT',
}

INFOSEEK_LANGUAGES = frozenset((
  'ja',
  'zhs',
  'zht',
  'ko',
  'vi',
  'th',
  'id',
  'en',
  'es',
  'de',
  'fr',
  'it',
  'pt',
))

def lang2engine(to, fr):
  """
  @param  to  unicode
  @param  fr  unicode
  @return  unicode
  """
  return INFOSEEK_ENGINES.get(fr + to) or 'JE' # from 'ja' to 'en'

def mt_s_langs(online=False): return INFOSEEK_LANGUAGES
def mt_t_langs(online=False): return INFOSEEK_LANGUAGES

def mt_test_lang(to=None, fr=None, online=True):
  """
  @param* to  str
  @param* fr  str
  @param* online  bool  ignored
  @return  bool
  """
  return ((fr + to) in INFOSEEK_ENGINES if fr and to else
      fr in INFOSEEK_LANGUAGES or
      to in INFOSEEK_LANGUAGES)

# EOF
