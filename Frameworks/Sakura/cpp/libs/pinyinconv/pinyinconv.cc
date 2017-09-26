// pinyinconv.cc
// 1/7/2015 jichi

#include "pinyinconv/pinyinconv.h"
#include <boost/algorithm/string.hpp>
#include <cstdint> // for uint8_t
#include <fstream>
#include <sstream>
#include <unordered_map>
//#include <iostream>
//#include <QDebug>

/** Helpers */

namespace { // unnamed

// CH_DELIM = '\t'
enum : char { CH_COMMENT = '#' }; // beginning of a comment

/** See: https://github.com/lxneng/xpinyin
 *  aoeiv:
 *  - aeiouü
 *  - āēīōūǖ
 *  - áéíóúǘ
 *  - ǎěǐǒǔǚ
 *  - àèìòùǜ
 */
const wchar_t *TONE_MARKS[] = { // aeiouv
  L"aeiou\u00fc"
  , L"\u0101\u0113\u012b\u014d\u016b\u01d6"
  , L"\u00e1\u00e9\u00ed\u00f3\u00fa\u01d8"
  , L"\u01ce\u011b\u01d0\u01d2\u01d4\u01da"
  , L"\u00e0\u00e8\u00ec\u00f2\u00f9\u01dc"
};

struct PinyinEntry
{
  std::string latin;
  uint8_t tone; // 0,1,2,3,4

  explicit PinyinEntry(const std::string &latin = std::string(), uint8_t tone = 0)
    : latin(latin), tone(tone) {}

  std::wstring tone_text() const
  {
    std::wstring ret(latin.begin(), latin.end());
    size_t pos = latin.find_first_of("aeiouv");
    if (pos != std::string::npos) {
      if (latin[pos] == 'u' && pos < latin.size() - 1 && ::strchr("aeio", latin[pos + 1]))
        pos++;
      ret[pos] = tone_char_of(latin[pos], tone);
    }
    return ret;
  }

private:
  static wchar_t tone_char_of(char c, uint8_t tone)
  {
    switch (c) {
    case 'a': return TONE_MARKS[tone][0];
    case 'e': return TONE_MARKS[tone][1];
    case 'i': return TONE_MARKS[tone][2];
    case 'o': return TONE_MARKS[tone][3];
    case 'u': return TONE_MARKS[tone][4];
    case 'v': return TONE_MARKS[tone][5];
    default: return 0;
    }
  }
};

} // unnamed namespace

/** Private class */

class PinyinConverterPrivate
{
public:
  typedef std::unordered_map<wchar_t, PinyinEntry> map_type;
  map_type map;
};

/** Public class */

// Construction

PinyinConverter::PinyinConverter() : d_(new D) {}
PinyinConverter::~PinyinConverter() { delete d_; }

int PinyinConverter::size() const { return d_->map.size(); }
bool PinyinConverter::isEmpty() const { return d_->map.empty(); }

void PinyinConverter::clear() { d_->map.clear(); }

// Initialization
bool PinyinConverter::addFile(const std::wstring &path)
{
#ifdef _MSC_VER
  std::ifstream fin(path);
#else
  std::string spath(path.begin(), path.end());
  std::ifstream fin(spath.c_str());
#endif // _MSC_VER
  if (!fin.is_open())
    return false;
  //fin.imbue(UTF8_LOCALE);

  for (std::string line; std::getline(fin, line);)
    if (line.size() >= 3 && line[0] != CH_COMMENT) {
      std::string pinyin;
      int order;
      std::istringstream(line)
          >> std::hex >> order >> pinyin;
      if (order <= 0xffff && !pinyin.empty()) {
        int tone = (pinyin[pinyin.size() - 1] - '0') % 5;
        pinyin.pop_back();
        boost::to_lower(pinyin); // always use lower case
        d_->map[order] = PinyinEntry(pinyin, tone);
      }
      //qDebug() << order << QString::fromStdString(py);
    }

  fin.close();
  return true;
}

// Conversion

std::wstring PinyinConverter::lookup(int ch, bool tone) const
{
  auto p = d_->map.find(ch);
  if (p != d_->map.end()) {
    const auto &py = p->second;
    return tone ? py.tone_text()
                : std::wstring(py.latin.begin(), py.latin.end());
  }
  return std::wstring();
}

std::wstring PinyinConverter::convert(const std::wstring &text,
    const std::wstring &delim, bool tone, bool capital) const
{
  if (text.empty() || d_->map.empty())
    return text;

  std::wstring ret;
  for (size_t i = 0; i < text.size(); i++) {
    wchar_t ch = text[i];
    if (!isascii(ch)) {
      auto p = d_->map.find(ch);
      if (p != d_->map.end()) {
        const auto &py = p->second;
        if (tone) {
          std::wstring t = py.tone_text();
          if (!t.empty()) {
            if (capital)
              t[0] = ::towupper(t[0]);
            ret.append(t);
          }
        } else if (capital) {
          ret.push_back(::toupper(py.latin.front()));
          if (py.latin.size() > 1)
            ret.append(py.latin.begin() + 1, py.latin.end());
        } else // not tone and not capital
          ret.append(py.latin.begin(), py.latin.end());
        if (!delim.empty())
          ret.append(delim);
        continue;
      }
    }
    ret.push_back(ch);
  }
  return ret;
}

// EOF
