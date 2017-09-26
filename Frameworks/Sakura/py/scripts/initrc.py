# coding: utf8
# initrc.py
# 10/27/2013 jichi

def initenv():
  import os, sys
  PWD = os.path.dirname(os.path.abspath(__file__))
  path = os.path.join(PWD, '../libs')
  sys.path.append(path)

  if os.name == 'posix': # only for debugging purpose
    import initdefs
    path = os.path.join(PWD, initdefs.PYTHON_RELPATH + '/Lib/site-packages')
    sys.path.append(path)

def chcwd():
  # https://mail.python.org/pipermail/tutor/2012-February/088267.html
  import os
  #cwd = os.getcwd()
  cwd = os.path.dirname(__file__)
  os.chdir(cwd)

APP_MUTEX = None
def lock(name): # unicode  file naem
  global APP_MUTEX
  if not APP_MUTEX:
    import os
    import initdefs
    path = initdefs.LOCK_RELPATH
    if not os.path.exists(path):
      os.makedirs(path)
    path = os.path.join(path, name)
    from lockfile import lockfile
    APP_MUTEX = lockfile.LockFile(path)
  return APP_MUTEX.tryLock()

# http://stackoverflow.com/questions/7387276/set-window-name-in-python
def settitle(title): # str ->
  import os
  if os.name == 'nt':
    if isinstance(title, unicode):
      title = title.encode('utf8', errors='ignore')
    import ctypes
    try: ctypes.windll.kernel32.SetConsoleTitleA(title)
    except Exception, e:
      from sakurakit.skdebug import dwarn
      dwarn(e)

# EOF
