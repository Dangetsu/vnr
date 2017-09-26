

#ifndef SBK_PYPINYIN_PYTHON_H
#define SBK_PYPINYIN_PYTHON_H

#include <sbkpython.h>
#include <conversions.h>
#include <sbkenum.h>
#include <basewrapper.h>
#include <bindingmanager.h>
#include <memory>

// Binded library includes
#include <pinyinconv.h>
// Conversion Includes - Primitive Types
#include <string>

// Type indices
#define SBK_PINYINCONVERTER_IDX                                      0
#define SBK_pypinyin_IDX_COUNT                                       1

// This variable stores all Python types exported by this module.
extern PyTypeObject** SbkpypinyinTypes;

// This variable stores all type converters exported by this module.
extern SbkConverter** SbkpypinyinTypeConverters;

// Converter indices
#define SBK_STD_WSTRING_IDX                                          0
#define SBK_pypinyin_CONVERTERS_IDX_COUNT                            1

// Macros for type check

namespace Shiboken
{

// PyType functions, to get the PyObjectType for a type T
template<> inline PyTypeObject* SbkType< ::PinyinConverter >() { return reinterpret_cast<PyTypeObject*>(SbkpypinyinTypes[SBK_PINYINCONVERTER_IDX]); }

} // namespace Shiboken

#endif // SBK_PYPINYIN_PYTHON_H

