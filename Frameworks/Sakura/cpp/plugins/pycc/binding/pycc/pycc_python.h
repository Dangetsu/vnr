

#ifndef SBK_PYCC_PYTHON_H
#define SBK_PYCC_PYTHON_H

#include <sbkpython.h>
#include <conversions.h>
#include <sbkenum.h>
#include <basewrapper.h>
#include <bindingmanager.h>
#include <memory>

// Binded library includes
#include <simplecc.h>
// Conversion Includes - Primitive Types
#include <string>

// Type indices
#define SBK_SIMPLECHINESECONVERTER_IDX                               0
#define SBK_pycc_IDX_COUNT                                           1

// This variable stores all Python types exported by this module.
extern PyTypeObject** SbkpyccTypes;

// This variable stores all type converters exported by this module.
extern SbkConverter** SbkpyccTypeConverters;

// Converter indices
#define SBK_STD_WSTRING_IDX                                          0
#define SBK_pycc_CONVERTERS_IDX_COUNT                                1

// Macros for type check

namespace Shiboken
{

// PyType functions, to get the PyObjectType for a type T
template<> inline PyTypeObject* SbkType< ::SimpleChineseConverter >() { return reinterpret_cast<PyTypeObject*>(SbkpyccTypes[SBK_SIMPLECHINESECONVERTER_IDX]); }

} // namespace Shiboken

#endif // SBK_PYCC_PYTHON_H

