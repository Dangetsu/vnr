#pragma once
#ifdef __cplusplus

// kstl/iterator_types.h
// 12/10/2011 jichi
// Modified from bits/stl_iterator_base_types.h from g++/4.6.2.

namespace kstd {

struct input_iterator_tag {};

///  Marking output iterators.
struct output_iterator_tag {};

/// Forward iterators support a superset of input iterator operations.
struct forward_iterator_tag : public input_iterator_tag {};

/// Bidirectional iterators support a superset of forward iterator
/// operations.
struct bidirectional_iterator_tag : public forward_iterator_tag {};

/// Random-access iterators support a superset of bidirectional
/// iterator operations.
struct random_access_iterator_tag : public bidirectional_iterator_tag {};
//@}

/**
 *  @brief  Common %iterator class.
 *
 *  This class does nothing but define nested typedefs.  %Iterator classes
 *  can inherit from this class to save some work.  The typedefs are then
 *  used in specializations and overloading.
 *
 *  In particular, there are no default implementations of requirements
 *  such as @c operator++ and the like.  (How could there be?)
*/
template<typename _Category, typename _Tp, typename _Distance = ptrdiff_t,
         typename _Pointer = _Tp*, typename _Reference = _Tp&>
  struct iterator
  {
    /// One of the @link iterator_tags tag types@endlink.
    typedef _Category  iterator_category;
    /// The type "pointed to" by the iterator.
    typedef _Tp        value_type;
    /// Distance between iterators is represented as this type.
    typedef _Distance  difference_type;
    /// This type represents a pointer-to-value_type.
    typedef _Pointer   pointer;
    /// This type represents a reference-to-value_type.
    typedef _Reference reference;
  };

/**
 *  @brief  Traits class for iterators.
 *
 *  This class does nothing but define nested typedefs.  The general
 *  version simply @a forwards the nested typedefs from the Iterator
 *  argument.  Specialized versions for pointers and pointers-to-const
 *  provide tighter, more correct semantics.
*/
template<typename _Iterator>
  struct iterator_traits
  {
    typedef typename _Iterator::iterator_category iterator_category;
    typedef typename _Iterator::value_type        value_type;
    typedef typename _Iterator::difference_type   difference_type;
    typedef typename _Iterator::pointer           pointer;
    typedef typename _Iterator::reference         reference;
  };

/// Partial specialization for pointer types.
template<typename _Tp>
  struct iterator_traits<_Tp*>
  {
    typedef random_access_iterator_tag iterator_category;
    typedef _Tp                         value_type;
    typedef ptrdiff_t                   difference_type;
    typedef _Tp*                        pointer;
    typedef _Tp&                        reference;
  };

/// Partial specialization for const pointer types.
template<typename _Tp>
  struct iterator_traits<const _Tp*>
  {
    typedef random_access_iterator_tag iterator_category;
    typedef _Tp                         value_type;
    typedef ptrdiff_t                   difference_type;
    typedef const _Tp*                  pointer;
    typedef const _Tp&                  reference;
  };

/**
 *  This function is not a part of the C++ standard but is syntactic
 *  sugar for internal library use only.
*/
template<typename _Iter>
  inline typename iterator_traits<_Iter>::iterator_category
  __iterator_category(const _Iter&)
  { return typename iterator_traits<_Iter>::iterator_category(); }

//@}

// If _Iterator has a base returns it otherwise _Iterator is returned
// untouched
template<typename _Iterator, bool _HasBase>
  struct _Iter_base
  {
    typedef _Iterator iterator_type;
    static iterator_type _S_base(_Iterator __it)
    { return __it; }
  };

template<typename _Iterator>
  struct _Iter_base<_Iterator, true>
  {
    typedef typename _Iterator::iterator_type iterator_type;
    static iterator_type _S_base(_Iterator __it)
    { return __it.base(); }
  };

} // namespace

#endif // __cplusplus
