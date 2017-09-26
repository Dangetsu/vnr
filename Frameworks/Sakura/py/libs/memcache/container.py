# coding: utf8
# container.py
# 1/15/2013 jichi
__all__ = 'SizeLimitedDict', 'SizeLimitedList'

# Use the slower version dict is not used as the time.
# See: http://anthon.home.xs4all.nl/Python/ordereddict/
# See: https://bitbucket.org/ruamel/ordereddict
#from _ordereddict import ordereddict as OrderedDict
from collections import OrderedDict

class SizeLimitedDict(OrderedDict):
  def __init__(self, *args, **kwargs):
    super(SizeLimitedDict, self).__init__(*args, **kwargs)
    self.maxsize = 0 # int

  def onsizechanged(self):
    size = len(self)
    if size > self.maxsize:
      for i in xrange(size - self.maxsize):
        self.popitem(0)

  def setmaxsize(self, v): # int
    if self.maxsize != v:
      self.maxsize = v
      self.onsizechanged()

  def __setitem__(self, *args, **kwargs):
    """@reimp"""
    super(SizeLimitedDict, self).__setitem__(*args, **kwargs)
    if len(self) > self.maxsize:
      self.popitem(0)

  def update(self, *args, **kwargs):
    """@reimp"""
    super(SizeLimitedDict, self).update(*args, **kwargs)
    self.onsizechanged()

class SizeLimitedList(list):
  def __init__(self, *args, **kwargs):
    super(SizeLimitedList, self).__init__(*args, **kwargs)
    self.maxsize = 0 # int

  def onsizechanged(self):
    size = len(self)
    if size > self.maxsize:
      for i in xrange(size - self.maxsize):
        del self[0]

  def setmaxsize(self, v): # int
    if self.maxsize != v:
      self.maxsize = v
      self.onsizechanged()

  def extend(self, *args, **kwargs):
    """@reimp"""
    super(SizeLimitedList, self).extend(*args, **kwargs)
    self.onsizechanged()

  def append(self, *args, **kwargs):
    """@reimp"""
    super(SizeLimitedList, self).append(*args, **kwargs)
    if len(self) > self.maxsize:
      del self[0]

  def insert(self, *args, **kwargs):
    """@reimp"""
    super(SizeLimitedList, self).insert(*args, **kwargs)
    if len(self) > self.maxsize:
      del self[0]

if __name__ == '__main__':
  d = SizeLimitedDict()
  d.maxsize = 2
  d[1]='a'
  d[2]='b'
  d[3]='c'
  d[4]='d'
  print len(d)
  print d

  l = SizeLimitedList()
  l.maxsize = 2
  l.append(1)
  l.append(2)
  l.append(3)
  l.append(4)
  print len(l)
  print l

# EOF
