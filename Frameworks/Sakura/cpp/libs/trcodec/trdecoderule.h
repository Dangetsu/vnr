#ifndef TRDDECODERULE_H
#define TRDDECODERULE_H

// trdecoderule.h
// 9/20/2014 jichi

#include "trcodec/trrule.h"
#include "sakurakit/skglobal.h"
#include <boost/algorithm/string.hpp>
#include <boost/regex.hpp>
#include <vector>

class TranslationDecodeRule : private TranslationBaseRule
{
  SK_EXTEND_CLASS(TranslationDecodeRule, TranslationBaseRule)

  enum : char { source_symbol_sep = '|' }; // any character that does not exist in token

  mutable bool valid; // whether the object is valid
  std::wstring target;
  std::string source_symbols; // symbols in source separated by ','
  size_t source_symbol_count;
public:
  using Base::match_category;

  TranslationDecodeRule() : valid(false), source_symbol_count(0) {}
  ~TranslationDecodeRule() {}

  void init(const TranslationRule &param);
  bool is_valid() const { return valid; }

public:
  /// Render target replacement
  std::wstring render_target(const std::vector<std::wstring> &args, bool mark = true) const;
};

#endif // TRDECODERULE_H
