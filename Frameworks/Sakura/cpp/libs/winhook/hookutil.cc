// hookutil.cc
// 5/29/2015 jichi
#include "winhook/hookutil.h"
#include "disasm/disasm.h"
#include "winasm/winasmdef.h"
#include <windows.h>
#include <cstdint>

WINHOOK_BEGIN_NAMESPACE

void *memcpy_(void *dst, const void *src, size_t num)
{
#ifdef WINHOOK_NO_LIBC
  auto d = static_cast<uint8_t *>(dst);
  auto s = static_cast<const uint8_t *>(src);
  for (size_t i = 0; i < num; i++)
    d[i] = s[i];
  return dst;
#else
  return ::memcpy(dst, src, num);
#endif // WINHOOK_NO_LIBC
}

void *memset_(void *ptr, int value, size_t num)
{
#ifdef WINHOOK_NO_LIBC
  auto p = static_cast<uint8_t *>(ptr);
  for (size_t i = 0; i < num; i++)
    p[i] = value;
  return ptr;
#else
  return ::memset(ptr, value, num);
#endif // WINHOOK_NO_LIBC
}

bool csmemcpy(void *dst, const void *src, size_t size)
{
  //return memcpy_(dst, src, size);

  DWORD oldProtect;
  if (!::VirtualProtect(dst, size, PAGE_EXECUTE_READWRITE, &oldProtect))
    return false;
  //HANDLE hProc = OpenProcess(PROCESS_VM_OPERATION|PROCESS_VM_READ|PROCESS_VM_WRITE, FALSE, ::GetCurrentProcessId());
  //VirtualProtectEx(hProc, dst, size, PAGE_EXECUTE_READWRITE, &oldProtect);

  memcpy_(dst, src, size);

  DWORD newProtect;
  ::VirtualProtect(dst, size, oldProtect, &newProtect); // the error code is not checked for this function
  //hProc = OpenProcess(PROCESS_VM_OPERATION|PROCESS_VM_READ|PROCESS_VM_WRITE, FALSE, ::GetCurrentProcessId());
  //VirtualProtectEx(hProc, dst, size, oldProtect, &newProtect);

  return true;
}

bool csmemset(void *dst, byte value, size_t size)
{
  //return memset_(dst, value, size);

  DWORD oldProtect;
  if (!::VirtualProtect(dst, size, PAGE_EXECUTE_READWRITE, &oldProtect))
    return false;
  //HANDLE hProc = OpenProcess(PROCESS_VM_OPERATION|PROCESS_VM_READ|PROCESS_VM_WRITE, FALSE, ::GetCurrentProcessId());
  //VirtualProtectEx(hProc, dst, size, PAGE_EXECUTE_READWRITE, &oldProtect);

  memset_(dst, value, size);

  DWORD newProtect;
  ::VirtualProtect(dst, size, oldProtect, &newProtect); // the error code is not checked for this function
  //hProc = OpenProcess(PROCESS_VM_OPERATION|PROCESS_VM_READ|PROCESS_VM_WRITE, FALSE, ::GetCurrentProcessId());
  //VirtualProtectEx(hProc, dst, size, oldProtect, &newProtect);

  return true;
}

bool remove_inst(ulong addr)
{
  auto p = (LPVOID)addr;
  size_t size = ::disasm(p);
  return size && csmemset(p, s1_nop, size);
}

WINHOOK_END_NAMESPACE

// EOF
