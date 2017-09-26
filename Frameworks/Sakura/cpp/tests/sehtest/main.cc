// main.cc
// 12/2/2013 jichi
// See: http://msdn.microsoft.com/en-us/library/ha52ak6a.aspx
// link with: /SAFESEH:NO
//
// Disable SafeSEH table
// http://stackoverflow.com/questions/19722308/exception-handler-not-called-in-c/20344222
// Alternative way: Register handler using MASM
// http://stackoverflow.com/questions/12019689/custom-seh-handler-with-safeseh
//
// Sample output:
// main: sizeof(dword) = 4, sizeof(dword_ptr) = 4
// main: enter: 2511b7,0,0
// level1: enter: 2511b7,251116,0
// level2: enter: 2511b7,251116,251091
// level2: leave
// level1: leave
// main: leave

# pragma warning (disable:4733)   // C4733: Inline asm assigning to 'FS:0' : handler not registered as safe handler

#include "winseh/winseh.h"
#include <windows.h>
#include <cstdio>

#define ILLEGAL_ACCESS  (*(int*)0 = 0)

void level2() {
  seh_with({
    printf("level2: enter: %x,%x,%x\n", seh_eip[0], seh_eip[1], seh_eip[2]);
    ILLEGAL_ACCESS;
  })
  printf("level2 leave\n");
}

void level1() {
  seh_with({
    printf("level1: enter: %x,%x,%x\n", seh_eip[0], seh_eip[1], seh_eip[2]);
    level2();
    ILLEGAL_ACCESS;
  })
  printf("level1: leave\n");
}

int main()
{
  printf("main: sizeof(dword) = %x, sizeof(dword_ptr) = %x\n", sizeof(DWORD), sizeof(DWORD_PTR));
  seh_with({
    printf("main: enter: %x,%x,%x\n", seh_eip[0], seh_eip[1], seh_eip[2]);
    level1();
    ILLEGAL_ACCESS;
  })
  printf("main: leave\n");

  __try {
    printf("main: __try\n");
    ILLEGAL_ACCESS;
  } __except(EXCEPTION_EXECUTE_HANDLER) {
    printf("main: __except\n");
  }
  printf("main: leave\n");
}

// EOF
