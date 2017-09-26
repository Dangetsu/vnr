#pragma once

// hookutil_p.h
// 5/29/2015 jichi
#include "winhook/hookdef.h"
#include "winasm/winasmdef.h"

// http://stackoverflow.com/questions/14698350/x86-64-asm-maximum-bytes-for-an-instruction
enum { max_ins_size = 15 }; // maximum individual instruction size
enum { jmp_ins_size = 5 }; // total size of jmp ????

WINHOOK_BEGIN_NAMESPACE

namespace detail {

/**
 *  @param  data  code data
 *  @param  address  the absolute address to jump to
 */
inline void set_jmp_ins(byte *data, ulong address)
{
  data[0] = s1_jmp_;
  *(ulong *)(data + 1) = address - ((ulong)data + jmp_ins_size);
}

/**
 *  @param  data  code data
 *  @param  address  the absolute address to jump to
 */
inline void set_call_ins(byte *data, ulong address)
{
  data[0] = s1_call_;
  *(ulong *)(data + 1) = address - ((ulong)data + jmp_ins_size);
}

/**
 *  Fix the jump and all instructionsin code originally at oldaddr to newaddr.
 *  @param  code  code data to modify
 *  @param  codesize  number of bytes in code
 *  @param  oldaddr  old address
 *  @param  newaddr  new address
 */
void move_code(void *code, size_t codesize, ulong oldaddr, ulong newaddr);

} // namespace detail

WINHOOK_END_NAMESPACE

// EOF
