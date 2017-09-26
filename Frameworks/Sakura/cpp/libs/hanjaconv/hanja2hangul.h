#ifndef HANJA2HANGUL_H
#define HANJA2HANGUL_H

// hanja2hangul.h
// 1/6/2015 jichi

#include "sakurakit/skglobal.h"
#include <functional>
#include <string>

class HanjaHangulConverterPrivate;
class HanjaHangulConverter
{
  SK_CLASS(HanjaHangulConverter)
  SK_DISABLE_COPY(HanjaHangulConverter)
  SK_DECLARE_PRIVATE(HanjaHangulConverterPrivate)

  // - Construction -
public:
  HanjaHangulConverter();
  ~HanjaHangulConverter();

  // Initialization

  ///  Return whether the script has been loaded, thread-safe
  bool isEmpty() const;

  ///  Clear the loaded script
  void clear();

  ///  Add script from file, reverse to determine the direction
  bool addWordDictionary(const wchar_t *path);
  bool addCharacterDictionary(const wchar_t *path);

  // Replacement

  // Replace the characters according to the script, thread-safe
  void replace(wchar_t *text) const;
  // The same as replace_copy
  std::wstring convert(const wchar_t *text) const;

  wchar_t lookupCharacter(wchar_t ch) const;
  std::wstring lookup(const wchar_t *text) const;
};

#endif // HANJA2HANGUL_H
