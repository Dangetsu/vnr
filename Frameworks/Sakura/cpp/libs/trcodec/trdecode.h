#ifndef TRDECODE_H
#define TRDECODE_H

// trdecode.h
// 9/20/2014 jichi

#include "sakurakit/skglobal.h"
#include "trcodec/trrule.h"

class TranslationDecoderPrivate;
class TranslationDecoder
{
  SK_CLASS(TranslationDecoder)
  SK_DISABLE_COPY(TranslationDecoder)
  SK_DECLARE_PRIVATE(TranslationDecoderPrivate)

  // - Construction -
public:
  TranslationDecoder();
  ~TranslationDecoder();

  // Initialization

  ///  Return the number of loaded rules
  int size() const;

  ///  Return whether the script has been loaded, thread-safe
  bool isEmpty() const;

  ///  Clear the loaded script
  void clear();

  ///  Add script from file
  void addRules(const TranslationRuleList &rules);

  void setRules(const TranslationRuleList &rules)
  {
    clear();
    addRules(rules);
  }

  // Replacement

  /// Decode translation with selected category and limit maximum number of iterations
  void decode(std::wstring &text, int selector = -1, bool mark = false) const;
};

#endif // TRDECODE_H
