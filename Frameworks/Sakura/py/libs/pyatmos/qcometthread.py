# coding: utf8
# qcometthread.py
# jichi 2/17/2014

__all__ = 'QCometThread',

from PySide.QtCore import Signal, QThread
from comet import CometConnection

class QCometThread(QThread):

  messageReceived = Signal(object, unicode) # requests.models.Response, data
  errorReceived = Signal(object, unicode) # requests.models.Response, data

  def __init__(self, url='', parent=None, debug=False):
    super(QCometThread, self).__init__(parent)
    self.debug = debug # debug
    self.comet = CometConnection(url=url)
    self.connected = False # bool
    self.subscribed = False # bool

    self.reconnectCount = 0 # int, current reconnect count
    self.maxReconnectCount = 5 # int, 5 times
    self.reconnectInterval = 5000 # int, 5 seconds

    for k in 'onMessage', 'onError':
      v = getattr(self, k)
      setattr(self.comet, k, v)

  def isSubscribed(self): return self.subscribed
  def isConnected(self): return self.connected

  def setMaxReconnectCount(self, v): # int
    self.maxReconnectCount = v
  def setReconnectInterval(self, v): # int msecs
    self.reconnectInterval = v

  def subscribe(self):
    self.subscribed = True
    if not self.isRunning():
      self.start()
  def unsubscribe(self):
    self.subscribed = False

  def onMessage(self, res, data): # requests.models.Response, data
    self.messageReceived.emit(res, data)

  def onError(self, res, msg): # requests.models.Response, data
    if self.debug:
      print "qcometpool: onError:", msg
    self.errorReceived.emit(res, msg)

  def onReconnect(self):
    if self.debug:
      print "qcometpool: onReconnect: %i/%i" % (self.reconnectCount, self.maxReconnectCount)

  def run(self): # override
    if self.subscribed:
      self.connected = self.comet.connect()
      if self.connected:
        self.reconnectCount = 0
        while self.subscribed and self.reconnectCount < self.maxReconnectCount:
          ok = self.comet.pop()
          if not ok:
            self.reconnectCount += 1
            if self.reconnectCount < self.maxReconnectCount:
              self.msleep(self.reconnectInterval)
              self.onReconnect()
          elif self.reconnectCount:
            self.reconnectCount = 0
        self.comet.disconnect()
        self.connected = False

  def push(self, data): # string ->
    self.comet.push(data)

# EOF
