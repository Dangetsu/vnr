#pragma once

// hookcall.h
// 5/31/2015 jichi

#include "winhook/hookdef.h"

WINHOOK_BEGIN_NAMESPACE

/**
 *  Replace the old function definition with the new one
 *  Do not change call type.
 *  @param  oldop  address of the near/far call/jump instruction
 *  @param  newop  the function call to replace
 *  @return  original function address being call
 */
ulong replace_call(ulong oldop, ulong newop);

/**
 *  Replace the old function definition with the new one
 *  Always use near call as the target.
 *  @param  oldop  address of the near/far call/jump instruction
 *  @param  newop  the function call to replace
 *  @return  original function address being call
 */
ulong replace_near_call(ulong oldop, ulong newop);

/**
 *  Replace the old function definition with the new one
 *  Always use far call as the target.
 *  @param  oldop  address of the near/far call/jump instruction
 *  @param  newop  the function call to replace
 *  @return  original function address being call
 */
// Not implemented as not used
//ulong replace_far_call(ulong oldop, ulong newop);

/**
 *  Restore hooked function
 *  @param  address  address being modified
 *  @return  address of the replaced function or 0 if failed
 */
//ulong restore_call(ulong address);

WINHOOK_END_NAMESPACE

// EOF
