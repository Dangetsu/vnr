# coding: utf8
# hanzidecomp.py
# 5/6/2015 jichi

if __name__ == '__main__':
  import sys
  sys.path.append('..')

from sakurakit.skdebug import dprint, derror
from sakurakit.skstr import findbetween

class HanziDecomposer(object):
  def __init__(self):
    self.__d = _HanziDecomposer()

  def isEmpty(self):
    """
    @return  bool
    """
    return bool(self.__d.chars)

  def size(self):
    """
    @return  bool
    """
    return len(self.__d.chars)

  def clear(self): self.__d.clear()

  def loadFile(self, path):
    """
    @param  path  unicode
    @return  bool
    """
    try:
      self.__d.clear()
      self.__d.addFile(path)
      return True
    except Exception, e:
      derror(e)
      return False

  def lookup(self, ch, recursive=False):
    """
    @param  ch  unicode
    @param* recursive  bool
    @return  [unicode or list] or None
    """
    ret = self.__d.lookupChar(ch)
    if ret and recursive:
      for i,it in enumerate(ret):
        ret[i] = self.__d.lookupChar(it) or it
    return ret

class _HanziDecomposer:
  #ENCODING = 'utf32'
  ENCODING = 'utf8' # skip utf32 characters

  def __init__(self):
    self.chars = {} # {int ord:[unicode or int]}
    self.rads = [] # [[unicode or int]] reusable components

  def clear(self):
    if self.chars:
      self.chars = {}
    if self.rads:
      self.rads = []

  def lookupChar(self, ch):
    """
    @param  ch  unicode
    @return  [unicode or list] or None
    """
    ret = self.chars.get(ch)
    if ret:
      try:
        indirect = False
        for it in ret:
          if isinstance(it, int):
            indirect = True
            break
        if indirect:
          ret = list(ret)
          for i,it in enumerate(ret):
            if isinstance(it, int):
              ret[i] = self._lookupRad(it)
        return ret
      except Exception, e: derror(e)

  def _lookupRad(self, index):
    """Raise instead of return None
    @param  ch  int
    @return  [unicode or list] not None
    @raise
    """
    ret = self.rads[index]
    assert ret
    indirect = False
    for it in ret:
      if isinstance(it, int):
        indirect = True
        break
    if indirect:
      ret = list(ret)
      for i,it in enumerate(ret):
        if isinstance(it, int):
          ret[i] = self._lookupRad(it)
    return ret

  def addFile(self, path):
    """
    @param  path  unicode
    @return  bool
    @raise
    """
    import codecs
    RAD_BASE = 10000
    with codecs.open(path, 'r', self.ENCODING) as f:
      charSection = False
      for line in f:
        left, mid, right = line.partition(':')
        #if len(left) > 1 and len(left) < 5:
        #  dprint("stop at utf16 character")
        #  break
        charSection = charSection or len(left) < 5

        radicals = findbetween(right, '(', ')').split(',')
        for i,r in enumerate(radicals):
          if len(r) == 3:
            radicals[i] = r.decode('utf8')
          elif len(r) >= 5:
            radicals[i] = int(r) - RAD_BASE
          # UTF32 characters are not skipped
          #else:
          #  radicals = None
          #  break
        if radicals:
          radicals = tuple(radicals) # use tuple instead of list to significantly reduce memory usage

        if left == u'密':
          l = findbetween(right, '(', ')').split(',')

        if charSection: # character section
          #assert len(left) == 1
          self.chars[left] = radicals

        else: # radical section
          index = int(left) - RAD_BASE
          while len(self.rads) < index:
            self.rads.append(None)
          self.rads.append(radicals)

if __name__ == '__main__':
  def wait(timeout=5):
    from time import sleep
    print "sleep %s" % timeout
    sleep(timeout)

  wait()
  path = '../../../../../Dictionaries/hanzi/cjk-decomp-0.4.0.txt'
  cc = HanziDecomposer()
  print cc.loadFile(path)
  print cc.isEmpty()
  print "size:", cc.size()
  wait()

  t = u'密'
  t = u'織'
  t = u'聴'
  l = cc.lookup(t)
  print l
  if l:
    for it in l:
      print it
      if isinstance(it, list):
        for r in it:
          print r
  wait()

# EOF
