

#ifndef SBK_PYMOUSESEL_PYTHON_H
#define SBK_PYMOUSESEL_PYTHON_H

#include <sbkpython.h>
#include <conversions.h>
#include <sbkenum.h>
#include <basewrapper.h>
#include <bindingmanager.h>
#include <memory>

#include <pysidesignal.h>
// Module Includes
#include <pyside_qtcore_python.h>
#include <pyside_qtgui_python.h>

// Binded library includes
#include <mouseselector.h>
// Conversion Includes - Primitive Types
#include <QStringList>
#include <qabstractitemmodel.h>
#include <QString>
#include <signalmanager.h>
#include <typeresolver.h>
#include <QtConcurrentFilter>

// Conversion Includes - Container Types
#include <QMap>
#include <QStack>
#include <QLinkedList>
#include <QVector>
#include <QSet>
#include <QPair>
#include <pysideconversions.h>
#include <QQueue>
#include <QList>
#include <QMultiMap>

// Type indices
#define SBK_MOUSESELECTOR_IDX                                        0
#define SBK_pymousesel_IDX_COUNT                                     1

// This variable stores all Python types exported by this module.
extern PyTypeObject** SbkpymouseselTypes;

// This variable stores all type converters exported by this module.
extern SbkConverter** SbkpymouseselTypeConverters;

// Converter indices
#define SBK_PYMOUSESEL_QLIST_QOBJECTPTR_IDX                          0 // const QList<QObject * > &
#define SBK_PYMOUSESEL_QLIST_QBYTEARRAY_IDX                          1 // QList<QByteArray >
#define SBK_PYMOUSESEL_QLIST_QVARIANT_IDX                            2 // QList<QVariant >
#define SBK_PYMOUSESEL_QLIST_QSTRING_IDX                             3 // QList<QString >
#define SBK_PYMOUSESEL_QMAP_QSTRING_QVARIANT_IDX                     4 // QMap<QString, QVariant >
#define SBK_pymousesel_CONVERTERS_IDX_COUNT                          5

// Macros for type check

namespace Shiboken
{

// PyType functions, to get the PyObjectType for a type T
template<> inline PyTypeObject* SbkType< ::MouseSelector >() { return reinterpret_cast<PyTypeObject*>(SbkpymouseselTypes[SBK_MOUSESELECTOR_IDX]); }

} // namespace Shiboken

#endif // SBK_PYMOUSESEL_PYTHON_H

