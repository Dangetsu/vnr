#ifndef HANGUL2HANJAWORD_H
#define HANGUL2HANJAWORD_H

// hanja2hangulword.h
// 7/11/2015 jichi

#include "sakurakit/skglobal.h"
#include <functional>
#include <string>

class HanjaHangulWordConverterPrivate;
class HanjaHangulWordConverter
{
  SK_CLASS(HanjaHangulWordConverter)
  SK_DISABLE_COPY(HanjaHangulWordConverter)
  SK_DECLARE_PRIVATE(HanjaHangulWordConverterPrivate)

  // - Construction -
public:
  HanjaHangulWordConverter();
  ~HanjaHangulWordConverter();

  // Initialization

  ///  Return total number of rules
  int size() const;

  ///  Return whether the script has been loaded, thread-safe
  bool isEmpty() const;

  ///  Clear the loaded script
  void clear();

  ///  Add script from file, reverse to determine the direction
  bool addDictionary(const wchar_t *path);

  // Replacement

  // Replace the Words according to the script, thread-safe
  void replace(wchar_t *text) const;

  std::wstring lookup(const wchar_t *text) const;
};

#endif // HANGUL2HANJAWORD_H
