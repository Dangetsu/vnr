

#ifndef SBK_PYTROSCRIPT_PYTHON_H
#define SBK_PYTROSCRIPT_PYTHON_H

#include <sbkpython.h>
#include <conversions.h>
#include <sbkenum.h>
#include <basewrapper.h>
#include <bindingmanager.h>
#include <memory>

// Binded library includes
#include <troscript.h>
// Conversion Includes - Primitive Types
#include <string>

// Type indices
#define SBK_TRANSLATIONOUTPUTSCRIPTPERFORMER_IDX                     0
#define SBK_pytroscript_IDX_COUNT                                    1

// This variable stores all Python types exported by this module.
extern PyTypeObject** SbkpytroscriptTypes;

// This variable stores all type converters exported by this module.
extern SbkConverter** SbkpytroscriptTypeConverters;

// Converter indices
#define SBK_STD_WSTRING_IDX                                          0
#define SBK_pytroscript_CONVERTERS_IDX_COUNT                         1

// Macros for type check

namespace Shiboken
{

// PyType functions, to get the PyObjectType for a type T
template<> inline PyTypeObject* SbkType< ::TranslationOutputScriptPerformer >() { return reinterpret_cast<PyTypeObject*>(SbkpytroscriptTypes[SBK_TRANSLATIONOUTPUTSCRIPTPERFORMER_IDX]); }

} // namespace Shiboken

#endif // SBK_PYTROSCRIPT_PYTHON_H

