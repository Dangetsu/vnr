// hijackmodule_kernel32.cc
// 1/27/2013 jichi
#include "hijack/hijackmodule_p.h"

#ifdef _MSC_VER
# pragma warning(disable:4800) // C4800: forcing value to bool
#endif // _MSC_VER

// Libraries and processes

HMODULE WINAPI Hijack::newLoadLibraryA(_In_ LPCSTR lpFileName)
{
  bool loaded = ::GetModuleHandleA(lpFileName); // this is the first load
  HMODULE ret = ::LoadLibraryA(lpFileName);
  if (ret && !loaded)
    overrideModuleFunctions(ret);
  return ret;
}

HMODULE WINAPI Hijack::newLoadLibraryW(_In_ LPCWSTR lpFileName)
{
  bool loaded = ::GetModuleHandleW(lpFileName); // this is the first load
  HMODULE ret = ::LoadLibraryW(lpFileName);
  if (ret && !loaded)
    overrideModuleFunctions(ret);
  return ret;
}

HMODULE WINAPI Hijack::newLoadLibraryExA(_In_ LPCSTR lpFileName, __reserved HANDLE hFile, _In_ DWORD dwFlags)
{
  bool loaded = ::GetModuleHandleA(lpFileName); // this is the first load
  HMODULE ret = ::LoadLibraryExA(lpFileName, hFile, dwFlags);
  if (ret && !loaded)
    overrideModuleFunctions(ret);
  return ret;
}

HMODULE WINAPI Hijack::newLoadLibraryExW(_In_ LPCWSTR lpFileName, __reserved HANDLE hFile, _In_ DWORD dwFlags)
{
  bool loaded = ::GetModuleHandleW(lpFileName); // this is the first load
  HMODULE ret = ::LoadLibraryExW(lpFileName, hFile, dwFlags);
  if (ret && !loaded)
    overrideModuleFunctions(ret);
  return ret;
}

LPVOID WINAPI Hijack::newGetProcAddress(HMODULE hModule, LPCSTR lpProcName)
{
  if (LPVOID ret = getOverridingFunctionAddress(hModule, lpProcName))
    return ret;
  return ::GetProcAddress(hModule, lpProcName);
}

// EOF

/*
// Strings

// Hijacking MultiByteToWideChar etc does not work
int WINAPI Hijack::newMultiByteToWideChar(UINT CodePage, DWORD dwFlags, LPCSTR lpMultiByteStr, int cbMultiByte, LPWSTR lpWideCharStr, int cchWideChar)
{
  //CodePage = 936;
  return ::MultiByteToWideChar(CodePage, dwFlags, lpMultiByteStr, cbMultiByte, lpWideCharStr, cchWideChar);
}

int WINAPI Hijack::newWideCharToMultiByte(UINT CodePage, DWORD dwFlags, LPCWSTR lpWideCharStr, int cchWideChar, LPSTR lpMultiByteStr, int cbMultiByte, LPCSTR lpDefaultChar, LPBOOL lpUsedDefaultChar)
{
  //CodePage = 936;
  return ::WideCharToMultiByte(CodePage, dwFlags, lpWideCharStr, cchWideChar, lpMultiByteStr, cbMultiByte, lpDefaultChar, lpUsedDefaultChar);
}

#ifdef WITH_LIB_WINHOOK
# include "winhook/funchook.h"

namespace { // unnamed

wchar_t MODULE_PATH[MAX_PATH]; // dll path

// - Helpers -

inline bool InjectDll(HANDLE hProcess)
{ return WinDbg::injectDllW(MODULE_PATH, 0, hProcess); }

// - Callbacks -

BOOL CALLBACK PostCreateProcessW(
  BOOL exitCode,
  _In_opt_     LPCWSTR lpApplicationName,
  _Inout_opt_  LPWSTR lpCommandLine,
  _In_opt_     LPSECURITY_ATTRIBUTES lpProcessAttributes,
  _In_opt_     LPSECURITY_ATTRIBUTES lpThreadAttributes,
  _In_         BOOL bInheritHandles,
  _In_         DWORD dwCreationFlags,
  _In_opt_     LPVOID lpEnvironment,
  _In_opt_     LPCWSTR lpCurrentDirectory,
  _In_         LPSTARTUPINFOW lpStartupInfo,
  _Out_        LPPROCESS_INFORMATION lpProcessInformation
  )
{
  CC_UNUSED(lpApplicationName);
  CC_UNUSED(lpCommandLine);
  CC_UNUSED(lpProcessAttributes);
  CC_UNUSED(lpThreadAttributes);
  CC_UNUSED(bInheritHandles);
  CC_UNUSED(dwCreationFlags);
  CC_UNUSED(lpEnvironment);
  CC_UNUSED(lpCurrentDirectory);
  CC_UNUSED(lpStartupInfo);
  // Note: exitCode should be 0 when lpProcessInformation is 0, anyways.  It's a required parameter.
  if (exitCode && lpProcessInformation)
    InjectDll(lpProcessInformation->hProcess);
  return exitCode;
}

BOOL CALLBACK PostCreateProcessA(
  BOOL exitCode,
  _In_opt_     LPCSTR lpApplicationName,
  _Inout_opt_  LPSTR lpCommandLine,
  _In_opt_     LPSECURITY_ATTRIBUTES lpProcessAttributes,
  _In_opt_     LPSECURITY_ATTRIBUTES lpThreadAttributes,
  _In_         BOOL bInheritHandles,
  _In_         DWORD dwCreationFlags,
  _In_opt_     LPVOID lpEnvironment,
  _In_opt_     LPCSTR lpCurrentDirectory,
  _In_         LPSTARTUPINFOA lpStartupInfo,
  _Out_        LPPROCESS_INFORMATION lpProcessInformation
  )
{
  CC_UNUSED(lpApplicationName);
  CC_UNUSED(lpCommandLine);
  CC_UNUSED(lpProcessAttributes);
  CC_UNUSED(lpThreadAttributes);
  CC_UNUSED(bInheritHandles);
  CC_UNUSED(dwCreationFlags);
  CC_UNUSED(lpEnvironment);
  CC_UNUSED(lpCurrentDirectory);
  CC_UNUSED(lpStartupInfo);
  // Note: exitCode should be 0 when lpProcessInformation is 0, anyways.  It's a required parameter.
  if (exitCode && lpProcessInformation)
    InjectDll(lpProcessInformation->hProcess);
  return exitCode;
}
} // unnamed namespace
#endif // WITH_LIB_WINHOOK
*/

/*
  DWORD WINAPI ThreadProc(LPVOID params)
  {
    CC_UNUSED(params);
    DWORD pid = ::GetCurrentProcessId();
    DWORD tid = ::GetCurrentThreadId();
    //Buffer buffer = {0,0};
    //buffer.size = 3000;
    //buffer.text = (wchar_t *)malloc(sizeof(wchar_t) * 3000);
    int idle = 0;
    int sleepTime = 500;
    int checkWindowInterval = 500;
    int checkWindowTime = 0;
    int rehookInterval = 10000;
    int rehookTime = 5000;
    int t = GetTickCount();
    while (true) {
      int oldt = t;
      t = GetTickCount();
      int dt = t - oldt;
      if (MainPrivate::globalInstance()->aboutToQuit)
        break;
      //CheckDrawing(t);
      rehookTime -= dt;
      if (rehookTime <= 0) {
        OverrideModules();
        rehookTime = rehookInterval;
      }
      checkWindowTime -= dt;
      if (checkWindowTime <= 0) { // && (settings.injectionFlags & TRANSLATE_MENUS)) {
        checkWindowTime = checkWindowInterval;
        HANDLE h = CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0);
        if (h == INVALID_HANDLE_VALUE)
          break;
        THREADENTRY32 thread;
        thread.dwSize = sizeof(thread);
        int count = 0;
        int windows = 0;
        if (Thread32First(h, &thread)) {
          do {
            if (thread.th32OwnerProcessID != pid || thread.th32ThreadID == tid)
              continue;
            //windows |= TranslateThreadWindows(thread.th32ThreadID, buffer);
            windows |= TranslateThreadWindows(thread.th32ThreadID);
            count++;
          }
          while (Thread32Next(h, &thread));
        }
        CloseHandle(h);
        if (!count) break;
        if (!windows) {
          idle++;
          if (idle >= 40)
            break;
        }
      }
      Sleep(sleepTime);
    }
    // Never seem to end up here, for some reason.
    //free(buffer.text);
    //UninitAtlas();
    return 0;
  }

*/
