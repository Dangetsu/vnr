#ifndef WORDDIC_H
#define WORDDIC_H

// worddic.h
// 1/7/2015 jichi

#include "sakurakit/skglobal.h"
#include <string>

class HanVietWordDictionaryPrivate;
class HanVietWordDictionary
{
  SK_CLASS(HanVietWordDictionary)
  SK_DISABLE_COPY(HanVietWordDictionary)
  SK_DECLARE_PRIVATE(HanVietWordDictionaryPrivate)

  // - Construction -
public:
  HanVietWordDictionary();
  ~HanVietWordDictionary();

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

  // Return the text for the character
  std::wstring lookup(int ch) const;

  // Replace the characters according to the script
  std::wstring translate(const std::wstring &text) const;
};

#endif // WORDDIC_H
