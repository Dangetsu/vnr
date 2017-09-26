#ifndef METACALLTHREAD_P_H
#define METACALLTHREAD_P_H

// metacallthread_p.h
// 4/27/2014 jichi

#include "qtmetacall/qtmetacall.h"
#include "sakurakit/skglobal.h"
#include <QtCore/QObject>

QTMETACALL_BEGIN_NAMESPACE

class MetaCallPropagator;
class MetaCallThread;
class MetaCallThreadPrivate : public QObject
{
  Q_OBJECT
  Q_DISABLE_COPY(MetaCallThreadPrivate)
  SK_EXTEND_CLASS(MetaCallThreadPrivate, QObject)
  //SK_DECLARE_PUBLIC(MetaCallThread)

  friend class MetaCallThread;
public:
  MetaCallPropagator *propagator;

  enum Role { ClientRole = 0, ServerRole };
  Role role;

  QString address;
  int port;

  explicit MetaCallThreadPrivate(QObject *parent = nullptr);

  void connectPropagator();
  void disconnectPropagator();

signals:
  void stopRequested();
};

QTMETACALL_END_NAMESPACE

#endif // METACALLTHREAD_P_H
