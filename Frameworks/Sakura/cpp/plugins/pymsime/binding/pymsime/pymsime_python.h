

#ifndef SBK_PYMSIME_PYTHON_H
#define SBK_PYMSIME_PYTHON_H

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
#include <pymsime.h>
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
#define SBK_MSIME_IDX                                                0
#define SBK_MSIME_RUBY_IDX                                           2
#define SBK_MSIME_LANGUAGE_IDX                                       1
#define SBK_pymsime_IDX_COUNT                                        3

// This variable stores all Python types exported by this module.
extern PyTypeObject** SbkpymsimeTypes;

// This variable stores all type converters exported by this module.
extern SbkConverter** SbkpymsimeTypeConverters;

// Converter indices
#define SBK_PYMSIME_QPAIR_QSTRING_QSTRING_IDX                        0 // QPair<QString, QString >
#define SBK_PYMSIME_QLIST_QPAIR_QSTRING_QSTRING_IDX                  1 // QList<QPair<QString, QString > >
#define SBK_PYMSIME_QLIST_QVARIANT_IDX                               2 // QList<QVariant >
#define SBK_PYMSIME_QLIST_QSTRING_IDX                                3 // QList<QString >
#define SBK_PYMSIME_QMAP_QSTRING_QVARIANT_IDX                        4 // QMap<QString, QVariant >
#define SBK_pymsime_CONVERTERS_IDX_COUNT                             5

// Macros for type check

namespace Shiboken
{

// PyType functions, to get the PyObjectType for a type T
template<> inline PyTypeObject* SbkType< ::Msime::Ruby >() { return SbkpymsimeTypes[SBK_MSIME_RUBY_IDX]; }
template<> inline PyTypeObject* SbkType< ::Msime::Language >() { return SbkpymsimeTypes[SBK_MSIME_LANGUAGE_IDX]; }
template<> inline PyTypeObject* SbkType< ::Msime >() { return reinterpret_cast<PyTypeObject*>(SbkpymsimeTypes[SBK_MSIME_IDX]); }

} // namespace Shiboken

#endif // SBK_PYMSIME_PYTHON_H

