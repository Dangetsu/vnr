#include "stdafx.h"
#include "log.h"

// jichi 4/4/2015 Disable logging
//
#if 0

HWND hLogWin, hLogRes;
HANDLE hLogEvent;
int logLine = 0;

void LogStartMsg()
{
  wchar_t lpEztPath[MAX_PATH];
  wchar_t lpExePath[MAX_PATH];

  GetLoadPath(lpEztPath, MAX_PATH);
  GetExecutePath(lpExePath, MAX_PATH);

  WriteLog(NORMAL_LOG, L"──── ━━\n");
  WriteLog(NORMAL_LOG, L"Ehnd :: 엔드 - VER. %s :: COMPILE AT %s, %s\n", WIDEN(EHND_VER), WIDEN(__DATE__), WIDEN(__TIME__));
  WriteLog(NORMAL_LOG, L"──── ━━ Ehnd -- sokcuri.neko.kr --\n");
  WriteLog(NORMAL_LOG, L"\n");
  WriteLog(NORMAL_LOG, L"- 제작자 : %s\n", L"소쿠릿");
  WriteLog(NORMAL_LOG, L"━━━━━━━━━───────────-＊\n");
  WriteLog(NORMAL_LOG, L"EzTransPath : %s\n", lpEztPath);
  WriteLog(NORMAL_LOG, L"ExecutePath : %s\n", lpExePath);
  return;
}

void CheckLogSize()
{
  FILE *fp;

  // 로그 사용안할때 끄기
  if (!pConfig->GetFileLogSwitch()) return;

  wchar_t lpFileName[MAX_PATH];
  if (pConfig->GetFileLogEztLoc())
    GetLoadPath(lpFileName, MAX_PATH);
  else GetExecutePath(lpFileName, MAX_PATH);
  wcscat_s(lpFileName, L"\\ehnd_log.log");

  if (_wfopen_s(&fp, lpFileName, L"a+t,ccs=UTF-8")) return;

  //fpos = ftell(fp);
  fseek(fp, 0, SEEK_END);
  int fsize = ftell(fp);
  int cf_size = pConfig->GetFileLogSize();

  if (cf_size != 0 && cf_size * 1024 < fsize)
  {
    fclose(fp);
    DeleteFile(lpFileName);
  }
  else
    fclose(fp);
}

void CheckConsoleLine()
{
  int cf_line = pConfig->GetConsoleMaxLine();

  if (cf_line != 0 && logLine > cf_line)
  {
    ClearLog();
    logLine = 0;
  }
}

void WriteLog(int LogType, const wchar_t *format, ...)
{
  if (!pConfig->GetLogTime() && LogType == TIME_LOG) return;
  if (!pConfig->GetLogDetail() && LogType == DETAIL_LOG) return;
  if (!pConfig->GetLogSkipLayer() && LogType == SKIPLAYER_LOG) return;
  if (!pConfig->GetLogUserDic() && LogType == USERDIC_LOG) return;

  va_list valist;
  FILE *fp = NULL;
  wchar_t lpBuffer[1024], lpTime[64];
  BOOL IsFileLog = pConfig->GetFileLogSwitch();
  if (IsFileLog)
  {
    wchar_t lpFileName[MAX_PATH];
    if (pConfig->GetFileLogEztLoc())
      GetLoadPath(lpFileName, MAX_PATH);
    else GetExecutePath(lpFileName, MAX_PATH);
    wcscat_s(lpFileName, L"\\ehnd_log.log");

    if (_wfopen_s(&fp, lpFileName, L"a+t,ccs=UTF-8")) return;
    _wstrtime_s(lpTime, 32);

    fwprintf_s(fp, L"%s.%03d | ", lpTime, GetTickCount() % 1000);
  }
  va_start(valist, format);

  _vsnwprintf_s(lpBuffer, _TRUNCATE, format, valist);

  if (wcslen(lpBuffer) > 1000)
    wcscpy_s(lpBuffer + 1000, 1024, L"...\r\n");

  if (IsShownLogWin()) SetLogText(lpBuffer);
  if (IsFileLog) fwprintf_s(fp, lpBuffer);

  va_end(valist);

  if (IsFileLog) fclose(fp);

  logLine++;
}

void WriteTextLog(const wchar_t *format, ...)
{
  va_list valist;
  FILE *fp = NULL;
  wchar_t lpBuffer[1024];

  const char* szFileName = ".\\ehnd_text.log";
  if (fopen_s(&fp, szFileName, "a+t,ccs=UTF-8")) return;
  va_start(valist, format);

  _vsnwprintf_s(lpBuffer, _TRUNCATE, format, valist);

  if (wcslen(lpBuffer) > 1000)
    wcscpy_s(lpBuffer + 1000, 1024, L"...\r\n");

  fwprintf_s(fp, lpBuffer);

  va_end(valist);

  fclose(fp);
}

bool CreateLogWin(HINSTANCE hInst)
{
  LoadLibrary(TEXT("Msftedit.dll"));
  WNDCLASSEX wc = { 0, };
  wc.cbSize = sizeof(WNDCLASSEX);
  wc.hbrBackground = (HBRUSH)GetStockObject(WHITE_BRUSH);
  wc.hCursor = LoadCursor(NULL, IDC_ARROW);
  wc.hIcon = LoadIcon(NULL, IDI_APPLICATION);
  wc.hInstance = hInst;
  wc.lpfnWndProc = LogProc;
  wc.lpszClassName = TEXT("EhndLogWin");
  wc.style = CS_HREDRAW | CS_VREDRAW;

  RegisterClassEx(&wc);
  //if (!) MessageBox(0, L"log reg failed", 0, 0);

  SECURITY_ATTRIBUTES thAttr;
  thAttr.bInheritHandle = false;
  thAttr.lpSecurityDescriptor = NULL;
  thAttr.nLength = sizeof(SECURITY_ATTRIBUTES);

  hLogEvent = CreateEvent(NULL, FALSE, FALSE, NULL);
  if (!hLogEvent)
  {
    WriteLog(ERROR_LOG, L"CreateLogWin : Event Init Error");
    return 0;
  }
  HANDLE hThread = CreateThread(&thAttr, 0, LogThreadMain, NULL, 0, NULL);
  if (hThread == NULL)
  {
    WriteLog(ERROR_LOG, L"CreateLogWin : Log Thread Create Error");
  }

  // 로그 윈도우가 초기화될때까지 기다림
  WaitForSingleObject(hLogEvent, INFINITE);
  return 0;
}

DWORD WINAPI LogThreadMain(LPVOID lpParam)
{
  HINSTANCE hInst = g_hInst;
  wchar_t wszTitle[255];

  wsprintf(wszTitle, L"Ehnd Log Window :: VER. %s (%s, %s)", WIDEN(EHND_VER), WIDEN(__DATE__), WIDEN(__TIME__));

  hLogWin = CreateWindowEx(0, L"EhndLogWin", wszTitle, WS_OVERLAPPEDWINDOW, 64, 64, 640, 480, 0, 0, hInst, 0);
  if (!hLogWin)
  {
    WriteLog(ERROR_LOG, L"LogThreadMain : Log Window Create Failed");
    return 0;
  }

  hLogRes = CreateWindowEx(0, MSFTEDIT_CLASS, L"", WS_VISIBLE | WS_CHILD | WS_VSCROLL | ES_MULTILINE | ES_LEFT | ES_NOHIDESEL | ES_AUTOVSCROLL, 0, 0, 640, 480, hLogWin, NULL, hInst, NULL);
  if (!hLogRes)
  {
    WriteLog(ERROR_LOG, L"LogThreadMain : Log Edit Create Failed");
  }

  CHARFORMAT2 cf;
  cf.cbSize = sizeof(CHARFORMAT2);
  cf.dwMask = CFM_COLOR | CFM_BACKCOLOR | CFM_EFFECTS2 | CFM_FACE | CFM_SIZE;
  cf.crTextColor = RGB(0, 0, 0);
  cf.crBackColor = RGB(255, 255, 255);
  cf.yHeight = 12 * 20;

  wcscpy_s(cf.szFaceName, L"굴림");
  cf.dwEffects = CFE_BOLD;
  SendMessage(hLogRes, EM_SETCHARFORMAT, SCF_ALL, (LPARAM)&cf);
  SendMessage(hLogRes, EM_REPLACESEL, TRUE, (LPARAM)L"");

  ShowWindow(hLogRes, true);

  MSG msg;
  BOOL bRet;

  // 쓰레드 초기화 완료
  SetEvent(hLogEvent);

  while ((bRet = GetMessage(&msg, NULL, 0, 0)) != 0)
  {
    TranslateMessage(&msg);
    DispatchMessage(&msg);
  }
  return msg.wParam;
}

void SetLogText(LPCWSTR Text)
{
  SetLogText(Text, RGB(0, 0, 0), RGB(255, 255, 255));
}

void SetLogText(LPCWSTR Text, COLORREF crText, COLORREF crBackground)
{
  CHARRANGE cr = { LONG_MAX, LONG_MAX };
  SendMessage(hLogRes, EM_EXSETSEL, 0, (LPARAM)&cr);

  CHARFORMAT2 cf;
  cf.cbSize = sizeof(CHARFORMAT2);
  cf.dwMask = CFM_COLOR | CFM_BACKCOLOR | CFM_EFFECTS2 | CFM_FACE | CFM_SIZE;
  cf.crTextColor = crText;
  cf.crBackColor = crBackground;
  cf.dwEffects = CFE_BOLD;

  int nLogFntSize = pConfig->GetConsoleFontSize();
  cf.yHeight = nLogFntSize * 20;
  wcscpy_s(cf.szFaceName, pConfig->GetConsoleFontName());
  SendMessage(hLogRes, EM_SETCHARFORMAT, SCF_SELECTION, (LPARAM)&cf);

  SendMessage(hLogRes, EM_REPLACESEL, TRUE, (LPARAM)Text);
}
void ClearLog(void)
{
  CHARRANGE cr = { 0, LONG_MAX };
  SendMessage(hLogRes, EM_EXSETSEL, 0, (LPARAM)&cr);
  SendMessage(hLogRes, EM_REPLACESEL, TRUE, NULL);
}

void ShowLogWin(bool bShow)
{
  if (!bShow) ClearLog();
  ShowWindow(hLogWin, bShow);
  ShowWindow(hLogRes, bShow);
}

bool IsShownLogWin(void)
{
  // jichi 4/3/2015: Allow disabling login window
  //return (GetWindowLong(hLogWin, GWL_STYLE) & WS_VISIBLE) ? true : false;
  return hLogWin && (GetWindowLong(hLogWin, GWL_STYLE) & WS_VISIBLE) ? true : false;
}

LRESULT CALLBACK LogProc(HWND hWnd, UINT Message, WPARAM wParam, LPARAM lParam)
{
  switch (Message)
  {
  case WM_SIZE:
    int w, h;
    w = LOWORD(lParam);
    h = HIWORD(lParam);
    MoveWindow(hLogRes, 0, 0, w, h, true);
    break;
  case WM_CLOSE:
    ShowLogWin(false);
    return 0;
  }
  return DefWindowProc(hWnd, Message, wParam, lParam);
}

#endif // 0
