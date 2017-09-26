# coding: utf8
# skproc.py
# 11/10/2012 jichi

import os, sys
import psutil
from skdebug import dprint, dwarn
import skos
if skos.WIN:
  import win32con

# Launch

def detach(args, path=''):
  """
  @param  args  [unicode]
  @param* path  unicode  working directory
  @return  bool
  """
  from PySide.QtCore import QProcess
  dprint("path: %s" % (path or '(empty)'))
  dprint(args)
  if path:
    return QProcess.startDetached(args[0], args[1:], path)
  else:
    return QProcess.startDetached(args[0], args[1:])

def detachgui(args):
  """Always hide command prompt on Windows
  @param  args  [unicode]
  @return  pid  ulong
  """
  dprint(args)
  # http://stackoverflow.com/questions/13592219/launch-a-totally-independent-process-from-python
  #DETACHED_PROCESS = win32con.DETACHED_PROCESS
  import subprocess
  try:
    if skos.WIN:
      flags = win32con.DETACHED_PROCESS|subprocess.CREATE_NEW_PROCESS_GROUP
    else:
      flags = 0
    p = subprocess.Popen(args,
        creationflags=flags,
        #shell=True,
        close_fds=True)
    return p.pid
  except Exception, e:
    dwarn(e)
    return 0

def attachgui(args):
  """Always hide command prompt on Windows
  @param  args  [unicode]
  @return  bool
  """
  dprint(args)
  # http://stackoverflow.com/questions/13592219/launch-a-totally-independent-process-from-python
  import subprocess
  try:
    if skos.WIN:
      flags = win32con.DETACHED_PROCESS|subprocess.CREATE_NEW_PROCESS_GROUP
    else:
      flags = 0
    errcode = subprocess.call(args,
        creationflags=flags,
        #shell=True,
        close_fds=True)
    return errcode == 0
  except Exception, e:
    dwarn(e)
    return False

# Search

def is_process_active(pid):
  """
  @param  pid  ulong
  @return  bool
  """
  if skos.WIN: # on mac, pid can be zero
    import skwin
    return bool(pid) and skwin.is_process_active(pid)
  else:
    dwarn("unimplemented")
    return False

def iterprocesses():
  """Generator of candidate game process
  @yield  (ulong pid, unicode path)

  Implemented using psutil. Using WMI is more efficient, but less portable.
  See: http://www.blog.pythonlibrary.org/2010/10/03/how-to-find-and-list-all-running-processes-with-python/
  """
  from skunicode import u
  for p in psutil.process_iter():
    if p.pid and p.is_running():      # pid == 0 will raise access denied exception on Mac
      try: path = u(p.exe)        # system processes raise access denied exception on Windows 7
      except: continue
      if path:
        #name = u(p.name)
        pid = p.pid
        yield pid, path

def normalize_path(path):
  """Return os-native format path
  @param  path  str or None
  @return  unicode or ""
  """
  return path.replace('/', os.path.sep).lower() if path else ""

def get_pid_by_path(path):
  """
  @param  path  unicode or None
  @return  Process or None
  """
  np = normalize_path(path)
  for pid,ppath in iterprocesses():
    if np == normalize_path(ppath):
      return pid

#def get_process_path(pid):
#  """
#  @return  unicode or None
#  """
#  if skos.WIN:
#    return get_process_path(pid)
#  else:
#    for p in iterprocesses():
#      if p.pid == pid:
#        return p.path

# EOF
