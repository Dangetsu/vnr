

#ifndef SBK_PYHANJA_PYTHON_H
#define SBK_PYHANJA_PYTHON_H

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
#include <qhanjahangulconv.h>
#include <qhangulhanjaconv.h>
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
#define SBK_QHANGULHANJACONVERTER_IDX                                0
#define SBK_QHANJAHANGULCONVERTER_IDX                                1
#define SBK_pyhanja_IDX_COUNT                                        2

// This variable stores all Python types exported by this module.
extern PyTypeObject** SbkpyhanjaTypes;

// This variable stores all type converters exported by this module.
extern SbkConverter** SbkpyhanjaTypeConverters;

// Converter indices
#define SBK_PYHANJA_QPAIR_QSTRING_QSTRING_IDX                        0 // QPair<QString, QString >
#define SBK_PYHANJA_QLIST_QPAIR_QSTRING_QSTRING_IDX                  1 // QList<QPair<QString, QString > >
#define SBK_PYHANJA_QLIST_QLIST_QPAIR_QSTRING_QSTRING_IDX            2 // QList<QList<QPair<QString, QString > > >
#define SBK_PYHANJA_QLIST_QVARIANT_IDX                               3 // QList<QVariant >
#define SBK_PYHANJA_QLIST_QSTRING_IDX                                4 // QList<QString >
#define SBK_PYHANJA_QMAP_QSTRING_QVARIANT_IDX                        5 // QMap<QString, QVariant >
#define SBK_pyhanja_CONVERTERS_IDX_COUNT                             6

// Macros for type check

namespace Shiboken
{

// PyType functions, to get the PyObjectType for a type T
template<> inline PyTypeObject* SbkType< ::QHangulHanjaConverter >() { return reinterpret_cast<PyTypeObject*>(SbkpyhanjaTypes[SBK_QHANGULHANJACONVERTER_IDX]); }
template<> inline PyTypeObject* SbkType< ::QHanjaHangulConverter >() { return reinterpret_cast<PyTypeObject*>(SbkpyhanjaTypes[SBK_QHANJAHANGULCONVERTER_IDX]); }

} // namespace Shiboken

#endif // SBK_PYHANJA_PYTHON_H

