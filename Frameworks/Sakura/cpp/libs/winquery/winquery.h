#pragma once

// winquery.h
// 2/1/2013 jichi

#include <windows.h>

#ifndef WINQUERY_BEGIN_NAMESPACE
# define WINQUERY_BEGIN_NAMESPACE namespace WinQuery {
#endif
#ifndef WINQUERY_END_NAMESPACE
# define WINQUERY_END_NAMESPACE   } // namespace WinQuery
#endif

WINQUERY_BEGIN_NAMESPACE

HWND getAnyWindowWithThreadId(_In_ DWORD threadId);
HWND getAnyWindowWithProcessId(_In_ DWORD processId);

/// Return any visible window in the current process
HWND getAnyWindowInCurrentProcess();

WINQUERY_END_NAMESPACE

// EOF
