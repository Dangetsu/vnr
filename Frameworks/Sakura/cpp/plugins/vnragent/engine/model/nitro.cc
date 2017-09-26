// nitro.cc
// 11/22/2014 jichi
#include "engine/model/nitro.h"
#include "engine/enginecontroller.h"
#include "engine/enginedef.h"
#include "engine/engineutil.h"
#include "util/textutil.h"
#include "memdbg/memsearch.h"
#include "winhook/hookcode.h"
#include "winhook/hookfun.h"
#include <qt_windows.h>
#include <cstdint>

#define DEBUG "model/nitro"
#include "sakurakit/skdebug.h"

namespace { // unnamed
namespace ScenarioHook {
namespace Private {
  /**
   *  Sample game: 凍京NECRO 体験版
   *  Text in arg1.
   */
  bool hookBefore(winhook::hook_stack *s)
  {
    static QByteArray data_; // persistent storage, which makes this function not thread-safe

    // All threads including character names are linked together
    enum { role = Engine::ScenarioRole, sig = 0 };

    LPCSTR text = (LPCSTR)s->stack[1]; // arg1

    // There is no system text hook.
    // But still skip English message.
    if (!text || !*text || Util::allAscii(text))
      return true;

    data_ = EngineController::instance()->dispatchTextA(text, role, sig);
    s->stack[1] = (ulong)data_.constData(); // arg2
    return true;
  }

} // namespace Private

/**
 *  Sample game: 凍京NECRO 体験版
 *  Debug step:
 *  1. find the text location that does not change
 *  2. Use Ollydbg to find where the text is modified
 *  3. Backtrack the stack to find proper caller.
 *
 *   Issues: It cannot extract character name.
 *
 *  File pattern: *.npk for new "Nitroplus" (p is lower case)
 *  btw, *.npa for old "Nitroplus"
 *
 *  00CF0E6A   CC               INT3
 *  00CF0E6B   CC               INT3
 *  00CF0E6C   CC               INT3
 *  00CF0E6D   CC               INT3
 *  00CF0E6E   CC               INT3
 *  00CF0E6F   CC               INT3
 *  00CF0E70   55               PUSH EBP	; jichi: text in arg1
 *  00CF0E71   8BEC             MOV EBP,ESP
 *  00CF0E73   6A FF            PUSH -0x1
 *  00CF0E75   68 184BDC00      PUSH .00DC4B18
 *  00CF0E7A   64:A1 00000000   MOV EAX,DWORD PTR FS:[0]
 *  00CF0E80   50               PUSH EAX
 *  00CF0E81   64:8925 00000000 MOV DWORD PTR FS:[0],ESP
 *  00CF0E88   83EC 1C          SUB ESP,0x1C
 *  00CF0E8B   8B55 08          MOV EDX,DWORD PTR SS:[EBP+0x8]
 *  00CF0E8E   53               PUSH EBX
 *  00CF0E8F   56               PUSH ESI
 *  00CF0E90   8BC2             MOV EAX,EDX
 *  00CF0E92   57               PUSH EDI
 *  00CF0E93   8BD9             MOV EBX,ECX
 *  00CF0E95   C745 EC 0F000000 MOV DWORD PTR SS:[EBP-0x14],0xF
 *  00CF0E9C   C745 E8 00000000 MOV DWORD PTR SS:[EBP-0x18],0x0
 *  00CF0EA3   C645 D8 00       MOV BYTE PTR SS:[EBP-0x28],0x0
 *  00CF0EA7   8D70 01          LEA ESI,DWORD PTR DS:[EAX+0x1]
 *  00CF0EAA   8D9B 00000000    LEA EBX,DWORD PTR DS:[EBX]
 *  00CF0EB0   8A08             MOV CL,BYTE PTR DS:[EAX]
 *  00CF0EB2   40               INC EAX
 *  00CF0EB3   84C9             TEST CL,CL
 *  00CF0EB5  ^75 F9            JNZ SHORT .00CF0EB0
 *  00CF0EB7   2BC6             SUB EAX,ESI
 *  00CF0EB9   52               PUSH EDX
 *  00CF0EBA   8BF8             MOV EDI,EAX
 *  00CF0EBC   8D75 D8          LEA ESI,DWORD PTR SS:[EBP-0x28]
 *  00CF0EBF   E8 0C0DF5FF      CALL .00C41BD0
 *  00CF0EC4   C745 FC 00000000 MOV DWORD PTR SS:[EBP-0x4],0x0	; jichi: pattern start
 *  00CF0ECB   8B8B 84030000    MOV ECX,DWORD PTR DS:[EBX+0x384]
 *  00CF0ED1   8B01             MOV EAX,DWORD PTR DS:[ECX]
 *  00CF0ED3   8B40 60          MOV EAX,DWORD PTR DS:[EAX+0x60]
 *  00CF0ED6   8BD6             MOV EDX,ESI
 *  00CF0ED8   52               PUSH EDX
 *  00CF0ED9   FFD0             CALL EAX   ;jichi: called here  .00CAEF00
 *  00CF0EDB   837D EC 10       CMP DWORD PTR SS:[EBP-0x14],0x10
 *  00CF0EDF   5F               POP EDI
 *  00CF0EE0   5E               POP ESI
 *  00CF0EE1   5B               POP EBX
 *  00CF0EE2   72 0C            JB SHORT .00CF0EF0
 *  00CF0EE4   8B4D D8          MOV ECX,DWORD PTR SS:[EBP-0x28]
 *  00CF0EE7   51               PUSH ECX
 *  00CF0EE8   E8 ED060B00      CALL .00DA15DA
 *  00CF0EED   83C4 04          ADD ESP,0x4
 *  00CF0EF0   8B4D F4          MOV ECX,DWORD PTR SS:[EBP-0xC]
 *  00CF0EF3   64:890D 00000000 MOV DWORD PTR FS:[0],ECX
 *  00CF0EFA   8BE5             MOV ESP,EBP
 *  00CF0EFC   5D               POP EBP
 *  00CF0EFD   C2 0400          RETN 0x4
 *  00CF0F00   8B89 84030000    MOV ECX,DWORD PTR DS:[ECX+0x384]
 *  00CF0F06   8B01             MOV EAX,DWORD PTR DS:[ECX]
 *  00CF0F08   8B50 64          MOV EDX,DWORD PTR DS:[EAX+0x64]
 *  00CF0F0B   FFE2             JMP EDX
 *  00CF0F0D   CC               INT3
 *  00CF0F0E   CC               INT3
 *  00CF0F0F   CC               INT3
 *  00CF0F10   55               PUSH EBP
 *  00CF0F11   8BEC             MOV EBP,ESP
 *  00CF0F13   83EC 10          SUB ESP,0x10
 *  00CF0F16   8B89 84030000    MOV ECX,DWORD PTR DS:[ECX+0x384]
 *  00CF0F1C   8B01             MOV EAX,DWORD PTR DS:[ECX]
 *  00CF0F1E   8B80 A0000000    MOV EAX,DWORD PTR DS:[EAX+0xA0]
 *  00CF0F24   8D55 F0          LEA EDX,DWORD PTR SS:[EBP-0x10]
 *  00CF0F27   52               PUSH EDX
 *  00CF0F28   FFD0             CALL EAX
 *  00CF0F2A   8D4D F8          LEA ECX,DWORD PTR SS:[EBP-0x8]
 *  00CF0F2D   FF15 7482DC00    CALL DWORD PTR DS:[0xDC8274]                                                          ; _1nput1_.1007E880
 *  00CF0F33   66:0F6E45 F0     MOVD MM0,DWORD PTR SS:[EBP-0x10]
 *  00CF0F38   66:0F6E4D F4     MOVD MM1,DWORD PTR SS:[EBP-0xC]
 *  00CF0F3D   8B0D E046E000    MOV ECX,DWORD PTR DS:[0xE046E0]
 *  00CF0F43   0F5B             ???                                                                                   ; Unknown command
 *  00CF0F45   C0F3 0F          SAL BL,0xF
 *  00CF0F48   1145 F8          ADC DWORD PTR SS:[EBP-0x8],EAX
 *  00CF0F4B   0F5B             ???                                                                                   ; Unknown command
 *  00CF0F4D   C9               LEAVE
 *  00CF0F4E   F3:0F114D FC     MOVSS DWORD PTR SS:[EBP-0x4],XMM1
 *  00CF0F53   8B41 54          MOV EAX,DWORD PTR DS:[ECX+0x54]
 *  00CF0F56   F3:0F1180 500100>MOVSS DWORD PTR DS:[EAX+0x150],XMM0
 *  00CF0F5E   F3:0F1045 FC     MOVSS XMM0,DWORD PTR SS:[EBP-0x4]
 *  00CF0F63   F3:0F1180 540100>MOVSS DWORD PTR DS:[EAX+0x154],XMM0
 *  00CF0F6B   0F57C0           XORPS XMM0,XMM0
 *  00CF0F6E   F3:0F1180 580100>MOVSS DWORD PTR DS:[EAX+0x158],XMM0
 *  00CF0F76   F3:0F1180 5C0100>MOVSS DWORD PTR DS:[EAX+0x15C],XMM0
 *  00CF0F7E   8BE5             MOV ESP,EBP
 *  00CF0F80   5D               POP EBP
 *  00CF0F81   C3               RETN
 *  00CF0F82   CC               INT3
 *  00CF0F83   CC               INT3
 *  00CF0F84   CC               INT3
 *  00CF0F85   CC               INT3
 *  00CF0F86   CC               INT3
 *  00CF0F87   CC               INT3
 *  00CF0F88   CC               INT3
 *  00CF0F89   CC               INT3
 *  00CF0F8A   CC               INT3
 *  00CF0F8B   CC               INT3
 *  00CF0F8C   CC               INT3
 *
 *  If the function does not work, here's the common function that performing strcpy
 *  00DA8E8A   CC               INT3
 *  00DA8E8B   CC               INT3
 *  00DA8E8C   CC               INT3
 *  00DA8E8D   CC               INT3
 *  00DA8E8E   CC               INT3
 *  00DA8E8F   CC               INT3
 *  00DA8E90   55               PUSH EBP
 *  00DA8E91   8BEC             MOV EBP,ESP
 *  00DA8E93   57               PUSH EDI
 *  00DA8E94   56               PUSH ESI
 *  00DA8E95   8B75 0C          MOV ESI,DWORD PTR SS:[EBP+0xC]
 *  00DA8E98   8B4D 10          MOV ECX,DWORD PTR SS:[EBP+0x10]
 *  00DA8E9B   8B7D 08          MOV EDI,DWORD PTR SS:[EBP+0x8]
 *  00DA8E9E   8BC1             MOV EAX,ECX
 *  00DA8EA0   8BD1             MOV EDX,ECX
 *  00DA8EA2   03C6             ADD EAX,ESI
 *  00DA8EA4   3BFE             CMP EDI,ESI
 *  00DA8EA6   76 08            JBE SHORT .00DA8EB0
 *  00DA8EA8   3BF8             CMP EDI,EAX
 *  00DA8EAA   0F82 A0010000    JB .00DA9050
 *  00DA8EB0   81F9 80000000    CMP ECX,0x80
 *  00DA8EB6   72 1C            JB SHORT .00DA8ED4
 *  00DA8EB8   833D D470E000 00 CMP DWORD PTR DS:[0xE070D4],0x0
 *  00DA8EBF   74 13            JE SHORT .00DA8ED4
 *  00DA8EC1   57               PUSH EDI
 *  00DA8EC2   56               PUSH ESI
 *  00DA8EC3   83E7 0F          AND EDI,0xF
 *  00DA8EC6   83E6 0F          AND ESI,0xF
 *  00DA8EC9   3BFE             CMP EDI,ESI
 *  00DA8ECB   5E               POP ESI
 *  00DA8ECC   5F               POP EDI
 *  00DA8ECD   75 05            JNZ SHORT .00DA8ED4
 *  00DA8ECF  ^E9 0E9FFFFF      JMP .00DA2DE2
 *  00DA8ED4   F7C7 03000000    TEST EDI,0x3
 *  00DA8EDA   75 14            JNZ SHORT .00DA8EF0
 *  00DA8EDC   C1E9 02          SHR ECX,0x2
 *  00DA8EDF   83E2 03          AND EDX,0x3
 *  00DA8EE2   83F9 08          CMP ECX,0x8
 *  00DA8EE5   72 29            JB SHORT .00DA8F10
 *  00DA8EE7   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS:[ESI]	; jichi: modified here
 *  00DA8EE9   FF2495 0090DA00  JMP DWORD PTR DS:[EDX*4+0xDA9000]
 *  00DA8EF0   8BC7             MOV EAX,EDI
 *  00DA8EF2   BA 03000000      MOV EDX,0x3
 *  00DA8EF7   83E9 04          SUB ECX,0x4
 *  00DA8EFA   72 0C            JB SHORT .00DA8F08
 *  00DA8EFC   83E0 03          AND EAX,0x3
 *  00DA8EFF   03C8             ADD ECX,EAX
 *  00DA8F01   FF2485 148FDA00  JMP DWORD PTR DS:[EAX*4+0xDA8F14]
 *  00DA8F08   FF248D 1090DA00  JMP DWORD PTR DS:[ECX*4+0xDA9010]
 *  00DA8F0F   90               NOP
 *  00DA8F10   FF248D 948FDA00  JMP DWORD PTR DS:[ECX*4+0xDA8F94]
 *  00DA8F17   90               NOP
 *  00DA8F18   24 8F            AND AL,0x8F
 *  00DA8F1A   DA00             FIADD DWORD PTR DS:[EAX]
 *  00DA8F1C   50               PUSH EAX
 *  00DA8F1D   8F               ???                                                                                   ; Unknown command
 *  00DA8F1E   DA00             FIADD DWORD PTR DS:[EAX]
 *  00DA8F20  ^74 8F            JE SHORT .00DA8EB1
 *  00DA8F22   DA00             FIADD DWORD PTR DS:[EAX]
 *  00DA8F24   23D1             AND EDX,ECX
 *  00DA8F26   8A06             MOV AL,BYTE PTR DS:[ESI]
 *  00DA8F28   8807             MOV BYTE PTR DS:[EDI],AL
 *  00DA8F2A   8A46 01          MOV AL,BYTE PTR DS:[ESI+0x1]
 *  00DA8F2D   8847 01          MOV BYTE PTR DS:[EDI+0x1],AL
 *  00DA8F30   8A46 02          MOV AL,BYTE PTR DS:[ESI+0x2]
 *  00DA8F33   C1E9 02          SHR ECX,0x2
 *  00DA8F36   8847 02          MOV BYTE PTR DS:[EDI+0x2],AL
 *  00DA8F39   83C6 03          ADD ESI,0x3
 *  00DA8F3C   83C7 03          ADD EDI,0x3
 *  00DA8F3F   83F9 08          CMP ECX,0x8
 *  00DA8F42  ^72 CC            JB SHORT .00DA8F10
 *  00DA8F44   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS:[ESI]
 *  00DA8F46   FF2495 0090DA00  JMP DWORD PTR DS:[EDX*4+0xDA9000]
 *  00DA8F4D   8D49 00          LEA ECX,DWORD PTR DS:[ECX]
 *  00DA8F50   23D1             AND EDX,ECX
 *  00DA8F52   8A06             MOV AL,BYTE PTR DS:[ESI]
 *  00DA8F54   8807             MOV BYTE PTR DS:[EDI],AL
 *  00DA8F56   8A46 01          MOV AL,BYTE PTR DS:[ESI+0x1]
 *  00DA8F59   C1E9 02          SHR ECX,0x2
 *  00DA8F5C   8847 01          MOV BYTE PTR DS:[EDI+0x1],AL
 *  00DA8F5F   83C6 02          ADD ESI,0x2
 *  00DA8F62   83C7 02          ADD EDI,0x2
 *  00DA8F65   83F9 08          CMP ECX,0x8
 *  00DA8F68  ^72 A6            JB SHORT .00DA8F10
 *  00DA8F6A   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS:[ESI]
 *  00DA8F6C   FF2495 0090DA00  JMP DWORD PTR DS:[EDX*4+0xDA9000]
 *  00DA8F73   90               NOP
 *  00DA8F74   23D1             AND EDX,ECX
 *  00DA8F76   8A06             MOV AL,BYTE PTR DS:[ESI]
 *  00DA8F78   8807             MOV BYTE PTR DS:[EDI],AL
 *  00DA8F7A   83C6 01          ADD ESI,0x1
 *  00DA8F7D   C1E9 02          SHR ECX,0x2
 *  00DA8F80   83C7 01          ADD EDI,0x1
 *  00DA8F83   83F9 08          CMP ECX,0x8
 *  00DA8F86  ^72 88            JB SHORT .00DA8F10
 *  00DA8F88   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS:[ESI]
 *  00DA8F8A   FF2495 0090DA00  JMP DWORD PTR DS:[EDX*4+0xDA9000]
 *  00DA8F91   8D49 00          LEA ECX,DWORD PTR DS:[ECX]
 *  00DA8F94   F7               ???                                                                                   ; Unknown command
 *  00DA8F95   8F               ???                                                                                   ; Unknown command
 *  00DA8F96   DA00             FIADD DWORD PTR DS:[EAX]
 *  00DA8F98   E4 8F            IN AL,0x8F                                                                            ; I/O command
 *  00DA8F9A   DA00             FIADD DWORD PTR DS:[EAX]
 *  00DA8F9C   DC8F DA00D48F    FMUL QWORD PTR DS:[EDI+0x8FD400DA]
 *  00DA8FA2   DA00             FIADD DWORD PTR DS:[EAX]
 *  00DA8FA4   CC               INT3
 *  00DA8FA5   8F               ???                                                                                   ; Unknown command
 *  00DA8FA6   DA00             FIADD DWORD PTR DS:[EAX]
 *  00DA8FA8   C48F DA00BC8F    LES ECX,FWORD PTR DS:[EDI+0x8FBC00DA]                                                 ; Modification of segment register
 *  00DA8FAE   DA00             FIADD DWORD PTR DS:[EAX]
 *  00DA8FB0   B4 8F            MOV AH,0x8F
 *
 */
bool attach(ulong startAddress, ulong stopAddress) // attach scenario
{
  const uint8_t bytes[] = {
    0xc7,0x45, 0xfc, 0x00,0x00,0x00,0x00, // 00cf0ec4   c745 fc 00000000 mov dword ptr ss:[ebp-0x4],0x0	; jichi: pattern start
    0x8b,0x8b, 0x84,0x03,0x00,0x00,       // 00cf0ecb   8b8b 84030000    mov ecx,dword ptr ds:[ebx+0x384]
    0x8b,0x01,                            // 00cf0ed1   8b01             mov eax,dword ptr ds:[ecx]
    0x8b,0x40, 0x60,                      // 00cf0ed3   8b40 60          mov eax,dword ptr ds:[eax+0x60]
    0x8b,0xd6,                            // 00cf0ed6   8bd6             mov edx,esi
    0x52,                                 // 00cf0ed8   52               push edx
    0xff,0xd0                             // 00cf0ed9   ffd0             call eax   ;jichi: called here  .00caef00
  };
  ulong addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  return winhook::hook_before(addr, Private::hookBefore);
}

} // namespace ScenarioHook
} // unnamed namespace

/** Public class */

bool NitroplusEngine::attach()
{
  ulong startAddress, stopAddress;
  if (!Engine::getProcessMemoryRange(&startAddress, &stopAddress))
    return false;
  if (!ScenarioHook::attach(startAddress, stopAddress))
    return false;
  // GDI text/font functions are not invoked at all
  //HijackManager::instance()->attachFunction((ulong)::CreateFontIndirectA);
  return true;
}

// EOF
