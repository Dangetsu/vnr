// bufferedlocalsocketclient.cc
// 4/29/2014 jichi
#include "qtsocketsvc/bufferedlocalsocketclient.h"
#include "qtsocketsvc/socketpack.h"
#include <QtCore/QTimer>

/** Private class */

class BufferedLocalSocketClientPrivate
{
  SK_DECLARE_PUBLIC(BufferedLocalSocketClient)
public:
  QByteArray sendBuffer;
  QTimer *sendTimer;
  int sendWaitTime;

  explicit BufferedLocalSocketClientPrivate(Q *q)
    : q_(q), sendWaitTime(0)
  {
    sendTimer = new QTimer(q);
    sendTimer->setSingleShot(true);
    q_->connect(sendTimer, SIGNAL(timeout()), SLOT(flushSendBuffer()));
  }

  void flushSendBuffer();
};


void BufferedLocalSocketClientPrivate::flushSendBuffer()
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

BufferedLocalSocketClient::BufferedLocalSocketClient(QObject *parent)
  : Base(parent), d_(new D(this))
{}

BufferedLocalSocketClient::~BufferedLocalSocketClient() { delete d_; }

void BufferedLocalSocketClient::flushSendBuffer() { d_->flushSendBuffer(); }

void BufferedLocalSocketClient::sendDataLater(const QByteArray &data, int interval, int waitTime)
{
  d_->sendBuffer.append(SocketService::packPacket(data));
  d_->sendTimer->start(interval);
  d_->sendWaitTime = waitTime;
}

// EOF
