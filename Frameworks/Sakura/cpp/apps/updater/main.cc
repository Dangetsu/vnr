// main.cc
// 10/6/2012 jichi
#include "ccutil/ccmacro.h"
#include <windows.h>
#include <string>
#include <memory>

#include "config.h"
#ifndef SCRIPT_PATH
# error "script path not defined"
#endif

//#define DEBUG "main"
//#include "qxkit/qxdebug.h"
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
  //wsDir += L"\\" CWD;
  ::SetCurrentDirectory(wsDir.c_str());

  //std::wstring wsApp = wsDir + L"\\" PLAYER_PATH;
  //std::wstring wsAppPath = dirname(wsApp);

  // $widir/system32
  if (CC_UNLIKELY(!GetSystemDirectoryW(wszBuffer, BUFFER_SIZE)))
    return -1;

  std::wstring wsApp = wszBuffer;
  wsApp += L"\\cmd.exe";

  // See: http://msdn.microsoft.com/en-us/library/windows/desktop/cc144102(v=vs.85).aspx
  //::SetFileAttributesW(wsDir.c_str(), FILE_ATTRIBUTE_READONLY);

  DOUT(QString::fromStdWString(app));

  STARTUPINFOW siStartupInfo;
  ::memset(&siStartupInfo, 0, sizeof(siStartupInfo));
  siStartupInfo.cb = sizeof(siStartupInfo);

  PROCESS_INFORMATION piProcessInfo;
  ::memset(&piProcessInfo, 0, sizeof(piProcessInfo));

  LPVOID lpEnvironment = nullptr;

  std::wstring wsCmdLine =
      L"\"" + wsApp + L"\"" // cmd.exe
      L" /c "               // /c
      L"\"" SCRIPT_PATH L"\""; // *.cmd

  // See: http://codingmisadventures.wordpress.com/2009/03/10/retrieving-command-line-parameters-from-winmain-in-win32/
  if (lpCmdLine &&
      ::MultiByteToWideChar(CP_ACP, 0, lpCmdLine, -1, wszBuffer, BUFFER_SIZE) &&
      wszBuffer[0]) {
    if (wszBuffer[0] != L' ')
      wsCmdLine += L" ";
    wsCmdLine += wszBuffer;
  }
  ::memcpy(wszBuffer, wsCmdLine.c_str(), (wsCmdLine.size() + 1) * sizeof(wchar_t));
  LPWSTR wszCmdLine = wszBuffer;

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
    wszCmdLine,         // app args
    0, 0,               // security attributes
    FALSE,              // inherited
    CREATE_DEFAULT_ERROR_MODE, // creation flags
    lpEnvironment,
    wsDir.c_str(),
    &siStartupInfo,
    &piProcessInfo
  );

  return bResult ? 0 : -1;
}

// EOF
