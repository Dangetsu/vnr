#ifndef D_QOBJECT_H
#define D_QOBJECT_H

// d_qobject.h
// 12/9/2012 jichi

#include <QtCore/QObject>

QT_FORWARD_DECLARE_CLASS(QObjectPrivate)

namespace QtPrivate {

class DQObject : public QObject
{
  DQObject() {}
public:
  // QObjectPrivate inherits QObjectData
  QObjectPrivate *d() const { return reinterpret_cast<QObjectPrivate *>(d_ptr.data()); }
};

inline QObjectPrivate *d_qobject(const QObject *q)
{ return !q ? nullptr : static_cast<const DQObject *>(q)->d(); }

template <typename T>
inline T d_q(const QObject *q)
{ return static_cast<T>(d_qobject(q)); } // dynanmic_cast not used to avoid linking

} // namespace QtPrivate

#endif // D_QOBJECT_H
