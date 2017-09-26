// winitertl.cc
// 4/29/2014 jichi

#include "winiter/winitertl.h"
#include <tlhelp32.h>

WINITER_BEGIN_NAMESPACE

void iterProcessThreadIds(DWORD processId, const std::function<void (DWORD)> &closure)
{
  HANDLE h = ::CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, processId);
  if (h == INVALID_HANDLE_VALUE)
    return;
  if (!processId)
    processId = ::GetCurrentProcessId();
  THREADENTRY32 thread = {};
  thread.dwSize = sizeof(thread);
  if (::Thread32First(h, &thread))
    do if (thread.th32OwnerProcessID == processId)
      closure(thread.th32ThreadID);
    while (::Thread32Next(h, &thread));
  ::CloseHandle(h);
}

WINITER_END_NAMESPACE

// EOF
