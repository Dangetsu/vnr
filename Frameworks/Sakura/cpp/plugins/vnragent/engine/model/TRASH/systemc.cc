// systemc.cc
// 6/30/2015 jichi
#include "engine/model/systemc.h"
#include "engine/enginecontroller.h"
#include "engine/enginedef.h"
#include "engine/enginehash.h"
#include "engine/engineutil.h"
#include "hijack/hijackmanager.h"
#include "memdbg/memsearch.h"
#include "winhook/hookcode.h"
#include <qt_windows.h>

#define DEBUG "systemc"
#include "sakurakit/skdebug.h"

/** Private data */

namespace { // unnamed

namespace ScenarioHook2 { // game process name is not SystemC for new CandySoft games, where text is in arg1

namespace Private {

  /**
   */
  bool hookBefore(winhook::hook_stack *s)
  {
    enum { role = Engine::ScenarioRole };
    auto text = (LPSTR)s->stack[1]; // arg1
    if (!text || !*text)
      return true;
    QByteArray data = EngineController::instance()->dispatchTextA(text, role);
    //::strcpy(text, data.constData());
    //s->stack[1] = (ulong)data_.constData(); // reset arg1
    return true;
  }

  ulong findFunction(ulong startAddress, ulong stopAddress)
  {
    for (DWORD i = startAddress + 0x1000; i < stopAddress - 4 ;i++) // 4 = sizeof(DWORD)
      if (*(WORD *)i == 0x5b3c || // cmp al,0x5b
          (*(DWORD *)i & 0xfff8fc) == 0x5bf880) // cmp reg,0x5B
        for (DWORD j = i, k = i - 0x100; j > k; j--) // backtrack to find beginning of the function
          if ((*(DWORD *)j & 0xffff) == 0x8b55) // push ebp, mov ebp,esp, sub esp,*
            return j;
    return 0;
  }

} // namespace Private

/**
 *  Process name is not SystemC.exe for new CandySoft games.
 *
 *  Sample game: 愛妹恋愛
 *
 *  00422E5D   CC               INT3
 *  00422E5E   CC               INT3
 *  00422E5F   CC               INT3
 *  00422E60   55               PUSH EBP
 *  00422E61   8BEC             MOV EBP,ESP
 *  00422E63   56               PUSH ESI
 *  00422E64   8B75 08          MOV ESI,DWORD PTR SS:[EBP+0x8]
 *  00422E67   85F6             TEST ESI,ESI
 *  00422E69   75 05            JNZ SHORT .00422E70
 *  00422E6B   33C0             XOR EAX,EAX
 *  00422E6D   5E               POP ESI
 *  00422E6E   5D               POP EBP
 *  00422E6F   C3               RETN
 *  00422E70   8BC6             MOV EAX,ESI
 *  00422E72   8D50 01          LEA EDX,DWORD PTR DS:[EAX+0x1]
 *  00422E75   8A08             MOV CL,BYTE PTR DS:[EAX]
 *  00422E77   40               INC EAX
 *  00422E78   84C9             TEST CL,CL
 *  00422E7A  ^75 F9            JNZ SHORT .00422E75
 *  00422E7C   2BC2             SUB EAX,EDX
 *  00422E7E   75 05            JNZ SHORT .00422E85
 *  00422E80   8BC6             MOV EAX,ESI
 *  00422E82   5E               POP ESI
 *  00422E83   5D               POP EBP
 *  00422E84   C3               RETN
 *  00422E85   53               PUSH EBX
 *  00422E86   40               INC EAX
 *  00422E87   57               PUSH EDI
 *  00422E88   50               PUSH EAX
 *  00422E89   E8 1B1D0300      CALL .00454BA9
 *  00422E8E   8BD8             MOV EBX,EAX
 *  00422E90   8BC6             MOV EAX,ESI
 *  00422E92   83C4 04          ADD ESP,0x4
 *  00422E95   8038 00          CMP BYTE PTR DS:[EAX],0x0
 *  00422E98   8BFB             MOV EDI,EBX
 *  00422E9A   74 65            JE SHORT .00422F01
 *  00422E9C   8D6424 00        LEA ESP,DWORD PTR SS:[ESP]
 *  00422EA0   0FBE0E           MOVSX ECX,BYTE PTR DS:[ESI]
 *  00422EA3   51               PUSH ECX
 *  00422EA4   E8 7B2A0300      CALL .00455924
 *  00422EA9   83C4 04          ADD ESP,0x4
 *  00422EAC   85C0             TEST EAX,EAX
 *  00422EAE   74 14            JE SHORT .00422EC4
 *  00422EB0   8A16             MOV DL,BYTE PTR DS:[ESI]
 *  00422EB2   8817             MOV BYTE PTR DS:[EDI],DL
 *  00422EB4   8A46 01          MOV AL,BYTE PTR DS:[ESI+0x1]
 *  00422EB7   47               INC EDI
 *  00422EB8   84C0             TEST AL,AL
 *  00422EBA   74 45            JE SHORT .00422F01
 *  00422EBC   8807             MOV BYTE PTR DS:[EDI],AL
 *  00422EBE   47               INC EDI
 *  00422EBF   83C6 02          ADD ESI,0x2
 *  00422EC2   EB 38            JMP SHORT .00422EFC
 *  00422EC4   8A06             MOV AL,BYTE PTR DS:[ESI]
 *  00422EC6   3C 5B            CMP AL,0x5B     ; jichi: instruction pattern
 *  00422EC8   75 2E            JNZ SHORT .00422EF8
 *  00422ECA   8D9B 00000000    LEA EBX,DWORD PTR DS:[EBX]
 *  00422ED0   0FBE46 01        MOVSX EAX,BYTE PTR DS:[ESI+0x1]
 *  00422ED4   46               INC ESI
 *  00422ED5   50               PUSH EAX
 *  00422ED6   E8 492A0300      CALL .00455924
 *  00422EDB   83C4 04          ADD ESP,0x4
 *  00422EDE   85C0             TEST EAX,EAX
 *  00422EE0   74 03            JE SHORT .00422EE5
 *  00422EE2   46               INC ESI
 *  00422EE3   EB 05            JMP SHORT .00422EEA
 *  00422EE5   803E 5D          CMP BYTE PTR DS:[ESI],0x5D
 *  00422EE8   74 07            JE SHORT .00422EF1
 *  00422EEA   803E 00          CMP BYTE PTR DS:[ESI],0x0
 *  00422EED  ^75 E1            JNZ SHORT .00422ED0
 *  00422EEF   EB 10            JMP SHORT .00422F01
 *  00422EF1   803E 00          CMP BYTE PTR DS:[ESI],0x0
 *  00422EF4   74 0B            JE SHORT .00422F01
 *  00422EF6   EB 03            JMP SHORT .00422EFB
 *  00422EF8   8807             MOV BYTE PTR DS:[EDI],AL
 *  00422EFA   47               INC EDI
 *  00422EFB   46               INC ESI
 *  00422EFC   803E 00          CMP BYTE PTR DS:[ESI],0x0
 *  00422EFF  ^75 9F            JNZ SHORT .00422EA0
 *  00422F01   8B55 08          MOV EDX,DWORD PTR SS:[EBP+0x8]
 *  00422F04   C607 00          MOV BYTE PTR DS:[EDI],0x0
 *  00422F07   8BC3             MOV EAX,EBX
 *  00422F09   2BD3             SUB EDX,EBX
 *  00422F0B   EB 03            JMP SHORT .00422F10
 *  00422F0D   8D49 00          LEA ECX,DWORD PTR DS:[ECX]
 *  00422F10   8A08             MOV CL,BYTE PTR DS:[EAX]
 *  00422F12   880C02           MOV BYTE PTR DS:[EDX+EAX],CL
 *  00422F15   40               INC EAX
 *  00422F16   84C9             TEST CL,CL
 *  00422F18  ^75 F6            JNZ SHORT .00422F10
 *  00422F1A   53               PUSH EBX
 *  00422F1B   E8 3D2A0300      CALL .0045595D
 *  00422F20   8B45 08          MOV EAX,DWORD PTR SS:[EBP+0x8]
 *  00422F23   83C4 04          ADD ESP,0x4
 *  00422F26   5F               POP EDI
 *  00422F27   5B               POP EBX
 *  00422F28   5E               POP ESI
 *  00422F29   5D               POP EBP
 *  00422F2A   C3               RETN
 *  00422F2B   CC               INT3
 *  00422F2C   CC               INT3
 */
bool attach(ulong startAddress, ulong stopAddress)
{
  ulong addr = Private::findFunction(startAddress, stopAddress);
  if (!addr)
    return false;
  return winhook::hook_before(addr, Private::hookBefore);
}

} // namespace ScenarioHook2

} // unnamed namespace


/** Public class */

bool SystemCEngine::attach()
{
  ulong startAddress, stopAddress;
  if (!Engine::getProcessMemoryRange(&startAddress, &stopAddress))
    return 0;
  if (!ScenarioHook2::attach(startAddress, stopAddress))
    return false;
  return true;
  //if (Engine::exists("SystemC.exe"))
  //  return ScenarioHook1::attach();
  //return ScenarioHook2::attach() || ScenarioHook1::attach();
}

// EOF

/*

// Process name is "SystemC.exe"
bool InsertCandyHook1()
{
  for (DWORD i = module_base_ + 0x1000; i < module_limit_ - 4; i++)
    if ((*(DWORD *)i&0xffffff) == 0x24f980) // cmp cl,24
      for (DWORD j = i, k = i - 0x100; j > k; j--)
        if (*(DWORD *)j == 0xc0330a8a) { // mov cl,[edx]; xor eax,eax
          HookParam hp = {};
          hp.address = j;
          hp.offset = -0x10;    // jichi: text in ecx
          hp.type = USING_STRING;
          ConsoleOutput("vnreng: INSERT SystemC#1");
          NewHook(hp, L"SystemC");
          //RegisterEngineType(ENGINE_CANDY);
          return true;
        }
  ConsoleOutput("vnreng:CandyHook1: failed");
  return false;
}
*/
