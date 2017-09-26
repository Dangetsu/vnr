// trrule.cc
// 9/20/2014 jichi

#include "trscript/trrule.h"
#include "cpputil/cppregex.h"
//#include <QDebug>

#define SK_NO_QT
#define DEBUG "trrule.cc"
#include "sakurakit/skdebug.h"

#define WITH(...) \
  try { \
    __VA_ARGS__ \
  } catch (boost::regex_error &e) { \
    DWERR("invalid term: " << id << ", what: " << e.what() << ", regex pattern: " << source); \
    valid = false; \
  }

// Render

#ifdef  WITH_LIB_TRRENDER
# include "trrender/trrender.h"
#endif // TRRENDER_ENABLED

std::wstring TranslationScriptRule::render_target() const
{
#ifdef WITH_LIB_TRRENDER
  return ::tr_render_rule(target, id); // complete = false, which is expensive and could break regex
#else
  return L"<u>" + target + L"</u>";
#endif // WITH_LIB_TRRENDER
}

// Construction

void TranslationScriptRule::init(const Base &param, bool precompile_regex)
{
  flags = param.flags;
  id = param.id;
  category = param.category;
  source = param.source;
  target = param.target;

  if (is_regex() && precompile_regex)
    WITH (
      cache_re();
      valid = true;
    )
  else
    valid = true; // must do this at the end
}

// Replacement

void TranslationScriptRule::string_replace(std::wstring &ret, bool mark) const
{
  if (target.empty()) {
    if (is_icase())
      boost::ierase_all(ret, source);
    else
      boost::erase_all(ret, source);
  } else {
    if (mark)
      cache_target();
    if (is_icase())
      boost::ireplace_all(ret, source,
                          mark ? rendered_target : target);
    else
      boost::replace_all(ret, source,
                         mark ? rendered_target : target);
  }
}

void TranslationScriptRule::regex_replace(std::wstring &ret, bool mark) const
{
  WITH (
    // match_default is the default value
    // format_all is needed to enable all features, but it is sligntly slower
    cache_re();
    if (target.empty() || !mark)
      ret = boost::regex_replace(ret, *source_re, target,
          boost::match_default|boost::format_all);
    else {
      if (mark)
        cache_target();
      //auto repl = [this](const boost::wsmatch &m) {
      //  return render_target(m[0]);
      //};
      ret = boost::regex_replace(ret, *source_re, mark ? rendered_target : target,
          boost::match_default|boost::format_all);
    }
  )
}

bool TranslationScriptRule::regex_exists(const std::wstring &t) const
{
  WITH (
    cache_re();
    return ::cpp_regex_contains(t, *source_re);
  )
  return false;
}

// EOF

//bool TranslationScriptRule::children_replace(std::wstring &ret, bool mark) const
//{
//  if (child_count && children)
//    for (size_t i = 0; i < child_count; i++) {
//      const auto &c = children[i];
//      if (c.is_valid() && c.replace(ret, mark) && !exists(ret))
//        return true;
//    }
//  return false;
//}
