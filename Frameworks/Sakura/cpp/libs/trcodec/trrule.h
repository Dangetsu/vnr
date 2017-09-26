#ifndef TRRULE_H
#define TRRULE_H

// trrule.h
// 9/20/2014 jichi

#include <cstdint>
#include <list>
#include <string>


struct TranslationBaseFlag
{
  mutable uint8_t flags;
  TranslationBaseFlag() : flags(0) {}

  bool has_flag(uint8_t f) const { return flags & f; }
  void set_flag(uint8_t f, bool t = true) { if (t) flags |= f; else flags &= ~f; }

  enum : uint8_t {
    TranslationRegexFlag = 1          // source is regular expression
    , TranslationIcaseFlag = 1 << 1   // ignore case for source
  };

#define DEF_FLAG(_method, _flag) \
  bool is_##_method() const { return has_flag(_flag); } \
  void set_##_method(bool t = true) { set_flag(_flag, t); }

  DEF_FLAG(regex, TranslationRegexFlag)
  DEF_FLAG(icase, TranslationIcaseFlag)
#undef DEF_FLAG
};

struct TranslationBaseRule : TranslationBaseFlag
{
  int id,
      category;

  bool match_category(int v) const { return v & category; }

  TranslationBaseRule() : id(0), category(-1) {}
};

struct TranslationRule : TranslationBaseRule
{
  std::string token;    // the LHS token
  std::wstring source,  // the RHS source
               target;  // the RHS target
};

typedef std::list<TranslationRule> TranslationRuleList;

#endif // TRRULE_H
