# coding: utf8
# cabocharc.py
# 6/13/2014 jichi

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import os
from sakurakit.skdebug import dwarn

def makeparserargs(**kwargs):
  """
  @param* kwargs  see cabocha --help
  @return  str not unicode
  """
  if not kwargs:
    return ''
  l = []
  for k,v in kwargs.iteritems():
    #if v:
    #if k in ('dicdir', 'rcfile', 'userdic'):
    #  v = normalizepath(v)
    #if not v:
    #  dwarn("skip path with spaces for %s" % k)
    #else:
    l.append('--%s %s' % (k, v))
  return ''.join(l).encode('sjis', errors='ignore') # TODO: Use system default encoding instead of sjis

def createparser(args=None):
  """
  @param* args
  @return  CaboCha.Parser or None
  """
  import CaboCha
  try: return CaboCha.Parser() if args is None else CaboCha.Parser(args)
  except Exception, e: dwarn(e)

PARSERS = {} # never delete
def getparser(**kwargs):
  """Parser is cached
  @param* dicdir  unicode  path
  @param* userdic  unicode  path
  @return  MeCab.Tagger or None
  """
  args = makeparserargs(**kwargs)
  ret = PARSERS.get(args)
  if not ret:
    ret = PARSERS[args] = createparser(args)
  return ret

# Environment variables

def setenvrc(path): # unicode  path to dic rcfile
  try:
    if os.name == 'nt':
      path = path.replace('/', os.path.sep)
    os.environ['CABOCHARC'] = path
  except Exception, e: dwarn(e)

def getenvrc(path): # -> unicode
  return os.environ.get('CABOCHARC')

def delenvrc():
  try: del os.environ['CABOCHARC']
  except: pass

if __name__ == '__main__':
  #rcfile = '/opt/local/etc/cabocharc'
  #rcfile = '/Users/jichi/stream/Library/Dictionaries/cabocharc/ipadic.rc'
  rcfile = '/Users/jichi/stream/Library/Dictionaries/cabocharc/unidic.rc'
  setenvrc(rcfile)
  parser = getparser()
  print parser

# EOF
