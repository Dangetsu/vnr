// debonosu.cc
// 6/18/2015 jichi
#include "engine/model/debonosu.h"
#include "engine/enginecontroller.h"
#include "engine/enginedef.h"
#include "engine/enginehash.h"
#include "engine/engineutil.h"
#include "hijack/hijackmanager.h"
#include "util/textutil.h"
#include "winhook/hookcode.h"
#include "memdbg/memsearch.h"
#include "ntinspect/ntinspect.h"
#include "winasm/winasmdef.h"
#include <qt_windows.h>
#include <QtCore/QRegExp>
#include <QtCore/QSet>
#include <cstdint>

#define DEBUG "model/debonosu"
#include "sakurakit/skdebug.h"

namespace { // unnamed
namespace ScenarioHook {
namespace Private {

  int hookStackIndex_;

  bool hookBefore(winhook::hook_stack *s)
  {
    static QByteArray data_;
    LPCSTR *lpText = (LPCSTR *)&s->stack[hookStackIndex_];

    auto text = *lpText;
    if (!text || !*text)
      return true;

    enum { role = Engine::ScenarioRole, sig = 0 };
    data_ = EngineController::instance()->dispatchTextA(text, role, sig);
    *lpText = data_.constData();
    //::strcpy(text, data.constData());
    return true;
  }

  // Get the address of the scenario function
  ulong findFunctionAddress(ulong startAddress, ulong stopAddress)
  {
    ulong funaddr = NtInspect::getModuleExportFunctionA("kernel32.dll", "lstrcatA");
    if (!funaddr)
      return false;
    funaddr = NtInspect::getProcessImportAddress(funaddr);
    if (!funaddr)
      return false;

    DWORD callinst = s2_farcall_ | (funaddr << 16); // jichi 10/20/2014: 0x15ff, far call dword ptr ds
    funaddr >>= 16;
    for (DWORD i = startAddress; i < stopAddress - 4; i++)
      if (*(DWORD *)i == callinst &&
          *(WORD *)(i + 4) == funaddr && // call dword ptr lstrcatA
          *(BYTE *)(i - 5) == s1_push_) { // 0x68, push $
        DWORD push = *(DWORD *)(i - 4); // the global value being pushed
        for (DWORD j = i + 6, k = j + 0x10; j < k; j++)
          if (*(BYTE *)j == 0xb8 && *(DWORD *)(j + 1) == push)
            if (DWORD addr = MemDbg::findEnclosingAlignedFunction(i, 0x200))
              return addr;
      }
    return 0;
  }

   // 00436B70   57               PUSH EDI
   // 00436B71   8BF8             MOV EDI,EAX ; jichi: use eax instead of ecx as this
  int getHookStackIndex(DWORD addr)
  {
    if (*(BYTE *)addr == s1_push_edi && *(WORD *)(addr + 1) == s2_mov_edi_eax)
      return winhook_stack_indexof(eax); // old game in eax
    return winhook_stack_indexof(ecx);  // new game in ecx
  }

} // namespace Private

/**
 *  Sample game: 神楽花莚譚
 *  base address: 0x0da0000
 *
 *  00DBD9BE   CC               INT3
 *  00DBD9BF   CC               INT3
 *  00DBD9C0   53               PUSH EBX
 *  00DBD9C1   56               PUSH ESI
 *  00DBD9C2   57               PUSH EDI
 *  00DBD9C3   8BF9             MOV EDI,ECX     ; jichi use: ecx as this
 *  00DBD9C5   C605 1830F200 00 MOV BYTE PTR DS:[0xF23018],0x0
 *  00DBD9CC   85FF             TEST EDI,EDI
 *  00DBD9CE   0F84 B8000000    JE .00DBDA8C
 *  00DBD9D4   8B1D 18A4E700    MOV EBX,DWORD PTR DS:[0xE7A418]          ; user32.CharNextA
 *  00DBD9DA   8D9B 00000000    LEA EBX,DWORD PTR DS:[EBX]
 *  00DBD9E0   6A 23            PUSH 0x23
 *  00DBD9E2   57               PUSH EDI
 *  00DBD9E3   E8 DE360600      CALL .00E210C6
 *  00DBD9E8   8BF0             MOV ESI,EAX
 *  00DBD9EA   83C4 08          ADD ESP,0x8
 *  00DBD9ED   85F6             TEST ESI,ESI
 *  00DBD9EF   0F84 87000000    JE .00DBDA7C
 *  00DBD9F5   2BC7             SUB EAX,EDI
 *  00DBD9F7   50               PUSH EAX
 *  00DBD9F8   57               PUSH EDI
 *  00DBD9F9   68 1830F200      PUSH .00F23018
 *  00DBD9FE   E8 2D6D0600      CALL .00E24730
 *  00DBDA03   83C4 0C          ADD ESP,0xC
 *  00DBDA06   BF 00000000      MOV EDI,0x0
 *  00DBDA0B   46               INC ESI
 *  00DBDA0C   74 48            JE SHORT .00DBDA56
 *  00DBDA0E   85F6             TEST ESI,ESI
 *  00DBDA10   74 1F            JE SHORT .00DBDA31
 *  00DBDA12   56               PUSH ESI
 *  00DBDA13   FFD3             CALL EBX
 *  00DBDA15   8BC8             MOV ECX,EAX
 *  00DBDA17   33C0             XOR EAX,EAX
 *  00DBDA19   85C9             TEST ECX,ECX
 *  00DBDA1B   75 08            JNZ SHORT .00DBDA25
 *  00DBDA1D   3846 01          CMP BYTE PTR DS:[ESI+0x1],AL
 *  00DBDA20   0F95C0           SETNE AL
 *  00DBDA23   EB 08            JMP SHORT .00DBDA2D
 *  00DBDA25   2BCE             SUB ECX,ESI
 *  00DBDA27   83F9 01          CMP ECX,0x1
 *  00DBDA2A   0F9FC0           SETG AL
 *  00DBDA2D   85C0             TEST EAX,EAX
 *  00DBDA2F   75 25            JNZ SHORT .00DBDA56
 *  00DBDA31   0FBE06           MOVSX EAX,BYTE PTR DS:[ESI]
 *  00DBDA34   50               PUSH EAX
 *  00DBDA35   E8 54450600      CALL .00E21F8E
 *  00DBDA3A   83C4 04          ADD ESP,0x4
 *  00DBDA3D   85C0             TEST EAX,EAX
 *  00DBDA3F   74 15            JE SHORT .00DBDA56
 *  00DBDA41   0FBE06           MOVSX EAX,BYTE PTR DS:[ESI]
 *  00DBDA44   8D3CBF           LEA EDI,DWORD PTR DS:[EDI+EDI*4]
 *  00DBDA47   56               PUSH ESI
 *  00DBDA48   8D7F E8          LEA EDI,DWORD PTR DS:[EDI-0x18]
 *  00DBDA4B   8D3C78           LEA EDI,DWORD PTR DS:[EAX+EDI*2]
 *  00DBDA4E   FFD3             CALL EBX
 *  00DBDA50   8BF0             MOV ESI,EAX
 *  00DBDA52   85F6             TEST ESI,ESI
 *  00DBDA54  ^75 BC            JNZ SHORT .00DBDA12
 *  00DBDA56   8BCF             MOV ECX,EDI
 *  00DBDA58   E8 53FDFFFF      CALL .00DBD7B0
 *  00DBDA5D   50               PUSH EAX
 *  00DBDA5E   68 1830F200      PUSH .00F23018 ; jichi: pattern starts
 *  00DBDA63   FF15 98A2E700    CALL DWORD PTR DS:[0xE7A298]             ; kernel32.lstrcatA
 *  00DBDA69   8BFE             MOV EDI,ESI
 *  00DBDA6B   85F6             TEST ESI,ESI
 *  00DBDA6D  ^0F85 6DFFFFFF    JNZ .00DBD9E0
 *  00DBDA73   B8 1830F200      MOV EAX,.00F23018 ; jichi: pattern starts
 *  00DBDA78   5F               POP EDI
 *  00DBDA79   5E               POP ESI
 *  00DBDA7A   5B               POP EBX
 *  00DBDA7B   C3               RETN
 *  00DBDA7C   85FF             TEST EDI,EDI
 *  00DBDA7E   74 0C            JE SHORT .00DBDA8C
 *  00DBDA80   57               PUSH EDI
 *  00DBDA81   68 1830F200      PUSH .00F23018
 *  00DBDA86   FF15 98A2E700    CALL DWORD PTR DS:[0xE7A298]             ; kernel32.lstrcatA
 *  00DBDA8C   5F               POP EDI
 *  00DBDA8D   5E               POP ESI
 *  00DBDA8E   B8 1830F200      MOV EAX,.00F23018
 *  00DBDA93   5B               POP EBX
 *  00DBDA94   C3               RETN
 *  00DBDA95   CC               INT3
 *  00DBDA96   CC               INT3
 *  00DBDA97   CC               INT3
 *  00DBDA98   CC               INT3
 *  00DBDA99   CC               INT3
 *
 *  Sample game: 神楽道中記
 *  00436B6E   CC               INT3
 *  00436B6F   CC               INT3
 *  00436B70   57               PUSH EDI
 *  00436B71   8BF8             MOV EDI,EAX ; jichi: use eax instead of ecx as this
 *  00436B73   85FF             TEST EDI,EDI
 *  00436B75   C605 60465B00 00 MOV BYTE PTR DS:[0x5B4660],0x0
 *  00436B7C   0F84 02010000    JE .00436C84
 *  00436B82   55               PUSH EBP
 *  00436B83   8B2D 68445400    MOV EBP,DWORD PTR DS:[0x544468]          ; user32.CharNextA
 *  00436B89   56               PUSH ESI
 *  00436B8A   8D9B 00000000    LEA EBX,DWORD PTR DS:[EBX]
 *  00436B90   6A 23            PUSH 0x23
 *  00436B92   57               PUSH EDI
 *  00436B93   E8 E8F40B00      CALL .004F6080
 *  00436B98   8BF0             MOV ESI,EAX
 *  00436B9A   83C4 08          ADD ESP,0x8
 *  00436B9D   85F6             TEST ESI,ESI
 *  00436B9F   0F84 CD000000    JE .00436C72
 *  00436BA5   2BC7             SUB EAX,EDI
 *  00436BA7   50               PUSH EAX
 *  00436BA8   57               PUSH EDI
 *  00436BA9   68 60465B00      PUSH .005B4660
 *  00436BAE   E8 7DF30B00      CALL .004F5F30
 *  00436BB3   83C4 0C          ADD ESP,0xC
 *  00436BB6   83C6 01          ADD ESI,0x1
 *  00436BB9   BF 00000000      MOV EDI,0x0
 *  00436BBE   74 46            JE SHORT .00436C06
 *  00436BC0   85F6             TEST ESI,ESI
 *  00436BC2   74 1F            JE SHORT .00436BE3
 *  00436BC4   56               PUSH ESI
 *  00436BC5   FFD5             CALL EBP
 *  00436BC7   85C0             TEST EAX,EAX
 *  00436BC9   75 08            JNZ SHORT .00436BD3
 *  00436BCB   3846 01          CMP BYTE PTR DS:[ESI+0x1],AL
 *  00436BCE   0F95C0           SETNE AL
 *  00436BD1   EB 0C            JMP SHORT .00436BDF
 *  00436BD3   2BC6             SUB EAX,ESI
 *  00436BD5   33C9             XOR ECX,ECX
 *  00436BD7   83F8 01          CMP EAX,0x1
 *  00436BDA   0F9FC1           SETG CL
 *  00436BDD   8BC1             MOV EAX,ECX
 *  00436BDF   85C0             TEST EAX,EAX
 *  00436BE1   75 23            JNZ SHORT .00436C06
 *  00436BE3   0FBE16           MOVSX EDX,BYTE PTR DS:[ESI]
 *  00436BE6   52               PUSH EDX
 *  00436BE7   E8 61F10B00      CALL .004F5D4D
 *  00436BEC   83C4 04          ADD ESP,0x4
 *  00436BEF   85C0             TEST EAX,EAX
 *  00436BF1   74 13            JE SHORT .00436C06
 *  00436BF3   0FBE0E           MOVSX ECX,BYTE PTR DS:[ESI]
 *  00436BF6   8D04BF           LEA EAX,DWORD PTR DS:[EDI+EDI*4]
 *  00436BF9   56               PUSH ESI
 *  00436BFA   8D7C41 D0        LEA EDI,DWORD PTR DS:[ECX+EAX*2-0x30]
 *  00436BFE   FFD5             CALL EBP
 *  00436C00   8BF0             MOV ESI,EAX
 *  00436C02   85F6             TEST ESI,ESI
 *  00436C04  ^75 BE            JNZ SHORT .00436BC4
 *  00436C06   85FF             TEST EDI,EDI
 *  00436C08   C605 60365B00 00 MOV BYTE PTR DS:[0x5B3660],0x0
 *  00436C0F   74 20            JE SHORT .00436C31
 *  00436C11   57               PUSH EDI
 *  00436C12   68 B85C5400      PUSH .00545CB8                           ; ASCII "GetGlobalWord: error. no(%d)"
 *  00436C17   E8 D44C0A00      CALL .004DB8F0
 *  00436C1C   83C4 08          ADD ESP,0x8
 *  00436C1F   68 58545400      PUSH .00545458
 *  00436C24   68 60365B00      PUSH .005B3660
 *  00436C29   FF15 3C425400    CALL DWORD PTR DS:[0x54423C]             ; kernel32.lstrcpyA
 *  00436C2F   EB 1E            JMP SHORT .00436C4F
 *  00436C31   68 B05C5400      PUSH .00545CB0                           ; ASCII "Result"
 *  00436C36   E8 F5EBFFFF      CALL .00435830
 *  00436C3B   50               PUSH EAX
 *  00436C3C   68 9C5C5400      PUSH .00545C9C                           ; ASCII "%d"
 *  00436C41   68 60365B00      PUSH .005B3660
 *  00436C46   FF15 AC445400    CALL DWORD PTR DS:[0x5444AC]             ; user32.wsprintfA
 *  00436C4C   83C4 10          ADD ESP,0x10
 *  00436C4F   68 60365B00      PUSH .005B3660
 *  00436C54   68 60465B00      PUSH .005B4660
 *  00436C59   FF15 40425400    CALL DWORD PTR DS:[0x544240]             ; kernel32.lstrcatA
 *  00436C5F   85F6             TEST ESI,ESI
 *  00436C61   8BFE             MOV EDI,ESI
 *  00436C63  ^0F85 27FFFFFF    JNZ .00436B90
 *  00436C69   5E               POP ESI
 *  00436C6A   5D               POP EBP
 *  00436C6B   B8 60465B00      MOV EAX,.005B4660
 *  00436C70   5F               POP EDI
 *  00436C71   C3               RETN
 *  00436C72   85FF             TEST EDI,EDI
 *  00436C74   74 0C            JE SHORT .00436C82
 *  00436C76   57               PUSH EDI
 *  00436C77   68 60465B00      PUSH .005B4660
 *  00436C7C   FF15 40425400    CALL DWORD PTR DS:[0x544240]             ; kernel32.lstrcatA
 *  00436C82   5E               POP ESI
 *  00436C83   5D               POP EBP
 *  00436C84   B8 60465B00      MOV EAX,.005B4660
 *  00436C89   5F               POP EDI
 *  00436C8A   C3               RETN
 *  00436C8B   CC               INT3
 *  00436C8C   CC               INT3
 */
bool attach(ulong startAddress, ulong stopAddress)
{
  ulong addr = Private::findFunctionAddress(startAddress, stopAddress);
  if (!addr)
    return false;

  Private::hookStackIndex_ = Private::getHookStackIndex(addr);

  //ulong call = MemDbg::findNearCallAddress(addr, startAddress, stopAddress);
  //if (!call)
  //  return false;

  //0x436b70
  //0x440743
  return winhook::hook_before(addr, Private::hookBefore);

  //int count = 0;
  //auto fun = [&count](ulong addr) -> bool {
  //  if (winhook::hook_before(addr, Private::hookBefore)) {
  //    // 0xc483 = add esp, $  old Debonosu game
  //    Private::version_ = *(WORD *)(addr + 4) == 0xc483 ? Private::OldVersion : Private::NewVersion;
  //    count++;
  //  }
  //  return true; // replace all functions
  //};
  //MemDbg::iterNearCallAddress(fun, addr, startAddress, stopAddress);
  //DOUT("call number =" << count);
  //return count;
}

//bool isOldVersion() // old Debonosu games
//{ return Private::textOffset_ == Private::TextOffsetEax; }

} // namespace ScenarioHook

namespace NameHook { // scenario with name, but scenario are rendered line-by-line and not good place to hook
  QSet<QByteArray> texts_;

namespace Private {
  bool hookBefore(winhook::hook_stack *s)
  {
    static QByteArray data_;
    auto text = (LPCSTR)s->ecx;
    if (!text || !*text)
      return true;

    enum { role = Engine::NameRole, sig = 0 };
    data_ = EngineController::instance()->dispatchTextA(text, role, sig);
    texts_.insert(data_);
    s->ecx = (ulong)data_.constData();
    return true;
  }
} // namespace Private
/**
 *  Sample games: 神楽花莚譚, 偽骸のアルルーナ, 戦場のフォークロア
 *  FIXME: This hook does not work for some old games such as 神楽道中記.
 *
 *  Functions found by debugging lstrcatA.
 *
 *  0032E3DB   CC               INT3
 *  0032E3DC   CC               INT3
 *  0032E3DD   CC               INT3
 *  0032E3DE   CC               INT3
 *  0032E3DF   CC               INT3
 *  0032E3E0   55               PUSH EBP ; jichi: text in arg1
 *  0032E3E1   8BEC             MOV EBP,ESP
 *  0032E3E3   6A FF            PUSH -0x1
 *  0032E3E5   68 19263E00      PUSH .003E2619
 *  0032E3EA   64:A1 00000000   MOV EAX,DWORD PTR FS:[0]
 *  0032E3F0   50               PUSH EAX
 *  0032E3F1   B8 04140000      MOV EAX,0x1404
 *  0032E3F6   64:8925 00000000 MOV DWORD PTR FS:[0],ESP
 *  0032E3FD   E8 8E310700      CALL .003A1590
 *  0032E402   53               PUSH EBX
 *  0032E403   56               PUSH ESI
 *  0032E404   8B75 24          MOV ESI,DWORD PTR SS:[EBP+0x24]
 *  0032E407   57               PUSH EDI
 *  0032E408   8BFA             MOV EDI,EDX
 *  0032E40A   897D E0          MOV DWORD PTR SS:[EBP-0x20],EDI
 *  0032E40D   894D E8          MOV DWORD PTR SS:[EBP-0x18],ECX
 *  0032E410   C745 C8 01000000 MOV DWORD PTR SS:[EBP-0x38],0x1
 *  0032E417   85F6             TEST ESI,ESI
 *  0032E419   75 11            JNZ SHORT .0032E42C
 *  0032E41B   A1 F4EF4600      MOV EAX,DWORD PTR DS:[0x46EFF4]
 *  0032E420   C1E0 08          SHL EAX,0x8
 *  0032E423   8BB0 CC6D4700    MOV ESI,DWORD PTR DS:[EAX+0x476DCC]
 *  0032E429   8975 24          MOV DWORD PTR SS:[EBP+0x24],ESI
 *  0032E42C   8B46 04          MOV EAX,DWORD PTR DS:[ESI+0x4]
 *  0032E42F   F640 48 02       TEST BYTE PTR DS:[EAX+0x48],0x2
 *  0032E433   74 16            JE SHORT .0032E44B
 *  0032E435   8B4D 08          MOV ECX,DWORD PTR SS:[EBP+0x8]
 *  0032E438   8B5D 10          MOV EBX,DWORD PTR SS:[EBP+0x10]
 *  0032E43B   51               PUSH ECX
 *  0032E43C   53               PUSH EBX
 *  0032E43D   8BCE             MOV ECX,ESI
 *  0032E43F   E8 1CFCFFFF      CALL .0032E060
 *  0032E444   83C4 08          ADD ESP,0x8
 *  0032E447   8BC8             MOV ECX,EAX
 *  0032E449   EB 35            JMP SHORT .0032E480
 *  0032E44B   E8 B09FFFFF      CALL .00328400
 *  0032E450   66:0F6E05 50ED46>MOVD MM0,DWORD PTR DS:[0x46ED50]
 *  0032E458   F3:              PREFIX REP:                              ; Superfluous prefix
 *  0032E459   0FE6             ???                                      ; Unknown command
 *  0032E45B   C08D 4802F20F 59 ROR BYTE PTR SS:[EBP+0xFF20248],0x59     ; Shift constant out of range 1..31
 *  0032E462   05 C0C64200      ADD EAX,.0042C6C0
 *  0032E467   8B46 04          MOV EAX,DWORD PTR DS:[ESI+0x4]
 *  0032E46A   8B70 64          MOV ESI,DWORD PTR DS:[EAX+0x64]
 *  0032E46D   F2:              PREFIX REPNE:                            ; Superfluous prefix
 *  0032E46E   0F2CC0           CVTTPS2PI MM0,XMM0
 *  0032E471   3BF0             CMP ESI,EAX
 *  0032E473   74 08            JE SHORT .0032E47D
 *  0032E475   0FAFC1           IMUL EAX,ECX
 *  0032E478   99               CDQ
 *  0032E479   F7FE             IDIV ESI
 *  0032E47B   8BC8             MOV ECX,EAX
 *  0032E47D   8B5D 10          MOV EBX,DWORD PTR SS:[EBP+0x10]
 *  0032E480   837D 30 03       CMP DWORD PTR SS:[EBP+0x30],0x3
 *  0032E484   1BC0             SBB EAX,EAX
 *  0032E486   83C0 02          ADD EAX,0x2
 *  0032E489   0FAFC1           IMUL EAX,ECX
 *  0032E48C   807D 28 00       CMP BYTE PTR SS:[EBP+0x28],0x0
 *  0032E490   8945 C4          MOV DWORD PTR SS:[EBP-0x3C],EAX
 *  0032E493   8D45 24          LEA EAX,DWORD PTR SS:[EBP+0x24]
 *  0032E496   8945 A8          MOV DWORD PTR SS:[EBP-0x58],EAX
 *  0032E499   74 3F            JE SHORT .0032E4DA
 *  0032E49B   F2:              PREFIX REPNE:                            ; Superfluous prefix
 *  0032E49C   0F1005 D86F4700  MOVUPS XMM0,DQWORD PTR DS:[0x476FD8]
 *  0032E4A3   0F57C9           XORPS XMM1,XMM1
 *  0032E4A6   66:0F2FC8        COMISS XMM1,XMM0
 *  0032E4AA   76 24            JBE SHORT .0032E4D0
 *  0032E4AC   B9 0C000000      MOV ECX,0xC
 *  0032E4B1   390D 485E4600    CMP DWORD PTR DS:[0x465E48],ECX
 *  0032E4B7   0F420D 485E4600  CMOVB ECX,DWORD PTR DS:[0x465E48]
 *  0032E4BE   8D04CD 00000000  LEA EAX,DWORD PTR DS:[ECX*8]
 *  0032E4C5   B9 084C4200      MOV ECX,.00424C08
 *  0032E4CA   2BC8             SUB ECX,EAX
 *  0032E4CC   F2:              PREFIX REPNE:                            ; Superfluous prefix
 *  0032E4CD   0F1001           MOVUPS XMM0,DQWORD PTR DS:[ECX]
 *  0032E4D0   66:0F2FC1        COMISS XMM0,XMM1
 *  0032E4D4   C645 2B 01       MOV BYTE PTR SS:[EBP+0x2B],0x1
 *  0032E4D8   77 04            JA SHORT .0032E4DE
 *  0032E4DA   C645 2B 00       MOV BYTE PTR SS:[EBP+0x2B],0x0
 *  0032E4DE   0F57C0           XORPS XMM0,XMM0
 *  0032E4E1   66:0FD6          ???                                      ; Unknown command
 *  0032E4E4   45               INC EBP
 *  0032E4E5   B0 85            MOV AL,0x85
 *  0032E4E7   DB               ???                                      ; Unknown command
 *  0032E4E8   74 13            JE SHORT .0032E4FD
 *  0032E4EA   8BCB             MOV ECX,EBX
 *  0032E4EC   8D51 01          LEA EDX,DWORD PTR DS:[ECX+0x1]
 *  0032E4EF   90               NOP
 *  0032E4F0   8A01             MOV AL,BYTE PTR DS:[ECX]
 *  0032E4F2   41               INC ECX
 *  0032E4F3   84C0             TEST AL,AL
 *  0032E4F5  ^75 F9            JNZ SHORT .0032E4F0
 *  0032E4F7   2BCA             SUB ECX,EDX
 *  0032E4F9   03CB             ADD ECX,EBX
 *  0032E4FB   EB 02            JMP SHORT .0032E4FF
 *  0032E4FD   33C9             XOR ECX,ECX
 *  0032E4FF   8B55 24          MOV EDX,DWORD PTR SS:[EBP+0x24]
 *  0032E502   8D42 1C          LEA EAX,DWORD PTR DS:[EDX+0x1C]
 *  0032E505   50               PUSH EAX
 *  0032E506   FF72 0C          PUSH DWORD PTR DS:[EDX+0xC]
 *  0032E509   8D45 B0          LEA EAX,DWORD PTR SS:[EBP-0x50]
 *  0032E50C   51               PUSH ECX
 *  0032E50D   8B4A 04          MOV ECX,DWORD PTR DS:[EDX+0x4]
 *  0032E510   53               PUSH EBX
 *  0032E511   50               PUSH EAX
 *  0032E512   E8 7918F7FF      CALL .0029FD90
 *  0032E517   807D 2B 00       CMP BYTE PTR SS:[EBP+0x2B],0x0
 *  0032E51B   8B45 B0          MOV EAX,DWORD PTR SS:[EBP-0x50]
 *  0032E51E   8945 D8          MOV DWORD PTR SS:[EBP-0x28],EAX
 *  0032E521   74 20            JE SHORT .0032E543
 *  0032E523   803B 00          CMP BYTE PTR DS:[EBX],0x0
 *  0032E526   74 1B            JE SHORT .0032E543
 *  0032E528   8B4D E8          MOV ECX,DWORD PTR SS:[EBP-0x18]
 *  0032E52B   6A 00            PUSH 0x0
 *  0032E52D   53               PUSH EBX
 *  0032E52E   8B5D 14          MOV EBX,DWORD PTR SS:[EBP+0x14]
 *  0032E531   53               PUSH EBX
 *  0032E532   FF75 24          PUSH DWORD PTR SS:[EBP+0x24]
 *  0032E535   03C1             ADD EAX,ECX
 *  0032E537   57               PUSH EDI
 *  0032E538   50               PUSH EAX
 *  0032E539   FF75 20          PUSH DWORD PTR SS:[EBP+0x20]
 *  0032E53C   E8 9F9BFFFF      CALL .003280E0
 *  0032E541   EB 13            JMP SHORT .0032E556
 *  0032E543   8B4D E8          MOV ECX,DWORD PTR SS:[EBP-0x18]
 *  0032E546   53               PUSH EBX
 *  0032E547   FF75 24          PUSH DWORD PTR SS:[EBP+0x24]
 *  0032E54A   03C1             ADD EAX,ECX
 *  0032E54C   57               PUSH EDI
 *  0032E54D   50               PUSH EAX
 *  0032E54E   E8 7D9CFFFF      CALL .003281D0
 *  0032E553   8B5D 14          MOV EBX,DWORD PTR SS:[EBP+0x14]
 *  0032E556   807D 2B 00       CMP BYTE PTR SS:[EBP+0x2B],0x0
 *  0032E55A   895D A4          MOV DWORD PTR SS:[EBP-0x5C],EBX
 *  0032E55D   74 11            JE SHORT .0032E570
 *  0032E55F   8B75 18          MOV ESI,DWORD PTR SS:[EBP+0x18]
 *  0032E562   85F6             TEST ESI,ESI
 *  0032E564   74 0A            JE SHORT .0032E570
 *  0032E566   8B06             MOV EAX,DWORD PTR DS:[ESI]
 *  0032E568   85C0             TEST EAX,EAX
 *  0032E56A   0F45D8           CMOVNE EBX,EAX
 *  0032E56D   895D 14          MOV DWORD PTR SS:[EBP+0x14],EBX
 *  0032E570   FF75 10          PUSH DWORD PTR SS:[EBP+0x10]
 *  0032E573   FF15 10A33E00    CALL DWORD PTR DS:[0x3EA310]             ; kernel32.lstrlenA
 *  0032E579   8945 C0          MOV DWORD PTR SS:[EBP-0x40],EAX
 *  0032E57C   8B35 18A43E00    MOV ESI,DWORD PTR DS:[0x3EA418]          ; user32.CharNextA
 *  0032E582   C645 33 00       MOV BYTE PTR SS:[EBP+0x33],0x0
 *  0032E586   8B55 08          MOV EDX,DWORD PTR SS:[EBP+0x8]
 *  0032E589   8A0A             MOV CL,BYTE PTR DS:[EDX]
 *  0032E58B   84C9             TEST CL,CL
 *  0032E58D   74 0E            JE SHORT .0032E59D
 *  0032E58F   8B45 C4          MOV EAX,DWORD PTR SS:[EBP-0x3C]
 *  0032E592   03C0             ADD EAX,EAX
 *  0032E594   3945 C0          CMP DWORD PTR SS:[EBP-0x40],EAX
 *  0032E597   0F8D EC0A0000    JGE .0032F089
 *  0032E59D   807D 1C 00       CMP BYTE PTR SS:[EBP+0x1C],0x0
 *  0032E5A1   74 3D            JE SHORT .0032E5E0
 *  0032E5A3   80F9 5C          CMP CL,0x5C
 *  0032E5A6   75 26            JNZ SHORT .0032E5CE
 *  0032E5A8   8A42 01          MOV AL,BYTE PTR DS:[EDX+0x1]
 *  0032E5AB   3C 72            CMP AL,0x72
 *  0032E5AD   75 17            JNZ SHORT .0032E5C6
 *  0032E5AF   384A 02          CMP BYTE PTR DS:[EDX+0x2],CL
 *  0032E5B2   75 0A            JNZ SHORT .0032E5BE
 *  0032E5B4   807A 03 6E       CMP BYTE PTR DS:[EDX+0x3],0x6E
 *  0032E5B8   0F84 760A0000    JE .0032F034
 *  0032E5BE   3C 72            CMP AL,0x72
 *  0032E5C0   0F84 B00A0000    JE .0032F076
 *  0032E5C6   3C 6E            CMP AL,0x6E
 *  0032E5C8   0F84 A80A0000    JE .0032F076
 *  0032E5CE   80F9 0D          CMP CL,0xD
 *  0032E5D1   0F84 920A0000    JE .0032F069
 *  0032E5D7   80F9 0A          CMP CL,0xA
 *  0032E5DA   0F84 8F0A0000    JE .0032F06F
 *  0032E5E0   84C9             TEST CL,CL
 *  0032E5E2   0F84 DC0A0000    JE .0032F0C4
 *  0032E5E8   52               PUSH EDX
 *  0032E5E9   FFD6             CALL ESI
 *  0032E5EB   8B4D 08          MOV ECX,DWORD PTR SS:[EBP+0x8]
 *  0032E5EE   8BF8             MOV EDI,EAX
 *  0032E5F0   2BC1             SUB EAX,ECX
 *  0032E5F2   8945 DC          MOV DWORD PTR SS:[EBP-0x24],EAX
 *  0032E5F5   40               INC EAX
 *  0032E5F6   50               PUSH EAX
 *  0032E5F7   51               PUSH ECX
 *  0032E5F8   8D45 EC          LEA EAX,DWORD PTR SS:[EBP-0x14]
 *  0032E5FB   50               PUSH EAX
 *  0032E5FC   FF15 BCA23E00    CALL DWORD PTR DS:[0x3EA2BC]             ; kernel32.lstrcpynA
 *  0032E602   837D DC 01       CMP DWORD PTR SS:[EBP-0x24],0x1
 *  0032E606   8A4D EC          MOV CL,BYTE PTR SS:[EBP-0x14]
 *  0032E609   897D 08          MOV DWORD PTR SS:[EBP+0x8],EDI
 *  0032E60C   0F85 BF000000    JNZ .0032E6D1
 *  0032E612   80F9 20          CMP CL,0x20
 *  0032E615   72 09            JB SHORT .0032E620
 *  0032E617   80F9 7F          CMP CL,0x7F
 *  0032E61A   0F82 B1000000    JB .0032E6D1
 *  0032E620   B1 20            MOV CL,0x20
 *  0032E622   884D EC          MOV BYTE PTR SS:[EBP-0x14],CL
 *  0032E625   C745 C8 00000000 MOV DWORD PTR SS:[EBP-0x38],0x0
 *  0032E62C   8B35 10A33E00    MOV ESI,DWORD PTR DS:[0x3EA310]          ; kernel32.lstrlenA
 *  0032E632   8B45 C4          MOV EAX,DWORD PTR SS:[EBP-0x3C]
 *  0032E635   8D0445 FEFFFFFF  LEA EAX,DWORD PTR DS:[EAX*2-0x2]
 *  0032E63C   3945 C0          CMP DWORD PTR SS:[EBP-0x40],EAX
 *  0032E63F   7C 52            JL SHORT .0032E693
 *  0032E641   8D45 EC          LEA EAX,DWORD PTR SS:[EBP-0x14]
 *  0032E644   50               PUSH EAX
 *  0032E645   FF35 E0714100    PUSH DWORD PTR DS:[0x4171E0]             ; .0041FF08
 *  0032E64B   E8 CA570600      CALL .00393E1A
 *
 *  ....
 *
 *  0032F637   E8 A47AF7FF      CALL .002A70E0
 *  0032F63C   56               PUSH ESI
 *  0032F63D   E8 9EFF0500      CALL .0038F5E0
 *  0032F642   83C4 04          ADD ESP,0x4
 *  0032F645   A1 F4EF4600      MOV EAX,DWORD PTR DS:[0x46EFF4]
 *  0032F64A   C1E0 08          SHL EAX,0x8
 *  0032F64D   5F               POP EDI
 *  0032F64E   5E               POP ESI
 *  0032F64F   C780 C06D4700 00>MOV DWORD PTR DS:[EAX+0x476DC0],0x0
 *  0032F659   32C0             XOR AL,AL
 *  0032F65B   5B               POP EBX
 *  0032F65C   8BE5             MOV ESP,EBP
 *  0032F65E   5D               POP EBP
 *  0032F65F   C3               RETN
 *  0032F660   55               PUSH EBP    ; jichi: name text in ecx, which could be zero though
 *  0032F661   8BEC             MOV EBP,ESP
 *  0032F663   81EC 2C080000    SUB ESP,0x82C
 *  0032F669   8B45 08          MOV EAX,DWORD PTR SS:[EBP+0x8]
 *  0032F66C   53               PUSH EBX
 *  0032F66D   56               PUSH ESI
 *  0032F66E   8BF1             MOV ESI,ECX
 *  0032F670   85C0             TEST EAX,EAX
 *  0032F672   8D4D F0          LEA ECX,DWORD PTR SS:[EBP-0x10]
 *  0032F675   0F45C8           CMOVNE ECX,EAX
 *  0032F678   57               PUSH EDI
 *  0032F679   C745 F0 00000000 MOV DWORD PTR SS:[EBP-0x10],0x0
 *  0032F680   8B01             MOV EAX,DWORD PTR DS:[ECX]
 *  0032F682   68 00080000      PUSH 0x800
 *  0032F687   8945 EC          MOV DWORD PTR SS:[EBP-0x14],EAX
 *  0032F68A   8D85 D8F7FFFF    LEA EAX,DWORD PTR SS:[EBP-0x828]
 *  0032F690   6A 00            PUSH 0x0
 *  0032F692   50               PUSH EAX
 *  0032F693   8955 F8          MOV DWORD PTR SS:[EBP-0x8],EDX
 *  0032F696   894D F4          MOV DWORD PTR SS:[EBP-0xC],ECX
 *  0032F699   E8 525D0600      CALL .003953F0
 *  0032F69E   8B1D F4EF4600    MOV EBX,DWORD PTR DS:[0x46EFF4]
 *  0032F6A4   8BCB             MOV ECX,EBX
 *  0032F6A6   C1E1 08          SHL ECX,0x8
 *  0032F6A9   83C4 0C          ADD ESP,0xC
 *  0032F6AC   83B9 346E4700 00 CMP DWORD PTR DS:[ECX+0x476E34],0x0
 *  0032F6B3   7D 0A            JGE SHORT .0032F6BF
 *  0032F6B5   C781 346E4700 00>MOV DWORD PTR DS:[ECX+0x476E34],0x0
 *  0032F6BF   8B55 10          MOV EDX,DWORD PTR SS:[EBP+0x10]
 *  0032F6C2   803A 00          CMP BYTE PTR DS:[EDX],0x0
 *  0032F6C5   74 67            JE SHORT .0032F72E
 *  0032F6C7   83B9 346E4700 00 CMP DWORD PTR DS:[ECX+0x476E34],0x0
 *  0032F6CE   0F94C0           SETE AL
 *  0032F6D1   8802             MOV BYTE PTR DS:[EDX],AL
 *  0032F6D3   84C0             TEST AL,AL
 *  0032F6D5   74 57            JE SHORT .0032F72E
 *  0032F6D7   8B89 C06D4700    MOV ECX,DWORD PTR DS:[ECX+0x476DC0]
 *  0032F6DD   68 000000FF      PUSH 0xFF000000
 *  0032F6E2   6A 00            PUSH 0x0
 *  0032F6E4   E8 278BF7FF      CALL .002A8210
 *  0032F6E9   FF75 14          PUSH DWORD PTR SS:[EBP+0x14]
 *  0032F6EC   A1 445E4600      MOV EAX,DWORD PTR DS:[0x465E44]
 *  0032F6F1   8B15 A46F4700    MOV EDX,DWORD PTR DS:[0x476FA4]
 *  0032F6F7   51               PUSH ECX
 *  0032F6F8   8B0D A06F4700    MOV ECX,DWORD PTR DS:[0x476FA0]
 *  0032F6FE   A3 1CF44700      MOV DWORD PTR DS:[0x47F41C],EAX
 *  0032F703   E8 F8E70000      CALL .0033DF00
 *  0032F708   A1 A06F4700      MOV EAX,DWORD PTR DS:[0x476FA0]
 *  0032F70D   8B1D F4EF4600    MOV EBX,DWORD PTR DS:[0x46EFF4]
 *  0032F713   0F57C0           XORPS XMM0,XMM0
 *  0032F716   83C4 08          ADD ESP,0x8
 *  0032F719   A3 A46F4700      MOV DWORD PTR DS:[0x476FA4],EAX
 *  0032F71E   F2:              PREFIX REPNE:                            ; Superfluous prefix
 *  0032F71F   0F1105 B86F4700  MOVUPS DQWORD PTR DS:[0x476FB8],XMM0
 *  0032F726   F2:              PREFIX REPNE:                            ; Superfluous prefix
 *  0032F727   0F1105 B06F4700  MOVUPS DQWORD PTR DS:[0x476FB0],XMM0
 *  0032F72E   807D 14 00       CMP BYTE PTR SS:[EBP+0x14],0x0
 *  0032F732   0F84 15010000    JE .0032F84D
 *  0032F738   85F6             TEST ESI,ESI
 *  0032F73A   0F84 0D010000    JE .0032F84D
 *  0032F740   803E 00          CMP BYTE PTR DS:[ESI],0x0
 *  0032F743   0F84 04010000    JE .0032F84D
 *  0032F749   8BCE             MOV ECX,ESI
 *  0032F74B   C645 17 01       MOV BYTE PTR SS:[EBP+0x17],0x1
 *  0032F74F   E8 2CD8FEFF      CALL .0031CF80
 *  0032F754   8BF8             MOV EDI,EAX
 *  0032F756   56               PUSH ESI
 *  0032F757   8D4F 20          LEA ECX,DWORD PTR DS:[EDI+0x20]
 *  0032F75A   51               PUSH ECX
 *  0032F75B   68 68404900      PUSH .00494068
 *  0032F760   E8 350F0600      CALL .0039069A
 *  0032F765   66:0F6E05 50ED46>MOVD MM0,DWORD PTR DS:[0x46ED50]
 *  0032F76D   8B0D F4EF4600    MOV ECX,DWORD PTR DS:[0x46EFF4]
 *  0032F773   F3:              PREFIX REP:                              ; Superfluous prefix
 *  0032F774   0FE6             ???                                      ; Unknown command
 *  0032F776   C0C1 E1          ROL CL,0xE1                              ; Shift constant out of range 1..31
 *  0032F779   08F2             OR DL,DH
 *  0032F77B   0F5905 68D84200  MULPS XMM0,DQWORD PTR DS:[0x42D868]
 *  0032F782   8B99 946D4700    MOV EBX,DWORD PTR DS:[ECX+0x476D94]
 *  0032F788   8BB1 A06D4700    MOV ESI,DWORD PTR DS:[ECX+0x476DA0]
 *  0032F78E   83C4 0C          ADD ESP,0xC
 */
bool attach(ulong startAddress, ulong stopAddress)
{
  const uint8_t bytes[] = {
                     // 0032f659   32c0             xor al,al
                     // 0032f65b   5b               pop ebx
                     // 0032f65c   8be5             mov esp,ebp
                     // 0032f65e   5d               pop ebp
                     // 0032f65f   c3               retn
    0x55,            // 0032f660   55               push ebp    ; jichi: name text in ecx, which could be zero though
    0x8b,0xec,       // 0032f661   8bec             mov ebp,esp
    0x81,0xec, XX4,  // 0032f663   81ec 2c080000    sub esp,0x82c
    0x8b,0x45, 0x08, // 0032f669   8b45 08          mov eax,dword ptr ss:[ebp+0x8]
    0x53,            // 0032f66c   53               push ebx
    0x56,            // 0032f66d   56               push esi
    0x8b,0xf1,       // 0032f66e   8bf1             mov esi,ecx
    0x85,0xc0,       // 0032f670   85c0             test eax,eax
    0x8d,0x4d, 0xf0, // 0032f672   8d4d f0          lea ecx,dword ptr ss:[ebp-0x10]
    0x0f,0x45,0xc8,  // 0032f675   0f45c8           cmovne ecx,eax
    0x57             // 0032f678   57               push edi
  };
  ulong addr = MemDbg::matchBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  if (!addr)
    return false;
  return winhook::hook_before(addr, Private::hookBefore);
}

} // namespace NameHook

namespace OtherHook {

namespace Private {

  struct FunctionStack
  {
    DWORD retaddr;
    LPDWORD unknown[4]; // arg1~4
    LPCSTR begin,   // arg5, start of the text
           end;     // arg6, stop of the text, usually \0

    bool isValid() const
    {
      int size = end - begin;
      return size > 2 // avoid translating individual character
          && Engine::isAddressWritable(begin, size);
    }
  };

  //inline const char *ltrim(const char *s) // skip leading "+" for choices
  //{
  //  for (; *s; s++)
  //    if ((signed char)*s < 0)
  //      break;
  //  return s;
  //}

  bool hookBefore(winhook::hook_stack *s)
  {
    static QByteArray data_;
    auto args = (FunctionStack *)s->stack; // new game, text in arg2 for the caller of GetTextExtentPoint32A
    if (!args->isValid())
      return true;

    QByteArray oldData(args->begin, args->end - args->begin);
    if (NameHook::texts_.contains(oldData)) // avoid re-translate character name
      return true;

    //auto text = ltrim(args->begin);
    //text = args->begin;
    //if (text != args->begin) {
    //  if (text >= args->end)
    //    return true;
    //  oldData = text;
    //}

    enum { role = Engine::OtherRole };
    auto split = args->retaddr;
    auto sig = Engine::hashThreadSignature(role, split);
    QByteArray newData = EngineController::instance()->dispatchTextA(oldData, role, sig);
    if (newData == oldData)
      return true;
    //if (text != args->begin)
    //  newData.prepend(args->begin, text - args->begin);
    data_ = newData;
    args->begin = data_.constData();
    args->end = args->begin + data_.size();
    return true;
  }

} // namespace Private

/**
 *  Sample game: 神楽花莚譚
 *  FIXME: This hook does not work for some old games such as 神楽道中記.
 *  FIXME: It does not hook for 偽骸のアルルーナ and 戦場のフォークロア as well.
 *
 *  Found by tracing GdipDrawString
 *
 *  0058E0E4   0005DC40   RETURN to .0005DC40 from .0010F510
 *  0058E0E8   00000030
 *  0058E0EC   00000073
 *  0058E0F0   0058E120
 *  0058E0F4   00000001
 *  0058E0F8   1984B378 ; jichi: text begin, arg5
 *  0058E0FC   1984B380 ; jichi: text end, arg6
 *  0058E100   021D3DF0
 *  0058E104   00000000
 *  0058E108   FFA0A0A0
 *  0058E10C   021D3E04
 *  0058E110   021D3E08
 *  0058E114   021D3E0C
 *  0058E118   0AFA2FB8
 *  0058E11C   00000030
 *  0058E120   00000000
 *  0058E124   00000000
 *
 *  0010F50E   CC               INT3
 *  0010F50F   CC               INT3
 *  0010F510   55               PUSH EBP
 *  0010F511   8BEC             MOV EBP,ESP
 *  0010F513   83E4 C0          AND ESP,0xFFFFFFC0
 *  0010F516   81EC B4000000    SUB ESP,0xB4
 *  0010F51C   8B45 2C          MOV EAX,DWORD PTR SS:[EBP+0x2C]
 *  0010F51F   53               PUSH EBX
 *  0010F520   8B5D 30          MOV EBX,DWORD PTR SS:[EBP+0x30]
 *  0010F523   56               PUSH ESI
 *  0010F524   8BF1             MOV ESI,ECX
 *  0010F526   8B08             MOV ECX,DWORD PTR DS:[EAX]
 *  0010F528   57               PUSH EDI
 *  0010F529   897424 4C        MOV DWORD PTR SS:[ESP+0x4C],ESI
 *  0010F52D   85C9             TEST ECX,ECX
 *  ...
 *  0010FB7D   0FB707           MOVZX EAX,WORD PTR DS:[EDI] ; jichi: pattern existed in new Debonosu games
 *  0010FB80   50               PUSH EAX
 *  0010FB81   FF75 14          PUSH DWORD PTR SS:[EBP+0x14]
 *  0010FB84   8BCE             MOV ECX,ESI
 *  0010FB86   FF75 10          PUSH DWORD PTR SS:[EBP+0x10]
 *  0010FB89   E8 22F8FFFF      CALL .0010F3B0
 *  0010FB8E   807E 1F 80       CMP BYTE PTR DS:[ESI+0x1F],0x80
 *  0010FB92   894424 44        MOV DWORD PTR SS:[ESP+0x44],EAX
 *  0010FB96   75 1E            JNZ SHORT .0010FBB6
 *  0010FB98   66:0F6E46 64     MOVD MM0,DWORD PTR DS:[ESI+0x64]
 *  ...
 *  0010FC02   FF75 14          PUSH DWORD PTR SS:[EBP+0x14]
 *  0010FC05   8BCE             MOV ECX,ESI
 *  0010FC07   FF75 10          PUSH DWORD PTR SS:[EBP+0x10]
 *  0010FC0A   E8 A1F7FFFF      CALL .0010F3B0
 *  0010FC0F   894424 44        MOV DWORD PTR SS:[ESP+0x44],EAX
 *  0010FC13  ^E9 36FEFFFF      JMP .0010FA4E
 *  0010FC18   8B7424 4C        MOV ESI,DWORD PTR SS:[ESP+0x4C]
 *  0010FC1C   57               PUSH EDI
 *  0010FC1D   FF15 18A42500    CALL DWORD PTR DS:[0x25A418]             ; user32.CharNextA
 *  0010FC23   F3:0F105424 3C   MOVSS XMM2,DWORD PTR SS:[ESP+0x3C]
 *  0010FC29   F3:0F104C24 40   MOVSS XMM1,DWORD PTR SS:[ESP+0x40]
 *  0010FC2F   F3:0F101D CCC329>MOVSS XMM3,DWORD PTR DS:[0x29C3CC]
 *  0010FC37   F3:0F104424 60   MOVSS XMM0,DWORD PTR SS:[ESP+0x60]
 *  0010FC3D   8B15 18A42500    MOV EDX,DWORD PTR DS:[0x25A418]          ; user32.CharNextA
 *  0010FC43   8BF8             MOV EDI,EAX
 *  0010FC45   3B7D 1C          CMP EDI,DWORD PTR SS:[EBP+0x1C]
 *  0010FC48  ^0F82 46FAFFFF    JB .0010F694
 *  0010FC4E   8B4424 44        MOV EAX,DWORD PTR SS:[ESP+0x44]
 *  0010FC52   85C0             TEST EAX,EAX
 *  0010FC54   79 1D            JNS SHORT .0010FC73
 *  0010FC56   50               PUSH EAX
 *  0010FC57   E8 FABA1000      CALL .0021B756
 *  0010FC5C   50               PUSH EAX
 *  0010FC5D   68 F4DE2800      PUSH .0028DEF4                           ; ASCII "D3DFont::Draw"
 *  0010FC62   68 40DD2800      PUSH .0028DD40                           ; ASCII "%s: %s"
 *  0010FC67   E8 74A40E00      CALL .001FA0E0
 *  0010FC6C   8B4424 50        MOV EAX,DWORD PTR SS:[ESP+0x50]
 */
bool attach(ulong startAddress, ulong stopAddress)
{
  ulong addr = 0;
  {
    const char *msg = "D3DFont::Draw";
    if (addr = MemDbg::findBytes(msg, ::strlen(msg+1), startAddress, stopAddress))
      addr = MemDbg::findPushAddress(addr, startAddress, stopAddress);
  }
  if (!addr) {
    DOUT("string pattern not found, try instruction pattern instead");
    const uint8_t bytes[] = {
      0x50,            // 0010fb80   50               push eax
      0xff,0x75, 0x14, // 0010fb81   ff75 14          push dword ptr ss:[ebp+0x14]
      0x8b,0xce,       // 0010fb84   8bce             mov ecx,esi
      0xff,0x75, 0x10  // 0010fb86   ff75 10          push dword ptr ss:[ebp+0x10]
    };
    addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  }
  if (!addr) {
    DOUT("pattern not found");
    return false;
  }
  //addr = MemDbg::findEnclosingAlignedFunction(addr); // This might not work as the address is not always aligned
  addr = MemDbg::findEnclosingFunctionAfterInt3(addr);
  if (!addr) {
    DOUT("function not found");
    return false;
  }
  return winhook::hook_before(addr, Private::hookBefore);
}

} // namespace OtherHook

} // unnamed namespace

/**
 *  Sample game: 神楽花莚譚
 *
 *  Here's the function using MultiByteToWideChar to decode sjis characters:
 *
 *  Pattern: f7 f9 33 d2 6a 04 8d 34 dd 00 00 00 00 0f 57 c0
 *
 *  0015ED1E   CC               INT3
 *  0015ED1F   CC               INT3
 *  0015ED20   55               PUSH EBP	; jichi: text in both arg1 and [arg2] in sjis encoding
 *  0015ED21   8BEC             MOV EBP,ESP
 *  0015ED23   64:A1 00000000   MOV EAX,DWORD PTR FS:[0]
 *  0015ED29   6A FF            PUSH -0x1
 *  0015ED2B   68 5EF12900      PUSH .0029F15E
 *  0015ED30   50               PUSH EAX
 *  0015ED31   64:8925 00000000 MOV DWORD PTR FS:[0],ESP
 *  0015ED38   81EC A4000000    SUB ESP,0xA4
 *  0015ED3E   33D2             XOR EDX,EDX
 *  0015ED40   53               PUSH EBX
 *  0015ED41   56               PUSH ESI
 *  0015ED42   57               PUSH EDI
 *  0015ED43   8BF9             MOV EDI,ECX
 *  0015ED45   33DB             XOR EBX,EBX
 *  0015ED47   BE FF7F0000      MOV ESI,0x7FFF
 *  0015ED4C   3957 6C          CMP DWORD PTR DS:[EDI+0x6C],EDX
 *  0015ED4F   76 1E            JBE SHORT .0015ED6F
 *  0015ED51   33C9             XOR ECX,ECX
 *  0015ED53   8B77 70          MOV ESI,DWORD PTR DS:[EDI+0x70]
 *  0015ED56   8B0431           MOV EAX,DWORD PTR DS:[ECX+ESI]
 *  0015ED59   85C0             TEST EAX,EAX
 *  0015ED5B   74 04            JE SHORT .0015ED61
 *  0015ED5D   48               DEC EAX
 *  0015ED5E   890431           MOV DWORD PTR DS:[ECX+ESI],EAX
 *  0015ED61   42               INC EDX
 *  0015ED62   83C1 1C          ADD ECX,0x1C
 *  0015ED65   3B57 6C          CMP EDX,DWORD PTR DS:[EDI+0x6C]
 *  0015ED68  ^72 E9            JB SHORT .0015ED53
 *  0015ED6A   BE FF7F0000      MOV ESI,0x7FFF
 *  0015ED6F   33C0             XOR EAX,EAX
 *  0015ED71   3947 6C          CMP DWORD PTR DS:[EDI+0x6C],EAX
 *  0015ED74   76 25            JBE SHORT .0015ED9B
 *  0015ED76   8B57 70          MOV EDX,DWORD PTR DS:[EDI+0x70]
 *  0015ED79   8DA424 00000000  LEA ESP,DWORD PTR SS:[ESP]
 *  0015ED80   8B0A             MOV ECX,DWORD PTR DS:[EDX]
 *  0015ED82   85C9             TEST ECX,ECX
 *  0015ED84   74 13            JE SHORT .0015ED99
 *  0015ED86   3BCE             CMP ECX,ESI
 *  0015ED88   73 04            JNB SHORT .0015ED8E
 *  0015ED8A   8BD8             MOV EBX,EAX
 *  0015ED8C   8BF1             MOV ESI,ECX
 *  0015ED8E   40               INC EAX
 *  0015ED8F   83C2 1C          ADD EDX,0x1C
 *  0015ED92   3B47 6C          CMP EAX,DWORD PTR DS:[EDI+0x6C]
 *  0015ED95  ^72 E9            JB SHORT .0015ED80
 *  0015ED97   EB 02            JMP SHORT .0015ED9B
 *  0015ED99   8BD8             MOV EBX,EAX
 *  0015ED9B   8B47 70          MOV EAX,DWORD PTR DS:[EDI+0x70]
 *  0015ED9E   8B4F 64          MOV ECX,DWORD PTR DS:[EDI+0x64]
 *  0015EDA1   8945 E4          MOV DWORD PTR SS:[EBP-0x1C],EAX
 *  0015EDA4   8B47 04          MOV EAX,DWORD PTR DS:[EDI+0x4]
 *  0015EDA7   894D D0          MOV DWORD PTR SS:[EBP-0x30],ECX
 *  0015EDAA   8B40 28          MOV EAX,DWORD PTR DS:[EAX+0x28]
 *  0015EDAD   99               CDQ
 *  0015EDAE   F7F9             IDIV ECX
 *  0015EDB0   33D2             XOR EDX,EDX
 *  0015EDB2   6A 04            PUSH 0x4
 *  0015EDB4   8D34DD 00000000  LEA ESI,DWORD PTR DS:[EBX*8]
 *  0015EDBB   0F57C0           XORPS XMM0,XMM0
 *  0015EDBE   2BF3             SUB ESI,EBX
 *  0015EDC0   8975 8C          MOV DWORD PTR SS:[EBP-0x74],ESI
 *  0015EDC3   66:0FD6          ???                                               ; Unknown command
 *  0015EDC6   45               INC EBP
 *  0015EDC7   AC               LODS BYTE PTR DS:[ESI]
 *  0015EDC8   8BC8             MOV ECX,EAX
 *  0015EDCA   8BC3             MOV EAX,EBX
 *  0015EDCC   F7F1             DIV ECX
 *  0015EDCE   8B4D D0          MOV ECX,DWORD PTR SS:[EBP-0x30]
 *  0015EDD1   0FAFCA           IMUL ECX,EDX
 *  0015EDD4   894D D0          MOV DWORD PTR SS:[EBP-0x30],ECX
 *  0015EDD7   8B4F 68          MOV ECX,DWORD PTR DS:[EDI+0x68]
 *  0015EDDA   0FAFC8           IMUL ECX,EAX
 *  0015EDDD   8D45 AC          LEA EAX,DWORD PTR SS:[EBP-0x54]
 *  0015EDE0   50               PUSH EAX
 *  0015EDE1   6A 02            PUSH 0x2
 *  0015EDE3   8D45 08          LEA EAX,DWORD PTR SS:[EBP+0x8]
 *  0015EDE6   50               PUSH EAX
 *  0015EDE7   6A 01            PUSH 0x1
 *  0015EDE9   6A 03            PUSH 0x3
 *  0015EDEB   898D 7CFFFFFF    MOV DWORD PTR SS:[EBP-0x84],ECX
 *  0015EDF1   FF15 68A22A00    CALL DWORD PTR DS:[0x2AA268]                      ; kernel32.MultiByteToWideChar
 *  0015EDF7   8D57 08          LEA EDX,DWORD PTR DS:[EDI+0x8]
 *  0015EDFA   8D4D 80          LEA ECX,DWORD PTR SS:[EBP-0x80]
 *  0015EDFD   E8 5EFCFFFF      CALL .0015EA60
 *  0015EE02   C745 FC 00000000 MOV DWORD PTR SS:[EBP-0x4],0x0
 *  0015EE09   FF77 68          PUSH DWORD PTR DS:[EDI+0x68]
 *  0015EE0C   8B57 64          MOV EDX,DWORD PTR DS:[EDI+0x64]
 *  0015EE0F   8D4D A4          LEA ECX,DWORD PTR SS:[EBP-0x5C]
 *  0015EE12   E8 B9FDFFFF      CALL .0015EBD0
 *  0015EE17   83C4 04          ADD ESP,0x4
 *  0015EE1A   8B45 A4          MOV EAX,DWORD PTR SS:[EBP-0x5C]
 *  0015EE1D   33C9             XOR ECX,ECX
 *  0015EE1F   894D EC          MOV DWORD PTR SS:[EBP-0x14],ECX
 *  0015EE22   85C0             TEST EAX,EAX
 *  0015EE24   74 12            JE SHORT .0015EE38
 *  0015EE26   8D4D EC          LEA ECX,DWORD PTR SS:[EBP-0x14]
 *  0015EE29   51               PUSH ECX
 *  0015EE2A   FF70 04          PUSH DWORD PTR DS:[EAX+0x4]
 *  0015EE2D   FF15 C0A72A00    CALL DWORD PTR DS:[0x2AA7C0]                      ; GdiPlus.GdipGetImageGraphicsContext
 *  0015EE33   8B4D EC          MOV ECX,DWORD PTR SS:[EBP-0x14]
 *  0015EE36   EB 06            JMP SHORT .0015EE3E
 *  0015EE38   8B85 78FFFFFF    MOV EAX,DWORD PTR SS:[EBP-0x88]
 *  0015EE3E   8945 E8          MOV DWORD PTR SS:[EBP-0x18],EAX
 *  0015EE41   898D 74FFFFFF    MOV DWORD PTR SS:[EBP-0x8C],ECX
 *  0015EE47   FF77 58          PUSH DWORD PTR DS:[EDI+0x58]
 *  0015EE4A   51               PUSH ECX
 *  0015EE4B   FF15 CCA72A00    CALL DWORD PTR DS:[0x2AA7CC]                      ; GdiPlus.GdipSetTextRenderingHint
 *  0015EE51   8B4D E8          MOV ECX,DWORD PTR SS:[EBP-0x18]
 *  0015EE54   85C0             TEST EAX,EAX
 *  0015EE56   6A 02            PUSH 0x2
 *  0015EE58   FF75 EC          PUSH DWORD PTR SS:[EBP-0x14]
 *  0015EE5B   0F45C8           CMOVNE ECX,EAX
 *  0015EE5E   894D E8          MOV DWORD PTR SS:[EBP-0x18],ECX
 *  0015EE61   FF15 D0A72A00    CALL DWORD PTR DS:[0x2AA7D0]                      ; GdiPlus.GdipSetPageUnit
 *  0015EE67   8B4D E8          MOV ECX,DWORD PTR SS:[EBP-0x18]
 *  0015EE6A   85C0             TEST EAX,EAX
 *  0015EE6C   0F45C8           CMOVNE ECX,EAX
 *  0015EE6F   51               PUSH ECX
 *  0015EE70   894D E8          MOV DWORD PTR SS:[EBP-0x18],ECX
 *  0015EE73   C70424 0000803F  MOV DWORD PTR SS:[ESP],0x3F800000
 *  0015EE7A   FF75 EC          PUSH DWORD PTR SS:[EBP-0x14]
 *  0015EE7D   FF15 D4A72A00    CALL DWORD PTR DS:[0x2AA7D4]                      ; GdiPlus.GdipSetPageScale
 *  0015EE83   8B4D E8          MOV ECX,DWORD PTR SS:[EBP-0x18]
 *  0015EE86   85C0             TEST EAX,EAX
 *  0015EE88   0F45C8           CMOVNE ECX,EAX
 *  0015EE8B   8D45 B8          LEA EAX,DWORD PTR SS:[EBP-0x48]
 *  0015EE8E   50               PUSH EAX
 *  0015EE8F   68 00040000      PUSH 0x400
 *  0015EE94   6A 00            PUSH 0x0
 *  0015EE96   894D E8          MOV DWORD PTR SS:[EBP-0x18],ECX
 *  0015EE99   C745 B8 00000000 MOV DWORD PTR SS:[EBP-0x48],0x0
 *  0015EEA0   FF15 B0A72A00    CALL DWORD PTR DS:[0x2AA7B0]                      ; GdiPlus.GdipCreateStringFormat
 *  0015EEA6   8945 BC          MOV DWORD PTR SS:[EBP-0x44],EAX
 *  0015EEA9   8B47 08          MOV EAX,DWORD PTR DS:[EDI+0x8]
 *  0015EEAC   F7D8             NEG EAX
 *  0015EEAE   66:0F6EC0        MOVD MM0,EAX
 *  0015EEB2   0F5B             ???                                               ; Unknown command
 *  0015EEB4   C08B 45E4F30F 5E ROR BYTE PTR DS:[EBX+0xFF3E445],0x5E              ; Shift constant out of range 1..31
 *  0015EEBB   05 30D52E00      ADD EAX,.002ED530
 *  0015EEC0   C745 C0 00000000 MOV DWORD PTR SS:[EBP-0x40],0x0
 *  0015EEC7   F3:0F1145 B4     MOVSS DWORD PTR SS:[EBP-0x4C],XMM0
 *  0015EECC   66:0F6E47 64     MOVD MM0,DWORD PTR DS:[EDI+0x64]
 *  0015EED1   0F5B             ???                                               ; Unknown command
 *  0015EED3   C0C7 45          ROL BH,0x45                                       ; Shift constant out of range 1..31
 *  0015EED6   C400             LES EAX,FWORD PTR DS:[EAX]                        ; Modification of segment register
 *  0015EED8   0000             ADD BYTE PTR DS:[EAX],AL
 *  0015EEDA   00C7             ADD BH,AL
 *  0015EEDC   45               INC EBP
 *  0015EEDD   C8 000000        ENTER 0x0,0x0
 *  0015EEE1   00C7             ADD BH,AL
 *  0015EEE3   45               INC EBP
 *  0015EEE4   CC               INT3
 *  0015EEE5   0000             ADD BYTE PTR DS:[EAX],AL
 *  0015EEE7   0000             ADD BYTE PTR DS:[EAX],AL
 *  0015EEE9   F3:0F1144B0 18   MOVSS DWORD PTR DS:[EAX+ESI*4+0x18],XMM0
 *  0015EEEF   FF75 AC          PUSH DWORD PTR SS:[EBP-0x54]
 *  0015EEF2   E8 09450F00      CALL .00253400
 *  0015EEF7   83C4 04          ADD ESP,0x4
 *  0015EEFA   85C0             TEST EAX,EAX
 *  0015EEFC   74 48            JE SHORT .0015EF46
 *  0015EEFE   8D45 08          LEA EAX,DWORD PTR SS:[EBP+0x8]
 *  0015EF01   50               PUSH EAX
 *  0015EF02   FF15 18A42A00    CALL DWORD PTR DS:[0x2AA418]                      ; user32.CharNextA
 *  0015EF08   8D4D 08          LEA ECX,DWORD PTR SS:[EBP+0x8]
 *  0015EF0B   2BC1             SUB EAX,ECX
 *  0015EF0D   83F8 01          CMP EAX,0x1
 *  0015EF10   8B45 E4          MOV EAX,DWORD PTR SS:[EBP-0x1C]
 *  0015EF13   75 14            JNZ SHORT .0015EF29
 *  0015EF15   F3:0F1044B0 18   MOVSS XMM0,DWORD PTR DS:[EAX+ESI*4+0x18]
 *  0015EF1B   F3:0F5905 CCC32E>MULSS XMM0,DWORD PTR DS:[0x2EC3CC]
 *  0015EF23   F3:0F1144B0 18   MOVSS DWORD PTR DS:[EAX+ESI*4+0x18],XMM0
 *  0015EF29   F3:0F1044B0 18   MOVSS XMM0,DWORD PTR DS:[EAX+ESI*4+0x18]
 *  0015EF2F   F3:0F1145 C8     MOVSS DWORD PTR SS:[EBP-0x38],XMM0
 *  0015EF34   66:0F6E47 68     MOVD MM0,DWORD PTR DS:[EDI+0x68]
 *  0015EF39   0F5B             ???                                               ; Unknown command
 *  0015EF3B   C0F3 0F          SAL BL,0xF
 *  0015EF3E   1145 CC          ADC DWORD PTR SS:[EBP-0x34],EAX
 *  0015EF41   E9 B7000000      JMP .0015EFFD
 *  0015EF46   8B45 80          MOV EAX,DWORD PTR SS:[EBP-0x80]	; jichi: text might be rendered here?
 *  0015EF49   C745 D4 00000000 MOV DWORD PTR SS:[EBP-0x2C],0x0
 *  0015EF50   C745 D8 00000000 MOV DWORD PTR SS:[EBP-0x28],0x0
 *  0015EF57   C745 DC 00000000 MOV DWORD PTR SS:[EBP-0x24],0x0
 *  0015EF5E   C745 E0 00000000 MOV DWORD PTR SS:[EBP-0x20],0x0
 *  0015EF65   85C0             TEST EAX,EAX
 *  0015EF67   74 04            JE SHORT .0015EF6D
 *  0015EF69   8B00             MOV EAX,DWORD PTR DS:[EAX]
 *  0015EF6B   EB 02            JMP SHORT .0015EF6F
 *  0015EF6D   33C0             XOR EAX,EAX
 *  0015EF6F   6A 00            PUSH 0x0
 *  0015EF71   6A 00            PUSH 0x0
 *  0015EF73   8D4D C0          LEA ECX,DWORD PTR SS:[EBP-0x40]
 *  0015EF76   51               PUSH ECX
 *  0015EF77   FF75 B8          PUSH DWORD PTR SS:[EBP-0x48]
 *  0015EF7A   8D4D D4          LEA ECX,DWORD PTR SS:[EBP-0x2C]
 *  0015EF7D   51               PUSH ECX
 *  0015EF7E   50               PUSH EAX
 *  0015EF7F   6A 01            PUSH 0x1
 *  0015EF81   8D45 AC          LEA EAX,DWORD PTR SS:[EBP-0x54]	; jichi: ebp-0x54 is the unicode char address
 *  0015EF84   50               PUSH EAX	; jichi: text
 *  0015EF85   FF75 EC          PUSH DWORD PTR SS:[EBP-0x14]	; jichi: graphics
 *  0015EF88   FF15 E0A72A00    CALL DWORD PTR DS:[0x2AA7E0]                      ; GdiPlus.GdipMeasureString: jichi: text painted here
 *  0015EF8E   66:0F6E47 64     MOVD MM0,DWORD PTR DS:[EDI+0x64]
 *  0015EF93   0F5B             ???                                               ; Unknown command
 *  0015EF95   C085 C0740589 45 ROL BYTE PTR SS:[EBP+0x890574C0],0x45             ; Shift constant out of range 1..31
 *  0015EF9C   E8 EB90F30F      CALL 1009808C
 *  0015EFA1   1145 88          ADC DWORD PTR SS:[EBP-0x78],EAX
 *  0015EFA4   F3:0F1045 B4     MOVSS XMM0,DWORD PTR SS:[EBP-0x4C]
 *  0015EFA9   F3:0F5905 18C72E>MULSS XMM0,DWORD PTR DS:[0x2EC718]
 *  0015EFB1   83EC 08          SUB ESP,0x8
 *  0015EFB4   F3:0F5845 C8     ADDSS XMM0,DWORD PTR SS:[EBP-0x38]
 *  0015EFB9   0F5A             ???                                               ; Unknown command
 *  0015EFBB   C0F2 0F          SAL DL,0xF
 *  0015EFBE   1145 DC          ADC DWORD PTR SS:[EBP-0x24],EAX
 *  0015EFC1   DD45 DC          FLD QWORD PTR SS:[EBP-0x24]
 *  0015EFC4   DD1C24           FSTP QWORD PTR SS:[ESP]
 *  0015EFC7   E8 A4611200      CALL .00285170
 *  0015EFCC   66:0F6E4F 64     MOVD MM1,DWORD PTR DS:[EDI+0x64]
 *  0015EFD1   DD5D DC          FSTP QWORD PTR SS:[EBP-0x24]
 *  0015EFD4   F2:              PREFIX REPNE:                                     ; Superfluous prefix
 *  0015EFD5   0F1045 DC        MOVUPS XMM0,DQWORD PTR SS:[EBP-0x24]
 *  0015EFD9   66:0F5A          ???                                               ; Unknown command
 *  0015EFDC   C00F 5B          ROR BYTE PTR DS:[EDI],0x5B                        ; Shift constant out of range 1..31
 *  0015EFDF   C9               LEAVE
 *  0015EFE0   83C4 08          ADD ESP,0x8
 *  0015EFE3   0F2FC1           COMISS XMM0,XMM1
 *  0015EFE6   8D4D E0          LEA ECX,DWORD PTR SS:[EBP-0x20]
 *  0015EFE9   8D45 88          LEA EAX,DWORD PTR SS:[EBP-0x78]
 *  0015EFEC   0F46C1           CMOVBE EAX,ECX
 *  0015EFEF   8B4D E4          MOV ECX,DWORD PTR SS:[EBP-0x1C]
 *  0015EFF2   F3:0F1145 E0     MOVSS DWORD PTR SS:[EBP-0x20],XMM0
 *  0015EFF7   8B00             MOV EAX,DWORD PTR DS:[EAX]
 *  0015EFF9   8944B1 18        MOV DWORD PTR DS:[ECX+ESI*4+0x18],EAX
 *  0015EFFD   FF77 68          PUSH DWORD PTR DS:[EDI+0x68]
 *  0015F000   F3:0F1045 B4     MOVSS XMM0,DWORD PTR SS:[EBP-0x4C]
 *  0015F005   FF77 64          PUSH DWORD PTR DS:[EDI+0x64]
 *  0015F008   A1 E0FF3200      MOV EAX,DWORD PTR DS:[0x32FFE0]
 *  0015F00D   6A 00            PUSH 0x0
 *  0015F00F   6A 00            PUSH 0x0
 *  0015F011   F3:0F1145 C0     MOVSS DWORD PTR SS:[EBP-0x40],XMM0
 *  0015F016   C745 C4 00000000 MOV DWORD PTR SS:[EBP-0x3C],0x0
 *  0015F01D   FF70 04          PUSH DWORD PTR DS:[EAX+0x4]
 *  0015F020   FF75 EC          PUSH DWORD PTR SS:[EBP-0x14]
 *  0015F023   FF15 D8A72A00    CALL DWORD PTR DS:[0x2AA7D8]                      ; GdiPlus.GdipFillRectangleI
 *  0015F029   8B4D E8          MOV ECX,DWORD PTR SS:[EBP-0x18]
 *  0015F02C   85C0             TEST EAX,EAX
 *  0015F02E   0F45C8           CMOVNE ECX,EAX
 *  0015F031   A1 2CFF3200      MOV EAX,DWORD PTR DS:[0x32FF2C]
 *  0015F036   898D 78FFFFFF    MOV DWORD PTR SS:[EBP-0x88],ECX
 *  0015F03C   85C0             TEST EAX,EAX
 *  0015F03E   74 05            JE SHORT .0015F045
 *  0015F040   8B48 04          MOV ECX,DWORD PTR DS:[EAX+0x4]
 *  0015F043   EB 02            JMP SHORT .0015F047
 *  0015F045   33C9             XOR ECX,ECX
 *  0015F047   8B45 80          MOV EAX,DWORD PTR SS:[EBP-0x80]
 *  0015F04A   85C0             TEST EAX,EAX
 *  0015F04C   74 04            JE SHORT .0015F052
 *  0015F04E   8B00             MOV EAX,DWORD PTR DS:[EAX]
 *  0015F050   EB 02            JMP SHORT .0015F054
 *  0015F052   33C0             XOR EAX,EAX
 *  0015F054   51               PUSH ECX
 *  0015F055   FF75 B8          PUSH DWORD PTR SS:[EBP-0x48]
 *  0015F058   8D4D C0          LEA ECX,DWORD PTR SS:[EBP-0x40]
 *  0015F05B   51               PUSH ECX
 *  0015F05C   50               PUSH EAX
 *  0015F05D   6A 01            PUSH 0x1
 *  0015F05F   8D45 AC          LEA EAX,DWORD PTR SS:[EBP-0x54]
 *  0015F062   50               PUSH EAX
 *  0015F063   FF75 EC          PUSH DWORD PTR SS:[EBP-0x14]
 *  0015F066   FF15 DCA72A00    CALL DWORD PTR DS:[0x2AA7DC]                      ; GdiPlus.GdipDrawString
 *  0015F06C   85C0             TEST EAX,EAX
 *  0015F06E   0F85 60010000    JNZ .0015F1D4
 *  0015F074   50               PUSH EAX
 *  0015F075   FF75 EC          PUSH DWORD PTR SS:[EBP-0x14]
 *  0015F078   FF15 C8A72A00    CALL DWORD PTR DS:[0x2AA7C8]                      ; GdiPlus.GdipFlush
 *  0015F07E   8B47 64          MOV EAX,DWORD PTR DS:[EDI+0x64]
 *  0015F081   8B55 A4          MOV EDX,DWORD PTR SS:[EBP-0x5C]
 *  0015F084   8B4F 68          MOV ECX,DWORD PTR DS:[EDI+0x68]
 *  0015F087   8945 DC          MOV DWORD PTR SS:[EBP-0x24],EAX
 *  0015F08A   8D85 58FFFFFF    LEA EAX,DWORD PTR SS:[EBP-0xA8]
 *  0015F090   50               PUSH EAX
 *  0015F091   68 06100200      PUSH 0x21006
 *  0015F096   6A 01            PUSH 0x1
 *  0015F098   8D45 D4          LEA EAX,DWORD PTR SS:[EBP-0x2C]
 *  0015F09B   50               PUSH EAX
 *  0015F09C   8995 54FFFFFF    MOV DWORD PTR SS:[EBP-0xAC],EDX
 *  0015F0A2   C745 D4 00000000 MOV DWORD PTR SS:[EBP-0x2C],0x0
 *  0015F0A9   C745 D8 00000000 MOV DWORD PTR SS:[EBP-0x28],0x0
 *  0015F0B0   894D E0          MOV DWORD PTR SS:[EBP-0x20],ECX
 *  0015F0B3   FF72 04          PUSH DWORD PTR DS:[EDX+0x4]
 *  0015F0B6   FF15 10A82A00    CALL DWORD PTR DS:[0x2AA810]                      ; GdiPlus.GdipBitmapLockBits
 *  0015F0BC   85C0             TEST EAX,EAX
 *  0015F0BE   74 08            JE SHORT .0015F0C8
 *  0015F0C0   8B4D A4          MOV ECX,DWORD PTR SS:[EBP-0x5C]
 *  0015F0C3   8941 08          MOV DWORD PTR DS:[ECX+0x8],EAX
 *  0015F0C6   EB 02            JMP SHORT .0015F0CA
 *  0015F0C8   33C0             XOR EAX,EAX
 *  0015F0CA   8985 70FFFFFF    MOV DWORD PTR SS:[EBP-0x90],EAX
 *  0015F0D0   C645 FC 04       MOV BYTE PTR SS:[EBP-0x4],0x4
 *  0015F0D4   85C0             TEST EAX,EAX
 *  0015F0D6   0F85 DB000000    JNZ .0015F1B7
 *  0015F0DC   8B45 E4          MOV EAX,DWORD PTR SS:[EBP-0x1C]
 *  0015F0DF   8B95 7CFFFFFF    MOV EDX,DWORD PTR SS:[EBP-0x84]
 *  0015F0E5   8B4D D0          MOV ECX,DWORD PTR SS:[EBP-0x30]
 *  0015F0E8   83C0 08          ADD EAX,0x8
 *  0015F0EB   8D34B0           LEA ESI,DWORD PTR DS:[EAX+ESI*4]
 *  0015F0EE   8B85 5CFFFFFF    MOV EAX,DWORD PTR SS:[EBP-0xA4]
 *  0015F0F4   03C2             ADD EAX,EDX
 *  0015F0F6   50               PUSH EAX
 *  0015F0F7   8B85 58FFFFFF    MOV EAX,DWORD PTR SS:[EBP-0xA8]
 *  0015F0FD   03C1             ADD EAX,ECX
 *  0015F0FF   50               PUSH EAX
 *  0015F100   52               PUSH EDX
 *  0015F101   51               PUSH ECX
 *  0015F102   56               PUSH ESI
 *  0015F103   FF15 14A42A00    CALL DWORD PTR DS:[0x2AA414]                      ; user32.SetRect
 *  0015F109   8B47 04          MOV EAX,DWORD PTR DS:[EDI+0x4]
 *  0015F10C   6A 00            PUSH 0x0
 *  0015F10E   56               PUSH ESI
 *  0015F10F   8945 90          MOV DWORD PTR SS:[EBP-0x70],EAX
 *  0015F112   C745 94 00000000 MOV DWORD PTR SS:[EBP-0x6C],0x0
 *  0015F119   8B40 10          MOV EAX,DWORD PTR DS:[EAX+0x10]
 *  0015F11C   8D55 98          LEA EDX,DWORD PTR SS:[EBP-0x68]
 *  0015F11F   8B08             MOV ECX,DWORD PTR DS:[EAX]
 *  0015F121   52               PUSH EDX
 *  0015F122   6A 00            PUSH 0x0
 *  0015F124   50               PUSH EAX
 *  0015F125   FF51 4C          CALL DWORD PTR DS:[ECX+0x4C]
 *  0015F128   8945 A0          MOV DWORD PTR SS:[EBP-0x60],EAX
 *  0015F12B   85C0             TEST EAX,EAX
 *  0015F12D   78 64            JS SHORT .0015F193
 *  0015F12F   8B45 90          MOV EAX,DWORD PTR SS:[EBP-0x70]
 *  0015F132   8B4F 5C          MOV ECX,DWORD PTR DS:[EDI+0x5C]
 *  0015F135   8B40 1C          MOV EAX,DWORD PTR DS:[EAX+0x1C]
 *  0015F138   83C0 EB          ADD EAX,-0x15
 *  0015F13B   83F8 1F          CMP EAX,0x1F
 *  0015F13E   77 53            JA SHORT .0015F193
 *  0015F140   0FB680 70F21500  MOVZX EAX,BYTE PTR DS:[EAX+0x15F270]
 *  0015F147   FF2485 5CF21500  JMP DWORD PTR DS:[EAX*4+0x15F25C]
 *  0015F14E   51               PUSH ECX
 *  0015F14F   8D95 54FFFFFF    LEA EDX,DWORD PTR SS:[EBP-0xAC]
 *  0015F155   8D4D 90          LEA ECX,DWORD PTR SS:[EBP-0x70]
 *  0015F158   E8 833D0000      CALL .00162EE0
 *  0015F15D   EB 31            JMP SHORT .0015F190
 *  0015F15F   51               PUSH ECX
 *  0015F160   8D95 54FFFFFF    LEA EDX,DWORD PTR SS:[EBP-0xAC]
 *  0015F166   8D4D 90          LEA ECX,DWORD PTR SS:[EBP-0x70]
 *  0015F169   E8 723E0000      CALL .00162FE0
 *  0015F16E   EB 20            JMP SHORT .0015F190
 *  0015F170   51               PUSH ECX
 *  0015F171   8D95 54FFFFFF    LEA EDX,DWORD PTR SS:[EBP-0xAC]
 *  0015F177   8D4D 90          LEA ECX,DWORD PTR SS:[EBP-0x70]
 *  0015F17A   E8 613F0000      CALL .001630E0
 *  0015F17F   EB 0F            JMP SHORT .0015F190
 *  0015F181   51               PUSH ECX
 *  0015F182   8D95 54FFFFFF    LEA EDX,DWORD PTR SS:[EBP-0xAC]
 *  0015F188   8D4D 90          LEA ECX,DWORD PTR SS:[EBP-0x70]
 *  0015F18B   E8 50400000      CALL .001631E0
 *  0015F190   83C4 04          ADD ESP,0x4
 *  0015F193   8B4D 8C          MOV ECX,DWORD PTR SS:[EBP-0x74]
 *  0015F196   8B55 E4          MOV EDX,DWORD PTR SS:[EBP-0x1C]
 *  0015F199   FF75 94          PUSH DWORD PTR SS:[EBP-0x6C]
 *  0015F19C   C7048A FE7F0000  MOV DWORD PTR DS:[EDX+ECX*4],0x7FFE
 *  0015F1A3   0FB745 08        MOVZX EAX,WORD PTR SS:[EBP+0x8]
 *  0015F1A7   89448A 04        MOV DWORD PTR DS:[EDX+ECX*4+0x4],EAX
 */
bool DebonosuEngine::attach()
{
  ulong startAddress, stopAddress;
  if (!Engine::getProcessMemoryRange(&startAddress, &stopAddress))
    return false;
  if (!ScenarioHook::attach(startAddress, stopAddress))
    return false;

  if (NameHook::attach(startAddress, stopAddress))
    DOUT("name text found");
  else
    DOUT("name text NOT FOUND");

  if (OtherHook::attach(startAddress, stopAddress))
    DOUT("other text found");
  else
    DOUT("other text NOT FOUND");

  //if (ChoiceHook::attach(startAddress, stopAddress))
  //  DOUT("choice text found");
  //else
  //  DOUT("choice text NOT FOUND");

  HijackManager::instance()->attachFunction((ulong)::MultiByteToWideChar);
  HijackManager::instance()->attachFunction((ulong)::GetTextExtentPoint32A);
  return true;
}

/**
 *  Example sentence: 暗闇の中、一組の男女が{蠢/うごめ}いていた。
 */
QString DebonosuEngine::rubyCreate(const QString &rb, const QString &rt)
{
  static QString fmt = "{%1/%2}";
  return fmt.arg(rb, rt);
}
QString DebonosuEngine::rubyRemove(const QString &text)
{
  if (!text.contains('{'))
    return text;
  static QRegExp rx("\\{(.+)/.+\\}");
  if (!rx.isMinimal())
    rx.setMinimal(true);
  return QString(text).replace(rx, "\\1");
}

// EOF

#if 0
namespace OtherHook {

namespace Private {

  BOOL WINAPI newGetTextExtentPoint32A(HDC hdc, LPCSTR lpString, int cchString, LPSIZE lpSize)
  {
    enum { TextCapacity = 0x10 };
    static std::unordered_set<LPCSTR> texts_;
    if (texts_.find(lpString) == texts_.end())
    if (auto q = EngineController::instance()) {
      QByteArray data(lpString, cchString);
      QString oldText = q->decode(data);
      if (!oldText.isEmpty()) {
        enum { role = Engine::OtherRole };
        ulong split = (ulong)_ReturnAddress();
        auto sig = Engine::hashThreadSignature(role, split);
        QString newText = q->dispatchTextW(oldText, role, sig);
        if (!newText.isEmpty() && newText != oldText) {
          texts_.insert(lpString);
          if (auto p = DynamicCodec::instance()) {
            QByteArray data = p->encode(newText);
            int size = qMin(TextCapacity, data.size() + 1);
            auto text = const_cast<LPSTR>(lpString);
            ::memcpy(text, data.constData(), size);
            text[size - 1] = 0;
          }
          return Hijack::oldGetTextExtentPoint32W(hdc, (LPCWSTR)newText.utf16(), newText.size(), lpSize);
        }
      }
    }
    return Hijack::oldGetTextExtentPoint32A(hdc, lpString, cchString, lpSize);
  }
} // namespace Private

bool attach()
{
  return Hijack::oldGetTextExtentPoint32A = (Hijack::GetTextExtentPoint32A_fun_t)
      winhook::replace_fun((ulong)::GetTextExtentPoint32A, (ulong)Private::newGetTextExtentPoint32A);
}

} // namespace OtherHook

namespace OtherHook {

std::unordered_set<LPCSTR> translatedTexts_; // text that has already been translated

inline char *ltrim(const char *s) // skip leading "+" for choices
{
  if (s && *s == '+')
    s++;
  return const_cast<char *>(s);
}

// Maximum characters in a text including \0
// Found by debugging text of 神楽花莚譚
// Need to use this value if copy is used

namespace Private {

  bool hookBefore(winhook::hook_stack *s)
  {
    enum { TextCapacity = 0x10 };
    LPSTR text = (LPSTR)s->stack[2]; // new game, text in arg2 for the caller of GetTextExtentPoint32A
    if (!Engine::isAddressWritable(text)) {
      text = (LPSTR)s->edx; // old game
      if (!Engine::isAddressWritable(text))
        return true;
    }
    if (translatedTexts_.find(text) != translatedTexts_.cend())
      return true;
    LPCSTR trimmedText = OtherHook::ltrim(text);
    if (!trimmedText || !*trimmedText)
      return true;
    enum { role = Engine::OtherRole };
    auto split = s->stack[0]; // retaddr
    auto sig = Engine::hashThreadSignature(role, split);
    QByteArray oldData = trimmedText,
               newData = EngineController::instance()->dispatchTextA(oldData, role, sig);
    if (oldData == newData)
      return true;
    //if (trimmedText != text)
    //  newData.prepend(text, trimmedText - text);
    int capacity = TextCapacity - (trimmedText - text);
    if (capacity <= 0)
      return true;
    ::memcpy(text, newData.constData(), qMax(newData.size() + 1, capacity));
    text[capacity - 1] = 0; // enforce trailing zero
    translatedTexts_.insert(text);
    return true;
  }

} // namespace Private

/**
 *  Sample game: 神楽花莚譚
 *
 *  01423C1C   CC               INT3
 *  01423C1D   CC               INT3
 *  01423C1E   CC               INT3
 *  01423C1F   CC               INT3
 *  01423C20   55               PUSH EBP    ; jichi: caller of the last two GetTextExtentPoint32A, text in arg2
 *  01423C21   8BEC             MOV EBP,ESP
 *  01423C23   83EC 30          SUB ESP,0x30
 *  01423C26   53               PUSH EBX
 *  01423C27   56               PUSH ESI
 *  01423C28   57               PUSH EDI
 *  01423C29   6A 24            PUSH 0x24
 *  01423C2B   894D EC          MOV DWORD PTR SS:[EBP-0x14],ECX
 *  01423C2E   E8 B2B90900      CALL .014BF5E5
 *  01423C33   8BF8             MOV EDI,EAX
 *  01423C35   83C4 04          ADD ESP,0x4
 *  01423C38   85FF             TEST EDI,EDI
 *  01423C3A   74 24            JE SHORT .01423C60
 *  01423C3C   C707 00000000    MOV DWORD PTR DS:[EDI],0x0
 *  01423C42   C747 04 00000000 MOV DWORD PTR DS:[EDI+0x4],0x0
 *  01423C49   C747 08 FFFFFFFF MOV DWORD PTR DS:[EDI+0x8],-0x1
 *  01423C50   C747 10 00000000 MOV DWORD PTR DS:[EDI+0x10],0x0
 *  01423C57   C747 0C 00000000 MOV DWORD PTR DS:[EDI+0xC],0x0
 *  01423C5E   EB 02            JMP SHORT .01423C62
 *  01423C60   33FF             XOR EDI,EDI
 *  01423C62   8B75 08          MOV ESI,DWORD PTR SS:[EBP+0x8]
 *  01423C65   8BCF             MOV ECX,EDI
 *  01423C67   F3:              PREFIX REP:                              ; Superfluous prefix
 *  01423C68   0F7E06           MOVD DWORD PTR DS:[ESI],MM0
 *  01423C6B   66:0FD6          ???                                      ; Unknown command
 *  01423C6E   07               POP ES                                   ; Modification of segment register
 *  01423C6F   F3:              PREFIX REP:                              ; Superfluous prefix
 *  01423C70   0F7E46 08        MOVD DWORD PTR DS:[ESI+0x8],MM0
 *  01423C74   66:0FD6          ???                                      ; Unknown command
 *  01423C77   47               INC EDI
 *  01423C78   08F3             OR BL,DH
 *  01423C7A   0F7E46 10        MOVD DWORD PTR DS:[ESI+0x10],MM0
 *  01423C7E   66:0FD6          ???                                      ; Unknown command
 *  01423C81   47               INC EDI
 *  01423C82   10F3             ADC BL,DH
 *  01423C84   0F7E46 18        MOVD DWORD PTR DS:[ESI+0x18],MM0
 *  01423C88   66:0FD6          ???                                      ; Unknown command
 *  01423C8B   47               INC EDI
 *  01423C8C   188B 46208947    SBB BYTE PTR DS:[EBX+0x47892046],CL
 *  01423C92   20C7             AND BH,AL
 *  01423C94   47               INC EDI
 *  01423C95   04 00            ADD AL,0x0
 *  01423C97   0000             ADD BYTE PTR DS:[EAX],AL
 *  01423C99   00FF             ADD BH,BH
 *  01423C9B   76 04            JBE SHORT .01423CA1
 *  01423C9D   897D F8          MOV DWORD PTR SS:[EBP-0x8],EDI
 *  01423CA0   E8 3BE7FFFF      CALL .014223E0
 *  01423CA5   8B46 0C          MOV EAX,DWORD PTR DS:[ESI+0xC]
 *  01423CA8   8945 08          MOV DWORD PTR SS:[EBP+0x8],EAX
 *  01423CAB   85C0             TEST EAX,EAX
 *  01423CAD   74 28            JE SHORT .01423CD7
 *  01423CAF   50               PUSH EAX
 *  01423CB0   FF15 10A35101    CALL DWORD PTR DS:[0x151A310]            ; kernel32.lstrlenA
 *  01423CB6   8D58 01          LEA EBX,DWORD PTR DS:[EAX+0x1]
 *  01423CB9   53               PUSH EBX
 *  01423CBA   E8 2EB00900      CALL .014BECED
 *  01423CBF   8BF0             MOV ESI,EAX
 *  01423CC1   83C4 04          ADD ESP,0x4
 *  01423CC4   85F6             TEST ESI,ESI
 *  01423CC6   74 0F            JE SHORT .01423CD7
 *  01423CC8   53               PUSH EBX
 *  01423CC9   FF75 08          PUSH DWORD PTR SS:[EBP+0x8]
 *  01423CCC   56               PUSH ESI
 *  01423CCD   E8 2E180A00      CALL .014C5500
 *  01423CD2   83C4 0C          ADD ESP,0xC
 *  01423CD5   EB 02            JMP SHORT .01423CD9
 *  01423CD7   33F6             XOR ESI,ESI
 *  01423CD9   8977 0C          MOV DWORD PTR DS:[EDI+0xC],ESI
 *  01423CDC   8B7D EC          MOV EDI,DWORD PTR SS:[EBP-0x14]
 *  01423CDF   8D45 F8          LEA EAX,DWORD PTR SS:[EBP-0x8]
 *  01423CE2   8D5F 58          LEA EBX,DWORD PTR DS:[EDI+0x58]
 *  01423CE5   50               PUSH EAX
 *  01423CE6   8BCB             MOV ECX,EBX
 *  01423CE8   E8 83B0F1FF      CALL .0133ED70
 *  01423CED   8D45 08          LEA EAX,DWORD PTR SS:[EBP+0x8]
 *  01423CF0   50               PUSH EAX
 *  01423CF1   8D4F 68          LEA ECX,DWORD PTR DS:[EDI+0x68]
 *  01423CF4   C745 08 00000000 MOV DWORD PTR SS:[EBP+0x8],0x0
 *  01423CFB   E8 70B0F1FF      CALL .0133ED70
 *  01423D00   837F 1C 00       CMP DWORD PTR DS:[EDI+0x1C],0x0
 *  01423D04   8D47 1C          LEA EAX,DWORD PTR DS:[EDI+0x1C]
 *  01423D07   0F84 15020000    JE .01423F22
 *  01423D0D   50               PUSH EAX
 *  01423D0E   FF15 68A05101    CALL DWORD PTR DS:[0x151A068]            ; gdi32.CreateFontIndirectA
 *  01423D14   8BF0             MOV ESI,EAX
 *  01423D16   8975 DC          MOV DWORD PTR SS:[EBP-0x24],ESI
 *  01423D19   85F6             TEST ESI,ESI
 *  01423D1B   75 19            JNZ SHORT .01423D36
 *  01423D1D   68 083C5501      PUSH .01553C08                           ; ASCII "AddItem error."
 *  01423D22   E8 B9630900      CALL .014BA0E0
 *  01423D27   83C4 04          ADD ESP,0x4
 *  01423D2A   83C8 FF          OR EAX,0xFFFFFFFF
 *  01423D2D   5F               POP EDI
 *  01423D2E   5E               POP ESI
 *  01423D2F   5B               POP EBX
 *  01423D30   8BE5             MOV ESP,EBP
 *  01423D32   5D               POP EBP
 *  01423D33   C2 0400          RETN 0x4
 *  01423D36   6A 00            PUSH 0x0
 *  01423D38   FF15 70A05101    CALL DWORD PTR DS:[0x151A070]            ; gdi32.CreateCompatibleDC
 *  01423D3E   8BD8             MOV EBX,EAX
 *  01423D40   56               PUSH ESI
 *  01423D41   53               PUSH EBX
 *  01423D42   895D F4          MOV DWORD PTR SS:[EBP-0xC],EBX
 *  01423D45   FF15 58A05101    CALL DWORD PTR DS:[0x151A058]            ; gdi32.SelectObject
 *  01423D4B   6A 01            PUSH 0x1
 *  01423D4D   53               PUSH EBX
 *  01423D4E   8945 E0          MOV DWORD PTR SS:[EBP-0x20],EAX
 *  01423D51   C745 D4 00000000 MOV DWORD PTR SS:[EBP-0x2C],0x0
 *  01423D58   C745 D8 00000000 MOV DWORD PTR SS:[EBP-0x28],0x0
 *  01423D5F   FF15 80A05101    CALL DWORD PTR DS:[0x151A080]            ; gdi32.SetMapMode
 *  01423D65   8B75 F8          MOV ESI,DWORD PTR SS:[EBP-0x8]
 *  01423D68   6A 5B            PUSH 0x5B
 *  01423D6A   FF76 04          PUSH DWORD PTR DS:[ESI+0x4]
 *  01423D6D   E8 54D30900      CALL .014C10C6
 *  01423D72   8BD8             MOV EBX,EAX
 *  01423D74   83C4 08          ADD ESP,0x8
 *  01423D77   85DB             TEST EBX,EBX
 *  01423D79   0F84 C4000000    JE .01423E43
 *  01423D7F   FF76 04          PUSH DWORD PTR DS:[ESI+0x4]
 *  01423D82   A1 10A35101      MOV EAX,DWORD PTR DS:[0x151A310]
 *  01423D87   FFD0             CALL EAX
 *  01423D89   8BF8             MOV EDI,EAX
 *  01423D8B   8B45 F8          MOV EAX,DWORD PTR SS:[EBP-0x8]
 *  01423D8E   8D4F 20          LEA ECX,DWORD PTR DS:[EDI+0x20]
 *  01423D91   8BF3             MOV ESI,EBX
 *  01423D93   2B70 04          SUB ESI,DWORD PTR DS:[EAX+0x4]
 *  01423D96   51               PUSH ECX
 *  01423D97   E8 51AF0900      CALL .014BECED
 *  01423D9C   8BC8             MOV ECX,EAX
 *  01423D9E   8B45 F8          MOV EAX,DWORD PTR SS:[EBP-0x8]
 *  01423DA1   56               PUSH ESI
 *  01423DA2   FF70 04          PUSH DWORD PTR DS:[EAX+0x4]
 *  01423DA5   894D F0          MOV DWORD PTR SS:[EBP-0x10],ECX
 *  01423DA8   51               PUSH ECX
 *  01423DA9   E8 52170A00      CALL .014C5500
 *  01423DAE   8B45 F8          MOV EAX,DWORD PTR SS:[EBP-0x8]
 *  01423DB1   0375 F0          ADD ESI,DWORD PTR SS:[EBP-0x10]
 *  01423DB4   8B40 04          MOV EAX,DWORD PTR DS:[EAX+0x4]
 *  01423DB7   03C7             ADD EAX,EDI
 *  01423DB9   83C4 10          ADD ESP,0x10
 *  01423DBC   C645 0B 00       MOV BYTE PTR SS:[EBP+0xB],0x0
 *  01423DC0   8945 E4          MOV DWORD PTR SS:[EBP-0x1C],EAX
 *  01423DC3   3BD8             CMP EBX,EAX
 *  01423DC5   73 54            JNB SHORT .01423E1B
 *  01423DC7   53               PUSH EBX
 *  01423DC8   FF15 18A45101    CALL DWORD PTR DS:[0x151A418]            ; user32.CharNextA
 *  01423DCE   8BC8             MOV ECX,EAX
 *  01423DD0   8BF9             MOV EDI,ECX
 *  01423DD2   2BFB             SUB EDI,EBX
 *  01423DD4   894D E8          MOV DWORD PTR SS:[EBP-0x18],ECX
 *  01423DD7   83FF 01          CMP EDI,0x1
 *  01423DDA   75 22            JNZ SHORT .01423DFE
 *  01423DDC   807D 0B 00       CMP BYTE PTR SS:[EBP+0xB],0x0
 *  01423DE0   74 0B            JE SHORT .01423DED
 *  01423DE2   803B 5D          CMP BYTE PTR DS:[EBX],0x5D
 *  01423DE5   75 2D            JNZ SHORT .01423E14
 *  01423DE7   C645 0B 00       MOV BYTE PTR SS:[EBP+0xB],0x0
 *  01423DEB   EB 27            JMP SHORT .01423E14
 *  01423DED   8A03             MOV AL,BYTE PTR DS:[EBX]
 *  01423DEF   3C 5B            CMP AL,0x5B
 *  01423DF1   75 06            JNZ SHORT .01423DF9
 *  01423DF3   C645 0B 01       MOV BYTE PTR SS:[EBP+0xB],0x1
 *  01423DF7   EB 1B            JMP SHORT .01423E14
 *  01423DF9   8806             MOV BYTE PTR DS:[ESI],AL
 *  01423DFB   46               INC ESI
 *  01423DFC   EB 16            JMP SHORT .01423E14
 *  01423DFE   807D 0B 00       CMP BYTE PTR SS:[EBP+0xB],0x0
 *  01423E02   75 10            JNZ SHORT .01423E14
 *  01423E04   57               PUSH EDI
 *  01423E05   53               PUSH EBX
 *  01423E06   56               PUSH ESI
 *  01423E07   E8 F4160A00      CALL .014C5500
 *  01423E0C   8B4D E8          MOV ECX,DWORD PTR SS:[EBP-0x18]
 *  01423E0F   83C4 0C          ADD ESP,0xC
 *  01423E12   03F7             ADD ESI,EDI
 *  01423E14   8BD9             MOV EBX,ECX
 *  01423E16   3B4D E4          CMP ECX,DWORD PTR SS:[EBP-0x1C]
 *  01423E19  ^72 AC            JB SHORT .01423DC7
 *  01423E1B   8B5D F0          MOV EBX,DWORD PTR SS:[EBP-0x10]
 *  01423E1E   8D45 D4          LEA EAX,DWORD PTR SS:[EBP-0x2C]
 *  01423E21   50               PUSH EAX
 *  01423E22   C606 00          MOV BYTE PTR DS:[ESI],0x0
 *  01423E25   2BF3             SUB ESI,EBX
 *  01423E27   56               PUSH ESI
 *  01423E28   53               PUSH EBX
 *  01423E29   FF75 F4          PUSH DWORD PTR SS:[EBP-0xC]
 *  01423E2C   FF15 7CA05101    CALL DWORD PTR DS:[0x151A07C]            ; gdi32.GetTextExtentPoint32A
 *  01423E32   53               PUSH EBX
 *  01423E33   E8 37C80900      CALL .014C066F
 *  01423E38   8B7D EC          MOV EDI,DWORD PTR SS:[EBP-0x14]
 *  01423E3B   8B5D F8          MOV EBX,DWORD PTR SS:[EBP-0x8]
 *  01423E3E   83C4 04          ADD ESP,0x4
 *  01423E41   EB 1E            JMP SHORT .01423E61
 *  01423E43   8B5D F8          MOV EBX,DWORD PTR SS:[EBP-0x8]
 *  01423E46   8D45 D4          LEA EAX,DWORD PTR SS:[EBP-0x2C]
 *  01423E49   50               PUSH EAX
 *  01423E4A   FF73 04          PUSH DWORD PTR DS:[EBX+0x4]
 *  01423E4D   A1 10A35101      MOV EAX,DWORD PTR DS:[0x151A310]
 *  01423E52   FFD0             CALL EAX
 *  01423E54   50               PUSH EAX
 *  01423E55   FF73 04          PUSH DWORD PTR DS:[EBX+0x4]
 *  01423E58   FF75 F4          PUSH DWORD PTR SS:[EBP-0xC]
 *  01423E5B   FF15 7CA05101    CALL DWORD PTR DS:[0x151A07C]            ; gdi32.GetTextExtentPoint32A
 *  01423E61   6A 0A            PUSH 0xA
 *  01423E63   FF73 04          PUSH DWORD PTR DS:[EBX+0x4]
 *  01423E66   BE 01000000      MOV ESI,0x1
 *  01423E6B   E8 56D20900      CALL .014C10C6
 *  01423E70   83C4 08          ADD ESP,0x8
 *  01423E73   85C0             TEST EAX,EAX
 *  01423E75   74 11            JE SHORT .01423E88
 *  01423E77   40               INC EAX
 *  01423E78   6A 0A            PUSH 0xA
 *  01423E7A   50               PUSH EAX
 *  01423E7B   46               INC ESI
 *  01423E7C   E8 45D20900      CALL .014C10C6
 *  01423E81   83C4 08          ADD ESP,0x8
 *  01423E84   85C0             TEST EAX,EAX
 *  01423E86  ^75 EF            JNZ SHORT .01423E77
 *  01423E88   8B45 E0          MOV EAX,DWORD PTR SS:[EBP-0x20]
 *  01423E8B   85C0             TEST EAX,EAX
 *  01423E8D   74 0A            JE SHORT .01423E99
 *  01423E8F   50               PUSH EAX
 *  01423E90   FF75 F4          PUSH DWORD PTR SS:[EBP-0xC]
 *  01423E93   FF15 58A05101    CALL DWORD PTR DS:[0x151A058]            ; gdi32.SelectObject
 *  01423E99   FF75 DC          PUSH DWORD PTR SS:[EBP-0x24]
 *  01423E9C   FF15 60A05101    CALL DWORD PTR DS:[0x151A060]            ; gdi32.DeleteObject
 *  01423EA2   FF75 F4          PUSH DWORD PTR SS:[EBP-0xC]
 *  01423EA5   FF15 74A05101    CALL DWORD PTR DS:[0x151A074]            ; gdi32.DeleteDC
 *  01423EAB   FF75 D8          PUSH DWORD PTR SS:[EBP-0x28]
 *  01423EAE   8D43 14          LEA EAX,DWORD PTR DS:[EBX+0x14]
 *  01423EB1   FF75 D4          PUSH DWORD PTR SS:[EBP-0x2C]
 *  01423EB4   6A 00            PUSH 0x0
 *  01423EB6   6A 00            PUSH 0x0
 *  01423EB8   50               PUSH EAX
 *  01423EB9   FF15 14A45101    CALL DWORD PTR DS:[0x151A414]            ; user32.SetRect
 *  01423EBF   8B45 D8          MOV EAX,DWORD PTR SS:[EBP-0x28]
 *  01423EC2   85C0             TEST EAX,EAX
 *  01423EC4   74 3C            JE SHORT .01423F02
 *  01423EC6   83FE 02          CMP ESI,0x2
 *  01423EC9   7C 37            JL SHORT .01423F02
 *  01423ECB   66:0F6ECE        MOVD MM1,ESI
 *  01423ECF   F3:              PREFIX REP:                              ; Superfluous prefix
 *  01423ED0   0FE6             ???                                      ; Unknown command
 *  01423ED2   C9               LEAVE
 *  01423ED3   66:0F6EC0        MOVD MM0,EAX
 *  01423ED7   F2:              PREFIX REPNE:                            ; Superfluous prefix
 *  01423ED8   0F580D 80C65501  ADDPS XMM1,DQWORD PTR DS:[0x155C680]
 *  01423EDF   F3:              PREFIX REP:                              ; Superfluous prefix
 *  01423EE0   0FE6             ???                                      ; Unknown command
 *  01423EE2   C0F2 0F          SAL DL,0xF
 *
 *  Runtime stack:
 *  0025CDE8   01468CC2  RETURN to .01468CC2 from .01423C20
 *  0025CDEC   0025DE00   ; jichi: point to an unknown small int (such as 2)
 *  0025CDF0   08DF0AB0   ; jichi: text here
 *  0025CDF4   00000000
 *  0025CDF8   08DDCCC8
 *  0025CDFC   00000000
 *  0025CE00   829F8E20
 *  0025CE04   827791CC
 *  0025CE08   82738DD6
 *  0025CE0C   000020AD
 *  0025CE10   00000000
 *  0025CE14   00000000
 *  0025CE18   00000000
 *  0025CE1C   00000000
 *  0025CE20   CC829F8E
 *  0025CE24   82779100
 *  0025CE28   738D00D6
 *  0025CE2C   DC82AB82
 *  0025CE30   A982B782
 *  0025CE34   61004881
 *  0025CE38   00000001
 *  0025CE3C  /0025CE74
 *  0025CE40  |00713BBB  RETURN to d3dx9_31.00713BBB
 *
 *  Sample game: 神楽道中記
 *
 *  004C635D   CC               INT3
 *  004C635E   CC               INT3
 *  004C635F   CC               INT3
 *  004C6360   83EC 28          SUB ESP,0x28
 *  004C6363   53               PUSH EBX
 *  004C6364   55               PUSH EBP
 *  004C6365   56               PUSH ESI
 *  004C6366   57               PUSH EDI
 *  004C6367   8BD9             MOV EBX,ECX
 *  004C6369   6A 24            PUSH 0x24
 *  004C636B   895C24 24        MOV DWORD PTR SS:[ESP+0x24],EBX
 *  004C636F   E8 50D70200      CALL .004F3AC4
 *  004C6374   33D2             XOR EDX,EDX
 *  004C6376   83C4 04          ADD ESP,0x4
 *  004C6379   3BC2             CMP EAX,EDX
 *  004C637B   74 16            JE SHORT .004C6393
 *  004C637D   8910             MOV DWORD PTR DS:[EAX],EDX
 *  004C637F   8950 04          MOV DWORD PTR DS:[EAX+0x4],EDX
 *  004C6382   C740 08 FFFFFFFF MOV DWORD PTR DS:[EAX+0x8],-0x1
 *  004C6389   8950 10          MOV DWORD PTR DS:[EAX+0x10],EDX
 *  004C638C   8950 0C          MOV DWORD PTR DS:[EAX+0xC],EDX
 *  004C638F   8BE8             MOV EBP,EAX
 *  004C6391   EB 02            JMP SHORT .004C6395
 *  004C6393   33ED             XOR EBP,EBP
 *  004C6395   8B4424 3C        MOV EAX,DWORD PTR SS:[ESP+0x3C]
 *  004C6399   8BF0             MOV ESI,EAX
 *  004C639B   B9 09000000      MOV ECX,0x9
 *  004C63A0   8BFD             MOV EDI,EBP
 *  004C63A2   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS>
 *  004C63A4   8955 04          MOV DWORD PTR SS:[EBP+0x4],EDX
 *  004C63A7   8B40 04          MOV EAX,DWORD PTR DS:[EAX+0x4]
 *  004C63AA   50               PUSH EAX
 *  004C63AB   8BCD             MOV ECX,EBP
 *  004C63AD   896C24 1C        MOV DWORD PTR SS:[ESP+0x1C],EBP
 *  004C63B1   E8 1AC9FFFF      CALL .004C2CD0
 *  004C63B6   8B4C24 3C        MOV ECX,DWORD PTR SS:[ESP+0x3C]
 *  004C63BA   8B71 0C          MOV ESI,DWORD PTR DS:[ECX+0xC]
 *  004C63BD   85F6             TEST ESI,ESI
 *  004C63BF   74 2E            JE SHORT .004C63EF
 *  004C63C1   56               PUSH ESI
 *  004C63C2   FF15 24425400    CALL DWORD PTR DS:[0x544224]             ; kernel32.lstrlenA
 *  004C63C8   8BF8             MOV EDI,EAX
 *  004C63CA   83C7 01          ADD EDI,0x1
 *  004C63CD   57               PUSH EDI
 *  004C63CE   E8 91CF0200      CALL .004F3364
 *  004C63D3   83C4 04          ADD ESP,0x4
 *  004C63D6   85C0             TEST EAX,EAX
 *  004C63D8   894424 3C        MOV DWORD PTR SS:[ESP+0x3C],EAX
 *  004C63DC   74 11            JE SHORT .004C63EF
 *  004C63DE   57               PUSH EDI
 *  004C63DF   56               PUSH ESI
 *  004C63E0   50               PUSH EAX
 *  004C63E1   E8 9AD70200      CALL .004F3B80
 *  004C63E6   8B4424 48        MOV EAX,DWORD PTR SS:[ESP+0x48]
 *  004C63EA   83C4 0C          ADD ESP,0xC
 *  004C63ED   EB 02            JMP SHORT .004C63F1
 *  004C63EF   33C0             XOR EAX,EAX
 *  004C63F1   8D73 54          LEA ESI,DWORD PTR DS:[EBX+0x54]
 *  004C63F4   8D5424 18        LEA EDX,DWORD PTR SS:[ESP+0x18]
 *  004C63F8   52               PUSH EDX
 *  004C63F9   8BCE             MOV ECX,ESI
 *  004C63FB   8945 0C          MOV DWORD PTR SS:[EBP+0xC],EAX
 *  004C63FE   897424 30        MOV DWORD PTR SS:[ESP+0x30],ESI
 *  004C6402   E8 79FEFFFF      CALL .004C6280
 *  004C6407   8D4424 3C        LEA EAX,DWORD PTR SS:[ESP+0x3C]
 *  004C640B   50               PUSH EAX
 *  004C640C   8D4B 68          LEA ECX,DWORD PTR DS:[EBX+0x68]
 *  004C640F   C74424 40 000000>MOV DWORD PTR SS:[ESP+0x40],0x0
 *  004C6417   E8 D4FEFFFF      CALL .004C62F0
 *  004C641C   837B 18 00       CMP DWORD PTR DS:[EBX+0x18],0x0
 *  004C6420   8D43 18          LEA EAX,DWORD PTR DS:[EBX+0x18]
 *  004C6423   0F84 BD010000    JE .004C65E6
 *  004C6429   50               PUSH EAX
 *  004C642A   FF15 5C405400    CALL DWORD PTR DS:[0x54405C]             ; gdi32.CreateFontIndirectA
 *  004C6430   8BF0             MOV ESI,EAX
 *  004C6432   85F6             TEST ESI,ESI
 *  004C6434   897424 28        MOV DWORD PTR SS:[ESP+0x28],ESI
 *  004C6438   75 0D            JNZ SHORT .004C6447
 *  004C643A   5F               POP EDI
 *  004C643B   5E               POP ESI
 *  004C643C   5D               POP EBP
 *  004C643D   83C8 FF          OR EAX,0xFFFFFFFF
 *  004C6440   5B               POP EBX
 *  004C6441   83C4 28          ADD ESP,0x28
 *  004C6444   C2 0400          RETN 0x4
 *  004C6447   6A 00            PUSH 0x0
 *  004C6449   FF15 80405400    CALL DWORD PTR DS:[0x544080]             ; gdi32.CreateCompatibleDC
 *  004C644F   8BF8             MOV EDI,EAX
 *  004C6451   56               PUSH ESI
 *  004C6452   57               PUSH EDI
 *  004C6453   897C24 20        MOV DWORD PTR SS:[ESP+0x20],EDI
 *  004C6457   FF15 78405400    CALL DWORD PTR DS:[0x544078]             ; gdi32.SelectObject
 *  004C645D   894424 24        MOV DWORD PTR SS:[ESP+0x24],EAX
 *  004C6461   33C0             XOR EAX,EAX
 *  004C6463   6A 01            PUSH 0x1
 *  004C6465   57               PUSH EDI
 *  004C6466   894424 38        MOV DWORD PTR SS:[ESP+0x38],EAX
 *  004C646A   894424 3C        MOV DWORD PTR SS:[ESP+0x3C],EAX
 *  004C646E   FF15 60405400    CALL DWORD PTR DS:[0x544060]             ; gdi32.SetMapMode
 *  004C6474   8B45 04          MOV EAX,DWORD PTR SS:[EBP+0x4]
 *  004C6477   6A 5B            PUSH 0x5B
 *  004C6479   50               PUSH EAX
 *  004C647A   E8 7A130300      CALL .004F77F9
 *  004C647F   8BF0             MOV ESI,EAX
 *  004C6481   83C4 08          ADD ESP,0x8
 *  004C6484   85F6             TEST ESI,ESI
 *  004C6486   0F84 E3000000    JE .004C656F
 *  004C648C   8B4D 04          MOV ECX,DWORD PTR SS:[EBP+0x4]
 *  004C648F   51               PUSH ECX
 *  004C6490   FF15 24425400    CALL DWORD PTR DS:[0x544224]             ; kernel32.lstrlenA
 *  004C6496   8BD8             MOV EBX,EAX
 *  004C6498   8D53 20          LEA EDX,DWORD PTR DS:[EBX+0x20]
 *  004C649B   8BFE             MOV EDI,ESI
 *  004C649D   2B7D 04          SUB EDI,DWORD PTR SS:[EBP+0x4]
 *  004C64A0   52               PUSH EDX
 *  004C64A1   E8 BECE0200      CALL .004F3364
 *  004C64A6   8B4D 04          MOV ECX,DWORD PTR SS:[EBP+0x4]
 *  004C64A9   57               PUSH EDI
 *  004C64AA   51               PUSH ECX
 *  004C64AB   50               PUSH EAX
 *  004C64AC   894424 24        MOV DWORD PTR SS:[ESP+0x24],EAX
 *  004C64B0   E8 CBD60200      CALL .004F3B80
 *  004C64B5   8B45 04          MOV EAX,DWORD PTR SS:[EBP+0x4]
 *  004C64B8   8B4C24 24        MOV ECX,DWORD PTR SS:[ESP+0x24]
 *  004C64BC   03C3             ADD EAX,EBX
 *  004C64BE   03F9             ADD EDI,ECX
 *  004C64C0   83C4 10          ADD ESP,0x10
 *  004C64C3   3BF0             CMP ESI,EAX
 *  004C64C5   897C24 10        MOV DWORD PTR SS:[ESP+0x10],EDI
 *  004C64C9   C64424 3C 00     MOV BYTE PTR SS:[ESP+0x3C],0x0
 *  004C64CE   894424 1C        MOV DWORD PTR SS:[ESP+0x1C],EAX
 *  004C64D2   73 6D            JNB SHORT .004C6541
 *  004C64D4   56               PUSH ESI
 *  004C64D5   FF15 68445400    CALL DWORD PTR DS:[0x544468]             ; user32.CharNextA
 *  004C64DB   8BD8             MOV EBX,EAX
 *  004C64DD   8BFB             MOV EDI,EBX
 *  004C64DF   2BFE             SUB EDI,ESI
 *  004C64E1   83FF 01          CMP EDI,0x1
 *  004C64E4   75 2F            JNZ SHORT .004C6515
 *  004C64E6   807C24 3C 00     CMP BYTE PTR SS:[ESP+0x3C],0x0
 *  004C64EB   74 0C            JE SHORT .004C64F9
 *  004C64ED   803E 5D          CMP BYTE PTR DS:[ESI],0x5D
 *  004C64F0   75 3F            JNZ SHORT .004C6531
 *  004C64F2   C64424 3C 00     MOV BYTE PTR SS:[ESP+0x3C],0x0
 *  004C64F7   EB 38            JMP SHORT .004C6531
 *  004C64F9   8A06             MOV AL,BYTE PTR DS:[ESI]
 *  004C64FB   3C 5B            CMP AL,0x5B
 *  004C64FD   75 07            JNZ SHORT .004C6506
 *  004C64FF   C64424 3C 01     MOV BYTE PTR SS:[ESP+0x3C],0x1
 *  004C6504   EB 2B            JMP SHORT .004C6531
 *  004C6506   8B4C24 10        MOV ECX,DWORD PTR SS:[ESP+0x10]
 *  004C650A   8801             MOV BYTE PTR DS:[ECX],AL
 *  004C650C   83C1 01          ADD ECX,0x1
 *  004C650F   894C24 10        MOV DWORD PTR SS:[ESP+0x10],ECX
 *  004C6513   EB 1C            JMP SHORT .004C6531
 *  004C6515   807C24 3C 00     CMP BYTE PTR SS:[ESP+0x3C],0x0
 *  004C651A   75 15            JNZ SHORT .004C6531
 *  004C651C   57               PUSH EDI
 *  004C651D   56               PUSH ESI
 *  004C651E   8B7424 18        MOV ESI,DWORD PTR SS:[ESP+0x18]
 *  004C6522   56               PUSH ESI
 *  004C6523   E8 58D60200      CALL .004F3B80
 *  004C6528   83C4 0C          ADD ESP,0xC
 *  004C652B   03F7             ADD ESI,EDI
 *  004C652D   897424 10        MOV DWORD PTR SS:[ESP+0x10],ESI
 *  004C6531   3B5C24 1C        CMP EBX,DWORD PTR SS:[ESP+0x1C]
 *  004C6535   8BF3             MOV ESI,EBX
 *  004C6537  ^72 9B            JB SHORT .004C64D4
 *  004C6539   8B4C24 14        MOV ECX,DWORD PTR SS:[ESP+0x14]
 *  004C653D   8B7C24 10        MOV EDI,DWORD PTR SS:[ESP+0x10]
 *  004C6541   8B4424 18        MOV EAX,DWORD PTR SS:[ESP+0x18]
 *  004C6545   8D5424 30        LEA EDX,DWORD PTR SS:[ESP+0x30]
 *  004C6549   52               PUSH EDX
 *  004C654A   C607 00          MOV BYTE PTR DS:[EDI],0x0
 *  004C654D   2BF9             SUB EDI,ECX
 *  004C654F   57               PUSH EDI
 *  004C6550   51               PUSH ECX
 *  004C6551   50               PUSH EAX
 *  004C6552   FF15 58405400    CALL DWORD PTR DS:[0x544058]             ; gdi32.GetTextExtentPoint32A
 *  004C6558   8B4C24 14        MOV ECX,DWORD PTR SS:[ESP+0x14]
 *  004C655C   51               PUSH ECX
 *  004C655D   E8 63060300      CALL .004F6BC5
 *  004C6562   8B5C24 24        MOV EBX,DWORD PTR SS:[ESP+0x24]
 *  004C6566   8B7C24 1C        MOV EDI,DWORD PTR SS:[ESP+0x1C]
 *  004C656A   83C4 04          ADD ESP,0x4
 *  004C656D   EB 1B            JMP SHORT .004C658A
 *  004C656F   8B45 04          MOV EAX,DWORD PTR SS:[EBP+0x4]
 *  004C6572   8D5424 30        LEA EDX,DWORD PTR SS:[ESP+0x30]
 *  004C6576   52               PUSH EDX
 *  004C6577   50               PUSH EAX
 *  004C6578   FF15 24425400    CALL DWORD PTR DS:[0x544224]             ; kernel32.lstrlenA
 *  004C657E   8B4D 04          MOV ECX,DWORD PTR SS:[EBP+0x4]
 *  004C6581   50               PUSH EAX
 *  004C6582   51               PUSH ECX
 *  004C6583   57               PUSH EDI
 *  004C6584   FF15 58405400    CALL DWORD PTR DS:[0x544058]             ; gdi32.GetTextExtentPoint32A
 *  004C658A   8B4424 24        MOV EAX,DWORD PTR SS:[ESP+0x24]
 *  004C658E   85C0             TEST EAX,EAX
 *  004C6590   74 08            JE SHORT .004C659A
 *  004C6592   50               PUSH EAX
 *  004C6593   57               PUSH EDI
 *  004C6594   FF15 78405400    CALL DWORD PTR DS:[0x544078]             ; gdi32.SelectObject
 *  004C659A   8B5424 28        MOV EDX,DWORD PTR SS:[ESP+0x28]
 *  004C659E   52               PUSH EDX
 *  004C659F   FF15 6C405400    CALL DWORD PTR DS:[0x54406C]             ; gdi32.DeleteObject
 *  004C65A5   57               PUSH EDI
 *  004C65A6   FF15 74405400    CALL DWORD PTR DS:[0x544074]             ; gdi32.DeleteDC
 *  004C65AC   8B4424 34        MOV EAX,DWORD PTR SS:[ESP+0x34]
 *  004C65B0   8B4C24 30        MOV ECX,DWORD PTR SS:[ESP+0x30]
 *  004C65B4   50               PUSH EAX
 *  004C65B5   51               PUSH ECX
 *  004C65B6   6A 00            PUSH 0x0
 *  004C65B8   6A 00            PUSH 0x0
 *  004C65BA   8D55 14          LEA EDX,DWORD PTR SS:[EBP+0x14]
 *  004C65BD   52               PUSH EDX
 *  004C65BE   FF15 60445400    CALL DWORD PTR DS:[0x544460]             ; user32.SetRect
 *  004C65C4   8B83 E8000000    MOV EAX,DWORD PTR DS:[EBX+0xE8]
 *  004C65CA   8945 20          MOV DWORD PTR SS:[EBP+0x20],EAX
 *  004C65CD   8B83 E0000000    MOV EAX,DWORD PTR DS:[EBX+0xE0]
 *  004C65D3   8B6D 1C          MOV EBP,DWORD PTR SS:[EBP+0x1C]
 *  004C65D6   3BC5             CMP EAX,EBP
 *  004C65D8   7F 02            JG SHORT .004C65DC
 *  004C65DA   8BC5             MOV EAX,EBP
 *  004C65DC   8B7424 2C        MOV ESI,DWORD PTR SS:[ESP+0x2C]
 *  004C65E0   8983 E0000000    MOV DWORD PTR DS:[EBX+0xE0],EAX
 *  004C65E6   8B8B E8000000    MOV ECX,DWORD PTR DS:[EBX+0xE8]
 *  004C65EC   018B E4000000    ADD DWORD PTR DS:[EBX+0xE4],ECX
 *  004C65F2   8BCB             MOV ECX,EBX
 *  004C65F4   E8 47C7FFFF      CALL .004C2D40
 *  004C65F9   8B46 04          MOV EAX,DWORD PTR DS:[ESI+0x4]
 *  004C65FC   85C0             TEST EAX,EAX
 *  004C65FE   75 0F            JNZ SHORT .004C660F
 *  004C6600   33F6             XOR ESI,ESI
 *  004C6602   5F               POP EDI
 *  004C6603   8D46 FF          LEA EAX,DWORD PTR DS:[ESI-0x1]
 *  004C6606   5E               POP ESI
 *  004C6607   5D               POP EBP
 *  004C6608   5B               POP EBX
 *  004C6609   83C4 28          ADD ESP,0x28
 *  004C660C   C2 0400          RETN 0x4
 *  004C660F   8B76 08          MOV ESI,DWORD PTR DS:[ESI+0x8]
 *  004C6612   2BF0             SUB ESI,EAX
 *  004C6614   C1FE 02          SAR ESI,0x2
 *  004C6617   5F               POP EDI
 *  004C6618   8D46 FF          LEA EAX,DWORD PTR DS:[ESI-0x1]
 *  004C661B   5E               POP ESI
 *  004C661C   5D               POP EBP
 *  004C661D   5B               POP EBX
 *  004C661E   83C4 28          ADD ESP,0x28
 *  004C6621   C2 0400          RETN 0x4
 *  004C6624   CC               INT3
 *  004C6625   CC               INT3
 *  004C6626   CC               INT3
 *
 *  Stack
 *  0012E460   00446BBD  RETURN to .00446BBD from .004C6360
 *  0012E464   0012E4B8  text here, the same value as eax
 *  0012E468   00000003
 *  0012E46C   07E87CA8
 *  0012E470   07E92830
 *  0012E474   07E92810
 *  0012E478   07E5EA50
 *  0012E47C   07E5EA50
 *
 *  EAX 0012E4B8
 *  ECX 01EA6490
 *  EDX 0012E4DC    ; jichi: text here
 *  EBX 00000000
 *  ESP 0012E460
 *  EBP FFFFFFFF
 *  ESI 00000000
 *  EDI 07E92810
 *  EIP 004C6360 .004C6360
 */
bool attach(ulong startAddress, ulong stopAddress)
{
  ulong addr = MemDbg::findLastCallerAddressAfterInt3((ulong)::GetTextExtentPoint32A, startAddress, stopAddress);
  if (!addr)
    return false;
  return winhook::hook_before(addr, Private::hookBefore);
  //int count = 0;
  //auto fun = [&count](ulong call) -> bool {
  //  count += winhook::hook_both(call, Private::hookBefore, Private::hookAfter);
  //  return true; // replace all functions
  //};
  //MemDbg::iterNearCallAddress(fun, addr, startAddress, stopAddress);
  //DOUT("call number =" << count);
  //return count;
}

} // namespace OtherHook
namespace ChoiceHook {

namespace Private {

  bool hookBefore(winhook::hook_stack *s)
  {
    enum { TextCapacity = 0x10 };
    LPCSTR text = (LPCSTR)s->ecx; // new game, text in arg2 for the caller of GetTextExtentPoint32A
    if (!Engine::isAddressWritable(text))
      return true;
    //if (OtherHook::translatedTexts_.find(text) != OtherHook::translatedTexts_.cend())
    //  return true;
    LPCSTR trimmedText = OtherHook::ltrim(text);
    if (!trimmedText || !*trimmedText)
      return true;
    enum { role = Engine::OtherRole };
    auto split = s->stack[0]; // retaddr
    auto sig = Engine::hashThreadSignature(role, split);
    QByteArray oldData = trimmedText,
               newData = EngineController::instance()->dispatchTextA(oldData, role, sig);
    if (newData == oldData)
      return true;
    //::strcpy(text, newData.constData());
    if (trimmedText != text)
      newData.prepend(text, trimmedText - text);

    s->ecx = (DWORD)newData.constData();
    return true;
  }

} // namespace Private

/**
 *  Sample game: 神楽花莚譚
 *
 *  Here's the caller of the scenario hook, text in ecx:
 *  01378BAA   CC               INT3
 *  01378BAB   CC               INT3
 *  01378BAC   CC               INT3
 *  01378BAD   CC               INT3
 *  01378BAE   CC               INT3
 *  01378BAF   CC               INT3
 *  01378BB0   55               PUSH EBP
 *  01378BB1   8BEC             MOV EBP,ESP
 *  01378BB3   B8 38100000      MOV EAX,0x1038
 *  01378BB8   E8 D3890600      CALL .013E1590
 *  01378BBD   803D 59704B01 00 CMP BYTE PTR DS:[0x14B7059],0x0
 *  01378BC4   53               PUSH EBX
 *  01378BC5   56               PUSH ESI
 *  01378BC6   57               PUSH EDI
 *  01378BC7   8955 F0          MOV DWORD PTR SS:[EBP-0x10],EDX
 *  01378BCA   8BF9             MOV EDI,ECX     ; jichi: edi is used as ecx for this
 *  01378BCC   74 09            JE SHORT .01378BD7
 *  01378BCE   C605 5A704B01 01 MOV BYTE PTR DS:[0x14B705A],0x1
 *  01378BD5   EB 0D            JMP SHORT .01378BE4
 *  01378BD7   803D 58704B01 00 CMP BYTE PTR DS:[0x14B7058],0x0
 *  01378BDE   0F85 FB000000    JNZ .01378CDF
 *  01378BE4   8B35 D0EE4A01    MOV ESI,DWORD PTR DS:[0x14AEED0]
 *  01378BEA   85F6             TEST ESI,ESI
 *  01378BEC   74 1D            JE SHORT .01378C0B
 *  01378BEE   8B0D D40C4B01    MOV ECX,DWORD PTR DS:[0x14B0CD4]
 *  01378BF4   8B01             MOV EAX,DWORD PTR DS:[ECX]
 *  01378BF6   3BC1             CMP EAX,ECX
 *  01378BF8   74 11            JE SHORT .01378C0B
 *  01378BFA   8D9B 00000000    LEA EBX,DWORD PTR DS:[EBX]
 *  01378C00   3970 08          CMP DWORD PTR DS:[EAX+0x8],ESI
 *  01378C03   74 19            JE SHORT .01378C1E
 *  01378C05   8B00             MOV EAX,DWORD PTR DS:[EAX]
 *  01378C07   3BC1             CMP EAX,ECX
 *  01378C09  ^75 F5            JNZ SHORT .01378C00
 *  01378C0B   E8 E0A8FFFF      CALL .013734F0
 *  01378C10   8B0D D40C4B01    MOV ECX,DWORD PTR DS:[0x14B0CD4]
 *  01378C16   8BF0             MOV ESI,EAX
 *  01378C18   8935 D0EE4A01    MOV DWORD PTR DS:[0x14AEED0],ESI
 *  01378C1E   0FBE07           MOVSX EAX,BYTE PTR DS:[EDI]
 *  01378C21   33DB             XOR EBX,EBX
 *  01378C23   895D F4          MOV DWORD PTR SS:[EBP-0xC],EBX
 *  01378C26   C745 F8 FFFFFFFF MOV DWORD PTR SS:[EBP-0x8],-0x1
 *  01378C2D   83F8 40          CMP EAX,0x40
 *  01378C30   77 3E            JA SHORT .01378C70
 *  01378C32   0FB680 488D3701  MOVZX EAX,BYTE PTR DS:[EAX+0x1378D48]
 *  01378C39   FF2485 308D3701  JMP DWORD PTR DS:[EAX*4+0x1378D30]
 *  01378C40   47               INC EDI
 *  01378C41   83CB 08          OR EBX,0x8
 *  01378C44   C745 F8 FF9000FF MOV DWORD PTR SS:[EBP-0x8],0xFF0090FF
 *  01378C4B   EB 1B            JMP SHORT .01378C68
 *  01378C4D   47               INC EDI
 *  01378C4E   83CB 10          OR EBX,0x10
 *  01378C51   C745 F8 FF9000FF MOV DWORD PTR SS:[EBP-0x8],0xFF0090FF
 *  01378C58   EB 0E            JMP SHORT .01378C68
 *  01378C5A   47               INC EDI
 *  01378C5B   83CB 04          OR EBX,0x4
 *  01378C5E   EB 08            JMP SHORT .01378C68
 *  01378C60   47               INC EDI
 *  01378C61   C745 F4 01000000 MOV DWORD PTR SS:[EBP-0xC],0x1
 *  01378C68   0FBE07           MOVSX EAX,BYTE PTR DS:[EDI]
 *  01378C6B   83F8 40          CMP EAX,0x40
 *  01378C6E  ^76 C2            JBE SHORT .01378C32
 *  01378C70   57               PUSH EDI    ; jichi: ecx as args is here
 *  01378C71   8D85 CCEFFFFF    LEA EAX,DWORD PTR SS:[EBP-0x1034]
 *  01378C77   68 584B4601      PUSH .01464B58                           ; ASCII " %s "
 *  01378C7C   50               PUSH EAX
 *  01378C7D   E8 187A0500      CALL .013D069A
 *  01378C82   8D85 CCEFFFFF    LEA EAX,DWORD PTR SS:[EBP-0x1034]
 *  01378C88   8945 D0          MOV DWORD PTR SS:[EBP-0x30],EAX
 *  01378C8B   8B45 F8          MOV EAX,DWORD PTR SS:[EBP-0x8]
 *  01378C8E   8945 D4          MOV DWORD PTR SS:[EBP-0x2C],EAX
 *  01378C91   8B45 F0          MOV EAX,DWORD PTR SS:[EBP-0x10]
 *  01378C94   8945 DC          MOV DWORD PTR SS:[EBP-0x24],EAX
 *  01378C97   8B45 08          MOV EAX,DWORD PTR SS:[EBP+0x8]
 *  01378C9A   83C4 0C          ADD ESP,0xC
 *  01378C9D   895D CC          MOV DWORD PTR SS:[EBP-0x34],EBX
 *  01378CA0   85C0             TEST EAX,EAX
 *  01378CA2   74 08            JE SHORT .01378CAC
 *  01378CA4   8038 00          CMP BYTE PTR DS:[EAX],0x0
 *  01378CA7   8945 D8          MOV DWORD PTR SS:[EBP-0x28],EAX
 *  01378CAA   75 07            JNZ SHORT .01378CB3
 *  01378CAC   C745 D8 00000000 MOV DWORD PTR SS:[EBP-0x28],0x0
 *  01378CB3   8B0D D0EE4A01    MOV ECX,DWORD PTR DS:[0x14AEED0]
 *  01378CB9   8D45 CC          LEA EAX,DWORD PTR SS:[EBP-0x34]
 *  01378CBC   50               PUSH EAX
 *  01378CBD   E8 5EAFFBFF      CALL .01333C20   ; jichi: caller of GetTextExtentPoint32A is here
 *  01378CC2   837D F4 00       CMP DWORD PTR SS:[EBP-0xC],0x0
 *  01378CC6   74 12            JE SHORT .01378CDA
 *  01378CC8   8B0D D0EE4A01    MOV ECX,DWORD PTR DS:[0x14AEED0]
 *  01378CCE   2B81 A8000000    SUB EAX,DWORD PTR DS:[ECX+0xA8]
 *  01378CD4   50               PUSH EAX
 *  01378CD5   E8 86B3FBFF      CALL .01334060
 *  01378CDA   E8 31A9FFFF      CALL .01373610
 *  01378CDF   5F               POP EDI
 *  01378CE0   5E               POP ESI
 *  01378CE1   5B               POP EBX
 *  01378CE2   8BE5             MOV ESP,EBP
 *  01378CE4   5D               POP EBP
 *  01378CE5   C3               RETN
 *  01378CE6   85F6             TEST ESI,ESI
 *  01378CE8   74 32            JE SHORT .01378D1C
 *  01378CEA   8B01             MOV EAX,DWORD PTR DS:[ECX]
 *  01378CEC   3BC1             CMP EAX,ECX
 *  01378CEE   74 2C            JE SHORT .01378D1C
 *  01378CF0   3970 08          CMP DWORD PTR DS:[EAX+0x8],ESI
 *  01378CF3   74 17            JE SHORT .01378D0C
 *  01378CF5   8B00             MOV EAX,DWORD PTR DS:[EAX]
 *  01378CF7   3BC1             CMP EAX,ECX
 *  01378CF9  ^75 F5            JNZ SHORT .01378CF0
 *  01378CFB   C705 D0EE4A01 00>MOV DWORD PTR DS:[0x14AEED0],0x0
 *  01378D05   5F               POP EDI
 *  01378D06   5E               POP ESI
 *  01378D07   5B               POP EBX
 *  01378D08   8BE5             MOV ESP,EBP
 *  01378D0A   5D               POP EBP
 *  01378D0B   C3               RETN
 *  01378D0C   8BCE             MOV ECX,ESI
 *  01378D0E   E8 9D99FBFF      CALL .013326B0
 *  01378D13   56               PUSH ESI
 *  01378D14   E8 C7680500      CALL .013CF5E0
 *  01378D19   83C4 04          ADD ESP,0x4
 *  01378D1C   5F               POP EDI
 *  01378D1D   5E               POP ESI
 *  01378D1E   C705 D0EE4A01 00>MOV DWORD PTR DS:[0x14AEED0],0x0
 *  01378D28   5B               POP EBX
 *  01378D29   8BE5             MOV ESP,EBP
 *  01378D2B   5D               POP EBP
 *  01378D2C   C3               RETN
 *  01378D2D   8D49 00          LEA ECX,DWORD PTR DS:[ECX]
 *  01378D30   E6 8C            OUT 0x8C,AL                              ; I/O command
 *  01378D32   37               AAA
 *  01378D33   0160 8C          ADD DWORD PTR DS:[EAX-0x74],ESP
 *  01378D36   37               AAA
 *  01378D37   0140 8C          ADD DWORD PTR DS:[EAX-0x74],EAX
 *  01378D3A   37               AAA
 *  01378D3B   015A 8C          ADD DWORD PTR DS:[EDX-0x74],EBX
 *  01378D3E   37               AAA
 *  01378D3F   014D 8C          ADD DWORD PTR SS:[EBP-0x74],ECX
 *  01378D42   37               AAA
 *  01378D43   0170 8C          ADD DWORD PTR DS:[EAX-0x74],ESI
 *  01378D46   37               AAA
 *  01378D47   0100             ADD DWORD PTR DS:[EAX],EAX
 *  01378D49   05 05050505      ADD EAX,0x5050505
 *  01378D4E   05 05050505      ADD EAX,0x5050505
 *  01378D53   05 05050505      ADD EAX,0x5050505
 *  01378D58   05 05050505      ADD EAX,0x5050505
 *  01378D5D   05 05050505      ADD EAX,0x5050505
 *  01378D62   05 05050505      ADD EAX,0x5050505
 *  01378D67   05 05010505      ADD EAX,0x5050105
 *  01378D6C   05 05050505      ADD EAX,0x5050505
 *  01378D71   05 02030505      ADD EAX,0x5050302
 *  01378D76   05 05050505      ADD EAX,0x5050505
 *  01378D7B   05 05050505      ADD EAX,0x5050505
 *  01378D80   05 05050505      ADD EAX,0x5050505
 *  01378D85   05 050504CC      ADD EAX,0xCC040505
 *  01378D8A   CC               INT3
 *  01378D8B   CC               INT3
 *  01378D8C   CC               INT3
 *  01378D8D   CC               INT3
 *  01378D8E   CC               INT3
 *  01378D8F   CC               INT3
 *
 */
bool attach(ulong startAddress, ulong stopAddress)
{
  const uint8_t bytes[] = {
    0x89,0x45, 0xd0, // 01378c88   8945 d0          mov dword ptr ss:[ebp-0x30],eax
    0x8b,0x45, 0xf8, // 01378c8b   8b45 f8          mov eax,dword ptr ss:[ebp-0x8]
    0x89,0x45, 0xd4, // 01378c8e   8945 d4          mov dword ptr ss:[ebp-0x2c],eax
    0x8b,0x45, 0xf0, // 01378c91   8b45 f0          mov eax,dword ptr ss:[ebp-0x10]
    0x89,0x45, 0xdc, // 01378c94   8945 dc          mov dword ptr ss:[ebp-0x24],eax
    0x8b,0x45, 0x08, // 01378c97   8b45 08          mov eax,dword ptr ss:[ebp+0x8]
    0x83,0xc4, 0x0c, // 01378c9a   83c4 0c          add esp,0xc
    0x89,0x5d, 0xcc, // 01378c9d   895d cc          mov dword ptr ss:[ebp-0x34],ebx
    0x85,0xc0,       // 01378ca0   85c0             test eax,eax
    0x74, 0x08       // 01378ca2   74 08            je short .01378cac
  };
  ulong addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  //return winhook::hook_before(addr, Private::hookBefore);
  int count = 0;
  auto fun = [&count](ulong call) -> bool {
    count += winhook::hook_before(call, Private::hookBefore);
    return true; // replace all functions
  };
  MemDbg::iterNearCallAddress(fun, addr, startAddress, stopAddress);
  DOUT("call number =" << count);
  return count;
}

} // namespace ChoiceHook

namespace ChoiceHook {

namespace Private {

  struct FunctionStack
  {
    DWORD retaddr;
    LPDWORD arg1;   // unknown
    LPCSTR begin,   // arg2, start of the text
           end;     // arg3, stop of the text, usually \0

    bool isValid() const
    { return Engine::isAddressWritable(begin, end - begin) && end - begin >= 3; }
  };

  bool hookBefore(winhook::hook_stack *s)
  {
    static QByteArray data_;
    auto args = (FunctionStack *)s->stack; // new game, text in arg2 for the caller of GetTextExtentPoint32A
    if (!args->isValid())
      return false;
    enum { role = Engine::OtherRole };
    auto split = args->retaddr;
    auto sig = Engine::hashThreadSignature(role, split);
    QByteArray oldData(args->begin, args->end - args->begin),
               newData = EngineController::instance()->dispatchTextA(oldData, role, sig);
    if (newData == oldData)
      return true;
    data_ = newData;
    args->begin = data_.constData();
    args->end = args->begin + data_.size();
    return true;
  }

} // namespace Private

/**
 *  Sample game: 神楽花莚譚
 *  Found by tracing CharNextA
 *
 *  0026E210   01451F57  RETURN to .01451F57 from .013FFD90
 *  0026E214   0026E2B0
 *  0026E218   01152080 ; jichi: text starts
 *  0026E21C   0115208E ; jichi: pointed to \0
 *  0026E220   00000000
 *  0026E224   185DDC6C
 *  0026E228   07B32310
 *  0026E22C   000001B6
 *
 *  013FFD8D   CC               INT3
 *  013FFD8E   CC               INT3
 *  013FFD8F   CC               INT3
 *  013FFD90   55               PUSH EBP    ; jichi: text is between arg2 and arg3, but it is used to measure text length instead of paint it
 *  013FFD91   8BEC             MOV EBP,ESP
 *  013FFD93   83EC 10          SUB ESP,0x10
 *  013FFD96   53               PUSH EBX
 *  013FFD97   8B5D 08          MOV EBX,DWORD PTR SS:[EBP+0x8]
 *  013FFD9A   56               PUSH ESI
 *  013FFD9B   8B75 0C          MOV ESI,DWORD PTR SS:[EBP+0xC]
 *  013FFD9E   57               PUSH EDI
 *  013FFD9F   33C0             XOR EAX,EAX
 *  013FFDA1   8BF9             MOV EDI,ECX
 *  013FFDA3   0F57C9           XORPS XMM1,XMM1
 *  013FFDA6   897D F4          MOV DWORD PTR SS:[EBP-0xC],EDI
 *  013FFDA9   C703 00000000    MOV DWORD PTR DS:[EBX],0x0
 *  013FFDAF   C743 04 00000000 MOV DWORD PTR DS:[EBX+0x4],0x0
 *  013FFDB6   F3:0F114D 0C     MOVSS DWORD PTR SS:[EBP+0xC],XMM1
 *  013FFDBB   8945 F8          MOV DWORD PTR SS:[EBP-0x8],EAX
 *  013FFDBE   3B75 10          CMP ESI,DWORD PTR SS:[EBP+0x10]
 *  013FFDC1   0F83 57020000    JNB .0140001E
 *  013FFDC7   8B15 18A45401    MOV EDX,DWORD PTR DS:[0x154A418]         ; user32.CharNextA
 *  013FFDCD   8D49 00          LEA ECX,DWORD PTR DS:[ECX]
 *  013FFDD0   8A0E             MOV CL,BYTE PTR DS:[ESI]
 *  013FFDD2   0FBEC1           MOVSX EAX,CL
 *  013FFDD5   83F8 7B          CMP EAX,0x7B
 *  013FFDD8   0F87 EF000000    JA .013FFECD
 *  013FFDDE   0FB680 44004001  MOVZX EAX,BYTE PTR DS:[EAX+0x1400044]
 *  013FFDE5   FF2485 2C004001  JMP DWORD PTR DS:[EAX*4+0x140002C]
 *  013FFDEC   46               INC ESI
 *  013FFDED   E9 23020000      JMP .01400015
 *  013FFDF2   807E 01 0A       CMP BYTE PTR DS:[ESI+0x1],0xA
 *  013FFDF6   75 05            JNZ SHORT .013FFDFD
 *  013FFDF8   56               PUSH ESI
 *  013FFDF9   FFD2             CALL EDX
 *  013FFDFB   8BF0             MOV ESI,EAX
 *  013FFDFD   0F57C9           XORPS XMM1,XMM1
 *  013FFE00   33C0             XOR EAX,EAX
 *  013FFE02   F3:0F114D 0C     MOVSS DWORD PTR SS:[EBP+0xC],XMM1
 *  013FFE07   8945 F8          MOV DWORD PTR SS:[EBP-0x8],EAX
 *  013FFE0A   E9 F2010000      JMP .01400001
 *  013FFE0F   8A46 01          MOV AL,BYTE PTR DS:[ESI+0x1]
 *  013FFE12   46               INC ESI
 *  013FFE13   84C0             TEST AL,AL
 *  013FFE15   0F84 E6010000    JE .01400001
 *  013FFE1B   EB 03            JMP SHORT .013FFE20
 *  013FFE1D   8D49 00          LEA ECX,DWORD PTR DS:[ECX]
 *  013FFE20   3C 5D            CMP AL,0x5D
 *  013FFE22   0F84 D9010000    JE .01400001
 *  013FFE28   0FBEC0           MOVSX EAX,AL
 *  013FFE2B   50               PUSH EAX
 *  013FFE2C   E8 5D210F00      CALL .014F1F8E
 *  013FFE31   83C4 04          ADD ESP,0x4
 *  013FFE34   85C0             TEST EAX,EAX
 *  013FFE36   75 14            JNZ SHORT .013FFE4C
 *  013FFE38   0FBE06           MOVSX EAX,BYTE PTR DS:[ESI]
 *  013FFE3B   50               PUSH EAX
 *  013FFE3C   E8 20210F00      CALL .014F1F61
 *  013FFE41   83C4 04          ADD ESP,0x4
 *  013FFE44   85C0             TEST EAX,EAX
 *  013FFE46   0F84 B5010000    JE .01400001
 *  013FFE4C   8A46 01          MOV AL,BYTE PTR DS:[ESI+0x1]
 *  013FFE4F   46               INC ESI
 *  013FFE50   84C0             TEST AL,AL
 *  013FFE52  ^75 CC            JNZ SHORT .013FFE20
 *  013FFE54   E9 A8010000      JMP .01400001
 *  013FFE59   8A46 01          MOV AL,BYTE PTR DS:[ESI+0x1]
 *  013FFE5C   46               INC ESI
 *  013FFE5D   84C0             TEST AL,AL
 *  013FFE5F   74 31            JE SHORT .013FFE92
 *  013FFE61   3C 7D            CMP AL,0x7D
 *  013FFE63   74 28            JE SHORT .013FFE8D
 *  013FFE65   0FBEC0           MOVSX EAX,AL
 *  013FFE68   50               PUSH EAX
 *  013FFE69   E8 20210F00      CALL .014F1F8E
 *  013FFE6E   83C4 04          ADD ESP,0x4
 *  013FFE71   85C0             TEST EAX,EAX
 *  013FFE73   75 10            JNZ SHORT .013FFE85
 *  013FFE75   0FBE06           MOVSX EAX,BYTE PTR DS:[ESI]
 *  013FFE78   50               PUSH EAX
 *  013FFE79   E8 E3200F00      CALL .014F1F61
 *  013FFE7E   83C4 04          ADD ESP,0x4
 *  013FFE81   85C0             TEST EAX,EAX
 *  013FFE83   74 08            JE SHORT .013FFE8D
 *  013FFE85   8A46 01          MOV AL,BYTE PTR DS:[ESI+0x1]
 *  013FFE88   46               INC ESI
 *  013FFE89   84C0             TEST AL,AL
 *  013FFE8B  ^75 D4            JNZ SHORT .013FFE61
 *  013FFE8D   F3:0F104D 0C     MOVSS XMM1,DWORD PTR SS:[EBP+0xC]
 *  013FFE92   F745 14 00000100 TEST DWORD PTR SS:[EBP+0x14],0x10000
 *  013FFE99   0F84 62010000    JE .01400001
 *  013FFE9F   8B45 18          MOV EAX,DWORD PTR SS:[EBP+0x18]
 *  013FFEA2   B9 58615C01      MOV ECX,.015C6158
 *  013FFEA7   8B00             MOV EAX,DWORD PTR DS:[EAX]
 *  013FFEA9   85C0             TEST EAX,EAX
 *  013FFEAB   0F45C8           CMOVNE ECX,EAX
 *  013FFEAE   8339 00          CMP DWORD PTR DS:[ECX],0x0
 *  013FFEB1   0F84 4A010000    JE .01400001
 *  013FFEB7   66:0F6E47 64     MOVD MM0,DWORD PTR DS:[EDI+0x64]
 *  013FFEBC   0F5B             ???                                      ; Unknown command
 *  013FFEBE   C0F3 0F          SAL BL,0xF
 *  013FFEC1   58               POP EAX
 *  013FFEC2   C8 F30F11        ENTER 0xFF3,0x11
 *  013FFEC6   4D               DEC EBP
 *  013FFEC7   0C E9            OR AL,0xE9
 *  013FFEC9   34 01            XOR AL,0x1
 *  013FFECB   0000             ADD BYTE PTR DS:[EAX],AL
 *  013FFECD   80F9 5C          CMP CL,0x5C
 *  013FFED0   75 01            JNZ SHORT .013FFED3
 *  013FFED2   46               INC ESI
 *  013FFED3   F647 48 02       TEST BYTE PTR DS:[EDI+0x48],0x2
 *  013FFED7   C745 FC 00000000 MOV DWORD PTR SS:[EBP-0x4],0x0
 *  013FFEDE   0F84 9B000000    JE .013FFF7F
 *  013FFEE4   833F 00          CMP DWORD PTR DS:[EDI],0x0
 *  013FFEE7   74 39            JE SHORT .013FFF22
 *  013FFEE9   56               PUSH ESI
 *  013FFEEA   FFD2             CALL EDX
 *  013FFEEC   2BC6             SUB EAX,ESI
 *  013FFEEE   83F8 01          CMP EAX,0x1
 *  013FFEF1   75 2F            JNZ SHORT .013FFF22
 *  013FFEF3   0FBE0E           MOVSX ECX,BYTE PTR DS:[ESI]
 *  013FFEF6   83E9 20          SUB ECX,0x20
 *  013FFEF9   C1E1 04          SHL ECX,0x4
 *  013FFEFC   034F 60          ADD ECX,DWORD PTR DS:[EDI+0x60]
 *  013FFEFF   8B41 08          MOV EAX,DWORD PTR DS:[ECX+0x8]
 *  013FFF02   2B01             SUB EAX,DWORD PTR DS:[ECX]
 *  013FFF04   83E8 02          SUB EAX,0x2
 *  013FFF07   66:0F6EC0        MOVD MM0,EAX
 *  013FFF0B   0F5B             ???                                      ; Unknown command
 *  013FFF0D   D0B8 02000000    SAR BYTE PTR DS:[EAX+0x2],1
 *  013FFF13   F3:0F5855 0C     ADDSS XMM2,DWORD PTR SS:[EBP+0xC]
 *  013FFF18   F3:0F1155 0C     MOVSS DWORD PTR SS:[EBP+0xC],XMM2
 *  013FFF1D   E9 A5000000      JMP .013FFFC7
 *  013FFF22   8B57 6C          MOV EDX,DWORD PTR DS:[EDI+0x6C]
 *  013FFF25   0FB71E           MOVZX EBX,WORD PTR DS:[ESI]
 *  013FFF28   33C0             XOR EAX,EAX
 *  013FFF2A   85D2             TEST EDX,EDX
 *  013FFF2C   74 21            JE SHORT .013FFF4F
 *  013FFF2E   8B4D F4          MOV ECX,DWORD PTR SS:[EBP-0xC]
 *  013FFF31   8BFB             MOV EDI,EBX
 *  013FFF33   8B49 70          MOV ECX,DWORD PTR DS:[ECX+0x70]
 *  013FFF36   83C1 04          ADD ECX,0x4
 *  013FFF39   8DA424 00000000  LEA ESP,DWORD PTR SS:[ESP]
 *  013FFF40   3939             CMP DWORD PTR DS:[ECX],EDI
 *  013FFF42   74 08            JE SHORT .013FFF4C
 *  013FFF44   40               INC EAX
 *  013FFF45   83C1 1C          ADD ECX,0x1C
 *  013FFF48   3BC2             CMP EAX,EDX
 *  013FFF4A  ^72 F4            JB SHORT .013FFF40
 *  013FFF4C   8B7D F4          MOV EDI,DWORD PTR SS:[EBP-0xC]
 *  013FFF4F   3BC2             CMP EAX,EDX
 *  013FFF51   75 08            JNZ SHORT .013FFF5B
 *  013FFF53   53               PUSH EBX
 *  013FFF54   8BCF             MOV ECX,EDI
 *  013FFF56   E8 C5EDFFFF      CALL .013FED20
 *  013FFF5B   8B5D 08          MOV EBX,DWORD PTR SS:[EBP+0x8]
 *  013FFF5E   8D0CC5 00000000  LEA ECX,DWORD PTR DS:[EAX*8]
 *  013FFF65   2BC8             SUB ECX,EAX
 *  013FFF67   8B47 70          MOV EAX,DWORD PTR DS:[EDI+0x70]
 *  013FFF6A   F3:0F104488 18   MOVSS XMM0,DWORD PTR DS:[EAX+ECX*4+0x18]
 *  013FFF70   F3:0F5845 0C     ADDSS XMM0,DWORD PTR SS:[EBP+0xC]
 *  013FFF75   0F28D0           MOVAPS XMM2,XMM0
 *  013FFF78   F3:0F1155 0C     MOVSS DWORD PTR SS:[EBP+0xC],XMM2
 *  013FFF7D   EB 45            JMP SHORT .013FFFC4
 *  013FFF7F   56               PUSH ESI
 *  013FFF80   FFD2             CALL EDX
 *  013FFF82   2BC6             SUB EAX,ESI
 *  013FFF84   83F8 01          CMP EAX,0x1
 *  013FFF87   75 26            JNZ SHORT .013FFFAF
 *  013FFF89   807F 1F 80       CMP BYTE PTR DS:[EDI+0x1F],0x80
 *  013FFF8D  ^0F85 60FFFFFF    JNZ .013FFEF3
 *  013FFF93   66:0F6E47 64     MOVD MM0,DWORD PTR DS:[EDI+0x64]
 *  013FFF98   0F5B             ???                                      ; Unknown command
 *  013FFF9A   D0F3             SAL BL,1
 *  013FFF9C   0F5915 CCC35801  MULPS XMM2,DQWORD PTR DS:[0x158C3CC]
 *  013FFFA3   F3:0F5855 0C     ADDSS XMM2,DWORD PTR SS:[EBP+0xC]
 *  013FFFA8   F3:0F1155 0C     MOVSS DWORD PTR SS:[EBP+0xC],XMM2
 *  013FFFAD   EB 15            JMP SHORT .013FFFC4
 *  013FFFAF   66:0F6E47 64     MOVD MM0,DWORD PTR DS:[EDI+0x64]
 *  013FFFB4   0F5B             ???                                      ; Unknown command
 *  013FFFB6   C0F3 0F          SAL BL,0xF
 *  013FFFB9   58               POP EAX
 *  013FFFBA   45               INC EBP
 *  013FFFBB   0C 0F            OR AL,0xF
 *  013FFFBD   28D0             SUB AL,DL
 *  013FFFBF   F3:0F1145 0C     MOVSS DWORD PTR SS:[EBP+0xC],XMM0
 *  013FFFC4   8B45 FC          MOV EAX,DWORD PTR SS:[EBP-0x4]
 *  013FFFC7   66:0F6E0B        MOVD MM1,DWORD PTR DS:[EBX]
 *  013FFFCB   66:0F6EC0        MOVD MM0,EAX
 *  013FFFCF   0F5B             ???                                      ; Unknown command
 *  013FFFD1   C00F 5B          ROR BYTE PTR DS:[EDI],0x5B               ; Shift constant out of range 1..31
 *  013FFFD4   C9               LEAVE
 *  013FFFD5   F3:0F58C2        ADDSS XMM0,XMM2
 *  013FFFD9   0F2FC8           COMISS XMM1,XMM0
 *  013FFFDC   77 03            JA SHORT .013FFFE1
 *  013FFFDE   0F28C8           MOVAPS XMM1,XMM0
 *  013FFFE1   8B55 F8          MOV EDX,DWORD PTR SS:[EBP-0x8]
 *  013FFFE4   F3:0F2CC1        CVTTSS2SI EAX,XMM1
 *  013FFFE8   8903             MOV DWORD PTR DS:[EBX],EAX
 *  013FFFEA   8B47 60          MOV EAX,DWORD PTR DS:[EDI+0x60]
 *  013FFFED   8B48 0C          MOV ECX,DWORD PTR DS:[EAX+0xC]
 *  013FFFF0   2B48 04          SUB ECX,DWORD PTR DS:[EAX+0x4]
 *  013FFFF3   3BD1             CMP EDX,ECX
 *  013FFFF5   7D 0A            JGE SHORT .01400001
 *  013FFFF7   8BC1             MOV EAX,ECX
 *  013FFFF9   2BC2             SUB EAX,EDX
 *  013FFFFB   0143 04          ADD DWORD PTR DS:[EBX+0x4],EAX
 *  013FFFFE   894D F8          MOV DWORD PTR SS:[EBP-0x8],ECX
 *  01400001   56               PUSH ESI
 *  01400002   FF15 18A45401    CALL DWORD PTR DS:[0x154A418]            ; user32.CharNextA	; jichi: choice accessed here
 *  01400008   F3:0F104D 0C     MOVSS XMM1,DWORD PTR SS:[EBP+0xC]
 *  0140000D   8B15 18A45401    MOV EDX,DWORD PTR DS:[0x154A418]         ; user32.CharNextA
 *  01400013   8BF0             MOV ESI,EAX
 *  01400015   3B75 10          CMP ESI,DWORD PTR SS:[EBP+0x10]
 *  01400018  ^0F82 B2FDFFFF    JB .013FFDD0
 *  0140001E   5F               POP EDI
 *  0140001F   5E               POP ESI
 */
bool attach(ulong startAddress, ulong stopAddress)
{
  const uint8_t bytes[] = {
                      // 013fffe8   8903             mov dword ptr ds:[ebx],eax
                      // 013fffea   8b47 60          mov eax,dword ptr ds:[edi+0x60]
                      // 013fffed   8b48 0c          mov ecx,dword ptr ds:[eax+0xc]
                      // 013ffff0   2b48 04          sub ecx,dword ptr ds:[eax+0x4]
                      // 013ffff3   3bd1             cmp edx,ecx
    0x7d, 0x0a,       // 013ffff5   7d 0a            jge short .01400001
    0x8b,0xc1,        // 013ffff7   8bc1             mov eax,ecx
    0x2b,0xc2,        // 013ffff9   2bc2             sub eax,edx
    0x01,0x43, 0x04,  // 013ffffb   0143 04          add dword ptr ds:[ebx+0x4],eax
    0x89,0x4d, 0xf8   // 013ffffe   894d f8          mov dword ptr ss:[ebp-0x8],ecx
                      // 01400002   ff15 18a45401    call dword ptr ds:[0x154a418]            ; user32.charnexta	; jichi: choice accessed here
                      // 01400008   f3:0f104d 0c     movss xmm1,dword ptr ss:[ebp+0xc]
                      // 0140000d   8b15 18a45401    mov edx,dword ptr ds:[0x154a418]         ; user32.charnexta
                      // 01400013   8bf0             mov esi,eax
                      // 01400015   3b75 10          cmp esi,dword ptr ss:[ebp+0x10]
  };
  ulong addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  return winhook::hook_before(addr, Private::hookBefore);
}

} // namespace ChoiceHook

#endif // 0
