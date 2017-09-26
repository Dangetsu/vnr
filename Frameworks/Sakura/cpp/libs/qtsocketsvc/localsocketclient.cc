// localsocketclient.cc
// 4/29/2014 jichi
#include "qtsocketsvc/socketdef.h"
#include "qtsocketsvc/localsocketclient.h"
#include "qtsocketsvc/socketio_p.h"
#include <QtCore/QDateTime>
//#include <QtCore/QEventLoop>
#include <QtNetwork/QLocalSocket>

#define DEBUG "LocalSocketClient"
#include <sakurakit/skdebug.h>

//QTSS_BEGIN_NAMESPACE

/** Private class */

class LocalSocketClientPrivate
{
  SK_DECLARE_PUBLIC(LocalSocketClient)
public:
  QLocalSocket *socket;
  QString serverName;
  quint32 currentDataSize; // current message body size read from socket
  bool dataJustReceived;

  explicit LocalSocketClientPrivate(Q *q)
    : q_(q),
      socket(nullptr), currentDataSize(0),
      dataJustReceived(false)
  {}

  void createSocket()
  {
    socket = new QLocalSocket(q_);
    q_->connect(socket, SIGNAL(readyRead()), SLOT(readSocket()));

    q_->connect(socket, SIGNAL(error(QLocalSocket::LocalSocketError)), SIGNAL(socketError()));
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

bool LocalSocketClientPrivate::writeSocket(const QByteArray &data, bool pack)
{ return socket && SocketService::writeSocket(socket, data, pack); }

QByteArray LocalSocketClientPrivate::readSocket()
{
  if (Q_UNLIKELY(!socket))
    return QByteArray();
  return SocketService::readSocket(socket, currentDataSize);
}

bool LocalSocketClientPrivate::waitForDataReceived(int interval)
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

void LocalSocketClientPrivate::dumpSocketInfo() const
{
  if (socket)
    DOUT("socket"
         ": serverName ="   << socket->serverName() <<
         ", state ="        << socket->state() <<
         ", error ="        << socket->errorString());
  else
    DOUT("socket = null");
}

/** Public class */

// Constructions:

LocalSocketClient::LocalSocketClient(QObject *parent)
  : Base(parent), d_(new D(this))
{}

LocalSocketClient::~LocalSocketClient() { delete d_; }

QString LocalSocketClient::serverName() const
{ return d_->serverName; }

void LocalSocketClient::setServerName(const QString &value)
{ d_->serverName = SocketService::toPipeName(value); }

void LocalSocketClient::start(QIODevice::OpenMode mode)
{
  if (!d_->socket)
    d_->createSocket();
  //d_->socket->flush();
  //d_->socket->disconnectFromServer();
  //d_->socket->close();
  d_->socket->connectToServer(d_->serverName, mode);
  DOUT("pass");
}

void LocalSocketClient::restart(QIODevice::OpenMode mode)
{
  d_->deleteSocket();
  start(mode);
  DOUT("pass");
}

void LocalSocketClient::stop()
{
  if (d_->socket && d_->socket->isOpen()) {
    d_->socket->close();
    DOUT("pass");
  }
}

bool LocalSocketClient::isConnected() const
{ return d_->socket && d_->socket->state() == QLocalSocket::ConnectedState; }

//bool LocalSocketClient::isReady() const
//{
//  return d_->socket && (
//    d_->socket->state() == QAbstractSocket::ConnectedState ||
//    d_->socket->state() == QAbstractSocket::UnconnectedState
//  );
//}

//void LocalSocketClient::waitForReady()
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

bool LocalSocketClient::sendData(const QByteArray &data, int waitTime, bool pack)
{
  bool ok = d_->writeSocket(data, pack);
  if (ok && waitTime)
    ok = d_->socket->waitForBytesWritten(waitTime);
  return ok;
}

bool LocalSocketClient::waitForConnected(int interval)
{ return d_->socket && d_->socket->waitForConnected(interval); }

bool LocalSocketClient::waitForDisconnected(int interval)
{ return d_->socket && d_->socket->waitForDisconnected(interval); }

bool LocalSocketClient::waitForBytesWritten(int interval)
{ return d_->socket && d_->socket->waitForBytesWritten(interval); }

bool LocalSocketClient::waitForReadyRead(int interval)
{ return d_->socket && d_->socket->waitForReadyRead(interval); }

bool LocalSocketClient::waitForDataReceived(int interval)
{ return d_->waitForDataReceived(interval); }

void LocalSocketClient::readSocket()
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

void LocalSocketClient::dumpSocketInfo() const { d_->dumpSocketInfo(); }

//QTSS_END_NAMESPACE

// EOF
