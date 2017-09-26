#pragma once
#ifdef __cplusplus

// kstl/new.h
// Kernel mode c++ extension for <new>.
// 12/9/2011 jichi
//
// All new/delete are implemented as nothrow.
//
// Explicit __cdecl is essential, since __stdcall is the default in winddk.
// Keep in mind that non-page pool is expensive.

#include "kstl/win.h"

inline void * __cdecl kstl_new(size_t size, POOL_TYPE type)
{
  if (!size)    // When the value of the expression in a direct-new-declarator is zero,
    size = 4;   // the allocation function is called to allocatean array with no elements.(ISO)

  //throw std::bad_alloc();
  return ExAllocatePool(type, size); // allocation not tagged
}

inline void __cdecl kstl_delete(void *p) throw()
{
  if (p) // checked to prevent kernel level double free fault
    ExFreePool(p);
}

inline void * __cdecl operator new(size_t size) throw()
{ return kstl_new(size, NonPagedPool); }

inline void * __cdecl operator new[](size_t size) throw()
{ return kstl_new(size, NonPagedPool); }

// Transparent to constructor, used in kstl/new_allocator.h.
inline void * __cdecl operator new(size_t, void *p) throw()
{ return p; }

inline void * __cdecl operator new[](size_t, void *p) throw()
{ return p; }

inline void __cdecl operator delete(void *p) throw()
{ kstl_delete(p); }

inline void  __cdecl operator delete[](void *p) throw()
{ kstl_delete(p); }

#endif // __cplusplus
// EOF
