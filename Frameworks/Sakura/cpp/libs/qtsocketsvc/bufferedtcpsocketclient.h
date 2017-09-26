#ifndef _SOCKETSVC_BUFFEREDTCPSOCKETCLIENT_H
#define _SOCKETSVC_BUFFEREDTCPSOCKETCLIENT_H

// bufferedtcpsocketclient.h
// 4/29/2014 jichi
//
// This class must be consistent with socketsvc/socketcli.py
#include "qtsocketsvc/TcpSocketClient.h"

class BufferedTcpSocketClientPrivate;
class BufferedTcpSocketClient : public TcpSocketClient
{
  Q_OBJECT
  Q_DISABLE_COPY(BufferedTcpSocketClient)
  SK_EXTEND_CLASS(BufferedTcpSocketClient, TcpSocketClient)
  SK_DECLARE_PRIVATE(BufferedTcpSocketClientPrivate)
public:
  explicit BufferedTcpSocketClient(QObject *parent = nullptr);
  ~BufferedTcpSocketClient();

  void sendDataLater(const QByteArray &data, int interval = 200, int waitTime = 0);

public slots:
  void flushSendBuffer();
};

#endif // _SOCKETSVC_BUFFEREDTCPSOCKETCLIENT_H
