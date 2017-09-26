# coding: utf8
# rc.py
# 2/10/2013 jichi

import os

APP_PATH = os.path.join(os.path.dirname(__file__), '../../apps')
SCRIPT_PATH = os.path.join(os.path.dirname(__file__), '../../scripts')

def scriptpath(fname): # str -> str
  return os.path.join(SCRIPT_PATH, fname)

def apppath(fname): # str -> str
  return os.path.join(APP_PATH, fname)

def runscript(pyfile, args=[], flags=['-B'], debug=True):
  """
  @param  pyfile  str
  @param* args [str]
  @param* debug  bool
  @return  bool
  """
  from sakurakit import skpaths, skproc
  python = skpaths.get_python_executable(gui=not debug) # enforce command line
  main = scriptpath(pyfile)
  l = [python]
  if flags:
    l.extend(flags)
  l.append(main)
  if args:
    l.extend(args)
  return skproc.detach(l)

def runapp(name, args=[], flags=['-B'], debug=True):
  """
  @param  pyfile  str
  @param* args [str]
  @param* debug  bool
  @return  bool
  """
  from sakurakit import skpaths, skproc
  python = skpaths.get_python_executable(gui=not debug) # enforce command line
  main = apppath(name)
  l = [python]
  if flags:
    l.extend(flags)
  l.append(main)
  if args:
    l.extend(args)
  if debug:
    l.append('--debug')
  return skproc.detach(l)

# EOF
