// cotopha.cc
// 6/30/2015 jichi
#include "engine/model/cotopha.h"
#include "engine/enginecontroller.h"
#include "engine/enginedef.h"
#include "engine/enginehash.h"
#include "engine/engineutil.h"
//#include "hijack/hijackmanager.h"
#include "memdbg/memsearch.h"
#include "winasm/winasmdef.h"
#include "winhook/hookcode.h"
#include <qt_windows.h>
#include <cstdint>
#include <unordered_set>

#define DEBUG "model/cotopha"
#include "sakurakit/skdebug.h"

/** Private data */

namespace { // unnamed

namespace ScenarioHook {

namespace Private {

  /**
   *  Sample game: お兄ちゃん、右手の使用を禁止します！ (old type)
   *
   *  - Name
   *
   *  EAX 00000000
   *  ECX 04A4C058
   *  EDX 00713FD8 .00713FD8
   *  EBX 17F90130
   *  ESP 0012EBBC
   *  EBP 0020C5A8
   *  ESI 04A4B678
   *  EDI 04A4C058
   *  EIP 005C2E20 .005C2E20
   *
   *  0012EBBC   0055D210  RETURN to .0055D210
   *  0012EBC0   17F90130
   *  0012EBC4   04A4B678
   *  0012EBC8   00000000
   *  0012EBCC   0020C5A8
   *  0012EBD0   00000000   ; jichi: used to identify name
   *  0012EBD4   00000000
   *  0012EBD8   04A4B678
   *  0012EBDC   00000000
   *  0012EBE0   0020C5A8
   *  0012EBE4   00000000
   *  0012EBE8   0055C58F  RETURN to .0055C58F from .0046CD30
   *  0012EBEC   0012EC54
   *  0012EBF0   0055C5A3  RETURN to .0055C5A3 from .0055D180
   *  0012EBF4   04A4C058
   *  0012EBF8   04A4B678
   *
   *  - Scenario
   *
   *  EAX 00000000
   *  ECX 04A4CC30
   *  EDX 00713FD8 .00713FD8
   *  EBX 17F90170
   *  ESP 0012EBBC
   *  EBP 00000015
   *  ESI 04A4C250
   *  EDI 04A4CC30
   *  EIP 005C2E20 .005C2E20
   *
   *  0012EBBC   0055D210  RETURN to .0055D210
   *  0012EBC0   17F90170
   *  0012EBC4   04A4C250
   *  0012EBC8   0000001E   ; jichi: old game arg3 is 1e
   *  0012EBCC   00000015
   *  0012EBD0   00000002
   *  0012EBD4   00000002
   *  0012EBD8   04A4C250
   *  0012EBDC   0000001E
   *  0012EBE0   00000015
   *  0012EBE4   00000000
   *  0012EBE8   0055C58F  RETURN to .0055C58F from .0046CD30
   *  0012EBEC   0012EC54
   *  0012EBF0   0055C5A3  RETURN to .0055C5A3 from .0055D180
   *
   *  Caller of the scenario/name thread:
   *  0055D207   8BCF             MOV ECX,EDI
   *  0055D209   897C24 34        MOV DWORD PTR SS:[ESP+0x34],EDI
   *  0055D20D   FF52 14          CALL DWORD PTR DS:[EDX+0x14]  ; jichi: called here
   *  0055D210   8BCF             MOV ECX,EDI   ; jichi: retaddr is here
   *  0055D212   894424 18        MOV DWORD PTR SS:[ESP+0x18],EAX
   *  0055D216   E8 456D0600      CALL .005C3F60
   *  0055D21B   33C9             XOR ECX,ECX
   *  0055D21D   894424 14        MOV DWORD PTR SS:[ESP+0x14],EAX
   *  0055D221   3BC1             CMP EAX,ECX
   *  0055D223   76 06            JBE SHORT .0055D22B
   *
   *  Sample game: キスと魔王と紅茶 (very old type)
   *
   *  - Name:
   *
   *  EAX 0A4106C0 ASCII "ｩa"
   *  ECX 0012F594
   *  EDX 0058032C ASCII "pgM"
   *  EBX 00000000
   *  ESP 0012F4F4
   *  EBP 00000003
   *  ESI 0012F618
   *  EDI 0012F594
   *  EIP 004D52B0 .004D52B0
   *
   *  0012F4F4   004DBFF2  RETURN to .004DBFF2
   *  0012F4F8   0A4106C0  ASCII "ｩa"
   *  0012F4FC   0012F698
   *  0012F500   0012F618
   *  0012F504   0296EA58
   *  0012F508   00000000  ; jichi: used to identify name
   *  0012F50C   0A40EC00
   *  0012F510   00000000
   *  0012F514   000000F9
   *  0012F518   00005DC8
   *  0012F51C   00580304  ASCII "PgM"
   *  0012F520   D90A0DDD
   *  0012F524   00000018
   *  0012F528   00000000
   *
   *  - Scenario:
   *
   *  EAX 00000000
   *  ECX 01B69134
   *  EDX 0058032C ASCII "pgM"
   *  EBX 09E82E88
   *  ESP 0012F548
   *  EBP 00000016
   *  ESI 01B68A70
   *  EDI 01B69134
   *  EIP 004D52B0 .004D52B0
   *
   *  0012F548   004B5210  RETURN to .004B5210
   *  0012F54C   09E82E88
   *  0012F550   01B68A70
   *  0012F554   00000018
   *  0012F558   00000016
   *  0012F55C   00000009
   *  0012F560   01B69134
   *  0012F564   01B68A70
   *  0012F568   00000018
   *  0012F56C   00000016
   *  0012F570   00000000
   *  0012F574   004B459F  RETURN to .004B459F from .0040DE50
   *  0012F578   0012F5E0
   *  0012F57C   004B45B3  RETURN to .004B45B3 from .004B5180
   *  0012F580   09E82E88
   *  0012F584   00000000
   *  0012F588   0012FC78
   *  0012F58C   00000000
   *  0012F590   01B68A70
   *  0012F594   005655D0  .005655D0
   *  0012F598   0057BB80  .0057BB80
   *  0012F59C   0A419628
   *
   *  Caller of the name/scenario thread
   *
   *  004B517D   90               NOP
   *  004B517E   90               NOP
   *  004B517F   90               NOP
   *  004B5180   83EC 1C          SUB ESP,0x1C
   *  004B5183   53               PUSH EBX
   *  004B5184   55               PUSH EBP
   *  004B5185   8B5C24 28        MOV EBX,DWORD PTR SS:[ESP+0x28]
   *  004B5189   56               PUSH ESI
   *  004B518A   8BF1             MOV ESI,ECX
   *  004B518C   57               PUSH EDI
   *  004B518D   8B86 A0050000    MOV EAX,DWORD PTR DS:[ESI+0x5A0]
   *  004B5193   85C0             TEST EAX,EAX
   *  004B5195   74 63            JE SHORT .004B51FA
   *  004B5197   53               PUSH EBX
   *  004B5198   8D8E C4060000    LEA ECX,DWORD PTR DS:[ESI+0x6C4]
   *  004B519E   E8 3DFD0100      CALL .004D4EE0
   *  004B51A3   8BF8             MOV EDI,EAX
   *  004B51A5   8D86 D4060000    LEA EAX,DWORD PTR DS:[ESI+0x6D4]
   *  004B51AB   8B8E EC060000    MOV ECX,DWORD PTR DS:[ESI+0x6EC]
   *  004B51B1   8BAE F0060000    MOV EBP,DWORD PTR DS:[ESI+0x6F0]
   *  004B51B7   8B10             MOV EDX,DWORD PTR DS:[EAX]
   *  004B51B9   895424 1C        MOV DWORD PTR SS:[ESP+0x1C],EDX
   *  004B51BD   8B50 04          MOV EDX,DWORD PTR DS:[EAX+0x4]
   *  004B51C0   895424 20        MOV DWORD PTR SS:[ESP+0x20],EDX
   *  004B51C4   8B50 08          MOV EDX,DWORD PTR DS:[EAX+0x8]
   *  004B51C7   8B40 0C          MOV EAX,DWORD PTR DS:[EAX+0xC]
   *  004B51CA   894424 28        MOV DWORD PTR SS:[ESP+0x28],EAX
   *  004B51CE   8BC2             MOV EAX,EDX
   *  004B51D0   2BC1             SUB EAX,ECX
   *  004B51D2   3BF8             CMP EDI,EAX
   *  004B51D4   7F 24            JG SHORT .004B51FA
   *  004B51D6   83BE A0050000 03 CMP DWORD PTR DS:[ESI+0x5A0],0x3
   *  004B51DD   75 0B            JNZ SHORT .004B51EA
   *  004B51DF   2BC7             SUB EAX,EDI
   *  004B51E1   99               CDQ
   *  004B51E2   2BC2             SUB EAX,EDX
   *  004B51E4   D1F8             SAR EAX,1
   *  004B51E6   03C8             ADD ECX,EAX
   *  004B51E8   EB 04            JMP SHORT .004B51EE
   *  004B51EA   2BD7             SUB EDX,EDI
   *  004B51EC   8BCA             MOV ECX,EDX
   *  004B51EE   898E EC060000    MOV DWORD PTR DS:[ESI+0x6EC],ECX
   *  004B51F4   89AE F0060000    MOV DWORD PTR DS:[ESI+0x6F0],EBP
   *  004B51FA   8B96 C4060000    MOV EDX,DWORD PTR DS:[ESI+0x6C4]
   *  004B5200   8DBE C4060000    LEA EDI,DWORD PTR DS:[ESI+0x6C4]
   *  004B5206   53               PUSH EBX
   *  004B5207   8BCF             MOV ECX,EDI
   *  004B5209   897C24 14        MOV DWORD PTR SS:[ESP+0x14],EDI
   *  004B520D   FF52 10          CALL DWORD PTR DS:[EDX+0x10]  ; jichi: called here
   *  004B5210   8BCF             MOV ECX,EDI   ; jichi: retaddr is here
   *  004B5212   894424 18        MOV DWORD PTR SS:[ESP+0x18],EAX
   *  004B5216   E8 85120200      CALL .004D64A0
   *  004B521B   33ED             XOR EBP,EBP
   *  004B521D   894424 14        MOV DWORD PTR SS:[ESP+0x14],EAX
   *  004B5221   3BC5             CMP EAX,EBP
   *  004B5223   76 06            JBE SHORT .004B522B
   *  004B5225   89AE A0050000    MOV DWORD PTR DS:[ESI+0x5A0],EBP
   *  004B522B   85C0             TEST EAX,EAX
   *  004B522D   896C24 30        MOV DWORD PTR SS:[ESP+0x30],EBP
   *  004B5231   76 68            JBE SHORT .004B529B
   *  004B5233   55               PUSH EBP
   *  004B5234   8BCF             MOV ECX,EDI
   *  004B5236   E8 75120200      CALL .004D64B0
   *  004B523B   85C0             TEST EAX,EAX
   *  004B523D   74 4F            JE SHORT .004B528E
   *  004B523F   50               PUSH EAX
   *  004B5240   8BCE             MOV ECX,ESI
   *  004B5242   E8 69000000      CALL .004B52B0
   *  004B5247   8BD8             MOV EBX,EAX
   *  004B5249   85DB             TEST EBX,EBX
   *  004B524B   74 41            JE SHORT .004B528E
   *  004B524D   8B86 C0060000    MOV EAX,DWORD PTR DS:[ESI+0x6C0]
   *  004B5253   8B8E B0060000    MOV ECX,DWORD PTR DS:[ESI+0x6B0]
   *  004B5259   8BAE 30070000    MOV EBP,DWORD PTR DS:[ESI+0x730]
   *  004B525F   8DBE 28070000    LEA EDI,DWORD PTR DS:[ESI+0x728]
   *  004B5265   03C8             ADD ECX,EAX
   *  004B5267   6A 00            PUSH 0x0
   *  004B5269   8D55 01          LEA EDX,DWORD PTR SS:[EBP+0x1]
   *  004B526C   898E C0060000    MOV DWORD PTR DS:[ESI+0x6C0],ECX
   *  004B5272   52               PUSH EDX
   *  004B5273   8BCF             MOV ECX,EDI
   *  004B5275   8983 C0000000    MOV DWORD PTR DS:[EBX+0xC0],EAX
   *  004B527B   E8 8003F8FF      CALL .00435600
   *  004B5280   8B47 04          MOV EAX,DWORD PTR DS:[EDI+0x4]
   *  004B5283   8B7C24 10        MOV EDI,DWORD PTR SS:[ESP+0x10]
   *  004B5287   891CA8           MOV DWORD PTR DS:[EAX+EBP*4],EBX
   *  004B528A   8B6C24 30        MOV EBP,DWORD PTR SS:[ESP+0x30]
   *  004B528E   8B4424 14        MOV EAX,DWORD PTR SS:[ESP+0x14]
   *  004B5292   45               INC EBP
   *  004B5293   3BE8             CMP EBP,EAX
   *  004B5295   896C24 30        MOV DWORD PTR SS:[ESP+0x30],EBP
   *  004B5299  ^72 98            JB SHORT .004B5233
   *  004B529B   8BCF             MOV ECX,EDI
   *  004B529D   E8 2E120200      CALL .004D64D0
   *  004B52A2   8B4424 18        MOV EAX,DWORD PTR SS:[ESP+0x18]
   *  004B52A6   5F               POP EDI
   *  004B52A7   5E               POP ESI
   *  004B52A8   5D               POP EBP
   *  004B52A9   5B               POP EBX
   *  004B52AA   83C4 1C          ADD ESP,0x1C
   *  004B52AD   C2 0400          RETN 0x4
   *  004B52B0   64:A1 00000000   MOV EAX,DWORD PTR FS:[0]
   *  004B52B6   6A FF            PUSH -0x1
   *  004B52B8   68 A1F15200      PUSH .0052F1A1
   *  004B52BD   50               PUSH EAX
   *  004B52BE   64:8925 00000000 MOV DWORD PTR FS:[0],ESP
   *  004B52C5   81EC CC000000    SUB ESP,0xCC
   *  004B52CB   56               PUSH ESI
   *  004B52CC   8BF1             MOV ESI,ECX
   *  004B52CE   8B8C24 E0000000  MOV ECX,DWORD PTR SS:[ESP+0xE0]
   *  004B52D5   57               PUSH EDI
   *  004B52D6   85C9             TEST ECX,ECX
   *  004B52D8   75 07            JNZ SHORT .004B52E1
   *  004B52DA   33C0             XOR EAX,EAX
   *  004B52DC   E9 55060000      JMP .004B5936
   *  004B52E1   8B79 14          MOV EDI,DWORD PTR DS:[ECX+0x14]
   *  004B52E4   85FF             TEST EDI,EDI
   *  004B52E6   897C24 18        MOV DWORD PTR SS:[ESP+0x18],EDI
   *  004B52EA   75 07            JNZ SHORT .004B52F3
   *  004B52EC   33C0             XOR EAX,EAX
   *  004B52EE   E9 43060000      JMP .004B5936
   *  004B52F3   8A86 AA060000    MOV AL,BYTE PTR DS:[ESI+0x6AA]
   *  004B52F9   84C0             TEST AL,AL
   *  004B52FB   74 51            JE SHORT .004B534E
   *  004B52FD   8B01             MOV EAX,DWORD PTR DS:[ECX]
   *  004B52FF   8D5424 08        LEA EDX,DWORD PTR SS:[ESP+0x8]
   *  004B5303   52               PUSH EDX
   *  004B5304   FF50 34          CALL DWORD PTR DS:[EAX+0x34]
   *  004B5307   8D86 D4060000    LEA EAX,DWORD PTR DS:[ESI+0x6D4]
   *  004B530D   8B8E D4060000    MOV ECX,DWORD PTR DS:[ESI+0x6D4]
   *  004B5313   894C24 48        MOV DWORD PTR SS:[ESP+0x48],ECX
   *  004B5317   8B50 04          MOV EDX,DWORD PTR DS:[EAX+0x4]
   *  004B531A   895424 4C        MOV DWORD PTR SS:[ESP+0x4C],EDX
   *  004B531E   8B48 08          MOV ECX,DWORD PTR DS:[EAX+0x8]
   *  004B5321   894C24 50        MOV DWORD PTR SS:[ESP+0x50],ECX
   *  004B5325   8A8E 14070000    MOV CL,BYTE PTR DS:[ESI+0x714]
   *  004B532B   8B40 0C          MOV EAX,DWORD PTR DS:[EAX+0xC]
   *  004B532E   84C9             TEST CL,CL
   *  004B5330   75 0D            JNZ SHORT .004B533F
   *  004B5332   394424 0C        CMP DWORD PTR SS:[ESP+0xC],EAX
   *  004B5336   7E 16            JLE SHORT .004B534E
   *  004B5338   33C0             XOR EAX,EAX
   *  004B533A   E9 F7050000      JMP .004B5936
   *
   *  Sample game: プライマルハーツ (new type), 0x54bd80
   *  Name:
   *  0012EB5C   004DACB0  RETURN to .004DACB0
   *  0012EB60   05067E40
   *  0012EB64   0000001E   ; jichi: new game arg2 is 1e
   *  0012EB68   0012ECA8
   *  0012EB6C   008D3E48
   *  0012EB70   004512DB  RETURN to .004512DB from .00450FE0
   *  0012EB74   0000001E
   *  0012EB78   00000025
   *  0012EB7C   0012ECA8
   *  0012EB80   008D3E48
   *  0012EB84   0000001E
   *  0012EB88   004DA1CB  RETURN to .004DA1CB from .00451280
   *  0012EB8C   004DA1DF  RETURN to .004DA1DF from .004DAC20   ; jichi: 004DAC20 is a better place to hook to
   *  0012EB90   05067E40
   *  0012EB94   5D9C7C59
   *  0012EB98   00000000
   *  0012EB9C   008D3E48
   *  0012EBA0   00000000
   *  0012EBA4   00000000
   *  0012EBA8   1600C8C8
   *  0012EBAC   006835B4  .006835B4
   *  0012EBB0   1621BBF0  UNICODE "\h:\f;MsgFont:\s:\c;E6ADFA:\v:"
   *  0012EBB4   00000025
   *
   *  0012EB5C   004DACB0  RETURN to .004DACB0
   *  0012EB60   05000420
   *  0012EB64   0000001E
   *  0012EB68   0012ECA8
   *  0012EB6C   008D3E48
   *  0012EB70   004512DB  RETURN to .004512DB from .00450FE0
   *  0012EB74   0000001E
   *  0012EB78   00000022
   *  0012EB7C   0012ECA8
   *  0012EB80   008D3E48
   *  0012EB84   0000001E
   *  0012EB88   004DA1CB  RETURN to .004DA1CB from .00451280
   *  0012EB8C   004DA1DF  RETURN to .004DA1DF from .004DAC20
   *  0012EB90   05000420
   *  0012EB94   5D9C7C59
   *  0012EB98   00000000
   *  0012EB9C   008D3E48
   *  0012EBA0   00000000
   *  0012EBA4   00000000
   *  0012EBA8   05000C90
   *  0012EBAC   006835B4  .006835B4
   *  0012EBB0   05000F40  UNICODE "\h:\f;MsgFont:\s:\c;DAD4FF:\v:"
   *  0012EBB4   00000022
   *  0012EBB8   00000034
   *  0012EBBC   00000022
   *  0012EBC0   FFFFFFFF
   *  0012EBC4   7C00FFFF
   *  0012EBC8   78000000
   *  0012EBCC   F8000001
   *  0012EBD0   00000000
   *  0012EBD4   58001384
   *  0012EBD8   28000000
   *  0012EBDC   28000000
   *  0012EBE0   00000048
   *  0012EBE4   00655A28  .00655A28
   *  0012EBE8   05000420
   *  0012EBEC   00000004
   *  0012EBF0   00000007
   *  0012EBF4   00210030
   *  0012EBF8   00000000
   *  0012EBFC   00DAD4FF
   *  0012EC00   0012EC98
   *  0012EC04   00000001
   *
   *  EAX 0054BD80 .0054BD80
   *  ECX 008D4848
   *  EDX 0069E80C .0069E80C
   *  EBX 05067E40
   *  ESP 0012EB5C
   *  EBP 0012ECA8
   *  ESI 008D3E48
   *  EDI 0000001E
   *  EIP 0054BD80 .0054BD80
   *
   *  004DAC98   89AE 300A0000    MOV DWORD PTR DS:[ESI+0xA30],EBP
   *  004DAC9E   8B96 000A0000    MOV EDX,DWORD PTR DS:[ESI+0xA00]
   *  004DACA4   8B42 14          MOV EAX,DWORD PTR DS:[EDX+0x14]
   *  004DACA7   8D8E 000A0000    LEA ECX,DWORD PTR DS:[ESI+0xA00]
   *  004DACAD   53               PUSH EBX
   *  004DACAE   FFD0             CALL EAX  ; jichi: called here
   *  004DACB0   8B8E 100A0000    MOV ECX,DWORD PTR DS:[ESI+0xA10]
   *  004DACB6   894424 14        MOV DWORD PTR SS:[ESP+0x14],EAX
   *  004DACBA   8B41 08          MOV EAX,DWORD PTR DS:[ECX+0x8]
   *  004DACBD   33FF             XOR EDI,EDI
   *  004DACBF   3BC7             CMP EAX,EDI
   *  004DACC1   894424 10        MOV DWORD PTR SS:[ESP+0x10],EAX
   *
   *  ecx:
   *  01814848  0C E8 69 00 60 C7 F8 13 00 00 00 00 00 00 00 00  i읠ᏸ....
   *  01814858  28 3E 81 01 00 00 00 00 00 00 00 00 80 01 00 00  㸨Ɓ....ƀ.  ; jichi: 810 is the width and 26 the height to paint
   *  01814868  26 00 00 00 FF FF FF 00 00 00 00 00 00 00 00 00  &..ÿ....
   *  01814878  00 00 00 00 26 00 00 00 00 00 00 00 00 00 00 00  ..&.....
   *  01814888  06 00 00 00 03 00 00 00 28 5A 65 00 98 3D 81 01  ..娨e㶘Ɓ
   *  01814898  2C 00 00 00 43 00 00 00 00 01 01 00 BA C1 1E 77  ,.C.Ā솺眞
   *  018148A8  35 FC 1C 77 20 FF 1C 77 90 16 38 0B 64 D5 68 00  ﰵ眜＠眜ᚐସ핤h
   *  018148B8  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ........
   *  018148C8  7E 31 00 00 4C 03 00 00 00 00 00 00 00 00 00 00  ㅾ.͌.....
   *  018148D8  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ........
   *  018148E8  00 00 00 00 00 00 F0 3F 00 00 00 00 00 00 F0 3F  ...㿰...㿰
   *  018148F8  00 00 00 00 00 00 00 00 94 C3 67 00 00 00 00 00  ....쎔g..
   *
   *  01814848  0C E8 69 00 58 EC E4 03 00 00 00 00 00 00 00 00  iϤ....
   *  01814858  28 3E 81 01 00 00 00 00 00 00 00 00 80 01 00 00  㸨Ɓ....ƀ.
   *  01814868  26 00 00 00 FF FF FF 00 00 00 00 00 00 00 00 00  &..ÿ....
   *  01814878  00 00 00 00 26 00 00 00 00 00 00 00 00 00 00 00  ..&.....
   *  01814888  06 00 00 00 03 00 00 00 28 5A 65 00 98 3D 81 01  ..娨e㶘Ɓ
   *  01814898  2C 00 00 00 43 00 00 00 00 01 01 00 BA C1 1E 77  ,.C.Ā솺眞
   *  018148A8  35 FC 1C 77 20 FF 1C 77 90 16 38 0B 64 D5 68 00  ﰵ眜＠眜ᚐସ핤h
   *  018148B8  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ........
   *  018148C8  4B 4F 00 00 4C 03 00 00 00 00 00 00 00 00 00 00  佋.͌.....
   *  018148D8  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ........
   *  018148E8  00 00 00 00 00 00 F0 3F 00 00 00 00 00 00 F0 3F  ...㿰...㿰
   *  018148F8  00 00 00 00 00 00 00 00 94 C3 67 00 00 00 00 00  ....쎔g..
   *
   *  Scenario:
   *  EAX 0054BD80 .0054BD80
   *  ECX 008D3C50
   *  EDX 0069E80C .0069E80C
   *  EBX 1621C280
   *  ESP 0012EB5C
   *  EBP 0012ECA8
   *  ESI 008D3250
   *  EDI 0000001E
   *  EIP 0054BD80 .0054BD80
   *
   *  0012EB5C   004DACB0  RETURN to .004DACB0
   *  0012EB60   1621C280
   *  0012EB64   0000001E
   *  0012EB68   0012ECA8
   *  0012EB6C   008D3250
   *  0012EB70   004512DB  RETURN to .004512DB from .00450FE0
   *  0012EB74   0000001E
   *  0012EB78   00000041
   *  0012EB7C   0012ECA8
   *  0012EB80   008D3250
   *  0012EB84   0000001E
   *  0012EB88   004DA1CB  RETURN to .004DA1CB from .00451280
   *  0012EB8C   004DA1DF  RETURN to .004DA1DF from .004DAC20
   *  0012EB90   1621C280
   *
   *  0012EB5C   004DACB0  RETURN to .004DACB0
   *  0012EB60   050003B8
   *  0012EB64   0000001E
   *  0012EB68   0012ECA8
   *  0012EB6C   008D3250
   *  0012EB70   004512DB  RETURN to .004512DB from .00450FE0
   *  0012EB74   0000001E
   *  0012EB78   00000034
   *  0012EB7C   0012ECA8
   *  0012EB80   008D3250
   *  0012EB84   0000001E
   *  0012EB88   004DA1CB  RETURN to .004DA1CB from .00451280
   *  0012EB8C   004DA1DF  RETURN to .004DA1DF from .004DAC20
   *  0012EB90   050003B8
   *  0012EB94   5D9C7C59
   *  0012EB98   00000000
   *  0012EB9C   008D3250
   *  0012EBA0   00000000
   *  0012EBA4   00000000
   *  0012EBA8   05007A68  UNICODE "38"
   *  0012EBAC   006835B4  .006835B4
   *  0012EBB0   0500E910  UNICODE "\h:\f;MsgFont:\s:\c;DAD4FF:\v:"
   *  0012EBB4   00000034
   *  0012EBB8   0000004F
   *  0012EBBC   00000034
   *  0012EBC0   FFFFFFFF
   *  0012EBC4   7C00FFFF
   *  0012EBC8   78000000
   *  0012EBCC   F8000001
   *  0012EBD0   00000000
   *  0012EBD4   58001384
   *  0012EBD8   28000000
   *  0012EBDC   28000000
   *  0012EBE0   00000040
   *  0012EBE4   00655A28  .00655A28
   *  0012EBE8   050003B8
   *
   *  ecx:
   *  01813C50  0C E8 69 00 80 E9 F8 13 00 00 00 00 00 00 00 00  iᏸ....
   *  01813C60  30 32 81 01 00 00 00 00 00 00 00 00 84 03 00 00  ㈰Ɓ....΄.  ; jichi: 384 is the width and 76 the height to paint
   *  01813C70  76 00 00 00 FF FF FF 00 00 00 00 00 00 00 00 00  v..ÿ....
   *  01813C80  00 00 00 00 26 00 00 00 00 00 00 00 00 00 00 00  ..&.....
   *  01813C90  06 00 00 00 03 00 00 00 28 5A 65 00 A0 31 81 01  ..娨eㆠƁ
   *  01813CA0  2C 00 00 00 43 00 00 00 00 01 01 00 BA C1 1E 77  ,.C.Ā솺眞
   *  01813CB0  35 FC 1C 77 20 FF 1C 77 20 24 34 0B 64 D5 68 00  ﰵ眜＠眜␠଴핤h
   *  01813CC0  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ........
   *  01813CD0  7E 31 00 00 50 03 00 00 00 00 00 00 00 00 00 00  ㅾ.͐.....
   *  01813CE0  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ........
   *  01813CF0  00 00 00 00 00 00 F0 3F 00 00 00 00 00 00 F0 3F  ...㿰...㿰
   *
   *  01813C50   0C E8 69 00 10 C4 E4 03 00 00 00 00 00 00 00 00  i쐐Ϥ....
   *  01813C60   30 32 81 01 00 00 00 00 00 00 00 00 84 03 00 00  ㈰Ɓ....΄.
   *  01813C70   76 00 00 00 FF FF FF 00 00 00 00 00 00 00 00 00  v..ÿ....
   *  01813C80   00 00 00 00 26 00 00 00 00 00 00 00 00 00 00 00  ..&.....
   *  01813C90   06 00 00 00 03 00 00 00 28 5A 65 00 A0 31 81 01  ..娨eㆠƁ
   *  01813CA0   2C 00 00 00 43 00 00 00 00 01 01 00 BA C1 1E 77  ,.C.Ā솺眞
   *  01813CB0   35 FC 1C 77 20 FF 1C 77 20 24 34 0B 64 D5 68 00  ﰵ眜＠眜␠଴핤h
   */
  bool attachCaller(ulong addr);
  size_t textSize_;
  bool hookBefore(winhook::hook_stack *s)
  {
    static QString text_; // persistent storage, which makes this function not thread-safe
    textSize_ = 0;
    auto text = (LPCWSTR)s->stack[1]; // arg1
    if (!text || !*text)
      return true;

    if (::wcscmp(text, L"----/--/-- --:--") == 0)
      return true;

    textSize_ = ::wcslen(text);
    if (s->stack[1] == s->stack[13]) // for new games
      attachCaller(s->stack[12]);
    else if (s->stack[1] == s->stack[14]) // for old games
      attachCaller(s->stack[13]);
    //else // very old or very new games

    auto retaddr = s->stack[0];

    //int textStackIndex = -1;

    auto role = Engine::OtherRole;
    if (s->stack[2] < 0x100) { // new game, this value is mostly 0x1e
      //if (s->stack[1] == s->stack[13])
      //  textStackIndex = 13;
      // 004DACA7   8D8E 000A0000    LEA ECX,DWORD PTR DS:[ESI+0xA00]
      // 004DACAD   53               PUSH EBX
      // 004DACAE   FFD0             CALL EAX  ; jichi: called here
      // 004DACB0   8B8E 100A0000    MOV ECX,DWORD PTR DS:[ESI+0xA10]
      // 004DACB6   894424 14        MOV DWORD PTR SS:[ESP+0x14],EAX
      // 004DACBA   8B41 08          MOV EAX,DWORD PTR DS:[ECX+0x8]
      // 004DACBD   33FF             XOR EDI,EDI
      //if (*(WORD *)retaddr == 0x8e8b) { // 004DACB0   8B8E 100A0000    MOV ECX,DWORD PTR DS:[ESI+0xA10]
      role = Engine::ScenarioRole;
      enum : wchar_t { w_open = 0x3010, w_close = 0x3011 }; /* 【】 */
      if (text[0] == w_open && text[::wcslen(text) - 1] == w_close)
        role = Engine::NameRole;

    } else if (s->stack[3] < 0x100 // for old game
               || *(WORD *)retaddr == s2_mov_ecx_edi && *(WORD *)(retaddr - 5) == 0x52ff) { // for very old game
      // Sample game: お兄ちゃん、右手の使用を禁止します！ (old type)
      // 0055D207   8BCF             MOV ECX,EDI
      // 0055D209   897C24 34        MOV DWORD PTR SS:[ESP+0x34],EDI
      // 0055D20D   FF52 14          CALL DWORD PTR DS:[EDX+0x14]  ; jichi: called here
      // 0055D210   8BCF             MOV ECX,EDI   ; jichi: retaddr is here
      // 0055D212   894424 18        MOV DWORD PTR SS:[ESP+0x18],EAX

      // Sample game: キスと魔王と紅茶 (old type)
      // name:
      // 004DBFEC   50               PUSH EAX
      // 004DBFED   8BCF             MOV ECX,EDI
      // 004DBFEF   FF52 10          CALL DWORD PTR DS:[EDX+0x10]   ; jichi: called here
      // 004DBFF2   8B7424 7C        MOV ESI,DWORD PTR SS:[ESP+0x7C]
      // 004DBFF6   33DB             XOR EBX,EBX
      // 004DBFF8   3BF3             CMP ESI,EBX
      // 004DBFFA   74 4B            JE SHORT .004DC047
      // 004DBFFC   8BCF             MOV ECX,EDI
      // 004DBFFE   E8 9DA4FFFF      CALL .004D64A0
      // 004DC003   8BE8             MOV EBP,EAX
      // 004DC005   891E             MOV DWORD PTR DS:[ESI],EBX
      // 004DC007   85ED             TEST EBP,EBP
      //
      // Scenario:
      // 004B5207   8BCF             MOV ECX,EDI
      // 004B5209   897C24 14        MOV DWORD PTR SS:[ESP+0x14],EDI
      // 004B520D   FF52 10          CALL DWORD PTR DS:[EDX+0x10]   ; jichi: called here
      // 004B5210   8BCF             MOV ECX,EDI
      // 004B5212   894424 18        MOV DWORD PTR SS:[ESP+0x18],EAX
      // 004B5216   E8 85120200      CALL .004D64A0
      // 004B521B   33ED             XOR EBP,EBP
      role = s->stack[5] == 0 ? Engine::NameRole : Engine::ScenarioRole;
    }

    auto sig = Engine::hashThreadSignature(role, retaddr);
    text_ = EngineController::instance()->dispatchTextW(QString::fromWCharArray(text), role, sig);
    s->stack[1] = (ulong)text_.utf16(); // reset arg1
    //if (textStackIndex >= 0)
    //  s->stack[textStackIndex] = s->stack[1];
    return true;
  }

  bool hookAfterCaller(winhook::hook_stack *s)
  {
    if (textSize_)
      s->eax = textSize_;
    return true;
  }
  bool attachCaller(ulong addr)
  {
    static std::unordered_set<ulong> addresses_;
    if (addresses_.find(addr) != addresses_.end())
      return false;
    addresses_.insert(addr);
    bool ok = winhook::hook_before(addr, hookAfterCaller);
    DOUT(ok);
    return ok;
  }

} // namespace Private

/**
 *  Sample game: キスと魔王と紅茶 (old type)
 *
 *  FIXME: Text with ruby cannot be translated
 *
 *  There are two or three GetTextMetricsA.
 *  The caller of the first one is hijacked.
 *
 *  The beginning of the function in キスと魔王と紅茶:
 *  The text is the first argument.
 *  Both name/scenario can be hooked.
 *  Sometimes, the text is zero.
 *
 *  004D52AB   90               NOP
 *  004D52AC   90               NOP
 *  004D52AD   90               NOP
 *  004D52AE   90               NOP
 *  004D52AF   90               NOP
 *  004D52B0   55               PUSH EBP
 *  004D52B1   8BEC             MOV EBP,ESP
 *  004D52B3   6A FF            PUSH -0x1
 *  004D52B5   68 2D085300      PUSH .0053082D
 *  004D52BA   64:A1 00000000   MOV EAX,DWORD PTR FS:[0]
 *  004D52C0   50               PUSH EAX
 *  004D52C1   64:8925 00000000 MOV DWORD PTR FS:[0],ESP
 *  004D52C8   81EC 88010000    SUB ESP,0x188
 *  004D52CE   8B45 08          MOV EAX,DWORD PTR SS:[EBP+0x8]
 *  004D52D1   53               PUSH EBX
 *  004D52D2   56               PUSH ESI
 *  004D52D3   57               PUSH EDI
 *  004D52D4   33FF             XOR EDI,EDI
 *  004D52D6   8BF1             MOV ESI,ECX
 *  004D52D8   3BC7             CMP EAX,EDI
 *  004D52DA   89B5 40FFFFFF    MOV DWORD PTR SS:[EBP-0xC0],ESI
 *  004D52E0   75 15            JNZ SHORT .004D52F7
 *  004D52E2   33C0             XOR EAX,EAX
 *  004D52E4   8B4D F4          MOV ECX,DWORD PTR SS:[EBP-0xC]
 *  004D52E7   64:890D 00000000 MOV DWORD PTR FS:[0],ECX
 *  004D52EE   5F               POP EDI
 *  004D52EF   5E               POP ESI
 *  004D52F0   5B               POP EBX
 *  004D52F1   8BE5             MOV ESP,EBP
 *  004D52F3   5D               POP EBP
 *  004D52F4   C2 0400          RETN 0x4
 *  004D52F7   89BD 64FFFFFF    MOV DWORD PTR SS:[EBP-0x9C],EDI
 *  004D52FD   89BD 68FFFFFF    MOV DWORD PTR SS:[EBP-0x98],EDI
 *  004D5303   89BD 6CFFFFFF    MOV DWORD PTR SS:[EBP-0x94],EDI
 *  004D5309   C785 60FFFFFF 90>MOV DWORD PTR SS:[EBP-0xA0],.00565590
 *  004D5313   897D FC          MOV DWORD PTR SS:[EBP-0x4],EDI
 *  004D5316   897D A8          MOV DWORD PTR SS:[EBP-0x58],EDI
 *  004D5319   897D AC          MOV DWORD PTR SS:[EBP-0x54],EDI
 *  004D531C   897D B0          MOV DWORD PTR SS:[EBP-0x50],EDI
 *  004D531F   C745 A4 10565600 MOV DWORD PTR SS:[EBP-0x5C],.00565610
 *  004D5326   8A4E 52          MOV CL,BYTE PTR DS:[ESI+0x52]
 *  004D5329   C645 FC 01       MOV BYTE PTR SS:[EBP-0x4],0x1
 *  004D532D   84C9             TEST CL,CL
 *  004D532F   0F85 B7000000    JNZ .004D53EC
 *  004D5335   50               PUSH EAX
 *  004D5336   8D8D 60FFFFFF    LEA ECX,DWORD PTR SS:[EBP-0xA0]
 *  004D533C   E8 CF25F3FF      CALL .00407910
 *  004D5341   8B85 68FFFFFF    MOV EAX,DWORD PTR SS:[EBP-0x98]
 *  004D5347   8B4D B0          MOV ECX,DWORD PTR SS:[EBP-0x50]
 *  004D534A   8BBD 64FFFFFF    MOV EDI,DWORD PTR SS:[EBP-0x9C]
 *  004D5350   40               INC EAX
 *  004D5351   3BC1             CMP EAX,ECX
 *  004D5353   72 0B            JB SHORT .004D5360
 *  004D5355   8B55 A4          MOV EDX,DWORD PTR SS:[EBP-0x5C]
 *  004D5358   40               INC EAX
 *  004D5359   50               PUSH EAX
 *  004D535A   8D4D A4          LEA ECX,DWORD PTR SS:[EBP-0x5C]
 *  004D535D   FF52 10          CALL DWORD PTR DS:[EDX+0x10]
 *  004D5360   8A1F             MOV BL,BYTE PTR DS:[EDI]
 *  004D5362   8B45 A8          MOV EAX,DWORD PTR SS:[EBP-0x58]
 *  004D5365   47               INC EDI
 *  004D5366   8945 08          MOV DWORD PTR SS:[EBP+0x8],EAX
 *  004D5369   84DB             TEST BL,BL
 *  004D536B   885D BC          MOV BYTE PTR SS:[EBP-0x44],BL
 *  004D536E   74 3F            JE SHORT .004D53AF
 *  004D5370   8B4D BC          MOV ECX,DWORD PTR SS:[EBP-0x44]
 *  004D5373   51               PUSH ECX
 *  004D5374   FF15 40525600    CALL DWORD PTR DS:[0x565240]             ; kernel32.IsDBCSLeadByte
 *  004D537A   85C0             TEST EAX,EAX
 *  004D537C   74 16            JE SHORT .004D5394
 *  004D537E   8B45 08          MOV EAX,DWORD PTR SS:[EBP+0x8]
 *  004D5381   33D2             XOR EDX,EDX
 *  004D5383   8AF3             MOV DH,BL
 *  004D5385   83C0 02          ADD EAX,0x2
 *  004D5388   8A17             MOV DL,BYTE PTR DS:[EDI]
 *  004D538A   8945 08          MOV DWORD PTR SS:[EBP+0x8],EAX
 *  004D538D   66:8950 FE       MOV WORD PTR DS:[EAX-0x2],DX
 *  004D5391   47               INC EDI
 *  004D5392   EB 11            JMP SHORT .004D53A5
 *  004D5394   8B45 08          MOV EAX,DWORD PTR SS:[EBP+0x8]
 *  004D5397   66:33C9          XOR CX,CX
 *  004D539A   8ACB             MOV CL,BL
 *  004D539C   66:8908          MOV WORD PTR DS:[EAX],CX
 *  004D539F   83C0 02          ADD EAX,0x2
 *  004D53A2   8945 08          MOV DWORD PTR SS:[EBP+0x8],EAX
 *  004D53A5   8A1F             MOV BL,BYTE PTR DS:[EDI]
 *  004D53A7   47               INC EDI
 *  004D53A8   84DB             TEST BL,BL
 *  004D53AA   885D BC          MOV BYTE PTR SS:[EBP-0x44],BL
 *  004D53AD  ^75 C1            JNZ SHORT .004D5370
 *  004D53AF   8B55 08          MOV EDX,DWORD PTR SS:[EBP+0x8]
 *  004D53B2   33C0             XOR EAX,EAX
 *  004D53B4   66:C702 0000     MOV WORD PTR DS:[EDX],0x0
 *  004D53B9   8B55 A8          MOV EDX,DWORD PTR SS:[EBP-0x58]
 *  004D53BC   8B7D B0          MOV EDI,DWORD PTR SS:[EBP-0x50]
 *  004D53BF   66:3902          CMP WORD PTR DS:[EDX],AX
 *  004D53C2   74 10            JE SHORT .004D53D4
 *  004D53C4   8BCA             MOV ECX,EDX
 *  004D53C6   3BC7             CMP EAX,EDI
 *  004D53C8   73 0C            JNB SHORT .004D53D6
 *  004D53CA   83C1 02          ADD ECX,0x2
 *  004D53CD   40               INC EAX
 *  004D53CE   66:8339 00       CMP WORD PTR DS:[ECX],0x0
 *  004D53D2  ^75 F2            JNZ SHORT .004D53C6
 *  004D53D4   3BC7             CMP EAX,EDI
 *  004D53D6   1BC9             SBB ECX,ECX
 *  004D53D8   41               INC ECX
 *  004D53D9   2BC1             SUB EAX,ECX
 *  004D53DB   33FF             XOR EDI,EDI
 *  004D53DD   8945 AC          MOV DWORD PTR SS:[EBP-0x54],EAX
 *  004D53E0   66:C70442 0000   MOV WORD PTR DS:[EDX+EAX*2],0x0
 *  004D53E6   8B55 A8          MOV EDX,DWORD PTR SS:[EBP-0x58]
 *  004D53E9   8955 08          MOV DWORD PTR SS:[EBP+0x8],EDX
 *  004D53EC   8B46 04          MOV EAX,DWORD PTR DS:[ESI+0x4]
 *  004D53EF   897D 98          MOV DWORD PTR SS:[EBP-0x68],EDI
 *  004D53F2   3BC7             CMP EAX,EDI
 *  004D53F4   75 0A            JNZ SHORT .004D5400
 *  004D53F6   57               PUSH EDI
 *  004D53F7   FF15 88505600    CALL DWORD PTR DS:[0x565088]             ; gdi32.CreateCompatibleDC
 *  004D53FD   8946 04          MOV DWORD PTR DS:[ESI+0x4],EAX
 *  004D5400   8B46 08          MOV EAX,DWORD PTR DS:[ESI+0x8]
 *  004D5403   8B4E 04          MOV ECX,DWORD PTR DS:[ESI+0x4]
 *  004D5406   50               PUSH EAX
 *  004D5407   51               PUSH ECX
 *  004D5408   FF15 C4505600    CALL DWORD PTR DS:[0x5650C4]             ; gdi32.SelectObject
 *  004D540E   8985 44FFFFFF    MOV DWORD PTR SS:[EBP-0xBC],EAX
 *  004D5414   8B46 04          MOV EAX,DWORD PTR DS:[ESI+0x4]
 *  004D5417   8D95 6CFEFFFF    LEA EDX,DWORD PTR SS:[EBP-0x194]
 *  004D541D   897D BC          MOV DWORD PTR SS:[EBP-0x44],EDI
 *  004D5420   52               PUSH EDX
 *  004D5421   50               PUSH EAX
 *  004D5422   FF15 70505600    CALL DWORD PTR DS:[0x565070]             ; gdi32.GetTextMetricsA
 *  004D5428   85C0             TEST EAX,EAX
 *  004D542A   74 09            JE SHORT .004D5435
 *  004D542C   8B8D 74FEFFFF    MOV ECX,DWORD PTR SS:[EBP-0x18C]
 *  004D5432   894D BC          MOV DWORD PTR SS:[EBP-0x44],ECX
 *  004D5435   8B45 08          MOV EAX,DWORD PTR SS:[EBP+0x8]
 *  004D5438   33DB             XOR EBX,EBX
 *  004D543A   895D D8          MOV DWORD PTR SS:[EBP-0x28],EBX
 *  004D543D   66:3938          CMP WORD PTR DS:[EAX],DI
 *  004D5440   74 0C            JE SHORT .004D544E
 *  004D5442   83C0 02          ADD EAX,0x2
 *
 *  Sample game: お兄ちゃん、右手の使用を禁止します！ (old type)
 *  005C2E19   5B               POP EBX
 *  005C2E1A   83C4 10          ADD ESP,0x10
 *  005C2E1D   C2 0800          RETN 0x8    ; jichi: this value is used to distinguish different engine tyep
 *  005C2E20   55               PUSH EBP ; jichi: here
 *  005C2E21   8BEC             MOV EBP,ESP
 *  005C2E23   6A FF            PUSH -0x1
 *  005C2E25   68 2D886B00      PUSH .006B882D
 *  005C2E2A   64:A1 00000000   MOV EAX,DWORD PTR FS:[0]
 *  005C2E30   50               PUSH EAX
 *  005C2E31   64:8925 00000000 MOV DWORD PTR FS:[0],ESP
 *  005C2E38   81EC 84010000    SUB ESP,0x184
 *  005C2E3E   53               PUSH EBX
 *  005C2E3F   56               PUSH ESI
 *  005C2E40   8BF1             MOV ESI,ECX
 *  005C2E42   8B4D 08          MOV ECX,DWORD PTR SS:[EBP+0x8]
 *  005C2E45   33C0             XOR EAX,EAX
 *  005C2E47   57               PUSH EDI
 *  005C2E48   3BC8             CMP ECX,EAX
 *  005C2E4A   89B5 4CFFFFFF    MOV DWORD PTR SS:[EBP-0xB4],ESI
 *  005C2E50   75 13            JNZ SHORT .005C2E65
 *  005C2E52   8B4D F4          MOV ECX,DWORD PTR SS:[EBP-0xC]
 *  005C2E55   64:890D 00000000 MOV DWORD PTR FS:[0],ECX
 *  005C2E5C   5F               POP EDI
 *
 *  Sample game: プライマルハーツ (new type), 0x54bd80
 *
 *  0054BD78   5B               POP EBX
 *  0054BD79   83C4 10          ADD ESP,0x10
 *  0054BD7C   C2 0800          RETN 0x8
 *  0054BD7F   CC               INT3    ; jichi: this value is used to distinguish different engine type
 *  0054BD80   55               PUSH EBP    ; jichi: hooked here
 *  0054BD81   8BEC             MOV EBP,ESP
 *  0054BD83   83E4 F8          AND ESP,0xFFFFFFF8
 *  0054BD86   6A FF            PUSH -0x1
 *  0054BD88   68 5EC46000      PUSH .0060C45E
 *  0054BD8D   64:A1 00000000   MOV EAX,DWORD PTR FS:[0]
 *  0054BD93   50               PUSH EAX
 *  0054BD94   81EC 10010000    SUB ESP,0x110
 */
bool attach(ulong startAddress, ulong stopAddress)
{
  // 004D52AF   90               NOP
  // 004D52B0   55               PUSH EBP
  // 004D52B1   8BEC             MOV EBP,ESP
  // 004D52B3   6A FF            PUSH -0x1
  // 004D52B5   68 2D085300      PUSH .0053082D
  enum : ulong { ins = 0xec8b55 }; // beginning of the function
  ulong addr = MemDbg::findCallerAddress((ulong)::GetTextMetricsA, ins, startAddress, stopAddress);
  if (!addr)
    return false;
  //if (*(uint8_t *)(addr - 1) == s1_int3)
  //  Private::type_ = Private::NewType;
  //else // new type is int3 instead of nop
  //  Private::type_ = Private::OldType;
  ////DOUT(addr);
  //DOUT("type =" << Private::type_);

  //addr = 0x004dac20;
  return winhook::hook_before(addr, Private::hookBefore);

  //addr = 0x004da1df - 5;
  //return winhook::hook_both(addr, Private::hookBefore, Private::hookAfter);
}

} // namespace ScenarioHook

} // unnamed namespace

/** Public class */

bool CotophaEngine::attach()
{
  ulong startAddress, stopAddress;
  return Engine::getProcessMemoryRange(&startAddress, &stopAddress)
      && ScenarioHook::attach(startAddress, stopAddress);
}

// EOF
