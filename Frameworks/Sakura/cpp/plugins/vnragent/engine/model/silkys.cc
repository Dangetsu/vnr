// silkys.cc
// 5/17/2015 jichi
// About MES and Silky's arc
// See: http://www.dsl.gr.jp/~sage/mamitool/case/elf/aishimai.html
// MES: http://tieba.baidu.com/p/2068362185
#include "engine/model/silkys.h"
#include "engine/enginecontroller.h"
#include "engine/enginedef.h"
#include "engine/enginehash.h"
#include "engine/util/textunion.h"
#include "hijack/hijackmanager.h"
#include "memdbg/memsearch.h"
#include "winhook/hookcode.h"
#include <qt_windows.h>
#include <cstdint>

#define DEBUG "model/silkys"
#include "sakurakit/skdebug.h"

namespace { // unnamed

namespace ScenarioHook {
namespace Private {

  /**
   *  Sample arg1:
   *  002BF540  00 00 00 00 18 09 75 00 E8 2C 67 77 68 99 73 00  .....u.・gwh冱.
   *  002BF550  01 00 00 00 34 00 00 00 3F 00 00 00 14 01 00 00  ...4...?.....
   *  002BF560  36 00 00 00 0E 00 00 00 20 00 00 00 FF FF FF 00  6...... ....
   *
   *  The first cell shoulda always be zero.
   */

  TextUnionA *arg_,
             argValue_;

  bool hookBefore(ulong retaddr, winhook::hook_stack *s)
  {
    static QByteArray data_;
    auto arg = (TextUnionA *)(s->stack[0] + sizeof(DWORD)); // arg1
    if (!arg || !arg->isValid())
      return true;

    // FIXME: I am not able to distinguish choice out
    auto role =
      s->stack[1] ? Engine::NameRole : // arg2 != 0 for name
      //s->ebx > 0x0fffffff ? Engine::ChoiceRole : // edx is a pointer for choice
      Engine::ScenarioRole;

    auto sig = Engine::hashThreadSignature(role, retaddr);
    QByteArray oldData(arg->getText(), arg->size),
               newData = EngineController::instance()->dispatchTextA(oldData, role, sig);
    if (newData == oldData)
      return true;

    arg_ = arg;
    argValue_ = *arg;
    data_ = newData;
    arg->setText(data_);
    return true;
  }

  bool hookAfter(winhook::hook_stack *)
  {
    if (arg_)  {
      *arg_ = argValue_;
      arg_ = nullptr;
    }
    return true;
  }

} // namespace Private

/** jichi: 6/17/2015
 *  Sample game: 堕ちていく新妻 trial
 *
 *  This function is found by backtracking GetGlyphOutlineA.
 *  There are two GetGlyphOutlineA, which are in the same function.
 *  That function are called by two other functions.
 *  The second function is hooked.
 *
 *  baseaddr = 08e0000
 *
 *  0096652E   CC               INT3
 *  0096652F   CC               INT3
 *  00966530   55               PUSH EBP
 *  00966531   8BEC             MOV EBP,ESP
 *  00966533   83EC 18          SUB ESP,0x18
 *  00966536   A1 00109F00      MOV EAX,DWORD PTR DS:[0x9F1000]
 *  0096653B   33C5             XOR EAX,EBP
 *  0096653D   8945 FC          MOV DWORD PTR SS:[EBP-0x4],EAX
 *  00966540   53               PUSH EBX
 *  00966541   8B5D 0C          MOV EBX,DWORD PTR SS:[EBP+0xC]
 *  00966544   56               PUSH ESI
 *  00966545   8B75 08          MOV ESI,DWORD PTR SS:[EBP+0x8]
 *  00966548   57               PUSH EDI
 *  00966549   6A 00            PUSH 0x0
 *  0096654B   894D EC          MOV DWORD PTR SS:[EBP-0x14],ECX
 *  0096654E   8B0D FCB7A200    MOV ECX,DWORD PTR DS:[0xA2B7FC]
 *  00966554   68 90D29D00      PUSH .009DD290                           ; ASCII "/Config/SceneSkip"
 *  00966559   895D F0          MOV DWORD PTR SS:[EBP-0x10],EBX
 *  0096655C   E8 2F4A0100      CALL .0097AF90
 *  00966561   83F8 01          CMP EAX,0x1
 *  00966564   0F84 E0010000    JE .0096674A
 *  0096656A   8B55 EC          MOV EDX,DWORD PTR SS:[EBP-0x14]
 *  0096656D   85DB             TEST EBX,EBX
 *  0096656F   75 09            JNZ SHORT .0096657A
 *  00966571   8B42 04          MOV EAX,DWORD PTR DS:[EDX+0x4]
 *  00966574   8B40 38          MOV EAX,DWORD PTR DS:[EAX+0x38]
 *  00966577   8945 F0          MOV DWORD PTR SS:[EBP-0x10],EAX
 *  0096657A   33C0             XOR EAX,EAX
 *  0096657C   C645 F8 00       MOV BYTE PTR SS:[EBP-0x8],0x0
 *  00966580   33C9             XOR ECX,ECX
 *  00966582   66:8945 F9       MOV WORD PTR SS:[EBP-0x7],AX
 *  00966586   3946 14          CMP DWORD PTR DS:[ESI+0x14],EAX
 *  00966589   0F86 BB010000    JBE .0096674A
 *
 *  Sample game: 根雪の幻影
 *
 *  Scenario stack:
 *
 *  002FF9DC   00955659  RETURN to .00955659 from .00966530
 *  002FF9E0   002FFA10  ; jichi: text in [arg1+4]
 *  002FF9E4   00000000  ; arg2 is zero
 *  002FF9E8   00000001
 *  002FF9EC   784B8FC7
 *
 *  0015F68C   002FF538  RETURN to .002FF538 from .00310580
 *  0015F690   0015F6C0
 *  0015F694   00000000
 *  0015F698   00528728  ASCII "neyuki05_02.mes"
 *  0015F69C   6431C29A
 *  0015F6A0   00516FA0
 *  0015F6A4   00000040
 *  0015F6A8   0030B2C3  .0030B2C3
 *  0015F6AC   0DD7F3B8
 *  0015F6B0   00000000
 *  0015F6B4   00000001
 *  0015F6B8   0DCD9C98
 *  0015F6BC   00528728  ASCII "neyuki05_02.mes"
 *  0015F6C0   00000000
 *
 *  EAX 0013F9E0
 *  ECX 0013FA30
 *  EDX 00000026
 *  EBX 00008200
 *  ESP 0013F9AC
 *  EBP 0013FA70
 *  ESI 00255DE0
 *  EDI 00268728 ASCII "neyuki05_02.mes"
 *  EIP 00910580 .00910580
 *
 *  002FF52B   50               PUSH EAX
 *  002FF52C   8D8C24 80000000  LEA ECX,DWORD PTR SS:[ESP+0x80]
 *  002FF533   E8 48100100      CALL .00310580
 *  002FF538   E8 336B0100      CALL .00316070
 *  002FF53D   8B40 08          MOV EAX,DWORD PTR DS:[EAX+0x8]
 *  002FF540   85C0             TEST EAX,EAX
 *  002FF542   74 1C            JE SHORT .002FF560
 *  002FF544   8B48 3C          MOV ECX,DWORD PTR DS:[EAX+0x3C]
 *  002FF547   8B40 40          MOV EAX,DWORD PTR DS:[EAX+0x40]
 *  002FF54A   2BC1             SUB EAX,ECX
 *  002FF54C   A9 E0FFFFFF      TEST EAX,0xFFFFFFE0
 *  002FF551   74 0D            JE SHORT .002FF560
 *
 *  Name stack:
 *
 *  002FF59C   00930A76  RETURN to .00930A76 from .00966530
 *  002FF5A0   002FF5D0 ; jichi: text in [arg1+4]
 *  002FF5A4   004DDEC0 ; arg2 is a pointer
 *  002FF5A8   00000001
 *  002FF5AC   784B8387
 *  002FF5B0   00000182
 *  002FF5B4   00000000
 *
 *  EAX 0013F5A0
 *  ECX 0013F5F0
 *  EDX 778570B4 ntdll.KiFastSystemCallRet
 *  EBX 002CA080
 *  ESP 0013F56C
 *  EBP 0013F6C4
 *  ESI 0B237008
 *  EDI 002CA080
 *  EIP 00910580 .00910580
 *
 *  002D8181   8D8C24 80000000  LEA ECX,DWORD PTR SS:[ESP+0x80]
 *  002D8188   C68424 4C010000 >MOV BYTE PTR SS:[ESP+0x14C],0x6
 *  002D8190   E8 EB830300      CALL .00310580
 *  002D8195   8B47 64          MOV EAX,DWORD PTR DS:[EDI+0x64]
 *  002D8198   8B9424 10010000  MOV EDX,DWORD PTR SS:[ESP+0x110]
 *  002D819F   8B48 3C          MOV ECX,DWORD PTR DS:[EAX+0x3C]
 *  002D81A2   8B82 C0050000    MOV EAX,DWORD PTR DS:[EDX+0x5C0]
 *  002D81A8   8981 C0050000    MOV DWORD PTR DS:[ECX+0x5C0],EAX
 *  002D81AE   8B82 C4050000    MOV EAX,DWORD PTR DS:[EDX+0x5C4]
 *  002D81B4   81C2 C8050000    ADD EDX,0x5C8
 *  002D81BA   8981 C4050000    MOV DWORD PTR DS:[ECX+0x5C4],EAX
 *  002D81C0   81C1 C8050000    ADD ECX,0x5C8
 *  002D81C6   3BCA             CMP ECX,EDX
 * *
 *  Scenario and Name are called by different callers.
 *
 *  Choice stack:
 *  0015F1FC   002FF538  RETURN to .002FF538 from .00310580
 *  0015F200   0015F230
 *  0015F204   00000000 ; jichi: the same as scenario that is zero
 *  0015F208   00528728  ASCII "neyuki05_02.mes"
 *  0015F20C   6431C62A
 *  0015F210   00516FA0
 *  0015F214   00000006
 *  0015F218   77862FE7  RETURN to ntdll.77862FE7 from ntdll.77862C51
 *  0015F21C   0015F1B0
 *  0015F220   00000000
 *  0015F224   00000001
 *  0015F228   0015F2E4
 *  0015F22C   00528728  ASCII "neyuki05_02.mes"
 *  0015F230   00000000
 *  0015F234   43989795
 *  0015F238   7700EA8F  shell32.7700EA8F
 *
 *  EAX 0013F550
 *  ECX 0013F5A0
 *  EDX 00000006
 *  EBX 7632BA00 kernel32.7632BA00
 *  ESP 0013F51C
 *  EBP 0013F5E0
 *  ESI 00255DE0
 *  EDI 00268728 ASCII "neyuki05_02.mes"
 *  EIP 00910580 .00910580
 *
 *  EAX 0013F330
 *  ECX 0013F380
 *  EDX 00000014
 *  EBX 00008200
 *  ESP 0013F2FC
 *  EBP 0013F3C0
 *  ESI 00305DE0
 *  EDI 00318728 ASCII "neyuki06_04.mes"
 *  EIP 011F0580 .011F0580
 */
bool attach(ulong startAddress, ulong stopAddress)
{
  const uint8_t bytes[] = {
    0x66,0x89,0x45, 0xf9,   // 00a1a062   66:8945 f9       mov word ptr ss:[ebp-0x7],ax
    0x39,0x47, 0x14         // 00a1a066   3947 14          cmp dword ptr ds:[edi+0x14],eax
  };
  ulong addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  if (!addr)
    return false;

  //const char *msg = "\0/Config/SceneSkip";
  //ulong addr = MemDbg::findBytes(msg, ::strlen(msg + 1) + 2, startAddress, stopAddress); // +1 to include \0 at the end
  //if (!addr)
  //  return false;
  //addr += 1; // skip leading "\0"
  //addr = MemDbg::findPushAddress(addr, startAddress, stopAddress);
  //if (!addr)
  //  return false;

  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;

  //ulong addr = MemDbg::findCallerAddressAfterInt3((ulong)::GetGlyphOutlineA, startAddress, stopAddress);
  //if (!addr)
  //  return false;
  //addr = MemDbg::findLastNearCallAddress(addr, startAddress, stopAddress);
  //if (!addr)
  //  return false;

  //DOUT(addr);

  int count = 0;
  auto fun = [&count](ulong addr) -> bool {
    auto before = std::bind(Private::hookBefore, addr + 5, std::placeholders::_1);
    count += winhook::hook_both(addr, before, Private::hookAfter);
    return true; // replace all functions
  };
  MemDbg::iterNearCallAddress(fun, addr, startAddress, stopAddress);
  DOUT("call number =" << count);
  return count;
}

} // namespace ScenarioHook
} // unnamed namespace

bool SilkysEngine::attach()
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
