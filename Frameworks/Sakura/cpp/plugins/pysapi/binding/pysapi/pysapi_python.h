

#ifndef SBK_PYSAPI_PYTHON_H
#define SBK_PYSAPI_PYTHON_H

#include <sbkpython.h>
#include <conversions.h>
#include <sbkenum.h>
#include <basewrapper.h>
#include <bindingmanager.h>
#include <memory>

// Binded library includes
#include <pysapi.h>
// Conversion Includes - Primitive Types
#include <string>

// Type indices
#define SBK_SAPIPLAYER_IDX                                           0
#define SBK_pysapi_IDX_COUNT                                         1

// This variable stores all Python types exported by this module.
extern PyTypeObject** SbkpysapiTypes;

// This variable stores all type converters exported by this module.
extern SbkConverter** SbkpysapiTypeConverters;

// Converter indices
#define SBK_STD_WSTRING_IDX                                          0
#define SBK_pysapi_CONVERTERS_IDX_COUNT                              1

// Macros for type check

namespace Shiboken
{

// PyType functions, to get the PyObjectType for a type T
template<> inline PyTypeObject* SbkType< ::SapiPlayer >() { return reinterpret_cast<PyTypeObject*>(SbkpysapiTypes[SBK_SAPIPLAYER_IDX]); }

} // namespace Shiboken

#endif // SBK_PYSAPI_PYTHON_H

