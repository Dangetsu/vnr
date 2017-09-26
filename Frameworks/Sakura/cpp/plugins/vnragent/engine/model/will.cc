// will.cc
// 7/3/2015 jichi
#include "engine/model/will.h"
#include "engine/enginecontroller.h"
#include "engine/enginehash.h"
#include "engine/enginedef.h"
#include "engine/engineutil.h"
#include "hijack/hijackmanager.h"
#include "dyncodec/dynsjis.h"
#include "memdbg/memsearch.h"
#include "winhook/hookcall.h"
#include "winhook/hookcode.h"
#include "winhook/hookutil.h"
#include <qt_windows.h>
#include <QtCore/QRegExp>
#include <cstdint>

#define DEBUG "model/will"
#include "sakurakit/skdebug.h"

/** Private data */

namespace { // unnamed

// Sample prefix: %LF
// Sample suffix: %L%P%W
template <typename strT>
strT trim(strT text, int *size)
{
  int length = *size;
  if (text[0] == '%') { // handle prefix
    int pos = 0;
    while (pos < length - 1 && text[pos] == '%' && ::isupper(text[pos+1])) {
      pos += 2;
      while (::isupper(text[pos]))
        pos++;
    }
    if (pos) {
      length -= pos;
      text += pos;
    }
  }
  { // handle suffix
    int pos = length;
    for (int i = length - 1; i >= 0; i--) {
      if (::isupper(text[i]))
        ;
      else if (text[i] == '%' && ::isupper(text[i+1]))
        pos = i;
      else
        break;
    }
    length = pos;
  }
  *size = length;
  return text;
}

class TextHookW
{
  typedef TextHookW Self;

  QString text_;
  int stackIndex_;
  int role_;

  bool hookBefore(winhook::hook_stack *s)
  {
    enum { sig = 0 };
    auto text = (LPCWSTR)s->stack[stackIndex_];
    if (!text || !*text)
      return true;
    int size = ::wcslen(text),
        trimmedSize = size;
    auto trimmedText = trim(text, &trimmedSize);
    if (!trimmedSize || !*trimmedText)
      return true;
    QString oldText = QString::fromWCharArray(trimmedText, trimmedSize),
            newText = EngineController::instance()->dispatchTextW(oldText, role_, sig);
    if (newText == oldText)
      return true;
    int prefixSize = trimmedText - text,
        suffixSize = size - prefixSize - trimmedSize;
    if (prefixSize)
      newText.prepend(QString::fromWCharArray(text, prefixSize));
    if (suffixSize)
      newText.append(QString::fromWCharArray(trimmedText + trimmedSize, suffixSize));
    text_ = newText;
    s->stack[stackIndex_] = (ulong)text_.utf16();
    return true;
  }

public:
  explicit TextHookW(int hookStackIndex, int role = Engine::UnknownRole) : stackIndex_(hookStackIndex), role_(role) {}

  bool attach(const uint8_t *pattern, size_t patternSize, ulong startAddress, ulong stopAddress)
  {
    ulong addr = MemDbg::findBytes(pattern, patternSize, startAddress, stopAddress);
    return addr && winhook::hook_before(addr,
        std::bind(&Self::hookBefore, this, std::placeholders::_1));
  }
};

/**
 *  Sample game: なついろレシピ
 *  See: http://capita.tistory.com/m/post/251
 *
 *  Scenario:
 *  00452A8F   77 05            JA SHORT .00452A96
 *  00452A91   E8 A25B0B00      CALL .00508638                           ; JMP to msvcr90._invalid_parameter_noinfo
 *  00452A96   8B43 0C          MOV EAX,DWORD PTR DS:[EBX+0xC]
 *  00452A99   8B48 18          MOV ECX,DWORD PTR DS:[EAX+0x18]
 *  00452A9C   83C0 10          ADD EAX,0x10
 *  00452A9F   33D2             XOR EDX,EDX
 *  00452AA1   8BC1             MOV EAX,ECX
 *  00452AA3   C78424 C4010000 >MOV DWORD PTR SS:[ESP+0x1C4],0x7
 *  00452AAE   C78424 C0010000 >MOV DWORD PTR SS:[ESP+0x1C0],0x0
 *  00452AB9   66:899424 B00100>MOV WORD PTR SS:[ESP+0x1B0],DX
 *  00452AC1   8D70 02          LEA ESI,DWORD PTR DS:[EAX+0x2]
 *  00452AC4   66:8B10          MOV DX,WORD PTR DS:[EAX]
 *  00452AC7   83C0 02          ADD EAX,0x2
 *  00452ACA   66:85D2          TEST DX,DX
 *  00452ACD  ^75 F5            JNZ SHORT .00452AC4
 *  00452ACF   2BC6             SUB EAX,ESI
 *  00452AD1   D1F8             SAR EAX,1
 *  00452AD3   50               PUSH EAX
 *  00452AD4   51               PUSH ECX
 *  00452AD5   8DB424 B4010000  LEA ESI,DWORD PTR SS:[ESP+0x1B4]
 *  00452ADC   E8 DF4DFBFF      CALL .004078C0
 *  00452AE1   C68424 B8020000 >MOV BYTE PTR SS:[ESP+0x2B8],0x8
 *  00452AE9   8B43 10          MOV EAX,DWORD PTR DS:[EBX+0x10]
 *  00452AEC   2B43 0C          SUB EAX,DWORD PTR DS:[EBX+0xC]
 *  00452AEF   C1F8 04          SAR EAX,0x4
 *  00452AF2   83F8 02          CMP EAX,0x2
 *  00452AF5   77 05            JA SHORT .00452AFC
 *  00452AF7   E8 3C5B0B00      CALL .00508638                           ; JMP to msvcr90._invalid_parameter_noinfo
 *  00452AFC   8B43 0C          MOV EAX,DWORD PTR DS:[EBX+0xC]
 *  00452AFF   8B48 28          MOV ECX,DWORD PTR DS:[EAX+0x28]
 *  00452B02   83C0 20          ADD EAX,0x20    ; jichi: hook before here, text in ecx
 *  00452B05   33D2             XOR EDX,EDX
 *  00452B07   8BC1             MOV EAX,ECX
 *  00452B09   C78424 E0010000 07000000        MOV DWORD PTR SS:[ESP+0x1E0],0x7 ; jichi: key pattern is here, text in eax
 *  00452B14   C78424 DC010000 00000000        MOV DWORD PTR SS:[ESP+0x1DC],0x0
 *  00452B27   8D70 02          LEA ESI,DWORD PTR DS:[EAX+0x2]
 *  00452B2A   33DB             XOR EBX,EBX
 *  00452B2C   8D6424 00        LEA ESP,DWORD PTR SS:[ESP]
 *  00452B30   66:8B10          MOV DX,WORD PTR DS:[EAX]
 *  00452B33   83C0 02          ADD EAX,0x2
 *  00452B36   66:3BD3          CMP DX,BX
 *  00452B39  ^75 F5            JNZ SHORT .00452B30
 *  00452B3B   2BC6             SUB EAX,ESI
 *  00452B3D   D1F8             SAR EAX,1
 *  00452B3F   50               PUSH EAX
 *  00452B40   51               PUSH ECX
 *  00452B41   8DB424 D0010000  LEA ESI,DWORD PTR SS:[ESP+0x1D0]
 *  00452B48   E8 734DFBFF      CALL .004078C0
 *  00452B4D   C68424 B8020000 >MOV BYTE PTR SS:[ESP+0x2B8],0x9
 *  00452B55   895C24 1C        MOV DWORD PTR SS:[ESP+0x1C],EBX
 *  00452B59   395C24 14        CMP DWORD PTR SS:[ESP+0x14],EBX
 *  00452B5D   0F84 77080000    JE .004533DA
 *  00452B63   BE 07000000      MOV ESI,0x7
 *  00452B68   33C0             XOR EAX,EAX
 *  00452B6A   895C24 20        MOV DWORD PTR SS:[ESP+0x20],EBX
 *  00452B6E   89B424 FC010000  MOV DWORD PTR SS:[ESP+0x1FC],ESI
 *  00452B75   899C24 F8010000  MOV DWORD PTR SS:[ESP+0x1F8],EBX
 *  00452B7C   66:898424 E80100>MOV WORD PTR SS:[ESP+0x1E8],AX
 *  00452B84   8D4C24 3C        LEA ECX,DWORD PTR SS:[ESP+0x3C]
 *  00452B88   51               PUSH ECX
 *  00452B89   C68424 BC020000 >MOV BYTE PTR SS:[ESP+0x2BC],0xA
 *  00452B91   E8 7AACFCFF      CALL .0041D810
 *  00452B96   C68424 B8020000 >MOV BYTE PTR SS:[ESP+0x2B8],0xB
 *  00452B9E   399C24 C0010000  CMP DWORD PTR SS:[ESP+0x1C0],EBX
 *  00452BA5   0F84 BB020000    JE .00452E66
 *  00452BAB   81C7 14010000    ADD EDI,0x114
 */
bool attachScenarioHookW1(ulong startAddress, ulong stopAddress)
{
  // ECX PTR: 83 C0 20 33 D2 8B C1 C7 84 24 E0 01 00 00 07 00 00 00
  const uint8_t bytes[] = {
    0x83,0xc0, 0x20,     // 00452b02   83c0 20     add eax,0x20    ; jichi: hook before here, text in ecx
    0x33,0xd2,           // 00452b05   33d2        xor edx,edx
    0x8b,0xc1,           // 00452b07   8bc1        mov eax,ecx
    0xc7,0x84,0x24, 0xe0,0x01,0x00,0x00, 0x07,0x00,0x00,0x00  // 00452b09   c78424 e0010000 07000000      mov dword ptr ss:[esp+0x1e0],0x7
                                                              // 00452b14   c78424 dc010000 00000000      mov dword ptr ss:[esp+0x1dc],0x0
  };
  int ecx = winhook_stack_indexof(ecx);
  static auto h = new TextHookW(ecx, Engine::ScenarioRole); // never deleted
  return h->attach(bytes, sizeof(bytes), startAddress, stopAddress);
}

/**
 *  1/9/2016: 見上げてごらん、夜空の星を　体験版
 *
 *  0045580D   C68424 B8020000 08             MOV BYTE PTR SS:[ESP+0x2B8],0x8
 *  00455815   8B47 10                        MOV EAX,DWORD PTR DS:[EDI+0x10]
 *  00455818   2B47 0C                        SUB EAX,DWORD PTR DS:[EDI+0xC]
 *  0045581B   C1F8 04                        SAR EAX,0x4
 *  0045581E   83F8 02                        CMP EAX,0x2
 *  00455821   77 05                          JA SHORT .00455828
 *  00455823   E8 A0F70B00                    CALL .00514FC8                           ; JMP to msvcr90._invalid_parameter_noinfo
 *  00455828   8B7F 0C                        MOV EDI,DWORD PTR DS:[EDI+0xC]
 *  0045582B   83C7 20                        ADD EDI,0x20
 *  0045582E   8B7F 08                        MOV EDI,DWORD PTR DS:[EDI+0x8]
 *  00455831   33C9                           XOR ECX,ECX
 *  00455833   8BC7                           MOV EAX,EDI ; jichi: hook befoe here, text in eax assigned from edi
 *  00455835   C78424 E0010000 07000000       MOV DWORD PTR SS:[ESP+0x1E0],0x7 ; jichi: key pattern is here, text i eax
 *  00455840   899C24 DC010000                MOV DWORD PTR SS:[ESP+0x1DC],EBX
 *  00455847   66:898C24 CC010000             MOV WORD PTR SS:[ESP+0x1CC],CX
 *  0045584F   8D50 02                        LEA EDX,DWORD PTR DS:[EAX+0x2]
 *  00455852   66:8B08                        MOV CX,WORD PTR DS:[EAX]
 *  00455855   83C0 02                        ADD EAX,0x2
 *  00455858   66:3BCB                        CMP CX,BX
 *  0045585B  ^75 F5                          JNZ SHORT .00455852
 *  0045585D   2BC2                           SUB EAX,EDX
 *  0045585F   D1F8                           SAR EAX,1
 *  00455861   50                             PUSH EAX
 *  00455862   57                             PUSH EDI
 *  00455863   8DB424 D0010000                LEA ESI,DWORD PTR SS:[ESP+0x1D0]
 *  0045586A   E8 2120FBFF                    CALL .00407890
 *  0045586F   C68424 B8020000 09             MOV BYTE PTR SS:[ESP+0x2B8],0x9
 *  00455877   895C24 30                      MOV DWORD PTR SS:[ESP+0x30],EBX
 *  0045587B   395C24 18                      CMP DWORD PTR SS:[ESP+0x18],EBX
 *  0045587F   0F84 D1080000                  JE .00456156
 *  00455885   33D2                           XOR EDX,EDX
 *  00455887   895C24 24                      MOV DWORD PTR SS:[ESP+0x24],EBX
 *  0045588B   C78424 FC010000 07000000       MOV DWORD PTR SS:[ESP+0x1FC],0x7
 *  00455896   899C24 F8010000                MOV DWORD PTR SS:[ESP+0x1F8],EBX
 *  0045589D   66:899424 E8010000             MOV WORD PTR SS:[ESP+0x1E8],DX
 *  004558A5   8D4424 3C                      LEA EAX,DWORD PTR SS:[ESP+0x3C]
 */
bool attachScenarioHookW2(ulong startAddress, ulong stopAddress)
{
  // key pattern: C78424 E0010000 07000000
  const uint8_t bytes[] = {
    0x8b,0xc7,                                               // 00455833   8bc7                           mov eax,edi ; jichi: text in eax assigned from edi
    0xc7,0x84,0x24, 0xe0,0x01,0x00,0x00, 0x07,0x00,0x00,0x00 // 00455835   c78424 e0010000 07000000       mov dword ptr ss:[esp+0x1e0],0x7 ; jichi: key pattern is here, text i eax
  };
  int edi = winhook_stack_indexof(edi);
  static auto h = new TextHookW(edi, Engine::ScenarioRole); // never deleted
  return h->attach(bytes, sizeof(bytes), startAddress, stopAddress);
}
/**
 *  Sample game: なついろレシピ
 *  See: http://capita.tistory.com/m/post/251
 *
 *  Name:
 *
 *  004534FA   64:A3 00000000                  MOV DWORD PTR FS:[0],EAX
 *  00453500   8B75 14                         MOV ESI,DWORD PTR SS:[EBP+0x14]
 *  00453503   8B46 10                         MOV EAX,DWORD PTR DS:[ESI+0x10]
 *  00453506   2B46 0C                         SUB EAX,DWORD PTR DS:[ESI+0xC]
 *  00453509   8BF9                            MOV EDI,ECX
 *  0045350B   C1F8 04                         SAR EAX,0x4
 *  0045350E   897C24 14                       MOV DWORD PTR SS:[ESP+0x14],EDI
 *  00453512   85C0                            TEST EAX,EAX
 *  00453514   77 05                           JA SHORT .0045351B
 *  00453516   E8 1D510B00                     CALL .00508638                           ; JMP to msvcr90._invalid_parameter_noinfo
 *  0045351B   8B76 0C                         MOV ESI,DWORD PTR DS:[ESI+0xC]
 *  0045351E   8B4E 08                         MOV ECX,DWORD PTR DS:[ESI+0x8]
 *  00453521   33DB                            XOR EBX,EBX  ; jichi: hook here, text in ecx
 *  00453523   33D2                            XOR EDX,EDX
 *  00453525   8BC1                            MOV EAX,ECX
 *  00453527   C78424 88000000 07000000        MOV DWORD PTR SS:[ESP+0x88],0x7
 *  00453532   899C24 84000000                 MOV DWORD PTR SS:[ESP+0x84],EBX
 *  00453539   66:895424 74                    MOV WORD PTR SS:[ESP+0x74],DX
 *  0045353E   8D70 02                         LEA ESI,DWORD PTR DS:[EAX+0x2]
 *  00453541   66:8B10                         MOV DX,WORD PTR DS:[EAX]
 *  00453544   83C0 02                         ADD EAX,0x2
 *  00453547   66:3BD3                         CMP DX,BX
 *  0045354A  ^75 F5                           JNZ SHORT .00453541
 *  0045354C   2BC6                            SUB EAX,ESI
 *  0045354E   D1F8                            SAR EAX,1
 *  00453550   50                              PUSH EAX
 *  00453551   51                              PUSH ECX
 *  00453552   8D7424 78                       LEA ESI,DWORD PTR SS:[ESP+0x78]
 *  00453556   E8 6543FBFF                     CALL .004078C0
 *  0045355B   899C24 70010000                 MOV DWORD PTR SS:[ESP+0x170],EBX
 *  00453562   A1 DCAA5500                     MOV EAX,DWORD PTR DS:[0x55AADC]
 *  00453567   894424 1C                       MOV DWORD PTR SS:[ESP+0x1C],EAX
 *  0045356B   B8 0F000000                     MOV EAX,0xF
 *  00453570   894424 6C                       MOV DWORD PTR SS:[ESP+0x6C],EAX
 *  00453574   895C24 68                       MOV DWORD PTR SS:[ESP+0x68],EBX
 *  00453578   885C24 58                       MOV BYTE PTR SS:[ESP+0x58],BL
 *  0045357C   894424 50                       MOV DWORD PTR SS:[ESP+0x50],EAX
 *  00453580   895C24 4C                       MOV DWORD PTR SS:[ESP+0x4C],EBX
 *  00453584   885C24 3C                       MOV BYTE PTR SS:[ESP+0x3C],BL
 *  00453588   C68424 70010000 02              MOV BYTE PTR SS:[ESP+0x170],0x2
 *  00453590   8B8424 84000000                 MOV EAX,DWORD PTR SS:[ESP+0x84]
 *  00453597   8BF0                            MOV ESI,EAX
 *  00453599   3BC3                            CMP EAX,EBX
 *  0045359B   74 3D                           JE SHORT .004535DA
 *  0045359D   83BC24 88000000 08              CMP DWORD PTR SS:[ESP+0x88],0x8
 *  004535A5   8B5424 74                       MOV EDX,DWORD PTR SS:[ESP+0x74]
 *  004535A9   73 04                           JNB SHORT .004535AF
 *  004535AB   8D5424 74                       LEA EDX,DWORD PTR SS:[ESP+0x74]
 */
bool attachNameHookW(ulong startAddress, ulong stopAddress)
{
  // ECX PTR: 33 DB 33 D2 8B C1 C7 84 24 88 00 00 00 07 00 00 00
  const uint8_t bytes[] = {
    0x33,0xdb,   // 00453521   33db                            xor ebx,ebx  ; jichi: hook here, text in ecx
    0x33,0xd2,   // 00453523   33d2                            xor edx,edx
    0x8b,0xc1,   // 00453525   8bc1                            mov eax,ecx
    0xc7,0x84,0x24, 0x88,0x00,0x00,0x00, 0x07,0x00,0x00,0x00 // 00453527   c78424 88000000 07000000        mov dword ptr ss:[esp+0x88],0x7
                                                             // 00453532   899c24 84000000                 mov dword ptr ss:[esp+0x84],ebx
  };
  int ecx = winhook_stack_indexof(ecx);
  static auto h = new TextHookW(ecx, Engine::NameRole); // never deleted
  return h->attach(bytes, sizeof(bytes), startAddress, stopAddress);
}

/**
 *  Sample game: なついろレシピ
 *  See: http://capita.tistory.com/m/post/251
 *
 *  Choice:
 *  00470D95   72 05                           JB SHORT .00470D9C
 *  00470D97   E8 9C780900                     CALL .00508638                           ; JMP to msvcr90._invalid_parameter_noinfo
 *  00470D9C   8BB5 EC020000                   MOV ESI,DWORD PTR SS:[EBP+0x2EC]
 *  00470DA2   037424 14                       ADD ESI,DWORD PTR SS:[ESP+0x14]
 *  00470DA6   8B4E 10                         MOV ECX,DWORD PTR DS:[ESI+0x10]
 *  00470DA9   2B4E 0C                         SUB ECX,DWORD PTR DS:[ESI+0xC]
 *  00470DAC   C1F9 04                         SAR ECX,0x4
 *  00470DAF   83F9 01                         CMP ECX,0x1
 *  00470DB2   77 05                           JA SHORT .00470DB9
 *  00470DB4   E8 7F780900                     CALL .00508638                           ; JMP to msvcr90._invalid_parameter_noinfo
 *  00470DB9   8B46 0C                         MOV EAX,DWORD PTR DS:[ESI+0xC]
 *  00470DBC   8B50 18                         MOV EDX,DWORD PTR DS:[EAX+0x18]
 *  00470DBF   83C0 10                         ADD EAX,0x10     ; jichi: text in edx
 *  00470DC2   52                              PUSH EDX
 *  00470DC3   8D8C24 7C040000                 LEA ECX,DWORD PTR SS:[ESP+0x47C]
 *  00470DCA   8D7424 4C                       LEA ESI,DWORD PTR SS:[ESP+0x4C]
 *  00470DCE   E8 EDA3F9FF                     CALL .0040B1C0
 *  00470DD3   83C4 04                         ADD ESP,0x4
 *  00470DD6   6A FF                           PUSH -0x1
 *  00470DD8   53                              PUSH EBX
 *  00470DD9   50                              PUSH EAX
 *  00470DDA   8D8424 84040000                 LEA EAX,DWORD PTR SS:[ESP+0x484]
 *  00470DE1   C68424 B0040000 07              MOV BYTE PTR SS:[ESP+0x4B0],0x7
 *  00470DE9   E8 1251F9FF                     CALL .00405F00
 *  00470DEE   BE 08000000                     MOV ESI,0x8
 *  00470DF3   C68424 A4040000 06              MOV BYTE PTR SS:[ESP+0x4A4],0x6
 *  00470DFB   397424 60                       CMP DWORD PTR SS:[ESP+0x60],ESI
 *  00470DFF   72 0D                           JB SHORT .00470E0E
 *  00470E01   8B4424 4C                       MOV EAX,DWORD PTR SS:[ESP+0x4C]
 *  00470E05   50                              PUSH EAX
 *  00470E06   E8 65770900                     CALL .00508570                           ; JMP to msvcr90.??3@YAXPAX@Z
 *  00470E0B   83C4 04                         ADD ESP,0x4
 *  00470E0E   8B9424 7C040000                 MOV EDX,DWORD PTR SS:[ESP+0x47C]
 *  00470E15   33C9                            XOR ECX,ECX
 *  00470E17   C74424 60 07000000              MOV DWORD PTR SS:[ESP+0x60],0x7
 *  00470E1F   895C24 5C                       MOV DWORD PTR SS:[ESP+0x5C],EBX
 *  00470E23   66:894C24 4C                    MOV WORD PTR SS:[ESP+0x4C],CX
 *  00470E28   39B424 90040000                 CMP DWORD PTR SS:[ESP+0x490],ESI
 *  00470E2F   73 07                           JNB SHORT .00470E38
 *  00470E31   8D9424 7C040000                 LEA EDX,DWORD PTR SS:[ESP+0x47C]
 *  00470E38   8B8424 44040000                 MOV EAX,DWORD PTR SS:[ESP+0x444]
 *  00470E3F   B9 10000000                     MOV ECX,0x10
 *  00470E44   398C24 58040000                 CMP DWORD PTR SS:[ESP+0x458],ECX
 *  00470E4B   73 07                           JNB SHORT .00470E54
 *  00470E4D   8D8424 44040000                 LEA EAX,DWORD PTR SS:[ESP+0x444]
 *  00470E54   398C24 74040000                 CMP DWORD PTR SS:[ESP+0x474],ECX
 *  00470E5B   8B8C24 60040000                 MOV ECX,DWORD PTR SS:[ESP+0x460]
 */
bool attachOtherHookW(ulong startAddress, ulong stopAddress)
{
  // EDX PTR : 83 C0 10 52 8D 8C 24 7C 04 00 00 8D 74 24 4C
  const uint8_t bytes[] = {
    0x83,0xc0, 0x10,                        // 00470dbf   83c0 10                         add eax,0x10     ; jichi: text in edx
    0x52,                                   // 00470dc2   52                              push edx
    0x8d,0x8c,0x24, 0x7c,0x04,0x00,0x00,    // 00470dc3   8d8c24 7c040000                 lea ecx,dword ptr ss:[esp+0x47c]
    0x8d,0x74,0x24, 0x4c                    // 00470dca   8d7424 4c                       lea esi,dword ptr ss:[esp+0x4c]
  };
  int edx = winhook_stack_indexof(edx);
  static auto h = new TextHookW(edx, Engine::OtherRole); // never deleted
  return h->attach(bytes, sizeof(bytes), startAddress, stopAddress);
}

namespace ScenarioHookA {

namespace Private {

  void dispatch(LPSTR text, int role)
  {
    enum { sig = 0 };
    if (!Engine::isAddressWritable(text) || !*text) // isAddressWritable is not needed for correct games
      return;
    int size = ::strlen(text),
        trimmedSize = size;
    auto trimmedText = trim(text, &trimmedSize);
    if (!trimmedSize || !*trimmedText)
      return;
    QByteArray oldData(trimmedText, trimmedSize),
               newData = EngineController::instance()->dispatchTextA(oldData, role, sig);
    if (newData == oldData)
      return;
    if (trimmedText[trimmedSize])
      newData.append(trimmedText + trimmedSize); //, size - trimmedSize - (trimmedText - text));
    ::strcpy(text, newData.constData());
  }

  bool hookBefore(winhook::hook_stack *s)
  {
    auto text = (LPSTR)s->eax;
    if (!text)
      return true;
    dispatch(text - 1024, Engine::NameRole);
    dispatch(text, Engine::ScenarioRole);
    return true;
  }

} // namespace Private

/**
 *  Sample games
 *  - [111028][PULLTOP] 神聖にして侵すべからず
 *  - Re：BIRTHDAY SONG～恋を唄う死神～（体験版）
 *  See: http://capita.tistory.com/m/post/84
 *
 *  ENCODEKOR,FORCEFONT(5),HOOK(0x0042B5E0,TRANS(0x004FFBF8,OVERWRITE(IGNORE)),RETNPOS(COPY),TRANS(0x004FF7F8,OVERWRITE(IGNORE))),HOOK(0x00413204,TRANS([ESP+0x1c],PTRCHEAT),RETNPOS(SOURCE)),HOOK(0x00424004,TRANS([ESP+0x1c],PTRCHEAT),RETNPOS(SOURCE)),HOOK(0x004242B9,TRANS([ESP+0x1c],PTRCHEAT),RETNPOS(SOURCE)),HOOK(0x00424109,TRANS([ESP+0x1c],PTRCHEAT),RETNPOS(SOURCE))
 *
 *  Scenario in eax
 *  Name in (eax - 1024)
 *  Memory can be directly overridden.
 *
 *  0042B5DE   CC               INT3
 *  0042B5DF   CC               INT3
 *  0042B5E0   81EC 14080000    SUB ESP,0x814	; jichi: text in eax, name in eax - 1024, able to copy
 *  0042B5E6   53               PUSH EBX
 *  0042B5E7   55               PUSH EBP
 *  0042B5E8   56               PUSH ESI
 *  0042B5E9   33DB             XOR EBX,EBX
 *  0042B5EB   57               PUSH EDI
 *  0042B5EC   8BF8             MOV EDI,EAX
 *  0042B5EE   399C24 28080000  CMP DWORD PTR SS:[ESP+0x828],EBX
 *  0042B5F5   75 13            JNZ SHORT .0042B60A
 *  0042B5F7   68 74030000      PUSH 0x374
 *  0042B5FC   53               PUSH EBX
 *  0042B5FD   68 7CC44F00      PUSH .004FC47C
 *  0042B602   E8 09E60500      CALL .00489C10
 *  0042B607   83C4 0C          ADD ESP,0xC
 *  0042B60A   33F6             XOR ESI,ESI
 *  0042B60C   895C24 1C        MOV DWORD PTR SS:[ESP+0x1C],EBX
 *  0042B610   895C24 10        MOV DWORD PTR SS:[ESP+0x10],EBX
 *  0042B614   381F             CMP BYTE PTR DS:[EDI],BL
 *  0042B616   0F84 0D020000    JE .0042B829
 *  0042B61C   8D6424 00        LEA ESP,DWORD PTR SS:[ESP]
 *  0042B620   8A4C37 01        MOV CL,BYTE PTR DS:[EDI+ESI+0x1]
 *  0042B624   84C9             TEST CL,CL
 *  0042B626   0F84 E6010000    JE .0042B812
 *  0042B62C   66:0FB6043E      MOVZX AX,BYTE PTR DS:[ESI+EDI]
 *  0042B631   8D2C3E           LEA EBP,DWORD PTR DS:[ESI+EDI]
 *  0042B634   66:C1E0 08       SHL AX,0x8
 *  0042B638   0FB7C0           MOVZX EAX,AX
 *  0042B63B   0FB6C9           MOVZX ECX,CL
 *  0042B63E   0BC1             OR EAX,ECX
 *  0042B640   50               PUSH EAX
 *  0042B641   E8 34B40500      CALL .00486A7A
 *  0042B646   83C4 04          ADD ESP,0x4
 *  0042B649   85C0             TEST EAX,EAX
 *  0042B64B   74 14            JE SHORT .0042B661
 *  0042B64D   66:8B55 00       MOV DX,WORD PTR SS:[EBP]
 *  0042B651   66:89541C 24     MOV WORD PTR SS:[ESP+EBX+0x24],DX
 *  0042B656   83C3 02          ADD EBX,0x2
 *  0042B659   83C6 02          ADD ESI,0x2
 *  0042B65C   E9 BA010000      JMP .0042B81B
 *  0042B661   807D 00 7B       CMP BYTE PTR SS:[EBP],0x7B
 *  0042B665   0F85 60010000    JNZ .0042B7CB
 *  0042B66B   8BC3             MOV EAX,EBX
 *  0042B66D   2B4424 1C        SUB EAX,DWORD PTR SS:[ESP+0x1C]
 *  0042B671   46               INC ESI
 *  0042B672   33ED             XOR EBP,EBP
 *  0042B674   894424 20        MOV DWORD PTR SS:[ESP+0x20],EAX
 *  0042B678   896C24 14        MOV DWORD PTR SS:[ESP+0x14],EBP
 *  0042B67C   8D6424 00        LEA ESP,DWORD PTR SS:[ESP]
 *  0042B680   8A0C3E           MOV CL,BYTE PTR DS:[ESI+EDI]
 *  0042B683   84C9             TEST CL,CL
 *  0042B685   0F84 B5010000    JE .0042B840
 *  0042B68B   0FB64437 01      MOVZX EAX,BYTE PTR DS:[EDI+ESI+0x1]
 *  0042B690   66:0FB6C9        MOVZX CX,CL
 *  0042B694   66:C1E1 08       SHL CX,0x8
 *  0042B698   0FB7D1           MOVZX EDX,CX
 *  0042B69B   0BC2             OR EAX,EDX
 *  0042B69D   50               PUSH EAX
 *  0042B69E   E8 D7B30500      CALL .00486A7A
 *  0042B6A3   83C4 04          ADD ESP,0x4
 *  0042B6A6   85C0             TEST EAX,EAX
 *  0042B6A8   74 1A            JE SHORT .0042B6C4
 *  0042B6AA   66:8B043E        MOV AX,WORD PTR DS:[ESI+EDI]
 *  0042B6AE   834424 14 02     ADD DWORD PTR SS:[ESP+0x14],0x2
 *  0042B6B3   66:89441C 24     MOV WORD PTR SS:[ESP+EBX+0x24],AX
 *  0042B6B8   83C3 02          ADD EBX,0x2
 *  0042B6BB   895C24 10        MOV DWORD PTR SS:[ESP+0x10],EBX
 *  0042B6BF   83C6 02          ADD ESI,0x2
 *  0042B6C2  ^EB BC            JMP SHORT .0042B680
 *  0042B6C4   8A043E           MOV AL,BYTE PTR DS:[ESI+EDI]
 *  0042B6C7   3C 3A            CMP AL,0x3A
 *  0042B6C9   74 10            JE SHORT .0042B6DB
 *  0042B6CB   FF4424 14        INC DWORD PTR SS:[ESP+0x14]
 *  0042B6CF   88441C 24        MOV BYTE PTR SS:[ESP+EBX+0x24],AL
 *  0042B6D3   43               INC EBX
 *  0042B6D4   895C24 10        MOV DWORD PTR SS:[ESP+0x10],EBX
 *  0042B6D8   46               INC ESI
 *  0042B6D9  ^EB A5            JMP SHORT .0042B680
 *  0042B6DB   896C24 18        MOV DWORD PTR SS:[ESP+0x18],EBP
 *  0042B6DF   46               INC ESI
 *  0042B6E0   8A0C3E           MOV CL,BYTE PTR DS:[ESI+EDI]
 *  0042B6E3   84C9             TEST CL,CL
 *  0042B6E5   0F84 55010000    JE .0042B840
 *  0042B6EB   0FB64437 01      MOVZX EAX,BYTE PTR DS:[EDI+ESI+0x1]
 *  0042B6F0   66:0FB6C9        MOVZX CX,CL
 *  0042B6F4   66:C1E1 08       SHL CX,0x8
 *  0042B6F8   0FB7D1           MOVZX EDX,CX
 *  0042B6FB   0BC2             OR EAX,EDX
 *  0042B6FD   50               PUSH EAX
 *  0042B6FE   E8 77B30500      CALL .00486A7A
 *  0042B703   83C4 04          ADD ESP,0x4
 *  0042B706   85C0             TEST EAX,EAX
 *  0042B708   74 18            JE SHORT .0042B722
 *  0042B70A   66:8B043E        MOV AX,WORD PTR DS:[ESI+EDI]
 *  0042B70E   FF4424 18        INC DWORD PTR SS:[ESP+0x18]
 *  0042B712   66:89842C 240400>MOV WORD PTR SS:[ESP+EBP+0x424],AX
 *  0042B71A   83C5 02          ADD EBP,0x2
 *  0042B71D   83C6 02          ADD ESI,0x2
 *  0042B720  ^EB BE            JMP SHORT .0042B6E0
 *  0042B722   8A043E           MOV AL,BYTE PTR DS:[ESI+EDI]
 *  0042B725   3C 7D            CMP AL,0x7D
 *  0042B727   74 0E            JE SHORT .0042B737
 *  0042B729   FF4424 18        INC DWORD PTR SS:[ESP+0x18]
 *  0042B72D   88842C 24040000  MOV BYTE PTR SS:[ESP+EBP+0x424],AL
 *  0042B734   45               INC EBP
 *  0042B735  ^EB A8            JMP SHORT .0042B6DF
 *  0042B737   8D8424 24040000  LEA EAX,DWORD PTR SS:[ESP+0x424]
 *  0042B73E   46               INC ESI
 *  0042B73F   C6842C 24040000 >MOV BYTE PTR SS:[ESP+EBP+0x424],0x0
 *  0042B747   8D50 01          LEA EDX,DWORD PTR DS:[EAX+0x1]
 *  0042B74A   8D9B 00000000    LEA EBX,DWORD PTR DS:[EBX]
 *  0042B750   8A08             MOV CL,BYTE PTR DS:[EAX]
 *  0042B752   40               INC EAX
 *  0042B753   84C9             TEST CL,CL
 *  0042B755  ^75 F9            JNZ SHORT .0042B750
 *  0042B757   2BC2             SUB EAX,EDX
 *  0042B759   83F8 1E          CMP EAX,0x1E
 *  0042B75C   0F87 DE000000    JA .0042B840
 *  0042B762   8B15 7CC44F00    MOV EDX,DWORD PTR DS:[0x4FC47C]
 *  0042B768   83FA 14          CMP EDX,0x14
 *  0042B76B   0F8D AE000000    JGE .0042B81F
 *  0042B771   6BD2 2C          IMUL EDX,EDX,0x2C
 *  0042B774   8D8C24 24040000  LEA ECX,DWORD PTR SS:[ESP+0x424]
 *  0042B77B   81C2 8CC44F00    ADD EDX,.004FC48C
 *  0042B781   8A01             MOV AL,BYTE PTR DS:[ECX]
 *  0042B783   8802             MOV BYTE PTR DS:[EDX],AL
 *  0042B785   41               INC ECX
 *  0042B786   42               INC EDX
 *  0042B787   84C0             TEST AL,AL
 *  0042B789  ^75 F6            JNZ SHORT .0042B781
 *  0042B78B   8B0D 7CC44F00    MOV ECX,DWORD PTR DS:[0x4FC47C]
 *  0042B791   8B5424 14        MOV EDX,DWORD PTR SS:[ESP+0x14]
 *  0042B795   6BC9 2C          IMUL ECX,ECX,0x2C
 *  0042B798   8991 88C44F00    MOV DWORD PTR DS:[ECX+0x4FC488],EDX
 *  0042B79E   A1 7CC44F00      MOV EAX,DWORD PTR DS:[0x4FC47C]
 *  0042B7A3   8B4C24 20        MOV ECX,DWORD PTR SS:[ESP+0x20]
 *  0042B7A7   6BC0 2C          IMUL EAX,EAX,0x2C
 *  0042B7AA   8988 80C44F00    MOV DWORD PTR DS:[EAX+0x4FC480],ECX
 *  0042B7B0   8B15 7CC44F00    MOV EDX,DWORD PTR DS:[0x4FC47C]
 *  0042B7B6   8B4424 18        MOV EAX,DWORD PTR SS:[ESP+0x18]
 *  0042B7BA   6BD2 2C          IMUL EDX,EDX,0x2C
 *  0042B7BD   8982 84C44F00    MOV DWORD PTR DS:[EDX+0x4FC484],EAX
 *  0042B7C3   FF05 7CC44F00    INC DWORD PTR DS:[0x4FC47C]
 *  0042B7C9   EB 54            JMP SHORT .0042B81F
 *  0042B7CB   55               PUSH EBP
 *  0042B7CC   E8 7F000000      CALL .0042B850
 *  0042B7D1   8BD8             MOV EBX,EAX
 *  0042B7D3   83C4 04          ADD ESP,0x4
 *  0042B7D6   85DB             TEST EBX,EBX
 *  0042B7D8   74 23            JE SHORT .0042B7FD
 *  0042B7DA   53               PUSH EBX
 *  0042B7DB   55               PUSH EBP
 *  0042B7DC   8B6C24 18        MOV EBP,DWORD PTR SS:[ESP+0x18]
 *  0042B7E0   8D4C2C 2C        LEA ECX,DWORD PTR SS:[ESP+EBP+0x2C]
 *  0042B7E4   51               PUSH ECX
 *  0042B7E5   E8 A6E40500      CALL .00489C90
 *  0042B7EA   03EB             ADD EBP,EBX
 *  0042B7EC   03F3             ADD ESI,EBX
 *  0042B7EE   83C4 0C          ADD ESP,0xC
 *  0042B7F1   015C24 1C        ADD DWORD PTR SS:[ESP+0x1C],EBX
 *  0042B7F5   896C24 10        MOV DWORD PTR SS:[ESP+0x10],EBP
 *  0042B7F9   8BDD             MOV EBX,EBP
 *  0042B7FB   EB 22            JMP SHORT .0042B81F
 *  0042B7FD   8B4424 10        MOV EAX,DWORD PTR SS:[ESP+0x10]
 *  0042B801   8A55 00          MOV DL,BYTE PTR SS:[EBP]
 *  0042B804   40               INC EAX
 *  0042B805   885404 23        MOV BYTE PTR SS:[ESP+EAX+0x23],DL
 *  0042B809   894424 10        MOV DWORD PTR SS:[ESP+0x10],EAX
 *  0042B80D   46               INC ESI
 *  0042B80E   8BD8             MOV EBX,EAX
 *  0042B810   EB 0D            JMP SHORT .0042B81F
 *  0042B812   8A043E           MOV AL,BYTE PTR DS:[ESI+EDI]
 *  0042B815   88441C 24        MOV BYTE PTR SS:[ESP+EBX+0x24],AL
 *  0042B819   43               INC EBX
 *  0042B81A   46               INC ESI
 *  0042B81B   895C24 10        MOV DWORD PTR SS:[ESP+0x10],EBX
 *  0042B81F   803C3E 00        CMP BYTE PTR DS:[ESI+EDI],0x0
 *  0042B823  ^0F85 F7FDFFFF    JNZ .0042B620
 *  0042B829   8D4424 24        LEA EAX,DWORD PTR SS:[ESP+0x24]
 *  0042B82D   8BC8             MOV ECX,EAX
 *  0042B82F   C6441C 24 00     MOV BYTE PTR SS:[ESP+EBX+0x24],0x0
 *  0042B834   2BF9             SUB EDI,ECX
 *  0042B836   8A08             MOV CL,BYTE PTR DS:[EAX]
 *  0042B838   880C07           MOV BYTE PTR DS:[EDI+EAX],CL
 *  0042B83B   40               INC EAX
 *  0042B83C   84C9             TEST CL,CL
 *  0042B83E  ^75 F6            JNZ SHORT .0042B836
 *  0042B840   5F               POP EDI
 *  0042B841   5E               POP ESI
 *  0042B842   5D               POP EBP
 *  0042B843   5B               POP EBX
 *  0042B844   81C4 14080000    ADD ESP,0x814
 *  0042B84A   C3               RETN
 *  0042B84B   CC               INT3
 *  0042B84C   CC               INT3
 *  0042B84D   CC               INT3
 *  0042B84E   CC               INT3
 *
 *  Skip scenario text:
 *  00438EF1   51               PUSH ECX
 *  00438EF2   56               PUSH ESI
 *  00438EF3   57               PUSH EDI
 *  00438EF4   52               PUSH EDX
 *  00438EF5   6A 03            PUSH 0x3    ; jichi: scenario arg1 is always 3
 *  00438EF7   E8 14F3FDFF      CALL .00418210  ; jichi: text called here
 *  00438EFC   894424 4C        MOV DWORD PTR SS:[ESP+0x4C],EAX
 *  00438F00   8D4424 78        LEA EAX,DWORD PTR SS:[ESP+0x78]
 *  00438F04   83C4 30          ADD ESP,0x30
 *  00438F07   897C24 34        MOV DWORD PTR SS:[ESP+0x34],EDI
 *  00438F0B   897424 38        MOV DWORD PTR SS:[ESP+0x38],ESI
 *  00438F0F   8D48 01          LEA ECX,DWORD PTR DS:[EAX+0x1]
 *  00438F12   8A10             MOV DL,BYTE PTR DS:[EAX]
 *  00438F14   40               INC EAX
 *  00438F15   84D2             TEST DL,DL
 */
bool attach(ulong startAddress, ulong stopAddress)
{
  const uint8_t bytes[] = {
    0x81,0xec, 0x14,0x08,0x00,0x00 // 0042B5E0   81EC 14080000    SUB ESP,0x814	; jichi: text in eax, name in eax - 1024, able to copy
  };
  ulong addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  return addr && winhook::hook_before(addr, Private::hookBefore);
}

} // namespace ScenarioHookA

namespace OtherHookA {

namespace Private {

  bool hookBefore(winhook::hook_stack *s)
  {
    static QByteArray data_;
    if (s->stack[1] == 3) // skip scenario hook where arg1 is 3
      return true;
    auto text = (LPCSTR)s->stack[8]; // text in arg8
    if (!Engine::isAddressReadable(text) || !*text || ::strlen(text) <= 2) // do not translate single character
      return true;
    enum { role = Engine::OtherRole };
    auto split = s->stack[0]; // use retaddr as split
    auto sig = Engine::hashThreadSignature(role, split);
    data_ = EngineController::instance()->dispatchTextA(text, role, sig);
    if (data_.isEmpty()) // do not allow delete other text
      return true;
    s->stack[8] = (ulong)data_.constData(); // arg8
    return true;
  }

} // namespace Private

/**
 *  Sample games: Re：BIRTHDAY SONG～恋を唄う死神～（体験版）
 *
 *  There are two GetGlyphOutlineA, that are called in the same functions.
 *
 *  Caller of GetGlyphOutlineA, text in arg8.
 */
bool attach(ulong startAddress, ulong stopAddress)
{
  ulong addr = MemDbg::findCallerAddressAfterInt3((ulong)::GetGlyphOutlineA, startAddress, stopAddress);
  return addr && winhook::hook_before(addr, Private::hookBefore);
}

} // namespace OtherHookA

namespace PatchA {

namespace Private {
  // The second argument is always 0 and not used
  bool isLeadByteChar(int ch, int)
  {
    return dynsjis::isleadchar(ch);
    //return ::IsDBCSLeadByte(HIBYTE(testChar));
  }

} // namespace Private

/**
 *  Sample game: Re:BIRTHDAY SONG
 *
 *  0x8140 is found by tracing the call of the caller of GetGlyphOutlineA.

 *  00487F8D   25 FF7F0000      AND EAX,0x7FFF
 *  00487F92   C3               RETN
 *  00487F93   8BFF             MOV EDI,EDI
 *  00487F95   55               PUSH EBP
 *  00487F96   8BEC             MOV EBP,ESP
 *  00487F98   83EC 10          SUB ESP,0x10
 *  00487F9B   FF75 0C          PUSH DWORD PTR SS:[EBP+0xC]
 *  00487F9E   8D4D F0          LEA ECX,DWORD PTR SS:[EBP-0x10]
 *  00487FA1   E8 02EEFFFF      CALL .00486DA8
 *  00487FA6   8B45 08          MOV EAX,DWORD PTR SS:[EBP+0x8]
 *  00487FA9   C1E8 08          SHR EAX,0x8
 *  00487FAC   0FB6C8           MOVZX ECX,AL
 *  00487FAF   8B45 F4          MOV EAX,DWORD PTR SS:[EBP-0xC]
 *  00487FB2   F64401 1D 04     TEST BYTE PTR DS:[ECX+EAX+0x1D],0x4
 *  00487FB7   74 10            JE SHORT .00487FC9
 *  00487FB9   0FB64D 08        MOVZX ECX,BYTE PTR SS:[EBP+0x8]
 *  00487FBD   F64401 1D 08     TEST BYTE PTR DS:[ECX+EAX+0x1D],0x8
 *  00487FC2   74 05            JE SHORT .00487FC9
 *  00487FC4   33C0             XOR EAX,EAX
 *  00487FC6   40               INC EAX
 *  00487FC7   EB 02            JMP SHORT .00487FCB
 *  00487FC9   33C0             XOR EAX,EAX
 *  00487FCB   807D FC 00       CMP BYTE PTR SS:[EBP-0x4],0x0
 *  00487FCF   74 07            JE SHORT .00487FD8
 *  00487FD1   8B4D F8          MOV ECX,DWORD PTR SS:[EBP-0x8]
 *  00487FD4   8361 70 FD       AND DWORD PTR DS:[ECX+0x70],0xFFFFFFFD
 *  00487FD8   C9               LEAVE
 *  00487FD9   C3               RETN
 *  00487FDA   8BFF             MOV EDI,EDI	; jichi: called here, text in arg1
 *  00487FDC   55               PUSH EBP
 *  00487FDD   8BEC             MOV EBP,ESP
 *  00487FDF   6A 00            PUSH 0x0
 *  00487FE1   FF75 08          PUSH DWORD PTR SS:[EBP+0x8]
 *  00487FE4   E8 AAFFFFFF      CALL .00487F93	; jichi: called here
 *  00487FE9   59               POP ECX
 *  00487FEA   59               POP ECX
 *  00487FEB   5D               POP EBP
 *  00487FEC   C3               RETN
 */

bool patchEncoding(ulong startAddress, ulong stopAddress)
{
  const uint8_t bytes[] = {
    0x6a, 0x00,                 // 00487fdf   6a 00            push 0x0
    0xff,0x75, 0x08,            // 00487fe1   ff75 08          push dword ptr ss:[ebp+0x8]
    0xe8, 0xaa,0xff,0xff,0xff   // 00487fe4   e8 aaffffff      call .00487f93	; jichi: called here
  };
  enum { addr_offset = 5 };
  ulong addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  return addr && winhook::replace_near_call(addr + addr_offset, (ulong)Private::isLeadByteChar);
}

} // namespace PatchA

} // unnamed namespace

/** Public class */

bool WillPlusEngine::attach()
{
  ulong startAddress, stopAddress;
  if (!Engine::getProcessMemoryRange(&startAddress, &stopAddress))
    return false;

  if (::attachScenarioHookW1(startAddress, stopAddress) || ::attachScenarioHookW2(startAddress, stopAddress)) {
    DOUT("wide char supported");
    name = "EmbedWillPlusW";
    encoding = Utf16Encoding;
    enableLocaleEmulation = true; // fix thread codepage in MultiByteToWideChar

    if (::attachNameHookW(startAddress, stopAddress))
      DOUT("name text found");
    else
      DOUT("name text NOT FOUND");

    if (::attachOtherHookW(startAddress, stopAddress))
      DOUT("other text found");
    else
      DOUT("other text NOT FOUND");

    HijackManager::instance()->attachFunction((ulong)::MultiByteToWideChar); // Font can already be dynamically changed and hence not needed
    //HijackManager::instance()->attachFunction((ulong)::GetGlyphOutlineW); // Font can already be dynamically changed and hence not needed
    return true;

  } else if (ScenarioHookA::attach(startAddress, stopAddress)) { // try widechar pattern first, which is more unique

    DOUT("wide char not supported");
    name = "EmbedWillPlusA";

    if (PatchA::patchEncoding(startAddress, stopAddress)) {
      enableDynamicEncoding = true;
      DOUT("patch encoding succeeded");
    } else
      DOUT("patch encoding FAILED");

    if (OtherHookA::attach(startAddress, stopAddress))
      DOUT("other text found");
    else
      DOUT("other text NOT FOUND");

    HijackManager::instance()->attachFunction((ulong)::GetGlyphOutlineA);
    HijackManager::instance()->attachFunction((ulong)::TextOutA); // not called. hijack in case it is used
    return true;
  }

  return false;
}

/**
 * Sample ruby: {風峰涼香:かざみねすずか}
 */

QString WillPlusEngine::rubyCreate(const QString &rb, const QString &rt)
{
  static QString fmt = "{%1:%2}";
  return fmt.arg(rb, rt);
}

// Remove furigana in scenario thread.
QString WillPlusEngine::rubyRemove(const QString &text)
{
  if (!text.contains('{'))
    return text;
  static QRegExp rx("\\{(.+):.+\\}");
  if (!rx.isMinimal())
    rx.setMinimal(true);
  return QString(text).replace(rx, "\\1");
}

// EOF

/*
// Sample prefix: %LF
// Sample suffix: %L%P%W
QString trimW(const QString &text, QString *prefix, QString *suffix)
{
  QString ret = text;
  if (text.startsWith('%')) {
    int pos = 0;
    while (pos < text.size() - 1 && text[pos].unicode() == '%' && ::isupper(text[pos+1].unicode())) {
      pos += 2;
      while (::isupper(text[pos].unicode()))
        pos++;
    }
    if (prefix)
      *prefix = ret.left(pos);
    ret = ret.mid(pos);
  }
  if (ret.contains('%')) {
    int pos = ret.size();
    for (int i = ret.size() - 1; i >= 0; i--) {
      wchar_t w = ret[i].unicode();
      if (::isupper(w))
        ;
      else if (w == '%')
        pos = i;
      else
        break;
    }
    if (pos != ret.size()) {
      if (suffix)
        *suffix = ret.mid(pos);
      ret = ret.left(pos);
    }
  }
  return ret;
}

QByteArray trimA(const QByteArray &text, QByteArray *prefix, QByteArray *suffix)
{
  QByteArray ret = text;
  if (text.startsWith('%')) {
    int pos = 0;
    while (pos < text.size() - 1 && text[pos] == '%' && ::isupper(text[pos+1])) {
      pos += 2;
      while (::isupper(text[pos]))
        pos++;
    }
    if (prefix)
      *prefix = ret.left(pos);
    ret = ret.mid(pos);
  }
  if (ret.contains('%')) {
    int pos = ret.size();
    for (int i = ret.size() - 1; i >= 0; i--) {
      quint8 ch = ret[i];
      if (::isupper(ch))
        ;
      else if (ch == '%')
        pos = i;
      else
        break;
    }
    if (pos != ret.size()) {
      if (suffix)
        *suffix = ret.mid(pos);
      ret = ret.left(pos);
    }
  }
  return ret;
}
*/
