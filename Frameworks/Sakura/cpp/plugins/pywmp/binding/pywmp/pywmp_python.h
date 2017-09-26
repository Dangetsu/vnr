

#ifndef SBK_PYWMP_PYTHON_H
#define SBK_PYWMP_PYTHON_H

#include <sbkpython.h>
#include <conversions.h>
#include <sbkenum.h>
#include <basewrapper.h>
#include <bindingmanager.h>
#include <memory>

// Binded library includes
#include <pywmp.h>
// Conversion Includes - Primitive Types
#include <string>

// Type indices
#define SBK_WINDOWSMEDIAPLAYER_IDX                                   0
#define SBK_pywmp_IDX_COUNT                                          1

// This variable stores all Python types exported by this module.
extern PyTypeObject** SbkpywmpTypes;

// This variable stores all type converters exported by this module.
extern SbkConverter** SbkpywmpTypeConverters;

// Converter indices
#define SBK_STD_WSTRING_IDX                                          0
#define SBK_pywmp_CONVERTERS_IDX_COUNT                               1

// Macros for type check

namespace Shiboken
{

// PyType functions, to get the PyObjectType for a type T
template<> inline PyTypeObject* SbkType< ::WindowsMediaPlayer >() { return reinterpret_cast<PyTypeObject*>(SbkpywmpTypes[SBK_WINDOWSMEDIAPLAYER_IDX]); }

} // namespace Shiboken

#endif // SBK_PYWMP_PYTHON_H

