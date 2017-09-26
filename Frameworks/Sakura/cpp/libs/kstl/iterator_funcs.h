#pragma once
#ifdef __cplusplus

// kstl/iterator_funcs.h
// 12/10/2011 jichi
// Modified from bits/stl_iterator_base_funcs.h from g++/4.6.2.
#include "kstl/iterator_types.h"

namespace kstd {

template<typename _InputIterator>
  inline typename iterator_traits<_InputIterator>::difference_type
  __distance(_InputIterator __first, _InputIterator __last,
             input_iterator_tag)
  {
    typename iterator_traits<_InputIterator>::difference_type __n = 0;
    while (__first != __last) {
      ++__first;
      ++__n;
    }
    return __n;
  }

template<typename _RandomAccessIterator>
  inline typename iterator_traits<_RandomAccessIterator>::difference_type
  __distance(_RandomAccessIterator __first, _RandomAccessIterator __last,
             random_access_iterator_tag)
  { return __last - __first; }

/**
 *  @brief A generalization of pointer arithmetic.
 *  @param  first  An input iterator.
 *  @param  last  An input iterator.
 *  @return  The distance between them.
 *
 *  Returns @c n such that first + n == last.  This requires that @p last
 *  must be reachable from @p first.  Note that @c n may be negative.
 *
 *  For random access iterators, this uses their @c + and @c - operations
 *  and are constant time.  For other %iterator classes they are linear time.
*/
template<typename _InputIterator>
  inline typename iterator_traits<_InputIterator>::difference_type
  distance(_InputIterator __first, _InputIterator __last)
  {
    // concept requirements -- taken care of in __distance
    return kstd::__distance(__first, __last,
                            kstd::__iterator_category(__first));
  }

template<typename _InputIterator, typename _Distance>
  inline void
  __advance(_InputIterator& __i, _Distance __n, input_iterator_tag)
  {
    while (__n--)
      ++__i;
  }

template<typename _BidirectionalIterator, typename _Distance>
  inline void
  __advance(_BidirectionalIterator& __i, _Distance __n,
            bidirectional_iterator_tag)
  {
    if (__n > 0)
      while (__n--)
        ++__i;
    else
      while (__n++)
        --__i;
  }

template<typename _RandomAccessIterator, typename _Distance>
  inline void
  __advance(_RandomAccessIterator& __i, _Distance __n,
            random_access_iterator_tag)
  { __i += __n; }

/**
 *  @brief A generalization of pointer arithmetic.
 *  @param  i  An input iterator.
 *  @param  n  The @a delta by which to change @p i.
 *  @return  Nothing.
 *
 *  This increments @p i by @p n.  For bidirectional and random access
 *  iterators, @p n may be negative, in which case @p i is decremented.
 *
 *  For random access iterators, this uses their @c + and @c - operations
 *  and are constant time.  For other %iterator classes they are linear time.
*/
template<typename _InputIterator, typename _Distance>
  inline void
  advance(_InputIterator& __i, _Distance __n)
  {
    // concept requirements -- taken care of in __advance
    typename iterator_traits<_InputIterator>::difference_type __d = __n;
    kstd::__advance(__i, __d, kstd::__iterator_category(__i));
  }

} // namespace kstl

#endif // __cplusplus
