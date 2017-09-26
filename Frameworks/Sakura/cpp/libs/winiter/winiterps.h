#pragma once

// winitertl.h
// 4/29/2014 jichi
// For <Psapi.h>, require lpsapi.

#include "winiter/winiter.h"

WINITER_BEGIN_NAMESPACE

/**
 *  Traverse the modules.
 *  If hProcess is null, process current process.
 */
void iterProcessModules(HANDLE hProcess, const std::function<void (HMODULE)> &closure);

inline void iterProcessModules(const std::function<void (HMODULE)> &closure)
{ iterProcessModules(::GetCurrentProcess(), closure); }

WINITER_END_NAMESPACE

// EOF


//inline void iterProcessThreadIds(DWORD processId, std::function<void (DWORD)> closure)
//{
//  iterProcessThreadIds(processId, std::function<void (DWORD)>(
//    [=](DWORD arg1) -> bool {
//      closure(arg1);
//      return true;
//    }));
//}
