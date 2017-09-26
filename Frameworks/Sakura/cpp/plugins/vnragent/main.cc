// main.cc
// 1/27/2013
// No Qt can appear in this file!
//
// It is very important to restrict from accessing Qt in this file, and make sure the instance to start with wintimer.
// Qt must have the same internal timer with the program's main window.

#include "config.h"
#include "winquery/winquery.h"
#include "wintimer/wintimer.h"
#include "winiter/winitertl.h"
#include "winsinglemutex/winsinglemutex.h"
#include "loader.h"
#include "ccutil/ccmacro.h"

namespace { // unnamed

HWND waitForWindowReady_(int retryCount = 100, int sleepInterval = 100) // retry for 10 seconds
{
  for (int i = 0; i < retryCount; i++) {
    if (HWND winId = WinQuery::getAnyWindowInCurrentProcess())
      return winId;
    ::Sleep(sleepInterval);
  }
  return nullptr;
}

HMODULE waitForModuleReady_(const char *name, int retryCount = 100, int sleepInterval = 100) // retry for 10 seconds
{
  for (int i = 0; i < retryCount; i++) {
    if (HMODULE h = ::GetModuleHandleA(name))
      return h;
    ::Sleep(sleepInterval);
  }
  return nullptr;
}

///  Kill the current process
void harakiri_() { ::TerminateProcess(::GetCurrentProcess(), EXIT_SUCCESS); }

///  Set the priority of all existing threads to the lowest.
void suppressExistingThreadsPriories_()
{
  WinIter::iterProcessThreadIds([] (DWORD threadId) {
    if (HANDLE h = ::OpenThread(THREAD_ALL_ACCESS, FALSE, threadId)) {
      ::SetThreadPriority(h, THREAD_PRIORITY_LOWEST);
      ::CloseHandle(h);
    }
  });
}

} // unnamed namespace

// - Main -

BOOL WINAPI DllMain(_In_ HINSTANCE hInstance, _In_ DWORD fdwReason, _In_ LPVOID lpvReserved)
{
  CC_UNUSED(lpvReserved);
  switch (fdwReason) {
  case DLL_PROCESS_ATTACH:
    if (!WinSingleMutex::acquire("vnragent"))
      //growl::error("already injected");
      return FALSE;

    ::DisableThreadLibraryCalls(hInstance); // Disable DLL_THREAD_ATTACH and DLL_THREAD_DETACH notifications

#ifdef VNRAGENT_ENABLE_THREAD
    suppressExistingThreadsPriories_();
    if (HANDLE h = ::CreateThread(nullptr, 0, (LPTHREAD_START_ROUTINE)Loader::initWithInstance, hInstance, 0, nullptr)) {
      // This is critical to make sure that the socket communication is delivered
      ::SetThreadPriority(h, THREAD_PRIORITY_HIGHEST|THREAD_PRIORITY_TIME_CRITICAL);
      ::CloseHandle(h);
    } else
      //growl::error("failed to create thread");
      return FALSE;
#else
    if (HWND winId = waitForWindowReady_())
      WinTimer::setGlobalWindow(winId);
    else
      //growl::error("failed to find main window");
      return FALSE;

    // It is critical to launch Qt application in the same thread as main window
    WinTimer::singleShot(100, [hInstance] {
      Loader::initWithInstance(hInstance);
    });
#endif // VNRAGENT_ENABLE_THREAD
    break;

  case DLL_PROCESS_DETACH:
    //if (HWND winId = WinQuery::getAnyWindowInCurrentProcess())
    //  WinTimer::singleShot(5000, harakiri_, winId);  // If hang, terminate the process in 5 seconds.
    Loader::destroy();
    break;
  }
  //SK_ASSERT(0);
  return TRUE;
}

// EOF

    //else
    //  //growl::error("cannot find window");
    //  return FALSE;

    //while(!::GetModuleHandleA("gdi32.dll"))
    //  ::Sleep(200);
    //while(!::GetModuleHandleA("d3d9.dll"))
    //  ::Sleep(200);
    //::CreateThread(nullptr, 0, reinterpret_cast<LPTHREAD_START_ROUTINE>(d3dhook), nullptr, 0, nullptr);
