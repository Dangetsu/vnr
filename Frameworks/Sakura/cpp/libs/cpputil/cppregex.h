#ifndef CPPREGEX_H
#define CPPREGEX_H

// cppregex.h
// 4/3/2016 jichi
// The original file was lost ...

#include <boost/regex.hpp>

// This function might raise
template <typename strT, typename regexT>
inline bool cpp_regex_contains(const strT &str, const regexT &pattern)
{ return boost::regex_search(str, pattern); }

// This function might raise
// http://stackoverflow.com/questions/8283735/count-number-of-matches
template <typename strT, typename regexT>
inline std::ptrdiff_t cpp_regex_count(const strT &str, const regexT &pattern)
{
  return std::distance(
      boost::sregex_iterator(str.begin(), str.end(), pattern),
      boost::sregex_iterator());
}

#endif // CPPUNICODE_H
