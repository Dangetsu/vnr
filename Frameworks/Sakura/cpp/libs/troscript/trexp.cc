// trexp.cc
// 5/17/2015 jichi
#include "troscript/trexp.h"
#include "trsym/trsym.h"
#include <vector>
#include <boost/algorithm/string.hpp>
//#include <QDebug>

#define SK_NO_QT
#define DEBUG "trexp.cc"
#include "sakurakit/skdebug.h"

std::wstring trexp::compile_format(const std::wstring &target, const std::wstring &source)
{
  size_t source_symbol_count = trsym::count_raw_symbols(source);
  if (!source_symbol_count)
    return target;
  std::wstring ret = target;
  if (source_symbol_count == 1) { // optimize if there is only one symbol, replace between "[[", "]]" by "$1"
    size_t start = ret.find(L"[[");
    if (start != std::wstring::npos) {
      size_t stop = ret.find(L"]]", start);
      if (stop != std::wstring::npos)
        ret.replace(start, stop - start + 2, L"$1"); // 2 = len("]]")
    }
  } else {
    std::vector<std::string> symbols;
    symbols.reserve(source_symbol_count);
    trsym::iter_raw_symbols(source, [&symbols](const std::string &it) {
      symbols.push_back(it);
    });
    for (size_t i = 0; i < symbols.size(); i++) {
      std::string repl = "$" + std::to_string(i + 1ll);
      boost::replace_all(ret, symbols[i], repl);
    }

    if (source.find('#') != std::wstring::npos && ret.find('#') != std::wstring::npos) // there might be unhandled '#'
      for (size_t i = 0; i < symbols.size(); i++) {
        size_t pos = symbols[i].find('#');
        if (pos != std::wstring::npos) {
          std::string pat = "[[" + symbols[i].substr(pos),
                      repl = "$" + std::to_string(i + 1ll);
          boost::replace_all(ret, pat, repl);
        }
      }
  }
  return ret;
}

// EOF
