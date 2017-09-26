// hanja2hangulchar.cc
// 7/11/2015 jichi

#include "hanjaconv/hanja2hangulchar.h"
#include "hanjaconv/hanjadef_p.h"
#include <fstream>

#ifdef __clang__
# define USE_BOOST_CXX11
#endif // __clang__

#ifdef USE_BOOST_CXX11
# include <boost/unordered_map.hpp>
  using boost::unordered_map;
#else
# include <unordered_map>
  using std::unordered_map;
#endif // USE_BOOST_CXX11

/** Private class */

class HanjaHangulCharacterConverterPrivate
{
public:
  typedef unordered_map<wchar_t, wchar_t> data_type;
  data_type data;
};

/** Public class */

// Construction

HanjaHangulCharacterConverter::HanjaHangulCharacterConverter() : d_(new D) {}
HanjaHangulCharacterConverter::~HanjaHangulCharacterConverter() { delete d_; }

int HanjaHangulCharacterConverter::size() const { return d_->data.size(); }
bool HanjaHangulCharacterConverter::isEmpty() const { return d_->data.empty(); }

void HanjaHangulCharacterConverter::clear() { d_->data.clear(); }

// Initialization
bool HanjaHangulCharacterConverter::addDictionary(const wchar_t *path)
{
#ifdef _MSC_VER
  std::wifstream fin(path);
#else
  std::string spath(path, path + ::wcslen(path));
  std::wifstream fin(spath.c_str());
#endif // _MSC_VER
  if (!fin.is_open())
    return false;
  fin.imbue(HANJA_UTF8_LOCALE);

  for (std::wstring line; std::getline(fin, line);)
    if (line.size() >= 3 && line[0] != CH_COMMENT && line[1] == CH_DELIM)
      d_->data[line[0]] = line[2];

  fin.close();
  return true;
}

// Conversion

void HanjaHangulCharacterConverter::replace(wchar_t *text) const
{
  if (!text || d_->data.empty())
    return;

  for (; *text; text++) {
    auto p = d_->data.find(*text);
    if (p != d_->data.end())
      *text = p->second;
  }
}

wchar_t HanjaHangulCharacterConverter::lookup(wchar_t ch) const
{
  if (!ch || d_->data.empty())
    return 0;
  auto p = d_->data.find(ch);
  if (p != d_->data.end())
    return p->second;
  return 0;
}

// EOF
