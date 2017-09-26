#ifndef JSONESCAPE_H
#define JSONESCAPE_H

// jsonescape.h
// 10/12/2014 jichi

#include "cppjson/cppjson.h"
#include <iomanip>
#include <sstream>
#include <ctype.h> // for isascii

CPPJSON_BEGIN_NAMESPACE

#define CPPJSON_ESCAPE_STRING   "\\\"/\b\f\n\r\t"

//template <typename _CharT, typename _Traits, typename _Alloc>
//inline bool requires_escape(const std::basic_string<_CharT, _Traits, _Alloc> &input)
//{ return input.find_first_of(CPPJSON_ESCAPE_STRING) != std::string::npos; }

///  Return escaped special string if succeed
inline const char *escape_special_char(int ch)
{
  switch (ch) {
  case '\\': return "\\\\";
  case '"': return "\\\"";
  case '\n': return "\\n";
  case '\r': return "\\r";
  case '\t': return "\\t";
  case '\b': return "\\b";
  case '\f': return "\\f";
  default: return nullptr;
  }
}

//QString escape_unicode(int ch)
//{
//  QString r = QString::number(ch, 16);
//  while (r.size() < 4)
//    r.prepend('0');
//  return "\\u" + r;
//}

/**
 *  @param  input  text to escape
 *  @param* escape_all  whether encode ascii char as well
 */
template <typename _CharT, typename _Traits, typename _Alloc>
inline std::string escape_basic_string(const std::basic_string<_CharT, _Traits, _Alloc> &input, bool escape_all = false)
//inline std::basic_string<_CharT, _Traits, _Alloc> escape_basic_string(const std::basic_string<_CharT, _Traits, _Alloc> &input, bool escape_all = false)
{
  // See: http://stackoverflow.com/questions/7724448/simple-json-string-escape-for-c
  //std::basic_ostringstream<_CharT, _Traits, _Alloc> is;
  std::ostringstream is;
  for (auto it = input.cbegin(); it != input.cend(); ++it) {
    auto ch = *it;
    if (escape_all) {
      if (const char *s = escape_special_char(ch))
        is << s;
      else
        is << "\\u"
           << std::setfill('0') << std::setw(4) // force 4 width for unicode, which might be wrong for 3 bit unicode
           << std::hex << (unsigned int)ch;

    } else {
      if (isascii(ch)) {
        if (const char *s = escape_special_char(ch))
          is << s;
        else
          is << ch;

      } else
        is << "\\u"
           << std::setfill('0') << std::setw(4) // force 4 width for unicode, which might be wrong for 3 bit unicode
           << std::hex << (unsigned int)ch;
    }
  }
  return is.str();
}

CPPJSON_END_NAMESPACE

#endif // JSONESCAPE_H
