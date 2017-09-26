#pragma once
#ifdef __cplusplus

// kstl/list.h
// 12/11/2011 jichi
// Modified from bits/stl_list.h from g++/4.6.2.

#include "kstl/allocator.h"
#include "kstl/iterator.h"
#include "kstl/move.h"

namespace kstd {

// + nodes +

struct _List_node_base
{
  typedef _List_node_base _Self;
  _Self *_M_next;
  _Self *_M_prev;

  // Not zero-ed after init.

  static void
  swap(_List_node_base& __x, _List_node_base& __y) throw ();

  void
  _M_transfer(_List_node_base* const __first,
              _List_node_base* const __last) throw ();

  void
  _M_reverse() throw ();

  void
  _M_hook(_List_node_base* const __position) throw ();

  void
  _M_unhook() throw ();
};

/// An actual node in the %list.
template<typename _Tp>
  struct _List_node : public _List_node_base
  { _Tp _M_data; };

// + iterators +

/**
 *  @brief A list::iterator.
 *
 *  All the functions are op overloads.
*/
template<typename _Tp>
  struct _List_iterator
  {
    typedef _List_iterator<_Tp>                _Self;
    typedef _List_node<_Tp>                    _Node;

    typedef ptrdiff_t                          difference_type;
    typedef bidirectional_iterator_tag         iterator_category;
    typedef _Tp                                value_type;
    typedef _Tp*                               pointer;
    typedef _Tp&                               reference;

    _List_iterator()
    : _M_node() {}

    explicit
    _List_iterator(_List_node_base* __x)
    : _M_node(__x) {}

    // Must downcast from _List_node_base to _List_node to get to _M_data.
    reference
    operator*() const
    { return static_cast<_Node*>(_M_node)->_M_data; }

    pointer
    operator->() const
    { return __addressof(static_cast<_Node*>(_M_node)->_M_data); }

    _Self&
    operator++()
    { _M_node = _M_node->_M_next; return *this; }

    _Self
    operator++(int)
    { _Self t = *this; _M_node = _M_node->_M_next; return t; }

    _Self&
    operator--()
    { _M_node = _M_node->_M_prev; return *this; }

    _Self
    operator--(int)
    { _Self t = *this; _M_node = _M_node->_M_prev; return t; }

    bool
    operator==(const _Self& __x) const
    { return _M_node == __x._M_node; }

    bool
    operator!=(const _Self& __x) const
    { return _M_node != __x._M_node; }

    // The only member points to the %list element.
    _List_node_base *_M_node;
  };

template<typename _Tp>
  struct _List_const_iterator
  {
    typedef _List_const_iterator<_Tp>          _Self;
    typedef const _List_node<_Tp>              _Node;
    typedef _List_iterator<_Tp>                iterator;

    typedef ptrdiff_t                          difference_type;
    typedef bidirectional_iterator_tag         iterator_category;
    typedef _Tp                                value_type;
    typedef const _Tp*                         pointer;
    typedef const _Tp&                         reference;

    _List_const_iterator()
    : _M_node() {}

    explicit
    _List_const_iterator(const _List_node_base* __x)
    : _M_node(__x) {}

    _List_const_iterator(const iterator& __x)
    : _M_node(__x._M_node) {}

    // Must downcast from List_node_base to _List_node to get to
    // _M_data.
    reference
    operator*() const
    { return static_cast<_Node*>(_M_node)->_M_data; }

    pointer
    operator->() const
    { return __addressof(static_cast<_Node*>(_M_node)->_M_data); }

    _Self&
    operator++()
    { _M_node = _M_node->_M_next; return *this; }

    _Self
    operator++(int)
    { _Self __tmp = *this; _M_node = _M_node->_M_next; return __tmp;
    }

    _Self&
    operator--()
    { _M_node = _M_node->_M_prev; return *this; }

    _Self
    operator--(int)
    { _Self __tmp = *this; _M_node = _M_node->_M_prev; return __tmp;
    }

    bool
    operator==(const _Self& __x) const
    { return _M_node == __x._M_node; }

    bool
    operator!=(const _Self& __x) const
    { return _M_node != __x._M_node; }

    // The only member points to the %list element.
    const _List_node_base *_M_node;
 };

template<typename _Val>
  inline bool
  operator==(const _List_iterator<_Val>& __x,
             const _List_const_iterator<_Val>& __y)
  { return __x._M_node == __y._M_node; }

template<typename _Val>
  inline bool
  operator!=(const _List_iterator<_Val>& __x,
             const _List_const_iterator<_Val>& __y)
  { return __x._M_node != __y._M_node; }


// + list =

template<typename _Tp, typename _Alloc>
  class _List_base
  {
  protected:
    typedef typename _Alloc::template rebind<_List_node<_Tp> >::other
      _Node_alloc_type;

    typedef typename _Alloc::template rebind<_Tp>::other _Tp_alloc_type;

    struct _List_impl
    : public _Node_alloc_type
    {
      _List_node_base _M_node;

      _List_impl()
      : _Node_alloc_type(), _M_node()
      {}

      _List_impl(const _Node_alloc_type& __a)
      : _Node_alloc_type(__a), _M_node()
      {}
    };

    _List_impl _M_impl;

    _List_node<_Tp>*
    _M_get_node()
    { return _M_impl._Node_alloc_type::allocate(1); }

    void
    _M_put_node(_List_node<_Tp>* p)
    { _M_impl._Node_alloc_type::deallocate(p, 1); }

  public:
    typedef _Alloc allocator_type;

    _Node_alloc_type&
    _M_get_Node_allocator()
    { return *static_cast<_Node_alloc_type*>(&this->_M_impl); }

    const _Node_alloc_type&
    _M_get_Node_allocator() const
    { return *static_cast<const _Node_alloc_type*>(&this->_M_impl); }

    _Tp_alloc_type
    _M_get_Tp_allocator() const
    { return _Tp_alloc_type(_M_get_Node_allocator()); }

    allocator_type
    get_allocator() const
    { return allocator_type(_M_get_Node_allocator()); }

    _List_base() : _M_impl() { _M_init(); }
    ~_List_base() { _M_clear(); }

    void _M_clear();

    void
    _M_init()
    {
      this->_M_impl._M_node._M_next = &this->_M_impl._M_node;
      this->_M_impl._M_node._M_prev = &this->_M_impl._M_node;
    }
  };

///  Partially implemented.
template<typename _Tp, typename _Alloc = allocator<_Tp> >
  class list : protected _List_base<_Tp, _Alloc>
  {
    typedef list<_Tp, _Alloc> _Self;
    typedef _List_base<_Tp, _Alloc> _Base;

    typedef typename _Base::_Tp_alloc_type		 _Tp_alloc_type;

  protected:
    typedef _List_node<_Tp>				 _Node;

    using _Base::_M_impl;
    using _Base::_M_put_node;
    using _Base::_M_get_node;
    using _Base::_M_get_Tp_allocator;
    using _Base::_M_get_Node_allocator;


    // - Types -
  public:
    typedef _Tp         value_type;
    typedef typename _Tp_alloc_type::pointer          pointer;
    typedef typename _Tp_alloc_type::const_pointer    const_pointer;
    typedef typename _Tp_alloc_type::reference        reference;
    typedef typename _Tp_alloc_type::const_reference  const_reference;
    typedef _List_iterator<_Tp>                       iterator;
    typedef _List_const_iterator<_Tp>                 const_iterator;
    //typedef std::reverse_iterator<const_iterator>     const_reverse_iterator;
    //typedef std::reverse_iterator<iterator>           reverse_iterator;
    typedef size_t      size_type;
    typedef ptrdiff_t   difference_type;
    typedef _Alloc      allocator_type;

    // - Constructions -
  public:
    list() {}

    void
    clear()
    {
      _Base::_M_clear();
      _Base::_M_init();
    }

    // - Properties -
  public:
    bool
    empty() const
    { return this->_M_impl._M_node._M_next == &this->_M_impl._M_node; }

    size_type
    size() const
    { return kstd::distance(begin(), end()); }

    size_type
    max_size() const
    { return _M_get_Node_allocator().max_size(); }

    iterator
    begin()
    { return iterator(this->_M_impl._M_node._M_next); }

    const_iterator
    begin() const
    { return const_iterator(this->_M_impl._M_node._M_next); }

    iterator
    end()
    { return iterator(&this->_M_impl._M_node); }

    const_iterator
    end() const
    { return const_iterator(&this->_M_impl._M_node); }

    reference
    front() { return *begin(); }

    const_reference
    front() const { return *begin(); }

    reference
    back() { iterator t = end(); return *--t; }

    const_reference
    back() const { const_iterator t = end(); return *--t; }


    // - Update -
 public:
    void
    push_front(const value_type& __x)
    { this->_M_insert(begin(), __x); }

    void
    pop_front()
    { this->_M_erase(begin()); }

    void
    push_back(const value_type& __x)
    { this->_M_insert(end(), __x); }

    void
    pop_back()
    { this->_M_erase(iterator(this->_M_impl._M_node._M_prev)); }

    // - Implementation -
  protected:
    void
    _M_insert(iterator __pos, const value_type &x)
    {
      if (_Node *t = _M_create_node(x))
        t->_M_hook(__pos._M_node);
    }

    void
    _M_erase(iterator __pos)
    {
      __pos._M_node->_M_unhook();
      _Node *__n = static_cast<_Node*>(__pos._M_node);
      _M_get_Tp_allocator().destroy(kstd::__addressof(__n->_M_data));
      _M_put_node(__n);
    }

    _Node*
    _M_create_node(const value_type &__x)
    {
      _Node *__p = this->_M_get_node();
      if (__p)
        _M_get_Tp_allocator().construct
          (kstd::__addressof(__p->_M_data), __x);
      return __p;
    }
  };

// namespace kstd

 - IMPLEMENTATION -
mespace kstd {

// - List - from g++ 4.6.6 src/list.cc
inline void
_List_node_base::swap(_List_node_base& __x, _List_node_base& __y)
{
  if (__x._M_next != &__x) {
    if (__y._M_next != &__y) {
      // Both __x and __y are not empty.
      kstd::swap(__x._M_next,__y._M_next);
      kstd::swap(__x._M_prev,__y._M_prev);
      __x._M_next->_M_prev = __x._M_prev->_M_next = &__x;
      __y._M_next->_M_prev = __y._M_prev->_M_next = &__y;
    } else {
      // __x is not empty, __y is empty.
      __y._M_next = __x._M_next;
      __y._M_prev = __x._M_prev;
      __y._M_next->_M_prev = __y._M_prev->_M_next = &__y;
      __x._M_next = __x._M_prev = &__x;
    }
  } else if (__y._M_next != &__y) {
    // __x is empty, __y is not empty.
    __x._M_next = __y._M_next;
    __x._M_prev = __y._M_prev;
    __x._M_next->_M_prev = __x._M_prev->_M_next = &__x;
    __y._M_next = __y._M_prev = &__y;
  }
}

inline void
_List_node_base::_M_transfer(_List_node_base * const __first,
                          _List_node_base * const __last)
{
  if (this != __last) {
    // Remove [first, last) from its old position.
    __last->_M_prev->_M_next  = this;
    __first->_M_prev->_M_next = __last;
    this->_M_prev->_M_next    = __first;

    // Splice [first, last) into its new position.
    _List_node_base* const __tmp = this->_M_prev;
    this->_M_prev                = __last->_M_prev;
    __last->_M_prev              = __first->_M_prev;
    __first->_M_prev             = __tmp;
  }
}

inline void
_List_node_base::_M_reverse()
{
  _List_node_base* __tmp = this;
  do {
    kstd::swap(__tmp->_M_next, __tmp->_M_prev);

    // Old next node is now prev.
    __tmp = __tmp->_M_prev;
  } while (__tmp != this);
}

inline void
_List_node_base::_M_hook(_List_node_base* const __position)
{
  this->_M_next = __position;
  this->_M_prev = __position->_M_prev;
  __position->_M_prev->_M_next = this;
  __position->_M_prev = this;
}

inline void
_List_node_base::_M_unhook()
{
  _List_node_base* const __next_node = this->_M_next;
  _List_node_base* const __prev_node = this->_M_prev;
  __prev_node->_M_next = __next_node;
  __next_node->_M_prev = __prev_node;
}

// - List - from g++ 4.6.2 bits/list.tcc
template <typename _Tp, typename _Alloc>
  inline void
  _List_base<_Tp, _Alloc>::
  _M_clear()
  {
    typedef _List_node<_Tp>  _Node;
    _Node* __cur = static_cast<_Node*>(this->_M_impl._M_node._M_next);
    while (__cur != &this->_M_impl._M_node)
    {
      _Node* __tmp = __cur;
      __cur = static_cast<_Node*>(__cur->_M_next);
      _M_get_Tp_allocator().destroy(kstd::__addressof(__tmp->_M_data));
      _M_put_node(__tmp);
    }
  }
}

#endif // __cplusplus
