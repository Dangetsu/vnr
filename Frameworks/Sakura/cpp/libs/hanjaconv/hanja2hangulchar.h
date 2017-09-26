#ifndef HANGUL2HANJACHAR_H
#define HANGUL2HANJACHAR_H

// hanja2hangulchar.h
// 7/11/2015 jichi

#include "sakurakit/skglobal.h"
#include <functional>

class HanjaHangulCharacterConverterPrivate;
class HanjaHangulCharacterConverter
{
  SK_CLASS(HanjaHangulCharacterConverter)
  SK_DISABLE_COPY(HanjaHangulCharacterConverter)
  SK_DECLARE_PRIVATE(HanjaHangulCharacterConverterPrivate)

  // - Construction -
public:
  HanjaHangulCharacterConverter();
  ~HanjaHangulCharacterConverter();

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

  // Replace the characters according to the script, thread-safe
  void replace(wchar_t *text) const;

  wchar_t lookup(wchar_t ch) const;
};

#endif // HANGUL2HANJACHAR_H
