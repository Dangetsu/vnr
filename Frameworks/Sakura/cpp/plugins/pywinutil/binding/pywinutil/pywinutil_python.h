

#ifndef SBK_PYWINUTIL_PYTHON_H
#define SBK_PYWINUTIL_PYTHON_H

#include <sbkpython.h>
#include <conversions.h>
#include <sbkenum.h>
#include <basewrapper.h>
#include <bindingmanager.h>
#include <memory>

// Binded library includes
#include <pywinutil.h>
// Conversion Includes - Primitive Types
#include <string>

// Type indices
#define SBK_WINUTIL_IDX                                              0
#define SBK_pywinutil_IDX_COUNT                                      1

// This variable stores all Python types exported by this module.
extern PyTypeObject** SbkpywinutilTypes;

// This variable stores all type converters exported by this module.
extern SbkConverter** SbkpywinutilTypeConverters;

// Converter indices
#define SBK_STD_WSTRING_IDX                                          0
#define SBK_pywinutil_CONVERTERS_IDX_COUNT                           1

// Macros for type check

namespace Shiboken
{

// PyType functions, to get the PyObjectType for a type T

} // namespace Shiboken

#endif // SBK_PYWINUTIL_PYTHON_H

