#pragma once
#ifdef __cplusplus

// kstl/allocator.h
// 12/11/2011

#include "kstl/new_allocator.h"

#define kstl_allocator kstd::new_allocator

namespace kstd {

template<typename _Tp>
  class allocator;

/// allocator<void> specialization.
template<>
  class allocator<void>
  {
  public:
    typedef size_t      size_type;
    typedef ptrdiff_t   difference_type;
    typedef void*       pointer;
    typedef const void* const_pointer;
    typedef void        value_type;

    template<typename _Tp1>
      struct rebind
      { typedef allocator<_Tp1> other; };
  };

/**
 * @brief  The @a standard allocator, as per [20.4].
 * @ingroup allocators
 *
 *  Further details:
 *  http://gcc.gnu.org/onlinedocs/libstdc++/manual/bk01pt04ch11.html
 */
template<typename _Tp>
  class allocator: public kstl_allocator<_Tp>
  {
    typedef allocator<_Tp>        _Self;
    typedef kstl_allocator<_Tp>   _Base;
 public:
    typedef size_t     size_type;
    typedef ptrdiff_t  difference_type;
    typedef _Tp*       pointer;
    typedef const _Tp* const_pointer;
    typedef _Tp&       reference;
    typedef const _Tp& const_reference;
    typedef _Tp        value_type;

    template<typename _Tp1>
      struct rebind
      { typedef allocator<_Tp1> other; };

    allocator() throw() {}

    allocator(const allocator& __a) throw()
    : _Base(__a) {}

    template<typename _Tp1>
      allocator(const allocator<_Tp1>&) throw() {}

    ~allocator() throw() {}

    // Inherit everything else.
  };

template<typename _T1, typename _T2>
  inline bool
  operator==(const allocator<_T1>&, const allocator<_T2>&)
  { return true; }

template<typename _Tp>
  inline bool
  operator==(const allocator<_Tp>&, const allocator<_Tp>&)
  { return true; }

template<typename _T1, typename _T2>
  inline bool
  operator!=(const allocator<_T1>&, const allocator<_T2>&)
  { return false; }

template<typename _Tp>
  inline bool
  operator!=(const allocator<_Tp>&, const allocator<_Tp>&)
  { return false; }

} // namespace kstd

#endif // __cplusplus
