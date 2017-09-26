// profile/locale.cc
// 6/15/2014

#include "profile.h"
#include "windbg/hijack.h"
#include <windows.h>

namespace { // unnamed

enum { LCID = 0x411 };

// Return 0x411 on the first call
LANGID WINAPI newGetSystemDefaultLangID()
{
  //return LCID;
  static bool once = false;
  if (!once) {
    once = true;
    return LCID;
  } else
    return ::GetSystemDefaultLangID();
}

} // unnamed namespace

namespace LocaleProfile {

bool load()
{
  if (::GetSystemDefaultLangID() != LCID) {
    HMODULE hModule = ::GetModuleHandleA(nullptr);
    return WinDbg::overrideFunctionA(hModule, "kernel32.dll", "GetSystemDefaultLangID", newGetSystemDefaultLangID);
  }
  return false;
}

} // namespace LocaleProfile

// EOF
