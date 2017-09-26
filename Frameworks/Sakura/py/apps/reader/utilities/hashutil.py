# coding: utf8
# hashutil.py
# 10/30/2012 jichi

if __name__ == '__main__':
  import sys
  sys.path.append('..')
  import debug
  debug.initenv()

import re
from sakurakit import skhash
from janovp import janovutil
import defs, textutil

MD5SUM = {} # {unicode path : str hex}
def md5sum(path):
  """
  @param  path  str or unicode not None  path to file
  @param  str  cached lowercase hex string
  """
  try: return MD5SUM[path]
  except KeyError:
    ret = skhash.md5sumpath(path)
    if ret:
      MD5SUM[path] = ret
    return ret

"""
@param  str or unicode not None
@return   str
"""
urlsum = skhash.md5sumdata

#"""
#@param  s  str or unicode not None
#@return   long
#"""
#urlhash = skhash.djb2
#
#def urlhashstr(url, maxsize=32):
#  """
#  @param  url  str
#  @param  maxsize  int
#  @return  str
#  """
#  h = urlhash(url)
#  ret = hex(h)
#  if len(ret) > maxsize:
#    ret = ret[-maxsize:]
#  return ret

"""Hash raw data. (hash1)
@param  s  str or unicode not None
@param* h long or None
@return   long
"""
strhash = skhash.djb2_64

"""Backward compat for VNR alpha
@param  s  str or unicode not None
@param* h long or None
@return   long
"""
strhash_old_vnr = skhash.djb2_64_s

"""Backward compat for Zky's subs of「はつゆきさくら」.
The problem is caused by 0 values in utf16 encoding.
@param  s  str or unicode not None
@return  long
"""
strhash_old_ap = skhash.djb2_64_s_nz

_normalizetext_space = re.compile(r'\s', re.UNICODE)
def _normalizetext(t):
  """Normalize game text
  @param  t  unicode
  @return   unicode
  """
  t = _normalizetext_space.sub('', t) # Remove unicode spaces
  t = textutil.remove_illegal_text(t)
  return t

def hashtext(t, h=None):
  """Hash unicode text (hash2)
  @param  t  unicode
  @param* h long or None
  @return   long
  """
  return strhash(_normalizetext(t), h)

def hashtexts(l, h=None):
  """Hash unicode text list
  @param  l  [unicode]
  @param* h long or None
  @return   long
  """
  if len(l) == 1:
    return hashtext(l[0], h)
  else:
    for it in l:
     h = hashtext(it, h)
    return h

#def _normalizecontext(t):
"""Hash unicode text combined with context_sep
@param  t  unicode
@return   unicode
"""
_normalizecontext = janovutil.remove_text_name

def hashcontext(t, h=None):
  """Hash unicode text combined with context_sep
  @param  t  unicode
  @return   long
  """
  t = _normalizecontext(t)
  if not t:
    return 0
  return hashtext(t, h)

def hashcontexts(t):
  """Hash unicode text combined with context_sep
  @param  t  unicode
  @return   long
  """
  if not t:
    return 0
  if defs.CONTEXT_SEP not in t:
    return hashcontext(t)
  l = t.split(defs.CONTEXT_SEP)
  for i,t in enumerate(l):
    l[i] = _normalizecontext(t)
  return hashtext(''.join(l))

if __name__ == '__main__':
  print urlsum("http://www.amazon.co.jp")
  print urlsum("http://www.amazon.co.jp/")

  print hashcontext(u"1")
  print hashcontext(u"111222")
  print hashcontext(u"111||222")
  print hashtext(u"111222\n\u3000")

  print hashcontext(u"そして、そこで初めて、オレたちに近づいてくる男の姿を視認する。||「…………」")
  print hashcontext(u"そして||「…………」")
  print hashcontext(u"そして||織「…………」")
  print hashcontext(u'アスタ「なんだ、キノウ姉ちゃんもいたんだ」')
  print hashcontext(      u'「なんだ、キノウ姉ちゃんもいたんだ」')

# EOF
