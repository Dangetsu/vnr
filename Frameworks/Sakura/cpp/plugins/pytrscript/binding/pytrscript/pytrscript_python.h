

#ifndef SBK_PYTRSCRIPT_PYTHON_H
#define SBK_PYTRSCRIPT_PYTHON_H

#include <sbkpython.h>
#include <conversions.h>
#include <sbkenum.h>
#include <basewrapper.h>
#include <bindingmanager.h>
#include <memory>

// Binded library includes
#include <trscript.h>
// Conversion Includes - Primitive Types
#include <string>

// Type indices
#define SBK_TRANSLATIONSCRIPTPERFORMER_IDX                           0
#define SBK_pytrscript_IDX_COUNT                                     1

// This variable stores all Python types exported by this module.
extern PyTypeObject** SbkpytrscriptTypes;

// This variable stores all type converters exported by this module.
extern SbkConverter** SbkpytrscriptTypeConverters;

// Converter indices
#define SBK_STD_WSTRING_IDX                                          0
#define SBK_pytrscript_CONVERTERS_IDX_COUNT                          1

// Macros for type check

namespace Shiboken
{

// PyType functions, to get the PyObjectType for a type T
template<> inline PyTypeObject* SbkType< ::TranslationScriptPerformer >() { return reinterpret_cast<PyTypeObject*>(SbkpytrscriptTypes[SBK_TRANSLATIONSCRIPTPERFORMER_IDX]); }

} // namespace Shiboken

#endif // SBK_PYTRSCRIPT_PYTHON_H

