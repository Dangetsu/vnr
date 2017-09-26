

#ifndef SBK_PYKBSIGNAL_PYTHON_H
#define SBK_PYKBSIGNAL_PYTHON_H

#include <sbkpython.h>
#include <conversions.h>
#include <sbkenum.h>
#include <basewrapper.h>
#include <bindingmanager.h>
#include <memory>

#include <pysidesignal.h>
// Module Includes
#include <pyside_qtcore_python.h>

// Binded library includes
#include <keyboardsignal.h>
// Conversion Includes - Primitive Types
#include <QString>
#include <signalmanager.h>
#include <typeresolver.h>
#include <QtConcurrentFilter>
#include <QStringList>
#include <qabstractitemmodel.h>

// Conversion Includes - Container Types
#include <QList>
#include <QMap>
#include <QStack>
#include <QMultiMap>
#include <QVector>
#include <QPair>
#include <pysideconversions.h>
#include <QSet>
#include <QQueue>
#include <QLinkedList>

// Type indices
#define SBK_KEYBOARDSIGNAL_IDX                                       0
#define SBK_pykbsignal_IDX_COUNT                                     1

// This variable stores all Python types exported by this module.
extern PyTypeObject** SbkpykbsignalTypes;

// This variable stores all type converters exported by this module.
extern SbkConverter** SbkpykbsignalTypeConverters;

// Converter indices
#define SBK_PYKBSIGNAL_QLIST_QOBJECTPTR_IDX                          0 // const QList<QObject * > &
#define SBK_PYKBSIGNAL_QLIST_QBYTEARRAY_IDX                          1 // QList<QByteArray >
#define SBK_PYKBSIGNAL_QLIST_QVARIANT_IDX                            2 // QList<QVariant >
#define SBK_PYKBSIGNAL_QLIST_QSTRING_IDX                             3 // QList<QString >
#define SBK_PYKBSIGNAL_QMAP_QSTRING_QVARIANT_IDX                     4 // QMap<QString, QVariant >
#define SBK_pykbsignal_CONVERTERS_IDX_COUNT                          5

// Macros for type check

namespace Shiboken
{

// PyType functions, to get the PyObjectType for a type T
template<> inline PyTypeObject* SbkType< ::KeyboardSignal >() { return reinterpret_cast<PyTypeObject*>(SbkpykbsignalTypes[SBK_KEYBOARDSIGNAL_IDX]); }

} // namespace Shiboken

#endif // SBK_PYKBSIGNAL_PYTHON_H

