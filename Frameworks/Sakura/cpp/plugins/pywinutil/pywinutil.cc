// pywinutil.cc
// 6/13/2013

#include "pywinutil/pywinutil.h"
#include "winshell/winshell.h"
#include <windows.h>

namespace { // unnamed

static inline std::wstring toNativeSeparators(const std::wstring &input)
{
  std::wstring ret = input;
  for (size_t i = 0; i < ret.size(); i++)
    if (ret[i] == L'/')
      ret[i] = L'\\';
  return ret;
}

} // unnamed namespace

std::wstring WinUtil::resolveLink(const std::wstring &input)
{
  wchar_t buf[MAX_PATH];
  std::wstring path = ::toNativeSeparators(input);
  return WinShell::resolveLink(path.c_str(), buf, MAX_PATH) ? buf : L"";
}

std::wstring WinUtil::toLongPath(const std::wstring &input)
{
  wchar_t buf[MAX_PATH];
  std::wstring path = ::toNativeSeparators(input);
  size_t size = ::GetLongPathNameW(path.c_str(), buf, MAX_PATH);
  return size ? std::wstring(buf, size) : std::wstring();
}

std::wstring WinUtil::toShortPath(const std::wstring &input)
{
  wchar_t buf[MAX_PATH];
  std::wstring path = ::toNativeSeparators(input);
  size_t size = ::GetShortPathNameW(path.c_str(), buf, MAX_PATH);
  return size ? std::wstring(buf, size) : std::wstring();
}

// EOF
