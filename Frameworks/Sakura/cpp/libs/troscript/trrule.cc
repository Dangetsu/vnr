// trrule.cc
// 5/17/2015 jichi

#include "troscript/trrule.h"
#include "troscript/trexp.h"
#include "trsym/trsym.h"
#include "cpputil/cppregex.h"
//#include <QDebug>

#define SK_NO_QT
#define DEBUG "trrule.cc"
#include "sakurakit/skdebug.h"

#define WITH(...) \
  try { \
    __VA_ARGS__ \
  } catch (boost::regex_error &e) { \
    DWERR("invalid term: " << id << ", what: " << e.what()); \
    if (source_re) { \
      auto p = source_re; \
      source_re = nullptr; \
      delete p; \
    } \
  }

// Render

#ifdef  WITH_LIB_TRRENDER
# include "trrender/trrender.h"
#endif // TRRENDER_ENABLED

std::wstring CompiledTranslationRule::render_target() const
{
#ifdef WITH_LIB_TRRENDER
  return ::tr_render_rule(target, id); // complete = false, which is expensive and could break regex
#else
  return L"<u>" + target + L"</u>";
#endif // WITH_LIB_TRRENDER
}

// Construction
void CompiledTranslationRule::init(const TranslationRule &param)
{
  id = param.id;
  category = param.category;

  if (!trsym::contains_raw_symbol(param.source)) {
    DWERR("invalid term missing symbol: " << id << ", pattern: " << param.source);
    return;
  }

  bool escape = !param.is_regex();
  std::wstring pattern = trsym::encode_output_symbol(param.source, escape);
  if (!pattern.empty())
    WITH (
      source_re = new boost::wregex(pattern,
        param.is_icase() ? boost::wregex::perl|boost::wregex::icase
                         : boost::wregex::perl
      );
    )

  if (source_re)
    target = trexp::compile_format(param.target, param.source);
}

// Replacement

bool CompiledTranslationRule::exists(const std::wstring &t) const
{
  //if (source_re)
  WITH (
    return ::cpp_regex_contains(t, *source_re);
  )
  return false;
}

void CompiledTranslationRule::replace(std::wstring &ret, bool mark) const
{
  //if (source_re)
  WITH (
    // match_default is the default value
    // format_all is needed to enable all features, but it is sligntly slower
    if (target.empty() || !mark)
      ret = boost::regex_replace(ret, *source_re, target,
          boost::match_default|boost::format_all);
    else {
      if (mark)
        cache_target();
      ret = boost::regex_replace(ret, *source_re, mark ? rendered_target : target,
          boost::match_default|boost::format_all);
    }
  )
}

// EOF
