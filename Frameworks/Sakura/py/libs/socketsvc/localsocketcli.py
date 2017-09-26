# coding: utf8
# localsocketcli.py
# jichi 4/28/2014

__all__ = 'LocalSocketClient',

if __name__ == '__main__':
  import sys
  sys.path.append('..')

from PySide.QtCore import QObject, Signal, QTimer
from sakurakit.skclass import Q_Q
from sakurakit.skdebug import dprint, dwarn
import socketio, socketpack

def _now(): # -> long  current time in milliseconds
  from time import time
  return long(time() * 1000)

class LocalSocketClient(QObject):

  def __init__(self, parent=None):
    super(LocalSocketClient, self).__init__(parent)
    self.__d = _LocalSocketClient(self)

  connected = Signal()
  disconnected = Signal()
  socketError = Signal()

  dataReceived = Signal(bytearray) # data

  def sendData(self, data, waitTime=0, **kwargs):
    """
    @param  data  str or unicode
    @param* waitTime  int
    @param* pack  bool  whether prepend header to data
    """
    ok = self.__d.writeSocket(data, **kwargs)
    if ok and waitTime:
      ok = self.__d.socket.waitForBytesWritten(waitTime)
    return ok

  def serverName(self): return self.__d.name # -> str
  def setServerName(self, v): self.__d.name = socketio.pipename(v)

  def isConnected(self): # -> bool
    s = self.__d.socket
    return bool(s) and s.state() == s.ConnectedState

  isActive = isConnected

  #def isReady(self): # -> bool, is connected or disconnected instead of connecting or uninitialized
  #  s = self.__d.socket
  #  return bool(s) and s.state() in (s.ConnectedState, s.UnconnectedState)

  def start(self, mode='rw'): self.__d.start(mode)
  def stop(self): self.__d.stop()

  #def waitForReady(self):
  #  s = self.__d.socket
  #  if s and s.state() not in (s.ConnectedState, s.UnconnectedState):
  #    from PySide.QtCore import QEventLoop
  #    loop = QEventLoop()
  #    s.stateChanged.connect(loop.quit)
  #    s.error.connect(loop.quit)
  #    loop.exec_();
  #    while s.state() in (s.HostLookupState, s.ConnectingState):
  #      loop.exec_()

  # QAbstractSocket default wait time is 30 seconds
  def waitForConnected(self, interval=30000): # -> bool
    return bool(self.__d.socket) and self.__d.socket.waitForConnected(interval)
  def waitForDisconnected(self, interval=30000): # -> bool
    return bool(self.__d.socket) and self.__d.socket.waitForDisconnected(interval)
  def waitForBytesWritten(self, interval=30000): # -> bool
    return bool(self.__d.socket) and self.__d.socket.waitForBytesWritten(interval)
  def waitForReadyRead(self, interval=30000): # -> bool
    return bool(self.__d.socket) and self.__d.socket.waitForReadyRead(interval)

  # Invoked after the dataReceived signal is emitted
  def waitForDataReceived(self, interval=30000): # -> bool
    return self.__d.waitForDataReceived(interval)

  waitForDataSent = waitForBytesWritten

  def dumpSocketInfo(self): # print the status of the socket. for debug only
    self.__d.dumpSocketInfo()

@Q_Q
class _LocalSocketClient(object):
  def __init__(self, q):
    self.encoding = 'utf8'
    self.name = '' # pipe name
    self.socket = None # # QLocalSocket
    self._dataJustReceived = False # bool

  def _createSocket(self):
    from PySide.QtNetwork import QLocalSocket
    q = self.q
    ret = QLocalSocket(q)
    socketio.initsocket(ret)
    ret.error.connect(q.socketError)
    ret.connected.connect(q.connected)
    ret.disconnected.connect(q.disconnected)
    ret.readyRead.connect(self.readSocket)
    return ret

  def start(self, modeStr):
    mode = socketio.iomode(modeStr)
    if not mode:
      dwarn("failed to parse IO device mode: %s" % modeStr)
      return
    if not self.socket:
      self.socket = self._createSocket()
    self.socket.connectToServer(self.name, mode)
    dprint("pass")

  def stop(self):
    if self.socket and self.socket.isOpen():
      self.socket.close()
      dprint("pass")

  def readSocket(self):
    s = self.socket
    if s:
      try:
        while s.bytesAvailable():
          data = socketio.readsocket(s)
          if data == None:
            break
          else:
            self.q.dataReceived.emit(data)
            self._dataJustReceived = True
      except Exception, e: # might raise runtime exception since the socket has been deleted
        dwarn(e)

  def writeSocket(self, data, pack=True):
    if not self.socket:
      return False;
    if isinstance(data, unicode):
      data = data.encode(self.encoding, errors='ignore')
    return socketio.writesocket(data, self.socket, pack=pack)

  def dumpSocketInfo(self): # for debug only
    if self.socket:
      dprint("name = %s" % self.socket.serverName())
      dprint("state = %s" % self.socket.state())
      dprint("error = %s" % self.socket.errorString())

  def waitForDataReceived(self, interval): # int -> bool
    self._dataJustReceived = False
    socket = self.socket
    if socket:
      startTime = _now()
      while interval > 0 and socket.waitForReadyRead(interval) and not self._dataJustReceived:
        now = _now()
        interval -= now - startTime
        startTime = now
    dprint("pass: ret = %s" % self._dataJustReceived)
    return self._dataJustReceived

# Cached

class BufferedLocalSocketClient(LocalSocketClient):

  def __init__(self, parent=None):
    super(BufferedLocalSocketClient, self).__init__(parent)
    self.__d = _BufferedLocalSocketClient(self)

  def sendDataLater(self, data, interval=200, waitTime=0):
    self.__d.sendBuffer += socketpack.packdata(data)
    self.__d.sendTimer.start(interval)
    self.__d.sendWaitTime = waitTime

  def flushSendBuffer(self): self.__d.flushSendBuffer()

class _BufferedLocalSocketClient(object):
  def __init__(self, q):
    self.q_sendData = q.sendData

    self.sendBuffer = '' # str
    self.sendWaitTime = 0 # int

    self.sendTimer = t = QTimer(q)
    t.setSingleShot(True)
    t.timeout.connect(self.flushSendBuffer)

  def flushSendBuffer(self):
    if self.sendTimer.isActive():
      self.sendTimer.stop()
    if self.sendBuffer:
      self.q_sendData(self.sendBuffer, waitTime=self.sendWaitTime, pack=False)
      self.sendBuffer = ''

if __name__ == '__main__':
  import sys
  from PySide.QtCore import QCoreApplication

  pipeName = 'pipetest'

  app =  QCoreApplication(sys.argv)
  #c = LocalSocketClient()
  c = BufferedLocalSocketClient()
  c.setServerName(pipeName)
  def f(data):
    print data, type(data), len(data)
    app.quit()
  c.dataReceived.connect(f)
  c.start()
  #c.waitForReady()
  c.waitForConnected()

  #t = "hello"
  #t = u"こんにちは"

  interval = 2000

  t = '0' * 100
  #print t
  #c.sendDataLater(t, interval)
  #c.sendData(t, interval)
  c.sendData(t, 0)

  c.waitForDataReceived()

  t = '1' * 100
  #print t
  c.sendDataLater(t, interval)
  t = '2' * 100
  #print t
  c.sendDataLater(t, interval)
  t = '3' * 100
  #print t
  c.sendDataLater(t, interval)
  t = '4' * 100
  #print t
  c.sendDataLater(t, interval)
  t = '5' * 100
  #print t
  c.sendDataLater(t, interval)
  print c.isActive()

  #t = '1' * 100
  #ok = c.sendData(t)
  #print ok

  c.disconnected.connect(app.quit)

  #c.dumpSocketInfo()

  sys.exit(app.exec_())

# EOF
