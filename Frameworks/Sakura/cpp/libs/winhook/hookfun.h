#pragma once

// hookfun.h
// 5/29/2015 jichi

#include "winhook/hookdef.h"

WINHOOK_BEGIN_NAMESPACE

// FIXME: move_code not invoked, and hence the first a few instruction of the function cannot be jmp/call
/**
 *  Replace the old function definition with the new one
 *  @param  oldfun  address to insert jump
 *  @param  newfun  the function call to replace
 *  @return  entry point to access the old function or 0 if failed
 */
ulong replace_fun(ulong oldfun, ulong newfun);

/**
 *  Restore hooked function
 *  @param  address  address being modified
 *  @return  address of the replaced function or 0 if failed
 */
ulong restore_fun(ulong address);

WINHOOK_END_NAMESPACE

// EOF
