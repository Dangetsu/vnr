#pragma once

// debug.h
// 2/1/2013 jichi

#include <qt_windows.h>

#ifdef QT_CORE_LIB
# include <QtCore/QString>
#endif // QT_CORE_LIB

inline void dmsg(const char *message)
{ ::MessageBoxA(nullptr, message, "VNR Message", MB_OK); }

inline void dmsg(char *message)
{ ::MessageBoxA(nullptr, message, "VNR Message", MB_OK); }

inline void dmsg(const wchar_t *message)
{ ::MessageBoxW(nullptr, message, L"VNR Message", MB_OK); }

inline void dmsg(wchar_t *message)
{ ::MessageBoxW(nullptr, message, L"VNR Message", MB_OK); }

#ifdef QT_CORE_LIB


//inline void dmsg(const ushort *message) { dmsg((LPCWSTR)message); }
//inline void dmsg(ushort *message){ dmsg((LPWSTR)message); }

inline void dmsg(const QString &message) { dmsg(message.utf16()); }
template <typename T> inline void dmsg(T number) { dmsg("0x" + QString::number(number, 16)); }

#endif //QT_CORE_LIB

#define DMSG(...) dmsg(__VA_ARGS__)
//#define DLOG(...) dlog(__VA_ARGS__)

// EOF
