#ifndef SIMPLECC_H
#define SIMPLECC_H

// simplecc.h
// 10/18/2014 jichi

#include "sakurakit/skglobal.h"
#include <string>

class SimpleChineseConverterPrivate;
class SimpleChineseConverter
{
  SK_CLASS(SimpleChineseConverter)
  SK_DISABLE_COPY(SimpleChineseConverter)
  SK_DECLARE_PRIVATE(SimpleChineseConverterPrivate)

  // - Construction -
public:
  SimpleChineseConverter();
  ~SimpleChineseConverter();

  // Initialization

  ///  Return the number of loaded rules
  int size() const;

  ///  Return whether the script has been loaded, thread-safe
  bool isEmpty() const;

  ///  Clear the loaded script
  void clear();

  ///  Add script from file, reverse to determine the direction
  bool addFile(const std::wstring &path, bool reverse = false);

  // Replacement

  // Replace the characters according to the script, thread-safe
  std::wstring convert(const std::wstring &text) const;

  // Return if it includes characters to convert
  bool needsConvert(const std::wstring &text) const;
};

#endif // SIMPLECC_H
