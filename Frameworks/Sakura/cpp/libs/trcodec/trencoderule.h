#ifndef TRENCODERULE_H
#define TRENCODERULE_H

// trencoderule.h
// 9/20/2014 jichi

#include "trcodec/trrule.h"
#include "sakurakit/skglobal.h"
#include <boost/algorithm/string.hpp>
#include <boost/regex.hpp>

class TranslationEncodeRule : private TranslationBaseRule
{
  SK_EXTEND_CLASS(TranslationEncodeRule, TranslationBaseRule)

  mutable bool valid; // whether the object is valid

  std::string *target,  // cached replacement, use pointer to avoid contention
               target_token; // the LHS token
  std::wstring source;       // the RHS source
  boost::wregex *source_re;  // cached compiled regex. Either source_re or source exists after init.
  size_t source_symbol_count;

public:
  using Base::match_category;

  TranslationEncodeRule()
    : valid(false), target(nullptr), source_re(nullptr), source_symbol_count(0) {}

  ~TranslationEncodeRule()
  {
    if (target) delete target;
    if (source_re) delete source_re;
  }

  void init(const TranslationRule &param);
  bool is_valid() const { return valid; }
  bool is_symbolic() const { return source_symbol_count; }

  // Replacement
private:
  void init_source(); // may throw regular expression exception
  void init_target();

  void cache_target() const
  {
    if (!target && !target_token.empty())
      self()->init_target();
  }

  void string_replace(std::wstring &ret) const;
  void regex_replace(std::wstring &ret) const;

  bool string_exists(const std::wstring &t) const // inline to make this function faster
  { return is_icase() ? boost::algorithm::icontains(t, source) : boost::algorithm::contains(t, source); }

  bool regex_exists(const std::wstring &t) const;

  bool exists(const std::wstring &text) const
  { return is_regex() ? regex_exists(text) : string_exists(text); }

public:
  bool replace(std::wstring &ret) const
  {
    if (!exists(ret))
      return false;
    if (is_regex())
      regex_replace(ret);
    else
      string_replace(ret);
    return true;
  }
};

#endif // TRENCODERULE_H
