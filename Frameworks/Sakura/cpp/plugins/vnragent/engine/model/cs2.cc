// cs2.cc
// 6/21/2015 jichi
#include "engine/model/cs2.h"
#include "engine/enginecontroller.h"
#include "engine/enginedef.h"
#include "engine/enginehash.h"
#include "engine/engineutil.h"
#include "engine/util/textcache.h"
#include "hijack/hijackmanager.h"
#include "util/textutil.h"
#include "disasm/disasm.h"
#include "dyncodec/dynsjis.h"
#include "winhook/hookcode.h"
#include "winhook/hookfun.h"
#include "memdbg/memsearch.h"
#include <qt_windows.h>
#include <cstdint>
#include <vector>

#define DEBUG "model/cs2"
#include "sakurakit/skdebug.h"

namespace { // unnamed
/**
 *  Sample game: ゆきこいめると
 *
 *  Example prefix to skip:
 *  03751294  81 40 5C 70 63 81 75 83 7B 83 4E 82 CC 8E AF 82  　\pc「ボクの識・
 *
 *  033CF370  5C 6E 81 40 5C 70 63 8C 4A 82 E8 95 D4 82 BB 82  \n　\pc繰り返そ・
 *  033CF380  A4 81 41 96 7B 93 96 82 C9 81 41 82 B1 82 CC 8B  ､、本当に、この・
 *  033CF390  47 90 DF 82 CD 81 41 83 8D 83 4E 82 C8 82 B1 82  G節は、ロクなこ・
 *  033CF3A0  C6 82 AA 82 C8 82 A2 81 42 00 AA 82 C8 82 A2 81  ﾆがない。.ｪない・
 *  033CF3B0  42 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  B...............
 *  033CF3C0  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
 *  033CF3D0  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
 *  033CF3E0  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
 *  033CF3F0  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
 *  033CF400  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
 *
 *  Sample choice texts:
 *
 *  str 155 選択肢
 *
 *  0 op01 最初から始める
 *
 *  1 select_go_tar たるひ初キスシーンを見る
 */
template <typename strT>
strT ltrim(strT text)
{
  strT lastText = nullptr;
  while (*text && text != lastText) {
    lastText = text;
    if (text[0] == 0x20)
      text++;
    if ((uchar)text[0] == 0x81 && (uchar)text[1] == 0x40) // skip space \u3000 (0x8140 in sjis)
      text += 2;
    if (text[0] == '\\') {
      text++;
      while (::islower(text[0]) || text[0] == '@')
        text++;
    }
  }
  while ((signed char)text[0] > 0 && text[0] != '[') // skip all leading ascii characters except "[" needed for ruby
    text++;
  return text;
}

// Remove trailing '\@'
size_t rtrim(LPCSTR text)
{
  size_t size = ::strlen(text);
  while (size >= 2 && text[size - 2] == '\\' && (uchar)text[size - 1] <= 127)
    size -= 2;
  return size;
}

namespace ScenarioHook {
namespace Private {

  bool isOtherText(LPCSTR text)
  {
    /* Sample game: ゆきこいめると */
    return ::strcmp(text, "\x91\x49\x91\xf0\x8e\x88") == 0; /* 選択肢 */
  }

  /**
   *  Sample game: 果つることなき未来ヨリ
   *
   *  Sample ecx:
   *
   *  03283A88    24 00 CD 02 76 16 02 00 24 00 CD 02 58 00 CD 02  $.ﾍv.$.ﾍX.ﾍ
   *  03283A98    BD 2D 01 00 1C 1C 49 03 14 65 06 00 14 65 06 00  ｽ-.Ie.e.
   *                                      this is ID,  this is the same ID: 0x066514
   *  03283AA8    80 64 06 00 20 8C 06 00 24 00 6C 0D 00 00 10 00  d. ・.$.l....
   *              this is ID: 0x066480
   *  03283AB8    C8 F1 C2 00 21 00 00 00 48 A9 75 00 E8 A9 96 00  ﾈ.!...Hｩu.隧・
   *  03283AC8    00 00 00 00 48 80 4F 03 00 00 00 00 CC CC CC CC  ....HO....ﾌﾌﾌﾌ
   *  03283AD8    CC CC CC CC CC CC CC CC CC CC CC CC CC CC CC CC  ﾌﾌﾌﾌﾌﾌﾌﾌﾌﾌﾌﾌﾌﾌﾌﾌ
   */
  //struct ClassArgument // for ecx
  //{
  //  DWORD unknown[7],
  //        split1,   // 0x20 - 9
  //        split2;   // 0x20
  //  // split1 - split2 is always 0x94
  //  DWORD split() const { return split1 - split2; } //
  //};
  bool hookBefore(winhook::hook_stack *s)
  {
    //static std::unordered_set<uint64_t> hashes_;
    auto text = (LPSTR)s->eax; // arg1
    if (!text || !*text || Util::allAscii(text))
      return true;
    // Alternatively, if do not skip ascii chars, edx is always 0x4ef74 for Japanese texts
    //if (s->edx != 0x4ef74)
    //  return true;
    auto trimmedText = ltrim(text);
    if (!trimmedText || !*trimmedText)
      return true;
    size_t trimmedSize = rtrim(trimmedText);
    auto role = Engine::OtherRole;
    //DOUT(QString::fromLocal8Bit((LPCSTR)s->esi));
    //auto splitText = (LPCSTR)s->esi;
    //if (::strcmp(splitText, "MES_SETNAME")) // This is for scenario text with voice
    //if (::strcmp(splitText, "MES_SETFACE"))
    //if (::strcmp(splitText, "pcm")) // first scenario or history without text
    //  return true;
    //auto retaddr = s->stack[1]; // caller
    //auto retaddr = s->stack[13]; // parent caller
    //auto split = *(DWORD *)s->esi;
    //auto split = s->esi - s->eax;
    //DOUT(split);
    //auto self = (ClassArgument *)s->ecx;
    //auto split = self->split();
    //enum { sig = 0 };
    auto self = s->ecx;
    if (!Engine::isAddressWritable(self)) // old cs2 game such as Grisaia
      self = s->stack[2]; // arg1
    ulong groupId = self;
    if (Engine::isAddressWritable(self))
      groupId = *(DWORD *)(self + 0x20);
    {
      static ulong minimumGroupId_ = -1; // I assume scenario thread to have minimum groupId
      static TextHashCache cache_(3); // capacity = 3
      //if (session_.addText(groupId, Engine::hashCharArray(text))) {
      if (groupId <= minimumGroupId_) {
        minimumGroupId_ = groupId;
        uint64_t h = Engine::hashCharArray(text);
        if (!cache_.contains(h)) {
          cache_.add(h);
          role = Engine::ScenarioRole;
          if (isOtherText(text))
            role = Engine::OtherRole;
          else if (::isdigit(text[0]))
            role = Engine::ChoiceRole;
          else if (trimmedText == text && !trimmedText[trimmedSize] // no prefix and suffix
                   && Engine::guessIsNameText(trimmedText, trimmedSize))
            role = Engine::NameRole;
        }
      }
    }
    auto sig = Engine::hashThreadSignature(role, groupId);
    QByteArray oldData(trimmedText, trimmedSize),
               newData = EngineController::instance()->dispatchTextA(oldData, role, sig);
    if (newData == oldData)
      return true;
    if (trimmedText[trimmedSize])
      newData.append(trimmedText + trimmedSize);
    ::strcpy(trimmedText, newData.constData());
    return true;
  }
} // namespace Private

/**
 *  Sample game: 果つることなき未来ヨリ
 *
 *  Debugging message:
 *  - Hook to GetGlyphOutlineA
 *  - Find "MES_SHOW" address on the stack
 *    Alternatively, find the address of "fes.int/flow.fes" immediately after the game is launched
 *  - Use hardware breakpoint to find out when "MES_SHOW" is overridden
 *    Only stop when text is written by valid scenario text.
 *
 *  00503ADE   CC               INT3
 *  00503ADF   CC               INT3
 *  00503AE0   8B4424 0C        MOV EAX,DWORD PTR SS:[ESP+0xC]
 *  00503AE4   8B4C24 04        MOV ECX,DWORD PTR SS:[ESP+0x4]
 *  00503AE8   56               PUSH ESI
 *  00503AE9   FF30             PUSH DWORD PTR DS:[EAX]
 *  00503AEB   E8 102F1600      CALL Hatsumir.00666A00	; jichi: text in eax after this call
 *  00503AF0   BE 18058900      MOV ESI,Hatsumir.00890518                ; ASCII "fes.int/flow.fes"
 *  00503AF5   8BC8             MOV ECX,EAX ; jichi: esi is the target location
 *  00503AF7   2BF0             SUB ESI,EAX
 *  00503AF9   8DA424 00000000  LEA ESP,DWORD PTR SS:[ESP]
 *  00503B00   8A11             MOV DL,BYTE PTR DS:[ECX]
 *  00503B02   8D49 01          LEA ECX,DWORD PTR DS:[ECX+0x1]
 *  00503B05   88540E FF        MOV BYTE PTR DS:[ESI+ECX-0x1],DL    ; jichi: target location modified here
 *  00503B09   84D2             TEST DL,DL
 *  00503B0B  ^75 F3            JNZ SHORT Hatsumir.00503B00
 *  00503B0D   8B4C24 0C        MOV ECX,DWORD PTR SS:[ESP+0xC]
 *  00503B11   50               PUSH EAX
 *  00503B12   68 18058900      PUSH Hatsumir.00890518                   ; ASCII "fes.int/flow.fes"
 *  00503B17   8B89 B4000000    MOV ECX,DWORD PTR DS:[ECX+0xB4]
 *  00503B1D   E8 EE030B00      CALL Hatsumir.005B3F10
 *  00503B22   B8 02000000      MOV EAX,0x2
 *  00503B27   5E               POP ESI
 *  00503B28   C2 1000          RETN 0x10
 *  00503B2B   CC               INT3
 *  00503B2C   CC               INT3
 *  00503B2D   CC               INT3
 *  00503B2E   CC               INT3
 *
 *  EAX 0353B1A0    ; jichi: text here
 *  ECX 00D86D08
 *  EDX 0004EF74
 *  EBX 00012DB2
 *  ESP 0525EBAC
 *  EBP 0525ED6C
 *  ESI 00D86D08
 *  EDI 00000000
 *  EIP 00503AF0 Hatsumir.00503AF0
 *
 *  0525EBAC   00D86D08
 *  0525EBB0   0066998E  RETURN to Hatsumir.0066998E
 *  0525EBB4   00D86D08
 *  0525EBB8   00B16188
 *  0525EBBC   035527D8
 *  0525EBC0   0525EBE4
 *  0525EBC4   00B16188
 *  0525EBC8   00D86D08
 *  0525EBCC   0525F62B  ASCII "ript.kcs"
 *  0525EBD0   00000004
 *  0525EBD4   00000116
 *  0525EBD8   00000003
 *  0525EBDC   00000003
 *  0525EBE0   00665C08  RETURN to Hatsumir.00665C08
 *  0525EBE4   CCCCCCCC
 *  0525EBE8   0525F620  ASCII "kcs.int/sscript.kcs"
 *  0525EBEC   00694D94  Hatsumir.00694D94
 *  0525EBF0   004B278F  RETURN to Hatsumir.004B278F from Hatsumir.00666CA0
 *  0525EBF4   B3307379
 *  0525EBF8   0525ED04
 *  0525EBFC   00B16188
 *  0525EC00   0525ED04
 *  0525EC04   00B16188
 *  0525EC08   00CC5440
 *  0525EC0C   02368938
 *  0525EC10   0069448C  ASCII "%s/%s"
 *  0525EC14   00B45B18  ASCII "kcs.int"
 *  0525EC18   00000001
 *  0525EC1C   023741E0
 *  0525EC20   0000000A
 *  0525EC24   0049DBB3  RETURN to Hatsumir.0049DBB3 from Hatsumir.00605A84
 *  0525EC28   72637373
 *  0525EC2C   2E747069
 *  0525EC30   0073636B  Hatsumir.0073636B
 *  0525EC34   0525ED04
 *  0525EC38   0053ECDE  RETURN to Hatsumir.0053ECDE from Hatsumir.004970C0
 *  0525EC3C   0525EC80
 *  0525EC40   023D9FB8
 *
 *  Alternative ruby hook:
 *  It will hook to the beginning of the Ruby processing function, which is not better than the current approach.
 *  http://lab.aralgood.com/index.php?mid=board_lecture&search_target=title_content&search_keyword=CS&document_srl=1993027
 *
 *  Sample game: Grisaia3 グリザイアの楽園
 *
 *  004B00CB   CC               INT3
 *  004B00CC   CC               INT3
 *  004B00CD   CC               INT3
 *  004B00CE   CC               INT3
 *  004B00CF   CC               INT3
 *  004B00D0   8B4424 0C        MOV EAX,DWORD PTR SS:[ESP+0xC]
 *  004B00D4   8B08             MOV ECX,DWORD PTR DS:[EAX]
 *  004B00D6   56               PUSH ESI
 *  004B00D7   51               PUSH ECX
 *  004B00D8   8B4C24 0C        MOV ECX,DWORD PTR SS:[ESP+0xC]
 *  004B00DC   E8 7F191300      CALL .005E1A60
 *  004B00E1   BE D0E87B00      MOV ESI,.007BE8D0
 *  004B00E6   8BC8             MOV ECX,EAX
 *  004B00E8   2BF0             SUB ESI,EAX
 *  004B00EA   8D9B 00000000    LEA EBX,DWORD PTR DS:[EBX]
 *  004B00F0   8A11             MOV DL,BYTE PTR DS:[ECX]
 *  004B00F2   88140E           MOV BYTE PTR DS:[ESI+ECX],DL
 *  004B00F5   41               INC ECX
 *  004B00F6   84D2             TEST DL,DL
 *  004B00F8  ^75 F6            JNZ SHORT .004B00F0
 *  004B00FA   8B5424 0C        MOV EDX,DWORD PTR SS:[ESP+0xC]
 *  004B00FE   8B8A B4000000    MOV ECX,DWORD PTR DS:[EDX+0xB4]
 *  004B0104   50               PUSH EAX
 *  004B0105   68 D0E87B00      PUSH .007BE8D0
 *  004B010A   E8 818D0600      CALL .00518E90
 *  004B010F   B8 02000000      MOV EAX,0x2
 *  004B0114   5E               POP ESI
 *  004B0115   C2 1000          RETN 0x10
 *  004B0118   CC               INT3
 *  004B0119   CC               INT3
 *  004B011A   CC               INT3
 *  004B011B   CC               INT3
 *  004B011C   CC               INT3
 *
 *  Sample game: Grisaia1 グリザイアの果実
 *  00498579   CC               INT3
 *  0049857A   CC               INT3
 *  0049857B   CC               INT3
 *  0049857C   CC               INT3
 *  0049857D   CC               INT3
 *  0049857E   CC               INT3
 *  0049857F   CC               INT3
 *  00498580   8B4424 0C        MOV EAX,DWORD PTR SS:[ESP+0xC]
 *  00498584   8B08             MOV ECX,DWORD PTR DS:[EAX]  ; jichi: ecx is no longer a pointer
 *  00498586   8B4424 04        MOV EAX,DWORD PTR SS:[ESP+0x4]
 *  0049858A   56               PUSH ESI
 *  0049858B   E8 10920500      CALL Grisaia.004F17A0
 *  00498590   BE D89C7600      MOV ESI,Grisaia.00769CD8                 ; ASCII "bgm01"
 *  00498595   8BC8             MOV ECX,EAX
 *  00498597   2BF0             SUB ESI,EAX
 *  00498599   8DA424 00000000  LEA ESP,DWORD PTR SS:[ESP]
 *  004985A0   8A11             MOV DL,BYTE PTR DS:[ECX]
 *  004985A2   88140E           MOV BYTE PTR DS:[ESI+ECX],DL
 *  004985A5   41               INC ECX
 *  004985A6   84D2             TEST DL,DL
 *  004985A8  ^75 F6            JNZ SHORT Grisaia.004985A0
 *  004985AA   8B4C24 0C        MOV ECX,DWORD PTR SS:[ESP+0xC]
 *  004985AE   8B91 B4000000    MOV EDX,DWORD PTR DS:[ECX+0xB4]
 *  004985B4   50               PUSH EAX
 *  004985B5   68 D89C7600      PUSH Grisaia.00769CD8                    ; ASCII "bgm01"
 *  004985BA   52               PUSH EDX
 *  004985BB   E8 701C0600      CALL Grisaia.004FA230
 *  004985C0   B8 02000000      MOV EAX,0x2
 *  004985C5   5E               POP ESI
 *  004985C6   C2 1000          RETN 0x10
 *  004985C9   CC               INT3
 *  004985CA   CC               INT3
 *  004985CB   CC               INT3
 *  004985CC   CC               INT3
 *  004985CD   CC               INT3
 */
bool attach(ulong startAddress, ulong stopAddress)
{
  const uint8_t bytes[] = {
    0xe8, XX4,              // 004b00dc   e8 7f191300      call .005e1a60 ; jichi: hook after here
    0xbe, XX4,              // 004b00e1   be d0e87b00      mov esi,.007be8d0
    0x8b,0xc8,              // 004b00e6   8bc8             mov ecx,eax
    0x2b,0xf0               // 004b00e8   2bf0             sub esi,eax
    //XX2, XX, 0x00,0x00,0x00 // 004b00ea   8d9b 00000000    lea ebx,dword ptr ds:[ebx]
  };
  ulong addr = MemDbg::matchBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  return addr && winhook::hook_after(addr, Private::hookBefore);
}

} // namespace ScenarioHook

namespace Patch {

namespace Private {
  // String in ecx
  bool __fastcall isLeadByteChar(const char *s, DWORD edx)
  {
    Q_UNUSED(edx);
    return s && dynsjis::isleadchar(*s);
    //return dynsjis::isleadstr(s); // no idea why this will cause Grisaia3 to hang
    //return ::IsDBCSLeadByte(HIBYTE(testChar));
  }

} // namespace Private

/**
 *  Sample game: ゆきこいめると
 *
 *  This function is found by searching the following instruction:
 *  00511C8E   3C 81            CMP AL,0x81
 *
 *  This function is very similar to that in LC-ScriptEngine.
 *
 *  Return 1 if the first byte in arg1 is leading byte else 0.
 *
 *  00511C7C   CC               INT3
 *  00511C7D   CC               INT3
 *  00511C7E   CC               INT3
 *  00511C7F   CC               INT3
 *  00511C80   8B4C24 04        MOV ECX,DWORD PTR SS:[ESP+0x4]
 *  00511C84   85C9             TEST ECX,ECX
 *  00511C86   74 2F            JE SHORT .00511CB7
 *  00511C88   8A01             MOV AL,BYTE PTR DS:[ECX]
 *  00511C8A   84C0             TEST AL,AL
 *  00511C8C   74 29            JE SHORT .00511CB7
 *  00511C8E   3C 81            CMP AL,0x81
 *  00511C90   72 04            JB SHORT .00511C96
 *  00511C92   3C 9F            CMP AL,0x9F
 *  00511C94   76 08            JBE SHORT .00511C9E
 *  00511C96   3C E0            CMP AL,0xE0
 *  00511C98   72 1D            JB SHORT .00511CB7
 *  00511C9A   3C EF            CMP AL,0xEF
 *  00511C9C   77 19            JA SHORT .00511CB7
 *  00511C9E   8A41 01          MOV AL,BYTE PTR DS:[ECX+0x1]
 *  00511CA1   3C 40            CMP AL,0x40
 *  00511CA3   72 04            JB SHORT .00511CA9
 *  00511CA5   3C 7E            CMP AL,0x7E
 *  00511CA7   76 08            JBE SHORT .00511CB1
 *  00511CA9   3C 80            CMP AL,0x80
 *  00511CAB   72 0A            JB SHORT .00511CB7
 *  00511CAD   3C FC            CMP AL,0xFC
 *  00511CAF   77 06            JA SHORT .00511CB7
 *  00511CB1   B8 01000000      MOV EAX,0x1
 *  00511CB6   C3               RETN
 *  00511CB7   33C0             XOR EAX,EAX
 *  00511CB9   C3               RETN
 *  00511CBA   CC               INT3
 *  00511CBB   CC               INT3
 *  00511CBC   CC               INT3
 *  00511CBD   CC               INT3
 *
 *  Sample game: Grisaia3 グリザイアの楽園
 *  0050747F   CC               INT3
 *  00507480   8B4C24 04        MOV ECX,DWORD PTR SS:[ESP+0x4]  ; jichi: text in arg1
 *  00507484   85C9             TEST ECX,ECX
 *  00507486   74 2F            JE SHORT .005074B7
 *  00507488   8A01             MOV AL,BYTE PTR DS:[ECX]
 *  0050748A   84C0             TEST AL,AL
 *  0050748C   74 29            JE SHORT .005074B7
 *  0050748E   3C 81            CMP AL,0x81
 *  00507490   72 04            JB SHORT .00507496
 *  00507492   3C 9F            CMP AL,0x9F
 *  00507494   76 08            JBE SHORT .0050749E
 *  00507496   3C E0            CMP AL,0xE0
 *  00507498   72 1D            JB SHORT .005074B7
 *  0050749A   3C EF            CMP AL,0xEF
 *  0050749C   77 19            JA SHORT .005074B7
 *  0050749E   8A41 01          MOV AL,BYTE PTR DS:[ECX+0x1]
 *  005074A1   3C 40            CMP AL,0x40
 *  005074A3   72 04            JB SHORT .005074A9
 *  005074A5   3C 7E            CMP AL,0x7E
 *  005074A7   76 08            JBE SHORT .005074B1
 *  005074A9   3C 80            CMP AL,0x80
 *  005074AB   72 0A            JB SHORT .005074B7
 *  005074AD   3C FC            CMP AL,0xFC
 *  005074AF   77 06            JA SHORT .005074B7
 *  005074B1   B8 01000000      MOV EAX,0x1
 *  005074B6   C3               RETN
 *  005074B7   33C0             XOR EAX,EAX
 *  005074B9   C3               RETN
 *  005074BA   CC               INT3
 *  005074BB   CC               INT3
 *  005074BC   CC               INT3
 *  005074BD   CC               INT3
 *
 *  Sample game: Grisaia1 グリザイアの果実
 *  0041488A   CC               INT3
 *  0041488B   CC               INT3
 *  0041488C   CC               INT3
 *  0041488D   CC               INT3
 *  0041488E   CC               INT3
 *  0041488F   CC               INT3
 *  00414890   85C9             TEST ECX,ECX    ; jichi: text in ecx
 *  00414892   74 2F            JE SHORT Grisaia.004148C3
 *  00414894   8A01             MOV AL,BYTE PTR DS:[ECX]
 *  00414896   84C0             TEST AL,AL
 *  00414898   74 29            JE SHORT Grisaia.004148C3
 *  0041489A   3C 81            CMP AL,0x81
 *  0041489C   72 04            JB SHORT Grisaia.004148A2
 *  0041489E   3C 9F            CMP AL,0x9F
 *  004148A0   76 08            JBE SHORT Grisaia.004148AA
 *  004148A2   3C E0            CMP AL,0xE0
 *  004148A4   72 1D            JB SHORT Grisaia.004148C3
 *  004148A6   3C EF            CMP AL,0xEF
 *  004148A8   77 19            JA SHORT Grisaia.004148C3
 *  004148AA   8A41 01          MOV AL,BYTE PTR DS:[ECX+0x1]
 *  004148AD   3C 40            CMP AL,0x40
 *  004148AF   72 04            JB SHORT Grisaia.004148B5
 *  004148B1   3C 7E            CMP AL,0x7E
 *  004148B3   76 08            JBE SHORT Grisaia.004148BD
 *  004148B5   3C 80            CMP AL,0x80
 *  004148B7   72 0A            JB SHORT Grisaia.004148C3
 *  004148B9   3C FC            CMP AL,0xFC
 *  004148BB   77 06            JA SHORT Grisaia.004148C3
 *  004148BD   B8 01000000      MOV EAX,0x1
 *  004148C2   C3               RETN
 *  004148C3   33C0             XOR EAX,EAX
 *  004148C5   C3               RETN
 *  004148C6   CC               INT3
 *  004148C7   CC               INT3
 *  004148C8   CC               INT3
 */
bool patchEncoding(ulong startAddress, ulong stopAddress)
{
  const uint8_t bytes[] = {
    0x74, 0x29,     // 00511c8c   74 29            je short .00511cb7
    0x3c, 0x81      // 00511c8e   3c 81            cmp al,0x81
  };
  ulong addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  for (auto p = addr; p - addr < 20; p += ::disasm((LPCVOID)p))
    if (*(WORD *)p == 0xc985)// 00414890   85C9             TEST ECX,ECX    ; jichi: text in ecx
      return winhook::replace_fun(p, (ulong)Private::isLeadByteChar);
  return false;
}

} // namespace Patch
} // unnamed namespace

bool CatSystemEngine::attach()
{
  ulong startAddress, stopAddress;
  if (!Engine::getProcessMemoryRange(&startAddress, &stopAddress))
    return false;
  if (!ScenarioHook::attach(startAddress, stopAddress))
    return false;
  if (Patch::patchEncoding(startAddress, stopAddress)) {
    enableDynamicEncoding = true;
    DOUT("patch encoding succeeded");
  } else
    DOUT("patch encoding FAILED");
  HijackManager::instance()->attachFunction((ulong)::GetGlyphOutlineA);
  return true;
}

/**
 *  Sample text:
 *
 *  0606DA2C  5B 8F E3 83 96 90 A3 2F 82 A9 82 DD 82 AA 82 B9  [上ヶ瀬/かみがせ
 *  0606DA3C  5D 8E 73 8A 58 82 A9 82 E7 83 6F 83 58 82 C5 97  ]市街からバスで・
 *  0606DA4C  68 82 E7 82 EA 82 E9 82 B1 82 C6 82 52 82 4F 95  hられること３０・
 *  0606DA5C  AA 81 42 91 E5 82 AB 82 C8 8B B4 82 F0 89 7A 82  ｪ。大きな橋を越・
 *  0606DA6C  A6 82 C4 81 41 8B DF 91 E3 93 49 82 C8 83 72 83  ｦて、近代的なビ・
 *  0606DA7C  8B 82 AA 8C 9A 82 BF 95 C0 82 D4 8D C5 90 56 89  汲ｪ建ち並ぶ最新・
 *  0606DA8C  73 82 CC 8A 58 81 41 82 BB 82 B5 82 C4 82 BB 82  sの街、そしてそ・
 *  0606DA9C  CC 92 86 90 53 82 C6 82 C8 82 E9 8A 77 89 80 81  ﾌ中心となる学園・
 *  0606DAAC  63 81 63 81 42 00 06 06 94 65 ED 76 38 01 31 00  c…。.覇咩81.
 *  0606DABC  70 65 ED 76 A5 2B A2 70 00 00 00 00 00 00 31 00  pe咩･+｢p......1.
 *  0606DACC  48 89 2D 10 10 8D 28 10 00 00 00 00 07 00 00 07  H・・......
 */
QString CatSystemEngine::rubyCreate(const QString &rb, const QString &rt)
{
  static QString fmt = "[%1/%2]";
  return fmt.arg(rb, rt);
}

// Remove furigana in scenario thread.
QString CatSystemEngine::rubyRemove(const QString &text)
{
  if (!text.contains(']'))
    return text;
  static QRegExp rx("\\[(.+)/.+\\]");
  if (!rx.isMinimal())
    rx.setMinimal(true);
  return QString(text).replace(rx, "\\1");
}

QString CatSystemEngine::translationFilter(const QString &text, int role)
{
  // http://sakuradite.com/topic/1100
  // Replace certain thin characters to wide ones for choice texts
  if (role != Engine::ChoiceRole)
    return text;
  QString ret = text;
  if (ret.contains('/'))
    ret.replace(" / ", "/")
       .replace('/', L'\xff0f');
  ret.replace(' ', L'\u3000');
  return ret;
}

// EOF

#if 0

  class TextSession
  {
    ulong sessionId_;
    bool sessionActive_;
    std::vector<uint64_t> hashes_;
  public:
    TextSession() : sessionId_(0), sessionActive_(false) {}
    bool addText(ulong sessionId, uint64_t hash); // Return if it is new text
  };

  bool TextSession::addText(ulong sessionId, uint64_t hash) // Return if it is new text
  {
    bool hashExists = std::find(hashes_.begin(), hashes_.end(), hash) != hashes_.end();
    if (sessionActive_ && sessionId == sessionId_) {
      if (!hashExists)
        hashes_.push_back(hash);
      return true;
    } else if (hashExists) {
      sessionActive_ = false;
      return false;
    } else {
      hashes_.clear();
      sessionId_ = sessionId;
      sessionActive_ = true;
      hashes_.push_back(hash);
      return true;
    }
  }


namespace ScenarioHook {
namespace Private {
  bool hookBefore(winhook::hook_stack *s)
  {
    auto text = (LPSTR)s->stack[1]; // arg1
    text = ltrim(text);
    if (!text || !*text || Util::allAscii(text))
      return true;
    size_t size = ::strlen(text);
    auto role = text[size + 2] ? Engine::NameRole : Engine::ScenarioRole;
    auto split = s->stack[0]; // retaddr
    auto sig = Engine::hashThreadSignature(role, split);
    QByteArray data = EngineController::instance()->dispatchTextA(text, role, sig);
    ::strcpy(text, data.constData());
    return true;
  }
} // namespace Private

/**
 *  Sample game: イノセントガール
 *  See: http://capita.tistory.com/m/post/176
 *
 *  Scenario pattern: 56 8B 74 24 08 8B C6 57 8D 78 01 EB 03
 *
 *  0040264C   CC               INT3
 *  0040264D   CC               INT3
 *  0040264E   CC               INT3
 *  0040264F   CC               INT3
 *  00402650   56               PUSH ESI
 *  00402651   8B7424 08        MOV ESI,DWORD PTR SS:[ESP+0x8]
 *  00402655   8BC6             MOV EAX,ESI
 *  00402657   57               PUSH EDI
 *  00402658   8D78 01          LEA EDI,DWORD PTR DS:[EAX+0x1]
 *  0040265B   EB 03            JMP SHORT .00402660
 *  0040265D   8D49 00          LEA ECX,DWORD PTR DS:[ECX]
 *  00402660   8A10             MOV DL,BYTE PTR DS:[EAX]
 *  00402662   40               INC EAX
 *  00402663   84D2             TEST DL,DL
 *  00402665  ^75 F9            JNZ SHORT .00402660
 *  00402667   2BC7             SUB EAX,EDI
 *  00402669   50               PUSH EAX
 *  0040266A   56               PUSH ESI
 *  0040266B   E8 F0000000      CALL .00402760
 *  00402670   5F               POP EDI
 *  00402671   5E               POP ESI
 *  00402672   C2 0400          RETN 0x4
 *  00402675   CC               INT3
 *  00402676   CC               INT3
 *  00402677   CC               INT3
 *  00402678   CC               INT3
 *  00402679   CC               INT3
 */
bool attach(ulong startAddress, ulong stopAddress)
{
  const uint8_t bytes[] = {
    0x56,                 // 00402650   56               push esi
    0x8b,0x74,0x24, 0x08, // 00402651   8b7424 08        mov esi,dword ptr ss:[esp+0x8]
    0x8b,0xc6,            // 00402655   8bc6             mov eax,esi
    0x57,                 // 00402657   57               push edi
    0x8d,0x78, 0x01,      // 00402658   8d78 01          lea edi,dword ptr ds:[eax+0x1]
    0xeb, 0x03            // 0040265b   eb 03            jmp short .00402660
  };
  ulong addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  if (!addr)
    return false;
  return winhook::hook_before(addr, Private::hookBefore);
}

} // namespace ScenarioHook

namespace HistoryHook {
namespace Private {
  bool hookBefore(winhook::hook_stack *s)
  {
    auto text = (LPSTR)s->stack[1]; // arg1
    text = ltrim(text);
    if (!text || !*text)
      return true;
    enum { role = Engine::HistoryRole };
    auto split = s->stack[0]; // retaddr
    auto sig = Engine::hashThreadSignature(role, split);
    QByteArray data = EngineController::instance()->dispatchTextA(text, role, sig);
    ::strcpy(text, data.constData());
    return true;
  }
} // namespace Private

/**
 *  Sample game: イノセントガール
 *  See: http://capita.tistory.com/m/post/176
 *
 *  History pattern: 74 0C B8 6E 5C 00 00
 *
 *  0832D9E8   00509ADC  RETURN to .00509ADC from .00508450
 *  0832D9EC   03751294
 *  0832D9F0   0832DA2C
 *  0832D9F4   0832DA30
 *  0832D9F8   0832DA60
 *  0832D9FC   599E574D
 *  0832DA00   0450B1B0
 *  0832DA04   036962E2
 *  0832DA08   00000000
 *  0832DA0C   04562390
 *  0832DA10   FFFFFFFF
 *  0832DA14   0832DB34
 *  0832DA18   0832DC34
 *  0832DA1C   00000000
 *  0832DA20   00000002
 *  0832DA24   00000000
 *
 *  Text in arg1. Sample text:
 *
 *  03751294  81 40 5C 70 63 81 75 83 7B 83 4E 82 CC 8E AF 82  　\pc「ボクの識・
 *  037512A4  C1 82 C4 82 A2 82 E9 90 A2 8A 45 82 CD 81 40 83  ﾁている世界は　・
 *  037512B4  4C 83 7E 82 C6 93 AF 82 B6 82 BE 82 EB 82 A4 82  Lミと同じだろう・
 *  037512C4  A9 81 76 00 00 00 00 00 00 00 00 00 00 00 00 00  ｩ」.............
 *  037512D4  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
 *  037512E4  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
 *  037512F4  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
 *  03751304  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
 *  03751314  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
 *
 *  EAX 0832DA2C
 *  ECX 04562390
 *  EDX 0832DA30
 *  EBX 00000010
 *  ESP 0832D9E8
 *  EBP 00000001
 *  ESI 04562390
 *  EDI 03751294
 *  EIP 00508450 .00508450
 *
 *  0050844B   CC               INT3
 *  0050844C   CC               INT3
 *  0050844D   CC               INT3
 *  0050844E   CC               INT3
 *  0050844F   CC               INT3
 *  00508450   6A FF            PUSH -0x1
 *  00508452   68 89706500      PUSH .00657089
 *  00508457   64:A1 00000000   MOV EAX,DWORD PTR FS:[0]
 *  0050845D   50               PUSH EAX
 *  0050845E   81EC 7C050000    SUB ESP,0x57C
 *  00508464   A1 889A7D00      MOV EAX,DWORD PTR DS:[0x7D9A88]
 *  00508469   33C4             XOR EAX,ESP
 *  0050846B   898424 78050000  MOV DWORD PTR SS:[ESP+0x578],EAX
 *  00508472   53               PUSH EBX
 *  00508473   55               PUSH EBP
 *  00508474   56               PUSH ESI
 *  00508475   57               PUSH EDI
 *  00508476   A1 889A7D00      MOV EAX,DWORD PTR DS:[0x7D9A88]
 *  0050847B   33C4             XOR EAX,ESP
 *  0050847D   50               PUSH EAX
 *  0050847E   8D8424 90050000  LEA EAX,DWORD PTR SS:[ESP+0x590]
 *  00508485   64:A3 00000000   MOV DWORD PTR FS:[0],EAX
 *  0050848B   8B8424 A0050000  MOV EAX,DWORD PTR SS:[ESP+0x5A0]
 *  00508492   8B9424 A8050000  MOV EDX,DWORD PTR SS:[ESP+0x5A8]
 *  00508499   8BAC24 AC050000  MOV EBP,DWORD PTR SS:[ESP+0x5AC]
 *  005084A0   33DB             XOR EBX,EBX
 *  005084A2   8BF1             MOV ESI,ECX
 *  005084A4   8B8C24 A4050000  MOV ECX,DWORD PTR SS:[ESP+0x5A4]
 *  005084AB   894424 1C        MOV DWORD PTR SS:[ESP+0x1C],EAX
 *  005084AF   894C24 68        MOV DWORD PTR SS:[ESP+0x68],ECX
 *  005084B3   895424 5C        MOV DWORD PTR SS:[ESP+0x5C],EDX
 *  005084B7   895C24 2C        MOV DWORD PTR SS:[ESP+0x2C],EBX
 *  005084BB   895C24 64        MOV DWORD PTR SS:[ESP+0x64],EBX
 *  005084BF   C78424 88000000 >MOV DWORD PTR SS:[ESP+0x88],0xF
 *  005084CA   899C24 84000000  MOV DWORD PTR SS:[ESP+0x84],EBX
 *  005084D1   885C24 74        MOV BYTE PTR SS:[ESP+0x74],BL
 *  005084D5   8B46 10          MOV EAX,DWORD PTR DS:[ESI+0x10]
 *  005084D8   8B40 1C          MOV EAX,DWORD PTR DS:[EAX+0x1C]
 *  005084DB   8B8E F0000000    MOV ECX,DWORD PTR DS:[ESI+0xF0]
 *  005084E1   8BBE DC000000    MOV EDI,DWORD PTR DS:[ESI+0xDC]
 *  005084E7   03C8             ADD ECX,EAX
 *  005084E9   894C24 6C        MOV DWORD PTR SS:[ESP+0x6C],ECX
 *  005084ED   8D4C24 70        LEA ECX,DWORD PTR SS:[ESP+0x70]
 *  005084F1   899C24 98050000  MOV DWORD PTR SS:[ESP+0x598],EBX
 *  005084F8   895C24 24        MOV DWORD PTR SS:[ESP+0x24],EBX
 *  005084FC   895C24 60        MOV DWORD PTR SS:[ESP+0x60],EBX
 *  00508500   E8 1B60F2FF      CALL .0042E520
 *  00508505   F686 E0000000 02 TEST BYTE PTR DS:[ESI+0xE0],0x2
 *  0050850C   74 72            JE SHORT .00508580
 *  0050850E   395E 08          CMP DWORD PTR DS:[ESI+0x8],EBX
 *  00508511   75 6D            JNZ SHORT .00508580
 *  00508513   8BC5             MOV EAX,EBP
 *  00508515   C74424 58 0F0000>MOV DWORD PTR SS:[ESP+0x58],0xF
 *  0050851D   895C24 54        MOV DWORD PTR SS:[ESP+0x54],EBX
 *  00508521   885C24 44        MOV BYTE PTR SS:[ESP+0x44],BL
 *  00508525   8D50 01          LEA EDX,DWORD PTR DS:[EAX+0x1]
 *  00508528   8A08             MOV CL,BYTE PTR DS:[EAX]
 *  0050852A   40               INC EAX
 *  0050852B   3ACB             CMP CL,BL
 *  0050852D  ^75 F9            JNZ SHORT .00508528
 *  0050852F   2BC2             SUB EAX,EDX
 *  00508531   50               PUSH EAX
 *  00508532   55               PUSH EBP
 *  00508533   8D4C24 48        LEA ECX,DWORD PTR SS:[ESP+0x48]
 *  00508537   E8 24A2EFFF      CALL .00402760
 *  0050853C   6A FF            PUSH -0x1
 *  0050853E   53               PUSH EBX
 *  0050853F   8D5424 48        LEA EDX,DWORD PTR SS:[ESP+0x48]
 *  00508543   52               PUSH EDX
 *  00508544   8D4C24 7C        LEA ECX,DWORD PTR SS:[ESP+0x7C]
 *  00508548   C68424 A4050000 >MOV BYTE PTR SS:[ESP+0x5A4],0x1
 *  00508550   E8 1BA0EFFF      CALL .00402570
 *  00508555   837C24 58 10     CMP DWORD PTR SS:[ESP+0x58],0x10
 *  0050855A   889C24 98050000  MOV BYTE PTR SS:[ESP+0x598],BL
 *  00508561   72 0D            JB SHORT .00508570
 *  00508563   8B4424 44        MOV EAX,DWORD PTR SS:[ESP+0x44]
 *  00508567   50               PUSH EAX
 *  00508568   E8 05620A00      CALL .005AE772
 *  0050856D   83C4 04          ADD ESP,0x4
 *  00508570   8BC5             MOV EAX,EBP
 *  00508572   8D50 01          LEA EDX,DWORD PTR DS:[EAX+0x1]
 *  00508575   8A08             MOV CL,BYTE PTR DS:[EAX]
 *  00508577   40               INC EAX
 *  00508578   3ACB             CMP CL,BL
 *  0050857A  ^75 F9            JNZ SHORT .00508575
 *  0050857C   2BC2             SUB EAX,EDX
 *  0050857E   2BF8             SUB EDI,EAX
 *  00508580   8B4424 1C        MOV EAX,DWORD PTR SS:[ESP+0x1C]
 *  00508584   8D4C24 28        LEA ECX,DWORD PTR SS:[ESP+0x28]
 *  00508588   51               PUSH ECX
 *  00508589   8D5424 1C        LEA EDX,DWORD PTR SS:[ESP+0x1C]
 *  0050858D   52               PUSH EDX
 *  0050858E   50               PUSH EAX
 *  0050858F   8BCE             MOV ECX,ESI
 *  00508591   E8 FAEBFFFF      CALL .00507190
 *  00508596   85C0             TEST EAX,EAX
 *  00508598   74 4E            JE SHORT .005085E8
 *  0050859A   8B96 98000000    MOV EDX,DWORD PTR DS:[ESI+0x98]
 *  005085A0   8B86 80000000    MOV EAX,DWORD PTR DS:[ESI+0x80]
 *  005085A6   8D8E 80000000    LEA ECX,DWORD PTR DS:[ESI+0x80]
 *  005085AC   895424 3C        MOV DWORD PTR SS:[ESP+0x3C],EDX
 *  005085B0   8D5424 18        LEA EDX,DWORD PTR SS:[ESP+0x18]
 *  005085B4   894424 38        MOV DWORD PTR SS:[ESP+0x38],EAX
 *  005085B8   52               PUSH EDX
 *  005085B9   8D4424 34        LEA EAX,DWORD PTR SS:[ESP+0x34]
 *  005085BD   50               PUSH EAX
 *  005085BE   E8 6D190000      CALL .00509F30
 *  005085C3   8BE8             MOV EBP,EAX
 *  005085C5   8B45 00          MOV EAX,DWORD PTR SS:[EBP]
 *  005085C8   3BC3             CMP EAX,EBX
 *  005085CA   74 06            JE SHORT .005085D2
 *  005085CC   3B4424 38        CMP EAX,DWORD PTR SS:[ESP+0x38]
 *  005085D0   74 05            JE SHORT .005085D7
 *  005085D2   E8 E1650A00      CALL .005AEBB8
 *  005085D7   8B4C24 3C        MOV ECX,DWORD PTR SS:[ESP+0x3C]
 *  005085DB   394D 04          CMP DWORD PTR SS:[EBP+0x4],ECX
 *  005085DE   74 08            JE SHORT .005085E8
 *  005085E0   8B5424 28        MOV EDX,DWORD PTR SS:[ESP+0x28]
 *  005085E4   895424 60        MOV DWORD PTR SS:[ESP+0x60],EDX
 *  005085E8   8B4424 1C        MOV EAX,DWORD PTR SS:[ESP+0x1C]
 *  005085EC   895C24 14        MOV DWORD PTR SS:[ESP+0x14],EBX
 *  005085F0   3818             CMP BYTE PTR DS:[EAX],BL
 *  005085F2   0F84 9E030000    JE .00508996
 *  005085F8   8D47 FF          LEA EAX,DWORD PTR DS:[EDI-0x1]
 *  005085FB   33C9             XOR ECX,ECX
 *  005085FD   3BC3             CMP EAX,EBX
 *  005085FF   895C24 38        MOV DWORD PTR SS:[ESP+0x38],EBX
 *  00508603   895C24 20        MOV DWORD PTR SS:[ESP+0x20],EBX
 *  00508607   7E 74            JLE SHORT .0050867D
 *  00508609   8D68 FF          LEA EBP,DWORD PTR DS:[EAX-0x1]
 *  0050860C   D1ED             SHR EBP,1
 *  0050860E   45               INC EBP
 *  0050860F   8D4C2D 00        LEA ECX,DWORD PTR SS:[EBP+EBP]
 *  00508613   894C24 30        MOV DWORD PTR SS:[ESP+0x30],ECX
 *  00508617   EB 07            JMP SHORT .00508620
 *  00508619   8DA424 00000000  LEA ESP,DWORD PTR SS:[ESP]
 *  00508620   6A 02            PUSH 0x2
 *  00508622   68 0CAC6600      PUSH .0066AC0C
 *  00508627   8D4C24 48        LEA ECX,DWORD PTR SS:[ESP+0x48]
 *  0050862B   C74424 60 0F0000>MOV DWORD PTR SS:[ESP+0x60],0xF
 *  00508633   895C24 5C        MOV DWORD PTR SS:[ESP+0x5C],EBX
 *  00508637   885C24 4C        MOV BYTE PTR SS:[ESP+0x4C],BL
 *  0050863B   E8 20A1EFFF      CALL .00402760
 *  00508640   6A FF            PUSH -0x1
 *  00508642   53               PUSH EBX
 *  00508643   8D5424 48        LEA EDX,DWORD PTR SS:[ESP+0x48]
 *  00508647   52               PUSH EDX
 *  00508648   8D4C24 7C        LEA ECX,DWORD PTR SS:[ESP+0x7C]
 *  0050864C   C68424 A4050000 >MOV BYTE PTR SS:[ESP+0x5A4],0x2
 *  00508654   E8 8759F2FF      CALL .0042DFE0
 *  00508659   837C24 58 10     CMP DWORD PTR SS:[ESP+0x58],0x10
 *  0050865E   889C24 98050000  MOV BYTE PTR SS:[ESP+0x598],BL
 *  00508665   72 0D            JB SHORT .00508674
 *  00508667   8B4424 44        MOV EAX,DWORD PTR SS:[ESP+0x44]
 *  0050866B   50               PUSH EAX
 *  0050866C   E8 01610A00      CALL .005AE772
 *  00508671   83C4 04          ADD ESP,0x4
 *  00508674   83ED 01          SUB EBP,0x1
 *  00508677  ^75 A7            JNZ SHORT .00508620
 *  00508679   8B4C24 30        MOV ECX,DWORD PTR SS:[ESP+0x30]
 *  0050867D   3BCF             CMP ECX,EDI
 *  0050867F   7D 5B            JGE SHORT .005086DC
 *  00508681   2BF9             SUB EDI,ECX
 *  00508683   6A 01            PUSH 0x1
 *  00508685   68 10AC6600      PUSH .0066AC10
 *  0050868A   8D4C24 48        LEA ECX,DWORD PTR SS:[ESP+0x48]
 *  0050868E   C74424 60 0F0000>MOV DWORD PTR SS:[ESP+0x60],0xF
 *  00508696   895C24 5C        MOV DWORD PTR SS:[ESP+0x5C],EBX
 *  0050869A   885C24 4C        MOV BYTE PTR SS:[ESP+0x4C],BL
 *  0050869E   E8 BDA0EFFF      CALL .00402760
 *  005086A3   6A FF            PUSH -0x1
 *  005086A5   53               PUSH EBX
 *  005086A6   8D4C24 48        LEA ECX,DWORD PTR SS:[ESP+0x48]
 *  005086AA   51               PUSH ECX
 *  005086AB   8D4C24 7C        LEA ECX,DWORD PTR SS:[ESP+0x7C]
 *  005086AF   C68424 A4050000 >MOV BYTE PTR SS:[ESP+0x5A4],0x3
 *  005086B7   E8 2459F2FF      CALL .0042DFE0
 *  005086BC   837C24 58 10     CMP DWORD PTR SS:[ESP+0x58],0x10
 *  005086C1   889C24 98050000  MOV BYTE PTR SS:[ESP+0x598],BL
 *  005086C8   72 0D            JB SHORT .005086D7
 *  005086CA   8B5424 44        MOV EDX,DWORD PTR SS:[ESP+0x44]
 *  005086CE   52               PUSH EDX
 *  005086CF   E8 9E600A00      CALL .005AE772
 *  005086D4   83C4 04          ADD ESP,0x4
 *  005086D7   83EF 01          SUB EDI,0x1
 *  005086DA  ^75 A7            JNZ SHORT .00508683
 *  005086DC   8BAC24 84000000  MOV EBP,DWORD PTR SS:[ESP+0x84]
 *  005086E3   3B2E             CMP EBP,DWORD PTR DS:[ESI]
 *  005086E5   8B4424 14        MOV EAX,DWORD PTR SS:[ESP+0x14]
 *  005086E9   894424 30        MOV DWORD PTR SS:[ESP+0x30],EAX
 *  005086ED   0F8D D8000000    JGE .005087CB
 *  005086F3   8B4C24 1C        MOV ECX,DWORD PTR SS:[ESP+0x1C]
 *  005086F7   8B5424 14        MOV EDX,DWORD PTR SS:[ESP+0x14]
 *  005086FB   8D3C11           LEA EDI,DWORD PTR DS:[ECX+EDX]
 *  005086FE   8D8424 8C040000  LEA EAX,DWORD PTR SS:[ESP+0x48C]
 *  00508705   50               PUSH EAX
 *  00508706   8D8C24 90000000  LEA ECX,DWORD PTR SS:[ESP+0x90]
 *  0050870D   51               PUSH ECX
 *  0050870E   57               PUSH EDI
 *  0050870F   8BCE             MOV ECX,ESI
 *  00508711   E8 6AEBFFFF      CALL .00507280
 *  00508716   3BC3             CMP EAX,EBX
 *  00508718   7E 34            JLE SHORT .0050874E
 *  0050871A   8D8C24 8C000000  LEA ECX,DWORD PTR SS:[ESP+0x8C]
 *  00508721   8D79 01          LEA EDI,DWORD PTR DS:[ECX+0x1]
 *  00508724   8A11             MOV DL,BYTE PTR DS:[ECX]
 *  00508726   41               INC ECX
 *  00508727   3AD3             CMP DL,BL
 *  00508729  ^75 F9            JNZ SHORT .00508724
 *  0050872B   8B5424 20        MOV EDX,DWORD PTR SS:[ESP+0x20]
 *  0050872F   2BCF             SUB ECX,EDI
 *  00508731   8B7E 04          MOV EDI,DWORD PTR DS:[ESI+0x4]
 *  00508734   03D1             ADD EDX,ECX
 *  00508736   8B0E             MOV ECX,DWORD PTR DS:[ESI]
 *  00508738   895424 20        MOV DWORD PTR SS:[ESP+0x20],EDX
 *  0050873C   03F9             ADD EDI,ECX
 *  0050873E   03D5             ADD EDX,EBP
 *  00508740   3BD7             CMP EDX,EDI
 *  00508742   0F8F 83000000    JG .005087CB
 *  00508748   014424 14        ADD DWORD PTR SS:[ESP+0x14],EAX
 *  0050874C   EB 54            JMP SHORT .005087A2
 *  0050874E   8D4424 28        LEA EAX,DWORD PTR SS:[ESP+0x28]
 *  00508752   50               PUSH EAX
 *  00508753   8D4C24 1C        LEA ECX,DWORD PTR SS:[ESP+0x1C]
 *  00508757   51               PUSH ECX
 *  00508758   57               PUSH EDI
 *  00508759   8BCE             MOV ECX,ESI
 *  0050875B   E8 30EAFFFF      CALL .00507190
 *  00508760   85C0             TEST EAX,EAX
 *  00508762   74 67            JE SHORT .005087CB
 *  00508764   8B15 A4118200    MOV EDX,DWORD PTR DS:[0x8211A4]
 *  0050876A   399A 94690000    CMP DWORD PTR DS:[EDX+0x6994],EBX
 *  00508770   74 0C            JE SHORT .0050877E  ; jichi: pattern found here
 *  00508772   B8 6E5C0000      MOV EAX,0x5C6E
 *  00508777   66:394424 18     CMP WORD PTR SS:[ESP+0x18],AX
 *  0050877C   74 35            JE SHORT .005087B3
 *  0050877E   8B5424 20        MOV EDX,DWORD PTR SS:[ESP+0x20]
 *  00508782   8B4424 28        MOV EAX,DWORD PTR SS:[ESP+0x28]
 *  00508786   8B0E             MOV ECX,DWORD PTR DS:[ESI]
 *  00508788   03D5             ADD EDX,EBP
 *  0050878A   03D0             ADD EDX,EAX
 *  0050878C   3BD1             CMP EDX,ECX
 *  0050878E   7D 3B            JGE SHORT .005087CB
 *  00508790   8B5424 14        MOV EDX,DWORD PTR SS:[ESP+0x14]
 *  00508794   895424 24        MOV DWORD PTR SS:[ESP+0x24],EDX
 *  00508798   03D0             ADD EDX,EAX
 *  0050879A   014424 20        ADD DWORD PTR SS:[ESP+0x20],EAX
 *  0050879E   895424 14        MOV DWORD PTR SS:[ESP+0x14],EDX
 *  005087A2   8B4424 20        MOV EAX,DWORD PTR SS:[ESP+0x20]
 *  005087A6   8D1428           LEA EDX,DWORD PTR DS:[EAX+EBP]
 *  005087A9   3BD1             CMP EDX,ECX
 *  005087AB  ^0F8C 42FFFFFF    JL .005086F3
 *  005087B1   EB 18            JMP SHORT .005087CB
 *  005087B3   8B4424 14        MOV EAX,DWORD PTR SS:[ESP+0x14]
 *  005087B7   894424 24        MOV DWORD PTR SS:[ESP+0x24],EAX
 *  005087BB   034424 28        ADD EAX,DWORD PTR SS:[ESP+0x28]
 *  005087BF   C74424 38 010000>MOV DWORD PTR SS:[ESP+0x38],0x1
 *  005087C7   894424 14        MOV DWORD PTR SS:[ESP+0x14],EAX
 *  005087CB   8B3E             MOV EDI,DWORD PTR DS:[ESI]
 *  005087CD   2BFD             SUB EDI,EBP
 *  005087CF   2B7C24 14        SUB EDI,DWORD PTR SS:[ESP+0x14]
 *  005087D3   8B6C24 1C        MOV EBP,DWORD PTR SS:[ESP+0x1C]
 *  005087D7   037E 04          ADD EDI,DWORD PTR DS:[ESI+0x4]
 *  005087DA   8D4424 24        LEA EAX,DWORD PTR SS:[ESP+0x24]
 *  005087DE   57               PUSH EDI
 *  005087DF   50               PUSH EAX
 *  005087E0   8D4C24 38        LEA ECX,DWORD PTR SS:[ESP+0x38]
 *  005087E4   51               PUSH ECX
 *  005087E5   55               PUSH EBP
 *  005087E6   8BCE             MOV ECX,ESI
 *  005087E8   E8 13F3FFFF      CALL .00507B00
 *  005087ED   57               PUSH EDI
 *  005087EE   8D5424 28        LEA EDX,DWORD PTR SS:[ESP+0x28]
 *  005087F2   52               PUSH EDX
 *  005087F3   8D4424 38        LEA EAX,DWORD PTR SS:[ESP+0x38]
 *  005087F7   50               PUSH EAX
 *  005087F8   55               PUSH EBP
 *  005087F9   8BCE             MOV ECX,ESI
 *  005087FB   E8 A0F3FFFF      CALL .00507BA0
 *  00508800   85C0             TEST EAX,EAX
 *  00508802   74 13            JE SHORT .00508817
 *  00508804   57               PUSH EDI
 *  00508805   8D4C24 28        LEA ECX,DWORD PTR SS:[ESP+0x28]
 *  00508809   51               PUSH ECX
 *  0050880A   8D5424 38        LEA EDX,DWORD PTR SS:[ESP+0x38]
 *  0050880E   52               PUSH EDX
 *  0050880F   55               PUSH EBP
 *  00508810   8BCE             MOV ECX,ESI
 *  00508812   E8 09F5FFFF      CALL .00507D20
 *  00508817   8B7C24 14        MOV EDI,DWORD PTR SS:[ESP+0x14]
 *  0050881B   8B6C24 30        MOV EBP,DWORD PTR SS:[ESP+0x30]
 *  0050881F   8B4C24 1C        MOV ECX,DWORD PTR SS:[ESP+0x1C]
 *  00508823   8BC7             MOV EAX,EDI
 *  00508825   2BC5             SUB EAX,EBP
 *  00508827   50               PUSH EAX
 *  00508828   03CD             ADD ECX,EBP
 *  0050882A   51               PUSH ECX
 *  0050882B   8D9424 94000000  LEA EDX,DWORD PTR SS:[ESP+0x94]
 *  00508832   52               PUSH EDX
 *  00508833   E8 A8430000      CALL .0050CBE0
 *  00508838   8B4424 44        MOV EAX,DWORD PTR SS:[ESP+0x44]
 *  0050883C   83C4 0C          ADD ESP,0xC
 *  0050883F   F7D8             NEG EAX
 *  00508841   1BC0             SBB EAX,EAX
 *  00508843   83E0 02          AND EAX,0x2
 *  00508846   2BF8             SUB EDI,EAX
 *  00508848   2BFD             SUB EDI,EBP
 *  0050884A   8D8424 8C000000  LEA EAX,DWORD PTR SS:[ESP+0x8C]
 *  00508851   889C3C 8C000000  MOV BYTE PTR SS:[ESP+EDI+0x8C],BL
 *  00508858   C74424 58 0F0000>MOV DWORD PTR SS:[ESP+0x58],0xF
 *  00508860   895C24 54        MOV DWORD PTR SS:[ESP+0x54],EBX
 *  00508864   885C24 44        MOV BYTE PTR SS:[ESP+0x44],BL
 *  00508868   8D78 01          LEA EDI,DWORD PTR DS:[EAX+0x1]
 *  0050886B   EB 03            JMP SHORT .00508870
 *  0050886D   8D49 00          LEA ECX,DWORD PTR DS:[ECX]
 *  00508870   8A08             MOV CL,BYTE PTR DS:[EAX]
 *  00508872   40               INC EAX
 *  00508873   3ACB             CMP CL,BL
 *  00508875  ^75 F9            JNZ SHORT .00508870
 *  00508877   2BC7             SUB EAX,EDI
 *  00508879   50               PUSH EAX
 *  0050887A   8D8424 90000000  LEA EAX,DWORD PTR SS:[ESP+0x90]
 *  00508881   50               PUSH EAX
 *  00508882   8D4C24 48        LEA ECX,DWORD PTR SS:[ESP+0x48]
 *  00508886   E8 D59EEFFF      CALL .00402760
 *  0050888B   6A FF            PUSH -0x1
 *  0050888D   53               PUSH EBX
 *  0050888E   8D4C24 48        LEA ECX,DWORD PTR SS:[ESP+0x48]
 *  00508892   51               PUSH ECX
 *  00508893   8D4C24 7C        LEA ECX,DWORD PTR SS:[ESP+0x7C]
 *  00508897   C68424 A4050000 >MOV BYTE PTR SS:[ESP+0x5A4],0x4
 *  0050889F   E8 3C57F2FF      CALL .0042DFE0
 *  005088A4   837C24 58 10     CMP DWORD PTR SS:[ESP+0x58],0x10
 *  005088A9   889C24 98050000  MOV BYTE PTR SS:[ESP+0x598],BL
 *  005088B0   72 0D            JB SHORT .005088BF
 *  005088B2   8B5424 44        MOV EDX,DWORD PTR SS:[ESP+0x44]
 *  005088B6   52               PUSH EDX
 *  005088B7   E8 B65E0A00      CALL .005AE772
 *  005088BC   83C4 04          ADD ESP,0x4
 *  005088BF   8B7E 14          MOV EDI,DWORD PTR DS:[ESI+0x14]
 *  005088C2   8B47 1C          MOV EAX,DWORD PTR DS:[EDI+0x1C]
 *  005088C5   40               INC EAX
 *  005088C6   3947 14          CMP DWORD PTR DS:[EDI+0x14],EAX
 *  005088C9   77 09            JA SHORT .005088D4
 *  005088CB   6A 01            PUSH 0x1
 *  005088CD   8BCF             MOV ECX,EDI
 *  005088CF   E8 2C1F0000      CALL .0050A800
 *  005088D4   8B6F 18          MOV EBP,DWORD PTR DS:[EDI+0x18]
 *  005088D7   036F 1C          ADD EBP,DWORD PTR DS:[EDI+0x1C]
 *  005088DA   8B47 14          MOV EAX,DWORD PTR DS:[EDI+0x14]
 *  005088DD   3BC5             CMP EAX,EBP
 *  005088DF   77 02            JA SHORT .005088E3
 *  005088E1   2BE8             SUB EBP,EAX
 *  005088E3   8B4F 10          MOV ECX,DWORD PTR DS:[EDI+0x10]
 *  005088E6   391CA9           CMP DWORD PTR DS:[ECX+EBP*4],EBX
 *  005088E9   75 10            JNZ SHORT .005088FB
 *  005088EB   6A 20            PUSH 0x20
 *  005088ED   E8 A65E0A00      CALL .005AE798
 *  005088F2   8B57 10          MOV EDX,DWORD PTR DS:[EDI+0x10]
 *  005088F5   83C4 04          ADD ESP,0x4
 *  005088F8   8904AA           MOV DWORD PTR DS:[EDX+EBP*4],EAX
 *  005088FB   8B47 10          MOV EAX,DWORD PTR DS:[EDI+0x10]
 *  005088FE   8B2CA8           MOV EBP,DWORD PTR DS:[EAX+EBP*4]
 *  00508901   896C24 38        MOV DWORD PTR SS:[ESP+0x38],EBP
 *  00508905   896C24 30        MOV DWORD PTR SS:[ESP+0x30],EBP
 *  00508909   C68424 98050000 >MOV BYTE PTR SS:[ESP+0x598],0x5
 *  00508911   3BEB             CMP EBP,EBX
 *  00508913   74 24            JE SHORT .00508939
 *  00508915   8B4C24 6C        MOV ECX,DWORD PTR SS:[ESP+0x6C]
 *  00508919   894D 00          MOV DWORD PTR SS:[EBP],ECX
 *  0050891C   6A FF            PUSH -0x1
 *  0050891E   8D4D 04          LEA ECX,DWORD PTR SS:[EBP+0x4]
 *  00508921   53               PUSH EBX
 *  00508922   8D5424 78        LEA EDX,DWORD PTR SS:[ESP+0x78]
 *  00508926   C741 18 0F000000 MOV DWORD PTR DS:[ECX+0x18],0xF
 *  0050892D   8959 14          MOV DWORD PTR DS:[ECX+0x14],EBX
 *  00508930   52               PUSH EDX
 *  00508931   8859 04          MOV BYTE PTR DS:[ECX+0x4],BL
 *  00508934   E8 379CEFFF      CALL .00402570
 *  00508939   B8 01000000      MOV EAX,0x1
 *  0050893E   0147 1C          ADD DWORD PTR DS:[EDI+0x1C],EAX
 *  00508941   889C24 98050000  MOV BYTE PTR SS:[ESP+0x598],BL
 *  00508948   395C24 64        CMP DWORD PTR SS:[ESP+0x64],EBX
 *  0050894C   75 12            JNZ SHORT .00508960
 *  0050894E   8B4E 14          MOV ECX,DWORD PTR DS:[ESI+0x14]
 *  00508951   8B51 1C          MOV EDX,DWORD PTR DS:[ECX+0x1C]
 *  00508954   8B4C24 68        MOV ECX,DWORD PTR SS:[ESP+0x68]
 *  00508958   2BD0             SUB EDX,EAX
 *  0050895A   8911             MOV DWORD PTR DS:[ECX],EDX
 *  0050895C   894424 64        MOV DWORD PTR SS:[ESP+0x64],EAX
 *  00508960   8B56 14          MOV EDX,DWORD PTR DS:[ESI+0x14]
 *  00508963   8B4A 1C          MOV ECX,DWORD PTR DS:[EDX+0x1C]
 *  00508966   8B5424 5C        MOV EDX,DWORD PTR SS:[ESP+0x5C]
 *  0050896A   014424 2C        ADD DWORD PTR SS:[ESP+0x2C],EAX
 *  0050896E   2BC8             SUB ECX,EAX
 *  00508970   890A             MOV DWORD PTR DS:[EDX],ECX
 *  00508972   8D4C24 70        LEA ECX,DWORD PTR SS:[ESP+0x70]
 *  00508976   E8 A55BF2FF      CALL .0042E520
 *  0050897B   8BBE DC000000    MOV EDI,DWORD PTR DS:[ESI+0xDC]
 *  00508981   8B4424 1C        MOV EAX,DWORD PTR SS:[ESP+0x1C]
 *  00508985   8B4C24 14        MOV ECX,DWORD PTR SS:[ESP+0x14]
 *  00508989   037C24 60        ADD EDI,DWORD PTR SS:[ESP+0x60]
 *  0050898D   381C08           CMP BYTE PTR DS:[EAX+ECX],BL
 *  00508990  ^0F85 62FCFFFF    JNZ .005085F8
 *  00508996   8B96 F4000000    MOV EDX,DWORD PTR DS:[ESI+0xF4]
 *  0050899C   8B4424 68        MOV EAX,DWORD PTR SS:[ESP+0x68]
 *  005089A0   0110             ADD DWORD PTR DS:[EAX],EDX
 *  005089A2   8B8E F4000000    MOV ECX,DWORD PTR DS:[ESI+0xF4]
 *  005089A8   8B4424 5C        MOV EAX,DWORD PTR SS:[ESP+0x5C]
 *  005089AC   0108             ADD DWORD PTR DS:[EAX],ECX
 *  005089AE   83BC24 88000000 >CMP DWORD PTR SS:[ESP+0x88],0x10
 *  005089B6   72 0D            JB SHORT .005089C5
 *  005089B8   8B5424 74        MOV EDX,DWORD PTR SS:[ESP+0x74]
 *  005089BC   52               PUSH EDX
 *  005089BD   E8 B05D0A00      CALL .005AE772
 *  005089C2   83C4 04          ADD ESP,0x4
 *  005089C5   8B4424 2C        MOV EAX,DWORD PTR SS:[ESP+0x2C]
 *  005089C9   8B8C24 90050000  MOV ECX,DWORD PTR SS:[ESP+0x590]
 *  005089D0   64:890D 00000000 MOV DWORD PTR FS:[0],ECX
 *  005089D7   59               POP ECX
 *  005089D8   5F               POP EDI
 *  005089D9   5E               POP ESI
 *  005089DA   5D               POP EBP
 *  005089DB   5B               POP EBX
 *  005089DC   8B8C24 78050000  MOV ECX,DWORD PTR SS:[ESP+0x578]
 *  005089E3   33CC             XOR ECX,ESP
 *  005089E5   E8 FC5C0A00      CALL .005AE6E6
 *  005089EA   81C4 88050000    ADD ESP,0x588
 *  005089F0   C2 1000          RETN 0x10
 *  005089F3   CC               INT3
 *  005089F4   CC               INT3
 *  005089F5   CC               INT3
 *  005089F6   CC               INT3
 *  005089F7   CC               INT3
 *  005089F8   CC               INT3
 */
bool attach(ulong startAddress, ulong stopAddress)
{
  const uint8_t bytes[] = {
    0x74, 0x0c,                 // 00508770   74 0c            je short .0050877e  ; jichi: pattern found here
    0xb8, 0x6e,0x5c,0x00,0x00   // 00508772   b8 6e5c0000      mov eax,0x5c6e
  };
  ulong addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  return winhook::hook_before(addr, Private::hookBefore);
}


} // namespace HistoryHook
} // unnamed namespace

namespace HistoryHook {
namespace Private {
  bool hookBefore(winhook::hook_stack *s)
  {
    static QByteArray data_;
    auto text = (LPCSTR)s->stack[1]; // arg1
    if (!text || !*text)
      return true;
    enum { role = Engine::ScenarioRole };
    auto split = s->stack[0]; // retaddr
    auto sig = Engine::hashThreadSignature(role, split);
    data_ = EngineController::instance()->dispatchTextA(text, role, sig);
    s->stack[1] = (ulong)data_.constData();
    //::strcpy(text, data.constData());
    return true;
  }
} // namespace Private

/**
 *  Sample game: カミカゼ
 *
 *  FIXME: This is the log function
 *
 *  Function found by debugging GetGlyphOutlineA, then traversing function stack
 *  005B516E   CC               INT3
 *  005B516F   CC               INT3
 *  005B5170   51               PUSH ECX ; jichi: text in arg1
 *  005B5171   8B43 1C          MOV EAX,DWORD PTR DS:[EBX+0x1C]
 *  005B5174   55               PUSH EBP
 *  005B5175   56               PUSH ESI
 *  005B5176   57               PUSH EDI
 *  005B5177   33FF             XOR EDI,EDI
 *  005B5179   8978 14          MOV DWORD PTR DS:[EAX+0x14],EDI
 *  005B517C   8978 08          MOV DWORD PTR DS:[EAX+0x8],EDI
 *  005B517F   8B73 1C          MOV ESI,DWORD PTR DS:[EBX+0x1C]
 *  005B5182   8D47 02          LEA EAX,DWORD PTR DS:[EDI+0x2]
 *  005B5185   E8 66ABEFFF      CALL .004AFCF0
 *  005B518A   FF46 14          INC DWORD PTR DS:[ESI+0x14]
 *  005B518D   8346 08 02       ADD DWORD PTR DS:[ESI+0x8],0x2
 *  005B5191   8B36             MOV ESI,DWORD PTR DS:[ESI]
 *  005B5193   C606 00          MOV BYTE PTR DS:[ESI],0x0
 *  005B5196   C646 01 00       MOV BYTE PTR DS:[ESI+0x1],0x0
 *  005B519A   8B43 1C          MOV EAX,DWORD PTR DS:[EBX+0x1C]
 *  005B519D   8B48 14          MOV ECX,DWORD PTR DS:[EAX+0x14]
 *  005B51A0   3BCF             CMP ECX,EDI
 *  005B51A2   7E 04            JLE SHORT .005B51A8
 *  005B51A4   49               DEC ECX
 *  005B51A5   8948 14          MOV DWORD PTR DS:[EAX+0x14],ECX
 *  005B51A8   8B4424 14        MOV EAX,DWORD PTR SS:[ESP+0x14]
 *  005B51AC   33ED             XOR EBP,EBP
 *  005B51AE   8038 00          CMP BYTE PTR DS:[EAX],0x0
 *  005B51B1   0F84 D0000000    JE .005B5287
 *  005B51B7   8B4C24 14        MOV ECX,DWORD PTR SS:[ESP+0x14]
 *  005B51BB   8D3429           LEA ESI,DWORD PTR DS:[ECX+EBP]
 *  005B51BE   8BCE             MOV ECX,ESI
 *  005B51C0   8BD3             MOV EDX,EBX
 *  005B51C2   E8 99FBFFFF      CALL .005B4D60
 *  005B51C7   85C0             TEST EAX,EAX
 *  005B51C9   7E 07            JLE SHORT .005B51D2
 *  005B51CB   03E8             ADD EBP,EAX
 *  005B51CD   E9 A7000000      JMP .005B5279
 *  005B51D2   7D 31            JGE SHORT .005B5205
 *  005B51D4   8B73 1C          MOV ESI,DWORD PTR DS:[EBX+0x1C]
 *  005B51D7   F7D8             NEG EAX
 *  005B51D9   894424 0C        MOV DWORD PTR SS:[ESP+0xC],EAX
 *  005B51DD   E8 0EABEFFF      CALL .004AFCF0
 *  005B51E2   8B4424 0C        MOV EAX,DWORD PTR SS:[ESP+0xC]
 *  005B51E6   FF46 14          INC DWORD PTR DS:[ESI+0x14]
 *  005B51E9   0146 08          ADD DWORD PTR DS:[ESI+0x8],EAX
 *  005B51EC   8B36             MOV ESI,DWORD PTR DS:[ESI]
 *  005B51EE   85C0             TEST EAX,EAX
 *  005B51F0   7E 75            JLE SHORT .005B5267
 *  005B51F2   8B5424 14        MOV EDX,DWORD PTR SS:[ESP+0x14]
 *  005B51F6   8A0C2A           MOV CL,BYTE PTR DS:[EDX+EBP]
 *  005B51F9   880C37           MOV BYTE PTR DS:[EDI+ESI],CL
 *  005B51FC   47               INC EDI
 *  005B51FD   45               INC EBP
 *  005B51FE   83E8 01          SUB EAX,0x1
 *  005B5201  ^75 EF            JNZ SHORT .005B51F2
 *  005B5203   EB 62            JMP SHORT .005B5267
 *  005B5205   8BCE             MOV ECX,ESI
 *  005B5207   E8 34C4EFFF      CALL .004B1640
 *  005B520C   8B73 1C          MOV ESI,DWORD PTR DS:[EBX+0x1C]
 *  005B520F   85C0             TEST EAX,EAX
 *  005B5211   74 2D            JE SHORT .005B5240
 *  005B5213   B8 02000000      MOV EAX,0x2
 *  005B5218   E8 D3AAEFFF      CALL .004AFCF0
 *  005B521D   FF46 14          INC DWORD PTR DS:[ESI+0x14]
 *  005B5220   8346 08 02       ADD DWORD PTR DS:[ESI+0x8],0x2
 *  005B5224   8B5424 14        MOV EDX,DWORD PTR SS:[ESP+0x14]
 *  005B5228   8B36             MOV ESI,DWORD PTR DS:[ESI]
 *  005B522A   8D042A           LEA EAX,DWORD PTR DS:[EDX+EBP]
 *  005B522D   8A00             MOV AL,BYTE PTR DS:[EAX]
 *  005B522F   880437           MOV BYTE PTR DS:[EDI+ESI],AL
 *  005B5232   45               INC EBP
 *  005B5233   47               INC EDI
 *  005B5234   8BCA             MOV ECX,EDX
 *  005B5236   8A1429           MOV DL,BYTE PTR DS:[ECX+EBP]
 *  005B5239   881437           MOV BYTE PTR DS:[EDI+ESI],DL
 *  005B523C   47               INC EDI
 *  005B523D   45               INC EBP
 *  005B523E   EB 27            JMP SHORT .005B5267
 *  005B5240   B8 01000000      MOV EAX,0x1
 *  005B5245   E8 A6AAEFFF      CALL .004AFCF0
 *  005B524A   8B4424 14        MOV EAX,DWORD PTR SS:[ESP+0x14]
 *  005B524E   B9 01000000      MOV ECX,0x1
 *  005B5253   014E 14          ADD DWORD PTR DS:[ESI+0x14],ECX
 *  005B5256   014E 08          ADD DWORD PTR DS:[ESI+0x8],ECX
 *  005B5259   8B36             MOV ESI,DWORD PTR DS:[ESI]
 *  005B525B   8A1428           MOV DL,BYTE PTR DS:[EAX+EBP]
 *  005B525E   03C5             ADD EAX,EBP
 *  005B5260   881437           MOV BYTE PTR DS:[EDI+ESI],DL
 *  005B5263   03F9             ADD EDI,ECX
 *  005B5265   03E9             ADD EBP,ECX
 *  005B5267   C60437 00        MOV BYTE PTR DS:[EDI+ESI],0x0
 *  005B526B   8B43 1C          MOV EAX,DWORD PTR DS:[EBX+0x1C]
 *  005B526E   8B48 14          MOV ECX,DWORD PTR DS:[EAX+0x14]
 *  005B5271   85C9             TEST ECX,ECX
 *  005B5273   7E 04            JLE SHORT .005B5279
 *  005B5275   49               DEC ECX
 *  005B5276   8948 14          MOV DWORD PTR DS:[EAX+0x14],ECX
 *  005B5279   8B4424 14        MOV EAX,DWORD PTR SS:[ESP+0x14]
 *  005B527D   803C28 00        CMP BYTE PTR DS:[EAX+EBP],0x0
 *  005B5281  ^0F85 30FFFFFF    JNZ .005B51B7
 *  005B5287   5F               POP EDI
 *  005B5288   5E               POP ESI
 *  005B5289   B8 01000000      MOV EAX,0x1
 *  005B528E   5D               POP EBP
 *  005B528F   59               POP ECX
 *  005B5290   C2 0400          RETN 0x4
 *  005B5293   CC               INT3
 *  005B5294   CC               INT3
 *  005B5295   CC               INT3
 *  005B5296   CC               INT3
 */
bool attach()
{
  ulong startAddress, stopAddress;
  if (!Engine::getProcessMemoryRange(&startAddress, &stopAddress))
    return false;

  const uint8_t bytes[] = {
    0xff,0x46, 0x14,        // 005b521d   ff46 14          inc dword ptr ds:[esi+0x14]
    0x83,0x46, 0x08, 0x02,  // 005b5220   8346 08 02       add dword ptr ds:[esi+0x8],0x2
    0x8b,0x54,0x24, 0x14,   // 005b5224   8b5424 14        mov edx,dword ptr ss:[esp+0x14]
    0x8b,0x36,              // 005b5228   8b36             mov esi,dword ptr ds:[esi]
    0x8d,0x04,0x2a,         // 005b522a   8d042a           lea eax,dword ptr ds:[edx+ebp]
    0x8a,0x00,              // 005b522d   8a00             mov al,byte ptr ds:[eax]
    0x88,0x04,0x37          // 005b522f   880437           mov byte ptr ds:[edi+esi],al
  };

  ulong addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  return winhook::hook_before(addr, Private::hookBefore);
}

} // namespace HistoryHook
#endif // 0
