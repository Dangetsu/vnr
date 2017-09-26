#ifndef TRENCODE_H
#define TRENCODE_H

// trencode.h
// 9/20/2014 jichi

#include "sakurakit/skglobal.h"
#include "trcodec/trrule.h"

class TranslationEncoderPrivate;
class TranslationEncoder
{
  SK_CLASS(TranslationEncoder)
  SK_DISABLE_COPY(TranslationEncoder)
  SK_DECLARE_PRIVATE(TranslationEncoderPrivate)

  // - Construction -
public:
  TranslationEncoder();
  ~TranslationEncoder();

  // Initialization

  ///  Return the number of loaded rules
  int size() const;

  ///  Return whether the script has been loaded, thread-safe
  bool isEmpty() const;

  ///  Clear the loaded script
  void clear();

  ///  Add script from file
  void setRules(const TranslationRuleList &rules);

  // Replacement

  /// Encode translation with selected category and limit maximum number of iterations
  void encode(std::wstring &text, int selector = -1, int limit = 100) const;
};

#endif // TRENCODE_H
