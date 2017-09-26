#ifndef _SOCKETSVC_QUEUEDLOCALSOCKETCLIENT_H
#define _SOCKETSVC_QUEUEDLOCALSOCKETCLIENT_H

// queuedlocalsocketclient.h
// 4/29/2014 jichi
//
// This class must be consistent with socketsvc/socketcli.py
#include "qtsocketsvc/LocalSocketClient.h"

class QueuedLocalSocketClientPrivate;
class QueuedLocalSocketClient : public LocalSocketClient
{
  Q_OBJECT
  Q_DISABLE_COPY(QueuedLocalSocketClient)
  SK_EXTEND_CLASS(QueuedLocalSocketClient, LocalSocketClient)
  SK_DECLARE_PRIVATE(QueuedLocalSocketClientPrivate)
public:
  explicit QueuedLocalSocketClient(QObject *parent = nullptr);
  ~QueuedLocalSocketClient();

  void sendDataNow(const QByteArray &data, int waitTime = 0);
  void sendDataLater(const QByteArray &data);

public slots:
  void flushSendBuffer(int waitTime = 0);
};

#endif // _SOCKETSVC_QUEUEDLOCALSOCKETCLIENT_H
