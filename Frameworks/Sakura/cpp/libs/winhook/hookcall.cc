// hookcall.cc
// 5/31/2015 jichi
#include "winhook/hookcall.h"
#include "winhook/hookutil.h"
#include "winhook/hookutil_p.h"
#include "disasm/disasm.h"
#include "winasm/winasmdef.h"
#include <windows.h>

WINHOOK_BEGIN_NAMESPACE

ulong replace_call(ulong addr, ulong val)
{
  DWORD ret;
  switch (::disasm((LPCVOID)addr)) {
  case 5:  // near call / short jmp: relative address
    ret = *(DWORD *)(addr + 1) + (addr + 5);
    val -= addr + 5;
    return csmemcpy((LPVOID)(addr + 1), &val, sizeof(val)) ? ret : 0;
  case 6:  // far car / long jmp: absolute address
    ret = *(DWORD *)(addr + 2);
    return csmemcpy((LPVOID)(addr + 2), &val, sizeof(val)) ? ret : 0;
  default: return 0;
  }
}

ulong replace_near_call(ulong addr, ulong val)
{
  DWORD ret;
  switch (::disasm((LPCVOID)addr)) {
  case 5:  // near call / short jmp: relative address
    ret = *(DWORD *)(addr + 1) + (addr + 5);
    val -= addr + 5;
    return csmemcpy((LPVOID)(addr + 1), &val, sizeof(val)) ? ret : 0;
  case 6:  // far car / long jmp: absolute address
    {
      ret = *(DWORD *)(addr + 2);
      BYTE data[6];
      data[0] = s1_call_;
      data[5] = s1_nop;
      *(DWORD *)(data + 1) = val - (addr + 5);
      return csmemcpy((LPVOID)addr, data, sizeof(data)) ? ret : 0;
    }
  default: return 0;
  }
}

WINHOOK_END_NAMESPACE

// EOF
