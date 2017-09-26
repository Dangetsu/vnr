#pragma once

// winshell.h
// 6/13/2013 jichi

#ifdef _MSC_VER
# include <cstddef> // for wchar_t
#endif // _MSC_VER

namespace WinShell {
bool resolveLink(const wchar_t *link, wchar_t *buf, int bufsize);
} // namespace WinShell

// EOF
