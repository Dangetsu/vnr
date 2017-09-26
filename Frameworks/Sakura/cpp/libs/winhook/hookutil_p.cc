// hookutil_p.cc
// 5/29/2015 jichi
#include "winhook/hookutil_p.h"
#include "disasm/disasm.h"
#include <windows.h>

WINHOOK_BEGIN_NAMESPACE

void detail::move_code(void *code, size_t codesize, ulong oldaddr, ulong newaddr)
{
  BYTE *begin = (BYTE *)code,
       *end = (BYTE *)code + codesize;
  size_t size = 0;
  for (BYTE *p = begin; p < end; p += size) {
    size = ::disasm(p);
    if (!size || p + size > end) // failed to decode instruction
      return;
    if (size == 5 && (*p == s1_jmp_ || *p == s1_call_))
      *(DWORD *)(p + 1) += oldaddr - newaddr;
  }
}

WINHOOK_END_NAMESPACE

// EOF
