#ifndef TRRULE_H
#define TRRULE_H

// trrule.h
// 9/20/2014 jichi

#include <boost/algorithm/string.hpp>
#include <boost/regex.hpp>
#include <cstdint>

struct TranslationRule
{
  uint8_t flags;
  int id,
      category;
  std::wstring source,  // the RHS source
               target;  // the RHS target

  enum : uint8_t {
    RegexFlag = 1
    , IcaseFlag = 1 << 1
  };

  void set_regex(bool t = true) { if (t) flags |= RegexFlag; else flags &= ~RegexFlag; }
  void set_icase(bool t = true) { if (t) flags |= IcaseFlag; else flags &= ~IcaseFlag; }

  bool is_regex() const { return flags & RegexFlag; }
  bool is_icase() const { return flags & IcaseFlag; }

  TranslationRule() : flags(0), id(0), category(-1) {}
};

class CompiledTranslationRule
{
  int id,
      category;
  std::wstring target;
  mutable boost::wregex *source_re; // cached compiled regex
  mutable std::wstring rendered_target;

public:
  CompiledTranslationRule() : id(0), category(-1), source_re(nullptr) {}
  ~CompiledTranslationRule() { if (source_re) delete source_re; }

  bool is_valid() const { return source_re; }

  bool match_category(int v) const { return v & category; }

  void init(const TranslationRule &param);

  bool exists(const std::wstring &text) const;
  void replace(std::wstring &ret, bool mark) const;

private:
  std::wstring render_target() const; //const std::wstring &matched_text = std::wstring()) const;
  void cache_target() const
  {
    if (!target.empty() && rendered_target.empty())
      rendered_target = render_target();
  }
};

#endif // TRRULE_H
