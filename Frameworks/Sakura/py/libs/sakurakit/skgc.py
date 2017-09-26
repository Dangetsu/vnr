# coding: utf8
# skgc.py
# 3/30/2013 jichi

#PREFIX = '_retain_'

def retain(obj):
  """
  @param  obj  any class object
  """
  try: obj.__retain_count += 1
  except AttributeError: # obj does not have attr
    obj.__retain_count = 1
    obj.__retain_instance = obj
  except TypeError: pass # obj is None

def release(obj):
  """
  @param  obj  any class object
  """
  try:
    obj.__retain_count -= 1
    if obj.__retain_count <= 0:
      del obj.__retain_count
      del obj.__retain_instance
  except (AttributeError, TypeError): pass

def retaincount(obj):
  """
  @param  obj  any class object
  @return  int
  """
  try: return obj.__retain_count
  except (AttributeError, TypeError): return 0


if __name__ == '__main__':
  class Test:
    def __init__(self): print "init:", self
    def __del__(self): print "del:",  self
  t = Test()
  t = Test()
  retain(t)
  t = Test()

# EOF
