

#ifndef SBK_PYVNRMEM_PYTHON_H
#define SBK_PYVNRMEM_PYTHON_H

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
#include <vnrsharedmemory.h>
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
#define SBK_VNRSHAREDMEMORY_IDX                                      0
#define SBK_pyvnrmem_IDX_COUNT                                       1

// This variable stores all Python types exported by this module.
extern PyTypeObject** SbkpyvnrmemTypes;

// This variable stores all type converters exported by this module.
extern SbkConverter** SbkpyvnrmemTypeConverters;

// Converter indices
#define SBK_PYVNRMEM_QLIST_QOBJECTPTR_IDX                            0 // const QList<QObject * > &
#define SBK_PYVNRMEM_QLIST_QBYTEARRAY_IDX                            1 // QList<QByteArray >
#define SBK_PYVNRMEM_QLIST_QVARIANT_IDX                              2 // QList<QVariant >
#define SBK_PYVNRMEM_QLIST_QSTRING_IDX                               3 // QList<QString >
#define SBK_PYVNRMEM_QMAP_QSTRING_QVARIANT_IDX                       4 // QMap<QString, QVariant >
#define SBK_pyvnrmem_CONVERTERS_IDX_COUNT                            5

// Macros for type check

namespace Shiboken
{

// PyType functions, to get the PyObjectType for a type T
template<> inline PyTypeObject* SbkType< ::VnrSharedMemory >() { return reinterpret_cast<PyTypeObject*>(SbkpyvnrmemTypes[SBK_VNRSHAREDMEMORY_IDX]); }

} // namespace Shiboken

#endif // SBK_PYVNRMEM_PYTHON_H

