# coding: utf8
# skos.py
# 10/8/2012 jichi

import os, platform, sys
from skdebug import dwarn

WIN     = os.name == 'nt'
WIN32   = sys.platform == 'win32'
WIN64   = sys.platform == 'win64'

POSIX   = os.name == 'posix'
MAC     = sys.platform == 'darwin'
LINUX   = POSIX and not MAC

# See: http://stackoverflow.com/questions/1405913/how-do-i-determine-if-my-python-shell-is-executing-in-32bit-or-64bit-mode
X86_64  = sys.maxsize > 2**32
X86     = not X86_64

name = 'mac' if MAC else 'win' if WIN else 'posix'

# http://stackoverflow.com/questions/196930/how-to-check-if-os-is-vista-in-python
# >>> import platform
# >>> platform.win32_ver()
# ('XP', '5.1.2600', 'SP2', 'Multiprocessor Free')
# >>> platform.system()
# 'Windows'
# >>> platform.version()
# '5.1.2600'
# >>> platform.release()
# 'XP'

WINXP = WIN and platform.release() == 'XP'
WIN7 = WIN and platform.release() == '7'
WIN8 = WIN and platform.release() == '8'

def kill_my_process():
  # http://stackoverflow.com/questions/1533200/qt-kill-current-process/9920452#9920452
  dwarn("pass")
  if WIN:
    import skwin
    skwin.kill_my_process()
  else:
    os.system("kill -9 %i" % os.getpid())

def restart_my_process(params=None): # extra parameters
  """
  @param* params  [unicode]
  """
  dwarn("pass")
  arg0 = sys.executable # path to python executable
  if not WIN:
    # See: http://www.daniweb.com/software-development/python/code/260268/restart-your-python-program
    if params:
      argv = params[:]
      argv.extend(sys.argv)
    else:
      argv = sys.argv
    os.execl(arg0, arg0, *argv) # execl(path, *args)
  else:
    args = [arg0]
    if params:
      args.extend(params)
    args.extend(sys.argv)
    import skproc
    skproc.detach(args)
    kill_my_process()

# See: http://www.stackoverflow.com/questions/6631299
def open_location(path):
  """
  @param  path  unicode
  @return  bool
  """
  try:
    if WIN:
      return os.startfile(path)
    elif MAC:
      import skproc
      return bool(skproc.detachgui(['open', path]))
    elif LINUX:
      import skproc
      return bool(skproc.detachgui(['xdg-open', path]))
    else:
      import webbrowser
      #if MAC and path.startswith('/'):
      #  path = 'file://' + path
      return webbrowser.open(path)
  except Exception, e:
    dwarn(e)
    return False

class CwdChanger:
  def __init__(self, path):
    """
    @param  path  unicode
    """
    self.path = path
  def __enter__(self):
    """
    @raise  os.error, TypeError
    """
    self.cwd = os.getcwd()
    os.chdir(self.path)
    return self

  def __exit__(self, *err):
    os.chdir(self.cwd)

# EOF
