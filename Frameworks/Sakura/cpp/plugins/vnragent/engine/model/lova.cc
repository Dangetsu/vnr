// lova.cc
// 7/19/2015 jichi
#include "engine/model/lova.h"
#include "engine/enginecontroller.h"
#include "engine/enginedef.h"
#include "engine/enginehash.h"
#include "engine/engineutil.h"
//#include "hijack/hijackmanager.h"
#include "memdbg/memsearch.h"
#include "winhook/hookcode.h"
#include "winhook/hookfun.h"
#include "winasm/winasmdef.h"
//#include "ntdll/ntdll.h"
#include <qt_windows.h>
#include <cstdint>

#define DEBUG "model/lova"
#include "sakurakit/skdebug.h"

#ifdef _MSC_VER
# pragma warning(disable:4018) // C4018: signed/unsigned mismatch
#endif // _MSC_VER

//#pragma intrinsic(_ReturnAddress)
//#pragma intrinsic(_AddressOfReturnAddress)

namespace { // unnamed
namespace ScenarioHook {
namespace Private {

  bool is_other_texts(const char *s)
  {
    {
      static const char *t[] = {
        "\xe3\x83\x9b\xe3\x83\xbc\xe3\x83\xa0", /* ホーム */
        "\xe3\x83\xa9\xe3\x82\xa4\xe3\x82\xbb\xe3\x83\xb3\xe3\x82\xb9", /* ライセンス */
        "\xe3\x82\xb2\xe3\x83\xbc\xe3\x83\xa0\xe3\x82\xb9\xe3\x82\xbf\xe3\x83\xbc\xe3\x83\x88", /* ゲームスタート */
        "\xe3\x82\xaa\xe3\x83\x97\xe3\x82\xb7\xe3\x83\xa7\xe3\x83\xb3\xe8\xa8\xad\xe5\xae\x9a" /* オプション設定 */
      };
      for (int i = 0; i < sizeof(t)/sizeof(*t); i++)
        if (::strcmp(s, t[i]) == 0)
          return true;
    }

    {
      static const char *t[] = {
        "VP",
        "\xe6\x83\x85\xe5\xa0\xb1\xe6\x9b\xb4\xe6\x96\xb0", /* 情報更新 */
        "\xe3\x83\x87\xe3\x83\xbc\xe3\x82\xbf\xe9\x80\x9a\xe4\xbf\xa1\xe4\xb8\xad" /* データ通信中 */
      };
      for (int i = 0; i < sizeof(t)/sizeof(*t); i++)
        if (::strstr(s, t[i]))
          return true;
    }
    return false;
  }

  /**
   *  Stack when RtlEnterCriticalSection is invoked:
   *
   *  0070C694   01C87097  RETURN to .01C87097 from ntdll.RtlEnterCriticalSection   ; jichi: returnAddress_
   *  0070C698   16FE00EC
   *  0070C69C   16FE8960 ; jichi: text address
   *  0070C6A0   16FF1BA4
   *  0070C6A4  /0070C6C4
   *  0070C6A8  |01C8F246  RETURN to .01C8F246  ; jichi: parentReturnAddress_
   *  0070C6AC  |00000054 ; jichi: size + 12
   *  0070C6B0  |00000000
   *  0070C6B4  |16FE8960 ; jichi: text address
   *  0070C6B8  |16FE8960 ; jichi: text address
   *  0070C6BC  |16FF1BCC
   *  0070C6C0  |16FED560
   *  0070C6C4  ]0070C6D8  RETURN to 0070C6D8
   *  0070C6C8  |01C8F2C2  RETURN to .01C8F2C2 from .01C8F1E0   ; jichi: RootParentReturnIndex
   *  0070C6CC  |16FE8960 ; jichi: text address
   *  0070C6D0  |00000048 ; jichi: size
   *  0070C6D4  |16FF1B10
   *  0070C6D8  ]0070CF98
   *  0070C6DC  |01D3E74D  RETURN to .01D3E74D from .01C8F2A0
   *  0070C6E0  |16FE8960 ; jichi: text address, not used
   *  0070C6E4  |16FF1B10
   *  0070C6E8  |16FF2930
   *  0070C6EC  |16FF1BCC
   *  0070C6F0  |85C3FEAD
   *  0070C6F4  |01292066  RETURN to .01292066 from .0128A6C0
   *  0070C6F8  |0070C72C
   *  0070C6FC  |0070CBA8
   *  0070C700  |00000000
   *  0070C704  |1DECE100
   *  0070C708  |00000001
   *  0070C70C  |1EFDB880
   *  0070C710  |01291E0E  RETURN to .01291E0E from .01F3A2B0
   *  0070C714  |85C3FF41
   *  0070C718  |0070CC3C
   *  0070C71C  |1EFDB880
   *  0070C720  |012920CE  RETURN to .012920CE from .01F3A116
   *  0070C724  |012920CE  RETURN to .012920CE from .01F3A116
   *  0070C728  |109D57C0
   *  0070C72C  |02136798  .02136798
   *  0070C730  |00000001
   *
   *  EAX 16FE00A0
   *  ECX 16FE00A0
   *  EDX 01C87080 .01C870
   *  EBX 00000048  ; jichi: size
   *  ESP 0070C694
   *  EBP 0070C6A4
   *  ESI 16FE00EC
   *  EDI 16FE00A0
   *  EIP 76FC77A0 ntdll.RtlEnterCriticalSection
   */
  ulong returnAddress_,
        parentReturnAddress_;
  bool hookBefore(winhook::hook_stack *s)
  {
    enum { ReturnIndex = 0, ParentReturnIndex = 5, RootReturnIndex = 13, RootParentReturnIndex = RootReturnIndex + 5 };

    static QByteArray data_;

    if (s->stack[ReturnIndex] != returnAddress_)
      return true;
    if (s->stack[ParentReturnIndex] != parentReturnAddress_)
      return true;

    if (*(BYTE *)s->stack[RootReturnIndex] != s1_pop_esi) // only keep the scenario thread
      return true;

    int size = s->stack[RootReturnIndex + 2];
    if (size <= 0 || size != s->ebx || size + 12 != s->stack[ParentReturnIndex + 1])
      return true;

    ulong textAddress = s->stack[RootReturnIndex + 1];
    if (textAddress != s->stack[ReturnIndex + 2])
      return true;
    auto text = (LPCSTR)textAddress;
    if (!text || *text == '<') // skip leading HTML tags
      return true;

    QString oldText = QString::fromUtf8(text, size);

    auto split = s->stack[RootParentReturnIndex];
    auto role = Engine::OtherRole;
    if (*(DWORD *)split == 0x000c7d80  // 017DE74D   807D 0C 00       CMP BYTE PTR SS:[EBP+0xC],0x0
        && (uchar)*text > 127
        && !is_other_texts(text)
        && !QString(oldText).remove("<br>").contains('>'))
      role = Engine::ScenarioRole;

    auto sig = Engine::hashThreadSignature(role, split);
    QString newText = EngineController::instance()->dispatchTextW(oldText, role, sig);
    if (newText.isEmpty() || newText == oldText)
      return true;
    //return true;
    data_ = newText.toUtf8();

    //if (data_.size() > size)
    //  data_ = data_.left(size); // truncate text

    size = data_.size();
    text = data_.constData();

    s->stack[ParentReturnIndex + 1] = size + 12;
    s->ebx = s->stack[RootReturnIndex + 2] = size;

    for (int i = 1; i < RootReturnIndex + 2; i++)
      if (textAddress == s->stack[i])
        s->stack[i] = (ulong)text;
    return true;
  }
} // namespace Private

/** 7/19/2015: Game engine specific for http://lova.jp
 *
 *  No idea why hooking to this place will crash the game.
 *
 *  Debugging method:
 *  - Find text in UTF8/UTF16
 *    There is one UTF8 matched, and 2 UTF16
 *  - Use virtual machine to find where UTF8 is MODIFIED
 *    It is modified in msvcrt
 *  - Backtrack the stack to find where text is accessed in main module
 *
 *  Base addr = 05f0000
 *
 *  0069CA18   01D9F2C2  RETURN to .01D9F2C2 from .01D9F1E0
 *  0069CA1C   13697A70 ; jichi: text
 *  0069CA20   00000094 ; jichi: text size excluding \0
 *  0069CA24   13685B10 ; jichi
 *  0069CA28  /0069D2E8
 *  0069CA2C  |01E4E74D  RETURN to .01E4E74D from .01D9F2A0
 *  0069CA30  |13697A70
 *  0069CA34  |13685B10
 *  0069CA38  |13686930
 *  0069CA3C  |13685BCC
 *  0069CA40  |0203ADB9  .0203ADB9
 *  0069CA44  |013A2066  RETURN to .013A2066 from .0139A6C0
 *  0069CA48  |0069CA7C
 *  0069CA4C  |0069CEF8
 *
 *  01D9F1DA   CC               INT3
 *  01D9F1DB   CC               INT3
 *  01D9F1DC   CC               INT3
 *  01D9F1DD   CC               INT3
 *  01D9F1DE   CC               INT3
 *  01D9F1DF   CC               INT3
 *  01D9F1E0   55               PUSH EBP
 *  01D9F1E1   8BEC             MOV EBP,ESP
 *  01D9F1E3   51               PUSH ECX
 *  01D9F1E4   53               PUSH EBX
 *  01D9F1E5   56               PUSH ESI
 *  01D9F1E6   57               PUSH EDI
 *  01D9F1E7   8BF9             MOV EDI,ECX
 *  01D9F1E9   8B17             MOV EDX,DWORD PTR DS:[EDI]
 *  01D9F1EB   8BC2             MOV EAX,EDX
 *  01D9F1ED   83E0 FC          AND EAX,0xFFFFFFFC
 *  01D9F1F0   8945 FC          MOV DWORD PTR SS:[EBP-0x4],EAX
 *  01D9F1F3   33C0             XOR EAX,EAX
 *  01D9F1F5   83E2 03          AND EDX,0x3
 *  01D9F1F8   2BD0             SUB EDX,EAX
 *  01D9F1FA   74 1B            JE SHORT .01D9F217
 *  01D9F1FC   4A               DEC EDX
 *  01D9F1FD   74 08            JE SHORT .01D9F207
 *  01D9F1FF   4A               DEC EDX
 *  01D9F200   75 1A            JNZ SHORT .01D9F21C
 *  01D9F202   8B47 04          MOV EAX,DWORD PTR DS:[EDI+0x4]
 *  01D9F205   EB 15            JMP SHORT .01D9F21C
 *  01D9F207   8B0D 04EA6902    MOV ECX,DWORD PTR DS:[0x269EA04]
 *  01D9F20D   8B01             MOV EAX,DWORD PTR DS:[ECX]
 *  01D9F20F   8B50 3C          MOV EDX,DWORD PTR DS:[EAX+0x3C]
 *  01D9F212   57               PUSH EDI
 *  01D9F213   FFD2             CALL EDX
 *  01D9F215   EB 05            JMP SHORT .01D9F21C
 *  01D9F217   A1 04EA6902      MOV EAX,DWORD PTR DS:[0x269EA04]
 *  01D9F21C   8B5D 0C          MOV EBX,DWORD PTR SS:[EBP+0xC]
 *  01D9F21F   85DB             TEST EBX,EBX
 *  01D9F221   75 14            JNZ SHORT .01D9F237
 *  01D9F223   6A 01            PUSH 0x1
 *  01D9F225   68 10CB5902      PUSH .0259CB10
 *  01D9F22A   FF15 70653201    CALL DWORD PTR DS:[0x1326570]            ; kernel32.InterlockedExchangeAdd
 *  01D9F230   BE 0CCB5902      MOV ESI,.0259CB0C
 *  01D9F235   EB 1F            JMP SHORT .01D9F256
 *  01D9F237   8B10             MOV EDX,DWORD PTR DS:[EAX]
 *  01D9F239   8B52 28          MOV EDX,DWORD PTR DS:[EDX+0x28]
 *  01D9F23C   6A 00            PUSH 0x0
 *  01D9F23E   8D4B 0C          LEA ECX,DWORD PTR DS:[EBX+0xC]
 *  01D9F241   51               PUSH ECX
 *  01D9F242   8BC8             MOV ECX,EAX
 *  01D9F244   FFD2             CALL EDX
 *  01D9F246   C64418 08 00     MOV BYTE PTR DS:[EAX+EBX+0x8],0x0
 *  01D9F24B   C740 04 01000000 MOV DWORD PTR DS:[EAX+0x4],0x1
 *  01D9F252   8918             MOV DWORD PTR DS:[EAX],EBX
 *  01D9F254   8BF0             MOV ESI,EAX
 *  01D9F256   8B45 08          MOV EAX,DWORD PTR SS:[EBP+0x8]  ; jichi: source size
 *  01D9F259   53               PUSH EBX
 *  01D9F25A   50               PUSH EAX
 *  01D9F25B   8D4E 08          LEA ECX,DWORD PTR DS:[ESI+0x8]
 *  01D9F25E   51               PUSH ECX
 *  01D9F25F   E8 CEAE2A00      CALL .0204A132                           ; JMP to msvcr100.memcpy, jichi: text found here
 *  01D9F264   8B07             MOV EAX,DWORD PTR DS:[EDI]
 *  01D9F266   83E0 03          AND EAX,0x3
 *  01D9F269   0BF0             OR ESI,EAX
 *  01D9F26B   83C4 0C          ADD ESP,0xC
 *  01D9F26E   8937             MOV DWORD PTR DS:[EDI],ESI
 *  01D9F270   8B75 FC          MOV ESI,DWORD PTR SS:[EBP-0x4]
 *  01D9F273   6A FF            PUSH -0x1
 *  01D9F275   8D56 04          LEA EDX,DWORD PTR DS:[ESI+0x4]
 *  01D9F278   52               PUSH EDX
 *  01D9F279   FF15 70653201    CALL DWORD PTR DS:[0x1326570]            ; kernel32.InterlockedExchangeAdd
 *  01D9F27F   48               DEC EAX
 *  01D9F280   75 0E            JNZ SHORT .01D9F290
 *  01D9F282   8B0D 04EA6902    MOV ECX,DWORD PTR DS:[0x269EA04]
 *  01D9F288   8B01             MOV EAX,DWORD PTR DS:[ECX]
 *  01D9F28A   8B50 30          MOV EDX,DWORD PTR DS:[EAX+0x30]
 *  01D9F28D   56               PUSH ESI
 *  01D9F28E   FFD2             CALL EDX
 *  01D9F290   5F               POP EDI
 *  01D9F291   5E               POP ESI
 *  01D9F292   5B               POP EBX
 *  01D9F293   8BE5             MOV ESP,EBP
 *  01D9F295   5D               POP EBP
 *  01D9F296   C2 0800          RETN 0x8
 *  01D9F299   CC               INT3
 *  01D9F29A   CC               INT3
 *  01D9F29B   CC               INT3
 *  01D9F29C   CC               INT3
 *  01D9F29D   CC               INT3
 *
 *  Function stack when memcpy is called
 *  0057C588   1C3E2B10
 *  0057C58C   1C30FBA4
 *  0057C590  /0057C5B4
 *  0057C594  |012FF264  RETURN to .012FF264 from .015AA132
 *  0057C598  |1C3E2B18
 *  0057C59C  |1C3E2A70
 *  0057C5A0  |00000094
 *  0057C5A4  |1C3E2A70
 *  0057C5A8  |1C3E2A70
 *  0057C5AC  |1C30FBCC
 *  0057C5B0  |1C3012A0
 *  0057C5B4  ]0057C5C8
 *  0057C5B8  |012FF2C2  RETURN to .012FF2C2 from .012FF1E0 ; jichi: offset +9
 *  0057C5BC  |1C3E2A70
 *  0057C5C0  |00000094
 *  0057C5C4  |1C30FB10
 *  0057C5C8  ]0057CE88
 *  0057C5CC  |013AE74D  RETURN to .013AE74D from .012FF2A0 ; jichi: offset +14
 *  0057C5D0  |1C3E2A70
 *  0057C5D4  |1C30FB10
 *  0057C5D8  |1C310930
 *
 *  Caller of the scenario thread
 *
 *  01C8F2B1   8A10             MOV DL,BYTE PTR DS:[EAX]
 *  01C8F2B3   40               INC EAX
 *  01C8F2B4   84D2             TEST DL,DL
 *  01C8F2B6  ^75 F9            JNZ SHORT .01C8F2B1
 *  01C8F2B8   2BC7             SUB EAX,EDI
 *  01C8F2BA   5F               POP EDI
 *  01C8F2BB   50               PUSH EAX
 *  01C8F2BC   56               PUSH ESI
 *  01C8F2BD   E8 1EFFFFFF      CALL .01C8F1E0  ; jichi: scenario thread
 *  01C8F2C2   5E               POP ESI
 *  01C8F2C3   5D               POP EBP
 *  01C8F2C4   C2 0400          RETN 0x4
 *  01C8F2C7   33C0             XOR EAX,EAX
 *  01C8F2C9   50               PUSH EAX
 *  01C8F2CA   56               PUSH ESI
 *  01C8F2CB   E8 10FFFFFF      CALL .01C8F1E0
 *  01C8F2D0   5E               POP ESI
 *  01C8F2D1   5D               POP EBP
 *  01C8F2D2   C2 0400          RETN 0x4
 *  01C8F2D5   CC               INT3
 *
 *  Caller of the other thread
 *  01CEA110   57               PUSH EDI
 *  01CEA111   56               PUSH ESI
 *  01CEA112   E8 C950FAFF      CALL .01C8F1E0  ; jichi: other thread
 *  01CEA117   85F6             TEST ESI,ESI
 *  01CEA119   74 0E            JE SHORT .01CEA129
 *  01CEA11B   8B0D 04EA5802    MOV ECX,DWORD PTR DS:[0x258EA04]
 *  01CEA121   8B11             MOV EDX,DWORD PTR DS:[ECX]
 *  01CEA123   8B42 30          MOV EAX,DWORD PTR DS:[EDX+0x30]
 *  01CEA126   56               PUSH ESI
 *  01CEA127   FFD0             CALL EAX
 *  01CEA129   5F               POP EDI
 *  01CEA12A   5E               POP ESI
 *  01CEA12B   B0 01            MOV AL,0x1
 *  01CEA12D   5B               POP EBX
 *  01CEA12E   8BE5             MOV ESP,EBP
 *  01CEA130   5D               POP EBP
 *  01CEA131   C2 0400          RETN 0x4
 *  01CEA134   CC               INT3
 *  01CEA135   CC               INT3
 *
 *  Caller's caler of the scenario thread:
 *  017DE736   838E 90000000 02 OR DWORD PTR DS:[ESI+0x90],0x2
 *  017DE73D   C645 0C 01       MOV BYTE PTR SS:[EBP+0xC],0x1
 *  017DE741   57               PUSH EDI
 *  017DE742   8D8E 94000000    LEA ECX,DWORD PTR DS:[ESI+0x94]
 *  017DE748   E8 530BF5FF      CALL .0172F2A0
 *  017DE74D   807D 0C 00       CMP BYTE PTR SS:[EBP+0xC],0x0
 *  017DE751   74 0C            JE SHORT .017DE75F
 *  017DE753   818E 90000000 00>OR DWORD PTR DS:[ESI+0x90],0x1000
 *  017DE75D   EB 0A            JMP SHORT .017DE769
 *  017DE75F   81A6 90000000 FF>AND DWORD PTR DS:[ESI+0x90],0xFFFFEFFF
 *  017DE769   8B9E 94000000    MOV EBX,DWORD PTR DS:[ESI+0x94]
 *  017DE76F   8B8E 90000000    MOV ECX,DWORD PTR DS:[ESI+0x90]
 *  017DE775   83E3 FC          AND EBX,0xFFFFFFFC
 *
 *  This is the function being called that is responsible to allocate new memory
 *  00B3707C   CC               INT3
 *  00B3707D   CC               INT3
 *  00B3707E   CC               INT3
 *  00B3707F   CC               INT3
 *  00B37080   55               PUSH EBP
 *  00B37081   8BEC             MOV EBP,ESP
 *  00B37083   57               PUSH EDI
 *  00B37084   8BF9             MOV EDI,ECX
 *  00B37086   807F 64 00       CMP BYTE PTR DS:[EDI+0x64],0x0
 *  00B3708A   74 28            JE SHORT .00B370B4
 *  00B3708C   56               PUSH ESI
 *  00B3708D   8D77 4C          LEA ESI,DWORD PTR DS:[EDI+0x4C]
 *  00B37090   56               PUSH ESI
 *  00B37091   FF15 7C650C00    CALL DWORD PTR DS:[0xC657C]              ; ntdll.RtlEnterCriticalSection
 *  00B37097   8B45 08          MOV EAX,DWORD PTR SS:[EBP+0x8]
 *  00B3709A   8B4F 68          MOV ECX,DWORD PTR DS:[EDI+0x68]
 *  00B3709D   50               PUSH EAX
 *  00B3709E   E8 4DFE0200      CALL .00B66EF0
 *  00B370A3   56               PUSH ESI
 *  00B370A4   8BF8             MOV EDI,EAX
 *  00B370A6   FF15 84650C00    CALL DWORD PTR DS:[0xC6584]              ; ntdll.RtlLeaveCriticalSection
 *  00B370AC   5E               POP ESI
 *  00B370AD   8BC7             MOV EAX,EDI
 *  00B370AF   5F               POP EDI
 *  00B370B0   5D               POP EBP
 *  00B370B1   C2 0800          RETN 0x8
 *  00B370B4   8B4D 08          MOV ECX,DWORD PTR SS:[EBP+0x8]
 *  00B370B7   51               PUSH ECX
 *  00B370B8   8B4F 68          MOV ECX,DWORD PTR DS:[EDI+0x68]
 *  00B370BB   E8 30FE0200      CALL .00B66EF0
 *  00B370C0   5F               POP EDI
 *  00B370C1   5D               POP EBP
 *  00B370C2   C2 0800          RETN 0x8
 *  00B370C5   CC               INT3
 *  00B370C6   CC               INT3
 *  00B370C7   CC               INT3
 */
bool attach(ulong startAddress, ulong stopAddress) // attach scenario
{
  {
    const uint8_t bytes[] = {
      0xEB, 0x1F,       // 01D9F235   EB 1F            JMP SHORT .01D9F256
      0x8B,0x10,        // 01D9F237   8B10             MOV EDX,DWORD PTR DS:[EAX]
      0x8B,0x52, 0x28,  // 01D9F239   8B52 28          MOV EDX,DWORD PTR DS:[EDX+0x28]
      0x6A, 0x00,       // 01D9F23C   6A 00            PUSH 0x0
      0x8D,0x4B, 0x0C,  // 01D9F23E   8D4B 0C          LEA ECX,DWORD PTR DS:[EBX+0xC]
      0x51,             // 01D9F241   51               PUSH ECX
      0x8B,0xC8,        // 01D9F242   8BC8             MOV ECX,EAX
      0xFF,0xD2         // 01D9F244   FFD2             CALL EDX
    };
    ulong addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
    if (!addr)
      return false;
    Private::parentReturnAddress_ = addr + sizeof(bytes);
  }

  {
    const uint8_t bytes[] = {
      0x55,                  // 00B37080   55               PUSH EBP
      0x8B,0xEC,             // 00B37081   8BEC             MOV EBP,ESP
      0x57,                  // 00B37083   57               PUSH EDI
      0x8B,0xF9,             // 00B37084   8BF9             MOV EDI,ECX
      0x80,0x7F, 0x64, 0x00, // 00B37086   807F 64 00       CMP BYTE PTR DS:[EDI+0x64],0x0
      0x74, 0x28,            // 00B3708A   74 28            JE SHORT .00B370B4
      0x56,                  // 00B3708C   56               PUSH ESI
      0x8D,0x77, 0x4C,       // 00B3708D   8D77 4C          LEA ESI,DWORD PTR DS:[EDI+0x4C]
      0x56,                  // 00B37090   56               PUSH ESI
      0xFF,0x15 //7C650C00   // 00B37091   FF15 7C650C00    CALL DWORD PTR DS:[0xC657C]              ; ntdll.RtlEnterCriticalSection
    };
    ulong addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
    if (!addr)
      return false;
    Private::returnAddress_ = addr + sizeof(bytes) + 4;
  }
  //ulong fun = (ulong)::RtlEnterCriticalSection;
  ulong fun = Engine::getModuleFunction("ntdll.dll", "RtlEnterCriticalSection"); // resolve function addr at runtime
  return fun && winhook::hook_before(fun, Private::hookBefore);
}

} // namespace ScenarioHook

} // unnamed namespace

/** Public class */

bool LovaEngine::attach()
{
  ulong startAddress, stopAddress;
  if (!Engine::getProcessMemoryRange(&startAddress, &stopAddress))
    return false;
  if (!ScenarioHook::attach(startAddress, stopAddress))
    return false;
  //HijackManager::instance()->attachFunction((ulong)::CreateFontIndirectW);
  return true;
}

// EOF

#if 0
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  return winhook::hook_before(addr, Private::hookBefore);
#endif //0
#if 0
  addr = Engine::getModuleFunction("msvcr100.dll", "memcpy");
  //NtInspect::getModuleExportFunctionA("msvcr100.dll", "memcpy");
  if (!addr)
    return false;
  return Private::old_memcpy = (Private::memcpy_fun_t)winhook::replace_fun(addr, (ulong)Private::new_memcpy);
#endif //0

#if 0
  {
    const uint8_t bytes[] = {
      0xC6,0x44,0x18, 0x08, 0x00,           // 012FF246   C64418 08 00     MOV BYTE PTR DS:[EAX+EBX+0x8],0x0
      0xC7,0x40, 0x04, 0x01,0x00,0x00,0x00, // 012FF24B   C740 04 01000000 MOV DWORD PTR DS:[EAX+0x4],0x1
      0x89,0x18,                            // 012FF252   8918             MOV DWORD PTR DS:[EAX],EBX
      0x8B,0xF0,                            // 012FF254   8BF0             MOV ESI,EAX
      0x8B,0x45, 0x08,                      // 012FF256   8B45 08          MOV EAX,DWORD PTR SS:[EBP+0x8]
      0x53,                                 // 012FF259   53               PUSH EBX
      0x50,                                 // 012FF25A   50               PUSH EAX
      0x8D,0x4E, 0x08,                      // 012FF25B   8D4E 08          LEA ECX,DWORD PTR DS:[ESI+0x8]
      0x51,                                 // 012FF25E   51               PUSH ECX
      0xE8 //CEAE2A00                       // 012FF25F   E8 CEAE2A00      CALL .015AA132                           ; JMP to msvcr100.memcpy, copied here
    };
    ulong addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
    if (!addr)
      return false;
    Private::returnAddress_ = addr + sizeof(bytes) + 4;
  }
#endif 0

#if 0
  typedef void *(* memcpy_fun_t)(void *, const void *, size_t);
  memcpy_fun_t old_memcpy;

  ulong returnAddress_;
  void *new_memcpy(void *dst, const void *src, size_t size)
  {
    // See: http://stackoverflow.com/questions/1847053/how-to-get-address-of-base-stack-pointer
    //volatile ulong frame = 0; // a portable way to get current stack pointer
    auto stack = (ulong *)&dst - 1; // use arg1 to get esp
    ulong retaddr = *stack;
    if (retaddr == returnAddress_) {
      auto text = static_cast<const char *>(src);
      if (size > 0 && !Util::allAscii(text)) {
        //auto stack = &frame;  // stack is the original esp
        //for (int i = 0; ; i++)    // get the original esp
        //  if (stack[-i] == retaddr) {
        //    stack -= i;
        //    break;
        //  }

        // 00B06F2D   8BCE             MOV ECX,ESI
        // 00B06F2F   52               PUSH EDX
        // 00B06F30   E8 5BFFFFFF      CALL .00B06E90  ; jichi: caller of the scenario thread
        // 00B06F35   85C0             TEST EAX,EAX
        // 00B06F37   75 33            JNZ SHORT .00B06F6C
        auto role = Engine::OtherRole;
        //auto stack = (ulong *)_AddressOfReturnAddress(); // pointed to esp just after calling function
        auto callerReturnAddress1 = stack[9], // return address of the caller
             callerReturnAddress2 = stack[14]; // return address of the caller's caller
        if (Engine::isAddressReadable(callerReturnAddress1) &&
            Engine::isAddressReadable(callerReturnAddress2) &&
            *(uint8_t *)callerReturnAddress1 == s1_pop_esi &&   // use the instruction before call as split
            *(DWORD *)callerReturnAddress2 == 0x000c7d80 &&     // 017DE74D   807D 0C 00       CMP BYTE PTR SS:[EBP+0xC],0x0
            !is_other_texts(text))
          role = Engine::ScenarioRole;
        auto split = callerReturnAddress2;
        //role = Engine::OtherRole; // FIXME: split scenario role out
        auto sig = Engine::hashThreadSignature(role, split);
        QString oldText = QString::fromUtf8(text, size),
                newText = EngineController::instance()->dispatchTextW(oldText, role, sig);
        if (!newText.isEmpty() && newText != oldText) {
          QByteArray data = newText.toUtf8();
          while (data.size() < size)
            data.push_back(' '); // padding zero
          return old_memcpy(dst, data.constData(), size); // text being truncated to size
        }
      }
    }
    return old_memcpy(dst, src, size);
  }
#endif 0

#if 0
  bool hookBefore(winhook::hook_stack *s)
  {
    return true;
    static QByteArray data_;
    auto text = (LPCSTR)s->stack[1]; // arg1 text
    int size = s->stack[2]; // arg2 size
    if (size <= 0 || !text)
      return true;
    enum { role = Engine::ScenarioRole };
    auto retaddr = s->stack[0];
    auto sig = Engine::hashThreadSignature(role, retaddr);
    QString oldText = QString::fromUtf8(text, size),
            newText = EngineController::instance()->dispatchTextW(oldText, role, sig);
    if (newText.isEmpty() || newText == oldText)
      return true;
    data_ = newText.toUtf8();
    s->stack[1] = (ulong)data_.constData(); // arg1 text
    s->stack[2] = data_.size(); // arg2 size
    return true;
  }
#endif // 0

