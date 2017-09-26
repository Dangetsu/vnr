// retouch.cc
// 6/20/2015 jichi
#include "engine/model/retouch.h"
#include "engine/enginecontroller.h"
#include "engine/enginedef.h"
#include "engine/enginehash.h"
#include "engine/engineutil.h"
#include "hijack/hijackmanager.h"
#include "memdbg/memsearch.h"
#include "disasm/disasm.h"
#include "winasm/winasmdef.h"
#include "winasm/winasmutil.h"
#include "winhook/hookcode.h"
#include "winhook/hookfun.h"
#include "winhook/hookcall.h"
#include <qt_windows.h>
#include <cstdint>

#define DEBUG "model/retouch"
#include "sakurakit/skdebug.h"

namespace { // unnamed
namespace ScenarioHook {
namespace Private {
  bool hookBefore(winhook::hook_stack *s)
  {
    static QByteArray data_; // persistent storage, which makes this function not thread-safe
    // All threads including character names are linked together
    LPCSTR text = (LPCSTR)s->stack[1]; // arg1
    auto role =
      s->eax == 0 ?  Engine::NameRole : Engine::ScenarioRole;
      //s->ebx == 0 ? Engine::ScenarioRole :
      //Engine::OtherRole; // ruby is not skipped
    auto split = s->stack[0]; // retaddr
    auto sig = Engine::hashThreadSignature(role, split);
    data_ = EngineController::instance()->dispatchTextA(text, role, sig);
    s->stack[1] = (ulong)data_.constData(); // arg1
    return true;
  }
} // namespace Private

/**
 *  Sample games:
 *  - らぶらぶプリンセス
 *  - 箱庭ロジック
 *  All two function entries exist.
 *
 *  ?printSub@RetouchPrintManager@@AAE_NPBDAAVUxPrintData@@K@Z
 *  - Scenario
 *  0653F7DC   05F5717A  RETURN to resident.05F5717A from resident.?printSub@RetouchPrintManager@@AAE_NPBDAAVUxPrintData@@K@Z
 *  0653F7E0   082E9D88 ; jichi: text here
 *  0653F7E4   0653F914
 *  0653F7E8   00000000
 *  0653F7EC   62100CB4
 *  0653F7F0   01575A68
 *  0653F7F4   00000003
 *  0653F7F8   01574F48
 *  0653F7FC   00000000
 *  0653F800   000000E7
 *  0653F804   0653F8F0
 *  0653F808   00000081
 *  0653F80C   01670000
 *  0653F810   08599530
 *  0653F814   0653F8F0
 *  0653F818   00000000
 *  0653F81C   00000000
 *  0653F820   00009530
 *  0653F824   00000000
 *  0653F828   E70000E7
 *  0653F82C   01670000
 *  0653F830   08599940
 *  0653F834   085F3FF8
 *  0653F838   08613340
 *  0653F83C   00000338
 *  0653F840   01670000
 *  0653F844   00000100
 *  0653F848   0C599530
 *  0653F84C   0653F93C
 *
 *  EAX 082E2A08
 *  ECX 01575A68
 *  EDX 0653F914
 *  EBX 00000000
 *  ESP 0653F7DC
 *  EBP 00000000
 *  ESI 01575A68
 *  EDI 00000000
 *  EIP 05F56EB0 resident.?printSub@RetouchPrintManager@@AAE_NPBDAAVUxPrintData@@K@Z
 *
 *  EAX 07FFF358
 *  ECX 01535C80
 *  EDX 08156FD8
 *  EBX 00000000
 *  ESP 0656F824
 *  EBP 00000015
 *  ESI 01535C80
 *  EDI 080BC520
 *  EIP 05C20650 resident.?printSub@RetouchPrintManager@@AAE_NPBDAAVUxPrintData@@K@Z
 *
 *  Name
 *  EAX 00000000 ; jichi: used as split
 *  ECX 01575A68
 *  EDX 0653F944
 *  EBX 00000000
 *  ESP 0653F7DC
 *  EBP 00000000
 *  ESI 01575A68
 *  EDI 08480A20
 *  EIP 05F56EB0 resident.?printSub@RetouchPrintManager@@AAE_NPBDAAVUxPrintData@@K@Z
 *
 *  Ruby surface
 *  EAX 07FFF670
 *  ECX 01535C80
 *  EDX 0656F95C
 *  EBX 00000000
 *  ESP 0656F824
 *  EBP 00000015
 *  ESI 01535C80
 *  EDI 08134B10
 *  EIP 05C20650 resident.?printSub@RetouchPrintManager@@AAE_NPBDAAVUxPrintData@@K@Z
 *
 *  Ruby text
 *  EAX 07FFF778
 *  ECX 01535C80
 *  EDX 00000000
 *  EBX 00000092
 *  ESP 0656F824
 *  EBP 00000015
 *  ESI 01535C80
 *  EDI 08134B10
 *  EIP 05C20650 resident.?printSub@RetouchPrintManager@@AAE_NPBDAAVUxPrintData@@K@Z
 *
 */
bool attach() // attach scenario
{
  // private: bool __thiscall RetouchPrintManager::printSub(char const *,class UxPrintData &,unsigned long)	0x10050650	0x00050650	2904 (0xb58)	resident.dll	C:\Local\箱庭ロジック\resident.dll	Exported Function
  const char *fun = "?printSub@RetouchPrintManager@@AAE_NPBDAAVUxPrintData@@K@Z";
  auto addr = Engine::getModuleFunction("resident.dll", fun);
  return addr && winhook::hook_before(addr, Private::hookBefore);
}
} // namespace ScenarioHook

namespace OtherHook {
namespace Private {
  bool hookBefore(winhook::hook_stack *s)
  {
    static QByteArray data_; // persistent storage, which makes this function not thread-safe
    // All threads including character names are linked together
    LPCSTR text = (LPCSTR)s->stack[1]; // arg1
    enum { role = Engine::OtherRole };
    auto split = s->stack[0]; // retaddr
    auto sig = Engine::hashThreadSignature(role, split);
    data_ = EngineController::instance()->dispatchTextA(text, role, sig);
    s->stack[1] = (ulong)data_.constData(); // arg1
    return true;
  }
} // namespace Private

bool attach() // attach scenario
{
  // private: void __thiscall RetouchPrintManager::printSub(char const *,unsigned long,int &,int &)	0x10046560	0x00046560	2902 (0xb56)	resident.dll	C:\Local\箱庭ロジック\resident.dll	Exported Function
  const char *fun = "?printSub@RetouchPrintManager@@AAEXPBDKAAH1@Z";
  auto addr = Engine::getModuleFunction("resident.dll", fun);
  return addr && winhook::hook_before(addr, Private::hookBefore);
}
} // namespace OtherHook

namespace HistoryHook {
namespace Private {
  bool hookBefore(winhook::hook_stack *s)
  {
    static QByteArray data_; // persistent storage, which makes this function not thread-safe
    // All threads including character names are linked together
    LPCSTR text = (LPCSTR)s->stack[1]; // arg1
    enum { role = Engine::HistoryRole };
    auto split = s->stack[0]; // retaddr
    auto sig = Engine::hashThreadSignature(role, split);
    data_ = EngineController::instance()->dispatchTextA(text, role, sig);
    s->stack[1] = (ulong)data_.constData(); // arg1
    return true;
  }
} // namespace Private

/**
 *  Sample game: 箱庭ロジック
 *
 *  Caller of the caller of the hijacked function:
 *  public: int __thiscall RetouchPrintManager::printHistory(class UxLayerSurface &,int &,int * const,int * const,int,bool,class scobjPrintArea &,class scobjPrintArea &,class std::map<int,int,struct std::less<int>,class std::allocator<struct std::pair<int const ,int> > > *)	0x10065260	0x00065260	2913 (0xb61)	resident.dll	C:\Local\Retouch\resident.dll	Exported Function
 *
 *  05005584   8B9424 28050000  MOV EDX,DWORD PTR SS:[ESP+0x528]
 *  0500558B   8B4A 14          MOV ECX,DWORD PTR DS:[EDX+0x14]
 *  0500558E   85C9             TEST ECX,ECX
 *  05005590   74 06            JE SHORT _1locke2.05005598
 *  05005592   50               PUSH EAX
 *  05005593   E8 489D1C00      CALL _1locke2.051CF2E0	; jichi: print history, text on eax
 *  05005598   8BAC24 24050000  MOV EBP,DWORD PTR SS:[ESP+0x524]
 *  0500559F   8B4D 14          MOV ECX,DWORD PTR SS:[EBP+0x14]
 *  050055A2   6A 00            PUSH 0x0
 *  050055A4   8D4424 2C        LEA EAX,DWORD PTR SS:[ESP+0x2C]
 *  050055A8   50               PUSH EAX
 *  050055A9   8D5424 74        LEA EDX,DWORD PTR SS:[ESP+0x74]
 *  050055AD   52               PUSH EDX
 *  050055AE   E8 FD2F1C00      CALL _1locke2.051C85B0
 *
 *  Intermediate call, which is used as instruction pattern, text on arg1:
 *  051CF2DE   CC               INT3
 *  051CF2DF   CC               INT3
 *  051CF2E0   8B4424 04        MOV EAX,DWORD PTR SS:[ESP+0x4]
 *  051CF2E4   6A 02            PUSH 0x2
 *  051CF2E6   6A 00            PUSH 0x0
 *  051CF2E8   6A 00            PUSH 0x0
 *  051CF2EA   6A 00            PUSH 0x0
 *  051CF2EC   50               PUSH EAX
 *  051CF2ED   E8 9EF8FFFF      CALL _1locke2.051CEB90
 *  051CF2F2   C2 0400          RETN 0x4
 *  051CF2F5   CC               INT3
 *
 *  Actual function that print history, text in arg1:
 *  051CEB8F   CC               INT3
 *  051CEB90   55               PUSH EBP
 *  051CEB91   8BEC             MOV EBP,ESP
 *  051CEB93   6A FF            PUSH -0x1
 *  051CEB95   68 C0FD2D05      PUSH _1locke2.052DFDC0
 *  051CEB9A   64:A1 00000000   MOV EAX,DWORD PTR FS:[0]
 *  051CEBA0   50               PUSH EAX
 *  051CEBA1   83EC 64          SUB ESP,0x64
 *  051CEBA4   53               PUSH EBX
 *  051CEBA5   56               PUSH ESI
 *  051CEBA6   57               PUSH EDI
 *  051CEBA7   A1 10073B05      MOV EAX,DWORD PTR DS:[0x53B0710]
 *  051CEBAC   33C5             XOR EAX,EBP
 *  051CEBAE   50               PUSH EAX
 *  051CEBAF   8D45 F4          LEA EAX,DWORD PTR SS:[EBP-0xC]
 *  051CEBB2   64:A3 00000000   MOV DWORD PTR FS:[0],EAX
 *  051CEBB8   8965 F0          MOV DWORD PTR SS:[EBP-0x10],ESP
 *  051CEBBB   8BF1             MOV ESI,ECX
 *  051CEBBD   8975 D4          MOV DWORD PTR SS:[EBP-0x2C],ESI
 *  051CEBC0   33DB             XOR EBX,EBX
 *  051CEBC2   895D E0          MOV DWORD PTR SS:[EBP-0x20],EBX
 *  051CEBC5   8B45 18          MOV EAX,DWORD PTR SS:[EBP+0x18]
 *  051CEBC8   8AC8             MOV CL,AL
 *  051CEBCA   80E1 01          AND CL,0x1
 *  051CEBCD   884D ED          MOV BYTE PTR SS:[EBP-0x13],CL
 *  051CEBD0   D1E8             SHR EAX,1
 *  051CEBD2   24 01            AND AL,0x1
 *  051CEBD4   8845 1B          MOV BYTE PTR SS:[EBP+0x1B],AL
 *  051CEBD7   8DBE A0000000    LEA EDI,DWORD PTR DS:[ESI+0xA0]
 *  051CEBDD   897D D0          MOV DWORD PTR SS:[EBP-0x30],EDI
 *  051CEBE0   8D47 1C          LEA EAX,DWORD PTR DS:[EDI+0x1C]
 *  051CEBE3   50               PUSH EAX
 *  051CEBE4   FF15 58022F05    CALL DWORD PTR DS:[0x52F0258]            ; kernel32.InterlockedIncrement
 *  051CEBEA   83C7 04          ADD EDI,0x4
 *  051CEBED   57               PUSH EDI
 *  051CEBEE   FF15 5C022F05    CALL DWORD PTR DS:[0x52F025C]            ; ntdll.RtlEnterCriticalSection
 *  051CEBF4   895D FC          MOV DWORD PTR SS:[EBP-0x4],EBX
 *  051CEBF7   395E 10          CMP DWORD PTR DS:[ESI+0x10],EBX
 *  051CEBFA   0F84 68060000    JE _1locke2.051CF268
 *  051CEC00   8975 C0          MOV DWORD PTR SS:[EBP-0x40],ESI
 *  051CEC03   8BCE             MOV ECX,ESI
 *  051CEC05   E8 B6B2FFFF      CALL _1locke2.051C9EC0
 *  051CEC0A   8945 C4          MOV DWORD PTR SS:[EBP-0x3C],EAX
 *  051CEC0D   C645 FC 01       MOV BYTE PTR SS:[EBP-0x4],0x1
 *  051CEC11   389E 49020000    CMP BYTE PTR DS:[ESI+0x249],BL
 *  051CEC17   74 07            JE SHORT _1locke2.051CEC20
 *  051CEC19   8BCE             MOV ECX,ESI
 *  051CEC1B   E8 409BFFFF      CALL _1locke2.051C8760
 *  051CEC20   C645 FC 02       MOV BYTE PTR SS:[EBP-0x4],0x2
 *  051CEC24   8B4E 6C          MOV ECX,DWORD PTR DS:[ESI+0x6C]
 *  051CEC27   3BCB             CMP ECX,EBX
 *  051CEC29   74 2F            JE SHORT _1locke2.051CEC5A
 *  051CEC2B   8079 10 00       CMP BYTE PTR DS:[ECX+0x10],0x0
 *  051CEC2F   74 29            JE SHORT _1locke2.051CEC5A
 *  051CEC31   8B45 10          MOV EAX,DWORD PTR SS:[EBP+0x10]
 *  051CEC34   3BC3             CMP EAX,EBX
 *  051CEC36   74 22            JE SHORT _1locke2.051CEC5A
 *  051CEC38   53               PUSH EBX
 *  051CEC39   53               PUSH EBX
 *  051CEC3A   53               PUSH EBX
 *  051CEC3B   53               PUSH EBX
 *  051CEC3C   53               PUSH EBX
 *  051CEC3D   53               PUSH EBX
 *  051CEC3E   53               PUSH EBX
 *  051CEC3F   6A 14            PUSH 0x14
 *  051CEC41   6A FF            PUSH -0x1
 *  051CEC43   53               PUSH EBX
 *  051CEC44   6A 08            PUSH 0x8
 *  051CEC46   50               PUSH EAX
 *  051CEC47   53               PUSH EBX
 *  051CEC48   E8 3391FCFF      CALL _1locke2.05197D80
 *  051CEC4D   6A 01            PUSH 0x1
 *  051CEC4F   53               PUSH EBX
 *  051CEC50   8B4E 6C          MOV ECX,DWORD PTR DS:[ESI+0x6C]
 *  051CEC53   E8 48C9FCFF      CALL _1locke2.0519B5A0
 *  051CEC58   EB 13            JMP SHORT _1locke2.051CEC6D
 *  051CEC5A   8B4D 14          MOV ECX,DWORD PTR SS:[EBP+0x14]
 *  051CEC5D   3BCB             CMP ECX,EBX
 *  051CEC5F   74 0C            JE SHORT _1locke2.051CEC6D
 *  051CEC61   53               PUSH EBX
 *  051CEC62   68 B0B32305      PUSH _1locke2.0523B3B0
 *  051CEC67   53               PUSH EBX
 *  051CEC68   E8 73C80600      CALL _1locke2.0523B4E0
 *  051CEC6D   66:C745 E8 0A00  MOV WORD PTR SS:[EBP-0x18],0xA
 *  051CEC73   8B4D 08          MOV ECX,DWORD PTR SS:[EBP+0x8]
 *  051CEC76   51               PUSH ECX
 *  051CEC77   8D4D 9C          LEA ECX,DWORD PTR SS:[EBP-0x64]
 *  051CEC7A   E8 81F9E1FF      CALL _1locke2.04FEE600
 *  051CEC7F   C645 FC 03       MOV BYTE PTR SS:[EBP-0x4],0x3
 *  051CEC83   8D55 9C          LEA EDX,DWORD PTR SS:[EBP-0x64]
 *  051CEC86   52               PUSH EDX
 *  051CEC87   8BCE             MOV ECX,ESI
 *  051CEC89   E8 72F2FFFF      CALL _1locke2.051CDF00
 *  051CEC8E   8D4D B4          LEA ECX,DWORD PTR SS:[EBP-0x4C]
 *  051CEC91   E8 AA28DDFF      CALL _1locke2.04FA1540
 *  051CEC96   C645 FC 04       MOV BYTE PTR SS:[EBP-0x4],0x4
 *  051CEC9A   8D4D A8          LEA ECX,DWORD PTR SS:[EBP-0x58]
 *  051CEC9D   E8 9E28DDFF      CALL _1locke2.04FA1540
 *  051CECA2   C645 FC 05       MOV BYTE PTR SS:[EBP-0x4],0x5
 *  051CECA6   895D E4          MOV DWORD PTR SS:[EBP-0x1C],EBX
 *  051CECA9   8B7D 0C          MOV EDI,DWORD PTR SS:[EBP+0xC]
 *  051CECAC   3BFB             CMP EDI,EBX
 *  051CECAE   75 06            JNZ SHORT _1locke2.051CECB6
 *  051CECB0   8D7E 70          LEA EDI,DWORD PTR DS:[ESI+0x70]
 *  051CECB3   897D 0C          MOV DWORD PTR SS:[EBP+0xC],EDI
 *  051CECB6   C645 EF 00       MOV BYTE PTR SS:[EBP-0x11],0x0
 *  051CECBA   8D9B 00000000    LEA EBX,DWORD PTR DS:[EBX]
 *  051CECC0   8B45 A4          MOV EAX,DWORD PTR SS:[EBP-0x5C]
 *  051CECC3   8038 0A          CMP BYTE PTR DS:[EAX],0xA
 *  051CECC6   75 19            JNZ SHORT _1locke2.051CECE1
 *  051CECC8   53               PUSH EBX
 *  051CECC9   57               PUSH EDI
 *  051CECCA   8BCE             MOV ECX,ESI
 *  051CECCC   E8 DFEEFFFF      CALL _1locke2.051CDBB0
 *  051CECD1   83F8 02          CMP EAX,0x2
 *  051CECD4   0F85 C9010000    JNZ _1locke2.051CEEA3
 *  051CECDA   8945 E0          MOV DWORD PTR SS:[EBP-0x20],EAX
 *  051CECDD   C645 EF 01       MOV BYTE PTR SS:[EBP-0x11],0x1
 *  051CECE1   BF 01000000      MOV EDI,0x1
 *  051CECE6   897D DC          MOV DWORD PTR SS:[EBP-0x24],EDI
 *  051CECE9   C645 EE 01       MOV BYTE PTR SS:[EBP-0x12],0x1
 *  051CECED   8B1D B4002F05    MOV EBX,DWORD PTR DS:[0x52F00B4]         ; gdi32.SetTextColor
 *  051CECF3   807D EF 00       CMP BYTE PTR SS:[EBP-0x11],0x0
 *  051CECF7   0F85 AF040000    JNZ _1locke2.051CF1AC
 *  051CECFD   85FF             TEST EDI,EDI
 *  051CECFF   0F84 A7040000    JE _1locke2.051CF1AC
 *  051CED05   6A 00            PUSH 0x0
 *  051CED07   8D4D E8          LEA ECX,DWORD PTR SS:[EBP-0x18]
 *  051CED0A   51               PUSH ECX
 *  051CED0B   8D55 B4          LEA EDX,DWORD PTR SS:[EBP-0x4C]
 *  051CED0E   52               PUSH EDX
 *  051CED0F   8D4D 9C          LEA ECX,DWORD PTR SS:[EBP-0x64]
 *  051CED12   E8 39B7F9FF      CALL _1locke2.0516A450
 *  051CED17   F7D8             NEG EAX
 *  051CED19   1BC0             SBB EAX,EAX
 *  051CED1B   F7D8             NEG EAX
 *  051CED1D   0F84 89040000    JE _1locke2.051CF1AC
 *  051CED23   8BF8             MOV EDI,EAX
 *  051CED25   897D DC          MOV DWORD PTR SS:[EBP-0x24],EDI
 *  051CED28   8B45 B8          MOV EAX,DWORD PTR SS:[EBP-0x48]
 *  051CED2B   8B40 14          MOV EAX,DWORD PTR DS:[EAX+0x14]
 *  051CED2E   8945 BC          MOV DWORD PTR SS:[EBP-0x44],EAX
 *  051CED31   807D EF 00       CMP BYTE PTR SS:[EBP-0x11],0x0
 *  051CED35   0F85 71040000    JNZ _1locke2.051CF1AC
 *  051CED3B   85FF             TEST EDI,EDI
 *  051CED3D   0F84 3B040000    JE _1locke2.051CF17E
 *  051CED43   8D4D B4          LEA ECX,DWORD PTR SS:[EBP-0x4C]
 *  051CED46   E8 F594F9FF      CALL _1locke2.05168240
 *  051CED4B   85C0             TEST EAX,EAX
 *  051CED4D   0F84 2B040000    JE _1locke2.051CF17E
 *  051CED53   8B4D BC          MOV ECX,DWORD PTR SS:[EBP-0x44]
 *  051CED56   51               PUSH ECX
 *  051CED57   FF15 8C032F05    CALL DWORD PTR DS:[0x52F038C]            ; kernel32.lstrlenA
 *  051CED5D   8BF8             MOV EDI,EAX
 *  051CED5F   897D D8          MOV DWORD PTR SS:[EBP-0x28],EDI
 *  051CED62   8B8E 58010000    MOV ECX,DWORD PTR DS:[ESI+0x158]
 *  051CED68   2B8E 50010000    SUB ECX,DWORD PTR DS:[ESI+0x150]
 *  051CED6E   8B96 64010000    MOV EDX,DWORD PTR DS:[ESI+0x164]
 *  051CED74   8B86 50010000    MOV EAX,DWORD PTR DS:[ESI+0x150]
 *  051CED7A   2B86 80010000    SUB EAX,DWORD PTR DS:[ESI+0x180]
 *  051CED80   2B86 7C010000    SUB EAX,DWORD PTR DS:[ESI+0x17C]
 *  051CED86   2BC2             SUB EAX,EDX
 *  051CED88   03C1             ADD EAX,ECX
 *  051CED8A   8945 08          MOV DWORD PTR SS:[EBP+0x8],EAX
 *  051CED8D   8D55 C8          LEA EDX,DWORD PTR SS:[EBP-0x38]
 *  051CED90   52               PUSH EDX
 *  051CED91   6A 00            PUSH 0x0
 *  051CED93   8D4D E4          LEA ECX,DWORD PTR SS:[EBP-0x1C]
 *  051CED96   51               PUSH ECX
 *  051CED97   50               PUSH EAX
 *  051CED98   57               PUSH EDI
 *  051CED99   8B55 BC          MOV EDX,DWORD PTR SS:[EBP-0x44]
 *  051CED9C   52               PUSH EDX
 *  051CED9D   8B86 50020000    MOV EAX,DWORD PTR DS:[ESI+0x250]
 *  051CEDA3   50               PUSH EAX
 *  051CEDA4   FF15 C4002F05    CALL DWORD PTR DS:[0x52F00C4]            ; gdi32.GetTextExtentExPointA
 *  051CEDAA   F786 84010000 00>TEST DWORD PTR DS:[ESI+0x184],0x400
 *  051CEDB4   74 21            JE SHORT _1locke2.051CEDD7
 *  051CEDB6   8B4D C8          MOV ECX,DWORD PTR SS:[EBP-0x38]
 *  051CEDB9   83C1 04          ADD ECX,0x4
 *  051CEDBC   394D 08          CMP DWORD PTR SS:[EBP+0x8],ECX
 *  051CEDBF   7D 16            JGE SHORT _1locke2.051CEDD7
 *  051CEDC1   8B45 E4          MOV EAX,DWORD PTR SS:[EBP-0x1C]
 *  051CEDC4   83C0 FF          ADD EAX,-0x1
 *  051CEDC7   83F8 01          CMP EAX,0x1
 *  051CEDCA   0F8D E0000000    JGE _1locke2.051CEEB0
 *  051CEDD0   C745 E4 00000000 MOV DWORD PTR SS:[EBP-0x1C],0x0
 *  051CEDD7   8B55 E4          MOV EDX,DWORD PTR SS:[EBP-0x1C]
 *  051CEDDA   52               PUSH EDX
 *  051CEDDB   8B45 BC          MOV EAX,DWORD PTR SS:[EBP-0x44]
 *  051CEDDE   50               PUSH EAX
 *  051CEDDF   8BCE             MOV ECX,ESI
 *  051CEDE1   E8 FAA0FFFF      CALL _1locke2.051C8EE0
 *  051CEDE6   8945 E4          MOV DWORD PTR SS:[EBP-0x1C],EAX
 *  051CEDE9   F786 84010000 00>TEST DWORD PTR DS:[ESI+0x184],0x100
 *  051CEDF3   74 71            JE SHORT _1locke2.051CEE66
 *  051CEDF5   3BC7             CMP EAX,EDI
 *  051CEDF7   7D 6D            JGE SHORT _1locke2.051CEE66
 *  051CEDF9   83F8 01          CMP EAX,0x1
 *  051CEDFC   7C 68            JL SHORT _1locke2.051CEE66
 *  051CEDFE   8D4D 90          LEA ECX,DWORD PTR SS:[EBP-0x70]
 *  051CEE01   E8 3A27DDFF      CALL _1locke2.04FA1540
 *  051CEE06   C645 FC 06       MOV BYTE PTR SS:[EBP-0x4],0x6
 *  051CEE0A   8B4D B8          MOV ECX,DWORD PTR SS:[EBP-0x48]
 *  051CEE0D   8B41 14          MOV EAX,DWORD PTR DS:[ECX+0x14]
 *  051CEE10   8B55 E4          MOV EDX,DWORD PTR SS:[EBP-0x1C]
 *  051CEE13   8D4C10 FF        LEA ECX,DWORD PTR DS:[EAX+EDX-0x1]
 *  051CEE17   51               PUSH ECX
 *  051CEE18   50               PUSH EAX
 *  051CEE19   8D55 90          LEA EDX,DWORD PTR SS:[EBP-0x70]
 *  051CEE1C   52               PUSH EDX
 *  051CEE1D   8D4D B4          LEA ECX,DWORD PTR SS:[EBP-0x4C]
 *  051CEE20   E8 4BB7F9FF      CALL _1locke2.0516A570
 *  051CEE25   8D45 90          LEA EAX,DWORD PTR SS:[EBP-0x70]
 *  051CEE28   50               PUSH EAX
 *  051CEE29   8D4D B4          LEA ECX,DWORD PTR SS:[EBP-0x4C]
 *  051CEE2C   E8 DF89F9FF      CALL _1locke2.05167810
 *  051CEE31   8B45 B8          MOV EAX,DWORD PTR SS:[EBP-0x48]
 *  051CEE34   8B78 08          MOV EDI,DWORD PTR DS:[EAX+0x8]
 *  051CEE37   897D D8          MOV DWORD PTR SS:[EBP-0x28],EDI
 *  051CEE3A   8B40 14          MOV EAX,DWORD PTR DS:[EAX+0x14]
 *  051CEE3D   8D4D C8          LEA ECX,DWORD PTR SS:[EBP-0x38]
 *  051CEE40   51               PUSH ECX
 *  051CEE41   57               PUSH EDI
 *  051CEE42   50               PUSH EAX
 *  051CEE43   8B96 50020000    MOV EDX,DWORD PTR DS:[ESI+0x250]
 *  051CEE49   52               PUSH EDX
 *  051CEE4A   FF15 BC002F05    CALL DWORD PTR DS:[0x52F00BC]            ; gdi32.GetTextExtentPoint32A
 *  051CEE50   C745 DC 00000000 MOV DWORD PTR SS:[EBP-0x24],0x0
 *  051CEE57   C645 FC 05       MOV BYTE PTR SS:[EBP-0x4],0x5
 *  051CEE5B   8D4D 90          LEA ECX,DWORD PTR SS:[EBP-0x70]
 *  051CEE5E   E8 4D89F9FF      CALL _1locke2.051677B0
 *  051CEE63   8B45 E4          MOV EAX,DWORD PTR SS:[EBP-0x1C]
 *  051CEE66   85C0             TEST EAX,EAX
 *  051CEE68   0F84 9D010000    JE _1locke2.051CF00B
 *  051CEE6E   3BC7             CMP EAX,EDI
 *  051CEE70   0F8D C4010000    JGE _1locke2.051CF03A
 *  051CEE76   8B4D BC          MOV ECX,DWORD PTR SS:[EBP-0x44]
 *  051CEE79   8D3C01           LEA EDI,DWORD PTR DS:[ECX+EAX]
 *  051CEE7C   894D 08          MOV DWORD PTR SS:[EBP+0x8],ECX
 *  051CEE7F   90               NOP
 *  051CEE80   3B7D 08          CMP EDI,DWORD PTR SS:[EBP+0x8]
 *  051CEE83   74 58            JE SHORT _1locke2.051CEEDD
 *  051CEE85   57               PUSH EDI
 *  051CEE86   8BCE             MOV ECX,ESI
 *  051CEE88   E8 63C4FFFF      CALL _1locke2.051CB2F0
 *  051CEE8D   85C0             TEST EAX,EAX
 *  051CEE8F   74 44            JE SHORT _1locke2.051CEED5
 *  051CEE91   57               PUSH EDI
 *  051CEE92   8B4D 08          MOV ECX,DWORD PTR SS:[EBP+0x8]
 *  051CEE95   51               PUSH ECX
 *  051CEE96   FF15 E4072F05    CALL DWORD PTR DS:[0x52F07E4]            ; user32.CharPrevA
 *  051CEE9C   8BF8             MOV EDI,EAX
 *  051CEE9E   8B45 E4          MOV EAX,DWORD PTR SS:[EBP-0x1C]
 *  051CEEA1  ^EB DD            JMP SHORT _1locke2.051CEE80
 *  051CEEA3   8D4D 9C          LEA ECX,DWORD PTR SS:[EBP-0x64]
 *  051CEEA6   E8 3574EBFF      CALL _1locke2.050862E0
 *  051CEEAB  ^E9 10FEFFFF      JMP _1locke2.051CECC0
 *  051CEEB0   8D55 C8          LEA EDX,DWORD PTR SS:[EBP-0x38]
 *  051CEEB3   52               PUSH EDX
 *  051CEEB4   6A 00            PUSH 0x0
 *  051CEEB6   8D4D E4          LEA ECX,DWORD PTR SS:[EBP-0x1C]
 *  051CEEB9   51               PUSH ECX
 *  051CEEBA   8B55 08          MOV EDX,DWORD PTR SS:[EBP+0x8]
 *  051CEEBD   52               PUSH EDX
 *  051CEEBE   50               PUSH EAX
 *  051CEEBF   8B45 BC          MOV EAX,DWORD PTR SS:[EBP-0x44]
 *  051CEEC2   50               PUSH EAX
 *  051CEEC3   8B8E 50020000    MOV ECX,DWORD PTR DS:[ESI+0x250]
 *  051CEEC9   51               PUSH ECX
 *  051CEECA   FF15 C4002F05    CALL DWORD PTR DS:[0x52F00C4]            ; gdi32.GetTextExtentExPointA
 *  051CEED0  ^E9 E1FEFFFF      JMP _1locke2.051CEDB6
 *  051CEED5   2B7D 08          SUB EDI,DWORD PTR SS:[EBP+0x8]
 *  051CEED8   8BC7             MOV EAX,EDI
 *  051CEEDA   8945 E4          MOV DWORD PTR SS:[EBP-0x1C],EAX
 *  051CEEDD   8B4D BC          MOV ECX,DWORD PTR SS:[EBP-0x44]
 *  051CEEE0   8D5401 FF        LEA EDX,DWORD PTR DS:[ECX+EAX-0x1]
 *  051CEEE4   52               PUSH EDX
 *  051CEEE5   51               PUSH ECX
 *  051CEEE6   8D45 A8          LEA EAX,DWORD PTR SS:[EBP-0x58]
 *  051CEEE9   50               PUSH EAX
 *  051CEEEA   8D4D B4          LEA ECX,DWORD PTR SS:[EBP-0x4C]
 *  051CEEED   E8 7EB6F9FF      CALL _1locke2.0516A570
 *  051CEEF2   807D EE 00       CMP BYTE PTR SS:[EBP-0x12],0x0
 *  051CEEF6   74 1C            JE SHORT _1locke2.051CEF14
 *  051CEEF8   8B86 68010000    MOV EAX,DWORD PTR DS:[ESI+0x168]
 *  051CEEFE   8B8E 64010000    MOV ECX,DWORD PTR DS:[ESI+0x164]
 *  051CEF04   898E 5C020000    MOV DWORD PTR DS:[ESI+0x25C],ECX
 *  051CEF0A   8986 60020000    MOV DWORD PTR DS:[ESI+0x260],EAX
 *  051CEF10   C645 EE 00       MOV BYTE PTR SS:[EBP-0x12],0x0
 *  051CEF14   80BE 49020000 00 CMP BYTE PTR DS:[ESI+0x249],0x0
 *  051CEF1B   0F85 BE000000    JNZ _1locke2.051CEFDF
 *  051CEF21   F786 84010000 00>TEST DWORD PTR DS:[ESI+0x184],0x400
 *  051CEF2B   0F84 AE000000    JE _1locke2.051CEFDF
 *  051CEF31   8B8E 04020000    MOV ECX,DWORD PTR DS:[ESI+0x204]
 *  051CEF37   51               PUSH ECX
 *  051CEF38   8B96 50020000    MOV EDX,DWORD PTR DS:[ESI+0x250]
 *  051CEF3E   52               PUSH EDX
 *  051CEF3F   FFD3             CALL EBX
 *  051CEF41   8BF8             MOV EDI,EAX
 *  051CEF43   8B45 AC          MOV EAX,DWORD PTR SS:[EBP-0x54]
 *  051CEF46   8B48 08          MOV ECX,DWORD PTR DS:[EAX+0x8]
 *  051CEF49   8B40 14          MOV EAX,DWORD PTR DS:[EAX+0x14]
 *  051CEF4C   8B96 68010000    MOV EDX,DWORD PTR DS:[ESI+0x168]
 *  051CEF52   8B9E 64010000    MOV EBX,DWORD PTR DS:[ESI+0x164]
 *  051CEF58   51               PUSH ECX
 *  051CEF59   50               PUSH EAX
 *  051CEF5A   52               PUSH EDX
 *  051CEF5B   83C3 FF          ADD EBX,-0x1
 *  051CEF5E   53               PUSH EBX
 *  051CEF5F   8BCE             MOV ECX,ESI
 *  051CEF61   E8 3ACEFFFF      CALL _1locke2.051CBDA0
 *  051CEF66   8B45 AC          MOV EAX,DWORD PTR SS:[EBP-0x54]
 *  051CEF69   8B48 08          MOV ECX,DWORD PTR DS:[EAX+0x8]
 *  051CEF6C   8B40 14          MOV EAX,DWORD PTR DS:[EAX+0x14]
 *  051CEF6F   8B96 68010000    MOV EDX,DWORD PTR DS:[ESI+0x168]
 *  051CEF75   8B9E 64010000    MOV EBX,DWORD PTR DS:[ESI+0x164]
 *  051CEF7B   51               PUSH ECX
 *  051CEF7C   50               PUSH EAX
 *  051CEF7D   52               PUSH EDX
 *  051CEF7E   83C3 01          ADD EBX,0x1
 *  051CEF81   53               PUSH EBX
 *  051CEF82   8BCE             MOV ECX,ESI
 *  051CEF84   E8 17CEFFFF      CALL _1locke2.051CBDA0
 *  051CEF89   8B45 AC          MOV EAX,DWORD PTR SS:[EBP-0x54]
 *  051CEF8C   8B48 08          MOV ECX,DWORD PTR DS:[EAX+0x8]
 *  051CEF8F   8B40 14          MOV EAX,DWORD PTR DS:[EAX+0x14]
 *  051CEF92   8B96 68010000    MOV EDX,DWORD PTR DS:[ESI+0x168]
 *  051CEF98   8B9E 64010000    MOV EBX,DWORD PTR DS:[ESI+0x164]
 *  051CEF9E   51               PUSH ECX
 *  051CEF9F   50               PUSH EAX
 *  051CEFA0   83C2 FF          ADD EDX,-0x1
 *  051CEFA3   52               PUSH EDX
 *  051CEFA4   53               PUSH EBX
 *  051CEFA5   8BCE             MOV ECX,ESI
 *  051CEFA7   E8 F4CDFFFF      CALL _1locke2.051CBDA0
 *  051CEFAC   8B45 AC          MOV EAX,DWORD PTR SS:[EBP-0x54]
 *  051CEFAF   8B48 08          MOV ECX,DWORD PTR DS:[EAX+0x8]
 *  051CEFB2   8B40 14          MOV EAX,DWORD PTR DS:[EAX+0x14]
 *  051CEFB5   8B96 68010000    MOV EDX,DWORD PTR DS:[ESI+0x168]
 *  051CEFBB   8B9E 64010000    MOV EBX,DWORD PTR DS:[ESI+0x164]
 *  051CEFC1   51               PUSH ECX
 *  051CEFC2   50               PUSH EAX
 *  051CEFC3   83C2 01          ADD EDX,0x1
 *  051CEFC6   52               PUSH EDX
 *  051CEFC7   53               PUSH EBX
 *  051CEFC8   8BCE             MOV ECX,ESI
 *  051CEFCA   E8 D1CDFFFF      CALL _1locke2.051CBDA0
 *  051CEFCF   57               PUSH EDI
 *  051CEFD0   8B86 50020000    MOV EAX,DWORD PTR DS:[ESI+0x250]
 *  051CEFD6   50               PUSH EAX
 *  051CEFD7   8B1D B4002F05    MOV EBX,DWORD PTR DS:[0x52F00B4]         ; gdi32.SetTextColor
 *  051CEFDD   FFD3             CALL EBX
 *  051CEFDF   8B45 AC          MOV EAX,DWORD PTR SS:[EBP-0x54]
 *  051CEFE2   8B48 08          MOV ECX,DWORD PTR DS:[EAX+0x8]
 *  051CEFE5   51               PUSH ECX
 *  051CEFE6   8B40 14          MOV EAX,DWORD PTR DS:[EAX+0x14]
 *  051CEFE9   50               PUSH EAX
 *  051CEFEA   8B96 68010000    MOV EDX,DWORD PTR DS:[ESI+0x168]
 *  051CEFF0   52               PUSH EDX
 *  051CEFF1   8BBE 64010000    MOV EDI,DWORD PTR DS:[ESI+0x164]
 *  051CEFF7   57               PUSH EDI
 *  051CEFF8   8BCE             MOV ECX,ESI
 *  051CEFFA   E8 A1CDFFFF      CALL _1locke2.051CBDA0
 *  051CEFFF   8B4D E4          MOV ECX,DWORD PTR SS:[EBP-0x1C]
 *  051CF002   8B55 BC          MOV EDX,DWORD PTR SS:[EBP-0x44]
 *  051CF005   8D040A           LEA EAX,DWORD PTR DS:[EDX+ECX]
 *  051CF008   8945 BC          MOV DWORD PTR SS:[EBP-0x44],EAX
 *  051CF00B   6A 00            PUSH 0x0
 *  051CF00D   8B45 0C          MOV EAX,DWORD PTR SS:[EBP+0xC]
 *  051CF010   50               PUSH EAX
 *  051CF011   8BCE             MOV ECX,ESI
 *  051CF013   E8 98EBFFFF      CALL _1locke2.051CDBB0
 *  051CF018   33C9             XOR ECX,ECX
 *  051CF01A   83F8 02          CMP EAX,0x2
 *  051CF01D   0F94C1           SETE CL
 *  051CF020   884D EF          MOV BYTE PTR SS:[EBP-0x11],CL
 *  051CF023   84C9             TEST CL,CL
 *  051CF025   0F84 4B010000    JE _1locke2.051CF176
 *  051CF02B   C745 E0 02000000 MOV DWORD PTR SS:[EBP-0x20],0x2
 *  051CF032   8B7D DC          MOV EDI,DWORD PTR SS:[EBP-0x24]
 *  051CF035  ^E9 F7FCFFFF      JMP _1locke2.051CED31
 *  051CF03A   F786 84010000 00>TEST DWORD PTR DS:[ESI+0x184],0x200
 *  051CF044   74 26            JE SHORT _1locke2.051CF06C
 *  051CF046   8B86 58010000    MOV EAX,DWORD PTR DS:[ESI+0x158]
 *  051CF04C   2B86 50010000    SUB EAX,DWORD PTR DS:[ESI+0x150]
 *  051CF052   2B45 C8          SUB EAX,DWORD PTR SS:[EBP-0x38]
 *  051CF055   99               CDQ
 *  051CF056   2BC2             SUB EAX,EDX
 *  051CF058   D1F8             SAR EAX,1
 *  051CF05A   85C0             TEST EAX,EAX
 *  051CF05C   7E 0E            JLE SHORT _1locke2.051CF06C
 *  051CF05E   8B8E 50010000    MOV ECX,DWORD PTR DS:[ESI+0x150]
 *  051CF064   03C8             ADD ECX,EAX
 *  051CF066   898E 64010000    MOV DWORD PTR DS:[ESI+0x164],ECX
 *  051CF06C   807D EE 00       CMP BYTE PTR SS:[EBP-0x12],0x0
 *  051CF070   74 1C            JE SHORT _1locke2.051CF08E
 *  051CF072   8B86 68010000    MOV EAX,DWORD PTR DS:[ESI+0x168]
 *  051CF078   8B8E 64010000    MOV ECX,DWORD PTR DS:[ESI+0x164]
 *  051CF07E   898E 5C020000    MOV DWORD PTR DS:[ESI+0x25C],ECX
 *  051CF084   8986 60020000    MOV DWORD PTR DS:[ESI+0x260],EAX
 *  051CF08A   C645 EE 00       MOV BYTE PTR SS:[EBP-0x12],0x0
 *  051CF08E   80BE 49020000 00 CMP BYTE PTR DS:[ESI+0x249],0x0
 *  051CF095   0F85 A4000000    JNZ _1locke2.051CF13F
 *  051CF09B   F786 84010000 00>TEST DWORD PTR DS:[ESI+0x184],0x400
 *  051CF0A5   0F84 94000000    JE _1locke2.051CF13F
 *  051CF0AB   8B8E 04020000    MOV ECX,DWORD PTR DS:[ESI+0x204]
 *  051CF0B1   51               PUSH ECX
 *  051CF0B2   8B96 50020000    MOV EDX,DWORD PTR DS:[ESI+0x250]
 *  051CF0B8   52               PUSH EDX
 *  051CF0B9   FFD3             CALL EBX
 *  051CF0BB   8945 08          MOV DWORD PTR SS:[EBP+0x8],EAX
 *  051CF0BE   8B86 68010000    MOV EAX,DWORD PTR DS:[ESI+0x168]
 *  051CF0C4   8B8E 64010000    MOV ECX,DWORD PTR DS:[ESI+0x164]
 *  051CF0CA   57               PUSH EDI
 *  051CF0CB   8B55 BC          MOV EDX,DWORD PTR SS:[EBP-0x44]
 *  051CF0CE   52               PUSH EDX
 *  051CF0CF   50               PUSH EAX
 *  051CF0D0   83C1 FF          ADD ECX,-0x1
 *  051CF0D3   51               PUSH ECX
 *  051CF0D4   8BCE             MOV ECX,ESI
 *  051CF0D6   E8 C5CCFFFF      CALL _1locke2.051CBDA0
 *  051CF0DB   8B86 68010000    MOV EAX,DWORD PTR DS:[ESI+0x168]
 *  051CF0E1   8B8E 64010000    MOV ECX,DWORD PTR DS:[ESI+0x164]
 *  051CF0E7   57               PUSH EDI
 *  051CF0E8   8B55 BC          MOV EDX,DWORD PTR SS:[EBP-0x44]
 *  051CF0EB   52               PUSH EDX
 *  051CF0EC   50               PUSH EAX
 *  051CF0ED   83C1 01          ADD ECX,0x1
 *  051CF0F0   51               PUSH ECX
 *  051CF0F1   8BCE             MOV ECX,ESI
 *  051CF0F3   E8 A8CCFFFF      CALL _1locke2.051CBDA0
 *  051CF0F8   8B86 68010000    MOV EAX,DWORD PTR DS:[ESI+0x168]
 *  051CF0FE   8B8E 64010000    MOV ECX,DWORD PTR DS:[ESI+0x164]
 *  051CF104   57               PUSH EDI
 *  051CF105   8B55 BC          MOV EDX,DWORD PTR SS:[EBP-0x44]
 *  051CF108   52               PUSH EDX
 *  051CF109   83C0 FF          ADD EAX,-0x1
 *  051CF10C   50               PUSH EAX
 *  051CF10D   51               PUSH ECX
 *  051CF10E   8BCE             MOV ECX,ESI
 *  051CF110   E8 8BCCFFFF      CALL _1locke2.051CBDA0
 *  051CF115   8B86 68010000    MOV EAX,DWORD PTR DS:[ESI+0x168]
 *  051CF11B   8B8E 64010000    MOV ECX,DWORD PTR DS:[ESI+0x164]
 *  051CF121   57               PUSH EDI
 *  051CF122   8B55 BC          MOV EDX,DWORD PTR SS:[EBP-0x44]
 *  051CF125   52               PUSH EDX
 *  051CF126   83C0 01          ADD EAX,0x1
 *  051CF129   50               PUSH EAX
 *  051CF12A   51               PUSH ECX
 *  051CF12B   8BCE             MOV ECX,ESI
 *  051CF12D   E8 6ECCFFFF      CALL _1locke2.051CBDA0
 *  051CF132   8B45 08          MOV EAX,DWORD PTR SS:[EBP+0x8]
 *  051CF135   50               PUSH EAX
 *  051CF136   8B8E 50020000    MOV ECX,DWORD PTR DS:[ESI+0x250]
 *  051CF13C   51               PUSH ECX
 *  051CF13D   FFD3             CALL EBX
 *  051CF13F   57               PUSH EDI
 *  051CF140   8B55 BC          MOV EDX,DWORD PTR SS:[EBP-0x44]
 *  051CF143   52               PUSH EDX
 *  051CF144   8B86 68010000    MOV EAX,DWORD PTR DS:[ESI+0x168]
 *  051CF14A   50               PUSH EAX
 *  051CF14B   8B8E 64010000    MOV ECX,DWORD PTR DS:[ESI+0x164]
 *  051CF151   51               PUSH ECX
 *  051CF152   8BCE             MOV ECX,ESI
 *  051CF154   E8 47CCFFFF      CALL _1locke2.051CBDA0
 *  051CF159   8B45 B8          MOV EAX,DWORD PTR SS:[EBP-0x48]
 *  051CF15C   8B48 14          MOV ECX,DWORD PTR DS:[EAX+0x14]
 *  051CF15F   0348 08          ADD ECX,DWORD PTR DS:[EAX+0x8]
 *  051CF162   894D BC          MOV DWORD PTR SS:[EBP-0x44],ECX
 *  051CF165   8B86 64010000    MOV EAX,DWORD PTR DS:[ESI+0x164]
 *  051CF16B   8B55 C8          MOV EDX,DWORD PTR SS:[EBP-0x38]
 *  051CF16E   03C2             ADD EAX,EDX
 *  051CF170   8986 64010000    MOV DWORD PTR DS:[ESI+0x164],EAX
 *  051CF176   8B7D DC          MOV EDI,DWORD PTR SS:[EBP-0x24]
 *  051CF179  ^E9 B3FBFFFF      JMP _1locke2.051CED31
 *  051CF17E   8B45 A4          MOV EAX,DWORD PTR SS:[EBP-0x5C]
 *  051CF181   8038 0A          CMP BYTE PTR DS:[EAX],0xA
 *  051CF184  ^0F85 69FBFFFF    JNZ _1locke2.051CECF3
 *  051CF18A   6A 00            PUSH 0x0
 *  051CF18C   8B4D 0C          MOV ECX,DWORD PTR SS:[EBP+0xC]
 *  051CF18F   51               PUSH ECX
 *  051CF190   8BCE             MOV ECX,ESI
 *  051CF192   E8 19EAFFFF      CALL _1locke2.051CDBB0
 *  051CF197   83F8 02          CMP EAX,0x2
 *  051CF19A  ^0F85 53FBFFFF    JNZ _1locke2.051CECF3
 *  051CF1A0   C645 EF 01       MOV BYTE PTR SS:[EBP-0x11],0x1
 *  051CF1A4   8945 E0          MOV DWORD PTR SS:[EBP-0x20],EAX
 *  051CF1A7  ^E9 47FBFFFF      JMP _1locke2.051CECF3
 *  051CF1AC   807D 1B 00       CMP BYTE PTR SS:[EBP+0x1B],0x0
 *  051CF1B0   74 07            JE SHORT _1locke2.051CF1B9
 *  051CF1B2   8BCE             MOV ECX,ESI
 *  051CF1B4   E8 F7D2FFFF      CALL _1locke2.051CC4B0
 *  051CF1B9   807D EF 00       CMP BYTE PTR SS:[EBP-0x11],0x0
 *  051CF1BD   75 60            JNZ SHORT _1locke2.051CF21F
 *  051CF1BF   807D ED 00       CMP BYTE PTR SS:[EBP-0x13],0x0
 *  051CF1C3   74 5A            JE SHORT _1locke2.051CF21F
 *  051CF1C5   8B46 0C          MOV EAX,DWORD PTR DS:[ESI+0xC]
 *  051CF1C8   85C0             TEST EAX,EAX
 *  051CF1CA   74 53            JE SHORT _1locke2.051CF21F
 *  051CF1CC   8B96 44020000    MOV EDX,DWORD PTR DS:[ESI+0x244]
 *  051CF1D2   52               PUSH EDX
 *  051CF1D3   50               PUSH EAX
 *  051CF1D4   8D86 4C010000    LEA EAX,DWORD PTR DS:[ESI+0x14C]
 *  051CF1DA   50               PUSH EAX
 *  051CF1DB   8B4D 0C          MOV ECX,DWORD PTR SS:[EBP+0xC]
 *  051CF1DE   E8 FDB80700      CALL _1locke2.0524AAE0
 *  051CF1E3   8B4E 6C          MOV ECX,DWORD PTR DS:[ESI+0x6C]
 *  051CF1E6   85C9             TEST ECX,ECX
 *  051CF1E8   74 15            JE SHORT _1locke2.051CF1FF
 *  051CF1EA   8079 10 00       CMP BYTE PTR DS:[ECX+0x10],0x0
 *  051CF1EE   74 0F            JE SHORT _1locke2.051CF1FF
 *  051CF1F0   837D 10 00       CMP DWORD PTR SS:[EBP+0x10],0x0
 *  051CF1F4   74 09            JE SHORT _1locke2.051CF1FF
 *  051CF1F6   6A 00            PUSH 0x0
 *  051CF1F8   E8 C3C4FCFF      CALL _1locke2.0519B6C0
 *  051CF1FD   EB 0E            JMP SHORT _1locke2.051CF20D
 *  051CF1FF   8B4D 14          MOV ECX,DWORD PTR SS:[EBP+0x14]
 *  051CF202   85C9             TEST ECX,ECX
 *  051CF204   74 07            JE SHORT _1locke2.051CF20D
 *  051CF206   6A 01            PUSH 0x1
 *  051CF208   E8 C3C30600      CALL _1locke2.0523B5D0
 *  051CF20D   8BCE             MOV ECX,ESI
 *  051CF20F   E8 7CE5FFFF      CALL _1locke2.051CD790
 *  051CF214   6A 01            PUSH 0x1
 *  051CF216   6A 01            PUSH 0x1
 *  051CF218   8BCE             MOV ECX,ESI
 */
bool attach() // attach scenario
{
  ulong startAddress, stopAddress;
  if (!Engine::getModuleMemoryRange(L"resident.dll", &startAddress, &stopAddress))
    return false;

  const uint8_t bytes[] = {
    0x8b,0x44,0x24, 0x04, // 051cf2e0   8b4424 04        mov eax,dword ptr ss:[esp+0x4]
    0x6a, 0x02,           // 051cf2e4   6a 02            push 0x2
    0x6a, 0x00,           // 051cf2e6   6a 00            push 0x0
    0x6a, 0x00,           // 051cf2e8   6a 00            push 0x0
    0x6a, 0x00,           // 051cf2ea   6a 00            push 0x0
    0x50,                 // 051cf2ec   50               push eax
    0xe8  //9ef8ffff      // 051cf2ed   e8 9ef8ffff      call _1locke2.051ceb90
                          // 051cf2f2   c2 0400          retn 0x4
  };
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  if (!addr)
    return false;
  addr += sizeof(bytes) - 1; // move to the short call instruction
  addr = winasm::get_jmp_absaddr(addr);
  return winhook::hook_before((ulong)addr, Private::hookBefore);
}

} // namespace HistoryHook
} // unnamed namespace

/** Public class */

bool RetouchEngine::attach()
{
  if (!ScenarioHook::attach())
    return false;
  if (OtherHook::attach())
    DOUT("other text found");
  else
    DOUT("other text NOT FOUND");

  if (HistoryHook::attach()) {
    DOUT("history text found");
    //h->attachFunction((ulong)::GetTextExtentPoint32A);    // This will cause problem for measuring text width ...
    //h->attachFunction((ulong)::GetTextExtentExPointA);
    //h->attachFunction((ulong)::CharPrevA);
  } else
    DOUT("history text NOT FOUND");

  HijackManager::instance()->attachFunction((ulong)::GetGlyphOutlineA);
  //HijackManager::instance()->attachFunction((ulong)::CreateFontIndirectA); // in resident.dll, but does not work
  return true;
}

// EOF
