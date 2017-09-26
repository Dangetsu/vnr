

#ifndef SBK_PYRICH_PYTHON_H
#define SBK_PYRICH_PYTHON_H

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
#include <richrubyparser.h>
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
#define SBK_RICHRUBYPARSER_IDX                                       0
#define SBK_pyrich_IDX_COUNT                                         1

// This variable stores all Python types exported by this module.
extern PyTypeObject** SbkpyrichTypes;

// This variable stores all type converters exported by this module.
extern SbkConverter** SbkpyrichTypeConverters;

// Converter indices
#define SBK_PYRICH_QLIST_QVARIANT_IDX                                0 // QList<QVariant >
#define SBK_PYRICH_QLIST_QSTRING_IDX                                 1 // QList<QString >
#define SBK_PYRICH_QMAP_QSTRING_QVARIANT_IDX                         2 // QMap<QString, QVariant >
#define SBK_pyrich_CONVERTERS_IDX_COUNT                              3

// Macros for type check

namespace Shiboken
{

// PyType functions, to get the PyObjectType for a type T
template<> inline PyTypeObject* SbkType< ::RichRubyParser >() { return reinterpret_cast<PyTypeObject*>(SbkpyrichTypes[SBK_RICHRUBYPARSER_IDX]); }

} // namespace Shiboken

#endif // SBK_PYRICH_PYTHON_H

