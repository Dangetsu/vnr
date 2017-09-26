// trsym.cc
// 3/5/2015 jichi
#include "trsym/trsym.h"
#include "trsym/trsymdef.h"
#include "cpputil/cppregex.h"
#include "cpputil/cppstring.h"
#include <stack>
#include <boost/algorithm/string.hpp>
#include <boost/regex.hpp>
//#include <QDebug>

#define SK_NO_QT
#define DEBUG "trsym.cc"
#include "sakurakit/skdebug.h"

#define SYMBOL_ESCAPE_RE L"\\|?!.+*^<>(){}" // characters needed to be escaped for a regex, except [] and $

// Precompiled regex
namespace { namespace rx {

const boost::wregex
  // To test [[x#123]]
  raw_symbol(
    L"\\[\\["
      TRCODEC_RE_TOKEN
      L"(?:#[0-9]+)?"
    L"\\]\\]"
  )

  // To capture [[x#123]]'s x part
  , raw_symbol_with_token_group(
    L"\\[\\["
      L"(" TRCODEC_RE_TOKEN L")"
      L"(?:#[0-9]+)?"
    L"\\]\\]"
  )

  // To capture [[x#123]]'s both x and #123 part
  , raw_symbol_with_symbol_group(
    L"\\[\\["
      L"("
        TRCODEC_RE_TOKEN
        L"(?:#[0-9]+)?"
      L")"
    L"\\]\\]"
  )

  // To test {{x<123>}}
  , encoded_symbol(
    L"{{"
      TRCODEC_RE_TOKEN
      L"<[-0-9<>]+>"
    L"}}"
  )

  // To capture {{x<123>}}'s <123> parts
  , encoded_symbol_with_param_group(
    L"{{"
      TRCODEC_RE_TOKEN
      L"(" L"<[-0-9<>]+>" L")"
    L"}}"
  )
;

}} // unnamed namespace rx

bool trsym::contains_raw_symbol(const std::wstring &s)
{
  return boost::algorithm::contains(s, "[[")
      && cpp_regex_contains(s, rx::raw_symbol);
}

bool trsym::contains_encoded_symbol(const std::wstring &s)
{
  return boost::algorithm::contains(s, "{{")
      && cpp_regex_contains(s, rx::encoded_symbol);
}

std::string trsym::create_symbol_target(const std::string &token, int id, int argc)
{
  std::string ret = "{{";
  ret += token;
  ret += '<';
  if (argc) {
    for (int i = 1; i <= argc; i++) {
      ret.push_back('\\'); // must be '\\' instead of '$' to avoid using {}
      if (i < 10)
        ret.push_back('0' + i);
      else {
        ret += '{';
        ret += std::to_string((long long)i);
        ret += '}';
      }
    }
  }
  ret += std::to_string((long long)id);
  ret += ">}}";
  return ret;
}

size_t trsym::count_raw_symbols(const std::wstring &s)
{
  return !boost::algorithm::contains(s, "[[") ? 0
       : ::cpp_regex_count(s, rx::raw_symbol);
}

/// Return whether a text contains regex special chars except '[]'
static inline bool _symbol_needs_escape_re(const std::wstring &s)
{ return std::wstring::npos != s.find_first_of(SYMBOL_ESCAPE_RE); }

/// Escape regex special chars. FIXME: This logic does not consider '$'
static inline std::wstring _symbol_escape_re(const wchar_t *s)
{
  std::wstring ret;
  while (wchar_t c = *s++) {
    if (::wcschr(SYMBOL_ESCAPE_RE, c))
      ret.push_back(L'\\');
    ret.push_back(c);
  }
  return ret;
}

static inline std::wstring _symbol_escape_re(const std::wstring &s)
{ return _symbol_escape_re(s.c_str()); }

#define _ENCODE_SYMBOL_MATCH \
  "{{" \
    "$1" \
    "(?:" "[_$]" TRCODEC_RE_TOKEN_A ")?" \
    "\\(<[-0-9<>]+>\\)" \
  "}}"
static std::wstring _encode_symbol_match(const boost::wsmatch &m)
{
  std::wstring ret = L"{{",
               tokens = m[1];
  if (tokens.find(',') == std::wstring::npos)
    ret += tokens;
  else {
    std::replace(tokens.begin(), tokens.end(), L',', L'|');
    ret += L"(?:";
    ret += tokens;
    ret += L')';
  }
  ret +=
    L"(?:" L"[_$]" TRCODEC_RE_TOKEN L")?"
    L"([-0-9<>]+)"
  L"}}";
  return ret;
}

#define _ENCODE_OUTPUT_SYMBOL_MATCH \
"\\(" \
  "{{" \
    "$1" \
    "(?:" "[_$]" TRCODEC_RE_TOKEN_A ")?" \
    "<[-0-9<>]+>" \
  "}}" \
"\\)"
static std::wstring _encode_output_symbol_match(const boost::wsmatch &m)
{
  std::wstring ret = L"({{",
               tokens = m[1];
  if (tokens.find('$') != std::wstring::npos)
    boost::replace_all(tokens, "$", "\\$");
  if (tokens.find(',') == std::wstring::npos)
    ret += tokens;
  else {
    std::replace(tokens.begin(), tokens.end(), L',', L'|');
    ret += L"(?:";
    ret += tokens;
    ret += L')';
  }
  ret +=
    L"(?:" L"[_$]" TRCODEC_RE_TOKEN L")?"
    L"[-0-9<>]+"
  L"}})";
  return ret;
}

std::wstring trsym::encode_symbol(const std::wstring &s, bool escape)
{
  if (s.find(',') == std::wstring::npos) {
    if (escape && _symbol_needs_escape_re(s))
      return boost::regex_replace(_symbol_escape_re(s), rx::raw_symbol_with_token_group, _ENCODE_SYMBOL_MATCH);
    else
      return boost::regex_replace(s, rx::raw_symbol_with_token_group, _ENCODE_SYMBOL_MATCH);
  } else {
    if (escape && _symbol_needs_escape_re(s))
      return boost::regex_replace(_symbol_escape_re(s), rx::raw_symbol_with_token_group, _encode_symbol_match);
    else
      return boost::regex_replace(s, rx::raw_symbol_with_token_group, _encode_symbol_match);
  }
}

std::wstring trsym::encode_output_symbol(const std::wstring &s, bool escape)
{
  if (s.find_first_of(L",$") == std::wstring::npos) {
    if (escape && _symbol_needs_escape_re(s))
      return boost::regex_replace(_symbol_escape_re(s), rx::raw_symbol_with_token_group, _ENCODE_OUTPUT_SYMBOL_MATCH);
    else
      return boost::regex_replace(s, rx::raw_symbol_with_token_group, _ENCODE_OUTPUT_SYMBOL_MATCH);
  } else {
    if (escape && _symbol_needs_escape_re(s))
      return boost::regex_replace(_symbol_escape_re(s), rx::raw_symbol_with_token_group, _encode_output_symbol_match);
    else
      return boost::regex_replace(s, rx::raw_symbol_with_token_group, _encode_output_symbol_match);
  }
}

void trsym::iter_raw_symbols(const std::wstring &target, const collect_string_f &fun)
{
  std::for_each(
    boost::wsregex_iterator(target.cbegin(), target.cend(), rx::raw_symbol_with_symbol_group),
    boost::wsregex_iterator(),
    [&fun](const boost::wsmatch &m) {
      std::string matched_text = ::cpp_string_of(m.str());
      fun(matched_text);
    }
  );
}

// Example text to decode: 4<3<1>>,<2>
static std::wstring _decode_symbol_stack(const char *str, const trsym::decode_f &fun)
{
  std::vector<std::wstring> args;

  {
    // Optimization for the first case <id>
    const char *pos;
    if (int id = ::strtol(str + 1, const_cast<char **>(&pos), 10))
      if (pos[0] == '>' && pos[1] == 0)
        return fun(id, args);
  }

  std::stack<std::wstring> tokens;
  while (char ch = *str++)
    if (ch == '<')
       tokens.push(std::wstring());
    else {
      if (::isdigit(ch) || ch == '-')
        if (int id = ::strtol(str - 1, const_cast<char **>(&str), 10))
          if (*str++ == '>') { // start reduce
            while (!tokens.empty() && !tokens.top().empty()) {
              args.insert(args.begin(), tokens.top()); // might be slow to insert at the beginning
              tokens.pop();
            }
            if (!tokens.empty()) {
              tokens.pop();
              std::wstring tok = fun(id, args);
              if (!tok.empty()) {
                tokens.push(tok);
                if (!args.empty())
                  args.clear();
                continue;
              }
            }
          }
      DERR("failed to decode symbol id");
      return std::wstring();
    }


  if (tokens.size() == 1)
    return tokens.top();

  DERR("failed to decode symbol stack");
  return std::wstring();
}

std::wstring trsym::decode_symbol(const std::wstring &text, const decode_f &fun)
{
  return boost::regex_replace(text, rx::encoded_symbol_with_param_group,
    [&fun](const boost::wsmatch &m) -> std::wstring {
      std::string matched_text = ::cpp_string_of(m.str(1));
      return _decode_symbol_stack(matched_text.c_str(), fun);
    }
  );
}

// EOF
