// gxp.cc
// 8/15/2015 jichi
#include "engine/model/gxp.h"
#include "engine/enginecontroller.h"
#include "engine/enginedef.h"
#include "engine/util/textunion.h"
//#include "hijack/hijackmanager.h"
#include "memdbg/memsearch.h"
#include "winhook/hookcode.h"
#include <qt_windows.h>
#include <QtCore/QRegExp>
#include <cstdint>

#define DEBUG "model/gxp"
#include "sakurakit/skdebug.h"

/** Private data */

namespace { // unnamed

ulong moduleBaseAddress_; // saved only for debugging purposes

bool isBadText(LPCWSTR text)
{
  return text[0] <= 127 || text[::wcslen(text) - 1] <= 127 // skip ascii text
      || ::wcschr(text, 0xff3f); // Skip system text containing: ＿
}

namespace ScenarioHook1 { // for old GXP1
namespace Private {
  TextUnionW *arg_,
             argValue_;
  bool hookBefore(ulong retaddr, winhook::hook_stack *s)
  {
    static QString text_; // persistent storage, which makes this function not thread-safe
    auto reladdr = retaddr - moduleBaseAddress_;
    auto role = Engine::OtherRole;
    // reladdr: 0xa28f1
    // 012328E5   50               PUSH EAX
    // 012328E6   8D8E E8010000    LEA ECX,DWORD PTR DS:[ESI+0x1E8]
    // 012328EC  -E9 0FD7260E      JMP 0F4A0000
    // 012328F1   8A4C24 0C        MOV CL,BYTE PTR SS:[ESP+0xC]
    // 012328F5   8A4424 18        MOV AL,BYTE PTR SS:[ESP+0x18]
    if (*(DWORD *)retaddr == 0x0c244c8a)
      role = Engine::ScenarioRole;
    // reladdr: 0x1763f
    // 011A7635   66:894424 20     MOV WORD PTR SS:[ESP+0x20],AX
    // 011A763A  -E9 C189E905      JMP 07040000
    // 011A763F   8B5424 44        MOV EDX,DWORD PTR SS:[ESP+0x44]
    // 011A7643   6A FF            PUSH -0x1
    // 011A7645   57               PUSH EDI
    //
    // reladdr: 0x66a0
    // 01196697   66:8946 04       MOV WORD PTR DS:[ESI+0x4],AX
    // 0119669B  -E9 60990501      JMP 021F0000
    // 011966A0   4F               DEC EDI
    // 011966A1   83C6 1C          ADD ESI,0x1C
    // 011966A4   885D FC          MOV BYTE PTR SS:[EBP-0x4],BL
    // 011966A7   8975 08          MOV DWORD PTR SS:[EBP+0x8],ESI
    else if (*(BYTE *)retaddr == 0x4f ||
        (*(DWORD *)retaddr & 0x00ff00ff) == 0x0024008b) // skip truncated texts
      return true;

    auto arg = (TextUnionW *)(s->stack[0] + 4); // arg1 + 0x4
    if (!arg->isValid())
      return true;

    auto text = arg->getText();
    if (isBadText(text))
      return true;
    QString oldText = QString::fromWCharArray(text),
            newText = EngineController::instance()->dispatchTextW(oldText, role, reladdr);
    if (newText == oldText)
      return true;
    text_ = newText;

    arg_ = arg;
    argValue_ = *arg;

    arg->setText(text_);

    //if (arg->size)
    //  hashes_.insert(Engine::hashWCharArray(arg->text, arg->size));
    return true;
  }
  bool hookAfter(winhook::hook_stack *)
  {
    if (arg_) {
      *arg_ = argValue_;
      arg_ = nullptr;
    }
    return 0;
  }
} // namespace Private

/**
 *  Sample game: 塔の下のエクセルキトゥス体験版
 *  Executable description shows "AVGEngineV2"
 *
 *  Debugging method: Find the fixed text address, and check when it is being modified
 *
 *  Scenario caller, text in the struct of arg1 + 0x4.
 */
bool attach(ulong startAddress, ulong stopAddress)
{
  const uint8_t bytes[] = {
    0xeb, 0x02,           // 01313bb6   eb 02            jmp short trial.01313bba
    0x8b,0xc5,            // 01313bb8   8bc5             mov eax,ebp
    0x8b,0x54,0x24, 0x18, // 01313bba   8b5424 18        mov edx,dword ptr ss:[esp+0x18]
    0x8d,0x0c,0x51,       // 01313bbe   8d0c51           lea ecx,dword ptr ds:[ecx+edx*2]
    0x8d,0x1c,0x3f        // 01313bc1   8d1c3f           lea ebx,dword ptr ds:[edi+edi]
  };
  ulong addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  if (!addr)
    return addr;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return addr;
  //return winhook::hook_before(addr, Private::hookBefore);

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
} // namespace ScenarioHook1

namespace ScenarioHook2 { // for new GXP2
namespace Private {
  /**
   *  Sample system text:
   *  cg/bg/ショップ前＿昼.png
   *
   *  Scenario caller:
   *  00187E65  |. 8B06           MOV EAX,DWORD PTR DS:[ESI]
   *  00187E67  |. FF90 A8020000  CALL DWORD PTR DS:[EAX+0x2A8]
   *  00187E6D  |. 8B45 08        MOV EAX,DWORD PTR SS:[EBP+0x8]
   *  00187E70  |. 8D8E A8010000  LEA ECX,DWORD PTR DS:[ESI+0x1A8]
   *  00187E76  |. 3BC8           CMP ECX,EAX
   *  00187E78  |. 74 0A          JE SHORT play.00187E84
   *  00187E7A  |. 6A FF          PUSH -0x1
   *  00187E7C  |. 6A 00          PUSH 0x0
   *  00187E7E  |. 50             PUSH EAX
   *  00187E7F  |. E8 CCDAFBFF    CALL play.00145950
   *  00187E84  |> 8A45 0C        MOV AL,BYTE PTR SS:[EBP+0xC]
   *  00187E87  |. 8B0D 882C4F00  MOV ECX,DWORD PTR DS:[0x4F2C88]
   *  00187E8D  |. 8886 03030000  MOV BYTE PTR DS:[ESI+0x303],AL
   *  00187E93  |. 8A45 10        MOV AL,BYTE PTR SS:[EBP+0x10]
   *  00187E96  |. 8886 05030000  MOV BYTE PTR DS:[ESI+0x305],AL
   *
   *  The history thread that is needed to be skipped to avoid retranslation
   *  0095391A   74 0A            JE SHORT 塔の下の.00953926
   *  0095391C   6A FF            PUSH -0x1
   *  0095391E   6A 00            PUSH 0x0
   *  00953920   50               PUSH EAX
   *  00953921   call
   *  00953926   A1 882CCB00      MOV EAX,DWORD PTR DS:[0xCB2C88]   ; jichi: retaddr
   *  0095392B   A8 01            TEST AL,0x1
   *  0095392D   75 28            JNZ SHORT 塔の下の.00953957
   */
  TextUnionW *arg_,
             argValue_;
  bool hookBefore(ulong retaddr, winhook::hook_stack *s)
  {
    static QString text_; // persistent storage, which makes this function not thread-safe
    auto arg = (TextUnionW *)s->stack[0]; // arg1
    if (!arg->isValid())
      return true;

    auto reladdr = retaddr - moduleBaseAddress_;
    // 00187E7F  |. E8 CCDAFBFF    CALL play.00145950
    // 00187E84  |> 8A45 0C        MOV AL,BYTE PTR SS:[EBP+0xC]
    auto role = Engine::OtherRole;
    if (*(WORD *)retaddr == 0x458a)
      role = Engine::ScenarioRole;
    // 00953926   A1 882CCB00      MOV EAX,DWORD PTR DS:[0xCB2C88]   ; jichi: retaddr
    else if (*(BYTE *)retaddr == 0xa1)
      return true;
    auto text = arg->getText();
    if (isBadText(text))
      return true;
    QString oldText = QString::fromWCharArray(text),
            newText = EngineController::instance()->dispatchTextW(oldText, role, reladdr);
    if (newText == oldText)
      return true;

    arg_ = arg;
    argValue_ = *arg;

    text_ = newText;
    arg->setText(text_);

    //if (arg->size)
    //  hashes_.insert(Engine::hashWCharArray(arg->text, arg->size));
    return true;
  }
  bool hookAfter(winhook::hook_stack *)
  {
    if (arg_) {
      *arg_ = argValue_;
      arg_ = nullptr;
    }
    return 0;
  }
} // namespace Private

/**
 *  Sample game: 塔の下のエクセルキトゥス体験版
 *  Executable description shows "AVGEngineV2"
 *
 *  Debugging method: Find the fixed text address, and check when it is being modified
 *
 *  Scenario caller, text in the struct of arg1.
 *
 *  0081594C  |. CC             INT3
 *  0081594D  |. CC             INT3
 *  0081594E  |. CC             INT3
 *  0081594F  |. CC             INT3
 *  00815950  |$ 55             PUSH EBP
 *  00815951  |. 8BEC           MOV EBP,ESP
 *  00815953  |. 53             PUSH EBX
 *  00815954  |. 8B5D 08        MOV EBX,DWORD PTR SS:[EBP+0x8]
 *  00815957  |. 56             PUSH ESI
 *  00815958  |. 57             PUSH EDI
 *  00815959  |. 8BF1           MOV ESI,ECX
 *  0081595B  |. 8B4D 0C        MOV ECX,DWORD PTR SS:[EBP+0xC]
 *  0081595E  |. 8B7B 10        MOV EDI,DWORD PTR DS:[EBX+0x10]
 *  00815961  |. 3BF9           CMP EDI,ECX
 *  00815963  |. 0F82 D0000000  JB play.00815A39
 *  00815969  |. 2BF9           SUB EDI,ECX
 *  0081596B  |. 397D 10        CMP DWORD PTR SS:[EBP+0x10],EDI
 *  0081596E  |. 0F427D 10      CMOVB EDI,DWORD PTR SS:[EBP+0x10]
 *  00815972  |. 3BF3           CMP ESI,EBX
 *  00815974  |. 75 20          JNZ SHORT play.00815996	; jichi: jump
 *  00815976  |. 8D040F         LEA EAX,DWORD PTR DS:[EDI+ECX]
 *  00815979  |. 8BCE           MOV ECX,ESI
 *  0081597B  |. 50             PUSH EAX
 *  0081597C  |. E8 DFFEFFFF    CALL play.00815860
 *  00815981  |. FF75 0C        PUSH DWORD PTR SS:[EBP+0xC]
 *  00815984  |. 8BCE           MOV ECX,ESI
 *  00815986  |. 6A 00          PUSH 0x0
 *  00815988  |. E8 13FFFFFF    CALL play.008158A0
 *  0081598D  |. 5F             POP EDI
 *  0081598E  |. 8BC6           MOV EAX,ESI
 *  00815990  |. 5E             POP ESI
 *  00815991  |. 5B             POP EBX
 *  00815992  |. 5D             POP EBP
 *  00815993  |. C2 0C00        RETN 0xC
 *  00815996  |> 81FF FEFFFF7F  CMP EDI,0x7FFFFFFE
 *  0081599C  |. 0F87 A1000000  JA play.00815A43
 *  008159A2  |. 8B46 14        MOV EAX,DWORD PTR DS:[ESI+0x14]
 *  008159A5  |. 3BC7           CMP EAX,EDI
 *  008159A7  |. 73 24          JNB SHORT play.008159CD
 *  008159A9  |. FF76 10        PUSH DWORD PTR DS:[ESI+0x10]
 *  008159AC  |. 8BCE           MOV ECX,ESI
 *  008159AE  |. 57             PUSH EDI
 *  008159AF  |. E8 DC000000    CALL play.00815A90
 *  008159B4  |. 8B4D 0C        MOV ECX,DWORD PTR SS:[EBP+0xC]
 *  008159B7  |. 85FF           TEST EDI,EDI
 *  008159B9  |. 74 75          JE SHORT play.00815A30
 *  008159BB  |> 837B 14 08     CMP DWORD PTR DS:[EBX+0x14],0x8
 *  008159BF  |. 72 02          JB SHORT play.008159C3
 *  008159C1  |. 8B1B           MOV EBX,DWORD PTR DS:[EBX]
 *  008159C3  |> 837E 14 08     CMP DWORD PTR DS:[ESI+0x14],0x8
 *  008159C7  |. 72 2E          JB SHORT play.008159F7
 *  008159C9  |. 8B16           MOV EDX,DWORD PTR DS:[ESI]
 *  008159CB  |. EB 2C          JMP SHORT play.008159F9	; jichi: jump
 *  008159CD  |> 85FF           TEST EDI,EDI
 *  008159CF  |.^75 EA          JNZ SHORT play.008159BB
 *  008159D1  |. 897E 10        MOV DWORD PTR DS:[ESI+0x10],EDI
 *  008159D4  |. 83F8 08        CMP EAX,0x8
 *  008159D7  |. 72 10          JB SHORT play.008159E9
 *  008159D9  |. 8B06           MOV EAX,DWORD PTR DS:[ESI]
 *  008159DB  |. 33C9           XOR ECX,ECX
 *  008159DD  |. 5F             POP EDI
 *  008159DE  |. 66:8908        MOV WORD PTR DS:[EAX],CX
 *  008159E1  |. 8BC6           MOV EAX,ESI
 *  008159E3  |. 5E             POP ESI
 *  008159E4  |. 5B             POP EBX
 *  008159E5  |. 5D             POP EBP
 *  008159E6  |. C2 0C00        RETN 0xC
 *  008159E9  |> 8BC6           MOV EAX,ESI
 *  008159EB  |. 33C9           XOR ECX,ECX
 *  008159ED  |. 5F             POP EDI
 *  008159EE  |. 5E             POP ESI
 *  008159EF  |. 5B             POP EBX
 *  008159F0  |. 66:8908        MOV WORD PTR DS:[EAX],CX
 *  008159F3  |. 5D             POP EBP
 *  008159F4  |. C2 0C00        RETN 0xC
 *  008159F7  |> 8BD6           MOV EDX,ESI
 *  008159F9  |> 85FF           TEST EDI,EDI
 *  008159FB  |. 74 11          JE SHORT play.00815A0E
 *
 *  008159FD  |. 8D043F         LEA EAX,DWORD PTR DS:[EDI+EDI]	; jichi: edi *= 2 for wchar_t
 *  00815A00  |. 50             PUSH EAX	; jichi: size
 *  00815A01  |. 8D044B         LEA EAX,DWORD PTR DS:[EBX+ECX*2]
 *  00815A04  |. 50             PUSH EAX	; jichi: source text
 *  00815A05  |. 52             PUSH EDX	; jichi: target text
 *
 *  00815A06  |. E8 C59E2200    CALL play.00A3F8D0	; jichi: called here
 *  00815A0B  |. 83C4 0C        ADD ESP,0xC
 *  00815A0E  |> 837E 14 08     CMP DWORD PTR DS:[ESI+0x14],0x8
 *  00815A12  |. 897E 10        MOV DWORD PTR DS:[ESI+0x10],EDI
 *  00815A15  |. 72 11          JB SHORT play.00815A28
 *  00815A17  |. 8B06           MOV EAX,DWORD PTR DS:[ESI]
 *  00815A19  |. 33C9           XOR ECX,ECX
 *  00815A1B  |. 66:890C78      MOV WORD PTR DS:[EAX+EDI*2],CX
 *  00815A1F  |. 8BC6           MOV EAX,ESI
 *  00815A21  |. 5F             POP EDI
 *  00815A22  |. 5E             POP ESI
 *  00815A23  |. 5B             POP EBX
 *  00815A24  |. 5D             POP EBP
 *  00815A25  |. C2 0C00        RETN 0xC
 *  00815A28  |> 8BC6           MOV EAX,ESI
 *  00815A2A  |. 33C9           XOR ECX,ECX
 *  00815A2C  |. 66:890C78      MOV WORD PTR DS:[EAX+EDI*2],CX
 *  00815A30  |> 5F             POP EDI
 *  00815A31  |. 8BC6           MOV EAX,ESI
 *  00815A33  |. 5E             POP ESI
 *  00815A34  |. 5B             POP EBX
 *  00815A35  |. 5D             POP EBP
 *  00815A36  |. C2 0C00        RETN 0xC
 *  00815A39  |> 68 A09FB000    PUSH play.00B09FA0                       ;  ASCII "invalid string position"
 *  00815A3E  |. E8 3AB22000    CALL play.00A20C7D
 *  00815A43  |> 68 B89FB000    PUSH play.00B09FB8                       ;  ASCII "string too long"
 *  00815A48  |. E8 02B22000    CALL play.00A20C4F
 *  00815A4D  |. CC             INT3
 *  00815A4E  |. CC             INT3
 *  00815A4F  |. CC             INT3
 *
 *  Alternatve pattern:
 *  Find one of caller of the push "invalid string position" instruction.
 */
bool attach(ulong startAddress, ulong stopAddress)
{
  const uint8_t bytes[] = {
    0x8d,0x04,0x3f, // 08159fd  |. 8d043f         lea eax,dword ptr ds:[edi+edi]	; jichi: edi *= 2 for wchar_t
    0x50,           // 0815a00  |. 50             push eax	; jichi: size
    0x8d,0x04,0x4b, // 0815a01  |. 8d044b         lea eax,dword ptr ds:[ebx+ecx*2]
    0x50,           // 0815a04  |. 50             push eax	; jichi: source text
    0x52            // 0815a05  |. 52             push edx	; jichi: target text
  };
  ulong addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  if (!addr)
    return addr;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return addr;
  //return winhook::hook_before(addr, Private::hookBefore);

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
} // namespace ScenarioHook2

namespace PopupHook1 { // only for old GXP1 engine
namespace Private {
  bool hookBefore(winhook::hook_stack *s)
  {
    static QString text_; // persistent storage, which makes this function not thread-safe
    auto arg = (TextUnionW *)(s->ecx + 0x1ec); // [ecx + 0x1ec]
    if (!arg->isValid())
      return true;
    auto text = arg->getText();
    if (isBadText(text))
      return true;
    auto retaddr = s->stack[0];
    auto reladdr = retaddr - moduleBaseAddress_;
    enum { role = Engine::OtherRole };
    QString oldText = QString::fromWCharArray(text),
            newText = EngineController::instance()->dispatchTextW(oldText, role, reladdr);
    if (newText == oldText)
      return true;
    text_ = newText;
    arg->setText(text_);
    return true;
  }
} // Private
/**
 *  Sample game: 魔導書の司書 (GXP1)
 *  Executable description shows "AVGEngineV2"
 *
 *  Debugging method:
 *  % hexstr ゲームを終了しますか utf16
 *  b230fc30e0309230427d864e57307e3059304b30
 *
 *  001090ED   CC               INT3
 *  001090EE   CC               INT3
 *  001090EF   CC               INT3
 *  001090F0   55               PUSH EBP
 *  001090F1   8BEC             MOV EBP,ESP
 *  001090F3   83E4 F8          AND ESP,0xFFFFFFF8
 *  001090F6   81EC A8000000    SUB ESP,0xA8
 *  001090FC   53               PUSH EBX
 *  001090FD   55               PUSH EBP
 *  001090FE   56               PUSH ESI
 *  001090FF   8BF1             MOV ESI,ECX
 *  00109101   8B06             MOV EAX,DWORD PTR DS:[ESI]
 *  00109103   8B90 A8000000    MOV EDX,DWORD PTR DS:[EAX+0xA8]
 *  00109109   57               PUSH EDI
 *  0010910A   FFD2             CALL EDX
 *  0010910C   8B10             MOV EDX,DWORD PTR DS:[EAX]
 *  0010910E   8BC8             MOV ECX,EAX
 *  00109110   8B82 00010000    MOV EAX,DWORD PTR DS:[EDX+0x100]
 *  00109116   56               PUSH ESI
 *  00109117   FFD0             CALL EAX
 *  00109119   84C0             TEST AL,AL
 *  0010911B   0F84 84040000    JE trial.001095A5
 *  00109121   E8 2AAA0000      CALL trial.00113B50
 *  00109126   E8 85F00100      CALL trial.001281B0
 *  0010912B   6A 01            PUSH 0x1
 *  0010912D   E8 7EEA0100      CALL trial.00127BB0
 *  00109132   8B16             MOV EDX,DWORD PTR DS:[ESI]
 *  00109134   8B92 B0000000    MOV EDX,DWORD PTR DS:[EDX+0xB0]
 *  0010913A   83C4 04          ADD ESP,0x4
 *  0010913D   8D4424 38        LEA EAX,DWORD PTR SS:[ESP+0x38]
 *  00109141   50               PUSH EAX
 *  00109142   8BCE             MOV ECX,ESI
 *  00109144   FFD2             CALL EDX
 *  00109146   D986 3C010000    FLD DWORD PTR DS:[ESI+0x13C]
 *  0010914C   DD05 B03C2500    FLD QWORD PTR DS:[0x253CB0]
 *  00109152   8B9E E4020000    MOV EBX,DWORD PTR DS:[ESI+0x2E4]
 *  00109158   DCC9             FMUL ST(1),ST
 *  0010915A   33ED             XOR EBP,EBP
 *  0010915C   D9C9             FXCH ST(1)
 *  0010915E   D95C24 60        FSTP DWORD PTR SS:[ESP+0x60]
 *  00109162   D986 40010000    FLD DWORD PTR DS:[ESI+0x140]
 *  00109168   D8C9             FMUL ST,ST(1)
 *  0010916A   D95C24 64        FSTP DWORD PTR SS:[ESP+0x64]
 *  0010916E   D88E 44010000    FMUL DWORD PTR DS:[ESI+0x144]
 *  00109174   D95C24 68        FSTP DWORD PTR SS:[ESP+0x68]
 *  00109178   D9EE             FLDZ
 *  0010917A   D95C24 6C        FSTP DWORD PTR SS:[ESP+0x6C]
 *  0010917E   D986 2C010000    FLD DWORD PTR DS:[ESI+0x12C]
 *  00109184   D95C24 48        FSTP DWORD PTR SS:[ESP+0x48]
 *  00109188   D986 30010000    FLD DWORD PTR DS:[ESI+0x130]
 *  0010918E   D95C24 4C        FSTP DWORD PTR SS:[ESP+0x4C]
 *  00109192   D986 4C010000    FLD DWORD PTR DS:[ESI+0x14C]
 *  00109198   D95C24 50        FSTP DWORD PTR SS:[ESP+0x50]
 *  0010919C   D986 50010000    FLD DWORD PTR DS:[ESI+0x150]
 *  001091A2   D95C24 54        FSTP DWORD PTR SS:[ESP+0x54]
 *  001091A6   3BDD             CMP EBX,EBP
 *  001091A8   74 7C            JE SHORT trial.00109226
 *  001091AA   D986 0C010000    FLD DWORD PTR DS:[ESI+0x10C]
 *  001091B0   8DBE EC000000    LEA EDI,DWORD PTR DS:[ESI+0xEC]
 *  001091B6   D95C24 28        FSTP DWORD PTR SS:[ESP+0x28]
 *  001091BA   8B86 74010000    MOV EAX,DWORD PTR DS:[ESI+0x174]
 *  001091C0   D947 24          FLD DWORD PTR DS:[EDI+0x24]
 *  001091C3   50               PUSH EAX
 *  001091C4   D95C24 30        FSTP DWORD PTR SS:[ESP+0x30]
 *  001091C8   51               PUSH ECX
 *  001091C9   D947 28          FLD DWORD PTR DS:[EDI+0x28]
 *  001091CC   8D4424 30        LEA EAX,DWORD PTR SS:[ESP+0x30]
 *  001091D0   D95C24 38        FSTP DWORD PTR SS:[ESP+0x38]
 *  001091D4   DB47 0C          FILD DWORD PTR DS:[EDI+0xC]
 *  001091D7   D84F 2C          FMUL DWORD PTR DS:[EDI+0x2C]
 *  001091DA   DC35 C83B2500    FDIV QWORD PTR DS:[0x253BC8]
 *  001091E0   D95C24 3C        FSTP DWORD PTR SS:[ESP+0x3C]
 *  001091E4   E8 C7FCF5FF      CALL trial.00068EB0
 *  001091E9   8B8E 70020000    MOV ECX,DWORD PTR DS:[ESI+0x270]
 *  001091EF   83C4 04          ADD ESP,0x4
 *  001091F2   50               PUSH EAX
 *  001091F3   51               PUSH ECX
 *  001091F4   8BC7             MOV EAX,EDI
 *  001091F6   E8 0500F6FF      CALL trial.00069200
 *  001091FB   D94424 44        FLD DWORD PTR SS:[ESP+0x44]
 *  001091FF   50               PUSH EAX
 *  00109200   8D5424 5C        LEA EDX,DWORD PTR SS:[ESP+0x5C]
 *  00109204   52               PUSH EDX
 *  00109205   8D4424 70        LEA EAX,DWORD PTR SS:[ESP+0x70]
 *  00109209   50               PUSH EAX
 *  0010920A   8D4C24 5C        LEA ECX,DWORD PTR SS:[ESP+0x5C]
 *  0010920E   51               PUSH ECX
 *  0010920F   83EC 08          SUB ESP,0x8
 *  00109212   D95C24 04        FSTP DWORD PTR SS:[ESP+0x4]
 *  00109216   D94424 58        FLD DWORD PTR SS:[ESP+0x58]
 *  0010921A   D91C24           FSTP DWORD PTR SS:[ESP]
 *  0010921D   53               PUSH EBX
 *  0010921E   E8 4DFC0100      CALL trial.00128E70
 *  00109223   83C4 24          ADD ESP,0x24
 *  00109226   8B86 F0020000    MOV EAX,DWORD PTR DS:[ESI+0x2F0]
 *  0010922C   8D4C24 70        LEA ECX,DWORD PTR SS:[ESP+0x70]
 *  00109230   E8 8BF6F5FF      CALL trial.000688C0
 *  00109235   DB86 F8000000    FILD DWORD PTR DS:[ESI+0xF8]
 *  0010923B   8B86 F4020000    MOV EAX,DWORD PTR DS:[ESI+0x2F4]
 *  00109241   8D8C24 80000000  LEA ECX,DWORD PTR SS:[ESP+0x80]
 *  00109248   DC35 C83B2500    FDIV QWORD PTR DS:[0x253BC8]
 *  0010924E   DD5424 28        FST QWORD PTR SS:[ESP+0x28]
 *  00109252   D84C24 7C        FMUL DWORD PTR SS:[ESP+0x7C]
 *  00109256   D95C24 7C        FSTP DWORD PTR SS:[ESP+0x7C]
 *  0010925A   E8 61F6F5FF      CALL trial.000688C0
 *  0010925F   D98424 8C000000  FLD DWORD PTR SS:[ESP+0x8C]
 *  00109266   896C24 18        MOV DWORD PTR SS:[ESP+0x18],EBP
 *  0010926A   DC4C24 28        FMUL QWORD PTR SS:[ESP+0x28]
 *  0010926E   D99C24 8C000000  FSTP DWORD PTR SS:[ESP+0x8C]
 *  00109275   39AE FC020000    CMP DWORD PTR DS:[ESI+0x2FC],EBP
 *  0010927B   0F84 A6000000    JE trial.00109327
 *  00109281   33FF             XOR EDI,EDI
 *  00109283   39AE FC010000    CMP DWORD PTR DS:[ESI+0x1FC],EBP
 *  00109289   0F86 A2000000    JBE trial.00109331
 *  0010928F   3BBE FC010000    CMP EDI,DWORD PTR DS:[ESI+0x1FC]
 *  00109295   76 05            JBE SHORT trial.0010929C
 *  00109297   E8 72540800      CALL trial.0018E70E
 *  0010929C   BB 08000000      MOV EBX,0x8
 *  001092A1   399E 00020000    CMP DWORD PTR DS:[ESI+0x200],EBX
 *  001092A7   72 08            JB SHORT trial.001092B1
 *  001092A9   8B86 EC010000    MOV EAX,DWORD PTR DS:[ESI+0x1EC] ; jichi: text in eax
 *  001092AF   EB 06            JMP SHORT trial.001092B7
 *  001092B1   8D86 EC010000    LEA EAX,DWORD PTR DS:[ESI+0x1EC]
 *  001092B7   0FB71478         MOVZX EDX,WORD PTR DS:[EAX+EDI*2]
 *  001092BB   52               PUSH EDX
 *  001092BC   E8 5F0C0300      CALL trial.00139F20
 *  001092C1   0FAF86 EC020000  IMUL EAX,DWORD PTR DS:[ESI+0x2EC]
 *  001092C8   99               CDQ
 *  001092C9   2BC2             SUB EAX,EDX
 *  001092CB   D1F8             SAR EAX,1
 *  001092CD   014424 1C        ADD DWORD PTR SS:[ESP+0x1C],EAX
 *  001092D1   83C4 04          ADD ESP,0x4
 *  001092D4   3BBE FC010000    CMP EDI,DWORD PTR DS:[ESI+0x1FC]
 *  001092DA   76 05            JBE SHORT trial.001092E1
 *  001092DC   E8 2D540800      CALL trial.0018E70E
 *  001092E1   399E 00020000    CMP DWORD PTR DS:[ESI+0x200],EBX
 *  001092E7   72 08            JB SHORT trial.001092F1
 *  001092E9   8B86 EC010000    MOV EAX,DWORD PTR DS:[ESI+0x1EC]
 *  001092EF   EB 06            JMP SHORT trial.001092F7
 *  001092F1   8D86 EC010000    LEA EAX,DWORD PTR DS:[ESI+0x1EC]
 *  001092F7   8B4E 34          MOV ECX,DWORD PTR DS:[ESI+0x34]
 *  001092FA   8B51 54          MOV EDX,DWORD PTR DS:[ECX+0x54]
 *  001092FD   8B8A 68030000    MOV ECX,DWORD PTR DS:[EDX+0x368]
 *  00109303   66:8B1478        MOV DX,WORD PTR DS:[EAX+EDI*2]
 *  00109307   66:3B91 9E000000 CMP DX,WORD PTR DS:[ECX+0x9E]
 *  0010930E   74 0B            JE SHORT trial.0010931B
 *  00109310   47               INC EDI
 *  00109311   3BBE FC010000    CMP EDI,DWORD PTR DS:[ESI+0x1FC]
 *  00109317  ^72 83            JB SHORT trial.0010929C
 *  00109319   EB 1B            JMP SHORT trial.00109336
 *  0010931B   8B86 54020000    MOV EAX,DWORD PTR DS:[ESI+0x254]
 *  00109321   894424 18        MOV DWORD PTR SS:[ESP+0x18],EAX
 *  00109325   EB 0F            JMP SHORT trial.00109336
 *  00109327   8B8E 54020000    MOV ECX,DWORD PTR DS:[ESI+0x254]
 *  0010932D   894C24 18        MOV DWORD PTR SS:[ESP+0x18],ECX
 *  00109331   BB 08000000      MOV EBX,0x8
 *  00109336   8B86 54020000    MOV EAX,DWORD PTR DS:[ESI+0x254]
 *  0010933C   394424 18        CMP DWORD PTR SS:[ESP+0x18],EAX
 *  00109340   7E 04            JLE SHORT trial.00109346
 *  00109342   894424 18        MOV DWORD PTR SS:[ESP+0x18],EAX
 *  00109346   33FF             XOR EDI,EDI
 *  00109348   897C24 1C        MOV DWORD PTR SS:[ESP+0x1C],EDI
 *  0010934C   3BBE FC010000    CMP EDI,DWORD PTR DS:[ESI+0x1FC]
 *  00109352   0F83 48020000    JNB trial.001095A0
 *  00109358   76 05            JBE SHORT trial.0010935F
 *  0010935A   E8 AF530800      CALL trial.0018E70E
 *  0010935F   399E 00020000    CMP DWORD PTR DS:[ESI+0x200],EBX
 *  00109365   72 08            JB SHORT trial.0010936F
 *  00109367   8B86 EC010000    MOV EAX,DWORD PTR DS:[ESI+0x1EC]
 *  0010936D   EB 06            JMP SHORT trial.00109375
 *  0010936F   8D86 EC010000    LEA EAX,DWORD PTR DS:[ESI+0x1EC]
 *  00109375   8B56 34          MOV EDX,DWORD PTR DS:[ESI+0x34]
 *  00109378   8B4A 54          MOV ECX,DWORD PTR DS:[EDX+0x54]
 *  0010937B   8B91 68030000    MOV EDX,DWORD PTR DS:[ECX+0x368]
 *  00109381   66:8B0478        MOV AX,WORD PTR DS:[EAX+EDI*2]
 *  00109385   66:3B82 9E000000 CMP AX,WORD PTR DS:[EDX+0x9E]
 *  0010938C   75 11            JNZ SHORT trial.0010939F
 *  0010938E   8B8E EC020000    MOV ECX,DWORD PTR DS:[ESI+0x2EC]
 *  00109394   33ED             XOR EBP,EBP
 *  00109396   014C24 1C        ADD DWORD PTR SS:[ESP+0x1C],ECX
 *  0010939A   E9 F4010000      JMP trial.00109593
 *  0010939F   3BBE FC010000    CMP EDI,DWORD PTR DS:[ESI+0x1FC]
 *  001093A5   76 05            JBE SHORT trial.001093AC
 *  001093A7   E8 62530800      CALL trial.0018E70E
 *  001093AC   399E 00020000    CMP DWORD PTR DS:[ESI+0x200],EBX
 *  001093B2   72 08            JB SHORT trial.001093BC
 *  001093B4   8B86 EC010000    MOV EAX,DWORD PTR DS:[ESI+0x1EC]
 *  001093BA   EB 06            JMP SHORT trial.001093C2
 *  001093BC   8D86 EC010000    LEA EAX,DWORD PTR DS:[ESI+0x1EC]
 *  001093C2   8B8E E8020000    MOV ECX,DWORD PTR DS:[ESI+0x2E8]
 *  001093C8   0FB71478         MOVZX EDX,WORD PTR DS:[EAX+EDI*2]
 *  001093CC   6BC9 70          IMUL ECX,ECX,0x70
 *  001093CF   52               PUSH EDX
 *  001093D0   8D8424 94000000  LEA EAX,DWORD PTR SS:[ESP+0x94]
 *  001093D7   50               PUSH EAX
 *  001093D8   81C1 408A2A00    ADD ECX,trial.002A8A40
 *  001093DE   E8 FDF50200      CALL trial.001389E0
 *  001093E3   8B86 54020000    MOV EAX,DWORD PTR DS:[ESI+0x254]
 *  001093E9   2B4424 18        SUB EAX,DWORD PTR SS:[ESP+0x18]
 *  001093ED   8B8E 50020000    MOV ECX,DWORD PTR DS:[ESI+0x250]
 *  001093F3   034C24 1C        ADD ECX,DWORD PTR SS:[ESP+0x1C]
 *  001093F7   99               CDQ
 *  001093F8   2BC2             SUB EAX,EDX
 *  001093FA   D1F8             SAR EAX,1
 *  001093FC   0386 4C020000    ADD EAX,DWORD PTR DS:[ESI+0x24C]
 *  00109402   894C24 24        MOV DWORD PTR SS:[ESP+0x24],ECX
 *  00109406   03C5             ADD EAX,EBP
 *  00109408   894424 20        MOV DWORD PTR SS:[ESP+0x20],EAX
 *  0010940C   DB4424 20        FILD DWORD PTR SS:[ESP+0x20]
 *  00109410   D95C24 20        FSTP DWORD PTR SS:[ESP+0x20]
 *  00109414   DB4424 24        FILD DWORD PTR SS:[ESP+0x24]
 *  00109418   D95C24 24        FSTP DWORD PTR SS:[ESP+0x24]
 *  0010941C   3BBE FC010000    CMP EDI,DWORD PTR DS:[ESI+0x1FC]
 *  00109422   76 05            JBE SHORT trial.00109429
 *  00109424   E8 E5520800      CALL trial.0018E70E
 *  00109429   399E 00020000    CMP DWORD PTR DS:[ESI+0x200],EBX
 *  0010942F   72 08            JB SHORT trial.00109439
 *  00109431   8B86 EC010000    MOV EAX,DWORD PTR DS:[ESI+0x1EC]
 *  00109437   EB 06            JMP SHORT trial.0010943F
 *  00109439   8D86 EC010000    LEA EAX,DWORD PTR DS:[ESI+0x1EC]
 *  0010943F   0FB71478         MOVZX EDX,WORD PTR DS:[EAX+EDI*2]
 *  00109443   8B9E EC020000    MOV EBX,DWORD PTR DS:[ESI+0x2EC]
 *  00109449   52               PUSH EDX
 *  0010944A   E8 D10A0300      CALL trial.00139F20
 *  0010944F   0FAFC3           IMUL EAX,EBX
 *  00109452   99               CDQ
 *  00109453   2BC2             SUB EAX,EDX
 *  00109455   D1F8             SAR EAX,1
 *  00109457   03E8             ADD EBP,EAX
 *  00109459   03DD             ADD EBX,EBP
 *  0010945B   83C4 04          ADD ESP,0x4
 *  0010945E   3B9E 54020000    CMP EBX,DWORD PTR DS:[ESI+0x254]
 *  00109464   7C 0C            JL SHORT trial.00109472
 *  00109466   8B86 EC020000    MOV EAX,DWORD PTR DS:[ESI+0x2EC]
 *  0010946C   33ED             XOR EBP,EBP
 *  0010946E   014424 1C        ADD DWORD PTR SS:[ESP+0x1C],EAX
 *  00109472   83BC24 90000000 >CMP DWORD PTR SS:[ESP+0x90],0x0
 *  0010947A   0F84 0E010000    JE trial.0010958E
 *  00109480   80BE F8020000 00 CMP BYTE PTR DS:[ESI+0x2F8],0x0
 *  00109487   0F84 85000000    JE trial.00109512
 *  0010948D   8B8E 74010000    MOV ECX,DWORD PTR DS:[ESI+0x174]
 *  00109493   D986 2C010000    FLD DWORD PTR DS:[ESI+0x12C]
 *  00109499   D95C24 58        FSTP DWORD PTR SS:[ESP+0x58]
 *  0010949D   51               PUSH ECX
 *  0010949E   D986 30010000    FLD DWORD PTR DS:[ESI+0x130]
 *  001094A4   6A 00            PUSH 0x0
 *  001094A6   8D8424 88000000  LEA EAX,DWORD PTR SS:[ESP+0x88]
 *  001094AD   D95C24 64        FSTP DWORD PTR SS:[ESP+0x64]
 *  001094B1   E8 FAF9F5FF      CALL trial.00068EB0
 *  001094B6   D9E8             FLD1
 *  001094B8   50               PUSH EAX
 *  001094B9   68 A8872A00      PUSH trial.002A87A8
 *  001094BE   68 B0872A00      PUSH trial.002A87B0
 *  001094C3   8D5424 6C        LEA EDX,DWORD PTR SS:[ESP+0x6C]
 *  001094C7   52               PUSH EDX
 *  001094C8   83EC 0C          SUB ESP,0xC
 *  001094CB   D95C24 08        FSTP DWORD PTR SS:[ESP+0x8]
 *  001094CF   8D8424 B4000000  LEA EAX,DWORD PTR SS:[ESP+0xB4]
 *  001094D6   D986 30010000    FLD DWORD PTR DS:[ESI+0x130]
 *  001094DC   D84C24 48        FMUL DWORD PTR SS:[ESP+0x48]
 *  001094E0   D84424 60        FADD DWORD PTR SS:[ESP+0x60]
 *  001094E4   D95C24 38        FSTP DWORD PTR SS:[ESP+0x38]
 *  001094E8   D94424 38        FLD DWORD PTR SS:[ESP+0x38]
 *  001094EC   D95C24 04        FSTP DWORD PTR SS:[ESP+0x4]
 *  001094F0   D986 2C010000    FLD DWORD PTR DS:[ESI+0x12C]
 *  001094F6   D84C24 44        FMUL DWORD PTR SS:[ESP+0x44]
 *  001094FA   D84424 5C        FADD DWORD PTR SS:[ESP+0x5C]
 *  001094FE   D95C24 38        FSTP DWORD PTR SS:[ESP+0x38]
 *  00109502   D94424 38        FLD DWORD PTR SS:[ESP+0x38]
 *  00109506   D91C24           FSTP DWORD PTR SS:[ESP]
 *  00109509   50               PUSH EAX
 *  0010950A   E8 41CAF6FF      CALL trial.00075F50
 *  0010950F   83C4 28          ADD ESP,0x28
 *  00109512   8B8E 74010000    MOV ECX,DWORD PTR DS:[ESI+0x174]
 *  00109518   D986 2C010000    FLD DWORD PTR DS:[ESI+0x12C]
 *  0010951E   D95C24 28        FSTP DWORD PTR SS:[ESP+0x28]
 *  00109522   51               PUSH ECX
 *  00109523   D986 30010000    FLD DWORD PTR DS:[ESI+0x130]
 *  00109529   6A 00            PUSH 0x0
 *  0010952B   8D4424 78        LEA EAX,DWORD PTR SS:[ESP+0x78]
 *  0010952F   D95C24 34        FSTP DWORD PTR SS:[ESP+0x34]
 *  00109533   E8 78F9F5FF      CALL trial.00068EB0
 *  00109538   D986 30010000    FLD DWORD PTR DS:[ESI+0x130]
 *  0010953E   D84C24 2C        FMUL DWORD PTR SS:[ESP+0x2C]
 *  00109542   50               PUSH EAX
 *  00109543   68 A8872A00      PUSH trial.002A87A8
 *  00109548   68 B0872A00      PUSH trial.002A87B0
 *  0010954D   D84424 50        FADD DWORD PTR SS:[ESP+0x50]
 *  00109551   8D5424 3C        LEA EDX,DWORD PTR SS:[ESP+0x3C]
 *  00109555   52               PUSH EDX
 *  00109556   83EC 08          SUB ESP,0x8
 *  00109559   D95C24 34        FSTP DWORD PTR SS:[ESP+0x34]
 *  0010955D   8D8424 B0000000  LEA EAX,DWORD PTR SS:[ESP+0xB0]
 *  00109564   D94424 34        FLD DWORD PTR SS:[ESP+0x34]
 *  00109568   D95C24 04        FSTP DWORD PTR SS:[ESP+0x4]
 *  0010956C   D986 2C010000    FLD DWORD PTR DS:[ESI+0x12C]
 *  00109572   D84C24 40        FMUL DWORD PTR SS:[ESP+0x40]
 *  00109576   D84424 58        FADD DWORD PTR SS:[ESP+0x58]
 *  0010957A   D95C24 34        FSTP DWORD PTR SS:[ESP+0x34]
 *  0010957E   D94424 34        FLD DWORD PTR SS:[ESP+0x34]
 *  00109582   D91C24           FSTP DWORD PTR SS:[ESP]
 *  00109585   50               PUSH EAX
 *  00109586   E8 25C9F6FF      CALL trial.00075EB0
 *  0010958B   83C4 24          ADD ESP,0x24
 *  0010958E   BB 08000000      MOV EBX,0x8
 *  00109593   47               INC EDI
 *  00109594   3BBE FC010000    CMP EDI,DWORD PTR DS:[ESI+0x1FC]
 *  0010959A  ^0F82 BFFDFFFF    JB trial.0010935F
 *  001095A0   E8 EBA50000      CALL trial.00113B90
 *  001095A5   5F               POP EDI
 *  001095A6   33C0             XOR EAX,EAX
 *  001095A8   5E               POP ESI
 *  001095A9   5D               POP EBP
 *  001095AA   5B               POP EBX
 *  001095AB   8BE5             MOV ESP,EBP
 *  001095AD   5D               POP EBP
 *  001095AE   C2 0800          RETN 0x8
 *  001095B1   CC               INT3
 *  001095B2   CC               INT3
 *  001095B3   CC               INT3
 *  001095B4   CC               INT3
 */
bool attach(ulong startAddress, ulong stopAddress)
{
  const uint8_t bytes[] = {
    0x8b,0x86, 0xec,0x01,0x00,0x00, // 001092a9   8b86 ec010000    mov eax,dword ptr ds:[esi+0x1ec] ; jichi: text in eax
    0xeb, 0x06,                     // 001092af   eb 06            jmp short trial.001092b7
    0x8d,0x86, 0xec,0x01,0x00,0x00, // 001092b1   8d86 ec010000    lea eax,dword ptr ds:[esi+0x1ec]
    0x0f,0xb7,0x14,0x78,            // 001092b7   0fb71478         movzx edx,word ptr ds:[eax+edi*2]
    0x52                            // 001092bb   52               push edx
  };
  ulong addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  return winhook::hook_before(addr, Private::hookBefore);
  // Function called at runtime
  //int count = 0;
  //auto fun = [&count](ulong addr) -> bool {
  //  auto before = std::bind(Private::hookBefore, addr + 5, std::placeholders::_1);
  //  count += winhook::hook_both(addr, before, Private::hookAfter);
  //  return true; // replace all functions
  //};
  //MemDbg::iterNearCallAddress(fun, addr, startAddress, stopAddress);
  //DOUT("call number =" << count);
  //return count;
}
} // namespace PopupHook1

namespace OtherHook { // for all GXP engines
namespace Private {
  bool hookBefore(winhook::hook_stack *s)
  {
    static QString text_;
    auto text = (LPCWSTR)s->stack[3]; // arg3
    if (!text || !*text)
      return true;
    auto retaddr = s->stack[0];
    auto reladdr = retaddr - moduleBaseAddress_;
    enum { role = Engine::OtherRole };
    QString oldText = QString::fromWCharArray(text),
            newText = EngineController::instance()->dispatchTextW(oldText, role, reladdr);
    if (newText.isEmpty() || oldText == newText)
      return true;
    newText.replace("%r", "\n");
    text_ = newText;
    s->stack[3] = (ulong)text_.utf16();
    return true;
  }
} // Private
/**
 *  Sample game: ウルスラグナ征戦のデュエリス (GXP2)
 *  Executable description shows "AVGEngineV2"
 *
 *  Function found by back-tracking GetGlyphOutlineW
 *
 *  014D449A   CC               INT3
 *  014D449B   CC               INT3
 *  014D449C   CC               INT3
 *  014D449D   CC               INT3
 *  014D449E   CC               INT3
 *  014D449F   CC               INT3
 *  014D44A0   55               PUSH EBP
 *  014D44A1   8BEC             MOV EBP,ESP
 *  014D44A3   6A FF            PUSH -0x1
 *  014D44A5   68 80DA5801      PUSH verethra.0158DA80
 *  014D44AA   64:A1 00000000   MOV EAX,DWORD PTR FS:[0]
 *  014D44B0   50               PUSH EAX
 *  014D44B1   83EC 2C          SUB ESP,0x2C
 *  014D44B4   53               PUSH EBX
 *  014D44B5   56               PUSH ESI
 *  014D44B6   57               PUSH EDI
 *  014D44B7   A1 20B06801      MOV EAX,DWORD PTR DS:[0x168B020]
 *  014D44BC   33C5             XOR EAX,EBP
 *  014D44BE   50               PUSH EAX
 *  014D44BF   8D45 F4          LEA EAX,DWORD PTR SS:[EBP-0xC]
 *  014D44C2   64:A3 00000000   MOV DWORD PTR FS:[0],EAX
 *  014D44C8   8B45 14          MOV EAX,DWORD PTR SS:[EBP+0x14]
 *  014D44CB   C745 C8 00000000 MOV DWORD PTR SS:[EBP-0x38],0x0
 *  014D44D2   C745 CC 00000000 MOV DWORD PTR SS:[EBP-0x34],0x0
 *  014D44D9   C745 D0 00000000 MOV DWORD PTR SS:[EBP-0x30],0x0
 *  014D44E0   8B10             MOV EDX,DWORD PTR DS:[EAX]
 *  014D44E2   8B48 04          MOV ECX,DWORD PTR DS:[EAX+0x4]
 *  014D44E5   8B40 08          MOV EAX,DWORD PTR DS:[EAX+0x8]
 *  014D44E8   2BC2             SUB EAX,EDX
 *  014D44EA   8955 EC          MOV DWORD PTR SS:[EBP-0x14],EDX
 *  014D44ED   894D E8          MOV DWORD PTR SS:[EBP-0x18],ECX
 *  014D44F0   8945 E0          MOV DWORD PTR SS:[EBP-0x20],EAX
 *  014D44F3   6A 04            PUSH 0x4
 *  014D44F5   8D4D C8          LEA ECX,DWORD PTR SS:[EBP-0x38]
 *  014D44F8   C745 FC 00000000 MOV DWORD PTR SS:[EBP-0x4],0x0
 *  014D44FF   E8 8C89EBFF      CALL verethra.0138CE90
 *  014D4504   C745 D4 00000000 MOV DWORD PTR SS:[EBP-0x2C],0x0
 *  014D450B   C745 D8 00000000 MOV DWORD PTR SS:[EBP-0x28],0x0
 *  014D4512   C745 DC 00000000 MOV DWORD PTR SS:[EBP-0x24],0x0
 *  014D4519   6A 04            PUSH 0x4
 *  014D451B   8D4D D4          LEA ECX,DWORD PTR SS:[EBP-0x2C]
 *  014D451E   C645 FC 01       MOV BYTE PTR SS:[EBP-0x4],0x1
 *  014D4522   E8 697BE8FF      CALL verethra.0135C090
 *  014D4527   8B7D 10          MOV EDI,DWORD PTR SS:[EBP+0x10]
 *  014D452A   33C0             XOR EAX,EAX
 *  014D452C   33DB             XOR EBX,EBX
 *  014D452E   8945 F0          MOV DWORD PTR SS:[EBP-0x10],EAX
 *  014D4531   66:3907          CMP WORD PTR DS:[EDI],AX
 *  014D4534   0F84 C3000000    JE verethra.014D45FD
 *  014D453A   BE 01000000      MOV ESI,0x1
 *  014D453F   8945 14          MOV DWORD PTR SS:[EBP+0x14],EAX
 *  014D4542   8975 10          MOV DWORD PTR SS:[EBP+0x10],ESI
 *  014D4545   8B4D D8          MOV ECX,DWORD PTR SS:[EBP-0x28]
 *  014D4548   B8 ABAAAA2A      MOV EAX,0x2AAAAAAB
 *  014D454D   2B4D D4          SUB ECX,DWORD PTR SS:[EBP-0x2C]
 *  014D4550   F7E9             IMUL ECX
 *  014D4552   C1FA 02          SAR EDX,0x2
 *  014D4555   8BC2             MOV EAX,EDX
 *  014D4557   C1E8 1F          SHR EAX,0x1F
 *  014D455A   03C2             ADD EAX,EDX
 *  014D455C   3BC3             CMP EAX,EBX
 *  014D455E   77 09            JA SHORT verethra.014D4569
 *  014D4560   56               PUSH ESI
 *  014D4561   8D4D D4          LEA ECX,DWORD PTR SS:[EBP-0x2C]
 *  014D4564   E8 C712F4FF      CALL verethra.01415830
 *  014D4569   8B45 CC          MOV EAX,DWORD PTR SS:[EBP-0x34]
 *  014D456C   2B45 C8          SUB EAX,DWORD PTR SS:[EBP-0x38]
 *  014D456F   C1F8 02          SAR EAX,0x2
 *  014D4572   3BC3             CMP EAX,EBX
 *  014D4574   77 14            JA SHORT verethra.014D458A
 *  014D4576   8D45 E4          LEA EAX,DWORD PTR SS:[EBP-0x1C]
 *  014D4579   C745 E4 00000000 MOV DWORD PTR SS:[EBP-0x1C],0x0
 *  014D4580   50               PUSH EAX
 *  014D4581   56               PUSH ESI
 *  014D4582   8D4D C8          LEA ECX,DWORD PTR SS:[EBP-0x38]
 *  014D4585   E8 06D2EDFF      CALL verethra.013B1790
 *  014D458A   0FB707           MOVZX EAX,WORD PTR DS:[EDI]
 *  014D458D   66:3B45 28       CMP AX,WORD PTR SS:[EBP+0x28]
 *  014D4591   74 4F            JE SHORT verethra.014D45E2
 *  014D4593   8B75 0C          MOV ESI,DWORD PTR SS:[EBP+0xC]
 *  014D4596   50               PUSH EAX
 *  014D4597   8B76 18          MOV ESI,DWORD PTR DS:[ESI+0x18]
 *  014D459A   E8 41100000      CALL verethra.014D55E0
 *  014D459F   8B4D 14          MOV ECX,DWORD PTR SS:[EBP+0x14]
 *  014D45A2   83C4 04          ADD ESP,0x4
 *  014D45A5   034D D4          ADD ECX,DWORD PTR SS:[EBP-0x2C]
 *  014D45A8   0FAFC6           IMUL EAX,ESI
 *  014D45AB   8B75 F0          MOV ESI,DWORD PTR SS:[EBP-0x10]
 *
 *  014D45AE   99               CDQ
 *  014D45AF   2BC2             SUB EAX,EDX
 *  014D45B1   D1F8             SAR EAX,1
 *  014D45B3   03F0             ADD ESI,EAX
 *  014D45B5   0FB707           MOVZX EAX,WORD PTR DS:[EDI]
 *
 *  014D45B8   50               PUSH EAX
 *  014D45B9   6A 01            PUSH 0x1
 *  014D45BB   8975 F0          MOV DWORD PTR SS:[EBP-0x10],ESI
 *  014D45BE   E8 5D40ECFF      CALL verethra.01398620
 *  014D45C3   8B55 C8          MOV EDX,DWORD PTR SS:[EBP-0x38]
 *  014D45C6   8BCE             MOV ECX,ESI
 *  014D45C8   8B45 0C          MOV EAX,DWORD PTR SS:[EBP+0xC]
 *  014D45CB   39349A           CMP DWORD PTR DS:[EDX+EBX*4],ESI
 *  014D45CE   0F4F0C9A         CMOVG ECX,DWORD PTR DS:[EDX+EBX*4]
 *  014D45D2   890C9A           MOV DWORD PTR DS:[EDX+EBX*4],ECX
 *  014D45D5   8B40 18          MOV EAX,DWORD PTR DS:[EAX+0x18]
 *  014D45D8   03C6             ADD EAX,ESI
 *  014D45DA   8B75 10          MOV ESI,DWORD PTR SS:[EBP+0x10]
 *  014D45DD   3B45 E0          CMP EAX,DWORD PTR SS:[EBP-0x20]
 *  014D45E0   7C 0E            JL SHORT verethra.014D45F0
 *  014D45E2   33C0             XOR EAX,EAX
 *  014D45E4   46               INC ESI
 *  014D45E5   43               INC EBX
 *  014D45E6   8975 10          MOV DWORD PTR SS:[EBP+0x10],ESI
 *  014D45E9   8345 14 18       ADD DWORD PTR SS:[EBP+0x14],0x18
 *  014D45ED   8945 F0          MOV DWORD PTR SS:[EBP-0x10],EAX
 *  014D45F0   83C7 02          ADD EDI,0x2
 *  014D45F3   66:833F 00       CMP WORD PTR DS:[EDI],0x0
 *  014D45F7  ^0F85 48FFFFFF    JNZ verethra.014D4545
 *  014D45FD   8B75 D8          MOV ESI,DWORD PTR SS:[EBP-0x28]
 *  014D4600   B8 ABAAAA2A      MOV EAX,0x2AAAAAAB
 *  014D4605   8B5D D4          MOV EBX,DWORD PTR SS:[EBP-0x2C]
 *  014D4608   8BCE             MOV ECX,ESI
 *  014D460A   2BCB             SUB ECX,EBX
 *  014D460C   F7E9             IMUL ECX
 *  014D460E   C1FA 02          SAR EDX,0x2
 *  014D4611   8BCA             MOV ECX,EDX
 *  014D4613   C1E9 1F          SHR ECX,0x1F
 *  014D4616   03CA             ADD ECX,EDX
 *  014D4618   894D E0          MOV DWORD PTR SS:[EBP-0x20],ECX
 *  014D461B   75 53            JNZ SHORT verethra.014D4670
 *  014D461D   8B7D 08          MOV EDI,DWORD PTR SS:[EBP+0x8]
 *  014D4620   8B4D EC          MOV ECX,DWORD PTR SS:[EBP-0x14]
 *  014D4623   8B45 E8          MOV EAX,DWORD PTR SS:[EBP-0x18]
 *  014D4626   890F             MOV DWORD PTR DS:[EDI],ECX
 *  014D4628   8947 04          MOV DWORD PTR DS:[EDI+0x4],EAX
 *  014D462B   894F 08          MOV DWORD PTR DS:[EDI+0x8],ECX
 *  014D462E   8947 0C          MOV DWORD PTR DS:[EDI+0xC],EAX
 *  014D4631   85DB             TEST EBX,EBX
 *  014D4633   74 17            JE SHORT verethra.014D464C
 *  014D4635   FF75 14          PUSH DWORD PTR SS:[EBP+0x14]
 *  014D4638   8D45 17          LEA EAX,DWORD PTR SS:[EBP+0x17]
 *  014D463B   50               PUSH EAX
 *  014D463C   56               PUSH ESI
 *  014D463D   53               PUSH EBX
 *  014D463E   E8 3D22E8FF      CALL verethra.01356880
 *  014D4643   53               PUSH EBX
 *  014D4644   E8 8CAE0600      CALL verethra.0153F4D5
 *  014D4649   83C4 14          ADD ESP,0x14
 *  014D464C   8B45 C8          MOV EAX,DWORD PTR SS:[EBP-0x38]
 *  014D464F   85C0             TEST EAX,EAX
 *  014D4651   74 09            JE SHORT verethra.014D465C
 *  014D4653   50               PUSH EAX
 *  014D4654   E8 7CAE0600      CALL verethra.0153F4D5
 *  014D4659   83C4 04          ADD ESP,0x4
 *  014D465C   8BC7             MOV EAX,EDI
 *  014D465E   8B4D F4          MOV ECX,DWORD PTR SS:[EBP-0xC]
 *  014D4661   64:890D 00000000 MOV DWORD PTR FS:[0],ECX
 *  014D4668   59               POP ECX
 *  014D4669   5F               POP EDI
 *  014D466A   5E               POP ESI
 *  014D466B   5B               POP EBX
 *  014D466C   8BE5             MOV ESP,EBP
 *  014D466E   5D               POP EBP
 *  014D466F   C3               RETN
 *  014D4670   33C0             XOR EAX,EAX
 *  014D4672   C745 E4 00000000 MOV DWORD PTR SS:[EBP-0x1C],0x0
 *  014D4679   33F6             XOR ESI,ESI
 *  014D467B   8945 10          MOV DWORD PTR SS:[EBP+0x10],EAX
 *  014D467E   85C9             TEST ECX,ECX
 *  014D4680   0F84 C0000000    JE verethra.014D4746
 *  014D4686   8B4D EC          MOV ECX,DWORD PTR SS:[EBP-0x14]
 *  014D4689   8BFB             MOV EDI,EBX
 *  014D468B   8B5D 0C          MOV EBX,DWORD PTR SS:[EBP+0xC]
 *  014D468E   894D E4          MOV DWORD PTR SS:[EBP-0x1C],ECX
 *  014D4691   66:0F6EC9        MOVD MM1,ECX
 *  014D4695   0F5B             ???                                      ; Unknown command
 *  014D4697   C9               LEAVE
 *  014D4698   F3:0F114D F0     MOVSS DWORD PTR SS:[EBP-0x10],XMM1
 *  014D469D   8D49 00          LEA ECX,DWORD PTR DS:[ECX]
 *  014D46A0   8B73 18          MOV ESI,DWORD PTR DS:[EBX+0x18]
 *  014D46A3   0FAFF0           IMUL ESI,EAX
 *  014D46A6   0375 E8          ADD ESI,DWORD PTR SS:[EBP-0x18]
 *  014D46A9   837F 14 08       CMP DWORD PTR DS:[EDI+0x14],0x8
 *  014D46AD   72 07            JB SHORT verethra.014D46B6
 *  014D46AF   8B07             MOV EAX,DWORD PTR DS:[EDI]
 *  014D46B1   8945 14          MOV DWORD PTR SS:[EBP+0x14],EAX
 *  014D46B4   EB 05            JMP SHORT verethra.014D46BB
 *  014D46B6   8BC7             MOV EAX,EDI
 *  014D46B8   897D 14          MOV DWORD PTR SS:[EBP+0x14],EDI
 *  014D46BB   FF75 28          PUSH DWORD PTR SS:[EBP+0x28]
 *  014D46BE   66:0F6EC6        MOVD MM0,ESI
 *  014D46C2   FF75 24          PUSH DWORD PTR SS:[EBP+0x24]
 *  014D46C5   0F5B             ???                                      ; Unknown command
 *  014D46C7   C06A 00 FF       SHR BYTE PTR DS:[EDX],0xFF               ; Shift constant out of range 1..31
 *  014D46CB   75 20            JNZ SHORT verethra.014D46ED
 *  014D46CD   68 A0956901      PUSH verethra.016995A0
 *  014D46D2   83EC 0C          SUB ESP,0xC
 *  014D46D5   C74424 08 000080>MOV DWORD PTR SS:[ESP+0x8],0x3F800000
 *  014D46DD   F3:0F114424 04   MOVSS DWORD PTR SS:[ESP+0x4],XMM0
 *  014D46E3   F3:0F110C24      MOVSS DWORD PTR SS:[ESP],XMM1
 *  014D46E8   50               PUSH EAX
 *  014D46E9   53               PUSH EBX
 *  014D46EA   E8 7156F4FF      CALL verethra.01419D60
 *  014D46EF   83C4 28          ADD ESP,0x28
 *  014D46F2   66:0F6EC6        MOVD MM0,ESI
 *  014D46F6   0F5B             ???                                      ; Unknown command
 *  014D46F8   C0FF 75          SAR BH,0x75                              ; Shift constant out of range 1..31
 *  014D46FB   28FF             SUB BH,BH
 *  014D46FD   75 24            JNZ SHORT verethra.014D4723
 *  014D46FF   FF75 1C          PUSH DWORD PTR SS:[EBP+0x1C]
 *  014D4702   FF75 18          PUSH DWORD PTR SS:[EBP+0x18]
 *  014D4705   68 A0956901      PUSH verethra.016995A0
 *  014D470A   83EC 08          SUB ESP,0x8
 *  014D470D   F3:0F114424 04   MOVSS DWORD PTR SS:[ESP+0x4],XMM0
 *  014D4713   F3:0F1045 F0     MOVSS XMM0,DWORD PTR SS:[EBP-0x10]
 *  014D4718   F3:0F110424      MOVSS DWORD PTR SS:[ESP],XMM0
 *  014D471D   FF75 14          PUSH DWORD PTR SS:[EBP+0x14]
 *  014D4720   53               PUSH EBX
 *  014D4721   E8 2AF5FFFF      CALL verethra.014D3C50
 *  014D4726   8B45 10          MOV EAX,DWORD PTR SS:[EBP+0x10]
 *  014D4729   83C4 24          ADD ESP,0x24
 *  014D472C   8B4D E0          MOV ECX,DWORD PTR SS:[EBP-0x20]
 *  014D472F   40               INC EAX
 *  014D4730   F3:0F104D F0     MOVSS XMM1,DWORD PTR SS:[EBP-0x10]
 *  014D4735   83C7 18          ADD EDI,0x18
 *  014D4738   8945 10          MOV DWORD PTR SS:[EBP+0x10],EAX
 *  014D473B   3BC1             CMP EAX,ECX
 *  014D473D  ^0F82 5DFFFFFF    JB verethra.014D46A0
 *  014D4743   8B5D D4          MOV EBX,DWORD PTR SS:[EBP-0x2C]
 *  014D4746   8B55 08          MOV EDX,DWORD PTR SS:[EBP+0x8]
 *  014D4749   8B45 EC          MOV EAX,DWORD PTR SS:[EBP-0x14]
 *  014D474C   8B7D C8          MOV EDI,DWORD PTR SS:[EBP-0x38]
 *  014D474F   8902             MOV DWORD PTR DS:[EDX],EAX
 *  014D4751   8B45 E8          MOV EAX,DWORD PTR SS:[EBP-0x18]
 *  014D4754   8942 04          MOV DWORD PTR DS:[EDX+0x4],EAX
 *  014D4757   8B448F FC        MOV EAX,DWORD PTR DS:[EDI+ECX*4-0x4]
 *  014D475B   0345 E4          ADD EAX,DWORD PTR SS:[EBP-0x1C]
 *  014D475E   8942 08          MOV DWORD PTR DS:[EDX+0x8],EAX
 *  014D4761   8B45 0C          MOV EAX,DWORD PTR SS:[EBP+0xC]
 *  014D4764   8B40 18          MOV EAX,DWORD PTR DS:[EAX+0x18]
 *  014D4767   03C6             ADD EAX,ESI
 *  014D4769   8942 0C          MOV DWORD PTR DS:[EDX+0xC],EAX
 *  014D476C   85DB             TEST EBX,EBX
 *  014D476E   74 46            JE SHORT verethra.014D47B6
 *  014D4770   8B45 D8          MOV EAX,DWORD PTR SS:[EBP-0x28]
 *  014D4773   8BF3             MOV ESI,EBX
 *  014D4775   3BD8             CMP EBX,EAX
 *  014D4777   74 34            JE SHORT verethra.014D47AD
 *  014D4779   8DA424 00000000  LEA ESP,DWORD PTR SS:[ESP]
 *  014D4780   837E 14 08       CMP DWORD PTR DS:[ESI+0x14],0x8
 *  014D4784   72 0D            JB SHORT verethra.014D4793
 *  014D4786   FF36             PUSH DWORD PTR DS:[ESI]
 *  014D4788   E8 48AD0600      CALL verethra.0153F4D5
 *  014D478D   8B45 D8          MOV EAX,DWORD PTR SS:[EBP-0x28]
 *  014D4790   83C4 04          ADD ESP,0x4
 *  014D4793   33C9             XOR ECX,ECX
 *  014D4795   C746 14 07000000 MOV DWORD PTR DS:[ESI+0x14],0x7
 *  014D479C   C746 10 00000000 MOV DWORD PTR DS:[ESI+0x10],0x0
 *  014D47A3   66:890E          MOV WORD PTR DS:[ESI],CX
 *  014D47A6   83C6 18          ADD ESI,0x18
 *  014D47A9   3BF0             CMP ESI,EAX
 *  014D47AB  ^75 D3            JNZ SHORT verethra.014D4780
 *  014D47AD   53               PUSH EBX
 *  014D47AE   E8 22AD0600      CALL verethra.0153F4D5
 *  014D47B3   83C4 04          ADD ESP,0x4
 *  014D47B6   85FF             TEST EDI,EDI
 *  014D47B8   74 09            JE SHORT verethra.014D47C3
 *  014D47BA   57               PUSH EDI
 *  014D47BB   E8 15AD0600      CALL verethra.0153F4D5
 *  014D47C0   83C4 04          ADD ESP,0x4
 *  014D47C3   8B45 08          MOV EAX,DWORD PTR SS:[EBP+0x8]
 *  014D47C6   8B4D F4          MOV ECX,DWORD PTR SS:[EBP-0xC]
 *  014D47C9   64:890D 00000000 MOV DWORD PTR FS:[0],ECX
 *  014D47D0   59               POP ECX
 *  014D47D1   5F               POP EDI
 *  014D47D2   5E               POP ESI
 *  014D47D3   5B               POP EBX
 *  014D47D4   8BE5             MOV ESP,EBP
 *  014D47D6   5D               POP EBP
 *  014D47D7   C3               RETN
 *  014D47D8   CC               INT3
 *  014D47D9   CC               INT3
 *  014D47DA   CC               INT3
 *  014D47DB   CC               INT3
 *  014D47DC   CC               INT3
 *  014D47DD   CC               INT3
 *  014D47DE   CC               INT3
 *  014D47DF   CC               INT3
 *
 *  Sample game: demonion2_trial2 (GXP1)
 *
 *  0108BFFC   CC               INT3
 *  0108BFFD   CC               INT3
 *  0108BFFE   CC               INT3
 *  0108BFFF   CC               INT3
 *  0108C000   6A FF            PUSH -0x1
 *  0108C002   68 003D1501      PUSH demonion.01153D00
 *  0108C007   64:A1 00000000   MOV EAX,DWORD PTR FS:[0]
 *  0108C00D   50               PUSH EAX
 *  0108C00E   83EC 44          SUB ESP,0x44
 *  0108C011   53               PUSH EBX
 *  0108C012   55               PUSH EBP
 *  0108C013   56               PUSH ESI
 *  0108C014   57               PUSH EDI
 *  0108C015   A1 90AA2401      MOV EAX,DWORD PTR DS:[0x124AA90]
 *  0108C01A   33C4             XOR EAX,ESP
 *  0108C01C   50               PUSH EAX
 *  0108C01D   8D4424 58        LEA EAX,DWORD PTR SS:[ESP+0x58]
 *  0108C021   64:A3 00000000   MOV DWORD PTR FS:[0],EAX
 *  0108C027   8B4424 74        MOV EAX,DWORD PTR SS:[ESP+0x74]
 *  0108C02B   8B48 04          MOV ECX,DWORD PTR DS:[EAX+0x4]
 *  0108C02E   8B38             MOV EDI,DWORD PTR DS:[EAX]
 *  0108C030   8B40 08          MOV EAX,DWORD PTR DS:[EAX+0x8]
 *  0108C033   894C24 20        MOV DWORD PTR SS:[ESP+0x20],ECX
 *  0108C037   2BC7             SUB EAX,EDI
 *  0108C039   8D4C24 28        LEA ECX,DWORD PTR SS:[ESP+0x28]
 *  0108C03D   897C24 1C        MOV DWORD PTR SS:[ESP+0x1C],EDI
 *  0108C041   894424 18        MOV DWORD PTR SS:[ESP+0x18],EAX
 *  0108C045   E8 16ACE3FF      CALL demonion.00EC6C60
 *  0108C04A   33DB             XOR EBX,EBX
 *  0108C04C   6A 04            PUSH 0x4
 *  0108C04E   8D4C24 2C        LEA ECX,DWORD PTR SS:[ESP+0x2C]
 *  0108C052   895C24 64        MOV DWORD PTR SS:[ESP+0x64],EBX
 *  0108C056   E8 D59AE7FF      CALL demonion.00F05B30
 *  0108C05B   8D4C24 40        LEA ECX,DWORD PTR SS:[ESP+0x40]
 *  0108C05F   E8 FCABE3FF      CALL demonion.00EC6C60
 *  0108C064   6A 04            PUSH 0x4
 *  0108C066   8D4C24 44        LEA ECX,DWORD PTR SS:[ESP+0x44]
 *  0108C06A   C64424 64 01     MOV BYTE PTR SS:[ESP+0x64],0x1
 *  0108C06F   E8 6C20E6FF      CALL demonion.00EEE0E0
 *  0108C074   8B4424 70        MOV EAX,DWORD PTR SS:[ESP+0x70]
 *  0108C078   33F6             XOR ESI,ESI
 *  0108C07A   8BE8             MOV EBP,EAX
 *  0108C07C   896C24 70        MOV DWORD PTR SS:[ESP+0x70],EBP
 *  0108C080   66:3918          CMP WORD PTR DS:[EAX],BX
 *  0108C083   0F84 84010000    JE demonion.0108C20D
 *  0108C089   BF 01000000      MOV EDI,0x1
 *  0108C08E   895C24 74        MOV DWORD PTR SS:[ESP+0x74],EBX
 *  0108C092   897C24 14        MOV DWORD PTR SS:[ESP+0x14],EDI
 *  0108C096   EB 08            JMP SHORT demonion.0108C0A0
 *  0108C098   8DA424 00000000  LEA ESP,DWORD PTR SS:[ESP]
 *  0108C09F   90               NOP
 *  0108C0A0   8B4C24 50        MOV ECX,DWORD PTR SS:[ESP+0x50]
 *  0108C0A4   2B4C24 4C        SUB ECX,DWORD PTR SS:[ESP+0x4C]
 *  0108C0A8   B8 93244992      MOV EAX,0x92492493
 *  0108C0AD   F7E9             IMUL ECX
 *  0108C0AF   03D1             ADD EDX,ECX
 *  0108C0B1   C1FA 04          SAR EDX,0x4
 *  0108C0B4   8BC2             MOV EAX,EDX
 *  0108C0B6   C1E8 1F          SHR EAX,0x1F
 *  0108C0B9   03C2             ADD EAX,EDX
 *  0108C0BB   3BC6             CMP EAX,ESI
 *  0108C0BD   77 27            JA SHORT demonion.0108C0E6
 *  0108C0BF   83EC 1C          SUB ESP,0x1C
 *  0108C0C2   8BC4             MOV EAX,ESP
 *  0108C0C4   33C9             XOR ECX,ECX
 *  0108C0C6   C740 18 07000000 MOV DWORD PTR DS:[EAX+0x18],0x7
 *  0108C0CD   C740 14 00000000 MOV DWORD PTR DS:[EAX+0x14],0x0
 *  0108C0D4   896424 40        MOV DWORD PTR SS:[ESP+0x40],ESP
 *  0108C0D8   66:8948 04       MOV WORD PTR DS:[EAX+0x4],CX
 *  0108C0DC   57               PUSH EDI
 *  0108C0DD   8D4C24 60        LEA ECX,DWORD PTR SS:[ESP+0x60]
 *  0108C0E1   E8 BAF9FFFF      CALL demonion.0108BAA0
 *  0108C0E6   8B5424 38        MOV EDX,DWORD PTR SS:[ESP+0x38]
 *  0108C0EA   2B5424 34        SUB EDX,DWORD PTR SS:[ESP+0x34]
 *  0108C0EE   C1FA 02          SAR EDX,0x2
 *  0108C0F1   3BD6             CMP EDX,ESI
 *  0108C0F3   77 0C            JA SHORT demonion.0108C101
 *  0108C0F5   6A 00            PUSH 0x0
 *  0108C0F7   57               PUSH EDI
 *  0108C0F8   8D4C24 30        LEA ECX,DWORD PTR SS:[ESP+0x30]
 *  0108C0FC   E8 0FA9E7FF      CALL demonion.00F06A10
 *  0108C101   0FB745 00        MOVZX EAX,WORD PTR SS:[EBP]
 *  0108C105   66:3B8424 880000>CMP AX,WORD PTR SS:[ESP+0x88]
 *  0108C10D   75 19            JNZ SHORT demonion.0108C128
 *  0108C10F   834424 74 1C     ADD DWORD PTR SS:[ESP+0x74],0x1C
 *  0108C114   47               INC EDI
 *  0108C115   33DB             XOR EBX,EBX
 *  0108C117   46               INC ESI
 *  0108C118   83C5 02          ADD EBP,0x2
 *  0108C11B   897C24 14        MOV DWORD PTR SS:[ESP+0x14],EDI
 *  0108C11F   896C24 70        MOV DWORD PTR SS:[ESP+0x70],EBP
 *  0108C123   E9 D4000000      JMP demonion.0108C1FC
 *  0108C128   8B6C24 6C        MOV EBP,DWORD PTR SS:[ESP+0x6C]
 *  0108C12C   8B7D 44          MOV EDI,DWORD PTR SS:[EBP+0x44]
 *  0108C12F   50               PUSH EAX
 *  0108C130   E8 1B200000      CALL demonion.0108E150
 *  0108C135   0FAFC7           IMUL EAX,EDI
 *  0108C138   8B4C24 54        MOV ECX,DWORD PTR SS:[ESP+0x54]
 *  0108C13C   2B4C24 50        SUB ECX,DWORD PTR SS:[ESP+0x50]
 *  0108C140   99               CDQ
 *  0108C141   2BC2             SUB EAX,EDX
 *  0108C143   D1F8             SAR EAX,1
 *  0108C145   03D8             ADD EBX,EAX
 *  0108C147   B8 93244992      MOV EAX,0x92492493
 *  0108C14C   F7E9             IMUL ECX
 *  0108C14E   03D1             ADD EDX,ECX
 *  0108C150   C1FA 04          SAR EDX,0x4
 *  0108C153   8BC2             MOV EAX,EDX
 *  0108C155   C1E8 1F          SHR EAX,0x1F
 *  0108C158   03C2             ADD EAX,EDX
 *  0108C15A   83C4 04          ADD ESP,0x4
 *  0108C15D   3BF0             CMP ESI,EAX
 *  0108C15F   72 05            JB SHORT demonion.0108C166
 *  0108C161   E8 CB0D0900      CALL demonion.0111CF31
 *  0108C166   8B4C24 70        MOV ECX,DWORD PTR SS:[ESP+0x70]
 *  0108C16A   0FB711           MOVZX EDX,WORD PTR DS:[ECX]
 *  0108C16D   8B4424 74        MOV EAX,DWORD PTR SS:[ESP+0x74]
 *  0108C171   8B4C24 4C        MOV ECX,DWORD PTR SS:[ESP+0x4C]
 *  0108C175   52               PUSH EDX
 *  0108C176   6A 01            PUSH 0x1
 *  0108C178   03C8             ADD ECX,EAX
 *  0108C17A   E8 316CECFF      CALL demonion.00F52DB0
 *  0108C17F   8B4C24 38        MOV ECX,DWORD PTR SS:[ESP+0x38]
 *  0108C183   8B4424 34        MOV EAX,DWORD PTR SS:[ESP+0x34]
 *  0108C187   8BD1             MOV EDX,ECX
 *  0108C189   2BD0             SUB EDX,EAX
 *  0108C18B   C1FA 02          SAR EDX,0x2
 *  0108C18E   3BF2             CMP ESI,EDX
 *  0108C190   72 0D            JB SHORT demonion.0108C19F
 *  0108C192   E8 9A0D0900      CALL demonion.0111CF31
 *  0108C197   8B4C24 38        MOV ECX,DWORD PTR SS:[ESP+0x38]
 *  0108C19B   8B4424 34        MOV EAX,DWORD PTR SS:[ESP+0x34]
 *  0108C19F   391CB0           CMP DWORD PTR DS:[EAX+ESI*4],EBX
 *  0108C1A2   7E 1D            JLE SHORT demonion.0108C1C1
 *  0108C1A4   8BD1             MOV EDX,ECX
 *  0108C1A6   2BD0             SUB EDX,EAX
 *  0108C1A8   C1FA 02          SAR EDX,0x2
 *  0108C1AB   3BF2             CMP ESI,EDX
 *  0108C1AD   72 0D            JB SHORT demonion.0108C1BC
 *  0108C1AF   E8 7D0D0900      CALL demonion.0111CF31
 *  0108C1B4   8B4C24 38        MOV ECX,DWORD PTR SS:[ESP+0x38]
 *  0108C1B8   8B4424 34        MOV EAX,DWORD PTR SS:[ESP+0x34]
 *  0108C1BC   8B3CB0           MOV EDI,DWORD PTR DS:[EAX+ESI*4]
 *  0108C1BF   EB 02            JMP SHORT demonion.0108C1C3
 *  0108C1C1   8BFB             MOV EDI,EBX
 *  0108C1C3   2BC8             SUB ECX,EAX
 *  0108C1C5   C1F9 02          SAR ECX,0x2
 *  0108C1C8   3BF1             CMP ESI,ECX
 *  0108C1CA   72 09            JB SHORT demonion.0108C1D5
 *  0108C1CC   E8 600D0900      CALL demonion.0111CF31
 *  0108C1D1   8B4424 34        MOV EAX,DWORD PTR SS:[ESP+0x34]
 *  0108C1D5   893CB0           MOV DWORD PTR DS:[EAX+ESI*4],EDI
 *  0108C1D8   8B45 44          MOV EAX,DWORD PTR SS:[EBP+0x44]
 *  0108C1DB   03C3             ADD EAX,EBX
 *  0108C1DD   3B4424 18        CMP EAX,DWORD PTR SS:[ESP+0x18]
 *  0108C1E1   7C 0C            JL SHORT demonion.0108C1EF
 *  0108C1E3   FF4424 14        INC DWORD PTR SS:[ESP+0x14]
 *  0108C1E7   33DB             XOR EBX,EBX
 *  0108C1E9   46               INC ESI
 *  0108C1EA   834424 74 1C     ADD DWORD PTR SS:[ESP+0x74],0x1C
 *  0108C1EF   834424 70 02     ADD DWORD PTR SS:[ESP+0x70],0x2
 *  0108C1F4   8B7C24 14        MOV EDI,DWORD PTR SS:[ESP+0x14]
 *  0108C1F8   8B6C24 70        MOV EBP,DWORD PTR SS:[ESP+0x70]
 *  0108C1FC   66:837D 00 00    CMP WORD PTR SS:[EBP],0x0
 *  0108C201  ^0F85 99FEFFFF    JNZ demonion.0108C0A0
 *  0108C207   8B7C24 1C        MOV EDI,DWORD PTR SS:[ESP+0x1C]
 *  0108C20B   33DB             XOR EBX,EBX
 *  0108C20D   8B4C24 50        MOV ECX,DWORD PTR SS:[ESP+0x50]
 *  0108C211   2B4C24 4C        SUB ECX,DWORD PTR SS:[ESP+0x4C]
 *  0108C215   B8 93244992      MOV EAX,0x92492493
 *  0108C21A   F7E9             IMUL ECX
 *  0108C21C   03D1             ADD EDX,ECX
 *  0108C21E   C1FA 04          SAR EDX,0x4
 *  0108C221   8BC2             MOV EAX,EDX
 *  0108C223   C1E8 1F          SHR EAX,0x1F
 *  0108C226   03C2             ADD EAX,EDX
 *  0108C228   75 3E            JNZ SHORT demonion.0108C268
 *  0108C22A   8B7424 68        MOV ESI,DWORD PTR SS:[ESP+0x68]
 *  0108C22E   8B4424 20        MOV EAX,DWORD PTR SS:[ESP+0x20]
 *  0108C232   8D4C24 40        LEA ECX,DWORD PTR SS:[ESP+0x40]
 *  0108C236   893E             MOV DWORD PTR DS:[ESI],EDI
 *  0108C238   8946 04          MOV DWORD PTR DS:[ESI+0x4],EAX
 *  0108C23B   897E 08          MOV DWORD PTR DS:[ESI+0x8],EDI
 *  0108C23E   8946 0C          MOV DWORD PTR DS:[ESI+0xC],EAX
 *  0108C241   E8 FAA8E3FF      CALL demonion.00EC6B40
 *  0108C246   8B4424 34        MOV EAX,DWORD PTR SS:[ESP+0x34]
 *  0108C24A   3BC3             CMP EAX,EBX
 *  0108C24C   74 09            JE SHORT demonion.0108C257
 *  0108C24E   50               PUSH EAX
 *  0108C24F   E8 30050900      CALL demonion.0111C784
 *  0108C254   83C4 04          ADD ESP,0x4
 *  0108C257   895C24 34        MOV DWORD PTR SS:[ESP+0x34],EBX
 *  0108C25B   895C24 38        MOV DWORD PTR SS:[ESP+0x38],EBX
 *  0108C25F   895C24 3C        MOV DWORD PTR SS:[ESP+0x3C],EBX
 *  0108C263   E9 0E020000      JMP demonion.0108C476
 *  0108C268   8D48 FF          LEA ECX,DWORD PTR DS:[EAX-0x1]
 *  0108C26B   3BC8             CMP ECX,EAX
 *  0108C26D   72 05            JB SHORT demonion.0108C274
 *  0108C26F   E8 BD0C0900      CALL demonion.0111CF31
 *  0108C274   8B4C24 50        MOV ECX,DWORD PTR SS:[ESP+0x50]
 *  0108C278   2B4C24 4C        SUB ECX,DWORD PTR SS:[ESP+0x4C]
 *  0108C27C   B8 93244992      MOV EAX,0x92492493
 *  0108C281   F7E9             IMUL ECX
 *  0108C283   03D1             ADD EDX,ECX
 *  0108C285   C1FA 04          SAR EDX,0x4
 *  0108C288   8BC2             MOV EAX,EDX
 *  0108C28A   C1E8 1F          SHR EAX,0x1F
 *  0108C28D   33FF             XOR EDI,EDI
 *  0108C28F   33F6             XOR ESI,ESI
 *  0108C291   03C2             ADD EAX,EDX
 *  0108C293   0F84 F2000000    JE demonion.0108C38B
 *  0108C299   33ED             XOR EBP,EBP
 *  0108C29B   8B4424 38        MOV EAX,DWORD PTR SS:[ESP+0x38]
 *  0108C29F   2B4424 34        SUB EAX,DWORD PTR SS:[ESP+0x34]
 *  0108C2A3   C1F8 02          SAR EAX,0x2
 *  0108C2A6   3BF0             CMP ESI,EAX
 *  0108C2A8   72 05            JB SHORT demonion.0108C2AF
 *  0108C2AA   E8 820C0900      CALL demonion.0111CF31
 *  0108C2AF   8B4C24 34        MOV ECX,DWORD PTR SS:[ESP+0x34]
 *  0108C2B3   8B4424 18        MOV EAX,DWORD PTR SS:[ESP+0x18]
 *  0108C2B7   2B04B1           SUB EAX,DWORD PTR DS:[ECX+ESI*4]
 *  0108C2BA   8B4C24 50        MOV ECX,DWORD PTR SS:[ESP+0x50]
 *  0108C2BE   2B4C24 4C        SUB ECX,DWORD PTR SS:[ESP+0x4C]
 *  0108C2C2   99               CDQ
 *  0108C2C3   2BC2             SUB EAX,EDX
 *  0108C2C5   8B5424 6C        MOV EDX,DWORD PTR SS:[ESP+0x6C]
 *  0108C2C9   8B7A 44          MOV EDI,DWORD PTR DS:[EDX+0x44]
 *  0108C2CC   8BD8             MOV EBX,EAX
 *  0108C2CE   0FAFFE           IMUL EDI,ESI
 *  0108C2D1   037C24 20        ADD EDI,DWORD PTR SS:[ESP+0x20]
 *  0108C2D5   B8 93244992      MOV EAX,0x92492493
 *  0108C2DA   F7E9             IMUL ECX
 *  0108C2DC   03D1             ADD EDX,ECX
 *  0108C2DE   C1FA 04          SAR EDX,0x4
 *  0108C2E1   8BC2             MOV EAX,EDX
 *  0108C2E3   D1FB             SAR EBX,1
 *  0108C2E5   035C24 1C        ADD EBX,DWORD PTR SS:[ESP+0x1C]
 *  0108C2E9   C1E8 1F          SHR EAX,0x1F
 *  0108C2EC   03C2             ADD EAX,EDX
 *  0108C2EE   895C24 70        MOV DWORD PTR SS:[ESP+0x70],EBX
 *  0108C2F2   897C24 74        MOV DWORD PTR SS:[ESP+0x74],EDI
 *  0108C2F6   3BF0             CMP ESI,EAX
 *  0108C2F8   72 05            JB SHORT demonion.0108C2FF
 *  0108C2FA   E8 320C0900      CALL demonion.0111CF31
 *  0108C2FF   8B4424 4C        MOV EAX,DWORD PTR SS:[ESP+0x4C]
 *  0108C303   837C28 18 08     CMP DWORD PTR DS:[EAX+EBP+0x18],0x8
 *  0108C308   72 06            JB SHORT demonion.0108C310
 *  0108C30A   8B4428 04        MOV EAX,DWORD PTR DS:[EAX+EBP+0x4]
 *  0108C30E   EB 04            JMP SHORT demonion.0108C314
 *  0108C310   8D4428 04        LEA EAX,DWORD PTR DS:[EAX+EBP+0x4]
 *  0108C314   8B8C24 88000000  MOV ECX,DWORD PTR SS:[ESP+0x88]
 *  0108C31B   DB4424 74        FILD DWORD PTR SS:[ESP+0x74]
 *  0108C31F   8B9424 84000000  MOV EDX,DWORD PTR SS:[ESP+0x84]
 *  0108C326   51               PUSH ECX
 *  0108C327   8B8C24 84000000  MOV ECX,DWORD PTR SS:[ESP+0x84]
 *  0108C32E   52               PUSH EDX
 *  0108C32F   8B9424 84000000  MOV EDX,DWORD PTR SS:[ESP+0x84]
 *  0108C336   51               PUSH ECX
 *  0108C337   8B8C24 84000000  MOV ECX,DWORD PTR SS:[ESP+0x84]
 *  0108C33E   52               PUSH EDX
 *  0108C33F   8B5424 7C        MOV EDX,DWORD PTR SS:[ESP+0x7C]
 *  0108C343   51               PUSH ECX
 *  0108C344   68 88C92701      PUSH demonion.0127C988
 *  0108C349   83EC 08          SUB ESP,0x8
 *  0108C34C   D95C24 04        FSTP DWORD PTR SS:[ESP+0x4]
 *  0108C350   DB8424 90000000  FILD DWORD PTR SS:[ESP+0x90]
 *  0108C357   D91C24           FSTP DWORD PTR SS:[ESP]
 *  0108C35A   50               PUSH EAX
 *  0108C35B   52               PUSH EDX
 *  0108C35C   E8 EFE3E4FF      CALL demonion.00EDA750
 *  0108C361   8B4C24 78        MOV ECX,DWORD PTR SS:[ESP+0x78]
 *  0108C365   2B4C24 74        SUB ECX,DWORD PTR SS:[ESP+0x74]
 *  0108C369   B8 93244992      MOV EAX,0x92492493
 *  0108C36E   F7E9             IMUL ECX
 *  0108C370   03D1             ADD EDX,ECX
 *  0108C372   C1FA 04          SAR EDX,0x4
 *  0108C375   8BC2             MOV EAX,EDX
 *  0108C377   C1E8 1F          SHR EAX,0x1F
 *  0108C37A   46               INC ESI
 *  0108C37B   03C2             ADD EAX,EDX
 *  0108C37D   83C4 28          ADD ESP,0x28
 *  0108C380   83C5 1C          ADD EBP,0x1C
 *  0108C383   3BF0             CMP ESI,EAX
 *  0108C385  ^0F82 10FFFFFF    JB demonion.0108C29B
 *  0108C38B   8B4C24 6C        MOV ECX,DWORD PTR SS:[ESP+0x6C]
 *  0108C38F   8B69 44          MOV EBP,DWORD PTR DS:[ECX+0x44]
 *  0108C392   8B4C24 50        MOV ECX,DWORD PTR SS:[ESP+0x50]
 *  0108C396   2B4C24 4C        SUB ECX,DWORD PTR SS:[ESP+0x4C]
 *  0108C39A   B8 93244992      MOV EAX,0x92492493
 *  0108C39F   F7E9             IMUL ECX
 *  0108C3A1   03D1             ADD EDX,ECX
 *  0108C3A3   8B4C24 34        MOV ECX,DWORD PTR SS:[ESP+0x34]
 *  0108C3A7   C1FA 04          SAR EDX,0x4
 *  0108C3AA   8BC2             MOV EAX,EDX
 *  0108C3AC   C1E8 1F          SHR EAX,0x1F
 *  0108C3AF   8D7402 FF        LEA ESI,DWORD PTR DS:[EDX+EAX-0x1]
 *  0108C3B3   8B4424 38        MOV EAX,DWORD PTR SS:[ESP+0x38]
 *  0108C3B7   8BD0             MOV EDX,EAX
 *  0108C3B9   2BD1             SUB EDX,ECX
 *  0108C3BB   C1FA 02          SAR EDX,0x2
 *  0108C3BE   3BF2             CMP ESI,EDX
 *  0108C3C0   72 0D            JB SHORT demonion.0108C3CF
 *  0108C3C2   E8 6A0B0900      CALL demonion.0111CF31
 *  0108C3C7   8B4C24 34        MOV ECX,DWORD PTR SS:[ESP+0x34]
 *  0108C3CB   8B4424 38        MOV EAX,DWORD PTR SS:[ESP+0x38]
 *  0108C3CF   2BC1             SUB EAX,ECX
 *  0108C3D1   C1F8 02          SAR EAX,0x2
 *  0108C3D4   8D14B1           LEA EDX,DWORD PTR DS:[ECX+ESI*4]
 *  0108C3D7   895424 74        MOV DWORD PTR SS:[ESP+0x74],EDX
 *  0108C3DB   85C0             TEST EAX,EAX
 *  0108C3DD   77 09            JA SHORT demonion.0108C3E8
 *  0108C3DF   E8 4D0B0900      CALL demonion.0111CF31
 *  0108C3E4   8B4C24 34        MOV ECX,DWORD PTR SS:[ESP+0x34]
 *  0108C3E8   8B4424 18        MOV EAX,DWORD PTR SS:[ESP+0x18]
 *  0108C3EC   2B01             SUB EAX,DWORD PTR DS:[ECX]
 *  0108C3EE   8B7424 68        MOV ESI,DWORD PTR SS:[ESP+0x68]
 *  0108C3F2   8B4C24 74        MOV ECX,DWORD PTR SS:[ESP+0x74]
 *  0108C3F6   99               CDQ
 *  0108C3F7   2BC2             SUB EAX,EDX
 *  0108C3F9   8B11             MOV EDX,DWORD PTR DS:[ECX]
 *  0108C3FB   D1F8             SAR EAX,1
 *  0108C3FD   034424 1C        ADD EAX,DWORD PTR SS:[ESP+0x1C]
 *  0108C401   03EF             ADD EBP,EDI
 *  0108C403   8906             MOV DWORD PTR DS:[ESI],EAX
 *  0108C405   8B4424 20        MOV EAX,DWORD PTR SS:[ESP+0x20]
 *  0108C409   8946 04          MOV DWORD PTR DS:[ESI+0x4],EAX
 *  0108C40C   8B4424 4C        MOV EAX,DWORD PTR SS:[ESP+0x4C]
 *  0108C410   03D3             ADD EDX,EBX
 *  0108C412   33FF             XOR EDI,EDI
 *  0108C414   8956 08          MOV DWORD PTR DS:[ESI+0x8],EDX
 *  0108C417   896E 0C          MOV DWORD PTR DS:[ESI+0xC],EBP
 *  0108C41A   3BC7             CMP EAX,EDI
 *  0108C41C   74 22            JE SHORT demonion.0108C440
 *  0108C41E   8B4C24 74        MOV ECX,DWORD PTR SS:[ESP+0x74]
 *  0108C422   51               PUSH ECX
 *  0108C423   8B4C24 54        MOV ECX,DWORD PTR SS:[ESP+0x54]
 *  0108C427   8D5424 4C        LEA EDX,DWORD PTR SS:[ESP+0x4C]
 *  0108C42B   52               PUSH EDX
 *  0108C42C   51               PUSH ECX
 *  0108C42D   50               PUSH EAX
 *  0108C42E   E8 ADA6E3FF      CALL demonion.00EC6AE0
 *  0108C433   8B5424 5C        MOV EDX,DWORD PTR SS:[ESP+0x5C]
 *  0108C437   52               PUSH EDX
 *  0108C438   E8 47030900      CALL demonion.0111C784
 *  0108C43D   83C4 14          ADD ESP,0x14
 *  0108C440   8B4424 40        MOV EAX,DWORD PTR SS:[ESP+0x40]
 *  0108C444   50               PUSH EAX
 *  0108C445   897C24 50        MOV DWORD PTR SS:[ESP+0x50],EDI
 *  0108C449   897C24 54        MOV DWORD PTR SS:[ESP+0x54],EDI
 *  0108C44D   897C24 58        MOV DWORD PTR SS:[ESP+0x58],EDI
 *  0108C451   E8 2E030900      CALL demonion.0111C784
 *  0108C456   8B4424 38        MOV EAX,DWORD PTR SS:[ESP+0x38]
 *  0108C45A   83C4 04          ADD ESP,0x4
 *  0108C45D   3BC7             CMP EAX,EDI
 *  0108C45F   74 09            JE SHORT demonion.0108C46A
 *  0108C461   50               PUSH EAX
 *  0108C462   E8 1D030900      CALL demonion.0111C784
 *  0108C467   83C4 04          ADD ESP,0x4
 *  0108C46A   897C24 34        MOV DWORD PTR SS:[ESP+0x34],EDI
 *  0108C46E   897C24 38        MOV DWORD PTR SS:[ESP+0x38],EDI
 *  0108C472   897C24 3C        MOV DWORD PTR SS:[ESP+0x3C],EDI
 *  0108C476   8B4C24 28        MOV ECX,DWORD PTR SS:[ESP+0x28]
 *  0108C47A   51               PUSH ECX
 *  0108C47B   E8 04030900      CALL demonion.0111C784
 *  0108C480   8BC6             MOV EAX,ESI
 *  0108C482   83C4 04          ADD ESP,0x4
 *  0108C485   8B4C24 58        MOV ECX,DWORD PTR SS:[ESP+0x58]
 *  0108C489   64:890D 00000000 MOV DWORD PTR FS:[0],ECX
 *  0108C490   59               POP ECX
 *  0108C491   5F               POP EDI
 *  0108C492   5E               POP ESI
 *  0108C493   5D               POP EBP
 *  0108C494   5B               POP EBX
 *  0108C495   83C4 50          ADD ESP,0x50
 *  0108C498   C3               RETN
 *  0108C499   CC               INT3
 *  0108C49A   CC               INT3
 *  0108C49B   CC               INT3
 *  0108C49C   CC               INT3
 *  0108C49D   CC               INT3
 *  0108C49E   CC               INT3
 */
bool attach(ulong startAddress, ulong stopAddress)
{
  const uint8_t bytes[] = {
    0x99,           // 014d45ae   99               cdq
    0x2b,0xc2,      // 014d45af   2bc2             sub eax,edx
    0xd1,0xf8,      // 014d45b1   d1f8             sar eax,1
    0x03 //,0xf0,   // 014d45b3   03f0             add esi,eax
  };
  int count = 0;
  auto fun = [&count](ulong addr) -> bool {
    count +=
        (addr = MemDbg::findEnclosingAlignedFunction(addr))
        && winhook::hook_before(addr, Private::hookBefore);
    return true;
  };
  MemDbg::iterFindBytes(fun, bytes, sizeof(bytes), startAddress, stopAddress);
  DOUT("call number =" << count);
  return count;
}
} // namespace OtherHook
} // unnamed namespace

/** Public class */

bool GXPEngine::attach()
{
  ulong startAddress, stopAddress;
  if (!Engine::getProcessMemoryRange(&startAddress, &stopAddress))
    return false;
  moduleBaseAddress_ = startAddress; // used to calculate reladdr for debug purposes
  if (ScenarioHook2::attach(startAddress, stopAddress)) {
    DOUT("found GXP2");
  } else if (ScenarioHook1::attach(startAddress, stopAddress)) {
    DOUT("found GXP1");
    if (PopupHook1::attach(startAddress, stopAddress))
      DOUT("popup text found");
    else
      DOUT("popup text NOT FOUND");
  } else
    return false;
  if (OtherHook::attach(startAddress, stopAddress))
    DOUT("other text found");
  else
    DOUT("other text NOT FOUND");
  //HijackManager::instance()->attachFunction((ulong)::GetGlyphOutlineW);
  return true;
}

/**
 *  FIXME: Figure out ruby syntax
 *  Guessed ruby syntax: ≪rb／rt≫, which would however crash the game.
 *  The above syntax might also work for YU-RIS engine.
 */
QString GXPEngine::rubyCreate(const QString &rb, const QString &rt)
{
  static QString fmt = QString::fromWCharArray(L"\x226a%1\xff0f%2\x226b");
  return fmt.arg(rb, rt);
}

// Remove furigana in scenario thread.
QString GXPEngine::rubyRemove(const QString &text)
{
  if (!text.contains((wchar_t)0x226a))
    return text;
  static QRegExp rx(QString::fromWCharArray(L"\x226a(.+)\xff0f.+\x226b"));
  if (!rx.isMinimal())
    rx.setMinimal(true);
  return QString(text).replace(rx, "\\1");
}

// EOF

#if 0
namespace DebugHook {
namespace Private {
  bool hookBefore(winhook::hook_stack *s)
  {
    static QString text_;
    auto text = (LPCWSTR)s->stack[1]; // arg1
    if (!text || !*text || text[0] <= 127)
      return true;
    auto retaddr = s->stack[0];
    auto reladdr = retaddr - moduleBaseAddress_;
    if (reladdr == 0x25660 || reladdr == 0x28301)
      return true;
    auto role = Engine::OtherRole;
    QString oldText = QString::fromWCharArray(text),
            newText = EngineController::instance()->dispatchTextW(oldText, role, reladdr);
    if (newText.isEmpty() || oldText == newText)
      return true;
    text_ = newText;
    s->stack[1] = (ulong)text_.utf16();
    return true;
  }
} // Private
/**
 *  Sample game: 塔の下のエクセルキトゥス体験版
 *  Executable description shows "AVGEngineV2"
 *
 *  This is the memcpy function.
 *
 *  arg1: target text
 *  arg2: source tex
 *  arg3: size
 *
 *  00A3F8CB     CC             INT3
 *  00A3F8CC     CC             INT3
 *  00A3F8CD     CC             INT3
 *  00A3F8CE     CC             INT3
 *  00A3F8CF     CC             INT3
 *  00A3F8D0   $ 57             PUSH EDI
 *  00A3F8D1   . 56             PUSH ESI
 *  00A3F8D2   . 8B7424 10      MOV ESI,DWORD PTR SS:[ESP+0x10]
 *  00A3F8D6   . 8B4C24 14      MOV ECX,DWORD PTR SS:[ESP+0x14]
 *  00A3F8DA   . 8B7C24 0C      MOV EDI,DWORD PTR SS:[ESP+0xC]
 *  00A3F8DE   . 8BC1           MOV EAX,ECX
 *  00A3F8E0   . 8BD1           MOV EDX,ECX
 *  00A3F8E2   . 03C6           ADD EAX,ESI
 *  00A3F8E4   . 3BFE           CMP EDI,ESI
 *  00A3F8E6   . 76 08          JBE SHORT play.00A3F8F0
 *  00A3F8E8   . 3BF8           CMP EDI,EAX
 *  00A3F8EA   . 0F82 68030000  JB play.00A3FC58
 *  00A3F8F0   > 0FBA25 581FBC0>BT DWORD PTR DS:[0xBC1F58],0x1
 *  00A3F8F8   . 73 07          JNB SHORT play.00A3F901
 *  00A3F8FA   . F3:A4          REP MOVS BYTE PTR ES:[EDI],BYTE PTR DS:[ESI]	; jichi: here
 *  00A3F8FC   . E9 17030000    JMP play.00A3FC18
 *  00A3F901   > 81F9 80000000  CMP ECX,0x80
 *  00A3F907   . 0F82 CE010000  JB play.00A3FADB
 *  00A3F90D   . 8BC7           MOV EAX,EDI
 *  00A3F90F   . 33C6           XOR EAX,ESI
 *  00A3F911   . A9 0F000000    TEST EAX,0xF
 *  00A3F916   . 75 0E          JNZ SHORT play.00A3F926
 *  00A3F918   . 0FBA25 3060B90>BT DWORD PTR DS:[0xB96030],0x1
 *  00A3F920   . 0F82 DA040000  JB play.00A3FE00
 *  00A3F926   > 0FBA25 581FBC0>BT DWORD PTR DS:[0xBC1F58],0x0
 *  00A3F92E   . 0F83 A7010000  JNB play.00A3FADB
 *  00A3F934   . F7C7 03000000  TEST EDI,0x3
 *  00A3F93A   . 0F85 B8010000  JNZ play.00A3FAF8
 *  00A3F940   . F7C6 03000000  TEST ESI,0x3
 *  00A3F946   . 0F85 97010000  JNZ play.00A3FAE3
 *  00A3F94C   . 0FBAE7 02      BT EDI,0x2
 *  00A3F950   . 73 0D          JNB SHORT play.00A3F95F
 *  00A3F952   . 8B06           MOV EAX,DWORD PTR DS:[ESI]
 *  00A3F954   . 83E9 04        SUB ECX,0x4
 *  00A3F957   . 8D76 04        LEA ESI,DWORD PTR DS:[ESI+0x4]
 *  00A3F95A   . 8907           MOV DWORD PTR DS:[EDI],EAX
 *  00A3F95C   . 8D7F 04        LEA EDI,DWORD PTR DS:[EDI+0x4]
 *  00A3F95F   > 0FBAE7 03      BT EDI,0x3
 *  00A3F963   . 73 11          JNB SHORT play.00A3F976
 *  00A3F965   . F3:            PREFIX REP:                              ;  Superfluous prefix
 *  00A3F966   . 0F7E0E         MOVD DWORD PTR DS:[ESI],MM1
 *  00A3F969   . 83E9 08        SUB ECX,0x8
 *  00A3F96C   . 8D76 08        LEA ESI,DWORD PTR DS:[ESI+0x8]
 *  00A3F96F     66             DB 66                                    ;  CHAR 'f'
 *  00A3F970     0F             DB 0F
 *  00A3F971     D6             DB D6
 *  00A3F972     0F             DB 0F
 */
bool attach(ulong startAddress, ulong stopAddress)
{
  /*
  // There are two exact the same functions
  // The last function is hooked.
  // It seems the functions are generated by inlining
  const uint8_t bytes[] = {
    0x57,                 // 00a3f8d0   $ 57             push edi
    0x56,                 // 00a3f8d1   . 56             push esi
    0x8b,0x74,0x24, 0x10, // 00a3f8d2   . 8b7424 10      mov esi,dword ptr ss:[esp+0x10]
    0x8b,0x4c,0x24, 0x14, // 00a3f8d6   . 8b4c24 14      mov ecx,dword ptr ss:[esp+0x14]
    0x8b,0x7c,0x24, 0x0c  // 00a3f8da   . 8b7c24 0c      mov edi,dword ptr ss:[esp+0xc]
  };
  ulong lastCall = 0;
  auto fun = [&lastCall](ulong addr) -> bool {
    //if (lastCall)
    lastCall = addr;
    return true;
  };
  MemDbg::iterFindBytes(fun, bytes, sizeof(bytes), startAddress, stopAddress);
  return lastCall && winhook::hook_before(lastCall, Private::hookBefore);
  */

  const uint8_t bytes[] = {
    0x8b,0xf1,                              // 001d45e9  |. 8bf1                mov esi,ecx
    0xc7,0x46, 0x14, 0x07,0x00,0x00,0x00,   // 001d45eb  |. c746 14 07000000    mov dword ptr ds:[esi+0x14],0x7
    0xc7,0x46, 0x10, 0x00,0x00,0x00,0x00,   // 001d45f2  |. c746 10 00000000    mov dword ptr ds:[esi+0x10],0x0
    0x66,0x89,0x06,                         // 001d45f9  |. 66:8906             mov word ptr ds:[esi],ax
    0x66,0x39,0x02                          // 001d45fc  |. 66:3902             cmp word ptr ds:[edx],ax   ; jichi: debug breakpoint stops here
  };
  ulong addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  return winhook::hook_before(addr, Private::hookBefore);
}
} // namespace DebugHook

namespace ChoiceHook { // FIXME: I am not able to distinguish Choice text out
namespace Private {
  bool hookBefore(winhook::hook_stack *s)
  {
    static QString text_;
    auto text = (LPCWSTR)s->eax;
    if (!text || !*text
        || text[0] <= 127)
      return true;
    size_t size = ::wcslen(text);
    if(text[size - 1] <= 127
       || text[size + 1] != 0 || text[size + 2] == 0)
      return true;
    auto retaddr = s->stack[2];
    auto reladdr = retaddr - moduleBaseAddress_;
    if (reladdr != 0x218d1)
      return true;
    auto role = Engine::ChoiceRole;
    QString oldText = QString::fromWCharArray(text),
            newText = EngineController::instance()->dispatchTextW(oldText, role, reladdr);
    if (newText.isEmpty() || oldText == newText)
      return true;
    //if (text[0] != 0x30d7)
    //  return true;
    text_ = newText;
    s->eax = (ulong)text_.utf16();
    return true;
  }
} // Private
/**
 *  Sample game: 塔の下のエクセルキトゥス体験版
 *  Executable description shows "AVGEngineV2"
 *
 *  arg1: source text
 *  arg2: target text to return
 *
 *  00E8562C     CC               INT3
 *  00E8562D     CC               INT3
 *  00E8562E     CC               INT3
 *  00E8562F     CC               INT3
 *  00E85630  /$ 55               PUSH EBP
 *  00E85631  |. 8BEC             MOV EBP,ESP
 *  00E85633  |. 51               PUSH ECX
 *  00E85634  |. 8B41 0C          MOV EAX,DWORD PTR DS:[ECX+0xC]	; jichi: text here in [ecx+0xc]
 *  00E85637  |. 8B4D 08          MOV ECX,DWORD PTR SS:[EBP+0x8]
 *  00E8563A  |. C745 FC 00000000 MOV DWORD PTR SS:[EBP-0x4],0x0
 *  00E85641  |. 56               PUSH ESI
 *  00E85642  |. 85C0             TEST EAX,EAX
 *  00E85644  |. 75 14            JNZ SHORT play.00E8565A
 *  00E85646  |. 68 C89F1501      PUSH play.01159FC8                       ; /Arg1 = 01159FC8
 *  00E8564B  |. E8 90EFFDFF      CALL play.00E645E0                       ; \play.001D45E0
 *  00E85650  |. 8B45 08          MOV EAX,DWORD PTR SS:[EBP+0x8]
 *  00E85653  |. 5E               POP ESI
 *  00E85654  |. 8BE5             MOV ESP,EBP
 *  00E85656  |. 5D               POP EBP
 *  00E85657  |. C2 0400          RETN 0x4
 *  00E8565A  |> 50               PUSH EAX                                 ; /Arg1
 *  00E8565B  |. E8 80EFFDFF      CALL play.00E645E0                       ; \play.001D45E0
 *  00E85660  |. 8B45 08          MOV EAX,DWORD PTR SS:[EBP+0x8]
 *  00E85663  |. 5E               POP ESI
 *  00E85664  |. 8BE5             MOV ESP,EBP
 *  00E85666  |. 5D               POP EBP
 *  00E85667  \. C2 0400          RETN 0x4
 *  00E8566A     CC               INT3
 *  00E8566B     CC               INT3
 *  00E8566C     CC               INT3
 *  00E8566D     CC               INT3
 */
bool attach(ulong startAddress, ulong stopAddress)
{
  const uint8_t bytes[] = {
    0x55,                                // 00e85630  /$ 55               push ebp
    0x8b,0xec,                           // 00e85631  |. 8bec             mov ebp,esp
    0x51,                                // 00e85633  |. 51               push ecx
    0x8b,0x41, 0x0c,                     // 00e85634  |. 8b41 0c          mov eax,dword ptr ds:[ecx+0xc]	; jichi: text here in [ecx+0xc]
    0x8b,0x4d, 0x08,                     // 00e85637  |. 8b4d 08          mov ecx,dword ptr ss:[ebp+0x8]
    0xc7,0x45, 0xfc, 0x00,0x00,0x00,0x00 // 00e8563a  |. c745 fc 00000000 mov dword ptr ss:[ebp-0x4],0x0
  };
  enum { addr_offset = 0x00e85637 - 0x00e85630 };
  ulong addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  if (!addr)
    return false;
  return winhook::hook_before(addr + addr_offset, Private::hookBefore);
}
} // namespace ChoiceHook

namespace OtherHook {
namespace Private {
  struct HookArgument
  {
    DWORD unknown[3];
    LPCWSTR text; // 0xc

    bool isValid() const
    {
      return Engine::isAddressWritable(text)
          && text[0] > 127 && text[::wcslen(text) - 1] > 127; // skip ascii text
    }
  };
  typedef HookArgument *(__fastcall *hook_fun_t)(void *ecx, void *edx, int offset1, int offset2);
  hook_fun_t oldHookFun;
  HookArgument * __fastcall newHookFun(void *ecx, void *edx, ulong offset1, ulong offset2)
  {
    auto arg = oldHookFun(ecx, edx, offset1, offset2);
    if (arg && arg->isValid()) {
      auto role = Engine::OtherRole;
      ulong split = (offset1 << 4) | offset2;
      auto sig = split;
      QString oldText = QString::fromWCharArray(arg->text),
              newText = EngineController::instance()->dispatchTextW(oldText, role, sig);
    }
    return arg;
  }
} // Private
/**
 *  Sample game: 塔の下のエクセルキトゥス体験版
 *  Executable description shows "AVGEngineV2"
 *
 *  arg1 and arg2 are offsets
 *  ecx is this
 *  eax is retaddr
 *
 *  00FC489E     CC             INT3
 *  00FC489F     CC             INT3
 *  00FC48A0  /$ 55             PUSH EBP
 *  00FC48A1  |. 8BEC           MOV EBP,ESP
 *  00FC48A3  |. A1 704D6201    MOV EAX,DWORD PTR DS:[0x1624D70]
 *  00FC48A8  |. 56             PUSH ESI
 *  00FC48A9  |. 8BF1           MOV ESI,ECX
 *  00FC48AB  |. A8 01          TEST AL,0x1
 *  00FC48AD  |. 75 48          JNZ SHORT play.00FC48F7
 *  00FC48AF  |. 83C8 01        OR EAX,0x1
 *  00FC48B2  |. C705 784D6201 >MOV DWORD PTR DS:[0x1624D78],play.012AC4>
 *  00FC48BC  |. 0F57C0         XORPS XMM0,XMM0
 *  00FC48BF  |. A3 704D6201    MOV DWORD PTR DS:[0x1624D70],EAX
 *  00FC48C4  |. 68 004F2201    PUSH play.01224F00                       ; /Arg1 = 01224F00
 *  00FC48C9  |. C705 884D6201 >MOV DWORD PTR DS:[0x1624D88],0x11        ; |
 *  00FC48D3  |. 66:0F1305 904D>MOVLPS QWORD PTR DS:[0x1624D90],XMM0     ; |
 *  00FC48DB  |. C705 804D6201 >MOV DWORD PTR DS:[0x1624D80],0x0         ; |
 *  00FC48E5  |. C705 844D6201 >MOV DWORD PTR DS:[0x1624D84],0x0         ; |
 *  00FC48EF  |. E8 23942000    CALL play.011CDD17                       ; \play.003FDD17
 *  00FC48F4  |. 83C4 04        ADD ESP,0x4
 *  00FC48F7  |> 8B4D 08        MOV ECX,DWORD PTR SS:[EBP+0x8]
 *  00FC48FA  |. 85C9           TEST ECX,ECX
 *  00FC48FC  |. 78 36          JS SHORT play.00FC4934
 *  00FC48FE  |. 8B55 0C        MOV EDX,DWORD PTR SS:[EBP+0xC]
 *  00FC4901  |. 85D2           TEST EDX,EDX
 *  00FC4903  |. 78 2F          JS SHORT play.00FC4934
 *  00FC4905  |. 8B46 38        MOV EAX,DWORD PTR DS:[ESI+0x38]
 *  00FC4908  |. 2B46 34        SUB EAX,DWORD PTR DS:[ESI+0x34]
 *  00FC490B  |. C1F8 04        SAR EAX,0x4
 *  00FC490E  |. 3BC1           CMP EAX,ECX
 *  00FC4910  |. 7E 22          JLE SHORT play.00FC4934
 *  00FC4912  |. 8B46 34        MOV EAX,DWORD PTR DS:[ESI+0x34]
 *  00FC4915  |. C1E1 04        SHL ECX,0x4
 *  00FC4918  |. 03C1           ADD EAX,ECX
 *  00FC491A  |. 8B48 08        MOV ECX,DWORD PTR DS:[EAX+0x8]
 *  00FC491D  |. 2B48 04        SUB ECX,DWORD PTR DS:[EAX+0x4]
 *  00FC4920  |. C1F9 05        SAR ECX,0x5
 *  00FC4923  |. 3BCA           CMP ECX,EDX
 *  00FC4925  |. 7E 0D          JLE SHORT play.00FC4934
 *  00FC4927  |. C1E2 05        SHL EDX,0x5
 *  00FC492A  |. 0350 04        ADD EDX,DWORD PTR DS:[EAX+0x4]
 *  00FC492D  |. 8BC2           MOV EAX,EDX
 *  00FC492F  |. 5E             POP ESI
 *  00FC4930  |. 5D             POP EBP
 *  00FC4931  |. C2 0800        RETN 0x8
 *  00FC4934  |> B8 784D6201    MOV EAX,play.01624D78
 *  00FC4939  |. 5E             POP ESI
 *  00FC493A  |. 5D             POP EBP
 *  00FC493B  \. C2 0800        RETN 0x8
 *  00FC493E     CC             INT3
 *  00FC493F     CC             INT3
 */
bool attach(ulong startAddress, ulong stopAddress)
{
  const uint8_t bytes[] = {
    0x56,           // 00fc48a8  |. 56             push esi
    0x8b,0xf1,      // 00fc48a9  |. 8bf1           mov esi,ecx
    0xa8, 0x01,     // 00fc48ab  |. a8 01          test al,0x1
    0x75, 0x48,     // 00fc48ad  |. 75 48          jnz short play.00fc48f7
    0x83,0xc8, 0x01 // 00fc48af  |. 83c8 01        or eax,0x1
  };
  ulong addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  return Private::oldHookFun = (Private::hook_fun_t)winhook::replace_fun(addr, (ulong)Private::newHookFun);
}
} // namespace OtherHook

/**
 *  Sample game: 塔の下のエクセルキトゥス体験版
 *  Executable description shows "AVGEngineV2"
 *
 *  This is the memcpy function.
 *
 *  arg1: target text
 *  arg2: source tex
 *  arg3: size
 *
 *  00A3F8CB     CC             INT3
 *  00A3F8CC     CC             INT3
 *  00A3F8CD     CC             INT3
 *  00A3F8CE     CC             INT3
 *  00A3F8CF     CC             INT3
 *  00A3F8D0   $ 57             PUSH EDI
 *  00A3F8D1   . 56             PUSH ESI
 *  00A3F8D2   . 8B7424 10      MOV ESI,DWORD PTR SS:[ESP+0x10]
 *  00A3F8D6   . 8B4C24 14      MOV ECX,DWORD PTR SS:[ESP+0x14]
 *  00A3F8DA   . 8B7C24 0C      MOV EDI,DWORD PTR SS:[ESP+0xC]
 *  00A3F8DE   . 8BC1           MOV EAX,ECX
 *  00A3F8E0   . 8BD1           MOV EDX,ECX
 *  00A3F8E2   . 03C6           ADD EAX,ESI
 *  00A3F8E4   . 3BFE           CMP EDI,ESI
 *  00A3F8E6   . 76 08          JBE SHORT play.00A3F8F0
 *  00A3F8E8   . 3BF8           CMP EDI,EAX
 *  00A3F8EA   . 0F82 68030000  JB play.00A3FC58
 *  00A3F8F0   > 0FBA25 581FBC0>BT DWORD PTR DS:[0xBC1F58],0x1
 *  00A3F8F8   . 73 07          JNB SHORT play.00A3F901
 *  00A3F8FA   . F3:A4          REP MOVS BYTE PTR ES:[EDI],BYTE PTR DS:[ESI]	; jichi: here
 *  00A3F8FC   . E9 17030000    JMP play.00A3FC18
 *  00A3F901   > 81F9 80000000  CMP ECX,0x80
 *  00A3F907   . 0F82 CE010000  JB play.00A3FADB
 *  00A3F90D   . 8BC7           MOV EAX,EDI
 *  00A3F90F   . 33C6           XOR EAX,ESI
 *  00A3F911   . A9 0F000000    TEST EAX,0xF
 *  00A3F916   . 75 0E          JNZ SHORT play.00A3F926
 *  00A3F918   . 0FBA25 3060B90>BT DWORD PTR DS:[0xB96030],0x1
 *  00A3F920   . 0F82 DA040000  JB play.00A3FE00
 *  00A3F926   > 0FBA25 581FBC0>BT DWORD PTR DS:[0xBC1F58],0x0
 *  00A3F92E   . 0F83 A7010000  JNB play.00A3FADB
 *  00A3F934   . F7C7 03000000  TEST EDI,0x3
 *  00A3F93A   . 0F85 B8010000  JNZ play.00A3FAF8
 *  00A3F940   . F7C6 03000000  TEST ESI,0x3
 *  00A3F946   . 0F85 97010000  JNZ play.00A3FAE3
 *  00A3F94C   . 0FBAE7 02      BT EDI,0x2
 *  00A3F950   . 73 0D          JNB SHORT play.00A3F95F
 *  00A3F952   . 8B06           MOV EAX,DWORD PTR DS:[ESI]
 *  00A3F954   . 83E9 04        SUB ECX,0x4
 *  00A3F957   . 8D76 04        LEA ESI,DWORD PTR DS:[ESI+0x4]
 *  00A3F95A   . 8907           MOV DWORD PTR DS:[EDI],EAX
 *  00A3F95C   . 8D7F 04        LEA EDI,DWORD PTR DS:[EDI+0x4]
 *  00A3F95F   > 0FBAE7 03      BT EDI,0x3
 *  00A3F963   . 73 11          JNB SHORT play.00A3F976
 *  00A3F965   . F3:            PREFIX REP:                              ;  Superfluous prefix
 *  00A3F966   . 0F7E0E         MOVD DWORD PTR DS:[ESI],MM1
 *  00A3F969   . 83E9 08        SUB ECX,0x8
 *  00A3F96C   . 8D76 08        LEA ESI,DWORD PTR DS:[ESI+0x8]
 *  00A3F96F     66             DB 66                                    ;  CHAR 'f'
 *  00A3F970     0F             DB 0F
 *  00A3F971     D6             DB D6
 *  00A3F972     0F             DB 0F
 */
bool attach(ulong startAddress, ulong stopAddress)
{
  // There are two exact the same functions
  // The last function is hooked.
  // It seems the functions are generated by inlining
  const uint8_t bytes[] = {
    0x57,                 // 00a3f8d0   $ 57             push edi
    0x56,                 // 00a3f8d1   . 56             push esi
    0x8b,0x74,0x24, 0x10, // 00a3f8d2   . 8b7424 10      mov esi,dword ptr ss:[esp+0x10]
    0x8b,0x4c,0x24, 0x14, // 00a3f8d6   . 8b4c24 14      mov ecx,dword ptr ss:[esp+0x14]
    0x8b,0x7c,0x24, 0x0c  // 00a3f8da   . 8b7c24 0c      mov edi,dword ptr ss:[esp+0xc]
  };
  ulong lastCall = 0;
  auto fun = [&lastCall](ulong addr) -> bool {
    //if (lastCall)
    lastCall = addr;
    return true;
  };
  MemDbg::iterFindBytes(fun, bytes, sizeof(bytes), startAddress, stopAddress);
  return lastCall && winhook::hook_before(lastCall, Private::hookBefore);
}

/**
 *  Sample game: 塔の下のエクセルキトゥス体験版
 *  Executable description shows "AVGEngineV2"
 *  Source text in arg1, which is truncated
 *
 *  001D45DA     CC                  INT3
 *  001D45DB     CC                  INT3
 *  001D45DC     CC                  INT3
 *  001D45DD     CC                  INT3
 *  001D45DE     CC                  INT3
 *  001D45DF     CC                  INT3
 *  001D45E0  /$ 55                  PUSH EBP
 *  001D45E1  |. 8BEC                MOV EBP,ESP
 *  001D45E3  |. 8B55 08             MOV EDX,DWORD PTR SS:[EBP+0x8]
 *  001D45E6  |. 33C0                XOR EAX,EAX
 *  001D45E8  |. 56                  PUSH ESI
 *  001D45E9  |. 8BF1                MOV ESI,ECX
 *  001D45EB  |. C746 14 07000000    MOV DWORD PTR DS:[ESI+0x14],0x7
 *  001D45F2  |. C746 10 00000000    MOV DWORD PTR DS:[ESI+0x10],0x0
 *  001D45F9  |. 66:8906             MOV WORD PTR DS:[ESI],AX
 *  001D45FC  |. 66:3902             CMP WORD PTR DS:[EDX],AX   ; jichi: debug breakpoint stops here
 *  001D45FF  |. 75 12               JNZ SHORT play.001D4613
 *  001D4601  |. 33C9                XOR ECX,ECX
 *  001D4603  |. 51                  PUSH ECX
 *  001D4604  |. 52                  PUSH EDX
 *  001D4605  |. 8BCE                MOV ECX,ESI
 *  001D4607  |. E8 A4160000         CALL play.001D5CB0
 *  001D460C  |. 8BC6                MOV EAX,ESI
 *  001D460E  |. 5E                  POP ESI
 *  001D460F  |. 5D                  POP EBP
 *  001D4610  |. C2 0400             RETN 0x4
 *  001D4613  |> 8BCA                MOV ECX,EDX
 *  001D4615  |. 57                  PUSH EDI
 *  001D4616  |. 8D79 02             LEA EDI,DWORD PTR DS:[ECX+0x2]
 *  001D4619  |. 8DA424 00000000     LEA ESP,DWORD PTR SS:[ESP]
 *  001D4620  |> 66:8B01             MOV AX,WORD PTR DS:[ECX]
 *  001D4623  |. 83C1 02             ADD ECX,0x2
 *  001D4626  |. 66:85C0             TEST AX,AX
 *  001D4629  |.^75 F5               JNZ SHORT play.001D4620
 *  001D462B  |. 2BCF                SUB ECX,EDI
 *  001D462D  |. D1F9                SAR ECX,1
 *  001D462F  |. 5F                  POP EDI
 *  001D4630  |. 51                  PUSH ECX
 *  001D4631  |. 52                  PUSH EDX
 *  001D4632  |. 8BCE                MOV ECX,ESI
 *  001D4634  |. E8 77160000         CALL play.001D5CB0
 *  001D4639  |. 8BC6                MOV EAX,ESI
 *  001D463B  |. 5E                  POP ESI
 *  001D463C  |. 5D                  POP EBP
 *  001D463D  \. C2 0400             RETN 0x4
 *  001D4640  /. 55                  PUSH EBP
 *  001D4641  |. 8BEC                MOV EBP,ESP
 *  001D4643  |. 51                  PUSH ECX
 *  001D4644  |. 56                  PUSH ESI
 *  001D4645  |. 8B75 08             MOV ESI,DWORD PTR SS:[EBP+0x8]
 *  001D4648  |. 33C0                XOR EAX,EAX
 *  001D464A  |. 50                  PUSH EAX
 *  001D464B  |. 68 C89F4C00         PUSH play.004C9FC8
 *  001D4650  |. 8BCE                MOV ECX,ESI
 *  001D4652  |. C745 FC 00000000    MOV DWORD PTR SS:[EBP-0x4],0x0
 *  001D4659  |. C746 14 07000000    MOV DWORD PTR DS:[ESI+0x14],0x7
 *  001D4660  |. C746 10 00000000    MOV DWORD PTR DS:[ESI+0x10],0x0
 *  001D4667  |. 66:8906             MOV WORD PTR DS:[ESI],AX
 *  001D466A  |. E8 41160000         CALL play.001D5CB0
 *  001D466F  |. 8BC6                MOV EAX,ESI
 *  001D4671  |. 5E                  POP ESI
 *  001D4672  |. 8BE5                MOV ESP,EBP
 *  001D4674  |. 5D                  POP EBP
 *  001D4675  \. C2 0400             RETN 0x4
 *  001D4678     CC                  INT3
 *  001D4679     CC                  INT3
 *  001D467A     CC                  INT3
 *  001D467B     CC                  INT3
 *  001D467C     CC                  INT3
 *  001D467D     CC                  INT3
 *  001D467E     CC                  INT3
 *  001D467F     CC                  INT3
 */
bool attach(ulong startAddress, ulong stopAddress)
{
  const uint8_t bytes[] = {
    0x8b,0xf1,                              // 001d45e9  |. 8bf1                mov esi,ecx
    0xc7,0x46, 0x14, 0x07,0x00,0x00,0x00,   // 001d45eb  |. c746 14 07000000    mov dword ptr ds:[esi+0x14],0x7
    0xc7,0x46, 0x10, 0x00,0x00,0x00,0x00,   // 001d45f2  |. c746 10 00000000    mov dword ptr ds:[esi+0x10],0x0
    0x66,0x89,0x06,                         // 001d45f9  |. 66:8906             mov word ptr ds:[esi],ax
    0x66,0x39,0x02                          // 001d45fc  |. 66:3902             cmp word ptr ds:[edx],ax   ; jichi: debug breakpoint stops here
  };
  ulong addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  return winhook::hook_before(addr, Private::hookBefore);
}

// FIXME: text get split to lines
// Need to find text containing "%r"
namespace ScenarioHook1 { // for old GXP1
namespace Private {
  /**
   *  Sample system text:
   *  cg/bg/ショップ前＿昼.png
   *
   *  Scenario caller:
   *  00187E65  |. 8B06           MOV EAX,DWORD PTR DS:[ESI]
   *  00187E67  |. FF90 A8020000  CALL DWORD PTR DS:[EAX+0x2A8]
   *  00187E6D  |. 8B45 08        MOV EAX,DWORD PTR SS:[EBP+0x8]
   *  00187E70  |. 8D8E A8010000  LEA ECX,DWORD PTR DS:[ESI+0x1A8]
   *  00187E76  |. 3BC8           CMP ECX,EAX
   *  00187E78  |. 74 0A          JE SHORT play.00187E84
   *  00187E7A  |. 6A FF          PUSH -0x1
   *  00187E7C  |. 6A 00          PUSH 0x0
   *  00187E7E  |. 50             PUSH EAX
   *  00187E7F  |. E8 CCDAFBFF    CALL play.00145950
   *  00187E84  |> 8A45 0C        MOV AL,BYTE PTR SS:[EBP+0xC]
   *  00187E87  |. 8B0D 882C4F00  MOV ECX,DWORD PTR DS:[0x4F2C88]
   *  00187E8D  |. 8886 03030000  MOV BYTE PTR DS:[ESI+0x303],AL
   *  00187E93  |. 8A45 10        MOV AL,BYTE PTR SS:[EBP+0x10]
   *  00187E96  |. 8886 05030000  MOV BYTE PTR DS:[ESI+0x305],AL
   *
   *  The history thread that is needed to be skipped to avoid retranslation
   *  0095391A   74 0A            JE SHORT 塔の下の.00953926
   *  0095391C   6A FF            PUSH -0x1
   *  0095391E   6A 00            PUSH 0x0
   *  00953920   50               PUSH EAX
   *  00953921   call
   *  00953926   A1 882CCB00      MOV EAX,DWORD PTR DS:[0xCB2C88]   ; jichi: retaddr
   *  0095392B   A8 01            TEST AL,0x1
   *  0095392D   75 28            JNZ SHORT 塔の下の.00953957
   */
  bool hookBefore(winhook::hook_stack *s)
  {
    static QString text_; // persistent storage, which makes this function not thread-safe
    auto text = (LPWSTR)s->stack[1]; // arg1
    auto size = s->stack[2]; // arg2
    if (!(size > 0 && Engine::isAddressWritable(text) && ::wcslen(text) == size
          && text[0] > 127 && text[size - 1] > 127))
      return true;

    auto retaddr = s->stack[0];
    auto reladdr = retaddr - moduleBaseAddress_;
    auto role = Engine::OtherRole;
    QString oldText = QString::fromWCharArray(text),
            newText = EngineController::instance()->dispatchTextW(oldText, role, reladdr);
    if (newText == oldText)
      return true;
    text_ = newText;
    s->stack[1] = (ulong)text_.utf16();
    s->stack[2] = text_.size();
    return true;
  }
} // namespace Private

/**
 *  Sample game: 塔の下のエクセルキトゥス体験版
 *  Executable description shows "AVGEngineV2"
 *
 *  Find one of caller of the push "invalid string position" instruction.
 *
 *  arg1: text
 *  arg2: size
 *
 *  00EC3DAE   CC               INT3
 *  00EC3DAF   CC               INT3
 *  00EC3DB0   53               PUSH EBX
 *  00EC3DB1   56               PUSH ESI
 *  00EC3DB2   8BF1             MOV ESI,ECX
 *  00EC3DB4   8B4C24 0C        MOV ECX,DWORD PTR SS:[ESP+0xC]
 *  00EC3DB8   57               PUSH EDI
 *  00EC3DB9   85C9             TEST ECX,ECX
 *  00EC3DBB   74 49            JE SHORT trial.00EC3E06
 *  00EC3DBD   8B7E 18          MOV EDI,DWORD PTR DS:[ESI+0x18]
 *  00EC3DC0   8D46 04          LEA EAX,DWORD PTR DS:[ESI+0x4]
 *  00EC3DC3   83FF 08          CMP EDI,0x8
 *  00EC3DC6   72 04            JB SHORT trial.00EC3DCC
 *  00EC3DC8   8B10             MOV EDX,DWORD PTR DS:[EAX]
 *  00EC3DCA   EB 02            JMP SHORT trial.00EC3DCE
 *  00EC3DCC   8BD0             MOV EDX,EAX
 *  00EC3DCE   3BCA             CMP ECX,EDX
 *  00EC3DD0   72 34            JB SHORT trial.00EC3E06
 *  00EC3DD2   83FF 08          CMP EDI,0x8
 *  00EC3DD5   72 04            JB SHORT trial.00EC3DDB
 *  00EC3DD7   8B10             MOV EDX,DWORD PTR DS:[EAX]
 *  00EC3DD9   EB 02            JMP SHORT trial.00EC3DDD
 *  00EC3DDB   8BD0             MOV EDX,EAX
 *  00EC3DDD   8B5E 14          MOV EBX,DWORD PTR DS:[ESI+0x14]
 *  00EC3DE0   8D145A           LEA EDX,DWORD PTR DS:[EDX+EBX*2]
 *  00EC3DE3   3BD1             CMP EDX,ECX
 *  00EC3DE5   76 1F            JBE SHORT trial.00EC3E06
 *  00EC3DE7   83FF 08          CMP EDI,0x8
 *  00EC3DEA   72 02            JB SHORT trial.00EC3DEE
 *  00EC3DEC   8B00             MOV EAX,DWORD PTR DS:[EAX]
 *  00EC3DEE   8B5424 14        MOV EDX,DWORD PTR SS:[ESP+0x14]
 *  00EC3DF2   2BC8             SUB ECX,EAX
 *  00EC3DF4   52               PUSH EDX
 *  00EC3DF5   D1F9             SAR ECX,1
 *  00EC3DF7   51               PUSH ECX
 *  00EC3DF8   56               PUSH ESI
 *  00EC3DF9   8BCE             MOV ECX,ESI
 *  00EC3DFB   E8 00FDFFFF      CALL trial.00EC3B00
 *  00EC3E00   5F               POP EDI
 *  00EC3E01   5E               POP ESI
 *  00EC3E02   5B               POP EBX
 *  00EC3E03   C2 0800          RETN 0x8
 *  00EC3E06   8B7C24 14        MOV EDI,DWORD PTR SS:[ESP+0x14]
 *  00EC3E0A   81FF FEFFFF7F    CMP EDI,0x7FFFFFFE
 *  00EC3E10   76 05            JBE SHORT trial.00EC3E17
 *  00EC3E12   E8 BFA01200      CALL trial.00FEDED6
 *  00EC3E17   8B46 18          MOV EAX,DWORD PTR DS:[ESI+0x18]
 *  00EC3E1A   3BC7             CMP EAX,EDI
 *  00EC3E1C   73 21            JNB SHORT trial.00EC3E3F
 *  00EC3E1E   8B46 14          MOV EAX,DWORD PTR DS:[ESI+0x14]
 *  00EC3E21   50               PUSH EAX
 *  00EC3E22   57               PUSH EDI
 *  00EC3E23   8BCE             MOV ECX,ESI
 *  00EC3E25   E8 36FEFFFF      CALL trial.00EC3C60
 *  00EC3E2A   85FF             TEST EDI,EDI
 *  00EC3E2C   76 67            JBE SHORT trial.00EC3E95
 *  00EC3E2E   8B4E 18          MOV ECX,DWORD PTR DS:[ESI+0x18]
 *  00EC3E31   55               PUSH EBP
 *  00EC3E32   8D6E 04          LEA EBP,DWORD PTR DS:[ESI+0x4]
 *  00EC3E35   83F9 08          CMP ECX,0x8
 *  00EC3E38   72 31            JB SHORT trial.00EC3E6B
 *  00EC3E3A   8B45 00          MOV EAX,DWORD PTR SS:[EBP]
 *  00EC3E3D   EB 2E            JMP SHORT trial.00EC3E6D
 *  00EC3E3F   85FF             TEST EDI,EDI
 *  00EC3E41  ^75 E9            JNZ SHORT trial.00EC3E2C
 *  00EC3E43   897E 14          MOV DWORD PTR DS:[ESI+0x14],EDI
 *  00EC3E46   83F8 08          CMP EAX,0x8
 *  00EC3E49   72 10            JB SHORT trial.00EC3E5B
 *  00EC3E4B   8B46 04          MOV EAX,DWORD PTR DS:[ESI+0x4]
 *  00EC3E4E   33C9             XOR ECX,ECX
 *  00EC3E50   5F               POP EDI
 *  00EC3E51   66:8908          MOV WORD PTR DS:[EAX],CX
 *  00EC3E54   8BC6             MOV EAX,ESI
 *  00EC3E56   5E               POP ESI
 *  00EC3E57   5B               POP EBX
 *  00EC3E58   C2 0800          RETN 0x8
 *  00EC3E5B   8D46 04          LEA EAX,DWORD PTR DS:[ESI+0x4]
 *  00EC3E5E   33C9             XOR ECX,ECX
 *  00EC3E60   5F               POP EDI
 *  00EC3E61   66:8908          MOV WORD PTR DS:[EAX],CX
 *  00EC3E64   8BC6             MOV EAX,ESI
 *  00EC3E66   5E               POP ESI
 *  00EC3E67   5B               POP EBX
 *  00EC3E68   C2 0800          RETN 0x8
 *  00EC3E6B   8BC5             MOV EAX,EBP
 *  00EC3E6D   8B5424 14        MOV EDX,DWORD PTR SS:[ESP+0x14]
 *  00EC3E71   8D1C3F           LEA EBX,DWORD PTR DS:[EDI+EDI]
 *  00EC3E74   53               PUSH EBX
 *  00EC3E75   52               PUSH EDX
 *  00EC3E76   03C9             ADD ECX,ECX
 *  00EC3E78   51               PUSH ECX
 *  00EC3E79   50               PUSH EAX
 *  00EC3E7A   E8 58A61200      CALL trial.00FEE4D7
 *  00EC3E7F   83C4 10          ADD ESP,0x10
 *  00EC3E82   837E 18 08       CMP DWORD PTR DS:[ESI+0x18],0x8
 *  00EC3E86   897E 14          MOV DWORD PTR DS:[ESI+0x14],EDI
 *  00EC3E89   72 03            JB SHORT trial.00EC3E8E
 *  00EC3E8B   8B6D 00          MOV EBP,DWORD PTR SS:[EBP]
 *  00EC3E8E   33D2             XOR EDX,EDX
 *  00EC3E90   66:89142B        MOV WORD PTR DS:[EBX+EBP],DX
 *  00EC3E94   5D               POP EBP
 *  00EC3E95   5F               POP EDI
 *  00EC3E96   8BC6             MOV EAX,ESI
 *  00EC3E98   5E               POP ESI
 *  00EC3E99   5B               POP EBX
 *  00EC3E9A   C2 0800          RETN 0x8
 *  00EC3E9D   CC               INT3
 *  00EC3E9E   CC               INT3
 *  00EC3E9F   CC               INT3
 *  00EC3EA0   56               PUSH ESI
 *  00EC3EA1   8B7424 08        MOV ESI,DWORD PTR SS:[ESP+0x8]
 *  00EC3EA5   8BC6             MOV EAX,ESI
 *  00EC3EA7   57               PUSH EDI
 *  00EC3EA8   8D78 02          LEA EDI,DWORD PTR DS:[EAX+0x2]
 *  00EC3EAB   EB 03            JMP SHORT trial.00EC3EB0
 *  00EC3EAD   8D49 00          LEA ECX,DWORD PTR DS:[ECX]
 *  00EC3EB0   66:8B10          MOV DX,WORD PTR DS:[EAX]
 *  00EC3EB3   83C0 02          ADD EAX,0x2
 *  00EC3EB6   66:85D2          TEST DX,DX
 *  00EC3EB9  ^75 F5            JNZ SHORT trial.00EC3EB0
 *  00EC3EBB   2BC7             SUB EAX,EDI
 *  00EC3EBD   D1F8             SAR EAX,1
 *  00EC3EBF   50               PUSH EAX
 *  00EC3EC0   56               PUSH ESI
 *  00EC3EC1   E8 EAFEFFFF      CALL trial.00EC3DB0
 *  00EC3EC6   5F               POP EDI
 *  00EC3EC7   5E               POP ESI
 *  00EC3EC8   C2 0400          RETN 0x4
 *  00EC3ECB   CC               INT3
 *  00EC3ECC   CC               INT3
 *  00EC3ECD   CC               INT3
 *  00EC3ECE   CC               INT3
 */
bool attach(ulong startAddress, ulong stopAddress)
{
  const uint8_t bytes[] = {
    0x8b,0x7c,0x24, 0x14,           // 00ec3e06   8b7c24 14        mov edi,dword ptr ss:[esp+0x14]
    0x81,0xff, 0xfe,0xff,0xff,0x7f, // 00ec3e0a   81ff feffff7f    cmp edi,0x7ffffffe
    0x76, 0x05                      // 00ec3e10   76 05            jbe short trial.00ec3e17
  };
  ulong addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  if (!addr)
    return addr;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return addr;
  return winhook::hook_before(addr, Private::hookBefore);
}
} // namespace ScenarioHook1

namespace ChoiceHook {
namespace Private {
  bool hookBefore(winhook::hook_stack *s)
  {
    static QString text_;
    auto text = (LPCWSTR)s->stack[3]; // arg3
    if (!text || !*text)
      return true;
    auto retaddr = s->stack[0];
    auto reladdr = retaddr - moduleBaseAddress_;
    enum { role = Engine::ChoiceRole };
    QString oldText = QString::fromWCharArray(text),
            newText = EngineController::instance()->dispatchTextW(oldText, role, reladdr);
    if (newText.isEmpty() || oldText == newText)
      return true;
    text_ = newText;
    s->stack[3] = (ulong)text_.utf16();
    return true;
  }
} // Private
/**
 *  Sample game: 塔の下のエクセルキトゥス体験版
 *  Executable description shows "AVGEngineV2"
 *
 *  This is the actual draw function. Text is looped.
 *  Function found by debugging the popup message (the second message is accessed):
 *
 *  % hexstr ゲームを終了しますか utf16
 *  b230fc30e0309230427d864e57307e3059304b30
 *
 *  002AFC58  |011D140E  RETURN to play.011D140E from play.01340FF0
 *  002AFC5C  |002AFD14
 *  002AFC60  |01537308  play.01537308
 *  002AFC64  |0A426B58	; jichi: text
 *  002AFC68  |002AFCC4
 *  002AFC6C  |FFFFFFFF
 *  002AFC70  |00000000
 *  002AFC74  |80000000
 *  002AFC78  |00000002
 *  002AFC7C  |0000007C
 *  002AFC80  |00000007
 *  002AFC84  |0A6A6640
 *  002AFC88  |01532D90  play.01532D90
 *  002AFC8C  |00000000
 *
 *  01340FEA     CC                INT3
 *  01340FEB     CC                INT3
 *  01340FEC     CC                INT3
 *  01340FED     CC                INT3
 *  01340FEE     CC                INT3
 *  01340FEF     CC                INT3
 *  01340FF0   $ 55                PUSH EBP
 *  01340FF1   . 8BEC              MOV EBP,ESP
 *  01340FF3   . 6A FF             PUSH -0x1
 *  01340FF5   . 68 00054001       PUSH play.01400500
 *  01340FFA   . 64:A1 00000000    MOV EAX,DWORD PTR FS:[0]
 *  01341000   . 50                PUSH EAX
 *  01341001   . 83EC 30           SUB ESP,0x30
 *  01341004   . 53                PUSH EBX
 *  01341005   . 56                PUSH ESI
 *  01341006   . 57                PUSH EDI
 *  01341007   . A1 10605001       MOV EAX,DWORD PTR DS:[0x1506010]
 *  0134100C   . 33C5              XOR EAX,EBP
 *  0134100E   . 50                PUSH EAX
 *  0134100F   . 8D45 F4           LEA EAX,DWORD PTR SS:[EBP-0xC]
 *  01341012   . 64:A3 00000000    MOV DWORD PTR FS:[0],EAX
 *  01341018   . 8B45 14           MOV EAX,DWORD PTR SS:[EBP+0x14]
 *  0134101B   . C745 C4 00000000  MOV DWORD PTR SS:[EBP-0x3C],0x0
 *  01341022   . C745 C8 00000000  MOV DWORD PTR SS:[EBP-0x38],0x0
 *  01341029   . C745 CC 00000000  MOV DWORD PTR SS:[EBP-0x34],0x0
 *  01341030   . 8B08              MOV ECX,DWORD PTR DS:[EAX]
 *  01341032   . 8B50 04           MOV EDX,DWORD PTR DS:[EAX+0x4]
 *  01341035   . 8B40 08           MOV EAX,DWORD PTR DS:[EAX+0x8]
 *  01341038   . 2BC1              SUB EAX,ECX
 *  0134103A   . 894D E8           MOV DWORD PTR SS:[EBP-0x18],ECX
 *  0134103D   . 8955 E4           MOV DWORD PTR SS:[EBP-0x1C],EDX
 *  01341040   . 8945 EC           MOV DWORD PTR SS:[EBP-0x14],EAX
 *  01341043   . 6A 04             PUSH 0x4
 *  01341045   . 8D4D C4           LEA ECX,DWORD PTR SS:[EBP-0x3C]
 *  01341048   . C745 FC 00000000  MOV DWORD PTR SS:[EBP-0x4],0x0
 *  0134104F   . E8 9CC7E7FF       CALL play.011BD7F0
 *  01341054   . C745 D0 00000000  MOV DWORD PTR SS:[EBP-0x30],0x0
 *  0134105B   . C745 D4 00000000  MOV DWORD PTR SS:[EBP-0x2C],0x0
 *  01341062   . C745 D8 00000000  MOV DWORD PTR SS:[EBP-0x28],0x0
 *  01341069   . 6A 04             PUSH 0x4                                 ; /Arg1 = 00000004
 *  0134106B   . 8D4D D0           LEA ECX,DWORD PTR SS:[EBP-0x30]          ; |
 *  0134106E   . C645 FC 01        MOV BYTE PTR SS:[EBP-0x4],0x1            ; |
 *  01341072   . E8 59B1E4FF       CALL play.0118C1D0                       ; \play.001DC1D0
 *  01341077   . 8B7D 10           MOV EDI,DWORD PTR SS:[EBP+0x10]
 *  0134107A   . 33C0              XOR EAX,EAX
 *  0134107C   . 33DB              XOR EBX,EBX
 *  0134107E   . 8945 F0           MOV DWORD PTR SS:[EBP-0x10],EAX
 *  01341081   . 66:3907           CMP WORD PTR DS:[EDI],AX	; jichi: here
 *  01341084   . 0F84 C3000000     JE play.0134114D
 *  0134108A   . BE 01000000       MOV ESI,0x1
 *  0134108F   . 8945 14           MOV DWORD PTR SS:[EBP+0x14],EAX
 *  01341092   . 8975 10           MOV DWORD PTR SS:[EBP+0x10],ESI
 *  01341095   > 8B4D D4           MOV ECX,DWORD PTR SS:[EBP-0x2C]
 *  01341098   . B8 ABAAAA2A       MOV EAX,0x2AAAAAAB
 *  0134109D   . 2B4D D0           SUB ECX,DWORD PTR SS:[EBP-0x30]
 *  013410A0   . F7E9              IMUL ECX
 *  013410A2   . C1FA 02           SAR EDX,0x2
 *  013410A5   . 8BC2              MOV EAX,EDX
 *  013410A7   . C1E8 1F           SHR EAX,0x1F
 *  013410AA   . 03C2              ADD EAX,EDX
 *  013410AC   . 3BC3              CMP EAX,EBX
 *  013410AE   . 77 09             JA SHORT play.013410B9
 *  013410B0   . 56                PUSH ESI                                 ; /Arg1
 *  013410B1   . 8D4D D0           LEA ECX,DWORD PTR SS:[EBP-0x30]          ; |
 *  013410B4   . E8 D703F1FF       CALL play.01251490                       ; \play.002A1490
 *  013410B9   > 8B45 C8           MOV EAX,DWORD PTR SS:[EBP-0x38]
 *  013410BC   . 2B45 C4           SUB EAX,DWORD PTR SS:[EBP-0x3C]
 *  013410BF   . C1F8 02           SAR EAX,0x2
 *  013410C2   . 3BC3              CMP EAX,EBX
 *  013410C4   . 77 14             JA SHORT play.013410DA
 *  013410C6   . 8D45 E0           LEA EAX,DWORD PTR SS:[EBP-0x20]
 *  013410C9   . C745 E0 00000000  MOV DWORD PTR SS:[EBP-0x20],0x0
 *  013410D0   . 50                PUSH EAX                                 ; /Arg2
 *  013410D1   . 56                PUSH ESI                                 ; |Arg1
 *  013410D2   . 8D4D C4           LEA ECX,DWORD PTR SS:[EBP-0x3C]          ; |
 *  013410D5   . E8 0610EAFF       CALL play.011E20E0                       ; \play.002320E0
 *  013410DA   > 0FB707            MOVZX EAX,WORD PTR DS:[EDI]
 *  013410DD   . 66:3B45 28        CMP AX,WORD PTR SS:[EBP+0x28]	; jichi: here
 *  013410D1   . 56                PUSH ESI                                 ; |Arg1
 *  013410D2   . 8D4D C4           LEA ECX,DWORD PTR SS:[EBP-0x3C]          ; |
 *  013410D5   . E8 0610EAFF       CALL play.011E20E0                       ; \play.002320E0
 *  013410DA   > 0FB707            MOVZX EAX,WORD PTR DS:[EDI]
 *  013410DD   . 66:3B45 28        CMP AX,WORD PTR SS:[EBP+0x28]
 *  013410E1   . 74 4F             JE SHORT play.01341132
 *  013410E3   . 8B75 0C           MOV ESI,DWORD PTR SS:[EBP+0xC]
 *  013410E6   . 50                PUSH EAX                                 ; /Arg1
 *  013410E7   . 8B76 18           MOV ESI,DWORD PTR DS:[ESI+0x18]          ; |
 *  013410EA   . E8 D1160000       CALL play.013427C0                       ; \play.003927C0
 *  013410EF   . 8B4D 14           MOV ECX,DWORD PTR SS:[EBP+0x14]
 *  013410F2   . 83C4 04           ADD ESP,0x4
 *  013410F5   . 034D D0           ADD ECX,DWORD PTR SS:[EBP-0x30]
 *  013410F8   . 0FAFC6            IMUL EAX,ESI
 *  013410FB   . 8B75 F0           MOV ESI,DWORD PTR SS:[EBP-0x10]
 *  013410FE   . 99                CDQ
 *  013410FF   . 2BC2              SUB EAX,EDX
 *  01341101   . D1F8              SAR EAX,1
 *  01341103   . 03F0              ADD ESI,EAX
 *  01341105   . 0FB707            MOVZX EAX,WORD PTR DS:[EDI]	; jichi
 *  01341108   . 50                PUSH EAX
 *  01341109   . 6A 01             PUSH 0x1
 *  0134110B   . 8975 F0           MOV DWORD PTR SS:[EBP-0x10],ESI
 *  0134110E   . E8 6D7EE8FF       CALL play.011C8F80
 *  01341113   . 8B55 C4           MOV EDX,DWORD PTR SS:[EBP-0x3C]
 *  01341116   . 8BCE              MOV ECX,ESI
 *  01341118   . 8B45 0C           MOV EAX,DWORD PTR SS:[EBP+0xC]
 *  ...
 */
bool attach(ulong startAddress, ulong stopAddress)
{
  const uint8_t bytes[] = {
    0x8b,0x45, 0x14,                        // 01341018   . 8b45 14           mov eax,dword ptr ss:[ebp+0x14]
    0xc7,0x45, 0xc4, 0x00,0x00,0x00,0x00    // 0134101b   . c745 c4 00000000  mov dword ptr ss:[ebp-0x3c],0x0
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
