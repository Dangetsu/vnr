// winiterss.cc
// 4/29/2014 jichi

#include "winiter/winiterps.h"
#include <psapi.h>

WINITER_BEGIN_NAMESPACE

void iterProcessModules(HANDLE hProcess, const std::function<void (HMODULE)> &closure)
{
  if (!hProcess)
    hProcess = ::GetCurrentProcess();
  enum { MAX_MODULE = 0x800 };
  HMODULE modules[MAX_MODULE];
  DWORD size;
  if (::EnumProcessModules(::GetCurrentProcess(), modules, sizeof(modules), &size) && (size/=4))
    for (DWORD i = 0; i < size; i++)
      closure(modules[i]);
}

WINITER_END_NAMESPACE

// EOF
