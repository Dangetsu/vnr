# coding: utf8
# lockfile.py
# 2/13/2014 jichi

__all__ = 'LockFile', 'SingleProcessMutex'

if __name__ == '__main__':
  import sys
  sys.path.append('..')


import os
from sakurakit import skos
from sakurakit.skdebug import dwarn, derror
if skos.POSIX:
  import fcntl

class _LockFile(object):
  def __init__(self, path):
    self.path = path # unicode
    self.locked = False # bool, whether succeeded or not

  def __del__(self):
    if self.locked:
      self.unlock()

  def lock(self): pass
  def unlock(self): pass

class _LockFile_posix(_LockFile):

  def lock(self):
    """@reimp
    """
    self._fp = open(self.path, 'w')
    try:
      fcntl.lockf(self._fp, fcntl.LOCK_EX|fcntl.LOCK_NB)
      self.locked = True
    except IOError:
      dwarn("failed to create lock file")

  def unlock(self):
    """@reimp"""
    try:
      if fcntl: # it will be None if deleted
        fcntl.lockf(self._fp, fcntl.LOCK_UN)
      #os.close(self._fp)
      if os.path.isfile(self.path):
        os.unlink(self.path)
    except Exception, e:
      derror(e)

class _LockFile_win(_LockFile):

  def lock(self):
    """@reimp
    """
    try:
      # file already exists, we try to remove (in case previous execution was interrupted)
      if os.path.exists(self.path):
        os.unlink(self.path)
      self._fd = os.open(self.path, os.O_CREAT|os.O_EXCL|os.O_RDWR)
      self.locked = True
    except OSError, e:
      #type_, err, tb = sys.exc_info()
      #if err.errno == 13:
      dwarn("failed to create lock file")

  def unlock(self):
    """@reimp
    """
    try:
      os.close(self._fd)
      os.unlink(self.path)
    except Exception, e:
      dwarn(e)
      try:
        if os.path.exists(self.path):
          os.remove(self.path)
      except Exception, e:
        dwarn(e)

# Implemented using file lock, modified from tendo
class LockFile(object):
  def __init__(self, path):
    _D = _LockFile_win if skos.WIN else _LockFile_posix
    self.__d = _D(path=path)

  def tryLock(self):
    """
    @return  bool
    """
    self.__d.lock()
    return self.__d.locked

  def unlock(self):
    self.__d.unlock()

  def isLocked(self):
    """
    @return  bool
    """
    return self.__d.locked

class SingleProcessMutex(LockFile):
  def __init__(self):
    path = self.getlockfile()
    super(SingleProcessMutex, self).__init__(path)

    #import atexit
    #atexit.register(self.unlock)

  @staticmethod
  def getlockfile():
    """
    @return  str  path to the lock file in $TMP directory
    """
    import sys, tempfile
    lockdir = tempfile.gettempdir()
    mainfile = os.path.abspath(sys.modules['__main__'].__file__)
    mainfile = os.path.normpath(mainfile)
    hashfile = (os.path.splitext(mainfile)[0]
      .replace("/","-")
      .replace(":","")
      .replace("\\","-"))
    ret = os.path.join(lockdir, hashfile + '.lock')
    return ret

if __name__ == '__main__':
  path = 'tmp.lock'
  print os.path.exists(path)
  f = LockFile(path)
  print f.tryLock()
  print os.path.exists(path)
  #f.unlock()

# EOF
