#ifndef _WINITER_H
#define _WINITER_H

// winiter.h
// 4/29/2014 jichi

#include <windows.h>
#include <functional>

#ifndef WINITER_BEGIN_NAMESPACE
# define WINITER_BEGIN_NAMESPACE namespace WinIter {
#endif
#ifndef WINITER_END_NAMESPACE
# define WINITER_END_NAMESPACE   } // WinIter
#endif

WINITER_BEGIN_NAMESPACE

/**
 *  Top-down iterate the windows belong to the thread and their child windows.
 *  If threadId is 0, process current thread.
 */
void iterThreadChildWindows(DWORD threadId, const std::function<void (HWND)> &closure);

inline void iterThreadChildWindows(const std::function<void (HWND)> &closure)
{ iterThreadChildWindows(::GetCurrentThreadId(), closure); }

WINITER_END_NAMESPACE

#endif // _WINITER_H
