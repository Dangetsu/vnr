// hijackmodule.cc
// 1/27/2013 jichi
#include "hijack/hijackmodule.h"
#include "hijack/hijackmodule_p.h"
#include "hijack/hijackfuns.h"
#include "windbg/hijack.h"
#include "winiter/winiterps.h"
#include "cpputil/cpppath.h"
#include <boost/foreach.hpp>

#ifdef _MSC_VER
# pragma warning (disable:4996)   // C4996: use POSIX function (wcsnimp)
#endif // _MSC_VER

// - Helpers -

namespace { // unnamed

const Hijack::FunctionInfo HIJACK_FUNCTIONS[] = { HIJACK_FUNCTIONS_INITIALIZER };

inline LPCWSTR applicationPathW()
{
  static WCHAR r[MAX_PATH];
  if (!*r)
    ::GetModuleFileNameW(nullptr, r, MAX_PATH);
  return r;
}

inline LPCWSTR applicationNameW()
{
  static LPCWSTR r = nullptr;
  if (!r && (r = applicationPathW()))
    r = ::cpp_wbasename(r);
  return r;
}

} // unnamed namespace

// API

void Hijack::overrideModules()
{
  LPCWSTR exeName = applicationNameW(),
          exePath = applicationPathW();
  if (!exeName || !exePath) {
    //dmsg("failed to get application name or path");
    return;
  }

  WCHAR path[MAX_PATH];
  WinIter::iterProcessModules([=, &path](HMODULE hModule) {
    if (::GetModuleFileNameW(hModule, path, MAX_PATH) &&
        !::wcsnicmp(path, exePath, exeName - exePath))
      overrideModuleFunctions(hModule);
  });
}

void Hijack::restoreModules()
{
  LPCWSTR exeName = applicationNameW(),
          exePath = applicationPathW();
  if (!exeName || !exePath)
    return;

  WCHAR path[MAX_PATH];
  WinIter::iterProcessModules([=, &path](HMODULE hModule) {
    if (::GetModuleFileNameW(hModule, path, MAX_PATH) &&
        !::wcsnicmp(path, exePath, exeName - exePath))
      restoreModuleFunctions(hModule);
  });
}

void Hijack::overrideModuleFunctions(HMODULE hModule)
{
  BOOST_FOREACH (const auto &fn, HIJACK_FUNCTIONS)
    if (PVOID ret = WinDbg::overrideFunctionA(hModule, fn.moduleName, fn.functionName, fn.newFunctionAddress)) {
      //dmsg(fn.functionName); // success
    }
}


void Hijack::restoreModuleFunctions(HMODULE hModule)
{
  BOOST_FOREACH (const auto &fn, HIJACK_FUNCTIONS)
    WinDbg::overrideFunctionA(hModule, fn.moduleName, fn.functionName, fn.oldFunctionAddress);
}

LPVOID Hijack::getOverridingFunctionAddress(HMODULE hModule, LPCSTR lpProcName)
{
  char modulePath[MAX_PATH];
  if (::GetModuleFileNameA(hModule, modulePath, MAX_PATH))
    if (const char *moduleName = ::cpp_basename(modulePath))
      BOOST_FOREACH (const auto &fn, HIJACK_FUNCTIONS)
        if (!::stricmp(moduleName, fn.moduleName) && !::stricmp(lpProcName, fn.functionName))
          return fn.newFunctionAddress;
  return nullptr;
}

// EOF
