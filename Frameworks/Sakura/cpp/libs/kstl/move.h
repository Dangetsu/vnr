#pragma once
#ifdef __cplusplus

// kstl/move.h
// 12/11/2011 jichi
// Modified from bits/move.h, g++ 4.6.2

namespace kstd {

// Used, in C++03 mode too, by allocators, etc.
template<typename _Tp>
  inline _Tp*
  __addressof(_Tp& __r)
  {
    return reinterpret_cast<_Tp*>
      (&const_cast<char&>(reinterpret_cast<const volatile char&>(__r)));
  }

/**
 *  @brief Returns the actual address of the object or function
 *         referenced by r, even in the presence of an overloaded
 *         operator&.
 *  @param  __r  Reference to an object or function.
 *  @return   The actual address.
*/
template<typename _Tp>
  inline _Tp*
  addressof(_Tp& __r)
  { return __addressof(__r); }

template<typename _Tp>
  inline void
  swap(_Tp& __a, _Tp& __b)
  {
    _Tp __tmp = __a;
    __a = __b;
    __b = __tmp;
  }

// _GLIBCXX_RESOLVE_LIB_DEFECTS
// DR 809. std::swap should be overloaded for array types.
template<typename _Tp, size_t _Nm>
  inline void
  swap(_Tp (&__a)[_Nm], _Tp (&__b)[_Nm])
  {
    for (size_t __n = 0; __n < _Nm; ++__n)
      swap(__a[__n], __b[__n]);
  }

} // namespace kstd

#endif // __cplusplus
