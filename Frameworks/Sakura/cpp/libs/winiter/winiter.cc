// winitertl.cc
// 4/29/2014 jichi

#include "winiter/winitertl.h"
#include <tlhelp32.h>

WINITER_BEGIN_NAMESPACE

static BOOL CALLBACK iterThreadChildWindowsProc(HWND hWnd, LPARAM lParam)
{
  typedef std::function<void (HWND)> fun_type;
  (*(fun_type *)lParam)(hWnd);
  ::EnumChildWindows(hWnd, (WNDENUMPROC)iterThreadChildWindowsProc, lParam);
  return TRUE;
}

void iterThreadChildWindows(DWORD threadId, const std::function<void (HWND)> &closure)
{
  if (!threadId)
    threadId = ::GetCurrentThreadId();
  ::EnumThreadWindows(threadId, (WNDENUMPROC)iterThreadChildWindowsProc, (LPARAM)&closure);
}

WINITER_END_NAMESPACE

// EOF
