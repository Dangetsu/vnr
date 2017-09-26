# coding: utf8
# hanjaconv.py
# 1/6/2015 jichi

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

from sakurakit.skclass import memoized
from sakurakit.skdebug import derror

#HANGUL_DIC_DIR = '' # to be set
#HANGUL_DIC_CONV = 'dic6.txt'

HANGUL_DIC_DIR = '.' # to be set

def setdicdir(path):
  global HANGUL_DIC_DIR
  HANGUL_DIC_DIR = path

@memoized
def hangul2hanja():
  import os
  from pyhanja import QHangulHanjaConverter
  ret = QHangulHanjaConverter()
  path = os.path.join(HANGUL_DIC_DIR, 'dic6.txt')
  if not os.path.exists(path) or not ret.loadFile(path):
    derror("failed to load dic:", path)
  return ret

@memoized
def hanja2hangul():
  import os
  from pyhanja import QHanjaHangulConverter
  ret = QHanjaHangulConverter()
  #path = os.path.join(HANGUL_DIC_DIR, HANGUL_DIC_CONV)
  path = os.path.join(HANGUL_DIC_DIR, 'dic4.txt')
  if not os.path.exists(path) or not ret.addWordDictionary(path):
    derror("failed to load word dic:", path)

  # dic1: Korean hanzi in unihan
  # dic3: Chinese hanzi converted from unihan
  # dic5: hanzi frequent in Chinese but not in unihan
  for f in 'dic1.txt', 'dic3.txt', 'dic5.txt':
    path = os.path.join(HANGUL_DIC_DIR, f)
    if not os.path.exists(path) or not ret.addCharacterDictionary(path):
      derror("failed to load char dic:", path)
  return ret

def to_hangul(text):
  """Hanja to hangul.
  @param  text  unicode
  @return  unicode
  """
  return hanja2hangul().convert(text)

def lookup_hanja_char(text):
  """Hanja to hangul.
  @param  text  unicode
  @return  unicode
  """
  if text and len(text) == 1:
    ch = hanja2hangul().lookupCharacter(ord(text[0]))
    if ch:
      return unichr(ch)
  return ''

def lookup_hanja(text):
  """Hanja to hangul.
  @param  text  unicode
  @return  unicode
  """
  return hanja2hangul().lookup(text)

def to_hanja(text):
  """Hangul to hanja.
  @param  text  unicode
  @return  unicode
  """
  return hangul2hanja().convert(text)

def to_hanja_list(text):
  """Hangul to hanja.
  @param  text  unicode
  @return  [[unicode hangul, unicode hanja]]
  """
  return hangul2hanja().parse(text)

if __name__ == '__main__':
  import os
  os.environ['PATH'] = os.path.pathsep.join((
    "../../../bin",
    "../../../../Qt/PySide",
    os.environ['PATH'],
  ))
  sys.path.append("../../../bin")
  sys.path.append("../../../../Qt/PySide")

  dic = "../../../../../Dictionaries/hangul"
  setdicdir(dic)

  # http://ko.wikipedia.org/wiki/자유_콘텐츠
  # 自由 콘텐츠는 著作權이 消滅된 퍼블릭 도메인은 勿論, 著作權이 있지만 위 基準에 따라 自由롭게 利用이 許諾된 콘텐츠도 包含한다."
  t = u"자유 콘텐츠는 저작권이 소멸된 퍼블릭 도메인은 물론, 저작권이 있지만 위 기준에 따라 자유롭게 이용이 허락된 콘텐츠도 포함한다."
  #  Supposed to be 利用이 instead of 이容易
  t = u"이용이"
  t = u"공주"
  r = to_hanja(t)

  from PySide.QtGui import *
  a = QApplication(sys.argv)
  w = QLabel(r)
  w.show()
  a.exec_()

# EOF
