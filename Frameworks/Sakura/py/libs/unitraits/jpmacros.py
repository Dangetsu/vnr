# coding: utf8
# jpmacros.py
# 1/15/2015 jichi
if __name__ == '__main__':
  import sys
  sys.path.append('..')

import re
from sakurakit.skdebug import dwarn

# Dump from Shared Dictionary at 1/15/2014
MACROS = {
  ':bos:': ur'。？！…~～〜♪❤【】＜《（『「“',
  ':eos:': ur'。？！…~～〜♪❤【】＞》）』」”',

  ':boc:': ur'{{:bos:}}、，―─',
  ':eoc:': ur'{{:eos:}}、，―─',

  'boc': ur'(?:^|(?<=[{{:boc:}}]))',
  'eoc': ur'(?:^|(?<=[{{:eoc:}}]))',

  'bos': ur'(?:^|(?<=[{{:bos:}}]))',
  'eos': ur'(?:^|(?<=[{{:eos:}}]))',

  ':digit:': ur'0-9',
  ':alpha:': ur'a-zA-Z',
  ':alnum:': ur'{{:alpha:}}{{:digit:}}',
  ':kanji:': ur'一-龯',
  ':hira:': ur'ぁ-ゖ',
  ':kata:': ur'ァ-ヺ',
  ':kana:': ur'{{:hira:}}{{:kata:}}',

  'digit': ur'[{{:digit:}}]',
  'alpha': ur'[{{:alpha:}}]',
  'alnum': ur'[{{:alpha:}}]',
  'kanji': ur'[{{:kanji:}}]',
  'hira': ur'[{{:hira:}}]',
  'kata': ur'[{{:kata:}}]',
  'kana': ur'[{{:kana:}}]',

  '!digit': ur'[^{{:digit:}}]',
  '?!digit': ur'(?!{{digit}})',
  '?<!digit': ur'(?<!{{digit}})',
  '?=digit': ur'(?={{digit}})',
  '?<=digit': ur'(?<={{digit}})',

  '!alpha': ur'[^{{:alpha:}}]',
  '?!alpha': ur'(?!{{alpha}})',
  '?<!alpha': ur'(?<!{{alpha}})',
  '?=alpha': ur'(?={{alpha}})',
  '?<=alpha': ur'(?<={{alpha}})',

  '!alnum': ur'[^{{:alnum:}}]',
  '?!alnum': ur'(?!{{alnum}})',
  '?<!alnum': ur'(?<!{{alnum}})',
  '?=alnum': ur'(?={{alnum}})',
  '?<=alnum': ur'(?<={{alnum}})',

  '!kanji': ur'[^{{:kanji:}}]',
  '?!kanji': ur'(?!{{kanji}})',
  '?<!kanji': ur'(?<!{{kanji}})',
  '?=kanji': ur'(?={{kanji}})',
  '?<=kanji': ur'(?<={{kanji}})',

  '!hira': ur'[^{{:hira:}}]',
  '?!hira': ur'(?!{{hira}})',
  '?<!hira': ur'(?<!{{hira}})',
  '?=hira': ur'(?={{hira}})',
  '?<=hira': ur'(?<={{hira}})',

  '!kata': ur'[^{{:kata:}}]',
  '?!kata': ur'(?!{{kata}})',
  '?<!kata': ur'(?<!{{kata}})',
  '?=kata': ur'(?={{kata}})',
  '?<=kata': ur'(?<={{kata}})',

  '!kana': ur'[^{{:kana:}}]',
  '?!kana': ur'(?!{{kana}})',
  '?<!kana': ur'(?<!{{kana}})',
  '?=kana': ur'(?={{kana}})',
  '?<=kana': ur'(?<={{kana}})',
}

_RE_MACRO = re.compile(r'{{(.+?)}}')

def evalmacros(macros, limit=1000):
  """
  @param  macros  {unicode name:unicode value}
  @param* limit  int  maximum iteration count
  @return  unicode
  """
  for count in xrange(1, limit):
    dirty = False
    for pattern,text in macros.iteritems(): # not iteritems as I will modify ret
      if text and '{{' in text:
        dirty = True
        ok = False
        for m in _RE_MACRO.finditer(text):
          macro = m.group(1)
          repl = macros.get(macro)
          if repl:
            text = text.replace("{{%s}}" % macro, repl)
            ok = True
          else:
            dwarn("missing macro", macro, text)
            ok = False
            break
        if ok:
          macros[pattern] = text
        else:
          macros[pattern] = None # delete this pattern
    if not dirty:
      break
  if count == limit - 1:
    dwarn("recursive macro definition")
evalmacros(MACROS)

def getmacro(name, macros=MACROS):
  """
  @param  name  unicode
  @param* macros  {unicode name:unicode value}
  @return  unicode
  """
  return macros.get(name)

def applymacros(text, macros=MACROS):
  """
  @param  text  unicode
  @param* macros  {unicode name:unicode value}
  @return  unicode
  """
  if text and '{{' in text:
    for m in _RE_MACRO.finditer(text):
      macro = m.group(1)
      repl = macros.get(macro)
      if repl is None:
        dwarn("missing macro:", macro, text)
      else:
        text = text.replace("{{%s}}" % macro, repl)
  return text

if __name__ == '__main__':
  import re

  t = u'す、す、すみません'
  boc = getmacro('boc')
  _re_jitter = re.compile(boc + ur'([あ-んア-ヴ])(?=[、…]\1)')
  t = _re_jitter.sub('xxx', t)
  print t

# EOF
