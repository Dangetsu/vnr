#ifndef TRCODEC_H
#define TRCODEC_H

// trcode.h
// 9/20/2014 jichi

#include "sakurakit/skglobal.h"
#include <string>

class TranslationCoderPrivate;
class TranslationCoder
{
  SK_CLASS(TranslationCoder)
  SK_DISABLE_COPY(TranslationCoder)
  SK_DECLARE_PRIVATE(TranslationCoderPrivate)

  // - Construction -
public:
  TranslationCoder();
  ~TranslationCoder();

  // Initialization

  ///  Return the number of loaded rules
  int size() const;

  ///  Return whether the script has been loaded, thread-safe
  bool isEmpty() const;

  ///  Clear the loaded script
  void clear();

  ///  Add script from file
  bool loadScript(const std::wstring &path);

  // Transformation

  /// Encode translation with selected category and limit maximum number of iterations
  std::wstring encode(const std::wstring &text, int selector = -1, int limit = 100) const;

  /// Decode translation with selected category and limit maximum number of iterations, and mark changes
  std::wstring decode(const std::wstring &text, int selector = -1, bool mark = false) const;
};

#endif // TRCODEC_H
