#ifndef _SOCKETSVC_BUFFEREDLOCALSOCKETCLIENT_H
#define _SOCKETSVC_BUFFEREDLOCALSOCKETCLIENT_H

// bufferedlocalsocketclient.h
// 4/29/2014 jichi
//
// This class must be consistent with socketsvc/socketcli.py
#include "qtsocketsvc/LocalSocketClient.h"

class BufferedLocalSocketClientPrivate;
class BufferedLocalSocketClient : public LocalSocketClient
{
  Q_OBJECT
  Q_DISABLE_COPY(BufferedLocalSocketClient)
  SK_EXTEND_CLASS(BufferedLocalSocketClient, LocalSocketClient)
  SK_DECLARE_PRIVATE(BufferedLocalSocketClientPrivate)
public:
  explicit BufferedLocalSocketClient(QObject *parent = nullptr);
  ~BufferedLocalSocketClient();

  void sendDataLater(const QByteArray &data, int interval = 200, int waitTime = 0);

public slots:
  void flushSendBuffer();
};

#endif // _SOCKETSVC_BUFFEREDLOCALSOCKETCLIENT_H
