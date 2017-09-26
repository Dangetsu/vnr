#include "stdafx.h"
#include "config.h"

bool config::LoadConfig()
{
  wchar_t INIPath[MAX_PATH], buf[255];
  // jichi 4/4/2015: do not hardcode ehnd.ini file name
  ::GetModuleBaseName(INIPath, MAX_PATH);
  wcscat_s(INIPath, L".ini");

  // jichi 4/4/2015: Get dic path
  ReadINI(L"DIC_PATH", L"CONFIG", buf, INIPath);
  if (buf[0])
    SetDicPath(buf);

  ReadINI(L"PREFILTER_SWITCH", L"CONFIG", buf, (wchar_t*)INIPath);
  if (buf[0] != NULL) (_wcsicmp(buf, L"OFF") != 0) ? SetPreSwitch(true) : SetPreSwitch(false);
  ReadINI(L"POSTFILTER_SWITCH", L"CONFIG", buf, (wchar_t*)INIPath);
  if (buf[0] != NULL) (_wcsicmp(buf, L"OFF") != 0) ? SetPostSwitch(true) : SetPostSwitch(false);
  ReadINI(L"JKDIC_SWITCH", L"CONFIG", buf, (wchar_t*)INIPath);
  if (buf[0] != NULL) (_wcsicmp(buf, L"OFF") != 0) ? SetJKDICSwitch(true) : SetJKDICSwitch(false);
  ReadINI(L"USERDIC_SWITCH", L"CONFIG", buf, (wchar_t*)INIPath);
  if (buf[0] != NULL) (_wcsicmp(buf, L"OFF") != 0) ? SetUserDicSwitch(true) : SetUserDicSwitch(false);
  ReadINI(L"EHNDWATCH_SWITCH", L"CONFIG", buf, (wchar_t*)INIPath);
  if (buf[0] != NULL) (_wcsicmp(buf, L"OFF") != 0) ? SetEhndWatchSwitch(true) : SetEhndWatchSwitch(false);
  ReadINI(L"COMMAND_SWITCH", L"CONFIG", buf, (wchar_t*)INIPath);
  if (buf[0] != NULL) (_wcsicmp(buf, L"OFF") != 0) ? SetCommandSwitch(true) : SetCommandSwitch(false);

  ReadINI(L"LOG_DETAIL", L"CONFIG", buf, (wchar_t*)INIPath);
  if (buf[0] != NULL) (_wcsicmp(buf, L"OFF") != 0) ? SetLogDetail(true) : SetLogDetail(false);
  ReadINI(L"LOG_TIME", L"CONFIG", buf, (wchar_t*)INIPath);
  if (buf[0] != NULL) (_wcsicmp(buf, L"OFF") != 0) ? SetLogTime(true) : SetLogTime(false);
  ReadINI(L"LOG_SKIPLAYER", L"CONFIG", buf, (wchar_t*)INIPath);
  if (buf[0] != NULL) (_wcsicmp(buf, L"OFF") != 0) ? SetLogSkipLayer(true) : SetLogSkipLayer(false);
  ReadINI(L"LOG_USERDIC", L"CONFIG", buf, (wchar_t*)INIPath);
  if (buf[0] != NULL) (_wcsicmp(buf, L"OFF") != 0) ? SetLogUserDic(true) : SetLogUserDic(false);


  ReadINI(L"FILELOG_SWITCH", L"CONFIG", buf, (wchar_t*)INIPath);
  if (buf[0] != NULL) (_wcsicmp(buf, L"OFF") != 0) ? SetFileLogSwitch(true) : SetFileLogSwitch(false);
  ReadINI(L"FILELOG_SIZE", L"CONFIG", buf, (wchar_t*)INIPath);
  if (buf[0] != NULL) SetFileLogSize(_wtoi(buf));
  ReadINI(L"FILELOG_EZTRANS_LOC", L"CONFIG", buf, (wchar_t*)INIPath);
  if (buf[0] != NULL) (_wcsicmp(buf, L"OFF") != 0) ? SetFileLogEztLoc(true) : SetFileLogEztLoc(false);
  ReadINI(L"FILELOG_STARTUP_CLEAR", L"CONFIG", buf, (wchar_t*)INIPath);
  if (buf[0] != NULL) (_wcsicmp(buf, L"OFF") != 0) ? SetFileLogStartupClear(true) : SetFileLogStartupClear(false);

  ReadINI(L"CONSOLE_SWITCH", L"CONFIG", buf, (wchar_t*)INIPath);
  if (buf[0] != NULL) (_wcsicmp(buf, L"OFF") != 0) ? SetConsoleSwitch(true) : SetConsoleSwitch(false);
  ReadINI(L"CONSOLE_MAXLINE", L"CONFIG", buf, (wchar_t*)INIPath);
  if (buf[0] != NULL) SetConsoleMaxLine(_wtoi(buf));
  ReadINI(L"CONSOLE_FONTNAME", L"CONFIG", buf, (wchar_t*)INIPath);
  if (buf[0] != NULL) SetConsoleFontName(buf);
  ReadINI(L"CONSOLE_FONTSIZE", L"CONFIG", buf, (wchar_t*)INIPath);
  if (buf[0] != NULL) SetConsoleFontSize(_wtoi(buf));

  if (!firstInit) WriteLog(NORMAL_LOG, L"LoadConfig : Success.\n");
  else firstInit = false;
  return true;
}

bool config::SaveConfig()
{
  wchar_t INIPath[MAX_PATH], buf[255];

  // jichi 4/4/2015: do not hardcode ehnd.ini file name
  GetModuleBaseName(INIPath, MAX_PATH);
  wcscat_s(INIPath, L".ini");

  // jichi 4/4/2015: Save dic path
  WriteINI(L"DIC_PATH", L"CONFIG", cfg_dic_path, INIPath);

  //wcscpy_s(buf, (GetPreSwitch() ? L"ON" : L"OFF"));
  //WriteINI(L"PREFILTER_SWITCH", L"CONFIG", buf, (wchar_t*)INIPath);
  //wcscpy_s(buf, (GetPostSwitch() ? L"ON" : L"OFF"));
  //WriteINI(L"POSTFILTER_SWITCH", L"CONFIG", buf, (wchar_t*)INIPath);
  //wcscpy_s(buf, (GetJKDICSwitch() ? L"ON" : L"OFF"));
  //WriteINI(L"JKDIC_SWITCH", L"CONFIG", buf, (wchar_t*)INIPath);
  wcscpy_s(buf, (GetCommandSwitch() ? L"ON" : L"OFF"));
  WriteINI(L"COMMAND_SWITCH", L"CONFIG", buf, (wchar_t*)INIPath);

  wcscpy_s(buf, (GetLogDetail() ? L"ON" : L"OFF"));
  WriteINI(L"LOG_DETAIL", L"CONFIG", buf, (wchar_t*)INIPath);
  wcscpy_s(buf, (GetLogTime() ? L"ON" : L"OFF"));
  WriteINI(L"LOG_TIME", L"CONFIG", buf, (wchar_t*)INIPath);
  wcscpy_s(buf, (GetLogSkipLayer() ? L"ON" : L"OFF"));
  WriteINI(L"LOG_SKIPLAYER", L"CONFIG", buf, (wchar_t*)INIPath);
  wcscpy_s(buf, (GetLogUserDic() ? L"ON" : L"OFF"));
  WriteINI(L"LOG_USERDIC", L"CONFIG", buf, (wchar_t*)INIPath);

  wcscpy_s(buf, (GetFileLogSwitch() ? L"ON" : L"OFF"));
  WriteINI(L"FILELOG_SWITCH", L"CONFIG", buf, (wchar_t*)INIPath);
  wsprintf(buf, L"%d", GetFileLogSize());
  WriteINI(L"FILELOG_SIZE", L"CONFIG", buf, (wchar_t*)INIPath);
  wcscpy_s(buf, (GetFileLogEztLoc() ? L"ON" : L"OFF"));
  WriteINI(L"FILELOG_EZTRANS_LOC", L"CONFIG", buf, (wchar_t*)INIPath);
  wcscpy_s(buf, (GetFileLogStartupClear() ? L"ON" : L"OFF"));
  WriteINI(L"FILELOG_STARTUP_CLEAR", L"CONFIG", buf, (wchar_t*)INIPath);

  wcscpy_s(buf, (GetConsoleSwitch() ? L"ON" : L"OFF"));
  WriteINI(L"CONSOLE_SWITCH", L"CONFIG", buf, (wchar_t*)INIPath);
  wsprintf(buf, L"%d", GetConsoleMaxLine());
  WriteINI(L"CONSOLE_MAXLINE", L"CONFIG", buf, (wchar_t*)INIPath);
  wsprintf(buf, L"%s", GetConsoleFontName());
  WriteINI(L"CONSOLE_FONTNAME", L"CONFIG", buf, (wchar_t*)INIPath);
  wsprintf(buf, L"%d", GetConsoleFontSize());
  WriteINI(L"CONSOLE_FONTSIZE", L"CONFIG", buf, (wchar_t*)INIPath);

  WriteLog(NORMAL_LOG, L"SaveConfig : Success.\n");
  return true;
}

bool config::ReadINI(const wchar_t *key, const wchar_t *section, wchar_t *buf, wchar_t *file)
{
  int n = GetPrivateProfileString(section, key, NULL, buf, 255, file);
  if (n == 0)
    return false;
  return true;
}


bool config::WriteINI(const wchar_t *key, const wchar_t *section, wchar_t *buf, wchar_t *file)
{
  int n = WritePrivateProfileString(section, key, buf, file);
  if (n == 0)
    return false;
  return true;
}
