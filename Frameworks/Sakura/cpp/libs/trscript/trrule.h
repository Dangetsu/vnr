#ifndef TRRULE_H
#define TRRULE_H

// trrule.h
// 9/20/2014 jichi

#include "sakurakit/skglobal.h"
#include <boost/algorithm/string.hpp>
#include <boost/regex.hpp>
#include <cstdint>

#ifdef __clang__
# pragma clang diagnostic ignored "-Wlogical-op-parentheses"
#endif // __clang__

struct TranslationScriptFlag
{
  uint8_t flags;
  TranslationScriptFlag() : flags(0) {}

  enum : uint8_t {
    RegexFlag = 1
    , IcaseFlag = 1 << 1
  };

  void set_regex(bool t = true) { if (t) flags |= RegexFlag; else flags &= ~RegexFlag; }
  void set_icase(bool t = true) { if (t) flags |= IcaseFlag; else flags &= ~IcaseFlag; }

  bool is_regex() const { return flags & RegexFlag; }
  bool is_icase() const { return flags & IcaseFlag; }
};

struct TranslationScriptBaseRule : TranslationScriptFlag
{
  std::wstring source,
               target;
  int id,
      category;

  TranslationScriptBaseRule() : id(0), category(-1) {}
};

class TranslationScriptRule : private TranslationScriptBaseRule
{
  SK_EXTEND_CLASS(TranslationScriptRule, TranslationScriptBaseRule)

  mutable bool valid; // whether the object is valid
  mutable boost::wregex *source_re; // cached compiled regex
  mutable std::wstring rendered_target; // cached rendered target, use pointer to avoid thread contention

public:
  TranslationScriptRule() : valid(false) , source_re(nullptr) {}
  ~TranslationScriptRule() { if (source_re) delete source_re; }

  bool is_valid() const { return valid; }

  bool match_category(int v) const { return v & category; }

  void init(const Base &param, bool precompile_regex = true);

  // Replacement
private:

  void cache_re() const // may throw
  {
    if (!source_re)
      source_re = new boost::wregex(source,
        is_icase() ? boost::wregex::perl|boost::wregex::icase
                   : boost::wregex::perl
      );
  }

  std::wstring render_target() const; //const std::wstring &matched_text = std::wstring()) const;
  void cache_target() const
  {
    if (!target.empty() && rendered_target.empty())
      rendered_target = render_target();
  }

  void string_replace(std::wstring &ret, bool mark) const;
  void regex_replace(std::wstring &ret, bool mark) const;

  bool string_exists(const std::wstring &t) const // inline to make this function faster
  { return is_icase() ? boost::algorithm::icontains(t, source) : boost::algorithm::contains(t, source); }

  bool regex_exists(const std::wstring &t) const;

public:
  bool exists(const std::wstring &text) const { return is_regex() ? regex_exists(text) : string_exists(text); }

  bool replace(std::wstring &ret, bool mark) const
  {
    if (!exists(ret))
      return false;
    if (is_regex())
      regex_replace(ret, mark);
    else
      string_replace(ret, mark);
    return true;
  }
};

#endif // TRRULE_H
