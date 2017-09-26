#pragma once

// winasmutil.h
// 6/2/2015 jichi
#include "winasm/winasm.h"

WINASM_BEGIN_NAMESPACE

/**
 *  @param  inst  address of the short jmp/near call instruction
 *  @return  absolute target address to jump to/call
 */
// FIXME: I didn't check short jump here
inline ulong get_jmp_absaddr(ulong inst)
{ return inst + 5 + *(ulong *)(inst + 1); }

WINASM_END_NAMESPACE
