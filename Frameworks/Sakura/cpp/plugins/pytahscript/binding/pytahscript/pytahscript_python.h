

#ifndef SBK_PYTAHSCRIPT_PYTHON_H
#define SBK_PYTAHSCRIPT_PYTHON_H

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
#include <tahscript.h>
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
#define SBK_TAHSCRIPTMANAGER_IDX                                     0
#define SBK_pytahscript_IDX_COUNT                                    1

// This variable stores all Python types exported by this module.
extern PyTypeObject** SbkpytahscriptTypes;

// This variable stores all type converters exported by this module.
extern SbkConverter** SbkpytahscriptTypeConverters;

// Converter indices
#define SBK_PYTAHSCRIPT_QLIST_QVARIANT_IDX                           0 // QList<QVariant >
#define SBK_PYTAHSCRIPT_QLIST_QSTRING_IDX                            1 // QList<QString >
#define SBK_PYTAHSCRIPT_QMAP_QSTRING_QVARIANT_IDX                    2 // QMap<QString, QVariant >
#define SBK_pytahscript_CONVERTERS_IDX_COUNT                         3

// Macros for type check

namespace Shiboken
{

// PyType functions, to get the PyObjectType for a type T
template<> inline PyTypeObject* SbkType< ::TahScriptManager >() { return reinterpret_cast<PyTypeObject*>(SbkpytahscriptTypes[SBK_TAHSCRIPTMANAGER_IDX]); }

} // namespace Shiboken

#endif // SBK_PYTAHSCRIPT_PYTHON_H

