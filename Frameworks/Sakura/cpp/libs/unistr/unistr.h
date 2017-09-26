#ifndef UNISTR_H
#define UNISTR_H

// unistr.h
// 2/2/2015 jichi

#include "unistr/unichar.h"
#include <algorithm> // for transform
#include <iterator> // for back_inserter

namespace unistr {

template <typename SequenceT, typename FunT>
inline void to_transform(SequenceT &s, const FunT &f)
{ std::transform(s.cbegin(), s.cend(), s.begin(), f); }

template <typename SequenceT, typename FunT>
inline SequenceT to_transform_copy(const SequenceT &s, const FunT &f)
{
  SequenceT t;
  std::transform(s.begin(), s.end(), std::back_inserter(t), f);
  return t;
}

template <typename SequenceT>
inline void to_thin(SequenceT &s)
{ to_transform(s, wide2thin); }

template <typename SequenceT>
inline SequenceT to_thin_copy(SequenceT &s)
{ return to_transform_copy(s, wide2thin); }

template <typename SequenceT>
inline void to_wide(SequenceT &s)
{ to_transform(s, thin2wide); }

template <typename SequenceT>
inline SequenceT to_wide_copy(SequenceT &s)
{ return to_transform_copy(s, thin2wide); }

} // namespace unistr

#endif // UNISTR_H
