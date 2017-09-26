# coding: utf8
# sktr.py
# 11/1/2012 jichi
import re
from functools import partial
from skdebug import dwarn

REGEX_SPECIAL_CHARS = r'()[]^$|\?!*+.'

RE_SPECIAL_CHARS = re.compile(r"[%s]" % re.escape(
  r'()[]^$|\?!*+.'
))
def contains_re_chars(text): # unicode -> bool
  return bool(RE_SPECIAL_CHARS.search(text))

# http://stackoverflow.com/questions/196345/how-to-check-if-a-string-in-python-is-in-ascii
def isascii(s):
  try: s.decode('ascii'); return True
  except UnicodeDecodeError: return False
  except Exception, e:
    dwarn(e)
    return False

def signed_ord(c):
  """Return signed char value of the character
  @param  c  char
  @return  int[-128,127]
  """
  ret = ord(c)
  return ret if ret < 128 else ret - 256

# http://stackoverflow.com/questions/2556108/how-to-replace-the-last-occurence-of-an-expression-in-a-string
def rreplace(s, old, new, count):
  """
  @param  s  unicode
  @param  old  unicode
  @param  new  unicode
  @param  count  int
  """
  if count == 1:
    left, mid, right = s.rpartition(old)
    if mid:
      return new.join((left, right))
  else:
    l = s.rsplit(old, count)
    if l:
      return new.join(l)
  return s

def findbetween(text, begin, end):
  """
  @param  text  unicode
  @param  begin  unicode
  @param  end  unicode
  @return  unicode or None
  """
  start = text.find(begin)
  if start != -1:
    start += len(begin)
    stop = text.find(end, start)
    if stop != -1:
      return text[start:stop]

def iterfindbetween(text, begin, end, limit=100):
  """
  @param  text  unicode
  @param  begin  unicode
  @param  end  unicode
  @param* limit  int
  @yield  unicode
  """
  start = text.find(begin)
  stop = 0
  count = 0
  while start != -1 and stop != -1 and count < limit:
    count += 1
    start += len(begin)
    stop = text.find(end, start)
    if stop != -1:
      yield text[start:stop]
      stop += len(end)
      start = text.find(begin, stop)

def rfindbetween(text, begin, end):
  """
  @param  text  unicode
  @param  begin  unicode
  @param  end  unicode
  @return  unicode or None
  """
  stop = text.rfind(end)
  if stop != -1:
    start = text.rfind(begin, 0, stop)
    if start != -1:
      start += len(begin)
      return text[start:stop]

def riterfindbetween(text, begin, end, limit=100):
  """
  @param  text  unicode
  @param  begin  unicode
  @param  end  unicode
  @param* limit int
  @return  unicode or None
  """
  stop = text.rfind(end)
  start = 0
  count = 0
  while stop != -1 and start != -1 and count < limit:
    count += 1
    start = text.rfind(begin, 0, stop)
    if start != -1:
      yield text[start + len(begin):stop]
      stop = text.rfind(end, 0, start)

def _multireplacer_lookup(table, match):
  """
  @param  table  {unicode fr:unicode to}
  @param  match  re.match
  """
  return table[match.group(1)]

# http://stackoverflow.com/questions/6609895/efficiently-replace-bad-characters
def multireplacer(table, flags=0, escape=False, prefix=None, suffix=None):
  """
  @param  table  {unicode fr:unicode to}
  @param* flags  re compile flags  However, re.IGNORECASE will break the dictionary
  @param* prefix  str or None
  @param* suffix  str or None
  @return  fn(text)
  """
  it = table.iterkeys() if escape else (re.escape(k) for k in table.iterkeys())
  l = sorted(it, key=len, reverse=True) # sort based on length of the string
  #l.reverse() # descendant
  pat = '(%s)' % '|'.join(l)
  if suffix:
    if escape:
      suffix = re.escape(suffix)
    pat += suffix
  if prefix:
    if escape:
      prefix = re.escape(prefix)
    pat = prefix + pat
  rx = re.compile(pat, flags)
  return partial(rx.sub,
      partial(_multireplacer_lookup, table))

def removebr(t):
  """Remove leading and trailing br
  @param  t  unicode
  @return  unicode
  """
  return t.replace('<br>', '').replace('<BR>', '')

__removeruby_rx = re.compile(r"</?ruby>|</?rb>|</?rt>|</?rp>", re.IGNORECASE)
def removeruby(t):
  """Remove leading and trailing br
  @param  t  unicode
  @return  unicode
  """
  return __removeruby_rx.sub('', t)

__stripbr_rx = re.compile(r"^(?:\s*<br>)+|(?:<br>\s*)+$", re.IGNORECASE)
def stripbr(t):
  """Remove leading and trailing br
  @param  t  unicode
  @return  unicode
  """
  return __stripbr_rx.sub('', t).strip()

def uniqbr(t, repeat=2):
  """Remove duplicate br
  @param  t  unicode
  @param* repeat  int  maximum number of repetition
  @return  unicode
  """
  pat = r"(?:\s*<br>\s*){%i,}" % repeat
  repl = "<br>" * (repeat - 1)
  return re.sub(pat, repl, t, re.IGNORECASE)

from HTMLParser import HTMLParser
_HP = HTMLParser()
# @param  t  unicode
# @return  unicode
unescapehtml = _HP.unescape

# @param  t  unicode
# @return  unicode
from cgi import escape as escapehtml

# See: http://stackoverflow.com/questions/1695183/how-to-percent-encode-url-parameters-in-python
import urllib
def urlencode(text, safe=''):
  """
  @param  text  str not unicode
  @param* safe  str  characters do not encode
  @param* encoding  str
  @param* errors  str
  @return  str not unicode
  """
  return urllib.quote(text, safe=safe) # to percentage encoding

def urldecode(text):
  """
  @param  text  str
  @param* encoding  str
  @param* errors  str
  @return  str not unicode
  """
  text = urllib.unquote(text) # from percentage encoding

def replacefun1(rx, fun1, text):
  """
  @param  rx  re
  @param  fun1  str->str
  @param  text  unicode
  @return  unicode
  """
  def replace1(m):
    return text[m.start(0):m.start(1)] + fun1(m.group(1)) + text[m.end(1):m.end(0)]
  return rx.sub(replace1, text)

_rx_link = re.compile(r'''<a [^>]*href=['"]([^'"]+?)['"]''', re.I)
def replacelinks(h, fun):
  """
  @param  h  unicode
  @param  fun  str->str
  @return  unicode
  """
  return replacefun1(_rx_link, fun, h)

_rx_img = re.compile(r'''<img[^<>]* src=['"]([^'"]+?)['"]''', re.I)
def replaceimgurls(h, fun):
  """
  @param  h  unicode
  @param  fun  str->str
  @return  unicode
  """
  return replacefun1(_rx_img, fun, h)

# Validate

# http://stackoverflow.com/questions/6701853/parentheses-pairing-issue
def checkpair(text, pair=("({[",")}]"), escape='\\'):
  """
  @param  text  unicode
  @param* pair  (unicode open, unicode close)
  @param* escape  unicode  prefix chars for escape, such as "\\" for regex
  @return  bool
  """
  pushChars, popChars = pair
  needcheck = False
  for c in text:
    if c in pushChars or c in popChars:
      needcheck = True
      break
  if not needcheck:
    return True
  if escape:
    for x in escape:
      if x in text:
        text = text.replace(x + x, '')
        for c in (pushChars + popChars):
          text = text.replace(x + c, '')
  stack = []
  for c in text:
    if c in pushChars:
      stack.append(c)
    elif c in popChars:
      if not stack:
        return False
      else:
        stackTop = stack.pop()
        balancingBracket = pushChars[popChars.index(c)]
        if stackTop != balancingBracket:
          return False
    #else:
    #  return False
  return not stack

def countleft(text, chars):
  """Count numbers of chars on the left of text
  @param  text
  @param  chars
  @return  int
  """
  if text and chars:
    for i,c in enumerate(text):
      if c not in chars:
        return i
  return 0

def countright(text, chars):
  """Count numbers of chars on the right of text
  @param  text
  @param  chars
  @return  int
  """
  if text and chars:
    for i,c in enumerate(reversed(text)):
      if c not in chars:
        return i
  return 0

if __name__ == '__main__':
  #print urlencode('hello world')
  #print multireplacer({
  #    '1': 'a',
  #    '123': 'b',
  #    })('123')

  #print replacelinks("<a href='http:/awef/' what", lambda it: "123")
  #print replaceimgurls("<img src='http:/awef/'", lambda it: "123")

  h = u'''
<img src="http://www.getchu.com/brandnew/718587/c718587charab15.jpg">
<img src="http://www.getchu.com/brandnew/718587/c718587charab15.jpg">
<img src="http://www.getchu.com/brandnew/718587/c718587charab15.jpg">
and
'''
  print replaceimgurls(h, lambda it: "123")

# EOF

# See: http://stackoverflow.com/questions/919056/python-case-insensitive-replace
#def remove(source, pattern, flags=0):
#  """
#  @param  pattern  str or None
#  @param  source  str or None
#  @param  flags  re flags
#  @return  str or ""
#  """
#  return ("" if not source or not pattern else
#      re.compile(re.escape(pattern), flags).sub(source, "") if flags else
#      source.replace(pattern, ""))

