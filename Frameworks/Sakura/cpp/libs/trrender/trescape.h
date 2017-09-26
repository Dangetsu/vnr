#ifndef TRESCAPE_H
#define TRESCAPE_H

// trescape.h
// 9/20/2014 jichi

#include "cppjson/jsonescape.h"
#include <boost/algorithm/string.hpp>

inline std::string trescape(const std::wstring &t)
{
  std::string r = cpp_json::escape_basic_string(t, true); // true = escape all chars
  if (r.find('\'') != std::string::npos)
    boost::replace_all(r, "'", "\\'");
  return r;
}

#endif // TRESCAPE_H
