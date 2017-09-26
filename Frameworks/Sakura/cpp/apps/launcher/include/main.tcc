// main.tcc
// 9/3/2011 jichi
#include "ccutil/ccmacro.h"
#include <windows.h>
#include <string>
#include <memory>

#if !defined(APP_PREFIX) || !defined(APP_EXE)
# error "app path not defined"
#endif

//#define DEBUG "main"
//#include "sakurakit/skdebug.h"
//#ifdef DEBUG
//  #include <QtCore>
//  #define DOUT(_msg)    qDebug() << "main:" << _msg
//#else
  #define DOUT(_dummy)  (void)0
//#endif // DEBUG

// - Launcher -

namespace { // unnamed

inline std::string dirname(const std::string &path)
{ return path.substr(0, path.find_last_of('\\')); }

inline std::wstring dirname(const std::wstring &path)
{ return path.substr(0, path.find_last_of(L'\\')); }

} // unnamed namespace


// - Main -

int CALLBACK WinMain(_In_ HINSTANCE hInstance, _In_ HINSTANCE hPrevInstance, _In_ LPSTR lpCmdLine, _In_ int nCmdShow)
{
  CC_UNUSED(hInstance);
  CC_UNUSED(hPrevInstance);
  CC_UNUSED(nCmdShow);

  enum { BUFFER_SIZE = MAX_PATH * 3 };
  WCHAR wszBuffer[BUFFER_SIZE];
  if (CC_UNLIKELY(::GetModuleFileNameW(0, wszBuffer, BUFFER_SIZE) == BUFFER_SIZE))
    return -1;

  std::wstring wsDir = dirname(wszBuffer);
  std::wstring wsApp = wsDir + L"\\" APP_PREFIX APP_EXE;
  std::wstring wsAppPath = dirname(wsApp);

  // See: http://msdn.microsoft.com/en-us/library/windows/desktop/cc144102(v=vs.85).aspx
  ::SetFileAttributesW(wsDir.c_str(), FILE_ATTRIBUTE_READONLY);

  std::wstring wsLibraryDir = wsDir + L"\\Library";
  ::SetFileAttributesW(wsLibraryDir.c_str(), FILE_ATTRIBUTE_READONLY);

  DOUT(QString::fromStdWString(app));

  STARTUPINFOW siStartupInfo = {};
  //::memset(&siStartupInfo, 0, sizeof(siStartupInfo));
  siStartupInfo.cb = sizeof(siStartupInfo);

  PROCESS_INFORMATION piProcessInfo = {};
  //::memset(&piProcessInfo, 0, sizeof(piProcessInfo));

  LPVOID lpEnvironment = nullptr; // TODO: Use AppLocale to load updater?

  LPWSTR lpwCmdLine = nullptr;
  if (lpCmdLine && ::MultiByteToWideChar(CP_ACP, 0, lpCmdLine, -1, wszBuffer, BUFFER_SIZE))
    lpwCmdLine = wszBuffer;

  // See: http://msdn.microsoft.com/en-us/library/windows/desktop/ms682425(v=vs.85).aspx
  //
  // BOOL WINAPI CreateProcess(
  //   _In_opt_     LPCTSTR lpApplicationName,
  //   _Inout_opt_  LPTSTR lpCommandLine,
  //   _In_opt_     LPSECURITY_ATTRIBUTES lpProcessAttributes,
  //   _In_opt_     LPSECURITY_ATTRIBUTES lpThreadAttributes,
  //   _In_         BOOL bInheritHandles,
  //   _In_         DWORD dwCreationFlags,
  //   _In_opt_     LPVOID lpEnvironment,
  //   _In_opt_     LPCTSTR lpCurrentDirectory,
  //   _In_         LPSTARTUPINFO lpStartupInfo,
  //   _Out_        LPPROCESS_INFORMATION lpProcessInformation
  // );
  //
  BOOL bResult = ::CreateProcessW(
    wsApp.c_str(),      // app path
    lpwCmdLine,         // app param
    0, 0,               // security attributes
    FALSE,              // inherited
    CREATE_DEFAULT_ERROR_MODE, // creation flags
    lpEnvironment,
    wsAppPath.c_str(),
    &siStartupInfo,
    &piProcessInfo
  );

  return bResult ? 0 : -1;
}

// EOF
