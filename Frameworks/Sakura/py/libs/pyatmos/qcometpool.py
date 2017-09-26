# coding: utf8
# qcometpool.py
# jichi 2/17/2014

__all__ = 'QCometPool',

from PySide.QtCore import QObject
from qcometthread import QCometThread

class QCometPool(QObject):
  def __init__(self, url='', parent=None, debug=False):
    super(QCometPool, self).__init__(parent)
    self.debug = debug # bool
    self.url = url # string, must end with '/'
    self.threads = {} # {string path:QCometThreads}

  def subscribe(self, path): # -> CometConnection or None
    t = self.threads.get(path)
    if not t:
      url = self.url + path
      self.threads[path] = t = QCometThread(url, debug=self.debug) # Important: threads have no parent!
    return t

  def unsubscribe(self, path): # -> CometConnection or None
    t = self.threads.get(path)
    if t:
      t.unsubscribe()

  def unsubscribeAll(self):
    if self.threads:
      for it in self.threads.itervalues():
        if it.isSubscribed():
          it.unsubscribe()

  def waitAll(self, interval=None): # interval: sec
    if self.threads:
      for it in self.threads.itervalues():
        if not it.isFinished():
          if interval is None:
            it.wait()
          else:
            it.wait(interval)

if __name__ == '__main__':

  def onMessage(res, msg):
    print "msg:", msg

  import sys
  from PySide.QtCore import *
  a = QCoreApplication(sys.argv)

  #from Queue import Queue
  #q = Queue()

  #url = 'http://localhost:8080/push/'
  url = 'http://sakuradite.com/push/vnr/topic/'
  pool = QCometPool(url, debug=True)

  t = pool.subscribe('term')
  t.messageReceived.connect(onMessage, Qt.QueuedConnection)
  t.finished.connect(a.quit)
  t.subscribe()

  a.exec_()

# EOF
