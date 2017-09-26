// worddic.cc
// 2/2/2015 jichi

#include "hanviet/worddic.h"
#include "cpputil/cpplocale.h"
#include "unistr/unichar.h"
#include <fstream>
#include <unordered_map>
//#include <iostream>
//#include <QDebug>

/** Helpers */

namespace { // unnamed

enum : char {
  CH_COMMENT = L'#'  // beginning of a comment
  , CH_DELIM = L'='  // deliminator
};

const std::locale UTF8_LOCALE = ::cpp_utf8_locale<wchar_t>();

} // unnamed namespace

/** Private class */

class HanVietWordDictionaryPrivate
{
public:
  typedef std::unordered_map<wchar_t, std::wstring> map_type;
  map_type map;
};

/** Public class */

// Construction

HanVietWordDictionary::HanVietWordDictionary() : d_(new D) {}
HanVietWordDictionary::~HanVietWordDictionary() { delete d_; }

int HanVietWordDictionary::size() const { return d_->map.size(); }
bool HanVietWordDictionary::isEmpty() const { return d_->map.empty(); }

void HanVietWordDictionary::clear() { d_->map.clear(); }

// Initialization
bool HanVietWordDictionary::addFile(const std::wstring &path)
{
#ifdef _MSC_VER
  std::wifstream fin(path);
#else
  std::string spath(path.begin(), path.end());
  std::wifstream fin(spath.c_str());
#endif // _MSC_VER
  if (!fin.is_open())
    return false;
  fin.imbue(UTF8_LOCALE);

  for (std::wstring line; std::getline(fin, line);)
    if (line.size() >= 3 && line[0] != CH_COMMENT && line[1] == CH_DELIM)
      d_->map[line[0]] = line.substr(2);

  fin.close();
  return true;
}

// Conversion

std::wstring HanVietWordDictionary::lookup(int ch) const
{
  auto p = d_->map.find(ch);
  if (p != d_->map.end())
    return p->second;
  return std::wstring();
}

std::wstring HanVietWordDictionary::translate(const std::wstring &text) const
{
  if (text.empty() || d_->map.empty())
    return text;
  if (text.size() == 1)
    return lookup(text[0]);

  enum : wchar_t { delim = L' ' };

  std::wstring ret;
  for (size_t i = 0; i < text.size(); i++) {
    wchar_t ch = text[i];
    if (unistr::iskanji(ch)) {
      auto p = d_->map.find(ch);
      if (p != d_->map.end()) {
        ret.append(p->second);
        if (i != text.size() - 1) // do not push delim for the last character
          ret.push_back(delim);
        continue;
      }
    }
    ret.push_back(ch);
  }
  return ret;
}

// EOF
