// queuedlocalsocketclient.cc
// 4/29/2014 jichi
#include "qtsocketsvc/queuedlocalsocketclient.h"
#include "qtsocketsvc/socketpack.h"
#include <QtCore/QTimer>

/** Private class */

class QueuedLocalSocketClientPrivate
{
public:
  QByteArray sendBuffer;
};

/** Public class */

// Constructions:

QueuedLocalSocketClient::QueuedLocalSocketClient(QObject *parent)
  : Base(parent), d_(new D)
{}

QueuedLocalSocketClient::~QueuedLocalSocketClient() { delete d_; }

void QueuedLocalSocketClient::flushSendBuffer(int waitTime)
{
  if (!d_->sendBuffer.isEmpty()) {
    sendData(d_->sendBuffer, waitTime, false);
    d_->sendBuffer.clear();
  }
}

void QueuedLocalSocketClient::sendDataLater(const QByteArray &data)
{
  d_->sendBuffer.append(SocketService::packPacket(data));
}

void QueuedLocalSocketClient::sendDataNow(const QByteArray &data, int waitTime)
{
  sendDataLater(data);
  flushSendBuffer(waitTime);
}

// EOF
