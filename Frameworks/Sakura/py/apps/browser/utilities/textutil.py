# coding: utf8
# textutil.py
# 3/21/2014 jichi

# Manipulate browesr URL

def completeurl(url): # str -> str
  url = url.strip()
  if '://' not in url and not url.startswith('about:'):
    url = 'http://' + url
  return url

def simplifyurl(url): # str -> str
  if not url:
    return ''
  if url.startswith('http://'):
    url = url[len('http://'):]
  if url and url[-1] == '/':
    url = url[:-1]
  return url.strip()

def elidetext(t, maxsize=20):
  if len(t) <= maxsize:
    return t
  else:
    return t[:maxsize - 3] + '...'

# Manipulate text for translation

def skipemptyline(text):
  """
  @param  text  unicode
  @return  bool
  """
  return bool(text) and text != '\n'

from sakurakit import skstr
normalizepunct = skstr.multireplacer({
  u"〜": u"～",
  u"‥": u"…",
  #u"\n": u" ", # JBeijing cannot handle multiple lines
})

# EOF
