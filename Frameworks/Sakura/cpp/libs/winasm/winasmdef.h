#pragma once

// winasmdef.h
// 5/25/2015 jichi

#define s1_0d           0,0,0,0 // 0x0000
#define s1_int3         0xcc    // int3
#define s1_nop          0x90    // nop

#define s1_call_        0xe8            // near call, incomplete
#define s1_call_0d      s1_call_, s1_0d // near call 0x0000
#define s1_jmp_         0xe9            // short jmp, incomplete
#define s1_jmp_0d       s1_jmp_, s1_0d  // short jmp 0x0000

#define s1_farcall_     0xff,0x15  // call, incomplete
#define s2_farcall_     0x15ff
#define s1_longjmp_     0xff,0x25  // call, incomplete
#define s2_longjmp_     0x25ff

#define s1_push_        0x68        // push, incomplete
#define s1_push_0d      0x68, s1_0d // push 0x0000

#define s1_push_eax     0x50    // push eax
#define s1_push_ecx     0x51    // push ecx
#define s1_push_edx     0x52    // push edx
#define s1_push_ebx     0x53    // push edi
#define s1_push_esp     0x54    // push esp
#define s1_push_esi     0x56    // push esi
#define s1_push_edi     0x57    // push edi
#define s1_pop_esp      0x5c    // pop esp
#define s1_pop_esi      0x5e    // pop esi
#define s1_pop_edi      0x5f    // pop edi

#define s1_pushad       0x60    // pushad
#define s1_popad        0x61    // popad
#define s1_pushfd       0x9c    // pushfd
#define s1_popfd        0x9d    // popfd

#define s1_mov_edi_eax  0x8b,0xf8   // mov edi,eax
#define s2_mov_edi_eax  0xf88b

#define s1_mov_ecx_edi  0x8b,0xcf   // mov ecx,edi
#define s2_mov_ecx_edi  0xcf8b

#define s1_mov_ecx_0d   0xb9, s1_0d // mov ecx, 0x0000

#define s1_test_eax_eax  0x85,0xc0   // text edi,eax
#define s2_test_eax_eax  0xc085

// EOF
