# coding: utf8
# mecabtagger.py
# 11/9/2013 jichi

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import os
from sakurakit.skdebug import dwarn
import mecabdef

# Environment variables

def setenvrc(path): # unicode  path to dic rcfile
  try:
    if os.name == 'nt':
      path = path.replace('/', os.path.sep)
    os.environ['MECABRC'] = path
  except Exception, e: dwarn(e)

def getenvrc(path): # -> unicode
  return os.environ.get('MECABRC')

def delenvrc():
  try: del os.environ['MECABRC']
  except: pass

# Helper functions

# http://stackoverflow.com/questions/10299807/mecab-path-parameters-doesnot-accept-whitespace
def normalizepath(path):
  """
  @param  path  unicode
  @return  str not unicode
  """
  if not path:
    return ''
  path = path.encode('utf8', errors='ignore') # must be ascii
  #if not os.path.exists(path):
  #  return ''
  if os.name == 'nt' and ' ' in path:
    path = path.replace('/', os.path.sep) #.lower()
    import win32api
    path = win32api.GetShortPathName(path) # eliminate spaces on the path
  return '' if ' ' in path else path # the path cannot contain spaces

def maketaggerargs(**kwargs):
  """
  @param  args  {unicode k:unicode v}
  @return  MeCab.Tagger or None
  """
  if not kwargs:
    return ''
  l = []
  for k,v in kwargs.iteritems():
    if v:
      if k in ('dicdir', 'rcfile', 'userdic'):
        v = normalizepath(v)
      if not v:
        dwarn("skip path with spaces for %s" % k)
      else:
        l.append('--%s %s' % (k, v))
  return ''.join(l)

def createtagger(args=None):
  """
  @param  args  str or None
  @return  MeCab.Tagger or None
  """
  import MeCab
  try:
    ret = MeCab.Tagger() if args is None else MeCab.Tagger(args)
    ret.parse("") # it is critical to warm up tagger
    return ret
  except Exception, e:
    dwarn(e)

# Wrapper class

class _MeCabTagger:
  def __init__(self, userdic):
    self._tagger = None
    self.userdic = userdic

  @property
  def tagger(self):
    if not self._tagger:
      args = maketaggerargs(userdic=self.userdic)
      self._tagger = createtagger(args)
    return self._tagger

class MeCabTagger(object):
  encoding = mecabdef.DICT_ENCODING

  def __init__(self, userdic=None):
    """
    @param* userdic  unicode
    """
    self.__d = _MeCabTagger(userdic)

  def userdic(self): return self.__d.userdic # -> unicode
  def setUserdic(self, v): self.__d.userdic = v

  def isValid(self): # -> bool
    return self.__d.tagger

  def iterparseToNode(self, text):
    """
    @param  text  unicode
    @yield  MeCab.Node
    """
    tagger = self.__d.tagger
    if tagger:
      if isinstance(text, unicode):
        text = text.encode(self.encoding, errors='ignore')
      if text:
        node = tagger.parseToNode(text)
        skip_stats = mecabdef.MECAB_BOS_NODE, mecabdef.MECAB_EOS_NODE
        while node:
          if node.stat not in skip_stats:
            yield node
          node = node.next

  def iterparse(self, text):
    """
    @param  text  unicode
    @yield  unicode surface, unicode feature
    """
    encoding = self.encoding
    for node in self.iterparseToNode(text):
      surface = node.surface[:node.length].decode(encoding, errors='ignore')
      feature = node.feature.decode(encoding, errors='ignore')
      #char_type = node.char_type
      yield surface, feature

if __name__ == '__main__':
  dicdir = '/opt/local/lib/mecab/dic/ipadic-utf8'
  dicdir = '/Users/jichi/opt/Visual Novel Reader/Library/Dictionaries/ipadic'
  dicdir = '/Users/jichi/src/unidic'
  dicdir = '/opt/local/lib/mecab/dic/naist-jdic-utf8'
  rcfile = '/Users/jichi/stream/Library/Dictionaries/mecabrc/ipadic.rc'
  setenvrc(rcfile)
  #tagger = gettagger(dicdir=dicdir)
  tagger = gettagger()
  print tagger

  #if os.name == 'nt' and hasattr(config, 'ENV_MECABRC'):
  #  assert os.path.exists(config.ENV_MECABRC), "mecabrc does not exist"
  #  os.putenv('MECABRC', config.ENV_MECABRC.replace('/', os.path.sep))
  #else:
  #  print "initrc:initenv: ignore mecabrc"

# EOF

#TAGGERS = {} # never delete
#def gettagger(**kwargs):
#  """Taggers are cached
#  @param* dicdir  unicode  path
#  @param* userdic  unicode  path
#  @return  MeCab.Tagger or None
#  """
#  args = maketaggerargs(**kwargs)
#  ret = TAGGERS.get(args)
#  if not ret:
#    ret = TAGGERS[args] = createtagger(args)
#  return ret
