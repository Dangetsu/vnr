#ifndef _SOCKETSVC_TCPSOCKETCLIENT_H
#define _SOCKETSVC_TCPSOCKETCLIENT_H

// tcpsocketclient.h
// 4/29/2014 jichi
//
// This class must be consistent with socketsvc/socketcli.py
#include "sakurakit/skglobal.h"
#include <QtCore/QIODevice>

class TcpSocketClientPrivate;
class TcpSocketClient : public QObject
{
  Q_OBJECT
  Q_DISABLE_COPY(TcpSocketClient)
  SK_EXTEND_CLASS(TcpSocketClient, QObject)
  SK_DECLARE_PRIVATE(TcpSocketClientPrivate)
public:
  explicit TcpSocketClient(QObject *parent = nullptr);
  ~TcpSocketClient();

  // Properties:
  int port() const;
  void setPort(int value);

  QString address() const;
  void setAddress(const QString &value);

  bool isConnected() const;
  //bool isReady() const;

  // Actions:
public:
  void start(QIODevice::OpenMode mode = QIODevice::ReadWrite);
  void restart(QIODevice::OpenMode mode = QIODevice::ReadWrite);
  void stop();
  //void waitForReady();

  bool sendData(const QByteArray &data, int waitTime = 0, bool pack = true);

  // QAbstractSocket default wait time is 30 seconds
  bool waitForConnected(int interval = 30000);
  bool waitForDisconnected(int interval = 30000);
  bool waitForBytesWritten(int interval = 30000);
  bool waitForReadyRead(int interval = 30000);

  // Invoked just after the dataReceived is emit
  bool waitForDataReceived(int interval = 30000);

  void dumpSocketInfo() const; // for debug only

signals:
  void connected();
  void disconnected();
  void socketError();
  void dataReceived(QByteArray data);

private slots:
  /**
   *  Invoked by QAbstractSocket::readyRead.
   *  Leave it in the public class as it  might be better to use  virutal protected in the future.
   */
  void readSocket();
};

#endif // _SOCKETSVC_TCPSOCKETCLIENT_H
