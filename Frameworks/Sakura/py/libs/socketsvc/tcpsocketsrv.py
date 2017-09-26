# coding: utf8
# tcpsocketsrv.py
# jichi 4/28/2014

__all__ = 'TcpSocketServer',

if __name__ == '__main__':
  import sys
  sys.path.append('..')

import weakref
from functools import partial
from PySide.QtCore import QObject, Signal
from sakurakit.skclass import Q_Q
from sakurakit.skdebug import dprint, dwarn
import socketio

class TcpSocketServer(QObject):
  """
  Message protocol:
  The first 4b is int32 (message size - 4) (little-endian).
  """

  def __init__(self, parent=None):
    super(TcpSocketServer, self).__init__(parent)
    self.__d = _TcpSocketServer(self)

  connected = Signal(QObject) # client socket
  disconnected = Signal(QObject) # client socket
  socketError = Signal(QObject) # client socket

  dataReceived = Signal(bytearray, QObject) # data, client socket

  def sendData(self, data, socket, waitTime=0):  # str, QTcpSocket, int -> bool
    ok = self.__d.writeSocket(data, socket)
    if ok and waitTime:
      ok = socket.waitForBytesWritten(waitTime)
    return ok

  def waitForBytesWritten(self, waitTime=30000): # -> bool
    ok = True
    for s in self.__d.sockets:
      ok = s.waitForBytesWritten(waitTime) and ok
    return ok

  def broadcastData(self, data, *args, **kwargs):  # str, int -> bool
    for s in self.__d.sockets:
      self.sendData(data, s, *args, **kwargs)

  def connectionCount(self):
    return len(self.__d.sockets)

  def address(self): return self.__d.address # -> str
  def setAddress(self, v): self.__d.address = v

  def port(self): return self.__d.port # -> int
  def setPort(self, v): self.__d.port = v

  def start(self): return self.__d.start() # -> bool
  def stop(self): self.__d.stop()

  def isListening(self): # -> bool
    return bool(self.__d.server) and self.__d.server.isListening()

  isActive = isListening

  def closeSocket(self, socket): # QTcpSocket
    if socket.isOpen():
      socket.close()
    self.__d.deleteSocket(socket)

@Q_Q
class _TcpSocketServer(object):
  def __init__(self, q):
    self.encoding = 'utf8'
    self.address = '127.0.0.1' # host name without http prefix
    self.port = 0 # int
    self.server = None # QTcpServer
    self.sockets = [] # [QTcpSocket]

  def _createServer(self):
    from PySide.QtNetwork import QTcpServer
    ret = QTcpServer(self.q)
    ret.newConnection.connect(self._onNewConnection)
    return ret

  def start(self): # -> bool
    from PySide.QtNetwork import QHostAddress
    if not self.server:
      self.server = self._createServer()
    ok = self.server.listen(QHostAddress(self.address), self.port)
    dprint("pass: ok = %s" % ok)
    return ok

  def stop(self):
    if self.server:
      self.server.close()
      dprint("pass")

  def _onNewConnection(self):
    #assert self.server
    socket = self.server.nextPendingConnection();
    if socket:
      socketio.initsocket(socket)
      self.sockets.append(socket)
      ref = weakref.ref(socket)
      socket.error.connect(partial(lambda ref, error:
          self.q.socketError.emit(ref()),
          ref))
      socket.connected.connect(partial(lambda ref:
          self.q.connected.emit(ref()),
          ref))
      socket.disconnected.connect(partial(lambda ref:
          self.q.disconnected.emit(ref()),
          ref))

      socket.disconnected.connect(partial(lambda ref:
          self.deleteSocket(ref()),
          ref))

      socket.readyRead.connect(partial(lambda ref:
          self.readSocket(ref()),
          ref))

  def deleteSocket(self, socket):
    socket.deleteLater()
    try: self.sockets.remove(socket)
    except ValueError: pass

  def readSocket(self, socket):
    try:
      while socket.bytesAvailable():
        data = socketio.readsocket(socket)
        if data == None:
          break
        else:
          self.q.dataReceived.emit(data, socket)
    except Exception, e: # might raise runtime exception since the socket has been deleted
      dwarn(e)

  def writeSocket(self, data, socket):
    if isinstance(data, unicode):
      data = data.encode(self.encoding, errors='ignore')
    return socketio.writesocket(data, socket)

if __name__ == '__main__':
  import sys
  from PySide.QtCore import QCoreApplication
  app =  QCoreApplication(sys.argv)
  s = TcpSocketServer()
  s.setPort(6002)
  s.start()

  def f(data):
    print data, type(data), len(data)
    #t = '0' * 100
    #t = u'あ' * 1000
    s.broadcastData(data)
    #s.waitForBytesWritten()
    #app.quit()
  s.dataReceived.connect(f)

  sys.exit(app.exec_())

# EOF
