# coding: utf8
# skmeta.py
# 1/6/2013 jichi

from functools import partial
from skclass import memoized
from skdebug import dwarn

# http://code.activestate.com/recipes/81732-dynamically-added-methods-to-a-class/
class setmethod:

  def __init__(self, method, target, name=None):
    self.target = target
    self.method = method
    setattr(obj, name or method.__name__, self)

  def __call__(self, *args, **kwargs):
    nargs = [self.target]
    if args:
      nargs.extend(args)
    return apply(self.method, nargs, kwargs)

class _SkPropertyBinding:
  def __init__(self):
    self.properties = [] # [(obj, pty)]

  def setValue(self, value):
    for obj, pty in self.properties:
      try:
        val = getattr(obj, pty)
        if value != val:
          setattr(obj, pty, value)
      except AttributeError: pass

class SkPropertyBinding(object):
  def __init__(self):
    self.__d = _SkPropertyBinding()

  def isEmpty(self):
    return not self.__d.properties

  def contains(self, obj, pty):
    return (obj, pty) in self.__d.properties

  def add(self, obj, pty):
    self.__d.properties.append((obj, pty))

  def bind(self):
    for obj, pty in self.__d.properties:
      try:
        val = getattr(obj, pty)
        valChanged = getattr(obj, pty + 'Changed')
        obj.destroyed.connect(partial(self.removeObject, obj))
        valChanged.connect(self.__d.setValue)
      except AttributeError:
        dwarn("failed to bind properties", obj, val)

  def removeObject(self, obj):
    d = self.__d
    if d.properties:
      d.properties = [it for it in d.properties if it.obj is not obj]

  def unbind(self):
    if self.__d.properties:
      self.__d.properties.clear()

class _SkPropertyBinder: pass
class SkPropertyBinder(object):
  def __init__(self):
    d = self.__d = _SkPropertyBinder()
    d.bindings = [] # [SkPropertyBinding]

  def bind(self, properties):
    """
    @param  properties  [(obj, pty)]
    """
    b = SkPropertyBinding()
    for obj, pty in properties:
      try:
        obj.destroyed.connect(partial(self.removeBinding, b))
        b.add(obj, pty)
      except AttributeError: pass
    if not b.isEmpty():
      b.bind()
      self.__d.bindings.append(b)

  def unbind(self, properties):
    b = self.findBinding(properties)
    if b:
      b.unbind()
      self.__d.binginds.remove(b)

  def removeBinding(self, b):
    if self.__d.bindings:
      try: self.__d.bindings.remove(b)
      except ValueError: pass

  def findBinding(self, properties):
    for b in self.__d.bindings:
      for obj, pty in properties:
        if not b.contains(obj, pty):
          continue
      return b

@memoized
def property_binder(): return PropertyBinder()

def bind_properties(properties):
  property_binder().bind(properties)
def unbind_properties(properties):
  property_binder().unbind(properties)

# EOF
