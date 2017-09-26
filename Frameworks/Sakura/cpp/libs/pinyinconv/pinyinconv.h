#ifndef PINYINCONV_H
#define PINYINCONV_H

// pinyinconv.h
// 1/7/2015 jichi

#include "sakurakit/skglobal.h"
#include <string>

class PinyinConverterPrivate;
class PinyinConverter
{
  SK_CLASS(PinyinConverter)
  SK_DISABLE_COPY(PinyinConverter)
  SK_DECLARE_PRIVATE(PinyinConverterPrivate)

  // - Construction -
public:
  PinyinConverter();
  ~PinyinConverter();

  // Initialization

  ///  Return the number of loaded rules
  int size() const;

  ///  Return whether the script has been loaded, thread-safe
  bool isEmpty() const;

  ///  Clear the loaded script
  void clear();

  ///  Add script from file, reverse to determine the direction
  bool addFile(const std::wstring &path);

  // Replacement

  std::wstring lookup(int ch, bool tone = true) const;

  // Replace the characters according to the script, thread-safe
  std::wstring convert(const std::wstring &text,
                       const std::wstring &delim = L" ",
                       bool tone = true,
                       bool capital = true) const;
};

#endif // PINYINCONV_H
