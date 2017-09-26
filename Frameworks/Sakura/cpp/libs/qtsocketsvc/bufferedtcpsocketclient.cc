// bufferedtcpsocketclient.cc
// 4/29/2014 jichi
#include "qtsocketsvc/bufferedtcpsocketclient.h"
#include "qtsocketsvc/socketpack.h"
#include <QtCore/QTimer>

/** Private class */

class BufferedTcpSocketClientPrivate
{
  SK_DECLARE_PUBLIC(BufferedTcpSocketClient)
public:
  QByteArray sendBuffer;
  QTimer *sendTimer;
  int sendWaitTime;

  explicit BufferedTcpSocketClientPrivate(Q *q)
    : q_(q), sendWaitTime(0)
  {
    sendTimer = new QTimer(q);
    sendTimer->setSingleShot(true);
    q_->connect(sendTimer, SIGNAL(timeout()), SLOT(flushSendBuffer()));
  }

  void flushSendBuffer();
};


void BufferedTcpSocketClientPrivate::flushSendBuffer()
{
  if (sendTimer->isActive())
    sendTimer->stop();
  if (!sendBuffer.isEmpty()) {
    q_->sendData(sendBuffer, sendWaitTime, false);
    sendBuffer.clear();
  }
}


/** Public class */

// Constructions:

BufferedTcpSocketClient::BufferedTcpSocketClient(QObject *parent)
  : Base(parent), d_(new D(this))
{}

BufferedTcpSocketClient::~BufferedTcpSocketClient() { delete d_; }

void BufferedTcpSocketClient::flushSendBuffer() { d_->flushSendBuffer(); }

void BufferedTcpSocketClient::sendDataLater(const QByteArray &data, int interval, int waitTime)
{
  d_->sendBuffer.append(SocketService::packPacket(data));
  d_->sendTimer->start(interval);
  d_->sendWaitTime = waitTime;
}

// EOF
