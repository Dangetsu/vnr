#pragma once
#ifdef __cplusplus

// new_allocator.h
// 12/11/2011 jichi
#include "kstl/new.h"
#include "kstl/move.h"

namespace kstd {

/**
 *  @brief  An allocator that uses global new, as per [20.4].
 *  @ingroup allocators
 *
 *  This is precisely the allocator defined in the C++ Standard.
 *    - all allocation calls operator new
 *    - all deallocation calls operator delete
 */
template<typename _Tp>
  class new_allocator
  {
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
      { typedef new_allocator<_Tp1> other; };

    new_allocator() throw() {}

    new_allocator(const new_allocator&) throw() {}

    template<typename _Tp1>
      new_allocator(const new_allocator<_Tp1>&) throw() {}

    ~new_allocator() throw() {}

    pointer
    address(reference __x) const { return std::__addressof(__x); }

    const_pointer
    address(const_reference __x) const { return std::__addressof(__x); }

    // NB: __n is permitted to be 0.  The C++ standard says nothing
    // about what the return value is when __n == 0.
    pointer
    allocate(size_type __n, const void* = 0) throw()
    {
      //if (__n > this->max_size())
      //  std::__throw_bad_alloc();

      return static_cast<_Tp*>(::operator new(__n * sizeof(_Tp)));
    }

    // __p is not permitted to be a null pointer.
    void
    deallocate(pointer __p, size_type)
    { ::operator delete(__p); }

    size_type
    max_size() const throw()
    { return size_t(-1) / sizeof(_Tp); }

    // 402. wrong new expression in [some_] allocator::construct
    // jichi FIXME: assignment is used rather than copy ctor.
    void
    construct(pointer __p, const _Tp& __val)
    { ::new((void *)__p) _Tp(__val); }

    void
    destroy(pointer __p) { __p->~_Tp(); }
  };

template<typename _Tp>
  inline bool
  operator==(const new_allocator<_Tp>&, const new_allocator<_Tp>&)
  { return true; }

template<typename _Tp>
  inline bool
  operator!=(const new_allocator<_Tp>&, const new_allocator<_Tp>&)
  { return false; }

} // namespace kstd

#endif // __cplusplus
