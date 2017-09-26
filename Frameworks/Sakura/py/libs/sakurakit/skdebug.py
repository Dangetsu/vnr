# coding: utf8
# skdebug.py
# 10/10/2012 jichi

from __future__ import print_function
import functools, inspect, os, sys
from colorama import Fore, Back, Style
import skinspect

DEBUG = True

## Functions ##

def safeprint(*args, **kwargs):
  try: print(*args, **kwargs)
  except Exception: pass

# See: http://stackoverflow.com/questions/5863512/python-how-to-get-the-class-of-a-calling-method-through-inspection
def dprint(msg, *args):
  if not DEBUG:
    return
  """Parameters are in the same format as print in Py3K"""
  caller = inspect.stack()[1] # caller object
  frame = caller[skinspect.CALLER_FRAME_INDEX]
  path = caller[skinspect.CALLER_FILE_INDEX]
  func = caller[skinspect.CALLER_FUNC_INDEX]

  try:
    self = frame.f_code.co_varnames[0]
    instance = frame.f_locals[self]
    class_ = instance.__class__.__name__
  except (KeyError, IndexError, TypeError):
    class_ = None # class name

  file_ = os.path.basename(path) # file name or module name
  if file_ == '__main__.py':
    file_ = os.path.basename(os.path.dirname(path))
    if func == '<module>':
      func = '__main__.py'
  if args:
    if class_:
      safeprint("%s:%s:%s:" % (file_,class_,func), msg, *args, file=sys.stderr)
    else:
      safeprint("%s:%s:" % (file_,func), msg, args, file=sys.stderr)
  else:
    if class_:
      safeprint("%s:%s:%s:" % (file_,class_,func), msg, file=sys.stderr)
    else:
      safeprint("%s:%s:" % (file_,func), msg, file=sys.stderr)

COLORAMA_INIT = False
def dwarn(msg, *args):
  if not DEBUG:
    return
  global COLORAMA_INIT
  if not COLORAMA_INIT:
    import colorama
    colorama.init()
    COLORAMA_INIT = True
  """Parameters are in the same format as print in Py3K"""
  caller = inspect.stack()[1] # caller object
  frame = caller[skinspect.CALLER_FRAME_INDEX]
  path = caller[skinspect.CALLER_FILE_INDEX]
  func = caller[skinspect.CALLER_FUNC_INDEX]

  try:
    self = frame.f_code.co_varnames[0]
    instance = frame.f_locals[self]
    class_ = instance.__class__.__name__
  except (KeyError, IndexError, TypeError):
    class_ = None  # class name

  file_ = os.path.basename(path) # file name or module name
  if file_ == '__main__.py':
    file_ = os.path.basename(os.path.dirname(path))
    if func == '<module>':
      func = '__main__.py'

  beg = Fore.RED
  end = Fore.RESET
  if args:
    if class_:
      safeprint(beg + "%s:%s:%s:" % (file_,class_,func), msg, args, end, file=sys.stderr)
    else:
      safeprint(beg + "%s:%s:" % (file_,func), msg, args, end, file=sys.stderr)
  else:
    if class_:
      safeprint(beg + "%s:%s:%s:" % (file_,class_,func), msg, end, file=sys.stderr)
    else:
      safeprint(beg + "%s:%s::" % (file_,func), msg, end, file=sys.stderr)

def derror(msg, *args):
  if not DEBUG:
    return
  global COLORAMA_INIT
  if not COLORAMA_INIT:
    import colorama
    colorama.init()
    COLORAMA_INIT = True
  """Parameters are in the same format as print in Py3K"""
  caller = inspect.stack()[1] # caller object
  frame = caller[skinspect.CALLER_FRAME_INDEX]
  path = caller[skinspect.CALLER_FILE_INDEX]
  func = caller[skinspect.CALLER_FUNC_INDEX]

  try:
    self = frame.f_code.co_varnames[0]
    instance = frame.f_locals[self]
    class_ = instance.__class__.__name__
  except (KeyError, IndexError, TypeError):
    class_ = None # class name

  file_ = os.path.basename(path) # file name or module name
  if file_ == '__main__.py':
    file_ = os.path.basename(os.path.dirname(path))
    if func == '<module>':
      func = '__main__.py'

  beg = Fore.BLACK + Back.RED
  end = Fore.RESET + Back.RESET
  if args:
    if class_:
      safeprint(beg + "%s:%s:%s:" % (file_,class_,func), msg, args, end, file=sys.stderr)
    else:
      safeprint(beg + "%s:%s:" % (file_,func), msg, args, end, file=sys.stderr)
  else:
    if class_:
      safeprint(beg + "%s:%s:%s:" % (file_,class_,func), msg, end, file=sys.stderr)
    else:
      safeprint(beg + "%s:%s:" % (file_,func), msg, end, file=sys.stderr)

## Decorators ##

# See: http://www.artima.com/weblogs/viewpost.jsp?thread=240808
def debugfunc(f):
  if not DEBUG:
    return f

  @functools.wraps(f)
  def ret(*args, **kwargs):
    caller = inspect.stack()[1] # caller object
    frame = caller[skinspect.CALLER_FRAME_INDEX]
    path = caller[skinspect.CALLER_FILE_INDEX]
    func = caller[skinspect.CALLER_FUNC_INDEX]
    file_ = os.path.basename(path) # file name or module name
    if file_ == '__main__.py':
      file_ = os.path.basename(os.path.dirname(path))
      if func == '<module>':
        func = '__main__.py'

    if func != f.__name__:
      func = func + ":" + f.__name__

    safeprint("%s:%s: enter" % (file_,func), file=sys.stderr)
    r = f(*args, **kwargs)
    safeprint("%s:%s: leave" % (file_,func), file=sys.stderr)
    return r
  return ret

def debugmethod(f):
  if not DEBUG:
    return f

  @functools.wraps(f)
  def ret(*args, **kwargs):
    caller = inspect.stack()[1] # caller object
    frame = caller[skinspect.CALLER_FRAME_INDEX]
    path = caller[skinspect.CALLER_FILE_INDEX]
    func = caller[skinspect.CALLER_FUNC_INDEX]
    file_ = os.path.basename(path) # file name or module name
    if file_ == '__main__.py':
      file_ = os.path.basename(os.path.dirname(path))
      if func == '<module>':
        func = '__main__.py'

    if func != f.__name__:
      func = func + ":" + f.__name__

    try:
      self = frame.f_code.co_varnames[0]
      instance = frame.f_locals[self]
      class_ = instance.__class__.__name__
    except (KeyError, IndexError, TypeError):
      class_ = None # class name

    if class_:
      safeprint("%s:%s:%s: enter" % (file_,class_,func), file=sys.stderr)
    else:
      safeprint("%s:%s: enter" % (file_,func), file=sys.stderr)

    r = f(*args, **kwargs)

    if class_:
      safeprint("%s:%s:%s: leave" % (file_,class_,func), file=sys.stderr)
    else:
      safeprint("%s:%s: leave" % (file_,func), file=sys.stderr)
    return r
  return ret

if __name__ == '__main__':
  dprint("hello print")
  dwarn("hello warning")
  derror("hello error")

  @debugfunc
  def func():
    safeprint("hello func", file=sys.stderr)
  func()

  class C:
    @debugmethod
    def method(self):
      safeprint("hello method", file=sys.stderr)
  C().method()

# EOF

# See: http://stackoverflow.com/questions/3425512/how-do-i-get-the-same-functionality-as-cs-function-in-python
# See: http://docs.python.org/library/logging.html
#import logging
#import sys
#
#logging.basicConfig(
#    format="%(filename)s:%(funcName)s:%(message)s",
#    level=logging.DEBUG,
#    stream=sys.stderr)
