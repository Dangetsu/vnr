# coding: utf8
# procbottle.py
# 10/19/2013 jichi

if __name__ == '__main__':
  import sys
  sys.path.append('..')

import os
from PySide.QtCore import QObject, Signal, Property
from sakurakit import skproc
from sakurakit.skdebug import dprint

class _ProcessBottle: pass
class ProcessBottle(QObject): #QRunnable
  def __init__(self, parent=None, pid=0, path=""):
    """
    @param  parent  QObject
    @param  pid  ulong
    @param  path  unicode
    """
    super(ProcessBottle, self).__init__(parent)
    d = self.__d = _ProcessBottle()
    d.pid = pid      # long
    d.path = path    # unicode

  def setPid(self, v):
    if v != self.__d.pid:
      self.__d.pid = v
      self.pidChanged.emit(v)
  pidChanged = Signal(long)
  pid = Property(long,
      lambda self: self.__d.pid,
      setPid,
      notify=pidChanged)

  def setPath(self, v):
    if v != self.__d.path:
      self.__d.path = v
      self.pathChanged.emit(v)
  pathChanged = Signal(unicode)
  path = Property(unicode,
      lambda self: self.__d.path,
      notify=pathChanged)

  def isActive(self):
    """
    @return  bool
    """
    return skproc.is_process_active(self.pid)

  def restart(self):
    """
    @return  bool
    """
    return self.run()

  def run(self):
    """Launch process without visible window
    @return  bool
    """
    if self.path:
      pid = skproc.get_pid_by_path(self.path)
      if pid:
        dprint('found existing process')
      else:
        dprint('launch new process')
        pid = self.createProcess()
      self.setPid(pid)
      return bool(pid)
    return False

  def createProcess(self):
    """Create new process
    @return  pid  long
    """
    cwd = os.path.dirname(self.path)
    return skproc.detach([self.path], path=cwd)

  #def kill(self):
  #  """
  #  @return  bool
  #  """
  #  return bool(self.pid)

if __name__ == '__main__':
  path = r'C:\Program Files\AHS\VOICEROID+\zunko\VOICEROID.exe'
  b = ProcessBottle(path=path)
  b.run()
  if b.isActive():
    print "active"

# EOF
