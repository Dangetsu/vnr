#pragma once
// kstl/type.h
// 12/17/2011 jichi

#include "kstl/win.h"


// - Type checking -

#ifdef __cplusplus

template <typename _Tp>
inline bool
kstl_is_bad_object(const _Tp *fo)
{ return fo->__kstl_unknown_type__; }

// FILE_OBJECT::Type = 5
// See: http://msdn.microsoft.com/en-us/library/windows/hardware/ff545834(v=vs.85).aspx
template <>
inline bool
kstl_is_bad_object<FILE_OBJECT>(const FILE_OBJECT *ffo)
{ return !ffo || ffo->Size != sizeof(*ffo) || ffo->Type != 5; }

#endif // __cplusplus

// EOF
