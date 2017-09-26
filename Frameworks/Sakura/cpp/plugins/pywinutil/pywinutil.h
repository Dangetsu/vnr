#ifndef PYWINUTIL_H
#define PYWINUTIL_H

// pywinutil.h
// 6/13/2013 jichi

#include <string>

namespace WinUtil {
std::wstring resolveLink(const std::wstring &lnkfile);
std::wstring toShortPath(const std::wstring &longpath);
std::wstring toLongPath(const std::wstring &shortpath);
} // namespace WinUtil

#endif // PYWINUTIL
