#ifndef METACALLTHREAD_H
#define METACALLTHREAD_H

// metacallthread.h
// 4/27/2014 jichi

#include "qtmetacall/qtmetacall.h"
#include "sakurakit/skglobal.h"
#include <QtCore/QThread>

QTMETACALL_BEGIN_NAMESPACE

class MetaCallPropagator;
class MetaCallThreadPrivate;
/**
 *  All signals in this class will be propagated to the remote object.
 *  DO NOT USE LOCAL SIGNALS
 */
class MetaCallThread : public QThread
{
  Q_OBJECT
  Q_DISABLE_COPY(MetaCallThread)
  SK_EXTEND_CLASS(MetaCallThread, QThread)
  SK_DECLARE_PRIVATE(MetaCallThreadPrivate)

public:
  explicit MetaCallThread(QObject *parent = nullptr);
  ~MetaCallThread();

  MetaCallPropagator *propagator() const;
  void setPropagator(MetaCallPropagator *value); ///< Do not take ownership

  void startServer(const QString &address, int port);
  void startClient(const QString &address, int port);

public slots:
  ///  Wait until ready. Only needed by client.
  void waitForReady() const;

  ///  Stop server/client
  void stop();

protected:
  void run() override;
};

QTMETACALL_END_NAMESPACE

#endif // METACALLTHREAD_H
