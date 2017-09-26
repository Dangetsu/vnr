// hanja2hangul.cc
// 1/6/2015 jichi

#include "hanjaconv/hanja2hangul.h"
#include "hanjaconv/hanja2hangulchar.h"
#include "hanjaconv/hanja2hangulword.h"

/** Private class */

class HanjaHangulConverterPrivate
{
public:
  HanjaHangulCharacterConverter charConverter;
  HanjaHangulWordConverter wordConverter;
};

/** Public class */

// Construction

HanjaHangulConverter::HanjaHangulConverter() : d_(new D) {}
HanjaHangulConverter::~HanjaHangulConverter() { delete d_; }

bool HanjaHangulConverter::isEmpty() const
{ return d_->charConverter.isEmpty() && d_->wordConverter.isEmpty(); }

void HanjaHangulConverter::clear()
{
  d_->charConverter.clear();
  d_->wordConverter.clear();
}

// Initialization
bool HanjaHangulConverter::addWordDictionary(const wchar_t *path)
{ return d_->wordConverter.addDictionary(path); }

bool HanjaHangulConverter::addCharacterDictionary(const wchar_t *path)
{ return d_->charConverter.addDictionary(path); }

// Conversion

void HanjaHangulConverter::replace(wchar_t *text) const
{
  d_->wordConverter.replace(text);
  d_->charConverter.replace(text);
}

std::wstring HanjaHangulConverter::convert(const wchar_t *text) const
{
  std::wstring ret = text;
  replace(&ret[0]);
  return ret;
}

wchar_t HanjaHangulConverter::lookupCharacter(wchar_t ch) const
{ return d_->charConverter.lookup(ch); }

std::wstring HanjaHangulConverter::lookup(const wchar_t *text) const
{
  std::wstring ret = d_->wordConverter.lookup(text);
  if (ret.empty() && ::wcslen(text) == 1)
     if (wchar_t ch = d_->charConverter.lookup(*text))
       ret.push_back(ch);
  return ret;
}

// EOF
