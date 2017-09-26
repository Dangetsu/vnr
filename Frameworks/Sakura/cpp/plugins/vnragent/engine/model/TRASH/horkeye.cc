// horkeye.cc
// 6/24/2015 jichi
#include "engine/model/horkeye.h"
#include "engine/enginecontroller.h"
#include "engine/enginedef.h"
#include "engine/enginehash.h"
#include "engine/engineutil.h"
//#include "hijack/hijackmanager.h"
#include "memdbg/memsearch.h"
#include "winhook/hookcode.h"
#include <qt_windows.h>
#include <QtCore/QTextCodec>

#define DEBUG "horkeye"
#include "sakurakit/skdebug.h"

namespace { // unnamed
namespace ScenarioHook {
namespace Private {

  // CharNextA not used in order to ustilize sjis prefix
  QByteArray ltrim(const QByteArray &data, QByteArray &prefix, QTextCodec *codec)
  {
    QString text = codec->toUnicode(data);
    if (text.isEmpty())
      return data;
    const wchar_t w_open = 0x3010,
                  w_close = 0x3011;
    if (text[0].unicode() != w_open)
      return data;
    int pos = text.indexOf(w_close);
    if (pos == -1)
      return data;
    pos++;
    QString left = text.left(pos),
            right = text.mid(pos);
    prefix = codec->fromUnicode(left);
    return codec->fromUnicode(right);
  }

  /**
   *  Example text:
   *  【直子,S001_A1_0027】「ほら犬がなにか悪さをすると、しらばっくれるけどばればれな表情するでしょ？　今のシンクローにはそういうの全然ないもの」
   *
   *  Sample argument:
   *  00F44148  58 3B F4 00 59 20 39 2C 20 35 30 30 2C 20 34 30
   *  00F44158  1E 00 00 00 1F 00 00 00 38 30 40 31 39 30 40 00
   *  00F44168  5A D8 83 49 00 00 00 88 20 53 30 30 31 5F 31 42
   *  00F44178  41 32 42 41 5F 30 30 30 5F 4C 2C 20 32 35 30 00
   *  00F44188  24 65 78 74 2C 25 30 00 45 D8 83 49 00 00 00 88
   *  00F44198  20 30 30 31 2C 20 35 30 30 40 30 40 2D 31 2C 20
   *  00F441A8  31 30 2C 20 31 00 00 00 00 00 00 00 00 00 00 00
   *  00F441B8  40 D8 83 49 00 00 00 8C 00 01 E3 00 20 2A 65 78
   *  00F441C8  6D 6F 64 65 00 00 00 00 00 00 00 00 0F 00 00 00
   *  00F441D8  00 00 00 00 00 00 00 00 4B D8 83 49 00 00 00 8C
   *
   *  00F43B58  90 5F 93 DE 90 EC 8C A7 81 40 90 BC 8F C3 92 6E  神奈川県　西湘地
   *  00F43B68  88 E6 81 40 8F AC 98 61 93 63 8E 73 81 42 00 00  域　小和田市。..
   */
  bool hookBefore(winhook::hook_stack *s)
  {
    static QByteArray data_;
    auto q = EngineController::instance();
    QTextCodec *codec = q->decoder(); // decoder have the sjis
    if (!codec)
      return true;
    //auto arg = (HookArgument *)s->eax;
    auto text = (LPCSTR)s->stack[1]; // text in arg1
    auto size = s->stack[2]; // size in arg2
    QByteArray oldData(text, size),
               prefix;
    oldData = ltrim(oldData, prefix, codec);

    enum { role = Engine::ScenarioRole };
    QByteArray newData = q->dispatchTextA(oldData, role);
    if (newData.isEmpty() || newData == oldData)
      return true;
    if (!prefix.isEmpty())
      newData.prepend(prefix);

    data_ = newData;
    s->stack[1] = (ulong)data_.constData(); // text in arg1
    s->stack[2] = data_.size(); // size in arg2
    //::strcpy(text, data_.constData());
    return true;
  }

  ulong findFunction(ulong startAddress, ulong stopAddress)
  {
    const quint8 bytes[] = {
      0x89,0x6c,0x24, 0x24,   // 013cdb01   896c24 24        mov dword ptr ss:[esp+0x24],ebp
      0x89,0x74,0x24, 0x0c,   // 013cdb05   897424 0c        mov dword ptr ss:[esp+0xc],esi
      0x89,0x4c,0x24, 0x18,   // 013cdb09   894c24 18        mov dword ptr ss:[esp+0x18],ecx
      0x8a,0x0c,0x1a          // 013cdb0d   8a0c1a           mov cl,byte ptr ds:[edx+ebx]        jichi: text is here
    };
    ulong addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
    if (!addr)
      return 0;

    // 013cdabf   c3               retn
    // 013cdac0   83ec 40          sub esp,0x40    ; jichi: text here in arg1
    //
    // 0x013cdb0d - 0x013cdabf = 78
    for (DWORD i = addr; i > addr - 0x100; i--)
      if (*(DWORD *)i == 0x40ec83c3)
        return i + 1;
    return 0;
  }
} // namespace Private

/** 10/20/2014 jichi: HorkEye, http://horkeye.com
 *  Sample games:
 *  - 結城友奈は勇者である 体験版
 *  - 姉小路直子と銀色の死神
 *
 *  No GDI functions are used by this game.
 *
 *  Debug method:
 *  There are two matched texts.
 *  The one having fixed address is used to insert hw breakpoints.
 *
 *  I found are two functions addressing the address, both of which seems to be good.
 *  The first one is used. Text in arg1, and size in arg2.
 *
 *  013cda60   8d4c24 1c        lea ecx,dword ptr ss:[esp+0x1c]
 *  013cda64   51               push ecx
 *  013cda65   68 48a8c201      push .01c2a848                                     ; ascii "if"
 *  013cda6a   e8 d1291600      call .01530440
 *  013cda6f   83c4 0c          add esp,0xc
 *  013cda72   6a 01            push 0x1
 *  013cda74   83ec 1c          sub esp,0x1c
 *  013cda77   8bcc             mov ecx,esp
 *  013cda79   896424 30        mov dword ptr ss:[esp+0x30],esp
 *  013cda7d   6a 10            push 0x10
 *  013cda7f   c741 14 0f000000 mov dword ptr ds:[ecx+0x14],0xf
 *  013cda86   c741 10 00000000 mov dword ptr ds:[ecx+0x10],0x0
 *  013cda8d   68 80125601      push .01561280
 *  013cda92   c601 00          mov byte ptr ds:[ecx],0x0
 *  013cda95   e8 5681ffff      call .013c5bf0
 *  013cda9a   e8 717a0900      call .01465510
 *  013cda9f   83c4 20          add esp,0x20
 *  013cdaa2   b8 01000000      mov eax,0x1
 *  013cdaa7   8b8c24 b8000000  mov ecx,dword ptr ss:[esp+0xb8]
 *  013cdaae   5f               pop edi
 *  013cdaaf   5e               pop esi
 *  013cdab0   5d               pop ebp
 *  013cdab1   5b               pop ebx
 *  013cdab2   33cc             xor ecx,esp
 *  013cdab4   e8 c7361600      call .01531180
 *  013cdab9   81c4 ac000000    add esp,0xac
 *  013cdabf   c3               retn
 *  013cdac0   83ec 40          sub esp,0x40    ; jichi: text here in arg1
 *  013cdac3   a1 24805d01      mov eax,dword ptr ds:[0x15d8024]
 *  013cdac8   8b15 c4709901    mov edx,dword ptr ds:[0x19970c4]
 *  013cdace   8d0c00           lea ecx,dword ptr ds:[eax+eax]
 *  013cdad1   a1 9c506b01      mov eax,dword ptr ds:[0x16b509c]
 *  013cdad6   0305 18805d01    add eax,dword ptr ds:[0x15d8018]
 *  013cdadc   53               push ebx
 *  013cdadd   8b5c24 48        mov ebx,dword ptr ss:[esp+0x48]
 *  013cdae1   55               push ebp
 *  013cdae2   8b6c24 50        mov ebp,dword ptr ss:[esp+0x50]
 *  013cdae6   894c24 34        mov dword ptr ss:[esp+0x34],ecx
 *  013cdaea   8b0d 20805d01    mov ecx,dword ptr ds:[0x15d8020]
 *  013cdaf0   894424 18        mov dword ptr ss:[esp+0x18],eax
 *  013cdaf4   a1 1c805d01      mov eax,dword ptr ds:[0x15d801c]
 *  013cdaf9   03c8             add ecx,eax
 *  013cdafb   56               push esi
 *  013cdafc   33f6             xor esi,esi
 *  013cdafe   d1f8             sar eax,1
 *  013cdb00   45               inc ebp
 *  013cdb01   896c24 24        mov dword ptr ss:[esp+0x24],ebp
 *  013cdb05   897424 0c        mov dword ptr ss:[esp+0xc],esi
 *  013cdb09   894c24 18        mov dword ptr ss:[esp+0x18],ecx
 *  013cdb0d   8a0c1a           mov cl,byte ptr ds:[edx+ebx]        jichi: here
 *  013cdb10   894424 30        mov dword ptr ss:[esp+0x30],eax
 *  013cdb14   8a441a 01        mov al,byte ptr ds:[edx+ebx+0x1]
 *  013cdb18   57               push edi
 *  013cdb19   897424 14        mov dword ptr ss:[esp+0x14],esi
 *  013cdb1d   3935 c8709901    cmp dword ptr ds:[0x19970c8],esi
 *
 *  The hooked place is only accessed once.
 *  013cdb0d   8a0c1a           mov cl,byte ptr ds:[edx+ebx]        jichi: here
 *  ebx is the text to be base address.
 *  edx is the offset to skip character name.
 *
 *  023B66A0  81 79 89 C4 EA A3 2C 53 30 30 35 5F 42 5F 30 30  【夏凜,S005_B_00
 *  023B66B0  30 32 81 7A 81 75 83 6F 81 5B 83 65 83 62 83 4E  02】「バーテック
 *  023B66C0  83 58 82 CD 82 B1 82 C1 82 BF 82 CC 93 73 8D 87  スはこっちの都合
 *  023B66D0  82 C8 82 C7 82 A8 8D 5C 82 A2 82 C8 82 B5 81 63  などお構いなし…
 *
 *  The second called function is here that is not used
 *  013CDC90   8B15 C4709901    MOV EDX,DWORD PTR DS:[0x19970C4]
 *  013CDC96   8A041E           MOV AL,BYTE PTR DS:[ESI+EBX]	; jichi: here
 *  013CDC99   884424 24        MOV BYTE PTR SS:[ESP+0x24],AL
 *  013CDC9D   0FB6C0           MOVZX EAX,AL
 *
 *  1/15/2015
 *  Alternative hook that might not need a text filter:
 *  http://www.hongfire.com/forum/showthread.php/36807-AGTH-text-extraction-tool-for-games-translation/page753
 *  /HA-4@552B5:姉小路直子と銀色の死神.exe
 *  If this hook no longer works, try that one instead.
 *
 *  0013F7B4   010E4826  RETURN to .010E4826 from .010DD980
 *  0013F7B8   00F83B58 ; jichi: arg1 text
 *  0013F7BC   0000001E ; jichi: arg2 size excluding count
 *  0013F7C0   0013F7DC
 *  0013F7C4   0013F7E4
 *  0013F7C8   FAB63973
 *
 *  姉小路直子と銀色の死神
 *  0114D972   33CC             XOR ECX,ESP
 *  0114D974   E8 A7411600      CALL .012B1B20
 *  0114D979   81C4 AC000000    ADD ESP,0xAC
 *  0114D97F   C3               RETN
 *  0114D980   83EC 40          SUB ESP,0x40    ; jichi: hook here
 *  0114D983   A1 24803501      MOV EAX,DWORD PTR DS:[0x1358024]
 *  0114D988   8B15 C4707101    MOV EDX,DWORD PTR DS:[0x17170C4]
 *  0114D98E   8D0C00           LEA ECX,DWORD PTR DS:[EAX+EAX]
 *  0114D991   A1 9C504301      MOV EAX,DWORD PTR DS:[0x143509C]
 *  0114D996   0305 18803501    ADD EAX,DWORD PTR DS:[0x1358018]
 *  0114D99C   53               PUSH EBX
 *  0114D99D   8B5C24 48        MOV EBX,DWORD PTR SS:[ESP+0x48] ; jichi: arg1 text
 *  0114D9A1   55               PUSH EBP
 *  0114D9A2   8B6C24 50        MOV EBP,DWORD PTR SS:[ESP+0x50] ; jichi: arg3
 *  0114D9A6   894C24 34        MOV DWORD PTR SS:[ESP+0x34],ECX
 *  0114D9AA   8B0D 20803501    MOV ECX,DWORD PTR DS:[0x1358020]
 *  0114D9B0   894424 18        MOV DWORD PTR SS:[ESP+0x18],EAX
 *  0114D9B4   A1 1C803501      MOV EAX,DWORD PTR DS:[0x135801C]
 *  0114D9B9   03C8             ADD ECX,EAX
 *  0114D9BB   56               PUSH ESI
 *  0114D9BC   33F6             XOR ESI,ESI
 *  0114D9BE   D1F8             SAR EAX,1
 *  0114D9C0   45               INC EBP
 *  0114D9C1   896C24 24        MOV DWORD PTR SS:[ESP+0x24],EBP
 *  0114D9C5   897424 0C        MOV DWORD PTR SS:[ESP+0xC],ESI
 *  0114D9C9   894C24 18        MOV DWORD PTR SS:[ESP+0x18],ECX
 *  0114D9CD   8A0C1A           MOV CL,BYTE PTR DS:[EDX+EBX]    ; jichi: text accessed here
 *  0114D9D0   894424 30        MOV DWORD PTR SS:[ESP+0x30],EAX
 *  0114D9D4   8A441A 01        MOV AL,BYTE PTR DS:[EDX+EBX+0x1]
 *  0114D9D8   57               PUSH EDI
 *  0114D9D9   897424 14        MOV DWORD PTR SS:[ESP+0x14],ESI
 *  0114D9DD   3935 C8707101    CMP DWORD PTR DS:[0x17170C8],ESI
 *  0114D9E3   0F85 9C000000    JNZ .0114DA85
 *  0114D9E9   80F9 5B          CMP CL,0x5B
 *  0114D9EC   75 6D            JNZ SHORT .0114DA5B
 *  0114D9EE   8BC2             MOV EAX,EDX
 *  0114D9F0   3BC5             CMP EAX,EBP
 *  0114D9F2   7D 0B            JGE SHORT .0114D9FF
 *  0114D9F4   803C18 5D        CMP BYTE PTR DS:[EAX+EBX],0x5D
 *  0114D9F8   74 59            JE SHORT .0114DA53
 *  0114D9FA   40               INC EAX
 *  0114D9FB   3BC5             CMP EAX,EBP
 *  0114D9FD  ^7C F5            JL SHORT .0114D9F4
 *  0114D9FF   3935 90504301    CMP DWORD PTR DS:[0x1435090],ESI
 *  0114DA05   74 78            JE SHORT .0114DA7F
 *  0114DA07   833D 94504301 00 CMP DWORD PTR DS:[0x1435094],0x0
 *  0114DA0E   8B3D 58504301    MOV EDI,DWORD PTR DS:[0x1435058]
 *  0114DA14   BE 02000000      MOV ESI,0x2
 *  0114DA19   8935 CC707101    MOV DWORD PTR DS:[0x17170CC],ESI
 *  0114DA1F   75 2A            JNZ SHORT .0114DA4B
 *  0114DA21   A1 60504301      MOV EAX,DWORD PTR DS:[0x1435060]
 *  0114DA26   66:8B0D 84803501 MOV CX,WORD PTR DS:[0x1358084]
 *  0114DA2D   C1E0 0A          SHL EAX,0xA
 *  0114DA30   8D8438 C8234001  LEA EAX,DWORD PTR DS:[EAX+EDI+0x14023C8]
 *  0114DA37   66:8908          MOV WORD PTR DS:[EAX],CX
 *  0114DA3A   8A0D 86803501    MOV CL,BYTE PTR DS:[0x1358086]
 *  0114DA40   03FE             ADD EDI,ESI
 *  0114DA42   8848 02          MOV BYTE PTR DS:[EAX+0x2],CL
 *  0114DA45   893D 58504301    MOV DWORD PTR DS:[0x1435058],EDI
 *  0114DA4B   8935 C8707101    MOV DWORD PTR DS:[0x17170C8],ESI
 *  0114DA51   EB 38            JMP SHORT .0114DA8B
 *  0114DA53   8A4C18 01        MOV CL,BYTE PTR DS:[EAX+EBX+0x1]
 *  0114DA57   8A4418 02        MOV AL,BYTE PTR DS:[EAX+EBX+0x2]
 *  0114DA5B   80F9 81          CMP CL,0x81
 *  0114DA5E  ^75 9F            JNZ SHORT .0114D9FF
 *  0114DA60   3C 75            CMP AL,0x75
 *  0114DA62   74 08            JE SHORT .0114DA6C
 *  0114DA64   3C 69            CMP AL,0x69
 *  0114DA66   74 04            JE SHORT .0114DA6C
 *  0114DA68   3C 77            CMP AL,0x77
 *  0114DA6A  ^75 93            JNZ SHORT .0114D9FF
 *  0114DA6C   A1 8C504301      MOV EAX,DWORD PTR DS:[0x143508C]
 *  0114DA71   F7D8             NEG EAX
 *  0114DA73   1BC0             SBB EAX,EAX
 *  0114DA75   83E0 02          AND EAX,0x2
 *  0114DA78   A3 CC707101      MOV DWORD PTR DS:[0x17170CC],EAX
 *  0114DA7D   EB 06            JMP SHORT .0114DA85
 *  0114DA7F   8935 CC707101    MOV DWORD PTR DS:[0x17170CC],ESI
 *  0114DA85   8B3D 58504301    MOV EDI,DWORD PTR DS:[0x1435058]
 *  0114DA8B   8BF2             MOV ESI,EDX
 *  0114DA8D   897424 18        MOV DWORD PTR SS:[ESP+0x18],ESI
 *  0114DA91   3BF5             CMP ESI,EBP
 *  0114DA93   0F8C BD000000    JL .0114DB56
 *  0114DA99   33C0             XOR EAX,EAX
 *  0114DA9B   3905 94504301    CMP DWORD PTR DS:[0x1435094],EAX
 *  0114DAA1   75 4C            JNZ SHORT .0114DAEF
 *  0114DAA3   B8 01000000      MOV EAX,0x1
 *  0114DAA8   0105 68504301    ADD DWORD PTR DS:[0x1435068],EAX
 *  0114DAAE   A3 94504301      MOV DWORD PTR DS:[0x1435094],EAX
 *  0114DAB3   A1 CC707101      MOV EAX,DWORD PTR DS:[0x17170CC]
 *  0114DAB8   8D4C07 02        LEA ECX,DWORD PTR DS:[EDI+EAX+0x2]
 *  0114DABC   8D1485 04803501  LEA EDX,DWORD PTR DS:[EAX*4+0x1358004]
 *  0114DAC3   A1 60504301      MOV EAX,DWORD PTR DS:[0x1435060]
 *  0114DAC8   51               PUSH ECX
 *  0114DAC9   C1E0 0A          SHL EAX,0xA
 *  0114DACC   52               PUSH EDX
 *  0114DACD   8D8438 C8234001  LEA EAX,DWORD PTR DS:[EAX+EDI+0x14023C8]
 *  ...
 *  001DE056   75 15            JNZ SHORT .001DE06D
 *  001DE058   FF05 6C504C00    INC DWORD PTR DS:[0x4C506C]
 *  001DE05E   A3 94504C00      MOV DWORD PTR DS:[0x4C5094],EAX
 *  001DE063   A3 CC707A00      MOV DWORD PTR DS:[0x7A70CC],EAX
 *  001DE068   A3 C8707A00      MOV DWORD PTR DS:[0x7A70C8],EAX
 *  001DE06D   8B5424 14        MOV EDX,DWORD PTR SS:[ESP+0x14]
 *  001DE071   5F               POP EDI
 *  001DE072   5E               POP ESI
 *  001DE073   5D               POP EBP
 *  001DE074   8915 C05B4800    MOV DWORD PTR DS:[0x485BC0],EDX
 *  001DE07A   B8 01000000      MOV EAX,0x1
 *  001DE07F   5B               POP EBX
 *  001DE080   83C4 40          ADD ESP,0x40
 *  001DE083   C3               RETN    ; jichi: return here, 0x703 from the beginning
 *  001DE084   86DC             XCHG AH,BL
 *  001DE086   1D 0032DC1D      SBB EAX,0x1DDC3200
 *  001DE08B   008D DB1D00F1    ADD BYTE PTR SS:[EBP+0xF1001DDB],CL
 *  001DE091   DB1D 0059DC1D    FISTP DWORD PTR DS:[0x1DDC5900]
 *  001DE097   0079 DC          ADD BYTE PTR DS:[ECX-0x24],BH
 *  001DE09A   1D 00EEDC1D      SBB EAX,0x1DDCEE00
 *  001DE09F   0000             ADD BYTE PTR DS:[EAX],AL
 *  001DE0A1   06               PUSH ES
 *  001DE0A2   06               PUSH ES
 *
 *  The only caller of this function, whic contains the second pattern:
 *
 *  012E470E   C78424 C8000000 >MOV DWORD PTR SS:[ESP+0xC8],-0x1
 *  012E4719   39B424 B4000000  CMP DWORD PTR SS:[ESP+0xB4],ESI
 *  012E4720   72 10            JB SHORT .012E4732
 *  012E4722   8B9424 A0000000  MOV EDX,DWORD PTR SS:[ESP+0xA0]
 *  012E4729   52               PUSH EDX
 *  012E472A   E8 9AC61500      CALL .01440DC9
 *  012E472F   83C4 04          ADD ESP,0x4
 *  012E4732   A1 60505C01      MOV EAX,DWORD PTR DS:[0x15C5060]    ; jichi: loop started here
 *  012E4737   8B0D F0ACB301    MOV ECX,DWORD PTR DS:[0x1B3ACF0]
 *  012E473D   8B15 F4ACB301    MOV EDX,DWORD PTR DS:[0x1B3ACF4]
 *  012E4743   890CC5 80555801  MOV DWORD PTR DS:[EAX*8+0x1585580],ECX
 *  012E474A   8B0D D4A9B301    MOV ECX,DWORD PTR DS:[0x1B3A9D4]
 *  012E4750   8914C5 84555801  MOV DWORD PTR DS:[EAX*8+0x1585584],EDX
 *  012E4757   8B15 54505C01    MOV EDX,DWORD PTR DS:[0x15C5054]
 *  012E475D   890C85 20BA4E01  MOV DWORD PTR DS:[EAX*4+0x14EBA20],ECX
 *  012E4764   891485 284D5C01  MOV DWORD PTR DS:[EAX*4+0x15C4D28],EDX
 *  012E476B   A1 BC708A01      MOV EAX,DWORD PTR DS:[0x18A70BC]
 *  012E4770   3BC3             CMP EAX,EBX
 *  012E4772   74 0B            JE SHORT .012E477F
 *  012E4774   292D D4A9B301    SUB DWORD PTR DS:[0x1B3A9D4],EBP
 *  012E477A   E9 DB000000      JMP .012E485A
 *  012E477F   8B5424 2C        MOV EDX,DWORD PTR SS:[ESP+0x2C]
 *  012E4783   8B4C24 34        MOV ECX,DWORD PTR SS:[ESP+0x34]
 *  012E4787   8D42 02          LEA EAX,DWORD PTR DS:[EDX+0x2]
 *  012E478A   3BC1             CMP EAX,ECX
 *  012E478C   7D 30            JGE SHORT .012E47BE
 *  012E478E   8B15 D0A9B301    MOV EDX,DWORD PTR DS:[0x1B3A9D0]
 *  012E4794   8B35 AC515C01    MOV ESI,DWORD PTR DS:[0x15C51AC]
 *  012E479A   8BCA             MOV ECX,EDX
 *  012E479C   03C9             ADD ECX,ECX
 *  012E479E   8B0CCE           MOV ECX,DWORD PTR DS:[ESI+ECX*8]
 *  012E47A1   8B7424 38        MOV ESI,DWORD PTR SS:[ESP+0x38]
 *  012E47A5   8B7431 10        MOV ESI,DWORD PTR DS:[ECX+ESI+0x10]
 *  012E47A9   8B76 10          MOV ESI,DWORD PTR DS:[ESI+0x10]
 *  012E47AC   03C0             ADD EAX,EAX
 *  012E47AE   8B04C1           MOV EAX,DWORD PTR DS:[ECX+EAX*8]
 *  012E47B1   8B48 10          MOV ECX,DWORD PTR DS:[EAX+0x10]
 *  012E47B4   897424 14        MOV DWORD PTR SS:[ESP+0x14],ESI
 *  012E47B8   894C24 1C        MOV DWORD PTR SS:[ESP+0x1C],ECX
 *  012E47BC   EB 3B            JMP SHORT .012E47F9
 *  012E47BE   42               INC EDX
 *  012E47BF   3BD1             CMP EDX,ECX
 *  012E47C1   8B15 D0A9B301    MOV EDX,DWORD PTR DS:[0x1B3A9D0]
 *  012E47C7   7D 26            JGE SHORT .012E47EF
 *  012E47C9   8B0D AC515C01    MOV ECX,DWORD PTR DS:[0x15C51AC]
 *  012E47CF   8BC2             MOV EAX,EDX
 *  012E47D1   03C0             ADD EAX,EAX
 *  012E47D3   8B04C1           MOV EAX,DWORD PTR DS:[ECX+EAX*8]
 *  012E47D6   8B4C24 38        MOV ECX,DWORD PTR SS:[ESP+0x38]
 *  012E47DA   8B4408 10        MOV EAX,DWORD PTR DS:[EAX+ECX+0x10]
 *  012E47DE   8B48 10          MOV ECX,DWORD PTR DS:[EAX+0x10] ; jichi: count
 *  012E47E1   894C24 14        MOV DWORD PTR SS:[ESP+0x14],ECX
 *  012E47E5   C74424 1C 000000>MOV DWORD PTR SS:[ESP+0x1C],0x0
 *  012E47ED   EB 0A            JMP SHORT .012E47F9
 *  012E47EF   33C0             XOR EAX,EAX
 *  012E47F1   894424 14        MOV DWORD PTR SS:[ESP+0x14],EAX
 *  012E47F5   894424 1C        MOV DWORD PTR SS:[ESP+0x1C],EAX
 *  012E47F9   A1 AC515C01      MOV EAX,DWORD PTR DS:[0x15C51AC]
 *  012E47FE   03D2             ADD EDX,EDX
 *  012E4800   8B0CD0           MOV ECX,DWORD PTR DS:[EAX+EDX*8]
 *  012E4803   8B5424 38        MOV EDX,DWORD PTR SS:[ESP+0x38]
 *  012E4807   8B040A           MOV EAX,DWORD PTR DS:[EDX+ECX]
 *  012E480A   8378 14 10       CMP DWORD PTR DS:[EAX+0x14],0x10
 *  012E480E   8B48 10          MOV ECX,DWORD PTR DS:[EAX+0x10] ; jichi: count
 *  012E4811   72 02            JB SHORT .012E4815
 *  012E4813   8B00             MOV EAX,DWORD PTR DS:[EAX]  ; jichi: HookArgument in eax
 *  012E4815   8D5424 1C        LEA EDX,DWORD PTR SS:[ESP+0x1C]
 *  012E4819   52               PUSH EDX
 *  012E481A   8D5424 18        LEA EDX,DWORD PTR SS:[ESP+0x18]
 *  012E481E   52               PUSH EDX
 *  012E481F   51               PUSH ECX    ; jichi: count
 *  012E4820   50               PUSH EAX    ; jichi: text
 *  012E4821   E8 5A91FFFF      CALL .012DD980  ; jichi: call here
 *  012E4826   83C4 10          ADD ESP,0x10
 *  012E4829   85C0             TEST EAX,EAX
 *  012E482B   0F84 2E010000    JE .012E495F
 *  012E4831   A1 C0708A01      MOV EAX,DWORD PTR DS:[0x18A70C0]
 *  012E4836   85C0             TEST EAX,EAX
 *  012E4838   0F84 EF000000    JE .012E492D
 *  012E483E   833D C05B5801 00 CMP DWORD PTR DS:[0x1585BC0],0x0
 *  012E4845   0F84 E2000000    JE .012E492D
 *  012E484B   833D C4708A01 00 CMP DWORD PTR DS:[0x18A70C4],0x0
 *  012E4852   74 06            JE SHORT .012E485A
 *  012E4854   FF0D D4A9B301    DEC DWORD PTR DS:[0x1B3A9D4]
 *  012E485A   50               PUSH EAX
 *  012E485B   E8 80740900      CALL .0137BCE0
 *  012E4860   83C4 04          ADD ESP,0x4
 *  012E4863   A1 B0A1B301      MOV EAX,DWORD PTR DS:[0x1B3A1B0]
 *  012E4868   33FF             XOR EDI,EDI
 *  012E486A   3BC7             CMP EAX,EDI
 *  012E486C   0F84 B3000000    JE .012E4925
 *  012E4872   8D77 02          LEA ESI,DWORD PTR DS:[EDI+0x2]
 *  012E4875   83F8 04          CMP EAX,0x4
 *  012E4878   75 3B            JNZ SHORT .012E48B5
 *  012E487A   8B0D AC515C01    MOV ECX,DWORD PTR DS:[0x15C51AC]
 *
 *  ...
 *  001EDFA1   D1FA             SAR EDX,1
 *  001EDFA3   52               PUSH EDX
 *  001EDFA4   B9 88DF7100      MOV ECX,.0071DF88
 *  001EDFA9   E8 B2720300      CALL .00225260	; jichi: this is where text is painted char by char for wide characters, it takes 4 args and two bytes on the stack
 *  001EDFAE   8B5C24 54        MOV EBX,DWORD PTR SS:[ESP+0x54]
 *  001EDFB2   8B7424 18        MOV ESI,DWORD PTR SS:[ESP+0x18]
 *  001EDFB6   8B3D 58504D00    MOV EDI,DWORD PTR DS:[0x4D5058]
 *  001EDFBC   46               INC ESI
 *
 *  Wide character painted here
 *  00F3525E   CC               INT3
 *  00F3525F   CC               INT3
 *  00F35260   6A FF            PUSH -0x1
 *  00F35262   68 F0680801      PUSH .010868F0
 *  00F35267   64:A1 00000000   MOV EAX,DWORD PTR FS:[0]
 *  00F3526D   50               PUSH EAX
 *  00F3526E   83EC 48          SUB ESP,0x48
 *  00F35271   A1 80A31001      MOV EAX,DWORD PTR DS:[0x110A380]
 *  00F35276   33C4             XOR EAX,ESP
 *  00F35278   894424 44        MOV DWORD PTR SS:[ESP+0x44],EAX
 *  00F3527C   53               PUSH EBX
 *  00F3527D   55               PUSH EBP
 *  00F3527E   56               PUSH ESI
 *  00F3527F   57               PUSH EDI
 *  00F35280   A1 80A31001      MOV EAX,DWORD PTR DS:[0x110A380]
 *  00F35285   33C4             XOR EAX,ESP
 *  00F35287   50               PUSH EAX
 *  00F35288   8D4424 5C        LEA EAX,DWORD PTR SS:[ESP+0x5C]
 *  00F3528C   64:A3 00000000   MOV DWORD PTR FS:[0],EAX
 *  00F35292   0FB64424 74      MOVZX EAX,BYTE PTR SS:[ESP+0x74]    ; jichi: arg3, first byte
 *  00F35297   8BF1             MOV ESI,ECX
 *  00F35299   0FB64C24 78      MOVZX ECX,BYTE PTR SS:[ESP+0x78]    ; jichi: arg4, second byte
 *  00F3529E   8BBE 848F0900    MOV EDI,DWORD PTR DS:[ESI+0x98F84]
 *  00F352A4   8B96 188F0900    MOV EDX,DWORD PTR DS:[ESI+0x98F18]
 *  00F352AA   66:C1E0 08       SHL AX,0x8
 *  00F352AE   66:0BC1          OR AX,CX    ; jichi: ax is the text two bytes character now
 *  00F352B1   66:89047A        MOV WORD PTR DS:[EDX+EDI*2],AX
 *  00F352B5   8B86 188F0900    MOV EAX,DWORD PTR DS:[ESI+0x98F18]
 *  00F352BB   0FB70478         MOVZX EAX,WORD PTR DS:[EAX+EDI*2]
 *  00F352BF   3D 40810000      CMP EAX,0x8140
 *  00F352C4   7F 0F            JG SHORT .00F352D5
 *  00F352C6   0F84 DC010000    JE .00F354A8
 *  00F352CC   85C0             TEST EAX,EAX
 *  00F352CE   75 3D            JNZ SHORT .00F3530D
 *  00F352D0   E9 D3010000      JMP .00F354A8
 *  00F352D5   05 BF7EFFFF      ADD EAX,0xFFFF7EBF
 *  00F352DA   83F8 01          CMP EAX,0x1
 *  00F352DD   77 2E            JA SHORT .00F3530D
 *  00F352DF   33DB             XOR EBX,EBX
 *  00F352E1   391D A88B1001    CMP DWORD PTR DS:[0x1108BA8],EBX
 *  00F352E7   7E 24            JLE SHORT .00F3530D
 *  00F352E9   8D6F 01          LEA EBP,DWORD PTR DS:[EDI+0x1]
 *  00F352EC   8D6424 00        LEA ESP,DWORD PTR SS:[ESP]
 *  00F352F0   8D4C24 14        LEA ECX,DWORD PTR SS:[ESP+0x14]
 *  00F352F4   51               PUSH ECX
 *  00F352F5   8D8E 748F0900    LEA ECX,DWORD PTR DS:[ESI+0x98F74]
 *  00F352FB   896C24 18        MOV DWORD PTR SS:[ESP+0x18],EBP
 *  00F352FF   E8 BCDEFFFF      CALL .00F331C0
 *  00F35304   43               INC EBX
 *  00F35305   3B1D A88B1001    CMP EBX,DWORD PTR DS:[0x1108BA8]
 *  00F3530B  ^7C E3            JL SHORT .00F352F0
 *  00F3530D   DB4424 70        FILD DWORD PTR SS:[ESP+0x70]
 *  00F35311   8B96 288F0900    MOV EDX,DWORD PTR DS:[ESI+0x98F28]
 *  00F35317   8B4424 70        MOV EAX,DWORD PTR SS:[ESP+0x70]
 *  00F3531B   83EC 08          SUB ESP,0x8
 *  00F3531E   D95C24 04        FSTP DWORD PTR SS:[ESP+0x4]
 *  00F35322   8904BA           MOV DWORD PTR DS:[EDX+EDI*4],EAX
 *  00F35325   8B8E 248F0900    MOV ECX,DWORD PTR DS:[ESI+0x98F24]
 *  00F3532B   DB4424 74        FILD DWORD PTR SS:[ESP+0x74]
 *  00F3532F   8B5424 74        MOV EDX,DWORD PTR SS:[ESP+0x74]
 *  00F35333   8914B9           MOV DWORD PTR DS:[ECX+EDI*4],EDX
 *  00F35336   D91C24           FSTP DWORD PTR SS:[ESP]
 *  00F35339   57               PUSH EDI
 *  00F3533A   8BCE             MOV ECX,ESI
 *  00F3533C   E8 3FD1FFFF      CALL .00F32480
 *  00F35341   8B86 2C8F0900    MOV EAX,DWORD PTR DS:[ESI+0x98F2C]
 *  00F35347   833CB8 00        CMP DWORD PTR DS:[EAX+EDI*4],0x0
 *  00F3534B   8D0CB8           LEA ECX,DWORD PTR DS:[EAX+EDI*4]
 *  00F3534E   75 1B            JNZ SHORT .00F3536B
 *  00F35350   8D86 348F0900    LEA EAX,DWORD PTR DS:[ESI+0x98F34]
 *  00F35356   6A 01            PUSH 0x1
 *  00F35358   50               PUSH EAX
 *  00F35359   50               PUSH EAX
 *  00F3535A   51               PUSH ECX
 *  00F3535B   E8 30CAFEFF      CALL .00F21D90
 *  00F35360   83C4 10          ADD ESP,0x10
 *  00F35363   85C0             TEST EAX,EAX
 *  00F35365   0F84 3D010000    JE .00F354A8
 *  00F3536B   8B8E 2C8F0900    MOV ECX,DWORD PTR DS:[ESI+0x98F2C]
 *  00F35371   8B04B9           MOV EAX,DWORD PTR DS:[ECX+EDI*4]
 *  00F35374   8B10             MOV EDX,DWORD PTR DS:[EAX]
 *  00F35376   8B52 4C          MOV EDX,DWORD PTR DS:[EDX+0x4C]
 *  00F35379   68 00200000      PUSH 0x2000
 *  00F3537E   6A 00            PUSH 0x0
 *  00F35380   8D4C24 20        LEA ECX,DWORD PTR SS:[ESP+0x20]
 *  00F35384   51               PUSH ECX
 *  00F35385   6A 00            PUSH 0x0
 *  00F35387   50               PUSH EAX
 *  00F35388   FFD2             CALL EDX
 *  00F3538A   85C0             TEST EAX,EAX
 *  00F3538C   79 73            JNS SHORT .00F35401
 *  00F3538E   8B86 2C8F0900    MOV EAX,DWORD PTR DS:[ESI+0x98F2C]
 *  00F35394   8B04B8           MOV EAX,DWORD PTR DS:[EAX+EDI*4]
 *  00F35397   8B08             MOV ECX,DWORD PTR DS:[EAX]
 *  00F35399   6A 00            PUSH 0x0
 *  00F3539B   6A 00            PUSH 0x0
 *  00F3539D   8D5424 20        LEA EDX,DWORD PTR SS:[ESP+0x20]
 *  00F353A1   52               PUSH EDX
 *  00F353A2   6A 00            PUSH 0x0
 *  00F353A4   50               PUSH EAX
 *  00F353A5   8B41 4C          MOV EAX,DWORD PTR DS:[ECX+0x4C]
 *  00F353A8   FFD0             CALL EAX
 *  00F353AA   85C0             TEST EAX,EAX
 *  00F353AC   79 53            JNS SHORT .00F35401
 *  00F353AE   50               PUSH EAX
 *  00F353AF   8D4C24 24        LEA ECX,DWORD PTR SS:[ESP+0x24]
 *  00F353B3   51               PUSH ECX
 *  00F353B4   E8 A7C6FEFF      CALL .00F21A60
 *  00F353B9   83EC 14          SUB ESP,0x14
 *  00F353BC   8BD4             MOV EDX,ESP
 *  00F353BE   896424 30        MOV DWORD PTR SS:[ESP+0x30],ESP
 *  00F353C2   50               PUSH EAX
 *  00F353C3   68 5C410901      PUSH .0109415C                           ; ASCII "SetChar LockRect "
 *  00F353C8   52               PUSH EDX
 *  00F353C9   C78424 8C000000 >MOV DWORD PTR SS:[ESP+0x8C],0x0
 *  00F353D4   E8 A719FCFF      CALL .00EF6D80
 *  00F353D9   83C4 0C          ADD ESP,0xC
 *  00F353DC   E8 BF2D0700      CALL .00FA81A0
 *  00F353E1   83C4 1C          ADD ESP,0x1C
 *  00F353E4   837C24 34 10     CMP DWORD PTR SS:[ESP+0x34],0x10
 *  00F353E9   0F82 B9000000    JB .00F354A8
 *  00F353EF   8B4424 20        MOV EAX,DWORD PTR SS:[ESP+0x20]
 *  00F353F3   50               PUSH EAX
 *  00F353F4   E8 D0B91200      CALL .01060DC9
 *  00F353F9   83C4 04          ADD ESP,0x4
 *  00F353FC   E9 A7000000      JMP .00F354A8
 *  00F35401   8B8E 348F0900    MOV ECX,DWORD PTR DS:[ESI+0x98F34]
 *  00F35407   0FAF4C24 18      IMUL ECX,DWORD PTR SS:[ESP+0x18]
 *  00F3540C   8B5424 1C        MOV EDX,DWORD PTR SS:[ESP+0x1C]
 *  00F35410   51               PUSH ECX
 *  00F35411   6A 00            PUSH 0x0
 *  00F35413   52               PUSH EDX
 *  00F35414   E8 D7DA1200      CALL .01062EF0
 *  00F35419   8B86 188F0900    MOV EAX,DWORD PTR DS:[ESI+0x98F18]
 *  00F3541F   0FB70C78         MOVZX ECX,WORD PTR DS:[EAX+EDI*2]
 *  00F35423   8B5424 24        MOV EDX,DWORD PTR SS:[ESP+0x24]
 *  00F35427   8B4424 28        MOV EAX,DWORD PTR SS:[ESP+0x28]
 *  00F3542B   83C4 0C          ADD ESP,0xC
 *  00F3542E   6A 00            PUSH 0x0
 *  00F35430   6A 00            PUSH 0x0
 *  00F35432   51               PUSH ECX
 *  00F35433   52               PUSH EDX
 *  00F35434   8B96 B48F0900    MOV EDX,DWORD PTR DS:[ESI+0x98FB4]
 *  00F3543A   50               PUSH EAX
 *  00F3543B   8BCE             MOV ECX,ESI
 *  00F3543D   FFD2             CALL EDX
 *  00F3543F   8B86 2C8F0900    MOV EAX,DWORD PTR DS:[ESI+0x98F2C]
 *  00F35445   8B3CB8           MOV EDI,DWORD PTR DS:[EAX+EDI*4]
 *  00F35448   8B0F             MOV ECX,DWORD PTR DS:[EDI]
 *  00F3544A   8B51 50          MOV EDX,DWORD PTR DS:[ECX+0x50]
 *  00F3544D   6A 00            PUSH 0x0
 *  00F3544F   57               PUSH EDI
 *  00F35450   FFD2             CALL EDX
 *  00F35452   85C0             TEST EAX,EAX
 *  00F35454   79 4C            JNS SHORT .00F354A2
 *  00F35456   50               PUSH EAX
 *  00F35457   8D4424 40        LEA EAX,DWORD PTR SS:[ESP+0x40]
 *  00F3545B   50               PUSH EAX
 *  00F3545C   E8 FFC5FEFF      CALL .00F21A60
 *  00F35461   83EC 14          SUB ESP,0x14
 *  00F35464   8BCC             MOV ECX,ESP
 *  00F35466   896424 30        MOV DWORD PTR SS:[ESP+0x30],ESP
 *  00F3546A   50               PUSH EAX
 *  00F3546B   68 48410901      PUSH .01094148                           ; ASCII "SetChar UnlockRect "
 *  00F35470   51               PUSH ECX
 *  00F35471   C78424 8C000000 >MOV DWORD PTR SS:[ESP+0x8C],0x1
 *  00F3547C   E8 FF18FCFF      CALL .00EF6D80
 *  00F35481   83C4 0C          ADD ESP,0xC
 *  00F35484   E8 172D0700      CALL .00FA81A0
 *  00F35489   83C4 1C          ADD ESP,0x1C
 *  00F3548C   837C24 50 10     CMP DWORD PTR SS:[ESP+0x50],0x10
 *  00F35491   72 15            JB SHORT .00F354A8
 *  00F35493   8B5424 3C        MOV EDX,DWORD PTR SS:[ESP+0x3C]
 *  00F35497   52               PUSH EDX
 *  00F35498   E8 2CB91200      CALL .01060DC9
 *  00F3549D   83C4 04          ADD ESP,0x4
 *  00F354A0   EB 06            JMP SHORT .00F354A8
 *  00F354A2   FF86 848F0900    INC DWORD PTR DS:[ESI+0x98F84]
 *  00F354A8   8B4C24 5C        MOV ECX,DWORD PTR SS:[ESP+0x5C]
 *  00F354AC   64:890D 00000000 MOV DWORD PTR FS:[0],ECX
 *  00F354B3   59               POP ECX
 *  00F354B4   5F               POP EDI
 *  00F354B5   5E               POP ESI
 *  00F354B6   5D               POP EBP
 *  00F354B7   5B               POP EBX
 *  00F354B8   8B4C24 44        MOV ECX,DWORD PTR SS:[ESP+0x44]
 *  00F354BC   33CC             XOR ECX,ESP
 *  00F354BE   E8 5DC61200      CALL .01061B20
 *  00F354C3   83C4 54          ADD ESP,0x54
 *  00F354C6   C2 1000          RETN 0x10
 *  00F354C9   CC               INT3
 *  00F354CA   CC               INT3
 *
 *  0029F738   00EFDFAE  RETURN to .00EFDFAE from .00F35260
 *  0029F73C   00000018 ; arg1
 *  0029F740   00000000 ; arg2
 *  0029F744   00000090 ; arg3, first byte
 *  0029F748   0000005F ; arg4, second byte
 *  0029F74C   0000042A
 *  0029F750   00000000
 *  0029F754   00000010
 *  0029F758   00E23B58
 *  0029F75C   00000000
 */
bool attach() // attach scenario
{
  ulong startAddress, stopAddress;
  if (!Engine::getProcessMemoryRange(&startAddress, &stopAddress))
    return false;
  ulong addr = Private::findFunction(startAddress, stopAddress);
  if (!addr)
    return false;
  return winhook::hook_before(addr, Private::hookBefore);

  //const BYTE bytes[] = {
  //  //0x8b,0x48, 0x10,      // 0093480e   8b48 10          mov ecx,dword ptr ds:[eax+0x10]
  //  //0x72, 0x0,0x02,       // 00934811   72 02            jb short .00934815
  //  0x8b,0x00,            // 00934813   8b00             mov eax,dword ptr ds:[eax]  ; jichi: hook here
  //  0x8d,0x54,0x24, 0x1c, // 00934815   8d5424 1c        lea edx,dword ptr ss:[esp+0x1c]
  //  0x52,                 // 00934819   52               push edx
  //  0x8d,0x54,0x24, 0x18, // 0093481a   8d5424 18        lea edx,dword ptr ss:[esp+0x18]
  //  0x52,                 // 0093481e   52               push edx
  //  0x51,                 // 0093481f   51               push ecx
  //  0x50                  // 00934820   50               push eax
  //};
  ////enum { addr_offset = 0x00934813 - 0x0093480e }; // = 5
  //ulong addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  //if (!addr)
  //  return 0;
  ////addr += addr_offset;
  //return winhook::hook_before(addr, Private::hookBefore2);

  //int count = 0;
  //auto fun = [&count](ulong call) {
  //  count += winhook::hook_both(call, Private::hookBefore, Private::hookAfter);
  //};
  //MemDbg::iterNearCallAddress(fun, addr, startAddress, stopAddress);
  //DOUT("call number =" << count);
  //return count;
}

} // namespace ScenarioHook

} // unnamed namespace

/** Public class */

bool HorkEyeEngine::attach() { return ScenarioHook::attach(); }

// EOF
/*
  struct HookArgument // struct in eax
  {
    LPCSTR text;  // 0x0
    DWORD unknown[3];
    int size,     // 0x10
        capacity; // 0x14
  };
  bool hookBefore2(winhook::hook_stack *s)
  {
    static QByteArray data_;
    auto q = EngineController::instance();
    QTextCodec *codec = q->decoder(); // decoder have the sjis
    if (!codec)
      return true;
    auto arg = (HookArgument *)s->eax;
    QByteArray oldData(arg->text, arg->size),
               prefix;
    oldData = ltrim(oldData, prefix, codec);

    enum { role = Engine::ScenarioRole, sig = Engine::ScenarioThreadSignature };
    QByteArray newData = q->dispatchTextA(oldData, role, sig);
    if (newData.isEmpty() || newData == oldData)
      return true;
    if (!prefix.isEmpty())
      newData.prepend(prefix);

    data_ = newData;

    arg->text = data_.constData(); // text in arg1
    s->ecx = arg->size = data_.size(); // size in arg2
    arg->capacity = arg->size + 1;

    //s->stack[1] = (ulong)data_.constData(); // text in arg1
    //s->stack[2] = data_.size(); // size in arg2
    //::strcpy(text, data_.constData());
    return true;
  }

 */
