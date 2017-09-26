#pragma once

/**
 *  detoursutil.h
 *  4/20/2014 jichi
 *
 *  Note for detours
 *  - It simply replaces the code with jmp and int3. Jmp to newHookFun
 *  - oldHookFun is the address to a code segment that jmp back to the original function
 */

namespace detours {

typedef void *address_t; // LPVOID
typedef const void *const_address_t; // LPCVOID

// Replace old_addr with new_addr, and return the backup of old_addr if succeed or 0 if fails.
address_t replace(address_t old_addr, const_address_t new_addr);
address_t restore(address_t restore_addr, const_address_t old_addr);

// Ignore type checking
template<typename Ret, typename Arg1, typename Arg2>
inline Ret replace(Arg1 arg1, Arg2 arg2)
{ return (Ret)replace((address_t)arg1, (const_address_t)arg2); }

// Ignore type checking
template<typename Ret, typename Arg1, typename Arg2>
inline Ret restore(Arg1 arg1, Arg2 arg2)
{ return (Ret)restore((address_t)arg1, (const_address_t)arg2); }

} // namespace detours

// EOF
