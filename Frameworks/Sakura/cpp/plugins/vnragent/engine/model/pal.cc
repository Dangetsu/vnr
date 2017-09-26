// pal.cc
// 7/18/2015 jichi
#include "engine/model/pal.h"
#include "engine/enginecontroller.h"
#include "engine/enginedef.h"
#include "engine/enginehash.h"
#include "engine/engineutil.h"
#include "hijack/hijackmanager.h"
#include "memdbg/memsearch.h"
#include "util/textutil.h"
#include "winhook/hookcode.h"
#include <qt_windows.h>
#include <QtCore/QRegExp>
#include <cstdint>

#define DEBUG "model/pal"
#include "sakurakit/skdebug.h"

/** Private data */

namespace { // unnamed

namespace ScenarioHook {
namespace Private {

  template <typename strT>
  strT trim(strT text, int *size)
  {
    //int length = ::strlen(text);
    auto length = *size;
    if (text[0] == '<' && text[1] == 'c') {
      auto p = ::strchr(text + 2, '>');
      if (!p)
        return text;
      p++;
      length -= p - text;
      text = p; // skip leading '<c .. >'
    }

    if (text[length - 1] == '>' && text[length - 2] == 'c' && text[length - 3] == '/' && text[length - 4] == '<')
      length -= 4; // skip the trailing </c>'

    *size = length;
    return text;
  }

  bool hookBefore(winhook::hook_stack *s)
  {
    //std::unordered_set<qint64> hashes_; // hashes of rendered text
    auto text = (LPSTR)s->stack[2]; // text in arg2
    if (!text || !*text)
      return true;

    int size = ::strlen(text),
        trimmedSize = size;
    auto trimmedText = trim(text, &trimmedSize);
    if (trimmedSize <= 0 || !trimmedText || !*trimmedText)
      return true;

    // 01237728   8B08             MOV ECX,DWORD PTR DS:[EAX]  ; jichi: scenario or name
    // 0123772A   51               PUSH ECX
    // 0123772B   E8 80F3FFFF      CALL .01236AB0  ; jichi: scenario text
    // 01237730   83C4 28          ADD ESP,0x28

    auto retaddr = s->stack[0];
    auto role = Engine::OtherRole;
    if (*(WORD *)(retaddr - 8) == 0x088b) // 8b08  mov ecx,dword ptr ds:[eax]
      role = s->stack[3] ? Engine::ScenarioRole : Engine::NameRole;

    //qint64 hash = 0;
    //if (role == Engine::OtherRole) {
    //   hash = Engine::hashCharArray(text);
    //   if (hashes_.find(hash) != hashes_.end())
    //     return true;
    //}

    auto sig = Engine::hashThreadSignature(role, retaddr);

    QByteArray oldData(trimmedText, trimmedSize),
               newData = EngineController::instance()->dispatchTextA(oldData, role, sig);
    if (newData == oldData)
      return true;

    int prefixSize = trimmedText - text,
        suffixSize = size - prefixSize - trimmedSize;
    //if (prefixSize)
    //  newData.prepend(text, prefixSize);
    if (suffixSize)
      newData.append(trimmedText + trimmedSize, suffixSize);

    ::strcpy(trimmedText, newData.constData());
    return true;
  }
} // namespace Private

/**
 *  Sample game: 時計仕掛けのレイライン
 *  There are three functions in Pal.dll that containing "text":
 *  - PalSpriteCreateTextEx
 *  - PalSpriteCreateText
 *  - PalFontDrawText
 *
 *  PalFontDrawText is used to draw scenario text character-by-character.
 *  The hooked function is found in main processing by debugging PalFontDrawText.
 *  It is the caller of the caller of PalFontDrawText, and text is in arg2, which can be overwritten.
 *
 *  002C6AAC   CC               INT3
 *  002C6AAD   CC               INT3
 *  002C6AAE   CC               INT3
 *  002C6AAF   CC               INT3
 *  002C6AB0   55               PUSH EBP
 *  002C6AB1   8BEC             MOV EBP,ESP
 *  002C6AB3   83EC 78          SUB ESP,0x78
 *  002C6AB6   A1 8C002F00      MOV EAX,DWORD PTR DS:[0x2F008C]
 *  002C6ABB   33C5             XOR EAX,EBP
 *  002C6ABD   8945 F8          MOV DWORD PTR SS:[EBP-0x8],EAX
 *  002C6AC0   53               PUSH EBX
 *  002C6AC1   57               PUSH EDI
 *  002C6AC2   E8 19A70000      CALL .002D11E0
 *  002C6AC7   83E0 10          AND EAX,0x10
 *  002C6ACA   74 07            JE SHORT .002C6AD3
 *  002C6ACC   33C0             XOR EAX,EAX
 *  002C6ACE   E9 4B060000      JMP .002C711E
 *  002C6AD3   C745 D0 00000000 MOV DWORD PTR SS:[EBP-0x30],0x0
 *  002C6ADA   33C0             XOR EAX,EAX
 *  002C6ADC   8945 D4          MOV DWORD PTR SS:[EBP-0x2C],EAX
 *  002C6ADF   C645 E0 00       MOV BYTE PTR SS:[EBP-0x20],0x0
 *  002C6AE3   33C9             XOR ECX,ECX
 *  002C6AE5   66:894D E1       MOV WORD PTR SS:[EBP-0x1F],CX
 *  002C6AE9   837D 10 00       CMP DWORD PTR SS:[EBP+0x10],0x0
 *  002C6AED   74 0A            JE SHORT .002C6AF9
 *  002C6AEF   8B55 10          MOV EDX,DWORD PTR SS:[EBP+0x10]
 *  002C6AF2   8B02             MOV EAX,DWORD PTR DS:[EDX]
 *  002C6AF4   8945 8C          MOV DWORD PTR SS:[EBP-0x74],EAX
 *  002C6AF7   EB 07            JMP SHORT .002C6B00
 *  002C6AF9   C745 8C 00000000 MOV DWORD PTR SS:[EBP-0x74],0x0
 *  002C6B00   8B4D 8C          MOV ECX,DWORD PTR SS:[EBP-0x74]
 *  002C6B03   894D D8          MOV DWORD PTR SS:[EBP-0x28],ECX
 *  002C6B06   837D 14 00       CMP DWORD PTR SS:[EBP+0x14],0x0
 *  002C6B0A   74 0A            JE SHORT .002C6B16
 *  002C6B0C   8B55 14          MOV EDX,DWORD PTR SS:[EBP+0x14]
 *  002C6B0F   8B02             MOV EAX,DWORD PTR DS:[EDX]
 *  002C6B11   8945 88          MOV DWORD PTR SS:[EBP-0x78],EAX
 *  002C6B14   EB 07            JMP SHORT .002C6B1D
 *  002C6B16   C745 88 00000000 MOV DWORD PTR SS:[EBP-0x78],0x0
 *  002C6B1D   8B4D 88          MOV ECX,DWORD PTR SS:[EBP-0x78]
 *  002C6B20   894D DC          MOV DWORD PTR SS:[EBP-0x24],ECX
 *  002C6B23   C745 BC 00000000 MOV DWORD PTR SS:[EBP-0x44],0x0
 *  002C6B2A   C745 CC 00000000 MOV DWORD PTR SS:[EBP-0x34],0x0
 *  002C6B31   837D 08 00       CMP DWORD PTR SS:[EBP+0x8],0x0
 *  002C6B35   74 1A            JE SHORT .002C6B51
 *  002C6B37   8D55 E4          LEA EDX,DWORD PTR SS:[EBP-0x1C]
 *  002C6B3A   52               PUSH EDX
 *  002C6B3B   8D45 C0          LEA EAX,DWORD PTR SS:[EBP-0x40]
 *  002C6B3E   50               PUSH EAX
 *  002C6B3F   8B4D 08          MOV ECX,DWORD PTR SS:[EBP+0x8]
 *  002C6B42   51               PUSH ECX
 *  002C6B43   FF15 FC332F00    CALL DWORD PTR DS:[0x2F33FC]             ; _4.10010BF0
 *  002C6B49   83C4 0C          ADD ESP,0xC
 *  002C6B4C   8945 B8          MOV DWORD PTR SS:[EBP-0x48],EAX
 *  002C6B4F   EB 0C            JMP SHORT .002C6B5D
 *  002C6B51   8B55 18          MOV EDX,DWORD PTR SS:[EBP+0x18]
 *  002C6B54   8955 C0          MOV DWORD PTR SS:[EBP-0x40],EDX
 *  002C6B57   8B45 1C          MOV EAX,DWORD PTR SS:[EBP+0x1C]
 *  002C6B5A   8945 E4          MOV DWORD PTR SS:[EBP-0x1C],EAX
 *  002C6B5D   FF15 74342F00    CALL DWORD PTR DS:[0x2F3474]             ; _4.10009150
 *  002C6B63   837D 24 00       CMP DWORD PTR SS:[EBP+0x24],0x0
 *  002C6B67   74 14            JE SHORT .002C6B7D
 *  002C6B69   8B4D 24          MOV ECX,DWORD PTR SS:[EBP+0x24]
 *  002C6B6C   83E9 02          SUB ECX,0x2
 *  002C6B6F   894D B4          MOV DWORD PTR SS:[EBP-0x4C],ECX
 *  002C6B72   8B55 20          MOV EDX,DWORD PTR SS:[EBP+0x20]
 *  002C6B75   0355 24          ADD EDX,DWORD PTR SS:[EBP+0x24]
 *  002C6B78   8955 C8          MOV DWORD PTR SS:[EBP-0x38],EDX
 *  002C6B7B   EB 10            JMP SHORT .002C6B8D
 *  002C6B7D   C745 B4 00000000 MOV DWORD PTR SS:[EBP-0x4C],0x0
 *  002C6B84   8B45 20          MOV EAX,DWORD PTR SS:[EBP+0x20]
 *  002C6B87   83C0 02          ADD EAX,0x2
 *  002C6B8A   8945 C8          MOV DWORD PTR SS:[EBP-0x38],EAX
 *  002C6B8D   8B4D 20          MOV ECX,DWORD PTR SS:[EBP+0x20]
 *  002C6B90   894D C4          MOV DWORD PTR SS:[EBP-0x3C],ECX
 *  002C6B93   8B55 C8          MOV EDX,DWORD PTR SS:[EBP-0x38]
 *  002C6B96   8955 B0          MOV DWORD PTR SS:[EBP-0x50],EDX
 *  002C6B99   8B45 0C          MOV EAX,DWORD PTR SS:[EBP+0xC]
 *  002C6B9C   0FB608           MOVZX ECX,BYTE PTR DS:[EAX]
 *  002C6B9F   85C9             TEST ECX,ECX
 *  002C6BA1   0F84 E5040000    JE .002C708C
 *
 *  Name/scenario/history texts all have different return addresses.
 *  I am not sure for choice texts.
 *
 *  Scenario:
 *
 *  0C11FBEC   01237730  RETURN to .01237730 from .01236AB0
 *  0C11FBF0   06F64558
 *  0C11FBF4   0BDF0D58
 *  0C11FBF8   0BDF0BEC ; jichi: only name is not zero
 *  0C11FBFC   0BDF0BF0
 *  0C11FC00   00000300
 *  0C11FC04   00000080
 *  0C11FC08   00000020
 *  0C11FC0C   00000008
 *  0C11FC10   0BDF0C44
 *  0C11FC14   0BDF0C20
 *
 *  EAX 01267A08 .01267A08
 *  ECX 06F64558
 *  EDX 0BDF035C
 *  EBX 00000000
 *  ESP 0C11FBEC
 *  EBP 0C11FE24
 *  ESI 06F58A58
 *  EDI 013C2A70
 *  EIP 01236AB0 .01236AB0
 *
 *  0123768B   E8 B0F0FFFF      CALL .01236740
 *  01237690   83C4 0C          ADD ESP,0xC
 *  01237693   8D95 FCFDFFFF    LEA EDX,DWORD PTR SS:[EBP-0x204]
 *  01237699   52               PUSH EDX
 *  0123769A   8B45 08          MOV EAX,DWORD PTR SS:[EBP+0x8]
 *  0123769D   05 000A0000      ADD EAX,0xA00
 *  012376A2   50               PUSH EAX
 *  012376A3   E8 88FAFFFF      CALL .01237130
 *  012376A8   83C4 08          ADD ESP,0x8
 *  012376AB   8B4D 0C          MOV ECX,DWORD PTR SS:[EBP+0xC]
 *  012376AE   C781 74080000 00>MOV DWORD PTR DS:[ECX+0x874],0x0
 *  012376B8   8B55 0C          MOV EDX,DWORD PTR SS:[EBP+0xC]
 *  012376BB   C782 90080000 00>MOV DWORD PTR DS:[EDX+0x890],0x0
 *  012376C5   8B45 0C          MOV EAX,DWORD PTR SS:[EBP+0xC]
 *  012376C8   C780 94080000 00>MOV DWORD PTR DS:[EAX+0x894],0x0
 *  012376D2   8B4D 0C          MOV ECX,DWORD PTR SS:[EBP+0xC]
 *  012376D5   81C1 C4080000    ADD ECX,0x8C4
 *  012376DB   51               PUSH ECX
 *  012376DC   8B55 0C          MOV EDX,DWORD PTR SS:[EBP+0xC]
 *  012376DF   81C2 E8080000    ADD EDX,0x8E8
 *  012376E5   52               PUSH EDX
 *  012376E6   8B45 0C          MOV EAX,DWORD PTR SS:[EBP+0xC]
 *  012376E9   8B48 10          MOV ECX,DWORD PTR DS:[EAX+0x10]
 *  012376EC   51               PUSH ECX
 *  012376ED   8B55 0C          MOV EDX,DWORD PTR SS:[EBP+0xC]
 *  012376F0   8B42 0C          MOV EAX,DWORD PTR DS:[EDX+0xC]
 *  012376F3   50               PUSH EAX
 *  012376F4   8B4D 0C          MOV ECX,DWORD PTR SS:[EBP+0xC]
 *  012376F7   8B51 20          MOV EDX,DWORD PTR DS:[ECX+0x20]
 *  012376FA   52               PUSH EDX
 *  012376FB   8B45 0C          MOV EAX,DWORD PTR SS:[EBP+0xC]
 *  012376FE   8B48 1C          MOV ECX,DWORD PTR DS:[EAX+0x1C]
 *  01237701   51               PUSH ECX
 *  01237702   8B55 0C          MOV EDX,DWORD PTR SS:[EBP+0xC]
 *  01237705   81C2 94080000    ADD EDX,0x894
 *  0123770B   52               PUSH EDX
 *  0123770C   8B45 0C          MOV EAX,DWORD PTR SS:[EBP+0xC]
 *  0123770F   05 90080000      ADD EAX,0x890
 *  01237714   50               PUSH EAX
 *  01237715   8B4D 08          MOV ECX,DWORD PTR SS:[EBP+0x8]
 *  01237718   81C1 000A0000    ADD ECX,0xA00
 *  0123771E   51               PUSH ECX
 *  0123771F   8B55 0C          MOV EDX,DWORD PTR SS:[EBP+0xC]
 *  01237722   8B82 A0080000    MOV EAX,DWORD PTR DS:[EDX+0x8A0]
 *  01237728   8B08             MOV ECX,DWORD PTR DS:[EAX]  ; jichi: scenario or name
 *  0123772A   51               PUSH ECX
 *  0123772B   E8 80F3FFFF      CALL .01236AB0  ; jichi: scenario text
 *  01237730   83C4 28          ADD ESP,0x28
 *  01237733   8B55 0C          MOV EDX,DWORD PTR SS:[EBP+0xC]
 *  01237736   8982 7C080000    MOV DWORD PTR DS:[EDX+0x87C],EAX
 *  0123773C   8B85 F4FDFFFF    MOV EAX,DWORD PTR SS:[EBP-0x20C]
 *  01237742   8B4D 0C          MOV ECX,DWORD PTR SS:[EBP+0xC]
 *  01237745   8B50 20          MOV EDX,DWORD PTR DS:[EAX+0x20]
 *  01237748   0B91 60080000    OR EDX,DWORD PTR DS:[ECX+0x860]
 *  0123774E   74 1D            JE SHORT .0123776D
 *  01237750   8B45 0C          MOV EAX,DWORD PTR SS:[EBP+0xC]
 *  01237753   05 C4080000      ADD EAX,0x8C4
 *  01237758   50               PUSH EAX
 *  01237759   8B4D 0C          MOV ECX,DWORD PTR SS:[EBP+0xC]
 *  0123775C   8B91 A0080000    MOV EDX,DWORD PTR DS:[ECX+0x8A0]
 *  01237762   8B02             MOV EAX,DWORD PTR DS:[EDX]
 *  01237764   50               PUSH EAX
 *  01237765   E8 E6D2FFFF      CALL .01234A50
 *  0123776A   83C4 08          ADD ESP,0x8
 *  0123776D   6A 02            PUSH 0x2
 *  0123776F   8B4D 0C          MOV ECX,DWORD PTR SS:[EBP+0xC]
 *  01237772   81C1 FC090000    ADD ECX,0x9FC
 *  01237778   51               PUSH ECX
 *  01237779   8B55 08          MOV EDX,DWORD PTR SS:[EBP+0x8]
 *  0123777C   81C2 24550000    ADD EDX,0x5524
 *  01237782   52               PUSH EDX
 *  01237783   E8 982EFFFF      CALL .0122A620
 *  01237788   83C4 0C          ADD ESP,0xC
 *  0123778B   8B4D FC          MOV ECX,DWORD PTR SS:[EBP-0x4]
 *  0123778E   33CD             XOR ECX,EBP
 *  01237790   E8 C1D20000      CALL .01244A56
 *  01237795   8BE5             MOV ESP,EBP
 *  01237797   5D               POP EBP
 *  01237798   C3               RETN
 *  01237799   CC               INT3
 *  0123779A   CC               INT3
 *  0123779B   CC               INT3
 *  0123779C   CC               INT3
 *  0123779D   CC               INT3
 *  0123779E   CC               INT3
 *
 *  Name:
 *
 *  0C11FDF4   01237843  RETURN to .01237843 from .01236AB0
 *  0C11FDF8   06F64620
 *  0C11FDFC   0BDF0C54
 *  0C11FE00   00000000
 *  0C11FE04   00000000
 *  0C11FE08   00000400
 *  0C11FE0C   00000040
 *  0C11FE10   00000020
 *  0C11FE14   00000000
 *  0C11FE18   0BDF0C44
 *  0C11FE1C   00000000
 *  0C11FE20   06FD2E78
 *  0C11FE24  /0C11FE4C
 *  0C11FE28  |01239743  RETURN to .01239743 from .012377A0
 *  0C11FE2C  |0BDF0358
 *  0C11FE30  |0BDF035C
 *
 *  EAX 01267BE8 .01267BE8
 *  ECX 06F64620
 *  EDX 0BDF035C
 *  EBX 00000000
 *  ESP 0C11FDF4
 *  EBP 0C11FE24
 *  ESI 06F58A58
 *  EDI 013C2A70
 *  EIP 01236AB0 .01236AB0
 *
 *  0123781F   68 00040000      PUSH 0x400
 *  01237824   6A 00            PUSH 0x0
 *  01237826   6A 00            PUSH 0x0
 *  01237828   8B4D 0C          MOV ECX,DWORD PTR SS:[EBP+0xC]
 *  0123782B   81C1 F8080000    ADD ECX,0x8F8
 *  01237831   51               PUSH ECX
 *  01237832   8B55 0C          MOV EDX,DWORD PTR SS:[EBP+0xC]
 *  01237835   8B82 9C080000    MOV EAX,DWORD PTR DS:[EDX+0x89C]
 *  0123783B   8B08             MOV ECX,DWORD PTR DS:[EAX]  ; jichi: scenario or name
 *  0123783D   51               PUSH ECX
 *  0123783E   E8 6DF2FFFF      CALL .01236AB0  ; jichi: name here
 *  01237843   83C4 28          ADD ESP,0x28
 *  01237846   8B55 0C          MOV EDX,DWORD PTR SS:[EBP+0xC]
 *  01237849   8B82 68080000    MOV EAX,DWORD PTR DS:[EDX+0x868]
 *  0123784F   83C8 01          OR EAX,0x1
 *  01237852   8B4D 0C          MOV ECX,DWORD PTR SS:[EBP+0xC]
 *  01237855   8981 68080000    MOV DWORD PTR DS:[ECX+0x868],EAX
 *  0123785B   6A 01            PUSH 0x1
 *  0123785D   8B55 0C          MOV EDX,DWORD PTR SS:[EBP+0xC]
 *  01237860   81C2 F8080000    ADD EDX,0x8F8
 *  01237866   52               PUSH EDX
 *  01237867   8B45 08          MOV EAX,DWORD PTR SS:[EBP+0x8]
 *  0123786A   05 24550000      ADD EAX,0x5524
 *  0123786F   50               PUSH EAX
 *  01237870   E8 AB2DFFFF      CALL .0122A620
 *  01237875   83C4 0C          ADD ESP,0xC
 *  01237878   EB 16            JMP SHORT .01237890
 *  0123787A   6A 01            PUSH 0x1
 *  0123787C   6A 00            PUSH 0x0
 *  0123787E   8B4D 08          MOV ECX,DWORD PTR SS:[EBP+0x8]
 *  01237881   81C1 24550000    ADD ECX,0x5524
 *  01237887   51               PUSH ECX
 *  01237888   E8 932DFFFF      CALL .0122A620
 *  0123788D   83C4 0C          ADD ESP,0xC
 *  01237890   8BE5             MOV ESP,EBP
 *  01237892   5D               POP EBP
 *  01237893   C3               RETN
 *  01237894   CC               INT3
 *  01237895   CC               INT3
 *  01237896   CC               INT3
 *  01237897   CC               INT3
 *
 *  History:
 *  0C11FDEC   0122AD9F  RETURN to .0122AD9F from .01236AB0
 *  0C11FDF0   0702B140
 *  0C11FDF4   0BDF6A6F
 *  0C11FDF8   00000000
 *  0C11FDFC   00000000
 *  0C11FE00   00000300
 *  0C11FE04   00000080
 *  0C11FE08   00000020
 *  0C11FE0C   00000008
 *  0C11FE10   0C11FE30
 *
 *  EAX 0BDF587C
 *  ECX 0702B140
 *  EDX 0BDF6A6F
 *  EBX 00000000
 *  ESP 0C11FDEC
 *  EBP 0C11FE4C
 *  ESI 06F58A58
 *  EDI 013C2A70
 *  EIP 01236AB0 .01236AB0
 *
 *  0122AD7B   8B45 D0          MOV EAX,DWORD PTR SS:[EBP-0x30]
 *  0122AD7E   8B48 10          MOV ECX,DWORD PTR DS:[EAX+0x10]
 *  0122AD81   51               PUSH ECX
 *  0122AD82   6A 00            PUSH 0x0
 *  0122AD84   6A 00            PUSH 0x0
 *  0122AD86   8B55 DC          MOV EDX,DWORD PTR SS:[EBP-0x24]
 *  0122AD89   81C2 FF000000    ADD EDX,0xFF
 *  0122AD8F   52               PUSH EDX
 *  0122AD90   8B45 D4          MOV EAX,DWORD PTR SS:[EBP-0x2C]
 *  0122AD93   8B88 08080000    MOV ECX,DWORD PTR DS:[EAX+0x808]
 *  0122AD99   51               PUSH ECX
 *  0122AD9A   E8 11BD0000      CALL .01236AB0  ; jichi: history
 *  0122AD9F   83C4 28          ADD ESP,0x28
 *  0122ADA2   8D55 EC          LEA EDX,DWORD PTR SS:[EBP-0x14]
 *  0122ADA5   52               PUSH EDX
 *  0122ADA6   8B45 D4          MOV EAX,DWORD PTR SS:[EBP-0x2C]
 *  0122ADA9   8B88 08080000    MOV ECX,DWORD PTR DS:[EAX+0x808]
 *  0122ADAF   51               PUSH ECX
 *  0122ADB0   FF15 68322601    CALL DWORD PTR DS:[0x1263268]            ; .01244322
 *  0122ADB6   83C4 08          ADD ESP,0x8
 *  0122ADB9   8B55 D8          MOV EDX,DWORD PTR SS:[EBP-0x28]
 *  0122ADBC   0355 F8          ADD EDX,DWORD PTR SS:[EBP-0x8]
 *  0122ADBF   8955 D8          MOV DWORD PTR SS:[EBP-0x28],EDX
 *  0122ADC2   8B45 DC          MOV EAX,DWORD PTR SS:[EBP-0x24]
 *  0122ADC5   0FB708           MOVZX ECX,WORD PTR DS:[EAX]
 *  0122ADC8   81F9 00810000    CMP ECX,0x8100
 *  0122ADCE   74 5B            JE SHORT .0122AE2B
 *  0122ADD0   6A 00            PUSH 0x0
 *  0122ADD2   8D55 E4          LEA EDX,DWORD PTR SS:[EBP-0x1C]
 *  0122ADD5   52               PUSH EDX
 *  0122ADD6   8B45 D0          MOV EAX,DWORD PTR SS:[EBP-0x30]
 *  0122ADD9   8B48 04          MOV ECX,DWORD PTR DS:[EAX+0x4]
 *  0122ADDC   51               PUSH ECX
 *  0122ADDD   8B55 D0          MOV EDX,DWORD PTR SS:[EBP-0x30]
 *  0122ADE0   8B02             MOV EAX,DWORD PTR DS:[EDX]
 *  0122ADE2   50               PUSH EAX
 *  0122ADE3   8B4D D0          MOV ECX,DWORD PTR SS:[EBP-0x30]
 *  0122ADE6   8B51 14          MOV EDX,DWORD PTR DS:[ECX+0x14]
 *  0122ADE9   52               PUSH EDX
 *  0122ADEA   8B45 D0          MOV EAX,DWORD PTR SS:[EBP-0x30]
 *  0122ADED   8B48 10          MOV ECX,DWORD PTR DS:[EAX+0x10]
 *  0122ADF0   51               PUSH ECX
 *  0122ADF1   6A 00            PUSH 0x0
 *  0122ADF3   6A 00            PUSH 0x0
 *  0122ADF5   8B55 DC          MOV EDX,DWORD PTR SS:[EBP-0x24]
 *  0122ADF8   52               PUSH EDX
 *  0122ADF9   8B45 D4          MOV EAX,DWORD PTR SS:[EBP-0x2C]
 *  0122ADFC   8B88 08080000    MOV ECX,DWORD PTR DS:[EAX+0x808]
 *  0122AE02   51               PUSH ECX
 *  0122AE03   E8 A8BC0000      CALL .01236AB0
 *  0122AE08   83C4 28          ADD ESP,0x28
 *  0122AE0B   8D55 EC          LEA EDX,DWORD PTR SS:[EBP-0x14]
 *  0122AE0E   52               PUSH EDX
 *  0122AE0F   8B45 D4          MOV EAX,DWORD PTR SS:[EBP-0x2C]
 *  0122AE12   8B88 08080000    MOV ECX,DWORD PTR DS:[EAX+0x808]
 *  0122AE18   51               PUSH ECX
 *  0122AE19   FF15 68322601    CALL DWORD PTR DS:[0x1263268]            ; .01244322
 *  0122AE1F   83C4 08          ADD ESP,0x8
 *
 *  0122A0C8   6A 00            PUSH 0x0
 *  0122A0CA   6A 00            PUSH 0x0
 *  0122A0CC   8B45 DC          MOV EAX,DWORD PTR SS:[EBP-0x24]
 *  0122A0CF   05 FF000000      ADD EAX,0xFF
 *  0122A0D4   50               PUSH EAX
 *  0122A0D5   8B4D CC          MOV ECX,DWORD PTR SS:[EBP-0x34]
 *  0122A0D8   8B55 D0          MOV EDX,DWORD PTR SS:[EBP-0x30]
 *  0122A0DB   8B848A 08040000  MOV EAX,DWORD PTR DS:[EDX+ECX*4+0x408]
 *  0122A0E2   50               PUSH EAX
 *  0122A0E3   E8 C8C90000      CALL .01236AB0  ; jichi: history
 *  0122A0E8   83C4 28          ADD ESP,0x28
 *  0122A0EB   8D4D EC          LEA ECX,DWORD PTR SS:[EBP-0x14]
 *  0122A0EE   51               PUSH ECX
 *  0122A0EF   8B55 CC          MOV EDX,DWORD PTR SS:[EBP-0x34]
 *  0122A0F2   8B45 D0          MOV EAX,DWORD PTR SS:[EBP-0x30]
 *  0122A0F5   8B8C90 08040000  MOV ECX,DWORD PTR DS:[EAX+EDX*4+0x408]
 *  0122A0FC   51               PUSH ECX
 *  0122A0FD   FF15 68322601    CALL DWORD PTR DS:[0x1263268]            ; _4.100120E0
 *  0122A103   83C4 08          ADD ESP,0x8
 *  0122A106   8B55 D8          MOV EDX,DWORD PTR SS:[EBP-0x28]
 *  0122A109   2B55 F8          SUB EDX,DWORD PTR SS:[EBP-0x8]
 *  0122A10C   8955 D8          MOV DWORD PTR SS:[EBP-0x28],EDX
 *
 *  EAX 0BDF587C
 *  ECX 0702B410
 *  EDX 00000000
 *  EBX 00000000
 *  ESP 0C11FD84
 *  EBP 0C11FE08
 *  ESI 06F58A58
 *  EDI 013C2A70
 *  EIP 01236AB0 .01236AB0
 *
 *  0C11FD84   0122A16F  RETURN to .0122A16F from .01236AB0
 *  0C11FD88   0702B410
 *  0C11FD8C   0BDF60F8
 *  0C11FD90   00000000
 *  0C11FD94   00000000
 *  0C11FD98   00000400
 *  0C11FD9C   00000040
 *  0C11FDA0   00000020
 *  0C11FDA4   00000008
 *  0C11FDA8   0BDF0C44
 *  0C11FDAC   00000000
 *  0C11FDB0   00000028
 *
 *  0122A15B   51               PUSH ECX
 *  0122A15C   8B55 CC          MOV EDX,DWORD PTR SS:[EBP-0x34]
 *  0122A15F   8B45 D0          MOV EAX,DWORD PTR SS:[EBP-0x30]
 *  0122A162   8B8C90 08020000  MOV ECX,DWORD PTR DS:[EAX+EDX*4+0x208]
 *  0122A169   51               PUSH ECX
 *  0122A16A   E8 41C90000      CALL .01236AB0  ; jichi: history
 *  0122A16F   83C4 28          ADD ESP,0x28
 *  0122A172   8B55 DC          MOV EDX,DWORD PTR SS:[EBP-0x24]
 *  0122A175   0FB702           MOVZX EAX,WORD PTR DS:[EDX]
 *  0122A178   3D 00810000      CMP EAX,0x8100
 *  0122A17D   0F84 4F010000    JE .0122A2D2
 *  0122A183   8B4D CC          MOV ECX,DWORD PTR SS:[EBP-0x34]
 *  0122A186   8B55 D0          MOV EDX,DWORD PTR SS:[EBP-0x30]
 */
bool attach()
{
  ulong startAddress, stopAddress;
  if (!Engine::getProcessMemoryRange(&startAddress, &stopAddress))
    return false;
  const uint8_t bytes[] = {
    0x55,               // 002c6ab0   55               push ebp
    0x8b,0xec,          // 002c6ab1   8bec             mov ebp,esp
    0x83,0xec, 0x78,    // 002c6ab3   83ec 78          sub esp,0x78
    0xa1, XX4,          // 002c6ab6   a1 8c002f00      mov eax,dword ptr ds:[0x2f008c]
    0x33,0xc5,          // 002c6abb   33c5             xor eax,ebp
    0x89,0x45, 0xf8     // 002c6abd   8945 f8          mov dword ptr ss:[ebp-0x8],eax
  };
  ulong addr = MemDbg::matchBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  if (!addr)
    return false;
  return winhook::hook_before(addr, Private::hookBefore);
}

} // namespace ScenarioHook

namespace OtherHook {
namespace Private {
  bool hookBefore(winhook::hook_stack *s)
  {
    static QByteArray data_; // persistent storage, which makes this function not thread-safe
    // All threads including character names are linked together
    LPCSTR text = (LPCSTR)s->stack[2]; // arg2
    enum { role = Engine::OtherRole };
    auto split = s->stack[0]; // retaddr
    auto sig = Engine::hashThreadSignature(role, split);
    data_ = EngineController::instance()->dispatchTextA(text, role, sig);
    s->stack[2] = (ulong)data_.constData(); // arg2
    return true;
  }
} // namespace Private

/**
 *  Sample game: 時計仕掛けのレイライン
 *  Hooked functions in Pal.dll:
 *  - PalSpriteCreateTextEx
 *  - PalSpriteCreateText
 *
 *  Text in arg2;
 */
bool attach() // attach scenario
{
  const char *funs[] = {
    "PalSpriteCreateText",
    "PalSpriteCreateTextEx"
  };
  bool ret = false;
  for (int i = 0; i < sizeof(funs)/sizeof(*funs); i++)
    if (auto addr = Engine::getModuleFunction("Pal.dll", funs[i]))
      ret = winhook::hook_before(addr, Private::hookBefore) || ret;
  return true;
}
} // namespace OtherHook

} // unnamed namespace

/** Public class */

bool PalEngine::attach()
{
  if (!ScenarioHook::attach())
    return false;

  if (OtherHook::attach())
    DOUT("other text found");
  else
    DOUT("other text NOT FOUND");

  //HijackManager::instance()->attachFunction((ulong)::GetGlyphOutlineA);
  HijackManager::instance()->attachFunction((ulong)::CreateFontIndirectA); // function used in main module
  HijackManager::instance()->attachFunction((ulong)::CreateFontA);  // function used in Pal.dll
  return true;
}

/**
 *  Sample text: <c#FFFF00 #FF87AB>text</c>
 */
QString PalEngine::textFilter(const QString &text, int role)
{
  Q_UNUSED(role);
  if (!text.contains('<'))
    return text;

  QString ret = text;
  ret.remove("</c>");

  static QRegExp rx("<c.*>");
  if (!rx.isMinimal())
    rx.setMinimal(true);
  ret.remove(rx);
  return ret;
}

/**
 *  Example: <rここ>空港</r>
 *  Exactly the same as BGI.
 *  http://sakuradite.com/topic/981
 */
QString PalEngine::rubyCreate(const QString &rb, const QString &rt)
{
  static QString fmt = "<r%2>%1</r>";
  return fmt.arg(rb, rt);
}

// Remove furigana in scenario thread.
QString PalEngine::rubyRemove(const QString &text)
{
  if (!text.contains("</r>"))
    return text;
  static QRegExp rx("<r.+>(.+)</r>");
  if (!rx.isMinimal())
    rx.setMinimal(true);
  return QString(text).replace(rx, "\\1");
}

// EOF
