# coding: utf8
# searchutil.py
# 1/16/2013 jichi

__all__ = 'lookup', 'lookupprefix'

import bisect
from itertools import islice

# https://docs.python.org/2/library/bisect.html#searching-sorted-lists
def lookup(key, pairs):
  """Locate the leftmost value exactly equal to x
  @param  key  unicode
  @param  pairs  [(unicode key, unicode value)]  sorted pairs of text and translation
  @return  matched pair or None
  """
  c = Compare(key)
  i = bisect.bisect_left(pairs, c)
  if i != len(pairs) and pairs[i][0] == key:
    return pairs[i]

#def lookupprefix(*args, **kwargs): # unicode, [(unicode fr,unicode to)] -> [pair]
#  return reversed(list(lookupprefix_r(*args, **kwargs)))

def lookupprefix(prefix, pairs): # unicode, [(unicode fr,unicode to)] -> return None or yield pair; reverse look up
  """Do binary search to get range of pairs matching the prefix.
  @param  prefix  unicode
  @param  pairs  [(unicode key, unicode value)]  sorted pairs of text and translation
  @return  None or yield matched pairs
  """
  c = PrefixCompare(prefix)
  rightindex = bisect.bisect_right(pairs, c) # int
  if rightindex > 0 and pairs[rightindex-1][0].startswith(prefix):
    i = rightindex - 2
    while i >= 0 and pairs[i][0].startswith(prefix):
      i  -= 1
    leftindex = i + 1
    #if leftIndex == rightIndex + 1
    #  yield pairs[leftindex]
    #else
    return islice(pairs, leftindex, rightindex)

class Compare:
  def __init__(self, value):
    self.value = value

  def __gt__(self, other): # unicode, pair -> bool
    """@reimp"""
    return self.value > other[0] # only compare the first element

# Only works for right search
# http://stackoverflow.com/questions/7380629/perform-a-binary-search-for-a-string-prefix-in-python
class PrefixCompare:
  def __init__(self, value):
    self.value = value

  def __lt__(self, other): # unicode, pair -> bool
    """@reimp"""
    return self.lt(other[0]) # only compare the first element

  def lt(self, other): # unicode, unicode -> bool
    if len(self.value) < len(other):
      return self.value < other[:len(self.value)]
    else:
      return self.value < other

if __name__ == '__main__':
  pairs = [
    ('a', 1),
    ('ab', 2),
    ('b', 3),
    ('bc', 4),
    ('bcd', 5),
    ('bcdawef', 6),
    ('bd', 7),
    ('cd', 8),
    ('z', 9),
  ]

  s = 'bc'
  ##t = 'd'
  s = 'bd'
  for t in lookupprefix(s, pairs):
    print t

  print lookup(s, pairs)

# EOF
