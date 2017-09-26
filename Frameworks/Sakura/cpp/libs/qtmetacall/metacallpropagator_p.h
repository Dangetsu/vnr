#ifndef METACALLPROPAGATOR_P_H
#define METACALLPROPAGATOR_P_H

// metacallpropagator_p.h
// 4/9/2012 jichi

#include "qtmetacall/qtmetacall.h"
#include "sakurakit/skglobal.h"
#include <QtCore/QObject>

QT_FORWARD_DECLARE_CLASS(QTcpServer)
QT_FORWARD_DECLARE_CLASS(QTcpSocket)

QTMETACALL_BEGIN_NAMESPACE

class MetaCallSocketFilter;
class MetaCallSocketObserver;
//class MetaCallPropagator;
class MetaCallPropagatorPrivate : public QObject
{
  Q_OBJECT
  Q_DISABLE_COPY(MetaCallPropagatorPrivate)
  SK_EXTEND_CLASS(MetaCallPropagatorPrivate, QObject)
  //SK_DECLARE_PUBLIC(MetaCallPropagator)

public:
  MetaCallSocketFilter *filter;
  MetaCallSocketObserver *socketObserver;
  QTcpServer *server; // for receiver
  QTcpSocket *socket; // for both sender and receiver

  explicit MetaCallPropagatorPrivate(QObject *parent = nullptr);

  void createFilter(QObject *watched);

  void connectSocketObserver();
  void disconnectSocketObserver();
public slots:
  void dumpSocketInfo() const; // for Debug only
  void serverAcceptsConnection();
};

QTMETACALL_END_NAMESPACE

#endif // METACALLPROPAGATOR_P_H
