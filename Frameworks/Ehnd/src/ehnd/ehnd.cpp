// ehnd.cpp : DLL 응용 프로그램을 위해 내보낸 함수를 정의합니다.
//

#include "stdafx.h"
#include "ehnd.h"
#include "config.h"

FARPROC apfnEzt[100];
FARPROC apfnMsv[100];

bool EhndInit(void)
{
    // Prevent duplicate initialization
  if (initOnce) return false;
  else initOnce = true;

  // 설정 로드
  //pConfig->LoadConfig();

  // jichi 4/4/2015: Disable logging
  // 기존 로그 삭제
  //if (pConfig->GetFileLogStartupClear())
  //{
  //  wchar_t lpFileName[MAX_PATH];
  //  if (pConfig->GetFileLogEztLoc())
  //    GetLoadPath(lpFileName, MAX_PATH);
  //  else GetExecutePath(lpFileName, MAX_PATH);
  //  wcscat_s(lpFileName, L"\\ehnd_log.log");
  //  DeleteFile(lpFileName);
  //}

  // jichi 4/3/2015: Disable log window
  //CreateLogWin(g_hInst);
  //ShowLogWin(pConfig->GetConsoleSwitch());
  //LogStartMsg();

  GetRealWC2MB();
  GetRealMB2WC();

  if (!hook()) return false;
  if (!hook_userdict()) return false;
  if (!hook_userdict2()) return false;
  if (!hook_getwordinfo()) return false;

  WriteLog(NORMAL_LOG, L"HookUserDict : 사용자사전 알고리즘 최적화.\n");

  // 엔드 임시파일 삭제
  pFilter->ehnddic_cleanup();

  pFilter->load();
  return true;
}

// 이지트랜스 API
__declspec(naked) void J2K_Initialize(void)
{
  __asm JMP apfnEzt[4 * 0];
}
void __stdcall J2K_InitializeEx(int data0, LPSTR key)
{
  SetLogText(L"J2K_InitializeEx : 이지트랜스 초기화\n");

  EhndInit();
  __asm
  {
    PUSH DWORD PTR DS : [key]
    PUSH data0
    CALL apfnEzt[4 * 1]
  }
}
__declspec(naked) void J2K_FreeMem(void)
{
  __asm JMP apfnEzt[4 * 2];
}
__declspec(naked) void J2K_GetPriorDict(void)
{
  __asm JMP apfnEzt[4 * 3];
}
__declspec(naked) void J2K_GetProperty(void)
{
  __asm JMP apfnEzt[4 * 4];
}
void __stdcall J2K_ReloadUserDict(void)
{
  pFilter->load_dic();
  __asm CALL apfnEzt[4 * 5];
  return;
}
__declspec(naked) void J2K_SetDelJPN(void)
{
  __asm JMP apfnEzt[4 * 6];
}
__declspec(naked) void J2K_SetField(void)
{
  __asm JMP apfnEzt[4 * 7];
}
__declspec(naked) void J2K_SetHnj2han(void)
{
  __asm JMP apfnEzt[4 * 8];
}
__declspec(naked) void J2K_SetJWin(void)
{
  __asm JMP apfnEzt[4 * 9];
}
__declspec(naked) void J2K_SetPriorDict(void)
{
  __asm JMP apfnEzt[4 * 10];
}
__declspec(naked) void J2K_SetProperty(void)
{
  __asm JMP apfnEzt[4 * 11];
}
__declspec(naked) void J2K_StopTranslation(void)
{
  __asm JMP apfnEzt[4 * 12];
}
__declspec(naked) void J2K_Terminate(void)
{
  __asm JMP apfnEzt[4 * 13];
}
__declspec(naked) void J2K_TranslateChat(void)
{
  __asm JMP apfnEzt[4 * 14];
}
__declspec(naked) void J2K_TranslateFM(void)
{
  __asm JMP apfnEzt[4 * 15];
}
__declspec(naked) void J2K_TranslateMM(void)
{
  __asm JMP apfnEzt[4 * 16];
}
__declspec(naked) void J2K_TranslateMMEx(void)
{
  __asm JMP apfnEzt[4 * 17];
}
__declspec(naked) void *msvcrt_free(void *_Memory)
{
  __asm JMP apfnMsv[4 * 0];
}
__declspec(naked) void *msvcrt_malloc(size_t _Size)
{
  __asm JMP apfnMsv[4 * 1];
}
__declspec(naked) void *msvcrt_fopen(char *path, char *mode)
{
  __asm JMP apfnMsv[4 * 2];
}

void *__stdcall J2K_TranslateMMNTW(int data0, LPCWSTR szIn)
{
  DWORD dwStart, dwEnd;
  LPWSTR szOut;
  wstring wsText, wsOriginal, wsLog;
  int i_len;
  LPWSTR lpKOR;
  LPSTR szJPN, szKOR;

  wsOriginal = szIn;
  wsText = szIn;

  // 로그 크기 체크
  CheckLogSize();

  // 콘솔 라인 체크
  CheckConsoleLine();

  wsLog = replace_all(wsText, L"%", L"%%");
  if (wsLog.length()) WriteLog(NORMAL_LOG, L"[REQUEST] %s\n\n", wsLog.c_str());

  // 넘어온 문자열의 길이가 0이거나 명령어일때 번역 프로세스 스킵
  if (wcslen(szIn) && !pFilter->cmd(wsText))
  {
    pFilter->pre(wsText);

    wsLog = replace_all(wsText, L"%", L"%%");
    WriteLog(NORMAL_LOG, L"[PRE] %s\n\n", wsLog.c_str());

    i_len = _WideCharToMultiByte(932, 0, wsText.c_str(), -1, NULL, NULL, NULL, NULL);
    szJPN = (LPSTR)msvcrt_malloc((i_len + 1) * 3);
    if (szJPN == NULL)
    {
      WriteLog(ERROR_LOG, L"J2K_TranslateMMNT : Memory Allocation Error.\n");
      return 0;
    }
    _WideCharToMultiByte(932, 0, wsText.c_str(), -1, szJPN, i_len, NULL, NULL);

    if (!pConfig->GetUserDicSwitch()) WriteLog(NORMAL_LOG, L"UserDic : 사용자 사전이 꺼져 있습니다.\n");

    dwStart = GetTickCount();

    __asm
    {
      PUSH DWORD PTR DS : [szJPN]
      PUSH data0
      CALL apfnEzt[4 * 18]
      MOV DWORD PTR DS : [szKOR], EAX
    }

    dwEnd = GetTickCount();

    WriteLog(TIME_LOG, L"J2K_TranslateMMNT : --- Elasped Time : %dms ---\n", dwEnd - dwStart);

    msvcrt_free(szJPN);

    i_len = _MultiByteToWideChar(949, MB_PRECOMPOSED, szKOR, -1, NULL, NULL);
    lpKOR = (LPWSTR)msvcrt_malloc((i_len + 1) * 3);
    if (lpKOR == NULL)
    {
      WriteLog(ERROR_LOG, L"J2K_TranslateMMNT : Memory Allocation Error.\n");
      return 0;
    }
    _MultiByteToWideChar(949, 0, szKOR, -1, lpKOR, i_len);

    wsText = lpKOR;
    msvcrt_free(szKOR);
    msvcrt_free(lpKOR);

    wsLog = replace_all(wsText, L"%", L"%%");
    WriteLog(NORMAL_LOG, L"[TRANS] %s\n\n", wsLog.c_str());

    pFilter->post(wsText);

    wsLog = replace_all(wsText, L"%", L"%%");
    WriteLog(NORMAL_LOG, L"[POST] %s\n\n", wsLog.c_str());
  }
  else if (wcslen(szIn))
  {
    wsLog = replace_all(wsText, L"%", L"%%");
    WriteLog(NORMAL_LOG, L"[COMMAND] %s\n\n", wsLog.c_str());
  }

  szOut = (LPWSTR)msvcrt_malloc((wsText.length() + 1) * 2);
  if (szOut == NULL)
  {
    WriteLog(ERROR_LOG, L"J2K_TranslateMMNT : Memory Allocation Error.\n");
    return 0;
  }
  wcscpy_s(szOut, (wsText.length() + 1) * 2, wsText.c_str());
  return (void *)szOut;
}

void *__stdcall J2K_TranslateMMNT(int data0, LPCSTR szIn)
{
  LPSTR szOut;
  wstring wsText, wsOriginal, wsLog;
  int i_len;
  LPWSTR lpJPN, lpKOR;

  lpJPN = 0;
  i_len = _MultiByteToWideChar(932, MB_PRECOMPOSED, szIn, -1, NULL, NULL);
  lpJPN = (LPWSTR)msvcrt_malloc((i_len + 1) * 3);
  if (lpJPN == NULL)
  {
    WriteLog(ERROR_LOG, L"J2K_TranslateMMNT : Memory Allocation Error.\n");
    return 0;
  }
  _MultiByteToWideChar(932, 0, szIn, -1, lpJPN, i_len);
  wsText = lpJPN;
  msvcrt_free(lpJPN);

  lpKOR = (LPWSTR)J2K_TranslateMMNTW(data0, wsText.c_str());

  // cp949 내보내기
  i_len = _WideCharToMultiByte(949, 0, lpKOR, -1, NULL, NULL, NULL, NULL);
  szOut = (LPSTR)msvcrt_malloc((i_len + 1) * 3);
  if (szOut == NULL)
  {
    WriteLog(ERROR_LOG, L"J2K_TranslateMMNT : Memory Allocation Error.\n");
    return 0;
  }
  _WideCharToMultiByte(949, 0, lpKOR, -1, szOut, i_len, NULL, NULL);
  msvcrt_free(lpKOR);

  return (void *)szOut;
}
__declspec(naked) void J2K_GetJ2KMainDir(void)
{
  __asm JMP apfnEzt[4 * 19];
}

// jichi: get enclosing directory path for the dll without trailing '\\'
bool GetModuleDirectory(HMODULE h, LPWSTR buf, int size)
{
  GetModuleFileName(h, buf, size);
  if (!buf[0])
    return false;
  int i = wcslen(buf);
  while (i--)
    if (buf[i] == L'\\') {
      buf[i] = 0;
      break;
    }
  return true;
}

// jichi 4/4/2015: Get dll file name without suffix
bool GetModuleBaseName(LPWSTR path, int size)
{
  GetModuleFileName(g_hInst, path, size);
  if (!path[0])
    return false;
  int i = wcslen(path);
  while (i--)
    if (path[i] == L'.') {
      path[i] = 0;
      break;
    }
  return true;
}

// jichi 4/4/2015: Get ehnd dic directory
std::wstring GetEhndDicPath()
{
  WCHAR buf[MAX_PATH];
  GetLoadPath(buf, MAX_PATH);
  std::wstring ret = buf;
  ret.push_back('\\');
  ret.append(pConfig->GetDicPath());
  return ret;
}

wstring replace_all(const wstring &str, const wstring &pattern, const wstring &replace)
{
  wstring result = str;
  wstring::size_type pos = 0, offset = 0;

  while ((pos = result.find(pattern, offset)) != wstring::npos)
  {
    result.replace(result.begin() + pos, result.begin() + pos + pattern.size(), replace);
    offset = pos + replace.size();
  }
  return result;
}
