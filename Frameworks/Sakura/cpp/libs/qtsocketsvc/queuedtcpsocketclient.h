#ifndef _SOCKETSVC_QUEUEDTCPSOCKETCLIENT_H
#define _SOCKETSVC_QUEUEDTCPSOCKETCLIENT_H

// queuedtcpsocketclient.h
// 4/29/2014 jichi
//
// This class must be consistent with socketsvc/socketcli.py
#include "qtsocketsvc/TcpSocketClient.h"

class QueuedTcpSocketClientPrivate;
class QueuedTcpSocketClient : public TcpSocketClient
{
  Q_OBJECT
  Q_DISABLE_COPY(QueuedTcpSocketClient)
  SK_EXTEND_CLASS(QueuedTcpSocketClient, TcpSocketClient)
  SK_DECLARE_PRIVATE(QueuedTcpSocketClientPrivate)
public:
  explicit QueuedTcpSocketClient(QObject *parent = nullptr);
  ~QueuedTcpSocketClient();

  void sendDataNow(const QByteArray &data, int waitTime = 0);
  void sendDataLater(const QByteArray &data);

public slots:
  void flushSendBuffer(int waitTime = 0);
};

#endif // _SOCKETSVC_QUEUEDTCPSOCKETCLIENT_H
