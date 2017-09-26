// bgi.cc
// 5/11/2014 jichi
#include "engine/model/bgi.h"
#include "engine/enginecontroller.h"
#include "engine/enginedef.h"
#include "engine/enginehash.h"
#include "engine/engineutil.h"
#include "hijack/hijackmanager.h"
#include "memdbg/memsearch.h"
#include "winhook/hookcode.h"
#include <qt_windows.h>
#include <cstdint>

#define DEBUG "model/bgi"
#include "sakurakit/skdebug.h"

namespace { // unnamed

namespace ScenarioHook {

namespace Private {
  enum { Type1 = 1, Type2, Type3 } type_;
  int textIndex_; // the i-th of argument on the stack holding the text

  /**
   *  Type 1: Sample game: FORTUNE ARTERIAL, 0x4207E0
   *
   *  ? __cdecl sub_4207E0 proc near
   *  - arg1: address
   *  - arg2: address
   *  - arg3: string, LPCSTR
   *  - arg4: 0
   *  - arg5: function address
   *  - arg6: address, pointed to 0
   *  - arg7: address, pointed to 0
   *  - arg8: 0x1c, 0x18, observation from FA: This value diff for scenario and name
   *  - arg9: 1
   *  - arg10: 0
   *  - arg11: 0 or 1, maybe, gender?
   *  - arg12: 0x00ffffff
   *  - arg13: addr
   *
   *  Guessed function signature:
   *  typedef int (__cdecl *hook_fun_t)(DWORD, DWORD, LPCSTR, DWORD, DWORD, DWORD,
   *                                    DWORD, DWORD, DWORD, DWORD, DWORD, DWORD, DWORD);
   *  static int __cdecl newHookFun(DWORD arg1, DWORD arg2, LPCSTR str, DWORD arg4, DWORD arg5, DWORD arg6,
   *                                DWORD arg7, DWORD split, DWORD arg9, DWORD arg10, DWORD arg11, DWORD arg12, DWORD arg13)
   *
   *  Type 2: Sample game: 世界と世界の真ん中 体験版, relative address: 0x31850;
   *
   *  ? __cdecl sub_31850(DWORD arg1, DWORD arg2, LPCSTR arg3, DWORD arg4)
   *  - arg1: address, could point to area of zero, seems to be the output of this function
   *  - arg2: address, the same as arg1
   *  - arg3: string
   *  - arg4: flags, choices: 0, character name & scenario: 1
   *  - return: not sure, seems always to be 0 when success
   *
   *  Guessed function signature:
   *  - typedef int (__cdecl *hook_fun_t)(DWORD, DWORD, LPCSTR, DWORD); // __stdcall will crash the game
   *  - static int __cdecl newHookFun(DWORD arg1, DWORD arg2, LPCSTR str, DWORD split)
   *
   *  History: 0x12b37ba
   *  012B37AC   52               PUSH EDX
   *  012B37AD   50               PUSH EAX
   *  012B37AE   8D8D 38FFFFFF    LEA ECX,DWORD PTR SS:[EBP-0xC8]
   *  012B37B4   51               PUSH ECX
   *  012B37B5   E8 96E0FFFF      CALL .012B1850    ; jichi: called here
   *  012B37BA   83C4 34          ADD ESP,0x34
   *  012B37BD   837D 24 00       CMP DWORD PTR SS:[EBP+0x24],0x0 ; jichi: used to distinguish choice out
   *  012B37C1   74 19            JE SHORT .012B37DC
   *  012B37C3   8B45 44          MOV EAX,DWORD PTR SS:[EBP+0x44]
   *  012B37C6   8D55 80          LEA EDX,DWORD PTR SS:[EBP-0x80]
   *  012B37C9   52               PUSH EDX
   *  012B37CA   56               PUSH ESI
   *  012B37CB   50               PUSH EAX
   *  012B37CC   8D8D 38FFFFFF    LEA ECX,DWORD PTR SS:[EBP-0xC8]
   *
   *  Scenario: 0x12b38ac
   *  012B3898   51               PUSH ECX
   *  012B3899   8B4D 10          MOV ECX,DWORD PTR SS:[EBP+0x10]
   *  012B389C   52               PUSH EDX
   *  012B389D   8B55 0C          MOV EDX,DWORD PTR SS:[EBP+0xC]
   *  012B38A0   50               PUSH EAX
   *  012B38A1   8B45 08          MOV EAX,DWORD PTR SS:[EBP+0x8]
   *  012B38A4   51               PUSH ECX
   *  012B38A5   52               PUSH EDX
   *  012B38A6   50               PUSH EAX
   *  012B38A7   E8 A4DFFFFF      CALL .012B1850    ; jichi: called here
   *  012B38AC   83C4 34          ADD ESP,0x34
   *  012B38AF   5D               POP EBP
   *  012B38B0   C2 3400          RETN 0x34
   *  012B38B3   CC               INT3
   *  012B38B4   CC               INT3
   *
   *  Sample game: サクラノ詩 (type 3)
   *
   *  Scenario:
   *
   *  0017F29C   0033390A  RETURN to .0033390A from .00333920
   *  0017F2A0   0CEE35B4
   *  0017F2A4   0BBB8A58
   *  0017F2A8   00000001
   *  0017F2AC   0017F320
   *  0017F2B0   0017F344
   *  0017F2B4   0000002A
   *  0017F2B8   00000001
   *  0017F2BC   00000000
   *  0017F2C0   00000001
   *  0017F2C4   00000000
   *
   *  003338FD   8B55 18          MOV EDX,DWORD PTR SS:[EBP+0x18]
   *  00333900   50               PUSH EAX
   *  00333901   51               PUSH ECX
   *  00333902   8B4D 0C          MOV ECX,DWORD PTR SS:[EBP+0xC]
   *  00333905   E8 16000000      CALL .00333920    ; jichi: called here
   *  0033390A   83C4 2C          ADD ESP,0x2C
   *  0033390D   5D               POP EBP
   *  0033390E   C2 3400          RETN 0x34
   *  00333911   CC               INT3
   *  00333912   CC               INT3
   *  00333913   CC               INT3
   *  00333914   CC               INT3
   *  00333915   CC               INT3
   *
   *  EAX 0BBB8A58
   *  ECX 0017F31C
   *  EDX 0044C4A4 .0044C4A4
   *  EBX 0CEE3538
   *  ESP 0017F29C
   *  EBP 0017F2CC
   *  ESI 0CEE35B4
   *  EDI 00000001
   *  EIP 00333920 .00333920
   *
   *  History:
   *  0017F0D8   0033338E  RETURN to .0033338E from .00333920
   *  0017F0DC   0017F148
   *  0017F0E0   0F8A2E78
   *  0017F0E4   00000001
   *  0017F0E8   0017F220
   *  0017F0EC   0017F210
   *  0017F0F0   00000028
   *  0017F0F4   00000001
   *  0017F0F8   00000000
   *  0017F0FC   00000001
   *  0017F100   00000000
   *
   *  EAX 0017F220
   *  ECX 0017F344
   *  EDX 0017F190
   *  EBX 00000001
   *  ESP 0017F0D8
   *  EBP 0017F1B8
   *  ESI 00000001
   *  EDI 00000001
   *  EIP 00333920 .00333920
   *
   *  00333385   52               PUSH EDX
   *  00333386   8D55 D8          LEA EDX,DWORD PTR SS:[EBP-0x28]
   *  00333389   E8 92050000      CALL .00333920    ; jichi: called here
   *  0033338E   83C4 2C          ADD ESP,0x2C
   *  00333391   85DB             TEST EBX,EBX
   *  00333393   74 19            JE SHORT .003333AE
   *  00333395   8B4D 40          MOV ECX,DWORD PTR SS:[EBP+0x40]
   *  00333398   8D45 D8          LEA EAX,DWORD PTR SS:[EBP-0x28]
   *  0033339B   50               PUSH EAX
   *  0033339C   51               PUSH ECX
   *
   *  Name:
   *  001AF0F0   0119338E  RETURN to .0119338E from .01193920
   *  001AF0F4   001AF160
   *  001AF0F8   0DC69690
   *  001AF0FC   00000000
   *  001AF100   001AF238
   *  001AF104   001AF228
   *  001AF108   00000018
   *  001AF10C   00000005
   *  001AF110   00000000   ; jichi: zero
   *  001AF114   00000000
   *  001AF118   00000000   ; jichi: zero
   *  001AF11C   001AF304
   *  001AF120   001AF288
   *  001AF124   0D5E1FF8
   *
   *  0119337F   8B4D 14          MOV ECX,DWORD PTR SS:[EBP+0x14]
   *  01193382   8D55 90          LEA EDX,DWORD PTR SS:[EBP-0x70]
   *  01193385   52               PUSH EDX
   *  01193386   8D55 D8          LEA EDX,DWORD PTR SS:[EBP-0x28]
   *  01193389   E8 92050000      CALL .01193920    ; jichi: called here
   *  0119338E   83C4 2C          ADD ESP,0x2C
   *  01193391   85DB             TEST EBX,EBX
   *  01193393   74 19            JE SHORT .011933AE
   *  01193395   8B4D 40          MOV ECX,DWORD PTR SS:[EBP+0x40]
   *  01193398   8D45 D8          LEA EAX,DWORD PTR SS:[EBP-0x28]
   *  0119339B   50               PUSH EAX
   *  0119339C   51               PUSH ECX
   *  0119339D   8B4D 44          MOV ECX,DWORD PTR SS:[EBP+0x44]
   *  011933A0   8D55 90          LEA EDX,DWORD PTR SS:[EBP-0x70]
   *  011933A3   52               PUSH EDX
   */
  bool hookBefore(winhook::hook_stack *s)
  {
    static QByteArray data_; // persistent storage, which makes this function not thread-safe

    LPCSTR text = (LPCSTR)s->stack[textIndex_]; // arg2 or arg3
    if (!text || !*text)
      return true;

    // In Type 1, split = arg8
    // In Type 2, there is no arg8. However, arg8 seems to be a good split that can differenciate choice and character name
    //DWORD split = stack->args[3]; // arg4
    //DWORD split = s->stack[8]; // arg8
    //auto sig = Engine::hashThreadSignature(s->stack[0], split);
    //enum { role = Engine::UnknownRole };

    //DWORD split = s->stack[8]; // this is a good split, but usually game-specific
    DWORD retaddr = s->stack[0]; // retaddr
    int role = Engine::OtherRole;
    switch (type_) {
    case Type3:
      switch (s->stack[textIndex_+1]) {
      case 1:
        if (*(WORD *)(retaddr + 8) == 0xcccc) // two int3
          role = Engine::ScenarioRole;
        break;
      case 0:
        if (s->stack[10] == 0x00ffffff && s->stack[10 - 3] == 1 ||   // for old BGI2 games
            s->stack[10] == 0 && s->stack[10 - 1] == 0 && s->stack[10 - 2] == 0) // for new BGI2 games
         role = Engine::NameRole;
        break;
      } break;
    case Type2:
      switch (s->stack[textIndex_+1]) {
      case 1:
        // Return address for history text
        // 012B37BA   83C4 34          ADD ESP,0x34
        // 012B37BD   837D 24 00       CMP DWORD PTR SS:[EBP+0x24],0x0
        if (*(WORD *)(retaddr + 3) != 0x7d83)
          role = Engine::ScenarioRole;
        break;
      case 0:
        if (s->stack[12] == 0x00ffffff && s->stack[12 - 3] == 2)
         role = Engine::NameRole;
        break;
      } break;
    case Type1:
      switch (s->stack[textIndex_+1]) {
      case 1: role = Engine::ScenarioRole; break;
      case 0:
        if (s->stack[12] == 0x00ffffff && s->stack[12 - 3] == 1)
         role = Engine::NameRole;
        break;
      } break;
    }

    auto sig = Engine::hashThreadSignature(role, retaddr);
    data_ = EngineController::instance()->dispatchTextA(text, role, sig);
    s->stack[textIndex_] = (DWORD)data_.constData();
    return true;
  }

  /**
   *  5/12/2014
   *  This is the caller of the ITH BGI hook, which extract text by characters
   *  and cannot be used for substition.
   *
   *  Sample game: 世界征服彼女
   *  ITH hooked function: BGI#2 0x425550, called by 0x427450
   *
   *  00427450  /$ 6a ff          push -0x1  ; jichi: function starts
   *  00427452  |. 68 78634900    push sekajyo_.00496378                   ;  se handler installation
   *  00427457  |. 64:a1 00000000 mov eax,dword ptr fs:[0]
   *  0042745d  |. 50             push eax
   *  0042745e  |. 64:8925 000000>mov dword ptr fs:[0],esp
   *  00427465  |. 81ec d80c0000  sub esp,0xcd8
   *  0042746b  |. 8b8424 080d000>mov eax,dword ptr ss:[esp+0xd08]
   *  00427472  |. 56             push esi
   *  00427473  |. 8d8c24 3801000>lea ecx,dword ptr ss:[esp+0x138]
   *  0042747a  |. 50             push eax
   *  0042747b  |. 51             push ecx
   *  0042747c  |. 8b0d e0464b00  mov ecx,dword ptr ds:[0x4b46e0]
   *  00427482  |. e8 f9fdfdff    call sekajyo_.00407280
   *  00427487  |. 33f6           xor esi,esi
   *  00427489  |. 898424 b800000>mov dword ptr ss:[esp+0xb8],eax
   *  00427490  |. 3bc6           cmp eax,esi
   *  00427492  |. 0f84 95140000  je sekajyo_.0042892d
   *  00427498  |. 53             push ebx
   *  00427499  |. 55             push ebp
   *  0042749a  |. 8bac24 fc0c000>mov ebp,dword ptr ss:[esp+0xcfc]
   *  004274a1  |. 57             push edi
   *  004274a2  |. 89b424 b400000>mov dword ptr ss:[esp+0xb4],esi
   *  004274a9  |. 897424 10      mov dword ptr ss:[esp+0x10],esi
   *  004274ad  |. 8a45 00        mov al,byte ptr ss:[ebp]
   *  004274b0  |. b9 01000000    mov ecx,0x1
   *  004274b5  |. 3c 20          cmp al,0x20
   *  004274b7  |. 7d 68          jge short sekajyo_.00427521
   *  004274b9  |. 0fbec0         movsx eax,al
   *  004274bc  |. 83c0 fe        add eax,-0x2                             ;  switch (cases 2..8)
   *
   *  Sample game: FORTUNE ARTERIAL
   *  ITH hooked function: BGI#2 sub_41EBD0, called by 0x4207e0
   *
   *  0041ebcd     90             nop
   *  0041ebce     90             nop
   *  0041ebcf     90             nop
   *  004207e0  /$ 81ec 30090000  sub esp,0x930   ; jichi: function starts
   *  004207e6  |. 8b8424 5409000>mov eax,dword ptr ss:[esp+0x954]
   *  004207ed  |. 56             push esi
   *  004207ee  |. 8d8c24 0401000>lea ecx,dword ptr ss:[esp+0x104]
   *  004207f5  |. 50             push eax
   *  004207f6  |. 51             push ecx
   *  004207f7  |. 8b0d 48634900  mov ecx,dword ptr ds:[0x496348]
   *  004207fd  |. e8 ee47feff    call bgi.00404ff0
   *  00420802  |. 33f6           xor esi,esi
   *  00420804  |. 894424 54      mov dword ptr ss:[esp+0x54],eax
   *  00420808  |. 3bc6           cmp eax,esi
   *  0042080a  |. 0f84 94080000  je bgi.004210a4
   *  00420810  |. 53             push ebx
   *  00420811  |. 55             push ebp
   *  00420812  |. 8bac24 4809000>mov ebp,dword ptr ss:[esp+0x948]
   *  00420819  |. 57             push edi
   *  0042081a  |. 897424 54      mov dword ptr ss:[esp+0x54],esi
   *  0042081e  |. 897424 10      mov dword ptr ss:[esp+0x10],esi
   *  00420822  |. 8a45 00        mov al,byte ptr ss:[ebp]
   *  00420825  |. 3c 20          cmp al,0x20
   *  00420827  |. 7d 69          jge short bgi.00420892
   *  00420829  |. 0fbec0         movsx eax,al
   *  0042082c  |. 83c0 fe        add eax,-0x2                             ;  switch (cases 2..8)
   *  0042082f  |. 83f8 06        cmp eax,0x6
   *  00420832  |. 77 5e          ja short bgi.00420892
   *  00420834  |. ff2485 ac10420>jmp dword ptr ds:[eax*4+0x4210ac]
   *  0042083b  |> c74424 54 0100>mov dword ptr ss:[esp+0x54],0x1          ;  case 2 of switch 0042082c
   *  00420843  |. eb 45          jmp short bgi.0042088a
   *  00420845  |> 8d5424 1c      lea edx,dword ptr ss:[esp+0x1c]          ;  case 4 of switch 0042082c
   *  00420849  |. 68 0c424800    push bgi.0048420c
   *  0042084e  |. 52             push edx
   *  0042084f  |. eb 29          jmp short bgi.0042087a
   *  00420851  |> 68 08424800    push bgi.00484208                        ;  case 5 of switch 0042082c
   *  00420856  |. eb 1d          jmp short bgi.00420875
   *  00420858  |> 8d4c24 1c      lea ecx,dword ptr ss:[esp+0x1c]          ;  case 6 of switch 0042082c
   *  0042085c  |. 68 04424800    push bgi.00484204
   *  00420861  |. 51             push ecx
   *  00420862  |. eb 16          jmp short bgi.0042087a
   *  00420864  |> 8d5424 1c      lea edx,dword ptr ss:[esp+0x1c]          ;  case 7 of switch 0042082c
   *  00420868  |. 68 00424800    push bgi.00484200
   *  0042086d  |. 52             push edx
   *  0042086e  |. eb 0a          jmp short bgi.0042087a
   *  00420870  |> 68 fc414800    push bgi.004841fc                        ;  case 8 of switch 0042082c
   *  00420875  |> 8d4424 20      lea eax,dword ptr ss:[esp+0x20]
   *  00420879  |. 50             push eax
   *  0042087a  |> c74424 18 0100>mov dword ptr ss:[esp+0x18],0x1
   *  00420882  |. e8 b9a7ffff    call bgi.0041b040
   *  00420887  |. 83c4 08        add esp,0x8
   *  0042088a  |> 45             inc ebp
   *  0042088b  |. 89ac24 4c09000>mov dword ptr ss:[esp+0x94c],ebp
   *  00420892  |> 8b9c24 3001000>mov ebx,dword ptr ss:[esp+0x130]         ;  default case of switch 0042082c
   *  00420899  |. 8d8c24 1001000>lea ecx,dword ptr ss:[esp+0x110]
   *  004208a0  |. 51             push ecx
   *  004208a1  |. 895c24 70      mov dword ptr ss:[esp+0x70],ebx
   *  004208a5  |. e8 76080000    call bgi.00421120
   *  004208aa  |. 894424 34      mov dword ptr ss:[esp+0x34],eax
   *  004208ae  |. 8b8424 5409000>mov eax,dword ptr ss:[esp+0x954]
   *  004208b5  |. 83c4 04        add esp,0x4
   *  004208b8  |. 3bc6           cmp eax,esi
   *  004208ba  |. 74 0f          je short bgi.004208cb
   *  004208bc  |. 53             push ebx
   *  004208bd  |. e8 7e080000    call bgi.00421140
   */
  ulong search1(ulong startAddress, ulong stopAddress)
  {
    //return 0x4207e0; // FORTUNE ARTERIAL
    //const BYTE bytes[] = {
    //  0x8a,0x45, 0x00,  // 00420822  |. 8a45 00        mov al,byte ptr ss:[ebp]
    //  0x3c, 0x20,       // 00420825  |. 3c 20          cmp al,0x20
    //  0x7d, 0x69,       // 00420827  |. 7d 69          jge short bgi.00420892
    //  0x0f,0xbe,0xc0,   // 00420829  |. 0fbec0         movsx eax,al
    //  0x83,0xc0, 0xfe,  // 0042082c  |. 83c0 fe        add eax,-0x2                             ;  switch (cases 2..8)
    //  0x83,0xf8, 0x06,  // 0042082f  |. 83f8 06        cmp eax,0x6
    //  0x77, 0x5e        // 00420832  |. 77 5e          ja short bgi.00420892
    //};
    //enum { hook_offset = 0x4207e0 - 0x420822 }; // distance to the beginning of the function

    const uint8_t bytes[] = { // 0fafcbf7e9c1fa058bc2c1e81f03d08bfa85ff
       0x0f,0xaf,0xcb,   // 004208de  |. 0fafcb         imul ecx,ebx
       0xf7,0xe9,        // 004208e1  |. f7e9           imul ecx
       0xc1,0xfa, 0x05,  // 004208e3  |. c1fa 05        sar edx,0x5
       0x8b,0xc2,        // 004208e6  |. 8bc2           mov eax,edx
       0xc1,0xe8, 0x1f,  // 004208e8  |. c1e8 1f        shr eax,0x1f
       0x03,0xd0,        // 004208eb  |. 03d0           add edx,eax
       0x8b,0xfa,        // 004208ed  |. 8bfa           mov edi,edx
       0x85,0xff,        // 004208ef  |. 85ff           test edi,edi
    };
    //enum { hook_offset = 0x4207e0 - 0x4208de }; // distance to the beginning of the function
    //ulong range = qMin(stopAddress - startAddress, Engine::MaximumMemoryRange);
    ulong addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
    if (!addr)
      //ConsoleOutput("vnreng:BGI2: pattern not found");
      return 0;
    enum : WORD {
      sub_esp = 0xec81   // 004207e0  /$ 81ec 30090000
      , push_ff = 0xff6a // 00427450  /$ 6a ff   push -0x1, seh handler
    };
    for (int i = 0; i < 300; i++, addr--)
      if (*(WORD *)addr == sub_esp) { // beginning of the function without seh

        // Sample game: 世界征服彼女 with SEH
        // 00427450  /$ 6a ff          push -0x1
        // 00427452  |. 68 78634900    push sekajyo_.00496378                   ;  se handler installation
        // 00427457  |. 64:a1 00000000 mov eax,dword ptr fs:[0]
        // 0042745d  |. 50             push eax
        // 0042745e  |. 64:8925 000000>mov dword ptr fs:[0],esp
        // 00427465  |. 81ec d80c0000  sub esp,0xcd8
        //
        // 0x00427465 - 0x00427450 == 21
        ulong seh_addr = addr;
        for (int j = 0; j < 40; j++, seh_addr--)
          if (*(WORD *)seh_addr == push_ff) // beginning of the function with seh
            return seh_addr;
        return addr;
      }

    return 0;
  }

  /**
   *  jichi 2/5/2014: Add an alternative BGI hook
   *
   *  Issue: This hook cannot extract character name for コトバの消えた日
   *
   *  See: http://tieba.baidu.com/p/2845113296
   *  世界と世界の真ん中で
   *  - /HSN4@349E0:sekachu.exe // Disabled BGI3, floating split char
   *  - /HS-1C:-4@68E56 // Not used, cannot detect character name
   *  - /HSC@34C80:sekachu.exe  // BGI2, extract both scenario and character names
   *
   *  [Lump of Sugar] 世界と世界の真ん中で
   *  /HSC@34C80:sekachu.exe
   *  - addr: 216192 = 0x34c80
   *  - module: 3599131534
   *  - off: 12 = 0xc
   *  - type: 65 = 0x41
   *
   *  base: 0x11a0000
   *  hook_addr = base + addr = 0x11d4c80
   *
   *  011d4c7e     cc             int3
   *  011d4c7f     cc             int3
   *  011d4c80  /$ 55             push ebp    ; jichi: hook here
   *  011d4c81  |. 8bec           mov ebp,esp
   *  011d4c83  |. 6a ff          push -0x1
   *  011d4c85  |. 68 e6592601    push sekachu.012659e6
   *  011d4c8a  |. 64:a1 00000000 mov eax,dword ptr fs:[0]
   *  011d4c90  |. 50             push eax
   *  011d4c91  |. 81ec 300d0000  sub esp,0xd30
   *  011d4c97  |. a1 d8c82801    mov eax,dword ptr ds:[0x128c8d8]
   *  011d4c9c  |. 33c5           xor eax,ebp
   *  011d4c9e  |. 8945 f0        mov dword ptr ss:[ebp-0x10],eax
   *  011d4ca1  |. 53             push ebx
   *  011d4ca2  |. 56             push esi
   *  011d4ca3  |. 57             push edi
   *  011d4ca4  |. 50             push eax
   *  011d4ca5  |. 8d45 f4        lea eax,dword ptr ss:[ebp-0xc]
   *  011d4ca8  |. 64:a3 00000000 mov dword ptr fs:[0],eax
   *  011d4cae  |. 8b4d 0c        mov ecx,dword ptr ss:[ebp+0xc]
   *  011d4cb1  |. 8b55 18        mov edx,dword ptr ss:[ebp+0x18]
   *  011d4cb4  |. 8b45 08        mov eax,dword ptr ss:[ebp+0x8]
   *  011d4cb7  |. 8b5d 10        mov ebx,dword ptr ss:[ebp+0x10]
   *  011d4cba  |. 8b7d 38        mov edi,dword ptr ss:[ebp+0x38]
   *  011d4cbd  |. 898d d8f3ffff  mov dword ptr ss:[ebp-0xc28],ecx
   *  011d4cc3  |. 8b4d 28        mov ecx,dword ptr ss:[ebp+0x28]
   *  011d4cc6  |. 8995 9cf3ffff  mov dword ptr ss:[ebp-0xc64],edx
   *  011d4ccc  |. 51             push ecx
   *  011d4ccd  |. 8b0d 305c2901  mov ecx,dword ptr ds:[0x1295c30]
   *  011d4cd3  |. 8985 e0f3ffff  mov dword ptr ss:[ebp-0xc20],eax
   *  011d4cd9  |. 8b45 1c        mov eax,dword ptr ss:[ebp+0x1c]
   *  011d4cdc  |. 8d95 4cf4ffff  lea edx,dword ptr ss:[ebp-0xbb4]
   *  011d4ce2  |. 52             push edx
   *  011d4ce3  |. 899d 40f4ffff  mov dword ptr ss:[ebp-0xbc0],ebx
   *  011d4ce9  |. 8985 1cf4ffff  mov dword ptr ss:[ebp-0xbe4],eax
   *  011d4cef  |. 89bd f0f3ffff  mov dword ptr ss:[ebp-0xc10],edi
   *  011d4cf5  |. e8 862efdff    call sekachu.011a7b80
   *  011d4cfa  |. 33c9           xor ecx,ecx
   *  011d4cfc  |. 8985 60f3ffff  mov dword ptr ss:[ebp-0xca0],eax
   *  011d4d02  |. 3bc1           cmp eax,ecx
   *  011d4d04  |. 0f84 0f1c0000  je sekachu.011d6919
   *  011d4d0a  |. e8 31f6ffff    call sekachu.011d4340
   *  011d4d0f  |. e8 6cf8ffff    call sekachu.011d4580
   *  011d4d14  |. 8985 64f3ffff  mov dword ptr ss:[ebp-0xc9c],eax
   *  011d4d1a  |. 8a03           mov al,byte ptr ds:[ebx]
   *  011d4d1c  |. 898d 90f3ffff  mov dword ptr ss:[ebp-0xc70],ecx
   *  011d4d22  |. 898d 14f4ffff  mov dword ptr ss:[ebp-0xbec],ecx
   *  011d4d28  |. 898d 38f4ffff  mov dword ptr ss:[ebp-0xbc8],ecx
   *  011d4d2e  |. 8d71 01        lea esi,dword ptr ds:[ecx+0x1]
   *  011d4d31  |. 3c 20          cmp al,0x20
   *  011d4d33  |. 7d 75          jge short sekachu.011d4daa
   *  011d4d35  |. 0fbec0         movsx eax,al
   *  011d4d38  |. 83c0 fe        add eax,-0x2                             ;  switch (cases 2..8)
   *  011d4d3b  |. 83f8 06        cmp eax,0x6
   *  011d4d3e  |. 77 6a          ja short sekachu.011d4daa
   *  011d4d40  |. ff2485 38691d0>jmp dword ptr ds:[eax*4+0x11d6938]
   */
  ulong search2(ulong startAddress, ulong stopAddress)
  {
    //return startAddress + 0x31850; // 世界と世界の真ん中 体験版
    const uint8_t bytes[] = { // 3c207d750fbec083c0fe83f806776a
      0x3c, 0x20,      // 011d4d31  |. 3c 20          cmp al,0x20
      0x7d, 0x75,      // 011d4d33  |. 7d 75          jge short sekachu.011d4daa
      0x0f,0xbe,0xc0,  // 011d4d35  |. 0fbec0         movsx eax,al
      0x83,0xc0, 0xfe, // 011d4d38  |. 83c0 fe        add eax,-0x2                             ;  switch (cases 2..8)
      0x83,0xf8, 0x06, // 011d4d3b  |. 83f8 06        cmp eax,0x6
      0x77, 0x6a       // 011d4d3e  |. 77 6a          ja short sekachu.011d4daa
    };
    enum { hook_offset = 0x34c80 - 0x34d31 }; // distance to the beginning of the function
    //ulong range = qMin(stopAddress - startAddress, Engine::MaximumMemoryRange);
    ulong addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
    if (!addr)
      //ConsoleOutput("vnreng:BGI2: pattern not found");
      return 0;

    addr += hook_offset;
    enum : uint8_t { push_ebp = 0x55 };  // 011d4c80  /$ 55             push ebp
    if (*(uint8_t *)addr != push_ebp)
      //ConsoleOutput("vnreng:BGI2: pattern found but the function offset is invalid");
      return 0;

    return addr;
  }

  /**
   *  Sample Game: type 3: 蒼の彼方 体験版 (8/6/2014)
   *  01312cce     cc             int3    ; jichi: reladdr = 0x32cd0
   *  01312ccf     cc             int3
   *  01312cd0   $ 55             push ebp
   *  01312cd1   . 8bec           mov ebp,esp
   *  01312cd3   . 83e4 f8        and esp,0xfffffff8
   *  01312cd6   . 6a ff          push -0x1
   *  01312cd8   . 68 86583a01    push 蒼の彼方.013a5886
   *  01312cdd   . 64:a1 00000000 mov eax,dword ptr fs:[0]
   *  01312ce3   . 50             push eax
   *  01312ce4   . 81ec 38090000  sub esp,0x938
   *  01312cea   . a1 24673c01    mov eax,dword ptr ds:[0x13c6724]
   *  01312cef   . 33c4           xor eax,esp
   *  01312cf1   . 898424 3009000>mov dword ptr ss:[esp+0x930],eax
   *  01312cf8   . 53             push ebx
   *  01312cf9   . 56             push esi
   *  01312cfa   . 57             push edi
   *  01312cfb   . a1 24673c01    mov eax,dword ptr ds:[0x13c6724]
   *  01312d00   . 33c4           xor eax,esp
   *  01312d02   . 50             push eax
   *  01312d03   . 8d8424 4809000>lea eax,dword ptr ss:[esp+0x948]
   *  01312d0a   . 64:a3 00000000 mov dword ptr fs:[0],eax
   *  01312d10   . 8b45 08        mov eax,dword ptr ss:[ebp+0x8]
   *  01312d13   . 8b7d 0c        mov edi,dword ptr ss:[ebp+0xc]
   *  01312d16   . 8b5d 30        mov ebx,dword ptr ss:[ebp+0x30]
   *  01312d19   . 898424 8800000>mov dword ptr ss:[esp+0x88],eax
   *  01312d20   . 8b45 14        mov eax,dword ptr ss:[ebp+0x14]
   *  01312d23   . 898c24 8c00000>mov dword ptr ss:[esp+0x8c],ecx
   *  01312d2a   . 8b0d a8734a01  mov ecx,dword ptr ds:[0x14a73a8]
   *  01312d30   . 894424 4c      mov dword ptr ss:[esp+0x4c],eax
   *  01312d34   . 899424 bc00000>mov dword ptr ss:[esp+0xbc],edx
   *  01312d3b   . 8b55 20        mov edx,dword ptr ss:[ebp+0x20]
   *  01312d3e   . 51             push ecx                                 ; /arg1 => 00000000
   *  01312d3f   . 8d8424 0c02000>lea eax,dword ptr ss:[esp+0x20c]         ; |
   *  01312d46   . 897c24 34      mov dword ptr ss:[esp+0x34],edi          ; |
   *  01312d4a   . 899c24 8800000>mov dword ptr ss:[esp+0x88],ebx          ; |
   *  01312d51   . e8 ca59fdff    call 蒼の彼方.012e8720                       ; \蒼の彼方.012e8720
   *  01312d56   . 33c9           xor ecx,ecx
   *  01312d58   . 898424 f400000>mov dword ptr ss:[esp+0xf4],eax
   *  01312d5f   . 3bc1           cmp eax,ecx
   *  01312d61   . 0f84 391b0000  je 蒼の彼方.013148a0
   *  01312d67   . e8 54280000    call 蒼の彼方.013155c0
   *  01312d6c   . e8 7f2a0000    call 蒼の彼方.013157f0
   *  01312d71   . 898424 f800000>mov dword ptr ss:[esp+0xf8],eax
   *  01312d78   . 8a07           mov al,byte ptr ds:[edi]
   *  01312d7a   . 898c24 c400000>mov dword ptr ss:[esp+0xc4],ecx
   *  01312d81   . 894c24 2c      mov dword ptr ss:[esp+0x2c],ecx
   *  01312d85   . 894c24 1c      mov dword ptr ss:[esp+0x1c],ecx
   *  01312d89   . b9 01000000    mov ecx,0x1
   *  01312d8e   . 3c 20          cmp al,0x20     ; jichi: pattern starts
   *  01312d90   . 7d 58          jge short 蒼の彼方.01312dea
   *  01312d92   . 0fbec0         movsx eax,al
   *  01312d95   . 83c0 fe        add eax,-0x2                             ;  switch (cases 2..8)
   *  01312d98   . 83f8 06        cmp eax,0x6
   *  01312d9b   . 77 4d          ja short 蒼の彼方.01312dea
   *  01312d9d   . ff2485 c448310>jmp dword ptr ds:[eax*4+0x13148c4]
   *  01312da4   > 898c24 c400000>mov dword ptr ss:[esp+0xc4],ecx          ;  case 2 of switch 01312d95
   *  01312dab   . 03f9           add edi,ecx
   *  01312dad   . eb 37          jmp short 蒼の彼方.01312de6
   *  01312daf   > 894c24 2c      mov dword ptr ss:[esp+0x2c],ecx          ;  case 3 of switch 01312d95
   *  01312db3   . 03f9           add edi,ecx
   *  01312db5   . eb 2f          jmp short 蒼の彼方.01312de6
   *  01312db7   > ba e0103b01    mov edx,蒼の彼方.013b10e0                    ;  case 4 of switch 01312d95
   *  01312dbc   . eb 1a          jmp short 蒼の彼方.01312dd8
   *  01312dbe   > ba e4103b01    mov edx,蒼の彼方.013b10e4                    ;  case 5 of switch 01312d95
   *  01312dc3   . eb 13          jmp short 蒼の彼方.01312dd8
   *  01312dc5   > ba e8103b01    mov edx,蒼の彼方.013b10e8                    ;  case 6 of switch 01312d95
   *  01312dca   . eb 0c          jmp short 蒼の彼方.01312dd8
   *  01312dcc   > ba ec103b01    mov edx,蒼の彼方.013b10ec                    ;  case 7 of switch 01312d95
   *  01312dd1   . eb 05          jmp short 蒼の彼方.01312dd8
   *  01312dd3   > ba f0103b01    mov edx,蒼の彼方.013b10f0                    ;  case 8 of switch 01312d95
   *  01312dd8   > 8d7424 14      lea esi,dword ptr ss:[esp+0x14]
   *  01312ddc   . 894c24 1c      mov dword ptr ss:[esp+0x1c],ecx
   *  01312de0   . e8 1b8dffff    call 蒼の彼方.0130bb00
   *  01312de5   . 47             inc edi
   *  01312de6   > 897c24 30      mov dword ptr ss:[esp+0x30],edi
   *  01312dea   > 8d8424 0802000>lea eax,dword ptr ss:[esp+0x208]         ;  default case of switch 01312d95
   *  01312df1   . e8 ba1b0000    call 蒼の彼方.013149b0
   *  01312df6   . 837d 10 00     cmp dword ptr ss:[ebp+0x10],0x0
   *  01312dfa   . 8bb424 2802000>mov esi,dword ptr ss:[esp+0x228]
   *  01312e01   . 894424 5c      mov dword ptr ss:[esp+0x5c],eax
   *  01312e05   . 74 12          je short 蒼の彼方.01312e19
   *  01312e07   . 56             push esi                                 ; /arg1
   *  01312e08   . e8 c31b0000    call 蒼の彼方.013149d0                       ; \蒼の彼方.013149d0
   *  01312e0d   . 83c4 04        add esp,0x4
   *  01312e10   . 898424 c000000>mov dword ptr ss:[esp+0xc0],eax
   *  01312e17   . eb 0b          jmp short 蒼の彼方.01312e24
   *  01312e19   > c78424 c000000>mov dword ptr ss:[esp+0xc0],0x0
   *  01312e24   > 8b4b 04        mov ecx,dword ptr ds:[ebx+0x4]
   *  01312e27   . 0fafce         imul ecx,esi
   *  01312e2a   . b8 1f85eb51    mov eax,0x51eb851f
   *  01312e2f   . f7e9           imul ecx
   *  01312e31   . c1fa 05        sar edx,0x5
   *  01312e34   . 8bca           mov ecx,edx
   *  01312e36   . c1e9 1f        shr ecx,0x1f
   *  01312e39   . 03ca           add ecx,edx
   *  01312e3b   . 894c24 70      mov dword ptr ss:[esp+0x70],ecx
   *  01312e3f   . 85c9           test ecx,ecx
   *  01312e41   . 7f 09          jg short 蒼の彼方.01312e4c
   *  01312e43   . b9 01000000    mov ecx,0x1
   *  01312e48   . 894c24 70      mov dword ptr ss:[esp+0x70],ecx
   *  01312e4c   > 8b53 08        mov edx,dword ptr ds:[ebx+0x8]
   *  01312e4f   . 0fafd6         imul edx,esi
   *  01312e52   . b8 1f85eb51    mov eax,0x51eb851f
   *  01312e57   . f7ea           imul edx
   *  01312e59   . c1fa 05        sar edx,0x5
   *  01312e5c   . 8bc2           mov eax,edx
   *  01312e5e   . c1e8 1f        shr eax,0x1f
   *  01312e61   . 03c2           add eax,edx
   *  01312e63   . 894424 78      mov dword ptr ss:[esp+0x78],eax
   *  01312e67   . 85c0           test eax,eax
   *  01312e69   . 7f 09          jg short 蒼の彼方.01312e74
   *  01312e6b   . b8 01000000    mov eax,0x1
   *  01312e70   . 894424 78      mov dword ptr ss:[esp+0x78],eax
   *  01312e74   > 33d2           xor edx,edx
   *  01312e76   . 895424 64      mov dword ptr ss:[esp+0x64],edx
   *  01312e7a   . 895424 6c      mov dword ptr ss:[esp+0x6c],edx
   *  01312e7e   . 8b13           mov edx,dword ptr ds:[ebx]
   *  01312e80   . 4a             dec edx                                  ;  switch (cases 1..2)
   *  01312e81   . 74 0e          je short 蒼の彼方.01312e91
   *  01312e83   . 4a             dec edx
   *  01312e84   . 75 13          jnz short 蒼の彼方.01312e99
   *  01312e86   . 8d1409         lea edx,dword ptr ds:[ecx+ecx]           ;  case 2 of switch 01312e80
   *  01312e89   . 895424 64      mov dword ptr ss:[esp+0x64],edx
   *  01312e8d   . 03c0           add eax,eax
   *  01312e8f   . eb 04          jmp short 蒼の彼方.01312e95
   *  01312e91   > 894c24 64      mov dword ptr ss:[esp+0x64],ecx          ;  case 1 of switch 01312e80
   *  01312e95   > 894424 6c      mov dword ptr ss:[esp+0x6c],eax
   *  01312e99   > 8b9c24 3802000>mov ebx,dword ptr ss:[esp+0x238]         ;  default case of switch 01312e80
   *  01312ea0   . 8bc3           mov eax,ebx
   *  01312ea2   . e8 d98bffff    call 蒼の彼方.0130ba80
   *  01312ea7   . 8bc8           mov ecx,eax
   *  01312ea9   . 8bc3           mov eax,ebx
   *  01312eab   . e8 e08bffff    call 蒼の彼方.0130ba90
   *  01312eb0   . 6a 01          push 0x1                                 ; /arg1 = 00000001
   *  01312eb2   . 8bd0           mov edx,eax                              ; |
   *  01312eb4   . 8db424 1c01000>lea esi,dword ptr ss:[esp+0x11c]         ; |
   *  01312ebb   . e8 3056fdff    call 蒼の彼方.012e84f0                       ; \蒼の彼方.012e84f0
   *  01312ec0   . 8bc7           mov eax,edi
   *  01312ec2   . 83c4 04        add esp,0x4
   *  01312ec5   . 8d70 01        lea esi,dword ptr ds:[eax+0x1]
   *  01312ec8   > 8a08           mov cl,byte ptr ds:[eax]
   *  01312eca   . 40             inc eax
   *  01312ecb   . 84c9           test cl,cl
   *  01312ecd   .^75 f9          jnz short 蒼の彼方.01312ec8
   *  01312ecf   . 2bc6           sub eax,esi
   *  01312ed1   . 40             inc eax
   *  01312ed2   . 50             push eax
   *  01312ed3   . e8 e74c0600    call 蒼の彼方.01377bbf
   *  01312ed8   . 33f6           xor esi,esi
   *  01312eda   . 83c4 04        add esp,0x4
   */
  ulong search3(ulong startAddress, ulong stopAddress)
  {
    //return startAddress + 0x31850; // 世界と世界の真ん中 体験版
    const uint8_t bytes[] = { // 3c207d580fbec083c0fe83f806774d
      0x3c, 0x20,       // 01312d8e   3c 20          cmp al,0x20     ; jichi: pattern starts
      0x7d, 0x58,       // 01312d90   7d 58          jge short 蒼の彼方.01312dea
      0x0f,0xbe,0xc0,   // 01312d92   0fbec0         movsx eax,al
      0x83,0xc0, 0xfe,  // 01312d95   83c0 fe        add eax,-0x2                             ;  switch (cases 2..8)
      0x83,0xf8, 0x06,  // 01312d98   83f8 06        cmp eax,0x6
      0x77, 0x4d        // 01312d9b   77 4d          ja short 蒼の彼方.01312dea
    };
    ulong addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
    if (!addr)
      return 0;

    // distance to the beginning of the function
    static const int hook_offsets[] = {
      0x01312cd0 - 0x01312d8e    // for new BGI2 game since 蒼の彼方 (2014/08), text is in arg2
      , 0x00a64260 - 0x00a64318  // For newer BGI2 game since コドモノアソビ (2015/11)
    };
    enum { hook_offset_count = sizeof(hook_offsets) / sizeof(*hook_offsets) };

    for (size_t i = 0; i < hook_offset_count; i++) {
      int hook_offset = hook_offsets[i];

      enum : uint8_t { push_ebp = 0x55 };  // 011d4c80  /$ 55             push ebp
      if (*(uint8_t *)(addr + hook_offset) == push_ebp)
        return addr + hook_offset;
    }
    return 0; // failed
  }

} // namespace Private

// BGI2 pattern also exists in BGI1
bool attach()
{
  ulong startAddress, stopAddress;
  if (!Engine::getProcessMemoryRange(&startAddress, &stopAddress))
    return false;
  ulong addr = Private::search3(startAddress, stopAddress);
  if (addr) {
    Private::type_ = Private::Type3;
    Private::textIndex_ = 2; // use arg2, name = "BGI2";
  } else if (addr = Private::search2(startAddress, stopAddress)) {
    Private::type_ = Private::Type2;
    Private::textIndex_ = 3; // use arg3, name = "BGI2";
  } else if (addr = Private::search1(startAddress, stopAddress)) {
    Private::type_ = Private::Type1;
    Private::textIndex_ = 3; // use arg3, name = "BGI";
  } else
    return false;
  if (!winhook::hook_before(addr, Private::hookBefore))
    return false;
  DOUT("type =" << Private::type_);
  return true;
}
} // namespace ScenarioHook
} // unnamed namespace

bool BGIEngine::attach()
{
  if (!ScenarioHook::attach())
    return false;
  HijackManager::instance()->attachFunction((ulong)::TextOutA);
  return true;
}

/**
 *  Example: <rここ>空港</r>
 *  http://sakuradite.com/topic/965
 */
QString BGIEngine::rubyCreate(const QString &rb, const QString &rt)
{
  static QString fmt = "<r%2>%1</r>";
  return fmt.arg(rb, rt);
}

// Remove furigana in scenario thread.
QString BGIEngine::rubyRemove(const QString &text)
{
  // It could be either <R..> or <r..>
  if (!text.contains("</r>", Qt::CaseInsensitive))
    return text;
  static QRegExp rx("<r.+>(.+)</r>", Qt::CaseInsensitive);
  if (!rx.isMinimal())
    rx.setMinimal(true);
  return QString(text).replace(rx, "\\1");
}

// EOF
