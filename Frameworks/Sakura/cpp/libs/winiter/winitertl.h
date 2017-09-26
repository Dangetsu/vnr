#pragma once

// winitertl.h
// 4/29/2014 jichi
// For <tlhelp32.h>

#include "winiter/winiter.h"

WINITER_BEGIN_NAMESPACE

/**
 *  Traverse the child threads.
 *  If processId is 0, process current process.
 */
void iterProcessThreadIds(DWORD processId, const std::function<void (DWORD)> &closure);

inline void iterProcessThreadIds(const std::function<void (DWORD)> &closure)
{ iterProcessThreadIds(::GetCurrentProcessId(), closure); }

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
