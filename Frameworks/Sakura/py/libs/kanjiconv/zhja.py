# coding: utf8
# zhja.py
# 9/21/2014: jichi
# See: http://www.jcdic.com/chinese_convert/index.php

#JT = dict(zip(J, T)) # {unicode:unicode}
#TJ = dict(zip(T, J)) # {unicode:unicode}
TJ = {
  # Equivalent conversion
  u"—": u"ー",

  u"誒": u"欸",
  u"內": u"内",
  u"晚": u"晩",
  u"說": u"説",
  u"悅": u"悦",
  u"蔥": u"葱",
  u"擊": u"撃",
  u"絕": u"絶",
  u"佈": u"布",
  u"幫": u"幇",
  u"雞": u"鶏",
  u"歲": u"歳",
  u"咖": u"珈",
  u"啡": u"琲",
  u"僱": u"雇",
  u"錄": u"録",
  u"莆": u"蒲",
  u"虛": u"虚",
  u"醬": u"醤",
  u"眾": u"衆",
  u"團": u"団",
  u"溫": u"温",
  u"狀": u"状",
  u"麽": u"麼",
  u"查": u"査",
  u"姬": u"姫",
  u"惠": u"恵",
  u"德": u"徳",
  u"綠": u"緑",
  u"沉": u"沈",

  # To simplified version
  #u"號": u"号",
  #u"體": u"体",
  u"遙": u"遥",

  # Wide text

  #u"你": u"ｲ尓",
  #u"妳": u"ｲ尓",
  #u"謊": u"言荒",
  #u"哪": u"ﾛ那",
  #u"啪": u"ﾛ拍",
  #u"喵": u"ﾛ苗",
  #u"咕": u"ﾛ古",
  #u"噜": u"ﾛ魯",
  #u"吵": u"ﾛ少",
  #u"瞄": u"目苗",

  #u"她": u"他",

  #u"脖": u"月孛",

  # Inequivalent conversion
  #u"呢": u"吶",
  #u"啊": u"哦",
  #u"噢": u"哦",
  #u"喲": u"哦",
  #u"喔": u"哦",
  #u"啦": u"吶",
  #u"哎": u"欸",
  #u"呃": u"額",
  #u"嗎": u"麼",

  #u"吧": u"吶",
  #u"嗯": u"恩",
  #u"噗": u"璞",
  #u"呲": u"兹",
  #u"嘟": u"都",
  #u"噥": u"農",

  #u"筷": u"快",
  #u"爸": u"粑",
  #u"桌": u"卓",
  #u"夠": u"構",

  #u"凳": u"椅", # 凳子
  #u"糰": u"団", # おにぎり
  #u"碟": u"盤", # 碟子

  #u"辦": u"做", # 办法、怎么办
}

#def zhs2ja(s): # unicode -> unicode

def zht2ja(t): # unicode -> unicode
  return ''.join((TJ.get(c) or c for c in t))

if __name__ == '__main__':
  ja = u"壹周刊:施明德說，目前藍綠惡鬥致使台灣無法變"
  zh = zht2ja(ja)
  print u"歲"== u"歳"
  print u"內"== u"内"
  print u"晚" == u"晩"
  print u"虛" == u"虚"
  print u"查" == u"査"

  from PySide.QtCore import *
  c = QTextCodec.codecForName('sjis')
  t = c.toUnicode(c.fromUnicode(zh))
  print t

# EOF
