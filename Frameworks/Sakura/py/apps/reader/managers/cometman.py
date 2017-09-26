# coding: utf8
# cometman.py
# 2/17/2013 jichi

if __name__ == '__main__':
  import sys
  sys.path.append('..')
  import debug
  debug.initenv()

from PySide.QtCore import Signal, Property, Qt, QObject
from sakurakit.skclass import Q_Q, memoized, memoizedproperty, hasmemoizedproperty
from sakurakit.skdebug import dprint, dwarn
#from sakurakit.skqml import QmlObject
import json

PATH_TOPIC_TERM = 'vnr/topic/term'

@Q_Q
class _CometManager(object):

  def __init__(self):
    self._resetTermTopic()

  def _resetTermTopic(self):
    self.termTopicConnectionCount = 0 # int

  @memoizedproperty
  def pool(self):
    from pyatmo.qcometpool import QCometPool
    from sakurakit.skdebug import DEBUG
    import config
    return QCometPool(parent=self.q, url=config.API_PUSH, debug=DEBUG)

  #@staticmethod
  #def parseJson(data): # unicode -> object or None
  #  try: return json.loads
  #  except Exception, e:
  #    dwarn(e)

  def unsubscribeAll(self):
    if hasmemoizedproperty(self, 'pool'):
      self.pool.unsubscribeAll()

  # Shared dictionary

  def subscribeTermTopic(self):
    t = self.pool.subscribe(PATH_TOPIC_TERM)
    if not hasattr(t, 'init'):
      t.messageReceived.connect(self._onTermTopicMessage, Qt.QueuedConnection)
      t.init = True
    t.subscribe()
    dprint("pass")

  def unsubscribeTermTopic(self):
    self.pool.unsubscribe(PATH_TOPIC_TERM)
    self._resetTermTopic()
    dprint("pass")

  def _onTermTopicMessage(self, res, data): # response, unicode data
    try:
      obj = json.loads(data)
      type_ =  obj['type']
      data = obj['data']
      if type_ == 'count':
        count  = int(data)
        if count != self.termTopicConnectionCount:
          self.termTopicConnectionCount = 0
          self.q.termTopicConnectionCountChanged.emit(count)
      else:
        dwarn("unknown object type: %s" % type_)
    except Exception, e:
      dwarn(e)

class CometManager(QObject):

  def __init__(self, parent = None):
    super(CometManager, self).__init__(parent)
    self.__d = _CometManager(self)
    self.enabled = True

  def isEnabled(self): return self.enabled
  def setEnabled(self, v):
    if self.enabled != v:
      self.enabled = v
      if not v:
        self.__d.unsubscribeAll()

  def unsubscribeAll(self): self.__d.unsubscribeAll()

  def subscribeTermTopic(self, t=True):
    if not t:
      self.unsubscribeTermTopic()
      return
    if self.enabled:
      self.__d.subscribeTermTopic()
  def unsubscribeTermTopic(self):
    self.__d.unsubscribeTermTopic()

  termTopicConnectionCountChanged = Signal(int)
  def termTopicConnectionCount(self): return self.__d.termTopicConnectionCount

@memoized
def manager(): return CometManager()

#@QmlObject
class CometManagerProxy(QObject):
  def __init__(self, parent=None):
    super(CometManagerProxy, self).__init__(parent)
    dm = manager()
    dm.termTopicConnectionCountChanged.connect(self.termTopicConnectionCountChanged)

  termTopicConnectionCountChanged = Signal(int)
  termTopicConnectionCount = Property(int,
      lambda self: manager().termTopicConnectionCount(),
      notify=termTopicConnectionCountChanged)

if __name__ == '__main__':
  a = debug.app()

  m = manager()
  m.subscribeTermTopic()

  a.exec_()

# EOF
