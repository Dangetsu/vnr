// main.cc
// 5/15/2014

#include "profile.h"
#include "winsinglemutex/winsinglemutex.h"
#include "ccutil/ccmacro.h"
#include <windows.h>

// - Main -

BOOL WINAPI DllMain(_In_ HINSTANCE hInstance, _In_ DWORD fdwReason, _In_ LPVOID lpvReserved)
{
  CC_UNUSED(lpvReserved);
  switch (fdwReason) {
  case DLL_PROCESS_ATTACH:
    ::DisableThreadLibraryCalls(hInstance); // Disable DLL_THREAD_ATTACH and DLL_THREAD_DETACH notifications

    if (!WinSingleMutex::acquire("vnrboot"))
      //dmsg("already injected");
      return FALSE;

    Profile::load();
    break;

  case DLL_PROCESS_DETACH:
    Profile::destroy();
    break;
  }
  //SK_ASSERT(0);
  return TRUE;
}

// EOF
