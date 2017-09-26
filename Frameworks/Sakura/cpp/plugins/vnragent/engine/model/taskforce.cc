// taskforce.cc
// 8/4/2015 jichi
#include "engine/model/taskforce.h"
#include "engine/enginecontroller.h"
#include "engine/enginedef.h"
#include "engine/enginehash.h"
#include "engine/engineutil.h"
#include "hijack/hijackmanager.h"
#include "winhook/hookcode.h"
#include "memdbg/memsearch.h"
#include <qt_windows.h>
#include <QtCore/QRegExp>
#include <cstdint>

#define DEBUG "model/taskforce"
#include "sakurakit/skdebug.h"

namespace { // unnamed
namespace ScenarioHook {
namespace Private {
  bool hookBefore(winhook::hook_stack *s)
  {
    static QByteArray data_;
    int capacity = s->stack[1]; // arg 2, should always be 0x1000
    auto text = (LPCSTR)s->stack[2]; // arg 3
    if (capacity <= 0 || !text || !*text)
      return true;
    auto role = s->stack[2] == s->stack[12] ? Engine::ScenarioRole : Engine::OtherRole;
    //auto split = s->edx;
    //auto sig = Engine::hashThreadSignature(role, split);
    enum { sig = 0 }; // split not used
    data_ = EngineController::instance()->dispatchTextA(text, role, sig);
    if (data_.size() >= capacity)
      data_ = data_.left(capacity - 1);
    s->stack[2] = (ulong)data_.constData(); // arg 3
    return true;
  }
} // namespace Private

/**
 *  Sample game: オトメスイッチ
 *
 *  Debugging method: hook to the ITH function, and then check stack
 *  strncpy is not hooked as it is also used to copy system text
 *
 *  0012D0D0   1A72224C
 *  0012D0D4   1A721FA4
 *  0012D0D8   00000000
 *  0012D0DC   0044A61A  RETURN to .0044A61A from .0058F477
 *  0012D0E0   1A72224C ; jichi: target text
 *  0012D0E4   00001000 ; jichi: this value is different for different callers
 *  0012D0E8   0D4CFA70	; jichi: source text here
 *  0012D0EC   00A53E0E  .00A53E0E
 *  0012D0F0   1A721F80
 *  0012D0F4   1AD70020
 *  0012D0F8   00000000
 *  0012D0FC   0012D138  Pointer to next SEH record
 *  0012D100   0069D878  SE handler
 *  0012D104   00000000
 *  0012D108   00451436  RETURN to .00451436 from .0044A5B0
 *  0012D10C   0D4CFAE8
 *  0012D110   0D4CFA70
 *  0012D114   0D4CF908
 *  0012D118   00000016
 *  0012D11C   00FFFFFF  .00FFFFFF
 *  0012D120   00000016
 *  0012D124   0000001F
 *  0012D128   00A53FD2  .00A53FD2
 *  0012D12C   006E3BC8  .006E3BC8
 *  0012D130   00000000
 *  0012D134   0012D10C
 *  0012D138   0012D8AC  Pointer to next SEH record
 *  0012D13C   0069D878  SE handler
 *  0012D140   00000000
 *  0012D144   004617DD  RETURN to .004617DD from .004513D0
 *  0012D148   00000000
 *  0012D14C   0D4CFAE8
 *  0012D150   00000000
 *  0012D154   00000000
 *  0012D158   006E3BC8  .006E3BC8
 *  0012D15C   00000016
 *  0012D160   0000001F
 *
 *  Caller of the strncpy function
 *  0044A5AF   CC               INT3
 *  0044A5B0   6A FF            PUSH -0x1
 *  0044A5B2   68 78D86900      PUSH .0069D878
 *  0044A5B7   64:A1 00000000   MOV EAX,DWORD PTR FS:[0]
 *  0044A5BD   50               PUSH EAX
 *  0044A5BE   53               PUSH EBX
 *  0044A5BF   55               PUSH EBP
 *  0044A5C0   57               PUSH EDI
 *  0044A5C1   A1 4C3F7F00      MOV EAX,DWORD PTR DS:[0x7F3F4C]
 *  0044A5C6   33C4             XOR EAX,ESP
 *  0044A5C8   50               PUSH EAX
 *  0044A5C9   8D4424 10        LEA EAX,DWORD PTR SS:[ESP+0x10]
 *  0044A5CD   64:A3 00000000   MOV DWORD PTR FS:[0],EAX
 *  0044A5D3   33DB             XOR EBX,EBX
 *  0044A5D5   895C24 18        MOV DWORD PTR SS:[ESP+0x18],EBX
 *  0044A5D9   8D7E 5C          LEA EDI,DWORD PTR DS:[ESI+0x5C]
 *  0044A5DC   8D6B 14          LEA EBP,DWORD PTR DS:[EBX+0x14]
 *  0044A5DF   90               NOP
 *  0044A5E0   53               PUSH EBX
 *  0044A5E1   68 C83B6E00      PUSH .006E3BC8
 *  0044A5E6   8BCF             MOV ECX,EDI
 *  0044A5E8   E8 A376FBFF      CALL .00401C90
 *  0044A5ED   83C7 1C          ADD EDI,0x1C
 *  0044A5F0   83ED 01          SUB EBP,0x1
 *  0044A5F3  ^75 EB            JNZ SHORT .0044A5E0
 *  0044A5F5   8B4424 24        MOV EAX,DWORD PTR SS:[ESP+0x24]
 *  0044A5F9   BD 10000000      MOV EBP,0x10
 *  0044A5FE   396C24 38        CMP DWORD PTR SS:[ESP+0x38],EBP
 *  0044A602   73 04            JNB SHORT .0044A608
 *  0044A604   8D4424 24        LEA EAX,DWORD PTR SS:[ESP+0x24]
 *  0044A608   50               PUSH EAX
 *
 *  0044A609   8DBE A8020000    LEA EDI,DWORD PTR DS:[ESI+0x2A8]
 *  0044A60F   68 00100000      PUSH 0x1000
 *  0044A614   57               PUSH EDI
 *
 *  0044A615   E8 5D4E1400      CALL .0058F477  ; jichi: called here
 *  0044A61A   8BC7             MOV EAX,EDI
 *  0044A61C   83C4 0C          ADD ESP,0xC
 *  0044A61F   895E 58          MOV DWORD PTR DS:[ESI+0x58],EBX
 *  0044A622   899E A8120000    MOV DWORD PTR DS:[ESI+0x12A8],EBX
 *  0044A628   899E AC120000    MOV DWORD PTR DS:[ESI+0x12AC],EBX
 *  0044A62E   8D50 01          LEA EDX,DWORD PTR DS:[EAX+0x1]
 *  0044A631   8A08             MOV CL,BYTE PTR DS:[EAX]
 *  0044A633   83C0 01          ADD EAX,0x1
 *  0044A636   3ACB             CMP CL,BL
 *  0044A638  ^75 F7            JNZ SHORT .0044A631
 *  0044A63A   2BC2             SUB EAX,EDX
 *  0044A63C   6A FF            PUSH -0x1
 *  0044A63E   8986 B0120000    MOV DWORD PTR DS:[ESI+0x12B0],EAX
 *  0044A644   53               PUSH EBX
 *  0044A645   8D4424 28        LEA EAX,DWORD PTR SS:[ESP+0x28]
 *  0044A649   50               PUSH EAX
 *  0044A64A   8D8E 8C020000    LEA ECX,DWORD PTR DS:[ESI+0x28C]
 *  0044A650   899E B8120000    MOV DWORD PTR DS:[ESI+0x12B8],EBX
 *  0044A656   E8 0575FBFF      CALL .00401B60
 *  0044A65B   396C24 38        CMP DWORD PTR SS:[ESP+0x38],EBP
 *  0044A65F   899E C8120000    MOV DWORD PTR DS:[ESI+0x12C8],EBX
 *  0044A665   72 0D            JB SHORT .0044A674
 *  0044A667   8B4C24 24        MOV ECX,DWORD PTR SS:[ESP+0x24]
 *  0044A66B   51               PUSH ECX
 *  0044A66C   E8 C14A1400      CALL .0058F132
 *  0044A671   83C4 04          ADD ESP,0x4
 *  0044A674   8B4C24 10        MOV ECX,DWORD PTR SS:[ESP+0x10]
 *  0044A678   64:890D 00000000 MOV DWORD PTR FS:[0],ECX
 *  0044A67F   59               POP ECX
 *  0044A680   5F               POP EDI
 *  0044A681   5D               POP EBP
 *  0044A682   5B               POP EBX
 *  0044A683   83C4 0C          ADD ESP,0xC
 *  0044A686   C2 1C00          RETN 0x1C
 *  0044A689   CC               INT3
 *
 *  This is properly the strncpy function. Capacity in arg2. Target in arg1. Source in arg3.
 *  0058F476   CC               INT3
 *  0058F477   8B4C24 04        MOV ECX,DWORD PTR SS:[ESP+0x4]
 *  0058F47B   53               PUSH EBX
 *  0058F47C   33DB             XOR EBX,EBX
 *  0058F47E   3BCB             CMP ECX,EBX
 *  0058F480   56               PUSH ESI
 *  0058F481   57               PUSH EDI
 *  0058F482   74 08            JE SHORT .0058F48C
 *  0058F484   8B7C24 14        MOV EDI,DWORD PTR SS:[ESP+0x14]
 *  0058F488   3BFB             CMP EDI,EBX
 *  0058F48A   77 1B            JA SHORT .0058F4A7
 *  0058F48C   E8 D8390000      CALL .00592E69
 *  0058F491   6A 16            PUSH 0x16
 *  0058F493   5E               POP ESI
 *  0058F494   8930             MOV DWORD PTR DS:[EAX],ESI
 *  0058F496   53               PUSH EBX
 *  0058F497   53               PUSH EBX
 *  0058F498   53               PUSH EBX
 *  0058F499   53               PUSH EBX
 *  0058F49A   53               PUSH EBX
 *  0058F49B   E8 D9010000      CALL .0058F679
 *  0058F4A0   83C4 14          ADD ESP,0x14
 *  0058F4A3   8BC6             MOV EAX,ESI
 *  0058F4A5   EB 31            JMP SHORT .0058F4D8
 *  0058F4A7   8B7424 18        MOV ESI,DWORD PTR SS:[ESP+0x18]
 *  0058F4AB   3BF3             CMP ESI,EBX
 *  0058F4AD   75 04            JNZ SHORT .0058F4B3
 *  0058F4AF   8819             MOV BYTE PTR DS:[ECX],BL
 *  0058F4B1  ^EB D9            JMP SHORT .0058F48C
 *  0058F4B3   8BD1             MOV EDX,ECX
 *
 *  Sample game: 神様（仮）-カミサマカッコカリ-路地裏繚乱編
 */

bool attach(ulong startAddress, ulong stopAddress)
{
  const uint8_t bytes[] = {
    0x8d,0xbe, 0xa8,0x02,0x00,0x00, // 0044a609   8dbe a8020000    lea edi,dword ptr ds:[esi+0x2a8]
    0x68, 0x00,0x10,0x00,0x00,      // 0044a60f   68 00100000      push 0x1000
    0x57,                           // 0044a614   57               push edi
    0xe8                            // 0044a615   e8 5d4e1400      call .0058f477  ; jichi: called here
  };
  enum { addr_offset = sizeof(bytes) - 1 };
  ulong addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  return addr && winhook::hook_before(addr + addr_offset, Private::hookBefore);
}

} // namespace ScenarioHook
} // unnamed namespace

bool TaskforceEngine::attach()
{
  ulong startAddress, stopAddress;
  if (!Engine::getProcessMemoryRange(&startAddress, &stopAddress))
    return false;
  if (!ScenarioHook::attach(startAddress, stopAddress))
    return false;
  HijackManager::instance()->attachFunction((ulong)::GetGlyphOutlineA);
  return true;
}

// EOF
