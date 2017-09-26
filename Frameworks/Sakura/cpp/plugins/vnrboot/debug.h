#pragma once

// debug.h
// 5/15/2014 jichi

#include <windows.h>

inline void dmsg(const char *message)
{ ::MessageBoxA(nullptr, message, "VNR Message", MB_OK); }

inline void dmsg(char *message)
{ ::MessageBoxA(nullptr, message, "VNR Message", MB_OK); }

inline void dmsg(const wchar_t *message)
{ ::MessageBoxW(nullptr, message, L"VNR Message", MB_OK); }

inline void dmsg(wchar_t *message)
{ ::MessageBoxW(nullptr, message, L"VNR Message", MB_OK); }

#define DMSG(...) dmsg(__VA_ARGS__)
//#define DLOG(...) dlog(__VA_ARGS__)

// EOF
