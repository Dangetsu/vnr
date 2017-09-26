#ifndef METACALLOBSERVER_H
#define METACALLOBSERVER_H

// metacallobserver.h
// 4/26/2014 jichi

#include "qtmetacall/qtmetacall.h"
#include "sakurakit/skglobal.h"
#include <QtCore/QObject>

QTMETACALL_BEGIN_NAMESPACE

class MetaCallPropagator;
class MetaCallSocketObserver : public QObject
{
  Q_OBJECT
  Q_DISABLE_COPY(MetaCallSocketObserver)
  SK_EXTEND_CLASS(MetaCallSocketObserver, QObject)
  friend class MetaCallPropagator;
public:
  explicit MetaCallSocketObserver(QObject *parent) : Base(parent) {}
signals:
  void connected();
  void disconnected();
  void error();
};

QTMETACALL_END_NAMESPACE

#endif // METACALLOBSERVER_H
