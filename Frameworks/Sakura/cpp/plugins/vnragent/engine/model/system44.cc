// system44.cc
// 8/16/2015 jichi
#include "engine/model/system4.h"
#include "engine/enginecontroller.h"
#include "engine/enginedef.h"
#include "engine/enginehash.h"
#include "engine/enginesettings.h"
#include "engine/engineutil.h"
//#include "hijack/hijackmanager.h"
//#include "util/textutil.h"
#include "memdbg/memsearch.h"
#include "winhook/hookcode.h"
#include <qt_windows.h>
#include <cstdint>
#include <unordered_set>

#define DEBUG "model/system44"
#include "sakurakit/skdebug.h"

/** Private data */

namespace { // unnamed

struct TextArgument // first argument of the scenario hook
{
  ulong *unknown[2];
  LPCSTR text;
  int size; // text data size including '\0', length = size - 1
  int capacity;
  ulong split;

  bool isValid() const
  {
    return size <= capacity && size >= 4 && text && ::strlen(text) + 1 == size // skip translating single text
        //&& !Util::allAscii(text)
        && (uchar)text[0] > 127 && (uchar)text[size - 3] > 127 // skip text beginning / ending with ascii
        && !::strstr(text, "\x81\x5e"); // "／"
  }
};

namespace ScenarioHook {

namespace Private {
  bool isOtherText(LPCSTR text)
  {
    static const char *s[] = {
      "\x82\xa2\x82\xa2\x82\xa6" /* いいえ */
      , "\x82\xcd\x82\xa2" /* はい */
    };
    for (int i = 0; i < sizeof(s)/sizeof(*s); i++)
      if (::strcmp(text, s[i]) == 0)
        return true;
    return false;
  }

  TextArgument *arg_,
               argValue_;
  /**
   *  Sample game: Rance03
   *
   *  Caller that related to load/save, which is the only caller get kept:
   *  005C68A7   8B86 74010000    MOV EAX,DWORD PTR DS:[ESI+0x174]
   *  005C68AD   8B1CA8           MOV EBX,DWORD PTR DS:[EAX+EBP*4]
   *  005C68B0   85DB             TEST EBX,EBX
   *  005C68B2   74 63            JE SHORT Rance03T.005C6917
   *  005C68B4   8B86 78010000    MOV EAX,DWORD PTR DS:[ESI+0x178]
   *  005C68BA   2B86 74010000    SUB EAX,DWORD PTR DS:[ESI+0x174]
   *  005C68C0   C1F8 02          SAR EAX,0x2
   *  005C68C3   3BD0             CMP EDX,EAX
   *  005C68C5   73 3C            JNB SHORT Rance03T.005C6903
   *  005C68C7   8B86 74010000    MOV EAX,DWORD PTR DS:[ESI+0x174]
   *  005C68CD   8B0C90           MOV ECX,DWORD PTR DS:[EAX+EDX*4]
   *  005C68D0   85C9             TEST ECX,ECX
   *  005C68D2   74 2F            JE SHORT Rance03T.005C6903
   *  005C68D4   53               PUSH EBX
   *  005C68D5  -E9 26976B09      JMP 09C80000  ; jichi: called
   *  005C68DA   84C0             TEST AL,AL
   *  005C68DC   75 18            JNZ SHORT Rance03T.005C68F6
   *  005C68DE   68 94726E00      PUSH Rance03T.006E7294
   *  005C68E3   68 00736E00      PUSH Rance03T.006E7300                   ; ASCII "S_ASSIGN"
   *  005C68E8   56               PUSH ESI
   *  005C68E9   E8 12BBFFFF      CALL Rance03T.005C2400
   *  005C68EE   83C4 0C          ADD ESP,0xC
   *  005C68F1   5F               POP EDI
   *  005C68F2   5E               POP ESI
   *
   *  Caller of the scenario thread:
   *
   *  005D6F80  ^74 BE            JE SHORT Rance03T.005D6F40
   *  005D6F82   85C0             TEST EAX,EAX
   *  005D6F84  ^74 BA            JE SHORT Rance03T.005D6F40
   *  005D6F86   50               PUSH EAX
   *  005D6F87   8BCF             MOV ECX,EDI
   *  005D6F89  -E9 72907009      JMP 09CE0000  ; jichi: called here
   *  005D6F8E  ^EB A8            JMP SHORT Rance03T.005D6F38
   *  005D6F90   8B46 0C          MOV EAX,DWORD PTR DS:[ESI+0xC]
   *  005D6F93   2B46 08          SUB EAX,DWORD PTR DS:[ESI+0x8]
   *  005D6F96   C1F8 02          SAR EAX,0x2
   *  005D6F99   3BD8             CMP EBX,EAX
   *  005D6F9B  ^73 A3            JNB SHORT Rance03T.005D6F40
   *  005D6F9D   8B46 08          MOV EAX,DWORD PTR DS:[ESI+0x8]
   *  005D6FA0   8B1C98           MOV EBX,DWORD PTR DS:[EAX+EBX*4]
   */
  bool hookBefore(winhook::hook_stack *s)
  {
    static QByteArray data_; // persistent storage, which makes this function not thread-safe
    static std::unordered_set<uint64_t> hashes_;
    //auto split = s->stack[5]; // parent function return address
    //auto split = s->stack[10]; // parent's parent function return address
    //auto split = *(DWORD *)(s->ecx + 0x10);
    auto split = *(DWORD *)(s->ecx + 0x34);
    //auto split = *(DWORD *)(s->ecx + 0x48);
    // 005C68DA   84C0             TEST AL,AL
    //if (*(WORD *)retaddr == 0xc084) // otherwise system text will be translated
    //  return true;
    //if (*(WORD *)retaddr != 0xc084) // only translate one caller
    //  return true;
    // 005D6F8E  ^EB A8            JMP SHORT Rance03T.005D6F38
    //if (*(WORD *)retaddr != 0xa8eb) // this function has 7 callers, and only one is kept
    //  return true;
    if (split > 0xff || split && split < 0xf)
      return true;
    auto arg = (TextArgument *)s->stack[0]; // arg1
    if (!arg || !arg->isValid()
        || hashes_.find(Engine::hashCharArray(arg->text)) != hashes_.end())
      return true;
    if (arg->size < 0xf && split > 0 && !isOtherText(arg->text))
      return true;
    //auto sig = Engine::hashThreadSignature(role, split);
    //auto role = Engine::OtherRole;
    auto role = Engine::OtherRole;
    if (!isOtherText(arg->text)) {
      if (split == 0 && arg->size <= 0x10)
        role = Engine::NameRole;
      else if (split >= 2 && split <= 0x14 && split != 3 && split != 0xb || split == 0x22)
        role = Engine::ScenarioRole;
    }
    QByteArray oldData = arg->text,
               newData = EngineController::instance()->dispatchTextA(oldData, role, split);
    if (role == Engine::NameRole || oldData == newData) // do not translate name
      return true;
    data_ = newData;

    arg_ = arg;
    argValue_ = *arg;

    arg->text = data_.constData();
    arg->size = data_.size() + 1;
    arg->capacity = arg->size;

    hashes_.insert(Engine::hashCharArray(arg->text));
    return true;
  }
  bool hookAfter(winhook::hook_stack *)
  {
    if (arg_) {
      *arg_ = argValue_;
      arg_ = nullptr;
    }
    return true;
  }
} // namespace Private

/**
 *  Sample game: Rance03
 *
 *  Function that is similar to memcpy, found by debugging where game text get modified:
 *
 *  0069D84F   CC               INT3
 *  0069D850   57               PUSH EDI
 *  0069D851   56               PUSH ESI
 *  0069D852   8B7424 10        MOV ESI,DWORD PTR SS:[ESP+0x10]
 *  0069D856   8B4C24 14        MOV ECX,DWORD PTR SS:[ESP+0x14]
 *  0069D85A   8B7C24 0C        MOV EDI,DWORD PTR SS:[ESP+0xC]
 *  0069D85E   8BC1             MOV EAX,ECX
 *  0069D860   8BD1             MOV EDX,ECX
 *  0069D862   03C6             ADD EAX,ESI
 *  0069D864   3BFE             CMP EDI,ESI
 *  0069D866   76 08            JBE SHORT Rance03T.0069D870
 *  0069D868   3BF8             CMP EDI,EAX
 *  0069D86A   0F82 68030000    JB Rance03T.0069DBD8
 *  0069D870   0FBA25 5CC97500 >BT DWORD PTR DS:[0x75C95C],0x1
 *  0069D878   73 07            JNB SHORT Rance03T.0069D881
 *  0069D87A   F3:A4            REP MOVS BYTE PTR ES:[EDI],BYTE PTR DS:[ESI]
 *  0069D87C   E9 17030000      JMP Rance03T.0069DB98
 *  0069D881   81F9 80000000    CMP ECX,0x80
 *  0069D887   0F82 CE010000    JB Rance03T.0069DA5B
 *  0069D88D   8BC7             MOV EAX,EDI
 *  0069D88F   33C6             XOR EAX,ESI
 *  0069D891   A9 0F000000      TEST EAX,0xF
 *  0069D896   75 0E            JNZ SHORT Rance03T.0069D8A6
 *  0069D898   0FBA25 10A47400 >BT DWORD PTR DS:[0x74A410],0x1
 *  0069D8A0   0F82 DA040000    JB Rance03T.0069DD80
 *  0069D8A6   0FBA25 5CC97500 >BT DWORD PTR DS:[0x75C95C],0x0
 *  0069D8AE   0F83 A7010000    JNB Rance03T.0069DA5B
 *  0069D8B4   F7C7 03000000    TEST EDI,0x3
 *  0069D8BA   0F85 B8010000    JNZ Rance03T.0069DA78
 *  0069D8C0   F7C6 03000000    TEST ESI,0x3
 *  0069D8C6   0F85 97010000    JNZ Rance03T.0069DA63
 *  0069D8CC   0FBAE7 02        BT EDI,0x2
 *  0069D8D0   73 0D            JNB SHORT Rance03T.0069D8DF
 *  0069D8D2   8B06             MOV EAX,DWORD PTR DS:[ESI]
 *  0069D8D4   83E9 04          SUB ECX,0x4
 *  0069D8D7   8D76 04          LEA ESI,DWORD PTR DS:[ESI+0x4]
 *  0069D8DA   8907             MOV DWORD PTR DS:[EDI],EAX
 *  0069D8DC   8D7F 04          LEA EDI,DWORD PTR DS:[EDI+0x4]
 *  0069D8DF   0FBAE7 03        BT EDI,0x3
 *  0069D8E3   73 11            JNB SHORT Rance03T.0069D8F6
 *  0069D8E5   F3:              PREFIX REP:                                   ; Superfluous prefix
 *  0069D8E6   0F7E0E           MOVD DWORD PTR DS:[ESI],MM1
 *  0069D8E9   83E9 08          SUB ECX,0x8
 *  0069D8EC   8D76 08          LEA ESI,DWORD PTR DS:[ESI+0x8]
 *  0069D8EF   66:0FD6          ???                                           ; Unknown command
 *  0069D8F2  -0F8D 7F08F7C6    JGE C760E177
 *  0069D8F8   07               POP ES                                        ; Modification of segment register
 *  0069D8F9   0000             ADD BYTE PTR DS:[EAX],AL
 *  0069D8FB   007463 0F        ADD BYTE PTR DS:[EBX+0xF],DH
 *  0069D8FF   BA E6030F83      MOV EDX,0x830F03E6
 *  0069D904   B2 00            MOV DL,0x0
 *  0069D906   0000             ADD BYTE PTR DS:[EAX],AL
 *  0069D908   66:0F6F4E F4     MOVQ MM1,QWORD PTR DS:[ESI-0xC]
 *  0069D90D   8D76 F4          LEA ESI,DWORD PTR DS:[ESI-0xC]
 *  0069D910   66:0F6F5E 10     MOVQ MM3,QWORD PTR DS:[ESI+0x10]
 *  0069D915   83E9 30          SUB ECX,0x30
 *  0069D918   66:0F6F46 20     MOVQ MM0,QWORD PTR DS:[ESI+0x20]
 *  0069D91D   66:0F6F6E 30     MOVQ MM5,QWORD PTR DS:[ESI+0x30]
 *  0069D922   8D76 30          LEA ESI,DWORD PTR DS:[ESI+0x30]
 *  0069D925   83F9 30          CMP ECX,0x30
 *  0069D928   66:0F6FD3        MOVQ MM2,MM3
 *  0069D92C   66:0F3A          ???                                           ; Unknown command
 *  0069D92F   0FD90C66         PSUBUSW MM1,QWORD PTR DS:[ESI]
 *  0069D933   0F7F1F           MOVQ QWORD PTR DS:[EDI],MM3
 *  0069D936   66:0F6FE0        MOVQ MM4,MM0
 *  0069D93A   66:0F3A          ???                                           ; Unknown command
 *  0069D93D   0FC20C66 0F      CMPPS XMM1,DQWORD PTR DS:[ESI],0xF
 *  0069D942   7F 47            JG SHORT Rance03T.0069D98B
 *  0069D944   1066 0F          ADC BYTE PTR DS:[ESI+0xF],AH
 *  0069D947   6F               OUTS DX,DWORD PTR ES:[EDI]                    ; I/O command
 *  0069D948   CD 66            INT 0x66
 *  0069D94A   0F3A             ???                                           ; Unknown command
 *  0069D94C   0FEC0C66         PADDSB MM1,QWORD PTR DS:[ESI]
 *  0069D950   0F7F6F 20        MOVQ QWORD PTR DS:[EDI+0x20],MM5
 *  0069D954   8D7F 30          LEA EDI,DWORD PTR DS:[EDI+0x30]
 *  0069D957  ^7D B7            JGE SHORT Rance03T.0069D910
 *  0069D959   8D76 0C          LEA ESI,DWORD PTR DS:[ESI+0xC]
 *  0069D95C   E9 AF000000      JMP Rance03T.0069DA10
 *  0069D961   66:0F6F4E F8     MOVQ MM1,QWORD PTR DS:[ESI-0x8]
 *  0069D966   8D76 F8          LEA ESI,DWORD PTR DS:[ESI-0x8]
 *  0069D969   8D49 00          LEA ECX,DWORD PTR DS:[ECX]
 *  0069D96C   66:0F6F5E 10     MOVQ MM3,QWORD PTR DS:[ESI+0x10]
 *  0069D971   83E9 30          SUB ECX,0x30
 *  0069D974   66:0F6F46 20     MOVQ MM0,QWORD PTR DS:[ESI+0x20]
 *  0069D979   66:0F6F6E 30     MOVQ MM5,QWORD PTR DS:[ESI+0x30]
 *  0069D97E   8D76 30          LEA ESI,DWORD PTR DS:[ESI+0x30]
 *  0069D981   83F9 30          CMP ECX,0x30
 *  0069D984   66:0F6FD3        MOVQ MM2,MM3
 *  0069D988   66:0F3A          ???                                           ; Unknown command
 *  0069D98B   0FD908           PSUBUSW MM1,QWORD PTR DS:[EAX]
 *  0069D98E   66:0F7F1F        MOVQ QWORD PTR DS:[EDI],MM3
 *  0069D992   66:0F6FE0        MOVQ MM4,MM0
 *  0069D996   66:0F3A          ???                                           ; Unknown command
 *  0069D999   0FC208 66        CMPPS XMM1,DQWORD PTR DS:[EAX],0x66
 *  0069D99D   0F7F47 10        MOVQ QWORD PTR DS:[EDI+0x10],MM0
 *  0069D9A1   66:0F6FCD        MOVQ MM1,MM5
 *  0069D9A5   66:0F3A          ???                                           ; Unknown command
 *  0069D9A8   0FEC08           PADDSB MM1,QWORD PTR DS:[EAX]
 *  0069D9AB   66:0F7F6F 20     MOVQ QWORD PTR DS:[EDI+0x20],MM5
 *  0069D9B0   8D7F 30          LEA EDI,DWORD PTR DS:[EDI+0x30]
 *  0069D9B3  ^7D B7            JGE SHORT Rance03T.0069D96C
 *  0069D9B5   8D76 08          LEA ESI,DWORD PTR DS:[ESI+0x8]
 *  0069D9B8   EB 56            JMP SHORT Rance03T.0069DA10
 *  0069D9BA   66:0F6F4E FC     MOVQ MM1,QWORD PTR DS:[ESI-0x4]
 *  0069D9BF   8D76 FC          LEA ESI,DWORD PTR DS:[ESI-0x4]
 *  0069D9C2   8BFF             MOV EDI,EDI
 *  0069D9C4   66:0F6F5E 10     MOVQ MM3,QWORD PTR DS:[ESI+0x10]
 *  0069D9C9   83E9 30          SUB ECX,0x30
 *  0069D9CC   66:0F6F46 20     MOVQ MM0,QWORD PTR DS:[ESI+0x20]
 *  0069D9D1   66:0F6F6E 30     MOVQ MM5,QWORD PTR DS:[ESI+0x30]
 *  0069D9D6   8D76 30          LEA ESI,DWORD PTR DS:[ESI+0x30]
 *  0069D9D9   83F9 30          CMP ECX,0x30
 *  0069D9DC   66:0F6FD3        MOVQ MM2,MM3
 *  0069D9E0   66:0F3A          ???                                           ; Unknown command
 *  0069D9E3   0FD90466         PSUBUSW MM0,QWORD PTR DS:[ESI]
 *  0069D9E7   0F7F1F           MOVQ QWORD PTR DS:[EDI],MM3
 *  0069D9EA   66:0F6FE0        MOVQ MM4,MM0
 *  0069D9EE   66:0F3A          ???                                           ; Unknown command
 *  0069D9F1   0FC20466 0F      CMPPS XMM0,DQWORD PTR DS:[ESI],0xF
 *  0069D9F6   7F 47            JG SHORT Rance03T.0069DA3F
 *  0069D9F8   1066 0F          ADC BYTE PTR DS:[ESI+0xF],AH
 *  0069D9FB   6F               OUTS DX,DWORD PTR ES:[EDI]                    ; I/O command
 *  0069D9FC   CD 66            INT 0x66
 *  0069D9FE   0F3A             ???                                           ; Unknown command
 *  0069DA00   0FEC0466         PADDSB MM0,QWORD PTR DS:[ESI]
 *  0069DA04   0F7F6F 20        MOVQ QWORD PTR DS:[EDI+0x20],MM5
 *  0069DA08   8D7F 30          LEA EDI,DWORD PTR DS:[EDI+0x30]
 *  0069DA0B  ^7D B7            JGE SHORT Rance03T.0069D9C4
 *  0069DA0D   8D76 04          LEA ESI,DWORD PTR DS:[ESI+0x4]
 *  0069DA10   83F9 10          CMP ECX,0x10
 *  0069DA13   7C 13            JL SHORT Rance03T.0069DA28
 *  0069DA15   F3:              PREFIX REP:                                   ; Superfluous prefix
 *  0069DA16   0F6F0E           MOVQ MM1,QWORD PTR DS:[ESI]
 *  0069DA19   83E9 10          SUB ECX,0x10
 *  0069DA1C   8D76 10          LEA ESI,DWORD PTR DS:[ESI+0x10]
 *  0069DA1F   66:0F7F0F        MOVQ QWORD PTR DS:[EDI],MM1
 *  0069DA23   8D7F 10          LEA EDI,DWORD PTR DS:[EDI+0x10]
 *  0069DA26  ^EB E8            JMP SHORT Rance03T.0069DA10
 *  0069DA28   0FBAE1 02        BT ECX,0x2
 *  0069DA2C   73 0D            JNB SHORT Rance03T.0069DA3B
 *  0069DA2E   8B06             MOV EAX,DWORD PTR DS:[ESI]
 *  0069DA30   83E9 04          SUB ECX,0x4
 *  0069DA33   8D76 04          LEA ESI,DWORD PTR DS:[ESI+0x4]
 *  0069DA36   8907             MOV DWORD PTR DS:[EDI],EAX
 *  0069DA38   8D7F 04          LEA EDI,DWORD PTR DS:[EDI+0x4]
 *  0069DA3B   0FBAE1 03        BT ECX,0x3
 *  0069DA3F   73 11            JNB SHORT Rance03T.0069DA52
 *  0069DA41   F3:              PREFIX REP:                                   ; Superfluous prefix
 *  0069DA42   0F7E0E           MOVD DWORD PTR DS:[ESI],MM1
 *  0069DA45   83E9 08          SUB ECX,0x8
 *  0069DA48   8D76 08          LEA ESI,DWORD PTR DS:[ESI+0x8]
 *  0069DA4B   66:0FD6          ???                                           ; Unknown command
 *  0069DA4E  -0F8D 7F088B04    JGE 04F4E2D3
 *  0069DA54   8D88 DB6900FF    LEA ECX,DWORD PTR DS:[EAX+0xFF0069DB]
 *  0069DA5A  ^E0 F7            LOOPDNE SHORT Rance03T.0069DA53
 *  0069DA5C   C703 00000075    MOV DWORD PTR DS:[EBX],0x75000000
 *  0069DA62   15 C1E90283      ADC EAX,0x8302E9C1
 *  0069DA67   E2 03            LOOPD SHORT Rance03T.0069DA6C
 *  0069DA69   83F9 08          CMP ECX,0x8
 *  0069DA6C   72 2A            JB SHORT Rance03T.0069DA98
 *  0069DA6E   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS:[ESI>
 *  0069DA70   FF2495 88DB6900  JMP DWORD PTR DS:[EDX*4+0x69DB88]
 *  0069DA77   90               NOP
 *
 *  0012F810   0B4D3F30
 *  0012F814   06128970
 *  0012F818   005D3E12  RETURN to Rance03T.005D3E12 from Rance03T.0069D850
 *  0012F81C   06160B98	; jichi: target text
 *  0012F820   07F8CA80 ; jichi: source text
 *  0012F824   00000017 ; jichi: size including \0
 *  0012F828   00384460
 *  0012F82C   00384240
 *  0012F830   0B4D3F30
 *  0012F834   005C68DA  RETURN to Rance03T.005C68DA from Rance03T.005D3D90
 *  0012F838   0B4D3F30
 *  0012F83C   0012FAA8
 *  0012F840   00384240
 *  0012F844   0012F85C
 *  0012F848   0012FF18
 *  0012F84C   005C1693  RETURN to Rance03T.005C1693 from Rance03T.005C6870
 *  0012F850   0012FAA8
 *  0012F854   00384240
 *  0012F858   0000000F
 *  0012F85C  /0012FF3C
 *
 *  Actual hooked function:
 *  005D3D8B   CC               INT3
 *  005D3D8C   CC               INT3
 *  005D3D8D   CC               INT3
 *  005D3D8E   CC               INT3
 *  005D3D8F   CC               INT3
 *  005D3D90   53               PUSH EBX
 *  005D3D91   56               PUSH ESI
 *  005D3D92   8B7424 0C        MOV ESI,DWORD PTR SS:[ESP+0xC]
 *  005D3D96   57               PUSH EDI
 *  005D3D97   8BF9             MOV EDI,ECX
 *  005D3D99   837E 0C 00       CMP DWORD PTR DS:[ESI+0xC],0x0
 *  005D3D9D   74 1C            JE SHORT Rance03T.005D3DBB
 *  005D3D9F   8B56 08          MOV EDX,DWORD PTR DS:[ESI+0x8]
 *  005D3DA2   85D2             TEST EDX,EDX
 *  005D3DA4   74 15            JE SHORT Rance03T.005D3DBB
 *  005D3DA6   8D4A 01          LEA ECX,DWORD PTR DS:[EDX+0x1]
 *  005D3DA9   8DA424 00000000  LEA ESP,DWORD PTR SS:[ESP]
 *  005D3DB0   8A02             MOV AL,BYTE PTR DS:[EDX]
 *  005D3DB2   42               INC EDX
 *  005D3DB3   84C0             TEST AL,AL
 *  005D3DB5  ^75 F9            JNZ SHORT Rance03T.005D3DB0
 *  005D3DB7   2BD1             SUB EDX,ECX
 *  005D3DB9   EB 02            JMP SHORT Rance03T.005D3DBD
 *  005D3DBB   33D2             XOR EDX,EDX
 *  005D3DBD   8D5A 01          LEA EBX,DWORD PTR DS:[EDX+0x1]
 *  005D3DC0   3B5F 0C          CMP EBX,DWORD PTR DS:[EDI+0xC]
 *  005D3DC3   76 1A            JBE SHORT Rance03T.005D3DDF
 *  005D3DC5   53               PUSH EBX
 *  005D3DC6   8D4F 04          LEA ECX,DWORD PTR DS:[EDI+0x4]
 *  005D3DC9   C747 0C 00000000 MOV DWORD PTR DS:[EDI+0xC],0x0
 *  005D3DD0   E8 DB700700      CALL Rance03T.0064AEB0
 *  005D3DD5   84C0             TEST AL,AL
 *  005D3DD7   75 06            JNZ SHORT Rance03T.005D3DDF
 *  005D3DD9   5F               POP EDI
 *  005D3DDA   5E               POP ESI
 *  005D3DDB   5B               POP EBX
 *  005D3DDC   C2 0400          RETN 0x4
 *  005D3DDF   837E 0C 00       CMP DWORD PTR DS:[ESI+0xC],0x0
 *  005D3DE3   75 04            JNZ SHORT Rance03T.005D3DE9
 *  005D3DE5   33C9             XOR ECX,ECX
 *  005D3DE7   EB 03            JMP SHORT Rance03T.005D3DEC
 *  005D3DE9   8B4E 08          MOV ECX,DWORD PTR DS:[ESI+0x8]
 *  005D3DEC   837F 0C 00       CMP DWORD PTR DS:[EDI+0xC],0x0
 *  005D3DF0   75 15            JNZ SHORT Rance03T.005D3E07
 *  005D3DF2   53               PUSH EBX
 *  005D3DF3   33C0             XOR EAX,EAX
 *  005D3DF5   51               PUSH ECX
 *  005D3DF6   50               PUSH EAX
 *  005D3DF7   E8 549A0C00      CALL Rance03T.0069D850
 *  005D3DFC   83C4 0C          ADD ESP,0xC
 *  005D3DFF   B0 01            MOV AL,0x1
 *  005D3E01   5F               POP EDI
 *  005D3E02   5E               POP ESI
 *  005D3E03   5B               POP EBX
 *  005D3E04   C2 0400          RETN 0x4
 *  005D3E07   8B47 08          MOV EAX,DWORD PTR DS:[EDI+0x8]
 *  005D3E0A   53               PUSH EBX
 *  005D3E0B   51               PUSH ECX
 *  005D3E0C   50               PUSH EAX
 *  005D3E0D  -E9 EEC1A201      JMP 02000000    ; jichi: called here
 *  005D3E12   83C4 0C          ADD ESP,0xC
 *  005D3E15   B0 01            MOV AL,0x1
 *  005D3E17   5F               POP EDI
 *  005D3E18   5E               POP ESI
 *  005D3E19   5B               POP EBX
 *  005D3E1A   C2 0400          RETN 0x4
 *  005D3E1D   CC               INT3
 *  005D3E1E   CC               INT3
 *  005D3E1F   CC               INT3
 *
 *  Arg1 of this function:
 *  07B743F8  90 7A 70 00 F4 87 70 00 70 0E 27 08 1B 00 00 00  諏p.p.p'...
 *  07B74408  20 00 00 00 02 00 00 00 01 00 00 00 CC 7F 2D 00   .........ﾌ-.
 *  07B74418  B3 52 41 00 FF FF FF FF EC 87 70 00 10 E3 1D 08  ｳRA.・p.・
 *
 *  Caller that preserved:
 *  005C68A7   8B86 74010000    MOV EAX,DWORD PTR DS:[ESI+0x174]
 *  005C68AD   8B1CA8           MOV EBX,DWORD PTR DS:[EAX+EBP*4]
 *  005C68B0   85DB             TEST EBX,EBX
 *  005C68B2   74 63            JE SHORT Rance03T.005C6917
 *  005C68B4   8B86 78010000    MOV EAX,DWORD PTR DS:[ESI+0x178]
 *  005C68BA   2B86 74010000    SUB EAX,DWORD PTR DS:[ESI+0x174]
 *  005C68C0   C1F8 02          SAR EAX,0x2
 *  005C68C3   3BD0             CMP EDX,EAX
 *  005C68C5   73 3C            JNB SHORT Rance03T.005C6903
 *  005C68C7   8B86 74010000    MOV EAX,DWORD PTR DS:[ESI+0x174]
 *  005C68CD   8B0C90           MOV ECX,DWORD PTR DS:[EAX+EDX*4]
 *  005C68D0   85C9             TEST ECX,ECX
 *  005C68D2   74 2F            JE SHORT Rance03T.005C6903
 *  005C68D4   53               PUSH EBX
 *  005C68D5   E8 B6D40000      CALL Rance03T.005D3D90 ; jichi: called
 *  005C68DA   84C0             TEST AL,AL      ; jichi: retaddr
 *  005C68DC   75 18            JNZ SHORT Rance03T.005C68F6
 *  005C68DE   68 94726E00      PUSH Rance03T.006E7294
 *  005C68E3   68 00736E00      PUSH Rance03T.006E7300                   ; ASCII "S_ASSIGN"
 *  005C68E8   56               PUSH ESI
 *  005C68E9   E8 12BBFFFF      CALL Rance03T.005C2400
 *  005C68EE   83C4 0C          ADD ESP,0xC
 *  005C68F1   5F               POP EDI
 *  005C68F2   5E               POP ESI
 */
bool attach(ulong startAddress, ulong stopAddress)
{
  const uint8_t bytes[] = {
    0x53,                                   // 005D3D90   53               PUSH EBX
    0x56,                                   // 005D3D91   56               PUSH ESI
    0x8B,0x74,0x24, 0x0C,                   // 005D3D92   8B7424 0C        MOV ESI,DWORD PTR SS:[ESP+0xC]
    0x57,                                   // 005D3D96   57               PUSH EDI
    0x8B,0xF9,                              // 005D3D97   8BF9             MOV EDI,ECX
    0x83,0x7E, 0x0C, 0x00,                  // 005D3D99   837E 0C 00       CMP DWORD PTR DS:[ESI+0xC],0x0
    0x74, 0x1C,                             // 005D3D9D   74 1C            JE SHORT Rance03T.005D3DBB
    0x8B,0x56, 0x08,                        // 005D3D9F   8B56 08          MOV EDX,DWORD PTR DS:[ESI+0x8]
    0x85,0xD2,                              // 005D3DA2   85D2             TEST EDX,EDX
    0x74, 0x15,                             // 005D3DA4   74 15            JE SHORT Rance03T.005D3DBB
    0x8D,0x4A, 0x01,                        // 005D3DA6   8D4A 01          LEA ECX,DWORD PTR DS:[EDX+0x1]
    0x8D,0xA4,0x24, 0x00,0x00,0x00,0x00,    // 005D3DA9   8DA424 00000000  LEA ESP,DWORD PTR SS:[ESP]
    0x8A,0x02,                              // 005D3DB0   8A02             MOV AL,BYTE PTR DS:[EDX]
    0x42,                                   // 005D3DB2   42               INC EDX
    0x84,0xC0                               // 005D3DB3   84C0             TEST AL,AL
  };
  ulong addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  if (!addr)
    return false;
  //addr = MemDbg::findEnclosingAlignedFunction(addr);
  //if (!addr)
  //  return false;
  //addr = 0x005D3D90;
  //return winhook::hook_before(addr, Private::hookBefore);

  int count = 0;
  auto fun = [&count](ulong addr) -> bool {
    auto retaddr = addr + 5;
    // 005C68DA   84C0             TEST AL,AL
    if (*(WORD *)retaddr == 0xc084)
      //auto before = std::bind(Private::hookBefore, addr + 5, std::placeholders::_1);
      count += winhook::hook_both(addr, Private::hookBefore, Private::hookAfter);
    return true; // replace all functions
  };
  MemDbg::iterNearCallAddress(fun, addr, startAddress, stopAddress);
  DOUT("call number =" << count);
  return count;
}

} // namespace ScenarioHook

} // unnamed namespace

bool System4Engine::attachSystem44(ulong startAddress, ulong stopAddress)
{ return ScenarioHook::attach(startAddress, stopAddress); }

// EOF
