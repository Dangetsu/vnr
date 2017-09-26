# coding: utf8
# 5/2/2015 jichi

# Split consonant

C_EN = u"""
#Large
#あ:a		#い:i		#う:u		#え:e		#お:o
か:k		き:k		く:k		け:k		こ:k
さ:s		し:s		す:s		せ:s		そ:s
た:t		ち:t		つ:t		て:t		と:t
な:n		に:n		ぬ:n		ね:n		の:n
は:h		ひ:h		ふ:f		へ:h		ほ:h
ま:m		み:m		む:m		め:m		も:m
や:y				ゆ:y				よ:y
ら:r		り:r		る:r		れ:r		ろ:r
わ:w								を:w
ん:n

が:g		ぎ:g		ぐ:g		げ:g		ご:g
ざ:z		じ:j		ず:z		ぜ:z		ぞ:z
だ:d		ぢ:j		づ:z		で:d		ど:d
ば:b		び:b		ぶ:b		べ:b		ぼ:b
ぱ:p		ぴ:p		ぷ:p		ぺ:p		ぽ:p

#Small
#ぁ:a		#ぃ:i		#ぅ:u		#ぇ:e		#ぉ:o
ゃ:y				ゅ:y				ょ:y
ゎ:w
ゕ:k						ゖ:k
"""

# See: http://en.wikipedia.org/wiki/Hangul_Syllables
C_KO = u"""
#Large
#あ:ㅏ		#い:ㅣ		#う:ㅜ		#え:ㅔ		#お:ㅗ
か:ㅋ		き:k		く:k		け:k		こ:k
さ:ㅅ		し:ㅅ		す:ㅅ		せ:ㅅ		そ:ㅅ
た:ㅌ		ち:ㅌ		つ:ㅌ		て:ㅌ		と:ㅌ
な:ㄴ		に:ㄴ		ぬ:ㄴ		ね:ㄴ		の:ㄴ
は:ㅎ		ひ:ㅎ		ふ:ㅎ		へ:ㅎ		ほ:ㅎ
ま:ㅁ		み:ㅁ		む:ㅁ		め:ㅁ		も:ㅁ
#や:ㅑ				#ゆ:ㅠ				#よ:ㅛ
ら:ㄹ		り:ㄹ		る:ㄹ		れ:r		ろ:ㄹ
わ:ㅜ								を:ㅜ
ん:ㄴ

が:g		ぎ:g		ぐ:g		げ:g		ご:g
ざ:z		じ:j		ず:z		ぜ:z		ぞ:z
だ:d		ぢ:j		づ:z		で:d		ど:d
ば:b		び:b		ぶ:b		べ:b		ぼ:b
ぱ:p		ぴ:p		ぷ:p		ぺ:p		ぽ:p

#Small
#ぁ:ㅏ		#ぃ:ㅣ		#ぅ:ㅜ		#ぇ:ㅔ		#ぉ:ㅗ
#ゃ:ㅑ				#ゅ:ㅠ				#ょ:ㅛ
ゎ:ㅜ
ゕ:ㅋ						ゖ:ㅋ
"""

CONSONANT_TABLES = {
  'en': C_EN,
  'ko': C_KO,
}

def parse(s):
  """
  @param  s  unicode
  @return  {unicode key:unicode value}
  """
  ret = {}
  for it in s.split():
    if it and it[0] != '#':
      k,v = it.split(':')
      ret[k] = v
  return ret

# EOF
