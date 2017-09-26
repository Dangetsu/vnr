

#ifndef SBK_PYZUNKO_PYTHON_H
#define SBK_PYZUNKO_PYTHON_H

#include <sbkpython.h>
#include <conversions.h>
#include <sbkenum.h>
#include <basewrapper.h>
#include <bindingmanager.h>
#include <memory>

// Binded library includes
#include <aitalked.h>
// Conversion Includes - Primitive Types
#include <string>

// Type indices
#define SBK_AITALKSYNTHESIZER_IDX                                    0
#define SBK_pyzunko_IDX_COUNT                                        1

// This variable stores all Python types exported by this module.
extern PyTypeObject** SbkpyzunkoTypes;

// This variable stores all type converters exported by this module.
extern SbkConverter** SbkpyzunkoTypeConverters;

// Converter indices
#define SBK_STD_WSTRING_IDX                                          0
#define SBK_pyzunko_CONVERTERS_IDX_COUNT                             1

// Macros for type check

namespace Shiboken
{

// PyType functions, to get the PyObjectType for a type T
template<> inline PyTypeObject* SbkType< ::AITalkSynthesizer >() { return reinterpret_cast<PyTypeObject*>(SbkpyzunkoTypes[SBK_AITALKSYNTHESIZER_IDX]); }

} // namespace Shiboken

#endif // SBK_PYZUNKO_PYTHON_H

