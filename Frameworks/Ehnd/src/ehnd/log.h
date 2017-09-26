#pragma once
#include <Richedit.h>

// jichi 4/4/2015 Disable logging

inline void WriteLog(int LogType, const wchar_t *format, ...) {}
inline void WriteTextLog(const wchar_t* format, ...) {}

inline void LogStartMsg() {}
inline void CheckLogSize() {}
inline void CheckConsoleLine() {}

inline bool CreateLogWin(HINSTANCE) {}
inline void SetLogText(LPCWSTR) {}
inline void SetLogText(LPCWSTR, COLORREF, COLORREF) {}
inline void ClearLog(void) {}
inline void ShowLogWin(bool bShow) {}
inline bool IsShownLogWin() {}
inline DWORD WINAPI LogThreadMain(LPVOID lpParam) {}
inline LRESULT CALLBACK LogProc(HWND, UINT, WPARAM, LPARAM) {}
//extern HWND hLogRes, hLogWin;
//extern int logLine;
