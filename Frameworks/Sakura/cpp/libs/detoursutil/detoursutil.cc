// detoursutil.cc
// 4/20/2014 jichi
//
// http://research.microsoft.com/en-us/projects/detours/
// Version 3.0 license costs $10000 orz
//
// http://social.msdn.microsoft.com/Forums/en-US/vcgeneral/thread/ef4a6bdd-6e9f-4f0a-9096-ca07ad65ddc2/
// http://stackoverflow.com/questions/3263688/using-detours-for-hooking-writing-text-in-notepad

#include "detoursutil/detoursutil.h"
#include <windows.h>
#include <detours.h>

//BOOL (WINAPI *OldTextOutA)(HDC hdc, int nXStart, int nYStart, LPCSTR lpString, int cchString) = TextOutA;
detours::address_t detours::replace(address_t old_addr, const_address_t new_addr)
{
  address_t ret = old_addr;
  ::DetourRestoreAfterWith();
  ::DetourTransactionBegin();
  ::DetourUpdateThread(::GetCurrentThread());
  ::DetourAttach((PVOID *)&ret, (PVOID)new_addr);
  ::DetourTransactionCommit();
  return ret;
}

 detours::address_t detours::restore(address_t restore_addr, const_address_t old_addr)
{
  address_t ret = restore_addr;
  //::DetourRestoreAfterWith();
  ::DetourTransactionBegin();
  ::DetourUpdateThread(::GetCurrentThread());
  ::DetourDetach((PVOID *)&ret, (PVOID)old_addr);
  ::DetourTransactionCommit();
  return ret;
}

// EOF
