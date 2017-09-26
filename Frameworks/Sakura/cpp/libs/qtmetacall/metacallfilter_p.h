#ifndef METACALLFILTER_P_H
#define METACALLFILTER_P_H

// metacallfilter_p.h
// 4/9/2012 jichi

#include "qtmetacall/qtmetacall.h"
#include "sakurakit/skglobal.h"
#include <QtCore/QObject>

QT_FORWARD_DECLARE_CLASS(QMetaCallEvent)
QT_FORWARD_DECLARE_CLASS(QAbstractSocket)

QTMETACALL_BEGIN_NAMESPACE

class MetaCallRouter;
class MetaCallSocketFilterPrivate;
class MetaCallSocketFilter : public QObject
{
  Q_OBJECT
  Q_DISABLE_COPY(MetaCallSocketFilter)
  SK_EXTEND_CLASS(MetaCallSocketFilter, QObject)
  SK_DECLARE_PRIVATE(MetaCallSocketFilterPrivate)

public:
  explicit MetaCallSocketFilter(QObject *parent = nullptr);
  ~MetaCallSocketFilter();

  bool eventFilter(QObject *watched, QEvent *e) override;

  ///  Do not take the ownership of the socket. Connect readyRead with readSocket signal.
  void setSocket(QAbstractSocket *socket);

  ///  Supposed to be the same object installed with this filter
  void setWatchedObject(QObject *obj);

  ///  Return if has active socket
  bool isActive() const;

  MetaCallRouter *router() const;
  void setRouter(MetaCallRouter *value);

protected slots:
  ///  Read event from socket and dispatch to the watched object
  void readSocket();
protected:
  ///  Send event to socket
  void writeSocket(const QMetaCallEvent *e);
};

QTMETACALL_END_NAMESPACE

#endif // METACALLFILTER_P_H
