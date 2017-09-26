// winquery.cc
// 2/1/2013 jichi
// TODO: Rewrite these functinos using my winiter lib.
#include "winquery/winquery.h"

//#define DEBUG "wingui"
#include "sakurakit/skdebug.h"

// - Helprs -

namespace { // unnamed

typedef struct tag_HWND_DWORD {
  HWND hwnd;
  DWORD dword;
} HWND_DWORD, *PHWND_DWORD;

BOOL CALLBACK getAnyWindowWithThreadIdProc(HWND hwnd, LPARAM lparam)
{
  DWORD dwThreadId = ::GetWindowThreadProcessId(hwnd, nullptr);
  auto lp = reinterpret_cast<PHWND_DWORD>(lparam);
  //Q_ASSERT(lp);
  if (dwThreadId == lp->dword) {
    lp->hwnd = hwnd;
    return FALSE; // break enumeration
  } else
    return TRUE; // continue enumeration
}

BOOL CALLBACK getAnyWindowWithProcessIdProc(HWND hwnd, LPARAM lparam)
{
  DWORD dwProcessId;
  ::GetWindowThreadProcessId(hwnd, &dwProcessId);
  auto lp = reinterpret_cast<PHWND_DWORD>(lparam);
  //Q_ASSERT(lp);
  if (dwProcessId == lp->dword) {
    lp->hwnd = hwnd;
    return FALSE; // break enumeration
  } else
    return TRUE; // continue enumeration
}

} // unnamed namespace

WINQUERY_BEGIN_NAMESPACE

HWND getAnyWindowWithThreadId(DWORD threadId)
{
  HWND_DWORD tuple = { nullptr, threadId };
  ::EnumWindows(getAnyWindowWithThreadIdProc, reinterpret_cast<LPARAM>(&tuple));
  return tuple.hwnd;
}

HWND getAnyWindowWithProcessId(DWORD processId)
{
  HWND_DWORD tuple = { nullptr, processId };
  ::EnumWindows(getAnyWindowWithProcessIdProc, reinterpret_cast<LPARAM>(&tuple));
  return tuple.hwnd;
}

HWND getAnyWindowInCurrentProcess()
{  return getAnyWindowWithProcessId(::GetCurrentProcessId()); }

WINQUERY_END_NAMESPACE

// EOF
