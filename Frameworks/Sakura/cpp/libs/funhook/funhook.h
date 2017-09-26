#pragma once

// funhook.h
// 1/27/2013

#ifdef _MSC_VER
# include <cstddef> // for wchar_t
#endif // _MSC_VER

#ifndef FUNHOOK_BEGIN_NAMESPACE
# define FUNHOOK_BEGIN_NAMESPACE namespace funhook {
#endif
#ifndef FUNHOOK_END_NAMESPACE
# define FUNHOOK_END_NAMESPACE   } // namespace funhook
#endif

FUNHOOK_BEGIN_NAMESPACE

/**
 *  HookAfterFunction only works for stdcall functions. Arguments to function are
 *  the output of the original function (Must be <= 32 bits) followed by the arguments
 *  to the original function. Must return return value itself.
 *  Currently doesn't pass a parameter around, just takes param for future extension.
 *  hookFxn passed param and stack from the middle of a code point.
 */
int hookAfterFunction(void *addr, wchar_t *id, void *param, void *hookFxn);

// hookFxn passed param and stack from the middle of a code point.
int hookRawAddress(void *addr, wchar_t *id, void *param, void *hookFxn);

FUNHOOK_END_NAMESPACE

// EOF
