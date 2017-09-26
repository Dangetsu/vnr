// queuedtcpocketclient.cc
// 4/29/2014 jichi
#include "qtsocketsvc/queuedtcpsocketclient.h"
#include "qtsocketsvc/socketpack.h"
#include <QtCore/QTimer>

/** Private class */

class QueuedTcpSocketClientPrivate
{
public:
  QByteArray sendBuffer;
};

/** Public class */

// Constructions:

QueuedTcpSocketClient::QueuedTcpSocketClient(QObject *parent)
  : Base(parent), d_(new D)
{}

QueuedTcpSocketClient::~QueuedTcpSocketClient() { delete d_; }

void QueuedTcpSocketClient::flushSendBuffer(int waitTime)
{
  if (!d_->sendBuffer.isEmpty()) {
    sendData(d_->sendBuffer, waitTime, false);
    d_->sendBuffer.clear();
  }
}

void QueuedTcpSocketClient::sendDataLater(const QByteArray &data)
{
  d_->sendBuffer.append(SocketService::packPacket(data));
}

void QueuedTcpSocketClient::sendDataNow(const QByteArray &data, int waitTime)
{
  sendDataLater(data);
  flushSendBuffer(waitTime);
}

// EOF
