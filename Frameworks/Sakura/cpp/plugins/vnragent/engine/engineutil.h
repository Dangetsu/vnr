#pragma once

// engineutil.h
// 4/20/2014 jichi

#include "memdbg/memsearch.h"
#include "cpputil/cppcstring.h"
#include <QtCore/QString>

enum : quint8 { XX = MemDbg::WidecardByte }; // 0x11
#define XX2 XX,XX       // WORD
#define XX4 XX2,XX2     // DWORD
#define XX8 XX4,XX4     // QWORD

namespace Engine {

// Detours
typedef void *address_type;
typedef const void *const_address_type;

///  Replace the instruction at the old_addr with jmp to new_addr. Return the address to the replaced code.
address_type replaceFunction(address_type old_addr, const_address_type new_addr);
//address_type restoreFunction(address_type restore_addr, const_address_type old_addr);

// Ignore type checking
template<typename Ret, typename Arg1, typename Arg2>
inline Ret replaceFunction(Arg1 arg1, Arg2 arg2)
{ return (Ret)replaceFunction((address_type)arg1, (const_address_type)arg2); }

// Not used
//template<typename Ret, typename Arg1, typename Arg2>
//inline Ret restoreFunction(Arg1 arg1, Arg2 arg2)
//{ return (Ret)restoreFunction((address_type)arg1, (const_address_type)arg2); }

// String
enum { MaxTextSize = 1500 };
template <typename charT>
inline size_t getTextLength(const charT *s, size_t capacity = MaxTextSize)
{ return cpp_basic_strnlen(s, capacity); }

// Return if the text might be a name
bool guessIsNameText(const char *text, size_t size = 0);

// File system
bool globs(const QString &relpath);
bool exists(const QString &relPath);

bool matchFiles(const QString &pattern);

QStringList glob(const QString &nameFilter);

// Keybord shortcuts
bool isPauseKeyPressed();

// Thread and process

QString getProcessName();
QString getNormalizedProcessName();

bool getModuleMemoryRange(const wchar_t *moduleName, unsigned long *startAddress, unsigned long *stopAddress);

inline bool getProcessMemoryRange(unsigned long *startAddress, unsigned long *stopAddress)
{ return getModuleMemoryRange(nullptr, startAddress, stopAddress); }

// This function might be cached and hence not thread-safe
ulong getModuleFunction(const char *moduleName, const char *funcName);

bool isAddressReadable(const ulong *p);
bool isAddressReadable(const char *p, size_t count = 1);
bool isAddressReadable(const wchar_t *p, size_t count = 1);
bool isAddressWritable(const ulong *p);
bool isAddressWritable(const char *p, size_t count = 1);
bool isAddressWritable(const wchar_t *p, size_t count = 1);

inline bool isAddressReadable(const void *addr) { return isAddressReadable((const ulong *)addr); }
inline bool isAddressReadable(ulong addr) { return isAddressReadable((const void *)addr); }
inline bool isAddressWritable(const void *addr) { return isAddressWritable((const ulong *)addr); }
inline bool isAddressWritable(ulong addr) { return isAddressWritable((const void *)addr); }

// Return numbers of continuous zeros. *end must be '\0'
size_t countZero(const char *end, size_t limit = MaxTextSize);

// find the near call instruction address in between two addresses
ulong findNearCall(ulong startAddress, ulong stopAddress = 0); // 0 stop address means no limit

} // namespace Engine

// EOF
