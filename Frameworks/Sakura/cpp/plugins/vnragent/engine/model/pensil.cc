// pensil.cc
// 8/1/2015 jichi
#include "engine/model/pensil.h"
#include "engine/enginecontroller.h"
#include "engine/enginedef.h"
#include "engine/enginehash.h"
#include "engine/engineutil.h"
#include "hijack/hijackmanager.h"
#include "winhook/hookcode.h"
#include "memdbg/memsearch.h"
#include "winasm/winasmdef.h"
#include <qt_windows.h>
#include <QtCore/QRegExp>
#include <cstdint>

#define DEBUG "model/pensil"
#include "sakurakit/skdebug.h"

namespace { // unnamed
namespace ScenarioHook {
namespace Private {

  /**
   *  Sample game: はにつま
   *
   *  Scenario:
   *  0012FA1C   004139FA  RETURN to .004139FA from .0046AFF0
   *  0012FA20   0027D528
   *  0012FA24   001FD576
   *  0012FA28   00000146
   *  0012FA2C   11407B21
   *  0012FA30   75802EB2  user32.PeekMessageA
   *  0012FA34   00170566
   *  0012FA38   75803569  user32.DispatchMessageA
   *  0012FA3C   7580910F  user32.TranslateMessage
   *  0012FA40   00000023
   *  0012FA44   0000001C
   *  0012FA48   00000146
   *  0012FA4C   00000004
   *  0012FA50   00000001
   *  0012FA54   0000104C
   *  0012FA58   00030000
   *  0012FA5C   004B5F78  .004B5F78
   *  0012FA60   006C737C  .006C737C
   *  0012FA64   004B5F8C  .004B5F8C
   *  0012FA68   00000000
   *
   *  Name:
   *  0012FA18   004139B0  RETURN to .004139B0 from .0046AFF0
   *  0012FA1C   0023DA90
   *  0012FA20   004B6038  .004B6038
   *  0012FA24   001FD44C
   *  0012FA28   00000001
   *  0012FA2C   11407B21
   *  0012FA30   75802EB2  user32.PeekMessageA
   *  0012FA34   00170566
   *  0012FA38   75803569  user32.DispatchMessageA
   *  0012FA3C   7580910F  user32.TranslateMessage
   *  0012FA40   00000024
   *  0012FA44   0000001C
   *  0012FA48   0000017A
   *  0012FA4C   00000005
   *  0012FA50   00000001
   *  0012FA54   000010B0
   *  0012FA58   00030000
   *  0012FA5C   004B5F78  .004B5F78
   *  0012FA60   006C737C  .006C737C
   *  0012FA64   004B5F8C  .004B5F8C
   *  0012FA68   00000000
   *  0012FA6C   00000000
   *  0012FA70   00000000
   *
   *  Config:
   *  0012FA20   0040CE86  RETURN to .0040CE86 from .0046AFF0
   *  0012FA24   0D183308
   *  0012FA28   009549BF
   *  0012FA2C   32C69D99
   *  0012FA30   75802EB2  user32.PeekMessageA
   *  0012FA34   0050020E  .0050020E
   *  0012FA38   75803569  user32.DispatchMessageA
   *  0012FA3C   7580910F  user32.TranslateMessage
   *  0012FA40   00000006
   *  0012FA44   00000000
   *  0012FA48   00000000
   *  0012FA4C   00000000
   *  0012FA50   00839880
   *  0012FA54   0002E468
   *  0012FA58   00000000
   *  0012FA5C   004B5F78  .004B5F78
   *  0012FA60   01E9DE60
   *  0012FA64   004B5F8C  .004B5F8C
   *  0012FA68   00000000
   *  0012FA6C   00000000
   *
   *  Sample game: 大正×対称アリス
   *  Name:
   *  0012F9EC   00414628  RETURN to .00414628 from .0046C970
   *  0012F9F0   04641998
   *  0012F9F4   004B7078  .004B7078
   *  0012F9F8   00000001
   *  0012F9FC   B85ABBDB
   *  0012FA00   75802EB2  user32.PeekMessageA
   *  0012FA04   001F0BA4
   *  0012FA08   75803569  user32.DispatchMessageA
   *  0012FA0C   7580910F  user32.TranslateMessage
   *  0012FA10   00000000
   *  0012FA14   00000615
   *  0012FA18   00000665
   *  0012FA1C   00000010
   *  0012FA20   00000001
   *  0012FA24   740C6765  RETURN to uxtheme.740C6765 from user32.PtInRect
   *  0012FA28   00030000
   *  0012FA2C   004B6FB8  .004B6FB8
   *  0012FA30   000001A3
   *  0012FA34   004B6FCC  .004B6FCC
   *  0012FA38   740C672B  RETURN to uxtheme.740C672B from uxtheme.740C6742
   *
   *  Scenario:
   *  0012F9EC   00414677  RETURN to .00414677 from .0046C970
   *  0012F9F0   043DB388
   *  0012F9F4   00243E15
   *  0012F9F8   00000001
   *  0012F9FC   B85ABBDB
   *  0012FA00   75802EB2  user32.PeekMessageA
   *  0012FA04   001F0BA4
   *  0012FA08   75803569  user32.DispatchMessageA
   *  0012FA0C   7580910F  user32.TranslateMessage
   *  0012FA10   00000000
   *  0012FA14   00000615
   *  0012FA18   00000665
   *  0012FA1C   00000010
   *  0012FA20   00000001
   *  0012FA24   740C6765  RETURN to uxtheme.740C6765 from user32.PtInRect
   *  0012FA28   00030000
   */
  bool hookBefore(winhook::hook_stack *s)
  {
    static QByteArray data_;
    auto text = (LPCSTR)s->stack[2]; // arg2
    size_t size = ::strlen(text);

    auto role = Engine::OtherRole;
    if (text[size + 1] == 0 && text[size + 2] == 0) //|| s->stack[4] == 1)
      //if (size <= 0x10) // name should not be very long
      role = Engine::NameRole;
    else if (s->stack[3] < 0xfffff) // this value seems to be a counter for scenario, and pointer for other tet
      role = Engine::ScenarioRole;

    auto retaddr = s->stack[0];
    auto sig = Engine::hashThreadSignature(role, retaddr);
    data_ = EngineController::instance()->dispatchTextA(text, role, sig);
    s->stack[2] = (ulong)data_.constData();
    return true;
  }

} // namespace Private

/**
 *  Sample game: はにつま
 *
 *  Debugging method:
 *  1. Hook to GetGlyphOutlineA
 *  2. Find text in memory
 *     There are three matches. The static scenario text is found
 *  3. Looking for text on the stack
 *     The text is just above Windows Message calls on the stack.
 *
 *  Name/Scenario/Other texts can be translated.
 *  History cannot be translated.
 *
 *  Text in arg2.
 *
 *  0046AFE8   CC               INT3
 *  0046AFE9   CC               INT3
 *  0046AFEA   CC               INT3
 *  0046AFEB   CC               INT3
 *  0046AFEC   CC               INT3
 *  0046AFED   CC               INT3
 *  0046AFEE   CC               INT3
 *  0046AFEF   CC               INT3
 *  0046AFF0   83EC 10          SUB ESP,0x10
 *  0046AFF3   56               PUSH ESI
 *  0046AFF4   57               PUSH EDI
 *  0046AFF5   8B7C24 1C        MOV EDI,DWORD PTR SS:[ESP+0x1C]
 *  0046AFF9   85FF             TEST EDI,EDI
 *  0046AFFB   0F84 D6020000    JE .0046B2D7
 *  0046B001   8B7424 20        MOV ESI,DWORD PTR SS:[ESP+0x20]
 *  0046B005   85F6             TEST ESI,ESI
 *  0046B007   0F84 CA020000    JE .0046B2D7
 *  0046B00D   55               PUSH EBP
 *  0046B00E   33ED             XOR EBP,EBP
 *  0046B010   392D A8766C00    CMP DWORD PTR DS:[0x6C76A8],EBP
 *  0046B016   75 09            JNZ SHORT .0046B021
 *  0046B018   5D               POP EBP
 *  0046B019   5F               POP EDI
 *  0046B01A   33C0             XOR EAX,EAX
 *  0046B01C   5E               POP ESI
 *  0046B01D   83C4 10          ADD ESP,0x10
 *  0046B020   C3               RETN
 *  0046B021   8B47 24          MOV EAX,DWORD PTR DS:[EDI+0x24]
 *  0046B024   8B4F 28          MOV ECX,DWORD PTR DS:[EDI+0x28]
 *  0046B027   8B57 2C          MOV EDX,DWORD PTR DS:[EDI+0x2C]
 *  0046B02A   894424 0C        MOV DWORD PTR SS:[ESP+0xC],EAX
 *  0046B02E   8B47 30          MOV EAX,DWORD PTR DS:[EDI+0x30]
 *  0046B031   53               PUSH EBX
 *  0046B032   894C24 14        MOV DWORD PTR SS:[ESP+0x14],ECX
 *  0046B036   895424 18        MOV DWORD PTR SS:[ESP+0x18],EDX
 *  0046B03A   894424 1C        MOV DWORD PTR SS:[ESP+0x1C],EAX
 *  0046B03E   8A1E             MOV BL,BYTE PTR DS:[ESI]
 *  0046B040   84DB             TEST BL,BL
 *  0046B042   0F84 95000000    JE .0046B0DD
 *  0046B048   EB 06            JMP SHORT .0046B050
 *  0046B04A   8D9B 00000000    LEA EBX,DWORD PTR DS:[EBX]
 *  0046B050   0FB716           MOVZX EDX,WORD PTR DS:[ESI]
 *  0046B053   0FB7C2           MOVZX EAX,DX
 *  0046B056   3D 5C630000      CMP EAX,0x635C
 *  0046B05B   0F8F 93010000    JG .0046B1F4
 *  0046B061   0F84 2B010000    JE .0046B192
 *  0046B067   3D 5C4E0000      CMP EAX,0x4E5C
 *  0046B06C   0F8F DF000000    JG .0046B151
 *  0046B072   0F84 9E010000    JE .0046B216
 *  0046B078   3D 5C430000      CMP EAX,0x435C
 *  0046B07D   0F84 0F010000    JE .0046B192
 *  0046B083   3D 5C460000      CMP EAX,0x465C
 *  0046B088   0F84 80000000    JE .0046B10E
 *  0046B08E   3D 5C470000      CMP EAX,0x475C
 *  0046B093   0F85 CA010000    JNZ .0046B263
 *  0046B099   8A46 02          MOV AL,BYTE PTR DS:[ESI+0x2]
 *  0046B09C   83C6 02          ADD ESI,0x2
 *  0046B09F   33C9             XOR ECX,ECX
 *  0046B0A1   3C 39            CMP AL,0x39
 *  0046B0A3   77 17            JA SHORT .0046B0BC
 *  0046B0A5   3C 30            CMP AL,0x30
 *  0046B0A7   72 13            JB SHORT .0046B0BC
 *  0046B0A9   83C6 01          ADD ESI,0x1
 *  0046B0AC   0FB6D0           MOVZX EDX,AL
 *  0046B0AF   8A06             MOV AL,BYTE PTR DS:[ESI]
 *  0046B0B1   3C 39            CMP AL,0x39
 *  0046B0B3   8D0C89           LEA ECX,DWORD PTR DS:[ECX+ECX*4]
 *  0046B0B6   8D4C4A D0        LEA ECX,DWORD PTR DS:[EDX+ECX*2-0x30]
 *  0046B0BA  ^76 E9            JBE SHORT .0046B0A5
 *  0046B0BC   8D4424 10        LEA EAX,DWORD PTR SS:[ESP+0x10]
 *  0046B0C0   50               PUSH EAX
 *  0046B0C1   81C1 00FFFFFF    ADD ECX,-0x100
 *  0046B0C7   51               PUSH ECX
 *  0046B0C8   57               PUSH EDI
 *  0046B0C9   E8 92F1FFFF      CALL .0046A260
 *  0046B0CE   83C4 0C          ADD ESP,0xC
 *  0046B0D1   03E8             ADD EBP,EAX
 *  0046B0D3   8A1E             MOV BL,BYTE PTR DS:[ESI]
 *  0046B0D5   84DB             TEST BL,BL
 *  0046B0D7  ^0F85 73FFFFFF    JNZ .0046B050
 *  0046B0DD   F647 10 01       TEST BYTE PTR DS:[EDI+0x10],0x1
 *  0046B0E1   74 09            JE SHORT .0046B0EC
 *  0046B0E3   57               PUSH EDI
 *  0046B0E4   E8 F7DDFFFF      CALL .00468EE0
 *  0046B0E9   83C4 04          ADD ESP,0x4
 *  0046B0EC   F647 10 08       TEST BYTE PTR DS:[EDI+0x10],0x8
 *  0046B0F0   74 12            JE SHORT .0046B104
 *  0046B0F2   833D 98026C00 00 CMP DWORD PTR DS:[0x6C0298],0x0
 *  0046B0F9   74 09            JE SHORT .0046B104
 *  0046B0FB   57               PUSH EDI
 *  0046B0FC   E8 6FE4FFFF      CALL .00469570
 *  0046B101   83C4 04          ADD ESP,0x4
 *  0046B104   5B               POP EBX
 *  0046B105   8BC5             MOV EAX,EBP
 *  0046B107   5D               POP EBP
 *  0046B108   5F               POP EDI
 *  0046B109   5E               POP ESI
 *  0046B10A   83C4 10          ADD ESP,0x10
 *  0046B10D   C3               RETN
 *  0046B10E   8A46 02          MOV AL,BYTE PTR DS:[ESI+0x2]
 *  0046B111   83C6 02          ADD ESI,0x2
 *  0046B114   33C9             XOR ECX,ECX
 *  0046B116   3C 39            CMP AL,0x39
 *  0046B118   77 1D            JA SHORT .0046B137
 *  0046B11A   8D9B 00000000    LEA EBX,DWORD PTR DS:[EBX]
 *  0046B120   3C 30            CMP AL,0x30
 *  0046B122   72 13            JB SHORT .0046B137
 *  0046B124   83C6 01          ADD ESI,0x1
 *  0046B127   0FB6D0           MOVZX EDX,AL
 *  0046B12A   8A06             MOV AL,BYTE PTR DS:[ESI]
 *  0046B12C   3C 39            CMP AL,0x39
 *  0046B12E   8D0C89           LEA ECX,DWORD PTR DS:[ECX+ECX*4]
 *  0046B131   8D4C4A D0        LEA ECX,DWORD PTR DS:[EDX+ECX*2-0x30]
 *  0046B135  ^76 E9            JBE SHORT .0046B120
 *  0046B137   6A 01            PUSH 0x1
 *  0046B139   8B0C8D 580D6C00  MOV ECX,DWORD PTR DS:[ECX*4+0x6C0D58]
 *  0046B140   8D4424 14        LEA EAX,DWORD PTR SS:[ESP+0x14]
 *  0046B144   50               PUSH EAX
 *  0046B145   51               PUSH ECX
 *  0046B146   57               PUSH EDI
 *  0046B147   E8 84FBFFFF      CALL .0046ACD0
 *  0046B14C   83C4 10          ADD ESP,0x10
 *  0046B14F  ^EB 80            JMP SHORT .0046B0D1
 *  0046B151   3D 5C520000      CMP EAX,0x525C
 *  0046B156   0F84 BA000000    JE .0046B216
 *  0046B15C   3D 5C530000      CMP EAX,0x535C
 *  0046B161  ^0F84 32FFFFFF    JE .0046B099
 *  0046B167   3D 5C5C0000      CMP EAX,0x5C5C
 *  0046B16C   0F85 F1000000    JNZ .0046B263
 *  0046B172   8D5424 10        LEA EDX,DWORD PTR SS:[ESP+0x10]
 *  0046B176   52               PUSH EDX
 *  0046B177   6A 5C            PUSH 0x5C
 *  0046B179   57               PUSH EDI
 *  0046B17A   E8 81F3FFFF      CALL .0046A500
 *  0046B17F   83C4 0C          ADD ESP,0xC
 *  0046B182   85C0             TEST EAX,EAX
 *  0046B184   0F84 43010000    JE .0046B2CD
 *  0046B18A   83C6 01          ADD ESI,0x1
 *  0046B18D  ^E9 41FFFFFF      JMP .0046B0D3
 *  0046B192   33C9             XOR ECX,ECX
 *  0046B194   83C6 02          ADD ESI,0x2
 *  0046B197   8A06             MOV AL,BYTE PTR DS:[ESI]
 *  0046B199   3C 39            CMP AL,0x39
 *  0046B19B   77 14            JA SHORT .0046B1B1
 *  0046B19D   3C 30            CMP AL,0x30
 *  0046B19F   72 10            JB SHORT .0046B1B1
 *  0046B1A1   83C1 FD          ADD ECX,-0x3
 *  0046B1A4   0FB6C0           MOVZX EAX,AL
 *  0046B1A7   C1E1 04          SHL ECX,0x4
 *  0046B1AA   03C8             ADD ECX,EAX
 *  0046B1AC   83C6 01          ADD ESI,0x1
 *  0046B1AF  ^EB E6            JMP SHORT .0046B197
 *  0046B1B1   3C 46            CMP AL,0x46
 *  0046B1B3   77 13            JA SHORT .0046B1C8
 *  0046B1B5   3C 41            CMP AL,0x41
 *  0046B1B7   72 0F            JB SHORT .0046B1C8
 *  0046B1B9   0FB6D0           MOVZX EDX,AL
 *  0046B1BC   C1E1 04          SHL ECX,0x4
 *  0046B1BF   8D4C11 C9        LEA ECX,DWORD PTR DS:[ECX+EDX-0x37]
 *  0046B1C3   83C6 01          ADD ESI,0x1
 *  0046B1C6  ^EB CF            JMP SHORT .0046B197
 *  0046B1C8   3C 66            CMP AL,0x66
 *  0046B1CA   77 13            JA SHORT .0046B1DF
 *  0046B1CC   3C 61            CMP AL,0x61
 *  0046B1CE   72 0F            JB SHORT .0046B1DF
 *  0046B1D0   0FB6C0           MOVZX EAX,AL
 *  0046B1D3   C1E1 04          SHL ECX,0x4
 *  0046B1D6   8D4C01 A9        LEA ECX,DWORD PTR DS:[ECX+EAX-0x57]
 *  0046B1DA   83C6 01          ADD ESI,0x1
 *  0046B1DD  ^EB B8            JMP SHORT .0046B197
 *  0046B1DF   894C24 1C        MOV DWORD PTR SS:[ESP+0x1C],ECX
 *  0046B1E3   894C24 18        MOV DWORD PTR SS:[ESP+0x18],ECX
 *  0046B1E7   894C24 14        MOV DWORD PTR SS:[ESP+0x14],ECX
 *  0046B1EB   894C24 10        MOV DWORD PTR SS:[ESP+0x10],ECX
 *  0046B1EF  ^E9 DFFEFFFF      JMP .0046B0D3
 *  0046B1F4   3D 5C720000      CMP EAX,0x725C
 *  0046B1F9   7F 56            JG SHORT .0046B251
 *  0046B1FB   74 19            JE SHORT .0046B216
 *  0046B1FD   3D 5C660000      CMP EAX,0x665C
 *  0046B202   74 23            JE SHORT .0046B227
 *  0046B204   3D 5C670000      CMP EAX,0x675C
 *  0046B209  ^0F84 8AFEFFFF    JE .0046B099
 *  0046B20F   3D 5C6E0000      CMP EAX,0x6E5C
 *  0046B214   75 4D            JNZ SHORT .0046B263
 *  0046B216   57               PUSH EDI
 *  0046B217   E8 54DBFFFF      CALL .00468D70
 *  0046B21C   83C4 04          ADD ESP,0x4
 *  0046B21F   83C6 02          ADD ESI,0x2
 *  0046B222  ^E9 ACFEFFFF      JMP .0046B0D3
 *  0046B227   8A46 02          MOV AL,BYTE PTR DS:[ESI+0x2]
 *  0046B22A   83C6 02          ADD ESI,0x2
 *  0046B22D   33C9             XOR ECX,ECX
 *  0046B22F   3C 39            CMP AL,0x39
 *  0046B231   77 17            JA SHORT .0046B24A
 *  0046B233   3C 30            CMP AL,0x30
 *  0046B235   72 13            JB SHORT .0046B24A
 *  0046B237   83C6 01          ADD ESI,0x1
 *  0046B23A   0FB6D0           MOVZX EDX,AL
 *  0046B23D   8A06             MOV AL,BYTE PTR DS:[ESI]
 *  0046B23F   3C 39            CMP AL,0x39
 *  0046B241   8D0C89           LEA ECX,DWORD PTR DS:[ECX+ECX*4]
 *  0046B244   8D4C4A D0        LEA ECX,DWORD PTR DS:[EDX+ECX*2-0x30]
 *  0046B248  ^76 E9            JBE SHORT .0046B233
 *  0046B24A   6A 00            PUSH 0x0
 *  0046B24C  ^E9 E8FEFFFF      JMP .0046B139
 *  0046B251   3D 5C730000      CMP EAX,0x735C
 *  0046B256  ^0F84 3DFEFFFF    JE .0046B099
 *  0046B25C   3D 5C7B0000      CMP EAX,0x7B5C
 *  0046B261   74 49            JE SHORT .0046B2AC
 *  0046B263   52               PUSH EDX
 *  0046B264   E8 C7D5FFFF      CALL .00468830
 *  0046B269   83C4 04          ADD ESP,0x4
 *  0046B26C   85C0             TEST EAX,EAX
 *  0046B26E   74 1E            JE SHORT .0046B28E
 *  0046B270   8D4424 10        LEA EAX,DWORD PTR SS:[ESP+0x10]
 *  0046B274   50               PUSH EAX
 *  0046B275   52               PUSH EDX
 *  0046B276   57               PUSH EDI
 *  0046B277   E8 E4EFFFFF      CALL .0046A260
 *  0046B27C   83C4 0C          ADD ESP,0xC
 *  0046B27F   85C0             TEST EAX,EAX
 *  0046B281   74 4A            JE SHORT .0046B2CD
 *  0046B283   83C6 02          ADD ESI,0x2
 *  0046B286   83C5 01          ADD EBP,0x1
 *  0046B289  ^E9 45FEFFFF      JMP .0046B0D3
 *  0046B28E   8D4C24 10        LEA ECX,DWORD PTR SS:[ESP+0x10]
 *  0046B292   51               PUSH ECX
 *  0046B293   53               PUSH EBX
 *  0046B294   57               PUSH EDI
 *  0046B295   E8 66F2FFFF      CALL .0046A500
 *  0046B29A   83C4 0C          ADD ESP,0xC
 *  0046B29D   85C0             TEST EAX,EAX
 *  0046B29F   74 2C            JE SHORT .0046B2CD
 *  0046B2A1   83C6 01          ADD ESI,0x1
 *  0046B2A4   83C5 01          ADD EBP,0x1
 *  0046B2A7  ^E9 27FEFFFF      JMP .0046B0D3
 *  0046B2AC   8D5424 24        LEA EDX,DWORD PTR SS:[ESP+0x24]
 *  0046B2B0   52               PUSH EDX
 *  0046B2B1   83C6 02          ADD ESI,0x2
 *  0046B2B4   56               PUSH ESI
 *  0046B2B5   57               PUSH EDI
 *  0046B2B6   E8 F5F4FFFF      CALL .0046A7B0
 *  0046B2BB   8BF0             MOV ESI,EAX
 *  0046B2BD   83C4 0C          ADD ESP,0xC
 *  0046B2C0   85F6             TEST ESI,ESI
 *  0046B2C2   74 09            JE SHORT .0046B2CD
 *  0046B2C4   036C24 24        ADD EBP,DWORD PTR SS:[ESP+0x24]
 *  0046B2C8  ^E9 06FEFFFF      JMP .0046B0D3
 *  0046B2CD   5B               POP EBX
 *  0046B2CE   5D               POP EBP
 *  0046B2CF   5F               POP EDI
 *  0046B2D0   33C0             XOR EAX,EAX
 *  0046B2D2   5E               POP ESI
 *  0046B2D3   83C4 10          ADD ESP,0x10
 *  0046B2D6   C3               RETN
 *  0046B2D7   5F               POP EDI
 *  0046B2D8   33C0             XOR EAX,EAX
 *  0046B2DA   5E               POP ESI
 *  0046B2DB   83C4 10          ADD ESP,0x10
 *  0046B2DE   C3               RETN
 *  0046B2DF   CC               INT3
 *
 *  Sample game: 母子愛2 (2RM)
 *  0047120D   CC               INT3
 *  0047120E   CC               INT3
 *  0047120F   CC               INT3
 *  00471210   83EC 10          SUB ESP,0x10
 *  00471213   56               PUSH ESI
 *  00471214   57               PUSH EDI
 *  00471215   8B7C24 1C        MOV EDI,DWORD PTR SS:[ESP+0x1C]
 *  00471219   85FF             TEST EDI,EDI
 *  0047121B   0F84 98030000    JE oyakoai2.004715B9
 *  00471221   8B7424 20        MOV ESI,DWORD PTR SS:[ESP+0x20]
 *  00471225   85F6             TEST ESI,ESI
 *  00471227   0F84 8C030000    JE oyakoai2.004715B9
 *  0047122D   55               PUSH EBP
 *  0047122E   33ED             XOR EBP,EBP
 *  00471230   392D 48E16C00    CMP DWORD PTR DS:[0x6CE148],EBP
 *  00471236   75 09            JNZ SHORT oyakoai2.00471241
 *  00471238   5D               POP EBP
 *  00471239   5F               POP EDI
 *  0047123A   33C0             XOR EAX,EAX
 *  0047123C   5E               POP ESI
 *  0047123D   83C4 10          ADD ESP,0x10
 *  00471240   C3               RETN
 *  00471241   8B47 60          MOV EAX,DWORD PTR DS:[EDI+0x60]
 *  00471244   8B4F 64          MOV ECX,DWORD PTR DS:[EDI+0x64]
 *  00471247   8B57 68          MOV EDX,DWORD PTR DS:[EDI+0x68]
 *  0047124A   894424 0C        MOV DWORD PTR SS:[ESP+0xC],EAX
 *  0047124E   8B47 6C          MOV EAX,DWORD PTR DS:[EDI+0x6C]
 *  00471251   894424 18        MOV DWORD PTR SS:[ESP+0x18],EAX
 *  00471255   8B47 4C          MOV EAX,DWORD PTR DS:[EDI+0x4C]
 *  00471258   25 00F00000      AND EAX,0xF000
 *  0047125D   3D 00100000      CMP EAX,0x1000
 *  00471262   894C24 10        MOV DWORD PTR SS:[ESP+0x10],ECX
 *  00471266   895424 14        MOV DWORD PTR SS:[ESP+0x14],EDX
 *  0047126A   74 26            JE SHORT oyakoai2.00471292
 *  0047126C   3D 00200000      CMP EAX,0x2000
 *  00471271   74 13            JE SHORT oyakoai2.00471286
 *  00471273   3D 00300000      CMP EAX,0x3000
 *  00471278   75 30            JNZ SHORT oyakoai2.004712AA
 *  0047127A   8D4C24 0C        LEA ECX,DWORD PTR SS:[ESP+0xC]
 *  0047127E   51               PUSH ECX
 *  0047127F   68 81770000      PUSH 0x7781
 *  00471284   EB 16            JMP SHORT oyakoai2.0047129C
 *  00471286   8D5424 0C        LEA EDX,DWORD PTR SS:[ESP+0xC]
 *  0047128A   52               PUSH EDX
 *  0047128B   68 81750000      PUSH 0x7581
 *  00471290   EB 0A            JMP SHORT oyakoai2.0047129C
 *  00471292   8D4424 0C        LEA EAX,DWORD PTR SS:[ESP+0xC]
 *  00471296   50               PUSH EAX
 *  00471297   68 81790000      PUSH 0x7981
 *  0047129C   57               PUSH EDI
 *  0047129D   E8 3EF0FFFF      CALL oyakoai2.004702E0
 *  004712A2   83C4 0C          ADD ESP,0xC
 *  004712A5   BD 02000000      MOV EBP,0x2
 *  004712AA   53               PUSH EBX
 *  004712AB   8A1E             MOV BL,BYTE PTR DS:[ESI]
 *  004712AD   84DB             TEST BL,BL
 *  004712AF   0F84 93000000    JE oyakoai2.00471348
 *  004712B5   0FB716           MOVZX EDX,WORD PTR DS:[ESI]
 *  004712B8   0FB7C2           MOVZX EAX,DX
 *  004712BB   3D 5C630000      CMP EAX,0x635C
 *  004712C0   0F8F A7010000    JG oyakoai2.0047146D
 *  004712C6   0F84 39010000    JE oyakoai2.00471405
 *  004712CC   3D 5C4E0000      CMP EAX,0x4E5C
 *  004712D1   0F8F ED000000    JG oyakoai2.004713C4
 *  004712D7   0F84 B2010000    JE oyakoai2.0047148F
 *  004712DD   3D 5C430000      CMP EAX,0x435C
 *  004712E2   0F84 1D010000    JE oyakoai2.00471405
 *  004712E8   3D 5C460000      CMP EAX,0x465C
 *  004712ED   0F84 8D000000    JE oyakoai2.00471380
 *  004712F3   3D 5C470000      CMP EAX,0x475C
 *  004712F8   0F85 E2010000    JNZ oyakoai2.004714E0
 *  004712FE   8A46 02          MOV AL,BYTE PTR DS:[ESI+0x2]
 *  00471301   83C6 02          ADD ESI,0x2
 *  00471304   33C9             XOR ECX,ECX
 *  00471306   3C 39            CMP AL,0x39
 *  00471308   77 1D            JA SHORT oyakoai2.00471327
 *  0047130A   8D9B 00000000    LEA EBX,DWORD PTR DS:[EBX]
 *  00471310   3C 30            CMP AL,0x30
 *  00471312   72 13            JB SHORT oyakoai2.00471327
 *  00471314   83C6 01          ADD ESI,0x1
 *  00471317   0FB6D0           MOVZX EDX,AL
 *  0047131A   8A06             MOV AL,BYTE PTR DS:[ESI]
 *  0047131C   3C 39            CMP AL,0x39
 *  0047131E   8D0C89           LEA ECX,DWORD PTR DS:[ECX+ECX*4]
 *  00471321   8D4C4A D0        LEA ECX,DWORD PTR DS:[EDX+ECX*2-0x30]
 *  00471325  ^76 E9            JBE SHORT oyakoai2.00471310
 *  00471327   8D4424 10        LEA EAX,DWORD PTR SS:[ESP+0x10]
 *  0047132B   50               PUSH EAX
 *  0047132C   81C1 00FFFFFF    ADD ECX,-0x100
 *  00471332   51               PUSH ECX
 *  00471333   57               PUSH EDI
 *  00471334   E8 A7EFFFFF      CALL oyakoai2.004702E0
 *  00471339   83C4 0C          ADD ESP,0xC
 *  0047133C   03E8             ADD EBP,EAX
 *  0047133E   8A1E             MOV BL,BYTE PTR DS:[ESI]
 *  00471340   84DB             TEST BL,BL
 *  00471342  ^0F85 6DFFFFFF    JNZ oyakoai2.004712B5
 *  00471348   8B47 4C          MOV EAX,DWORD PTR DS:[EDI+0x4C]
 *  0047134B   25 00F00000      AND EAX,0xF000
 *  00471350   3D 00100000      CMP EAX,0x1000
 *  00471355   0F84 05020000    JE oyakoai2.00471560
 *  0047135B   3D 00200000      CMP EAX,0x2000
 *  00471360   0F84 EE010000    JE oyakoai2.00471554
 *  00471366   3D 00300000      CMP EAX,0x3000
 *  0047136B   0F85 05020000    JNZ oyakoai2.00471576
 *  00471371   8D4C24 10        LEA ECX,DWORD PTR SS:[ESP+0x10]
 *  00471375   51               PUSH ECX
 *  00471376   68 81780000      PUSH 0x7881
 *  0047137B   E9 EA010000      JMP oyakoai2.0047156A
 *  00471380   8A46 02          MOV AL,BYTE PTR DS:[ESI+0x2]
 *  00471383   83C6 02          ADD ESI,0x2
 *  00471386   33C9             XOR ECX,ECX
 *  00471388   3C 39            CMP AL,0x39
 *  0047138A   77 1B            JA SHORT oyakoai2.004713A7
 *  0047138C   8D6424 00        LEA ESP,DWORD PTR SS:[ESP]
 *  00471390   3C 30            CMP AL,0x30
 *  00471392   72 13            JB SHORT oyakoai2.004713A7
 *  00471394   83C6 01          ADD ESI,0x1
 *  00471397   0FB6D0           MOVZX EDX,AL
 *  0047139A   8A06             MOV AL,BYTE PTR DS:[ESI]
 *  0047139C   3C 39            CMP AL,0x39
 *  0047139E   8D0C89           LEA ECX,DWORD PTR DS:[ECX+ECX*4]
 *  004713A1   8D4C4A D0        LEA ECX,DWORD PTR DS:[EDX+ECX*2-0x30]
 *  004713A5  ^76 E9            JBE SHORT oyakoai2.00471390
 *  004713A7   6A 01            PUSH 0x1
 *  004713A9   8B0C8D E8776C00  MOV ECX,DWORD PTR DS:[ECX*4+0x6C77E8]
 *  004713B0   8D4424 14        LEA EAX,DWORD PTR SS:[ESP+0x14]
 *  004713B4   50               PUSH EAX
 *  004713B5   51               PUSH ECX
 *  004713B6   57               PUSH EDI
 *  004713B7   E8 34FBFFFF      CALL oyakoai2.00470EF0
 *  004713BC   83C4 10          ADD ESP,0x10
 *  004713BF  ^E9 78FFFFFF      JMP oyakoai2.0047133C
 *  004713C4   3D 5C520000      CMP EAX,0x525C
 *  004713C9   0F84 C0000000    JE oyakoai2.0047148F
 *  004713CF   3D 5C530000      CMP EAX,0x535C
 *  004713D4  ^0F84 24FFFFFF    JE oyakoai2.004712FE
 *  004713DA   3D 5C5C0000      CMP EAX,0x5C5C
 *  004713DF   0F85 FB000000    JNZ oyakoai2.004714E0
 *  004713E5   8D5424 10        LEA EDX,DWORD PTR SS:[ESP+0x10]
 *  004713E9   52               PUSH EDX
 *  004713EA   6A 5C            PUSH 0x5C
 *  004713EC   57               PUSH EDI
 *  004713ED   E8 2EF2FFFF      CALL oyakoai2.00470620
 *  004713F2   83C4 0C          ADD ESP,0xC
 *  004713F5   85C0             TEST EAX,EAX
 *  004713F7   0F84 4D010000    JE oyakoai2.0047154A
 *  004713FD   83C6 01          ADD ESI,0x1
 *  00471400  ^E9 39FFFFFF      JMP oyakoai2.0047133E
 *  00471405   33C9             XOR ECX,ECX
 *  00471407   83C6 02          ADD ESI,0x2
 *  0047140A   8D9B 00000000    LEA EBX,DWORD PTR DS:[EBX]
 *  00471410   8A06             MOV AL,BYTE PTR DS:[ESI]
 *  00471412   3C 39            CMP AL,0x39
 *  00471414   77 14            JA SHORT oyakoai2.0047142A
 *  00471416   3C 30            CMP AL,0x30
 *  00471418   72 10            JB SHORT oyakoai2.0047142A
 *  0047141A   83C1 FD          ADD ECX,-0x3
 *  0047141D   0FB6C0           MOVZX EAX,AL
 *  00471420   C1E1 04          SHL ECX,0x4
 *  00471423   03C8             ADD ECX,EAX
 *  00471425   83C6 01          ADD ESI,0x1
 *  00471428  ^EB E6            JMP SHORT oyakoai2.00471410
 *  0047142A   3C 46            CMP AL,0x46
 *  0047142C   77 13            JA SHORT oyakoai2.00471441
 *  0047142E   3C 41            CMP AL,0x41
 *  00471430   72 0F            JB SHORT oyakoai2.00471441
 *  00471432   0FB6D0           MOVZX EDX,AL
 *  00471435   C1E1 04          SHL ECX,0x4
 *  00471438   8D4C11 C9        LEA ECX,DWORD PTR DS:[ECX+EDX-0x37]
 *  0047143C   83C6 01          ADD ESI,0x1
 *  0047143F  ^EB CF            JMP SHORT oyakoai2.00471410
 *  00471441   3C 66            CMP AL,0x66
 *  00471443   77 13            JA SHORT oyakoai2.00471458
 *  00471445   3C 61            CMP AL,0x61
 *  00471447   72 0F            JB SHORT oyakoai2.00471458
 *  00471449   0FB6C0           MOVZX EAX,AL
 *  0047144C   C1E1 04          SHL ECX,0x4
 *  0047144F   8D4C01 A9        LEA ECX,DWORD PTR DS:[ECX+EAX-0x57]
 *  00471453   83C6 01          ADD ESI,0x1
 *  00471456  ^EB B8            JMP SHORT oyakoai2.00471410
 *  00471458   894C24 1C        MOV DWORD PTR SS:[ESP+0x1C],ECX
 *  0047145C   894C24 18        MOV DWORD PTR SS:[ESP+0x18],ECX
 *  00471460   894C24 14        MOV DWORD PTR SS:[ESP+0x14],ECX
 *  00471464   894C24 10        MOV DWORD PTR SS:[ESP+0x10],ECX
 *  00471468  ^E9 D1FEFFFF      JMP oyakoai2.0047133E
 *  0047146D   3D 5C720000      CMP EAX,0x725C
 *  00471472   7F 5A            JG SHORT oyakoai2.004714CE
 *  00471474   74 19            JE SHORT oyakoai2.0047148F
 *  00471476   3D 5C660000      CMP EAX,0x665C
 *  0047147B   74 23            JE SHORT oyakoai2.004714A0
 *  0047147D   3D 5C670000      CMP EAX,0x675C
 *  00471482  ^0F84 76FEFFFF    JE oyakoai2.004712FE
 *  00471488   3D 5C6E0000      CMP EAX,0x6E5C
 *  0047148D   75 51            JNZ SHORT oyakoai2.004714E0
 *  0047148F   57               PUSH EDI
 *  00471490   E8 BBD2FFFF      CALL oyakoai2.0046E750
 *  00471495   83C4 04          ADD ESP,0x4
 *  00471498   83C6 02          ADD ESI,0x2
 *  0047149B  ^E9 9EFEFFFF      JMP oyakoai2.0047133E
 *  004714A0   8A46 02          MOV AL,BYTE PTR DS:[ESI+0x2]
 *  004714A3   83C6 02          ADD ESI,0x2
 *  004714A6   33C9             XOR ECX,ECX
 *  004714A8   3C 39            CMP AL,0x39
 *  004714AA   77 1B            JA SHORT oyakoai2.004714C7
 *  004714AC   8D6424 00        LEA ESP,DWORD PTR SS:[ESP]
 *  004714B0   3C 30            CMP AL,0x30
 *  004714B2   72 13            JB SHORT oyakoai2.004714C7
 *  004714B4   83C6 01          ADD ESI,0x1
 *  004714B7   0FB6D0           MOVZX EDX,AL
 *  004714BA   8A06             MOV AL,BYTE PTR DS:[ESI]
 *  004714BC   3C 39            CMP AL,0x39
 *  004714BE   8D0C89           LEA ECX,DWORD PTR DS:[ECX+ECX*4]
 *  004714C1   8D4C4A D0        LEA ECX,DWORD PTR DS:[EDX+ECX*2-0x30]
 *  004714C5  ^76 E9            JBE SHORT oyakoai2.004714B0
 *  004714C7   6A 00            PUSH 0x0
 *  004714C9  ^E9 DBFEFFFF      JMP oyakoai2.004713A9
 *  004714CE   3D 5C730000      CMP EAX,0x735C
 *  004714D3  ^0F84 25FEFFFF    JE oyakoai2.004712FE
 *  004714D9   3D 5C7B0000      CMP EAX,0x7B5C
 *  004714DE   74 49            JE SHORT oyakoai2.00471529
 *  004714E0   52               PUSH EDX
 *  004714E1   E8 5ACDFFFF      CALL oyakoai2.0046E240
 *  004714E6   83C4 04          ADD ESP,0x4
 *  004714E9   85C0             TEST EAX,EAX
 *  004714EB   74 1E            JE SHORT oyakoai2.0047150B
 *  004714ED   8D4424 10        LEA EAX,DWORD PTR SS:[ESP+0x10]
 *  004714F1   50               PUSH EAX
 *  004714F2   52               PUSH EDX
 *  004714F3   57               PUSH EDI
 *  004714F4   E8 E7EDFFFF      CALL oyakoai2.004702E0
 *  004714F9   83C4 0C          ADD ESP,0xC
 *  004714FC   85C0             TEST EAX,EAX
 *  004714FE   74 4A            JE SHORT oyakoai2.0047154A
 *  00471500   83C6 02          ADD ESI,0x2
 *  00471503   83C5 01          ADD EBP,0x1
 *  00471506  ^E9 33FEFFFF      JMP oyakoai2.0047133E
 *  0047150B   8D4C24 10        LEA ECX,DWORD PTR SS:[ESP+0x10]
 *  0047150F   51               PUSH ECX
 *  00471510   53               PUSH EBX
 *  00471511   57               PUSH EDI
 *  00471512   E8 09F1FFFF      CALL oyakoai2.00470620
 *  00471517   83C4 0C          ADD ESP,0xC
 *  0047151A   85C0             TEST EAX,EAX
 *  0047151C   74 2C            JE SHORT oyakoai2.0047154A
 *  0047151E   83C6 01          ADD ESI,0x1
 *  00471521   83C5 01          ADD EBP,0x1
 *  00471524  ^E9 15FEFFFF      JMP oyakoai2.0047133E
 *  00471529   8D5424 24        LEA EDX,DWORD PTR SS:[ESP+0x24]
 *  0047152D   52               PUSH EDX
 *  0047152E   83C6 02          ADD ESI,0x2
 *  00471531   56               PUSH ESI
 *  00471532   57               PUSH EDI
 *  00471533   E8 38F4FFFF      CALL oyakoai2.00470970
 *  00471538   8BF0             MOV ESI,EAX
 *  0047153A   83C4 0C          ADD ESP,0xC
 *  0047153D   85F6             TEST ESI,ESI
 *  0047153F   74 09            JE SHORT oyakoai2.0047154A
 *  00471541   036C24 24        ADD EBP,DWORD PTR SS:[ESP+0x24]
 *  00471545  ^E9 F4FDFFFF      JMP oyakoai2.0047133E
 *  0047154A   5B               POP EBX
 *  0047154B   5D               POP EBP
 *  0047154C   5F               POP EDI
 *  0047154D   33C0             XOR EAX,EAX
 *  0047154F   5E               POP ESI
 *  00471550   83C4 10          ADD ESP,0x10
 *  00471553   C3               RETN
 *  00471554   8D5424 10        LEA EDX,DWORD PTR SS:[ESP+0x10]
 *  00471558   52               PUSH EDX
 *  00471559   68 81760000      PUSH 0x7681
 *  0047155E   EB 0A            JMP SHORT oyakoai2.0047156A
 *  00471560   8D4424 10        LEA EAX,DWORD PTR SS:[ESP+0x10]
 *  00471564   50               PUSH EAX
 *  00471565   68 817A0000      PUSH 0x7A81
 *  0047156A   57               PUSH EDI
 *  0047156B   E8 70EDFFFF      CALL oyakoai2.004702E0
 *  00471570   83C4 0C          ADD ESP,0xC
 *  00471573   83C5 02          ADD EBP,0x2
 *  00471576   F647 4C 01       TEST BYTE PTR DS:[EDI+0x4C],0x1
 *  0047157A   74 09            JE SHORT oyakoai2.00471585
 *  0047157C   57               PUSH EDI
 *  0047157D   E8 4ED3FFFF      CALL oyakoai2.0046E8D0
 *  00471582   83C4 04          ADD ESP,0x4
 *  00471585   F747 4C 00010000 TEST DWORD PTR DS:[EDI+0x4C],0x100
 *  0047158C   74 09            JE SHORT oyakoai2.00471597
 *  0047158E   57               PUSH EDI
 *  0047158F   E8 4CD6FFFF      CALL oyakoai2.0046EBE0
 *  00471594   83C4 04          ADD ESP,0x4
 *  00471597   F647 4C 08       TEST BYTE PTR DS:[EDI+0x4C],0x8
 *  0047159B   74 12            JE SHORT oyakoai2.004715AF
 *  0047159D   833D 306D6C00 00 CMP DWORD PTR DS:[0x6C6D30],0x0
 *  004715A4   74 09            JE SHORT oyakoai2.004715AF
 *  004715A6   57               PUSH EDI
 *  004715A7   E8 C4DCFFFF      CALL oyakoai2.0046F270
 *  004715AC   83C4 04          ADD ESP,0x4
 *  004715AF   5B               POP EBX
 *  004715B0   8BC5             MOV EAX,EBP
 *  004715B2   5D               POP EBP
 *  004715B3   5F               POP EDI
 *  004715B4   5E               POP ESI
 *  004715B5   83C4 10          ADD ESP,0x10
 *  004715B8   C3               RETN
 *  004715B9   5F               POP EDI
 *  004715BA   33C0             XOR EAX,EAX
 *  004715BC   5E               POP ESI
 *  004715BD   83C4 10          ADD ESP,0x10
 *  004715C0   C3               RETN
 *  004715C1   CC               INT3
 *  004715C2   CC               INT3
 *  004715C3   CC               INT3
 *  004715C4   CC               INT3
 *  004715C5   CC               INT3
 *  004715C6   CC               INT3
 *  004715C7   CC               INT3
 *  004715C8   CC               INT3
 *  004715C9   CC               INT3
 *  004715CA   CC               INT3
 *  004715CB   CC               INT3
 *  004715CC   CC               INT3
 *  004715CD   CC               INT3
 *  004715CE   CC               INT3
 *  004715CF   CC               INT3
 */
bool attach(ulong startAddress, ulong stopAddress)
{
  const uint8_t bytes[] = {
    0x75, 0x09,      // 00471236   75 09            jnz short oyakoai2.00471241
    0x5d,            // 00471238   5d               pop ebp
    0x5f,            // 00471239   5f               pop edi
    0x33,0xc0,       // 0047123a   33c0             xor eax,eax
    0x5e,            // 0047123c   5e               pop esi
    0x83,0xc4, 0x10, // 0047123d   83c4 10          add esp,0x10
    0xc3             // 00471240   c3               retn
  };
  ulong addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  return winhook::hook_before(addr, Private::hookBefore);
}

} // namespace ScenarioHook

namespace OtherHook {
namespace Private {

  bool hookBefore(winhook::hook_stack *s)
  {
    static QByteArray data_;
    auto text = (LPCSTR)s->stack[1]; // arg1
    enum { role = Engine::ChoiceRole };
    auto retaddr = s->stack[0];
    auto sig = Engine::hashThreadSignature(role, retaddr);
    data_ = EngineController::instance()->dispatchTextA(text, role, sig);
    s->stack[1] = (ulong)data_.constData();
    return true;
  }

} // namespace Private

/**
 *  Sample game: 母子愛2 (2RM)
 *
 *  Debugging method:
 *  1. Hook to GetGlyphOutlineA
 *  2. Looking for text on the stack
 *     The text is just above Windows Message calls on the stack.
 *
 *  0012FAAC   00808080
 *  0012FAB0   00808080
 *  0012FAB4   00808080
 *  0012FAB8   00808080
 *  0012FABC   00408AB9  RETURN to oyakoai2.00408AB9 from oyakoai2.004250F0
 *  0012FAC0   00246314 ; jichi: choice text
 *  0012FAC4   00000ECC
 *  0012FAC8   F568A74D
 *  0012FACC   763B286F  user32.GetMessageA
 *  0012FAD0   00400344  oyakoai2.00400344
 *  0012FAD4   00400000  oyakoai2.00400000
 *  0012FAD8   00000000
 *  0012FADC   0000001C
 *
 *  004250EC   CC               INT3
 *  004250ED   CC               INT3
 *  004250EE   CC               INT3
 *  004250EF   CC               INT3
 *  004250F0   83EC 28          SUB ESP,0x28
 *  004250F3   56               PUSH ESI
 *  004250F4   8BF1             MOV ESI,ECX
 *  004250F6   837E 14 00       CMP DWORD PTR DS:[ESI+0x14],0x0
 *  004250FA   75 09            JNZ SHORT oyakoai2.00425105
 *  004250FC   33C0             XOR EAX,EAX
 *  004250FE   5E               POP ESI
 *  004250FF   83C4 28          ADD ESP,0x28
 *  00425102   C2 0800          RETN 0x8
 *  00425105   8B86 F81F0000    MOV EAX,DWORD PTR DS:[ESI+0x1FF8]
 *  0042510B   3D FE000000      CMP EAX,0xFE
 *  00425110  ^74 EA            JE SHORT oyakoai2.004250FC
 *  00425112   8B4C24 34        MOV ECX,DWORD PTR SS:[ESP+0x34]
 *  00425116   57               PUSH EDI
 *  00425117   8B7C24 34        MOV EDI,DWORD PTR SS:[ESP+0x34]
 *  0042511B   897C86 18        MOV DWORD PTR DS:[ESI+EAX*4+0x18],EDI
 *  0042511F   8B86 F81F0000    MOV EAX,DWORD PTR DS:[ESI+0x1FF8]
 *  00425125   6A 08            PUSH 0x8
 *  00425127   898C86 04140000  MOV DWORD PTR DS:[ESI+EAX*4+0x1404],ECX
 *  0042512E   E8 5BC10500      CALL oyakoai2.0048128E
 *  00425133   83C4 04          ADD ESP,0x4
 *  00425136   85C0             TEST EAX,EAX
 *  00425138   74 09            JE SHORT oyakoai2.00425143
 *  0042513A   8BC8             MOV ECX,EAX
 *  0042513C   E8 1FC9FFFF      CALL oyakoai2.00421A60
 *  00425141   EB 02            JMP SHORT oyakoai2.00425145
 *  00425143   33C0             XOR EAX,EAX
 *  00425145   8B96 F81F0000    MOV EDX,DWORD PTR DS:[ESI+0x1FF8]
 *  0042514B   898496 FC1B0000  MOV DWORD PTR DS:[ESI+EDX*4+0x1BFC],EAX
 *  00425152   8B8E F81F0000    MOV ECX,DWORD PTR DS:[ESI+0x1FF8]
 *  00425158   83BC8E FC1B0000 >CMP DWORD PTR DS:[ESI+ECX*4+0x1BFC],0x0
 *  00425160   75 0A            JNZ SHORT oyakoai2.0042516C
 *  00425162   5F               POP EDI
 *  00425163   33C0             XOR EAX,EAX
 *  00425165   5E               POP ESI
 *  00425166   83C4 28          ADD ESP,0x28
 *  00425169   C2 0800          RETN 0x8
 *  0042516C   8B86 F4270000    MOV EAX,DWORD PTR DS:[ESI+0x27F4]
 *  00425172   85C0             TEST EAX,EAX
 *  00425174   74 26            JE SHORT oyakoai2.0042519C
 *  00425176   6A 00            PUSH 0x0
 *  00425178   6A 00            PUSH 0x0
 *  0042517A   6A 1C            PUSH 0x1C
 *  0042517C   6A 00            PUSH 0x0
 *  0042517E   50               PUSH EAX
 *  0042517F   E8 3C6C0100      CALL oyakoai2.0043BDC0
 *  00425184   50               PUSH EAX
 *  00425185   E8 C6E30000      CALL oyakoai2.00433550
 *  0042518A   8B8E F81F0000    MOV ECX,DWORD PTR DS:[ESI+0x1FF8]
 *  00425190   83C4 18          ADD ESP,0x18
 *  00425193   89848E FC1F0000  MOV DWORD PTR DS:[ESI+ECX*4+0x1FFC],EAX
 *  0042519A   EB 0B            JMP SHORT oyakoai2.004251A7
 *  0042519C   C7848E FC1F0000 >MOV DWORD PTR DS:[ESI+ECX*4+0x1FFC],0x0
 *  004251A7   8B96 F8270000    MOV EDX,DWORD PTR DS:[ESI+0x27F8]
 *  004251AD   6A 00            PUSH 0x0
 *  004251AF   6A 00            PUSH 0x0
 *  004251B1   6A 1C            PUSH 0x1C
 *  004251B3   6A 00            PUSH 0x0
 *  004251B5   52               PUSH EDX
 *  004251B6   E8 056C0100      CALL oyakoai2.0043BDC0
 *  004251BB   50               PUSH EAX
 *  004251BC   E8 8FE30000      CALL oyakoai2.00433550
 *  004251C1   8B8E F81F0000    MOV ECX,DWORD PTR DS:[ESI+0x1FF8]
 *  004251C7   89848E F8230000  MOV DWORD PTR DS:[ESI+ECX*4+0x23F8],EAX
 *  004251CE   8B96 F81F0000    MOV EDX,DWORD PTR DS:[ESI+0x1FF8]
 *  004251D4   8B8496 FC1F0000  MOV EAX,DWORD PTR DS:[ESI+EDX*4+0x1FFC]
 *  004251DB   6A 04            PUSH 0x4
 *  004251DD   6A 00            PUSH 0x0
 *  004251DF   50               PUSH EAX
 *  004251E0   E8 2BE20000      CALL oyakoai2.00433410
 *  004251E5   8B8E F81F0000    MOV ECX,DWORD PTR DS:[ESI+0x1FF8]
 *  004251EB   8B948E F8230000  MOV EDX,DWORD PTR DS:[ESI+ECX*4+0x23F8]
 *  004251F2   6A 04            PUSH 0x4
 *  004251F4   6A 00            PUSH 0x0
 *  004251F6   52               PUSH EDX
 *  004251F7   E8 14E20000      CALL oyakoai2.00433410
 *  004251FC   83C4 30          ADD ESP,0x30
 *  004251FF   83BE F81F0000 00 CMP DWORD PTR DS:[ESI+0x1FF8],0x0
 *  00425206   75 1D            JNZ SHORT oyakoai2.00425225
 *  00425208   8B96 F8230000    MOV EDX,DWORD PTR DS:[ESI+0x23F8]
 *  0042520E   8D86 00280000    LEA EAX,DWORD PTR DS:[ESI+0x2800]
 *  00425214   50               PUSH EAX
 *  00425215   8D8E FC270000    LEA ECX,DWORD PTR DS:[ESI+0x27FC]
 *  0042521B   51               PUSH ECX
 *  0042521C   52               PUSH EDX
 *  0042521D   E8 7EDF0000      CALL oyakoai2.004331A0
 *  00425222   83C4 0C          ADD ESP,0xC
 *  00425225   8B86 04280000    MOV EAX,DWORD PTR DS:[ESI+0x2804]
 *  0042522B   8B96 F81F0000    MOV EDX,DWORD PTR DS:[ESI+0x1FF8]
 *  00425231   53               PUSH EBX
 *  00425232   894424 30        MOV DWORD PTR SS:[ESP+0x30],EAX
 *  00425236   894424 2C        MOV DWORD PTR SS:[ESP+0x2C],EAX
 *  0042523A   894424 28        MOV DWORD PTR SS:[ESP+0x28],EAX
 *  0042523E   894424 24        MOV DWORD PTR SS:[ESP+0x24],EAX
 *  00425242   B8 74395100      MOV EAX,oyakoai2.00513974
 *  00425247   55               PUSH EBP
 *  00425248   894424 24        MOV DWORD PTR SS:[ESP+0x24],EAX
 *  0042524C   894424 20        MOV DWORD PTR SS:[ESP+0x20],EAX
 *  00425250   894424 1C        MOV DWORD PTR SS:[ESP+0x1C],EAX
 *  00425254   894424 18        MOV DWORD PTR SS:[ESP+0x18],EAX
 *  00425258   6A 00            PUSH 0x0
 *  0042525A   8D4424 1C        LEA EAX,DWORD PTR SS:[ESP+0x1C]
 *  0042525E   50               PUSH EAX
 *  0042525F   8D4C24 30        LEA ECX,DWORD PTR SS:[ESP+0x30]
 *  00425263   51               PUSH ECX
 *  00425264   8B8C96 FC1B0000  MOV ECX,DWORD PTR DS:[ESI+EDX*4+0x1BFC]
 *  0042526B   57               PUSH EDI
 *  0042526C   E8 7FFDFFFF      CALL oyakoai2.00424FF0
 *  00425271   8B46 08          MOV EAX,DWORD PTR DS:[ESI+0x8]
 *  00425274   8B4E 10          MOV ECX,DWORD PTR DS:[ESI+0x10]
 *  00425277   8BAE 00280000    MOV EBP,DWORD PTR DS:[ESI+0x2800]
 *  0042527D   8386 F81F0000 01 ADD DWORD PTR DS:[ESI+0x1FF8],0x1
 *  00425284   8BBE F81F0000    MOV EDI,DWORD PTR DS:[ESI+0x1FF8]
 *  0042528A   8B5E 0C          MOV EBX,DWORD PTR DS:[ESI+0xC]
 *  0042528D   2B5E 04          SUB EBX,DWORD PTR DS:[ESI+0x4]
 *  00425290   2BC8             SUB ECX,EAX
 *  00425292   2B9E FC270000    SUB EBX,DWORD PTR DS:[ESI+0x27FC]
 *  00425298   8BC5             MOV EAX,EBP
 *  0042529A   2B05 D8776C00    SUB EAX,DWORD PTR DS:[0x6C77D8]
 *  004252A0   D1EB             SHR EBX,1
 *  004252A2   99               CDQ
 *  004252A3   2BC2             SUB EAX,EDX
 *  004252A5   D1F8             SAR EAX,1
 *  004252A7   894424 10        MOV DWORD PTR SS:[ESP+0x10],EAX
 *  004252AB   8BC7             MOV EAX,EDI
 *  004252AD   F7D8             NEG EAX
 *  004252AF   894424 3C        MOV DWORD PTR SS:[ESP+0x3C],EAX
 *  004252B3   8D45 08          LEA EAX,DWORD PTR SS:[EBP+0x8]
 *  004252B6   BA 08000000      MOV EDX,0x8
 *  004252BB   0FAFC7           IMUL EAX,EDI
 *  004252BE   8BFF             MOV EDI,EDI
 *  004252C0   3BC1             CMP EAX,ECX
 *  004252C2   76 24            JBE SHORT oyakoai2.004252E8
 *  004252C4   034424 3C        ADD EAX,DWORD PTR SS:[ESP+0x3C]
 *  004252C8   83EA 01          SUB EDX,0x1
 *  004252CB   85D2             TEST EDX,EDX
 *  004252CD   895424 40        MOV DWORD PTR SS:[ESP+0x40],EDX
 *  004252D1  ^7D ED            JGE SHORT oyakoai2.004252C0
 *  004252D3   5D               POP EBP
 *  004252D4   83C7 FF          ADD EDI,-0x1
 *  004252D7   5B               POP EBX
 *  004252D8   89BE F81F0000    MOV DWORD PTR DS:[ESI+0x1FF8],EDI
 *  004252DE   5F               POP EDI
 *  004252DF   33C0             XOR EAX,EAX
 *  004252E1   5E               POP ESI
 *  004252E2   83C4 28          ADD ESP,0x28
 *  004252E5   C2 0800          RETN 0x8
 *  004252E8   85D2             TEST EDX,EDX
 *  004252EA   7D 15            JGE SHORT oyakoai2.00425301
 *  004252EC   5D               POP EBP
 *  004252ED   83C7 FF          ADD EDI,-0x1
 *  004252F0   5B               POP EBX
 *  004252F1   89BE F81F0000    MOV DWORD PTR DS:[ESI+0x1FF8],EDI
 *  004252F7   5F               POP EDI
 *  004252F8   33C0             XOR EAX,EAX
 *  004252FA   5E               POP ESI
 *  004252FB   83C4 28          ADD ESP,0x28
 *  004252FE   C2 0800          RETN 0x8
 *  00425301   03EA             ADD EBP,EDX
 *  00425303   896C24 14        MOV DWORD PTR SS:[ESP+0x14],EBP
 *  00425307   0FAFEF           IMUL EBP,EDI
 *  0042530A   2BCD             SUB ECX,EBP
 *  0042530C   D1E9             SHR ECX,1
 *  0042530E   034E 08          ADD ECX,DWORD PTR DS:[ESI+0x8]
 *  00425311   85FF             TEST EDI,EDI
 *  00425313   C74424 40 000000>MOV DWORD PTR SS:[ESP+0x40],0x0
 *  0042531B   0F86 C4000000    JBE oyakoai2.004253E5
 *  00425321   8D86 FC1B0000    LEA EAX,DWORD PTR DS:[ESI+0x1BFC]
 *  00425327   8BE9             MOV EBP,ECX
 *  00425329   894424 3C        MOV DWORD PTR SS:[ESP+0x3C],EAX
 *  0042532D   8DBE 14040000    LEA EDI,DWORD PTR DS:[ESI+0x414]
 *  00425333   891F             MOV DWORD PTR DS:[EDI],EBX
 *  00425335   896F 04          MOV DWORD PTR DS:[EDI+0x4],EBP
 *  00425338   8B8E FC270000    MOV ECX,DWORD PTR DS:[ESI+0x27FC]
 *  0042533E   03CB             ADD ECX,EBX
 *  00425340   894F 08          MOV DWORD PTR DS:[EDI+0x8],ECX
 *  00425343   8B96 00280000    MOV EDX,DWORD PTR DS:[ESI+0x2800]
 *  00425349   03D5             ADD EDX,EBP
 *  0042534B   8957 0C          MOV DWORD PTR DS:[EDI+0xC],EDX
 *  0042534E   8B8E 24280000    MOV ECX,DWORD PTR DS:[ESI+0x2824]
 *  00425354   85C9             TEST ECX,ECX
 *  00425356   74 0B            JE SHORT oyakoai2.00425363
 *  00425358   8B4424 40        MOV EAX,DWORD PTR SS:[ESP+0x40]
 *  0042535C   50               PUSH EAX
 *  0042535D   57               PUSH EDI
 *  0042535E   E8 CD2C0000      CALL oyakoai2.00428030
 *  00425363   DB47 04          FILD DWORD PTR DS:[EDI+0x4]
 *  00425366   8B4C24 3C        MOV ECX,DWORD PTR SS:[ESP+0x3C]
 *  0042536A   8B91 00040000    MOV EDX,DWORD PTR DS:[ECX+0x400]
 *  00425370   6A 00            PUSH 0x0
 *  00425372   83EC 08          SUB ESP,0x8
 *  00425375   D95C24 04        FSTP DWORD PTR SS:[ESP+0x4]
 *  00425379   DB07             FILD DWORD PTR DS:[EDI]
 *  0042537B   D91C24           FSTP DWORD PTR SS:[ESP]
 *  0042537E   52               PUSH EDX
 *  0042537F   E8 CC160100      CALL oyakoai2.00436A50
 *  00425384   DB47 04          FILD DWORD PTR DS:[EDI+0x4]
 *  00425387   8B4424 4C        MOV EAX,DWORD PTR SS:[ESP+0x4C]
 *  0042538B   8B88 FC070000    MOV ECX,DWORD PTR DS:[EAX+0x7FC]
 *  00425391   83C4 10          ADD ESP,0x10
 *  00425394   6A 00            PUSH 0x0
 *  00425396   83EC 08          SUB ESP,0x8
 *  00425399   D95C24 04        FSTP DWORD PTR SS:[ESP+0x4]
 *  0042539D   DB07             FILD DWORD PTR DS:[EDI]
 *  0042539F   D91C24           FSTP DWORD PTR SS:[ESP]
 *  004253A2   51               PUSH ECX
 *  004253A3   E8 A8160100      CALL oyakoai2.00436A50
 *  004253A8   8B5424 4C        MOV EDX,DWORD PTR SS:[ESP+0x4C]
 *  004253AC   8B0A             MOV ECX,DWORD PTR DS:[EDX]
 *  004253AE   83C4 10          ADD ESP,0x10
 *  004253B1   85C9             TEST ECX,ECX
 *  004253B3   74 0D            JE SHORT oyakoai2.004253C2
 *  004253B5   8B47 04          MOV EAX,DWORD PTR DS:[EDI+0x4]
 *  004253B8   034424 10        ADD EAX,DWORD PTR SS:[ESP+0x10]
 *  004253BC   50               PUSH EAX
 *  004253BD   E8 AEC6FFFF      CALL oyakoai2.00421A70
 *  004253C2   8B4424 40        MOV EAX,DWORD PTR SS:[ESP+0x40]
 *  004253C6   834424 3C 04     ADD DWORD PTR SS:[ESP+0x3C],0x4
 *  004253CB   036C24 14        ADD EBP,DWORD PTR SS:[ESP+0x14]
 *  004253CF   83C0 01          ADD EAX,0x1
 *  004253D2   83C7 10          ADD EDI,0x10
 *  004253D5   3B86 F81F0000    CMP EAX,DWORD PTR DS:[ESI+0x1FF8]
 *  004253DB   894424 40        MOV DWORD PTR SS:[ESP+0x40],EAX
 *  004253DF  ^0F82 4EFFFFFF    JB oyakoai2.00425333
 *  004253E5   8B86 F81F0000    MOV EAX,DWORD PTR DS:[ESI+0x1FF8]
 *  004253EB   5D               POP EBP
 *  004253EC   5B               POP EBX
 *  004253ED   5F               POP EDI
 *  004253EE   83E8 01          SUB EAX,0x1
 *  004253F1   5E               POP ESI
 *  004253F2   83C4 28          ADD ESP,0x28
 *  004253F5   C2 0800          RETN 0x8
 *  004253F8   CC               INT3
 *  004253F9   CC               INT3
 *  004253FA   CC               INT3
 *  004253FB   CC               INT3
 *  004253FC   CC               INT3
 *  004253FD   CC               INT3
 *  004253FE   CC               INT3
 */
bool attach(ulong startAddress, ulong stopAddress)
{
  const uint8_t bytes[] = {
    0x83,0x7e, 0x14, 0x00,  // 004250f6   837e 14 00       cmp dword ptr ds:[esi+0x14],0x0
    0x75, 0x09,             // 004250fa   75 09            jnz short oyakoai2.00425105
    0x33,0xc0,              // 004250fc   33c0             xor eax,eax
    0x5e,                   // 004250fe   5e               pop esi
    0x83,0xc4, 0x28,        // 004250ff   83c4 28          add esp,0x28
    0xc2, 0x08,0x00         // 00425102   c2 0800          retn 0x8
  };
  ulong addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  return winhook::hook_before(addr, Private::hookBefore);
}

} // namespace OtherHook
} // unnamed namespace

bool PensilEngine::attach()
{
  ulong startAddress, stopAddress;
  if (!Engine::getProcessMemoryRange(&startAddress, &stopAddress))
    return false;
  if (!ScenarioHook::attach(startAddress, stopAddress))
    return false;
  if (OtherHook::attach(startAddress, stopAddress))
    DOUT("other text found");
  else
    DOUT("other text NOT FOUND");
  // Unfortunately, GetGlyphOutlineA is not invoked for all Pensil games
  HijackManager::instance()->attachFunction((ulong)::GetGlyphOutlineA);
  return true;
}

/**
 *  Sample ruby: 凄い綺麗な\{女性|ひと}だ。
 */
QString PensilEngine::rubyCreate(const QString &rb, const QString &rt)
{
  static QString fmt = "\\{%1|%2}";
  return fmt.arg(rb, rt);
}

// Remove furigana in scenario thread.
QString PensilEngine::rubyRemove(const QString &text)
{
  if (!text.contains('|'))
    return text;
  static QRegExp rx("\\\\\\{(.*)\\|.*\\}");
  if (!rx.isMinimal())
    rx.setMinimal(true);
  return QString(text).replace(rx, "\\1");
}

// EOF
