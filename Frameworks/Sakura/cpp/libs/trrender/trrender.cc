// trrender.cc
// 9/20/2014 jichi

#include "trrender/trrender.h"
#include "trrender/trescape.h"

// A sample expected output without escape:
// <a href='json://{"type":"term","id":12345,"source":"pattern","target":"text"}'>pattern</a>
std::wstring tr_render_rule(const std::wstring &target, int id)
{
  if (id <= 0) // do not encode if no valid id
    return L"<u>" + target + L"</u>";

  std::wstring ret = L"{\"type\":\"term\"";
  ret.append(L",\"id\":")
     .append(std::to_wstring((long long)id));

  // Target could be expensive
  //if (complete) { // do not render regex source/target which is expensive and dangerous
  //  if (!source.empty()) {
  //    std::string s = ::trescape(source);
  //    ret.append(L",\"source\":\"")
  //       .append(s.cbegin(), s.cend())
  //       .push_back('"');
  //  }
  //  if (!target.empty()) {
  //    std::string s = ::trescape(target);
  //    ret.append(L",\"target\":\"")
  //       .append(s.cbegin(), s.cend())
  //       .push_back('"');
  //  }
  //}

  ret.push_back('}');

  ret.insert(0, L"<a href='json://");
  ret.push_back('\'');

  //if (!markStyle.empty())
  //  ret.append(" style=\"")
  //     .append(markStyle)
  //     .append("\"");

  ret.push_back('>');
  ret.append(target)
     .append(L"</a>");
  return ret;
}

// EOF
