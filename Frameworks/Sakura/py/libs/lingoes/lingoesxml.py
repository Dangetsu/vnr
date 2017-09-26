# coding: utf8
# lingoesxml.py
# 8/1/2014 jichi
# Utitlies to parse the XML lingoes content.

if __name__ == '__main__':
  import sys
  sys.path.append("..")

import re

# GBK Chinese-Japanese dictionary
# Sample: <C><F><H /><I><N>【ふとん】<n />[名]被褥</N></I></F></C>
_rx_zh = re.compile(ur'(?<=])[^\]<；。]+')
def zh_translate(text):
  """
  @param  text  unicode  XML
  @return  unicode or None
  """
  m = _rx_zh.search(text)
  if m:
    r = m.group()
    i = r.rfind(u"，") # use the last explanation after comma
    return r if r == -1 else r[i+1:]

if __name__ == '__main__':
  import os
  from lingoesdict import LingoesDict
  location = '/Users/jichi/Dropbox/Developer/Dictionaries/LD2/'
  if os.name == 'nt':
    location = 'C:' + location

  dic = 'GBK Japanese-Chinese Dictionary.ld2'
  ld = LingoesDict(location + dic, 'utf8')

  #t = u"布団"
  #t = u"可愛い"
  t = u"殺す"
  xml = ld.get(t)
  if xml:
    print xml
    r = zh_translate(xml)
    print r

# EOF
