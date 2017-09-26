// engineutil.cc
// 4/26/2014 jichi

#include "config.h"
#include "engine/engineutil.h"
#include "detoursutil/detoursutil.h"
#include "ntinspect/ntinspect.h"
#include "winhook/hookfun.h"
#include "disasm/disasm.h"
#include "winasm/winasmdef.h"
#include "winkey/winkey.h"
//#include "windbg/util.h"
#include <QtCore/QDir>
#include <QtCore/QCoreApplication>
#include <QtCore/QFileInfo>
#include <QtCore/QStringList>
#include <qt_windows.h>
#include <unordered_map>
#include <utility>

namespace { // unnamed

inline QStringList globDir(const QDir &dir, const QString &filter)
{ return dir.entryList(QStringList(filter)); }

inline bool globsDir(const QDir &dir, const QString &filter)
{ return !dir.entryList(QStringList(filter)).isEmpty(); }

inline bool existsPath(const QString &path)
{ return QFileInfo(path).exists(); }

} // unnamed namespace

// - Memory -

bool Engine::isAddressReadable(const ulong *p)
{ return p && !::IsBadReadPtr(p, sizeof(*p)); }

bool Engine::isAddressReadable(const char *p, size_t count)
{ return p && count && !::IsBadReadPtr(p, sizeof(*p) * count); }

bool Engine::isAddressReadable(const wchar_t *p, size_t count)
{ return p && count && !::IsBadReadPtr(p, sizeof(*p) * count); }

bool Engine::isAddressWritable(const ulong *p)
{ return p && !::IsBadWritePtr((LPVOID)p, sizeof(*p)); }

bool Engine::isAddressWritable(const char *p, size_t count)
{ return p && count && !::IsBadWritePtr((LPVOID)p, sizeof(*p) * count); }

bool Engine::isAddressWritable(const wchar_t *p, size_t count)
{ return p && count && !::IsBadWritePtr((LPVOID)p, sizeof(*p) * count); }

// - Keyboards -

bool Engine::isPauseKeyPressed()
{
  return WinKey::isKeyControlPressed()
      || WinKey::isKeyShiftPressed() && !WinKey::isKeyReturnPressed();
}

// - Detours -

Engine::address_type Engine::replaceFunction(address_type old_addr, const_address_type new_addr)
{
#ifdef VNRAGENT_ENABLE_DETOURS
  return detours::replace(old_addr, new_addr);
#endif // VNRAGENT_ENABLE_DETOURS
#ifdef VNRAGENT_ENABLE_MHOOK
  DWORD addr = old_addr;
  return Mhook_SetHook(&addr, new_addr) ? addr : 0;
#endif // VNRAGENT_ENABLE_MHOOK
  // Use my own function hook instead, which might not be thread-safe
  //WinDbg::ThreadsSuspender suspendedThreads; // lock all threads to prevent crashing
  return (address_type)winhook::replace_fun((DWORD)old_addr, (DWORD)new_addr);
}

// Not used
//Engine::address_type Engine::restoreFunction(address_type restore_addr, const_address_type old_addr)
//{
//#ifdef VNRAGENT_ENABLE_DETOURS
//  WinDbg::ThreadsSuspender suspendedThreads; // lock all threads to prevent crashing
//  return detours::restore(restore_addr, old_addr);
//#endif // VNRAGENT_ENABLE_DETOURS
//}

// - File -

QStringList Engine::glob(const QString &relpath)
{
  QString path = QCoreApplication::applicationDirPath();
  int i = relpath.lastIndexOf('/');
  if (i != -1) {
    QDir dir = path + "/" + relpath.left(i);
    return dir.exists() ? ::globDir(dir, relpath.mid(i+1)) : QStringList();
  } else {
    QDir dir = path;
    return ::globDir(dir, relpath);
  }
}

bool Engine::globs(const QString &relpath)
{
  QString path = QCoreApplication::applicationDirPath();
  int i = relpath.lastIndexOf('/');
  if (i != -1) {
    QDir dir = path + "/" + relpath.left(i);
    return dir.exists() && ::globsDir(dir, relpath.mid(i+1));
  } else {
    QDir dir = path;
    return ::globsDir(dir, relpath);
  }
}

//bool Engine::globs(const QStringList &nameFilters)
//{
//  QDir dir = QCoreApplication::applicationDirPath();
//  foreach (const QString &filter, nameFilters)
//    if (!::globsDir(dir, filter))
//      return false;
//  return true;
//}

//bool Engine::globs(const QString &relPath, const QStringList &nameFilters)
//{
//  QDir dir = QCoreApplication::applicationDirPath() + "/" + relPath;
//  if (!dir.exists())
//    return false;
//  foreach (const QString &filter, nameFilters)
//    if (!::globsDir(dir, filter))
//      return false;
//  return true;
//}

bool Engine::exists(const QString &relPath)
{
  QString path = QCoreApplication::applicationDirPath() + "/" + relPath;
  return ::existsPath(path);
}

//bool Engine::exists(const QStringList &relPaths)
//{
//  QString base = QCoreApplication::applicationDirPath();
//  foreach (const QString &path, relPaths)
//    if (!::existsPath(base + "/" + path))
//      return false;
//  return true;
//}

bool Engine::matchFiles(const QString &pattern)
{
  if (pattern.isEmpty())
    return false;

  if (pattern[0].unicode() == '!' && pattern.size() > 1)
    return !matchFiles(pattern.mid(1));

  if (pattern.contains('*'))
    return globs(pattern);

  return exists(pattern);
}

// - Process and threads -

QString Engine::getProcessName()
{
  static QString ret;
  if (ret.isEmpty()) {
    wchar_t path[MAX_PATH];
    ::GetModuleFileNameW(nullptr, path, MAX_PATH);
    ret = QString::fromWCharArray(path);
  }
  return ret;
}

QString Engine::getNormalizedProcessName()
{
  static QString ret;
  if (ret.isEmpty()) {
    QString path = QCoreApplication::applicationFilePath();
    ret = QFileInfo(path).fileName().toLower();
  }
  return ret;
}

//bool Engine::getMemoryRange(const char *moduleName, unsigned long *startAddress, unsigned long *stopAddress)
//{
//  std::wstring ws = moduleName;
//  return Engine::getMemoryRange(ws.c_str(), startAddress, stopAddress);
//}

bool Engine::getModuleMemoryRange(const wchar_t *moduleName, unsigned long *startAddress, unsigned long *stopAddress)
{
  static std::unordered_map<const wchar_t *, std::pair<DWORD, DWORD> > cache;
  auto p = cache.find(moduleName);
  if (p != cache.end()) {
    auto pair = p->second;
    if (startAddress)
      *startAddress = pair.first;
    if (stopAddress)
      *stopAddress = pair.first;
    return true;
  }

  DWORD start,
        stop;

  wchar_t processName[MAX_PATH]; // cached
  if (!moduleName) {
    if (!NtInspect::getProcessName(processName, MAX_PATH)) // Initialize process name
      return false;
    moduleName = processName;
  }
  if (!NtInspect::getModuleMemoryRange(moduleName, &start, &stop))
    return false;
  cache[moduleName] = std::make_pair(start, stop);
  if (startAddress)
    *startAddress = start;
  if (stopAddress)
    *stopAddress = stop;
  return true;
}

ulong Engine::getModuleFunction(const char *moduleName, const char *funcName)
{
  if (HMODULE h = ::GetModuleHandleA(moduleName)) {
    DWORD ret = (DWORD)::GetProcAddress(h, funcName);
    ::CloseHandle(h);
    return ret;
  }
  return 0;
}

ulong Engine::findNearCall(ulong start, ulong stop)
{
  ulong addr = start,
        size = ::disasm((LPCVOID)addr);
  while (size) {
    enum { call_size = 5 }; //  size of near call instruction is 5
    if (size == call_size && *(BYTE *)addr == s1_call_)
      return addr;
    addr += size;
    if (stop && stop < addr + call_size)
      return 0;
    size = ::disasm((LPCVOID)addr);
  }
  return 0;
};

size_t Engine::countZero(const char *s, size_t limit)
{
  size_t count = 0;
  for (auto p = s; !*p && count < limit; p++, count++);
  return count == limit ? 0 : count;
}

// - Text -

static bool containsNamePunct_(const char *text)
{
  static const char *puncts[] = {
    "\x81\x41" /* 、 */
    , "\x81\x43" /* ， */
    , "\x81\x42" /* 。 */
    //, "\x81\x48" /* ？ */
    , "\x81\x49" /* ！ */
    , "\x81\x63" /* … */
    , "\x81\x64" /* ‥ */

    //, "\x81\x79" /* 【 */
    //, "\x81\x7a" /* 】 */
    , "\x81\x75" /* 「 */
    , "\x81\x76" /* 」 */
    , "\x81\x77" /* 『 */
    , "\x81\x78" /* 』 */
    //, "\x81\x69" /* （ */
    //, "\x81\x6a" /* ） */
    //, "\x81\x6f" /* ｛ */
    //, "\x81\x70" /* ｝ */
    //, "\x81\x71" /* 〈 */
    //, "\x81\x72" /* 〉 */
    , "\x81\x6d" /* ［ */
    , "\x81\x6e" /* ］ */
    //, "\x81\x83", /* ＜ */
    //, "\x81\x84", /* ＞ */
    , "\x81\x65" /* ‘ */
    , "\x81\x66" /* ’ */
    , "\x81\x67" /* “ */
    , "\x81\x68" /* ” */
  };
  for (size_t i = 0; i < sizeof(puncts)/sizeof(*puncts); i++)
    if (::strstr(text, puncts[i]))
      return true;

  if (::strstr(text, "\x81\x48") /* ？ */
      && !::strstr(text, "\x81\x48\x81\x48\x81\x48")) /* ？？？ */
    return true;
  return false;
}
bool Engine::guessIsNameText(const char *text, size_t size)
{
  enum { MaximumNameSize = 0x10 };
  if (!size)
    size = ::strlen(text);
  return size < MaximumNameSize && !containsNamePunct_(text);
}

// EOF
