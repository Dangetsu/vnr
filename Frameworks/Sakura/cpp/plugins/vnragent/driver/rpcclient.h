#pragma once

// rpcclient.h
// 2/1/2013 jichi

#include "sakurakit/skglobal.h"
#include <QtCore/QObject>

class RpcClientPrivate;
class RpcClient : public QObject
{
  Q_OBJECT
  Q_DISABLE_COPY(RpcClient)
  SK_EXTEND_CLASS(RpcClient, QObject)
  SK_DECLARE_PRIVATE(RpcClientPrivate)

public:
  static Self *instance();
  explicit RpcClient(QObject *parent = nullptr);
  ~RpcClient();
  bool isActive() const;
  void quit();

  bool waitForDataReceived(int interval); // wait until after the server message is received and emit

  // - API -
signals:
  void detachRequested(); // unload this DLL
  void disableRequested();
  void clearTranslationRequested();

  void reconnected(); // server close/open
  void disconnected(); // server disconnected
  void aborted(); // the last communication was aborted

  void settingsReceived(QString json);

  // Window
  void clearWindowTranslationRequested();
  void enableWindowTranslationRequested(bool t);
  void windowTranslationReceived(QString json); // json: {hash:text}

  // Engine
  void clearEngineRequested();
  void enableEngineRequested(bool t);
  void engineTranslationReceived(QString text, qint64 hash, int role, QString language);

public slots:
  void sendEngineName(const QString &name);
  void sendEngineText(const QString &text, qint64 hash, long signature, int role, bool needsTranslation);
  void requestWindowTranslation(const QString &json); // json: {hash:text}

  void growlMessage(const QString &message);
  void growlWarning(const QString &message);
  void growlError(const QString &message);
  void growlNotification(const QString &message);

  // Direct IO bypassing Qt, blocking
public:
  void directSendEngineText(const QString &text, qint64 hash, long signature, int role, bool needsTranslation);
};

// EOF
