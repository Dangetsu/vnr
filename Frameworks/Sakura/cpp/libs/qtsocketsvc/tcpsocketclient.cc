// tcpsocketclient.cc
// 4/29/2014 jichi
#include "qtsocketsvc/socketdef.h"
#include "qtsocketsvc/tcpsocketclient.h"
#include "qtsocketsvc/socketio_p.h"
#include <QtCore/QDateTime>
//#include <QtCore/QEventLoop>
#include <QtNetwork/QHostAddress>
#include <QtNetwork/QTcpSocket>

#define DEBUG "TcpSocketClient"
#include <sakurakit/skdebug.h>

//QTSS_BEGIN_NAMESPACE

/** Private class */

class TcpSocketClientPrivate
{
  SK_DECLARE_PUBLIC(TcpSocketClient)
public:
  QTcpSocket *socket;
  int port;
  QString address;
  quint32 currentDataSize; // current message body size read from socket
  bool dataJustReceived;

  explicit TcpSocketClientPrivate(Q *q)
    : q_(q),
      socket(nullptr), port(0), address(SOCKET_SERVICE_HOST), currentDataSize(0),
      dataJustReceived(false)
  {}

  void createSocket()
  {
    socket = new QTcpSocket(q_);
    q_->connect(socket, SIGNAL(readyRead()), SLOT(readSocket()));

    q_->connect(socket, SIGNAL(error(QAbstractSocket::SocketError)), SIGNAL(socketError()));
    q_->connect(socket, SIGNAL(connected()), SIGNAL(connected()));
    q_->connect(socket, SIGNAL(disconnected()), SIGNAL(disconnected()));
  }

  void deleteSocket()
  {
    if (socket) {
      delete socket;
      socket = nullptr;
    }
  }

  bool writeSocket(const QByteArray &data, bool pack);
  QByteArray readSocket();

  bool waitForDataReceived(int interval);

  void dumpSocketInfo() const; // for debug only

private:
  // Return current msec
  static qint64 now() { return QDateTime::currentMSecsSinceEpoch(); }
};

bool TcpSocketClientPrivate::writeSocket(const QByteArray &data, bool pack)
{ return socket && SocketService::writeSocket(socket, data, pack); }

QByteArray TcpSocketClientPrivate::readSocket()
{
  if (Q_UNLIKELY(!socket))
    return QByteArray();
  return SocketService::readSocket(socket, currentDataSize);
}

bool TcpSocketClientPrivate::waitForDataReceived(int interval)
{
  if (Q_UNLIKELY(!socket))
    return false;
  dataJustReceived = false;
  qint64 startTime = now();
  while (interval > 0 && socket->waitForReadyRead(interval) && !dataJustReceived) {
    qint64 time = now();
    interval -= time - startTime;
    startTime = time;
  }
  return dataJustReceived;
}

void TcpSocketClientPrivate::dumpSocketInfo() const
{
  if (socket)
    DOUT("socket"
         ": localAddress ="<< socket->localAddress() <<
         ", localPort ="   << socket->localPort() <<
         ", peerAddress =" << socket->peerAddress() <<
         ", peerPort ="    << socket->peerPort() <<
         ", state ="       << socket->state() <<
         ", error ="       << socket->errorString());
  else
    DOUT("socket = null");
}

/** Public class */

// Constructions:

TcpSocketClient::TcpSocketClient(QObject *parent)
  : Base(parent), d_(new D(this))
{}

TcpSocketClient::~TcpSocketClient() { delete d_; }

int TcpSocketClient::port() const { return d_->port; }
void TcpSocketClient::setPort(int value) { d_->port = value; }

QString TcpSocketClient::address() const { return d_->address; }
void TcpSocketClient::setAddress(const QString &value) { d_->address = value; }

void TcpSocketClient::start(QIODevice::OpenMode mode)
{
  if (!d_->socket)
    d_->createSocket();
  d_->socket->connectToHost(QHostAddress(d_->address), d_->port, mode);
  DOUT("pass");
}

void TcpSocketClient::restart(QIODevice::OpenMode mode)
{
  d_->deleteSocket();
  start(mode);
  DOUT("pass");
}

void TcpSocketClient::stop()
{
  if (d_->socket && d_->socket->isOpen()) {
    d_->socket->close();
    DOUT("pass");
  }
}

bool TcpSocketClient::isConnected() const
{ return d_->socket && d_->socket->state() == QAbstractSocket::ConnectedState; }

//bool TcpSocketClient::isReady() const
//{
//  return d_->socket && (
//    d_->socket->state() == QAbstractSocket::ConnectedState ||
//    d_->socket->state() == QAbstractSocket::UnconnectedState
//  );
//}

//void TcpSocketClient::waitForReady()
//{
//  if (d_->socket &&
//    d_->socket->state() != QAbstractSocket::ConnectedState &&
//    d_->socket->state() != QAbstractSocket::UnconnectedState) {
//
//    QEventLoop loop;
//    connect(d_->socket, SIGNAL(stateChanged(QAbstractSocket::SocketState)), &loop, SLOT(quit()));
//    connect(d_->socket, SIGNAL(error(QAbstractSocket::SocketError)), &loop, SLOT(quit()));
//    do loop.exec();
//    while (!d_->socket ||
//           d_->socket->state() == QAbstractSocket::HostLookupState ||
//           d_->socket->state() == QAbstractSocket::ConnectingState);
//  }
//}

// I/O:

bool TcpSocketClient::sendData(const QByteArray &data, int waitTime, bool pack)
{
  bool ok = d_->writeSocket(data, pack);
  if (ok && waitTime)
    ok = d_->socket->waitForBytesWritten(waitTime);
  return ok;
}

bool TcpSocketClient::waitForConnected(int interval)
{ return d_->socket && d_->socket->waitForConnected(interval); }

bool TcpSocketClient::waitForDisconnected(int interval)
{ return d_->socket && d_->socket->waitForDisconnected(interval); }

bool TcpSocketClient::waitForBytesWritten(int interval)
{ return d_->socket && d_->socket->waitForBytesWritten(interval); }

bool TcpSocketClient::waitForReadyRead(int interval)
{ return d_->socket && d_->socket->waitForReadyRead(interval); }

bool TcpSocketClient::waitForDataReceived(int interval)
{ return d_->waitForDataReceived(interval); }

void TcpSocketClient::readSocket()
{
  if (Q_LIKELY(d_->socket))
    while (d_->socket->bytesAvailable()) {
      QByteArray data = d_->readSocket();
      if (data.isEmpty())
        break;
      else {
        emit dataReceived(data);
        d_->dataJustReceived = true;
      }
    }
}

void TcpSocketClient::dumpSocketInfo() const { d_->dumpSocketInfo(); }

//QTSS_END_NAMESPACE

// EOF
