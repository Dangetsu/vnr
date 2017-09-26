# coding: utf8
# skclass.py
# 11/3/2012 jichi

import collections, sys, weakref
from functools import wraps

## Properties ##

# See: http://stackoverflow.com/questions/9937279/can-modules-have-properties
class classproperty(property):
  """Method decorator"""
  def __init__(self, method):
    super(classproperty, self).__init__(classmethod(method))
  def __get__(self, cls, owner):
    return self.fget.__get__(None, owner)()

class staticproperty(property):
  """Method decorator"""
  def __init__(self, method):
    super(staticproperty, self).__init__(staticmethod(method))
  def __get__(self, none, owner):
    return self.fget.__get__(None, owner)()

# http://wiki.python.org/moin/PythonDecoratorLibrary#Property_Definition
def propget(func): # readonly
  """Method decorator"""
  locals = sys._getframe(1).f_locals
  name = func.__name__
  prop = locals.get(name)
  if not isinstance(prop, property):
    prop = property(func, doc=func.__doc__)
  else:
    doc = prop.__doc__ or func.__doc__
    prop = property(func, prop.fset, prop.fdel, doc)
  return prop

def propset(func): # write only
  """Method decorator"""
  locals = sys._getframe(1).f_locals
  name = func.__name__
  prop = locals.get(name)
  if not isinstance(prop, property):
    prop = property(None, func, doc=func.__doc__)
  else:
    doc = prop.__doc__ or func.__doc__
    prop = property(prop.fget, func, prop.fdel, doc)
  return prop

def propdel(func): # del only
  """Method decorator"""
  locals = sys._getframe(1).f_locals
  name = func.__name__
  prop = locals.get(name)
  if not isinstance(prop, property):
    prop = property(None, None, func, doc=func.__doc__)
  else:
    prop = property(prop.fget, prop.fset, func, prop.__doc__)
  return prop

## Caching ##

# http://wiki.python.org/moin/PythonDecoratorLibrary#Alternate_memoize_as_nested_functions
# See: pip decolib

def hash_args(*args, **kwargs):
  """
  @return  int
  """
  return (0 if not args and not kwargs else
      hash(args) if not kwargs else
      hash(sorted(kwargs.iteritems())) if not args else
      hash((args, sorted(kwargs.iteritems()))))

def memoized(func):
  """Function decorator"""
  func._memoized = {}
  @wraps(func)
  def memo(*args, **kwargs):
    h = hash_args(*args, **kwargs)
    try: return func._memoized[h]
    except KeyError:
      ret = func._memoized[h] = func(*args, **kwargs)
      return ret
  return memo

def memoizedmethod(method):
  """Method decorator"""
  #return property(memoized(method))
  @wraps(method)
  def memo(self, *args, **kwargs):
    h = hash_args(method.__name__, *args, **kwargs)
    try: return self._memoized[h]
    except KeyError: pass
    except AttributeError:
      self._memoized = {}
    ret = self._memoized[h] = method(self, *args, **kwargs)
    return ret
  return memo

#memoizedstaticmethod = memoized
#memoizedclassmethod = memoized

# This will leak memory after self is deleted
def memoizedproperty(method):
  """Method decorator"""
  return property(memoizedmethod(method))

def memoizedstaticproperty(method):
  """Method decorator"""
  return staticproperty(memoized(method))

def memoizedclassproperty(method):
  """Method decorator"""
  return classproperty(memoized(method))

def hasmemoized(func,  *args, **kwargs):
  """
  @param  func  function
  @return  bool
  """
  try: m = func._memoized
  except AttributeError: return False
  h = hash_args(*args, **kwargs)
  return h in m

def hasmemoizedmethod(obj, name, *args, **kwargs):
  """
  @param  obj  object
  @param  name  str
  @return  bool
  """
  try: m = obj._memoized
  except AttributeError: return False
  h = hash_args(name, *args, **kwargs)
  return h in m

def hasmemoizedproperty(obj, name):
  return hasmemoizedmethod(obj, name)

def memoized_filter(f):
  """Return function decorator
  @param  f  take return value, and return bool
  @return  function declarator
  """
  def memoizer(func):
    func._memoized = {}
    @wraps(func)
    def memo(*args, **kwargs):
      h = hash_args(*args, **kwargs)
      try: return func._memoized[h]
      except KeyError:
        ret = func(*args, **kwargs)
        if f(ret):
          func._memoized[h] = ret
        return ret
  return memoizer

# This will leak memory after self is deleted
def memoizedmethod_filter(f):
  """Return function decorator
  @param  f  take return value, and return bool
  @return  function declarator
  """
  def memoizer(method):
    """Method decorator"""
    #return property(memoized(method))
    @wraps(method)
    def memo(self, *args, **kwargs):
      h = hash_args(method.__name__, *args, **kwargs)
      try: return self._memoized[h]
      except KeyError: pass
      except AttributeError:
        self._memoized = {}
      ret = method(self, *args, **kwargs)
      if f(ret):
        self._memoized[h] = ret
      return ret
    return memo
  return memoizer

## Coding convention ##

# Similar to Q_DECLARE_PUBLIC/Q_DECLARE_PRIVATE
def Q_Q(cls):
  """Class decorator
  @param  cls  any class, but object preferred
  """
  cls.q = property(lambda self: self.qref())

  try:
    old_init = cls.__init__
    @wraps(old_init)
    def init(*args, **kwargs):
      #assert len(args) >= 2, "the first arguments must be self, q"
      self, q = args[:2]
      self.qref = weakref.ref(q)

      try: old_init(*args, **kwargs)
      except TypeError:
        #assert(len(args) == 2)
        #assert(len(kwargs) == 0)
        old_init(self)
      #old_init(*args, **kwargs)

  except AttributeError:
    def init(self, q): self.qref = weakref.ref(q)

  cls.__init__ = init

  return cls

if __name__ == '__main__':

  def test_qt():
    from PySide.QtCore import QObject

    @Q_Q
    class _A(object):
      def __init__(self, q):
        pass

      def __del__(self):
        print "del B"

    class A(QObject):
      def __init__(self):
        super(A, self).__init__()
        self.__d = _A(self)

      def __del__(self):
        print "del A"

    a = A()
    b = QObject()
    #b.setParent(a)
    a = 0


  def test_mem():
    class X(object):
      def __del__(self):
        print "del X"

    class Y(object):
      def __del__(self):
        print "del Y"
      @memoizedproperty
      def x(self): return X()

    y = Y()
    y.x
    y = None

  test_mem()

  print "exit"

# EOF

#class cached_property(object):
#  '''Decorator for read-only properties evaluated only once within TTL period.
#
#  It can be used to created a cached property like this::
#
#    import random
#
#    # the class containing the property must be a new-style class
#    class MyClass(object):
#      # create property whose value is cached for ten minutes
#      @cached_property(ttl=600)
#      def randint(self):
#        # will only be evaluated every 10 min. at maximum.
#        return random.randint(0, 100)
#
#  The value is cached  in the '_cache' attribute of the object instance that
#  has the property getter method wrapped by this decorator. The '_cache'
#  attribute value is a dictionary which has a key for every property of the
#  object which is wrapped by this decorator. Each entry in the cache is
#  created only when the property is accessed for the first time and is a
#  two-element tuple with the last computed property value and the last time
#  it was updated in seconds since the epoch.
#
#  The default time-to-live (TTL) is 300 seconds (5 minutes). Set the TTL to
#  zero for the cached value to never expire.
#
#  To expire a cached property value manually just do::
#
#    del instance._cache[<property name>]
#
#  '''
#  def __init__(self, ttl=300):
#    self.ttl = ttl
#
#  def __call__(self, fget, doc=None):
#    self.fget = fget
#    self.__doc__ = doc or fget.__doc__
#    self.__name__ = fget.__name__
#    self.__module__ = fget.__module__
#    return self
#
#  def __get__(self, inst, owner):
#    now = time.time()
#    try:
#      value, last_update = inst._cache[self.__name__]
#      if self.ttl > 0 and now - last_update > self.ttl:
#        raise AttributeError
#    except (KeyError, AttributeError):
#      value = self.fget(inst)
#      try:
#        cache = inst._cache
#      except AttributeError:
#        cache = inst._cache = {}
#      cache[self.__name__] = (value, now)
#    return value

