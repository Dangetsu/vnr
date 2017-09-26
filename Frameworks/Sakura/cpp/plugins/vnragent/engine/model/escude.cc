// escude.cc
// 7/23/2015 jichi
#include "engine/model/escude.h"
#include "engine/enginecontroller.h"
#include "engine/enginedef.h"
#include "engine/enginehash.h"
#include "engine/engineutil.h"
#include "hijack/hijackmanager.h"
#include "winhook/hookcode.h"
#include "memdbg/memsearch.h"
#include <qt_windows.h>
#include <QtCore/QRegExp>
#include <cstdint>

#define DEBUG "model/escude"
#include "sakurakit/skdebug.h"

namespace { // unnamed
namespace ScenarioHook {
namespace Private {

  /**
   *  Sample game: Re;Lord ～ヘルフォルトの魔女とぬいぐるみ～
   *  06AD3604  3C 66 6F 6E 74 20 73 69 7A 65 3D 27 2B 30 27 20  <font size='+0'
   *  06AD3614  61 6C 69 67 6E 3D 27 63 65 6E 74 65 72 27 3E 81  align='center'>・
   *  06AD3624  5C 81 5C 89 E4 81 58 82 CD 82 A2 82 C2 94 73 96  \―我々はいつ敗・
   *  06AD3634  6B 82 B5 82 BD 82 CC 82 BE 81 48 00 AA 90 B6 82  kしたのだ？.ｪ生・
   *  06AD3644  AB 82 E9 82 B1 82 C6 82 A9 81 48 00 00 00 00 00  ｫることか？.....
   *  06AD3654  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
   *  06AD3664  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
   */
  LPCSTR ltrim(LPCSTR text)
  {
    if (*text == '<')
      for (auto p = text; (signed char)*p > 0; p++)
        if (*p == '>')
          return p + 1;
    return text;
  }

  /**
   *  Sample game: Re;Lord ～ヘルフォルトの魔女とぬいぐるみ～, text in arg1+0x20
   *  077CF7D5  2F 00 00 00 DD F7 7C 07 3D C1 B8 06 05 F9 7C 07  /...ﾝ=ﾁｸ
   *  077CF7E5  0A 00 00 00 0A 00 00 00 00 F4 FF FF D0 C3 1C 00  .........・ﾐﾃ.
   *  077CF7F5  54 05 7D 07 2F 00 00 00 30 00 00 00 E7 00 00 00  T}/...0...・..
   *  077CF805  CA 01 00 00 B1 00 00 00 16 00 00 00 00 00 00 00  ﾊ..ｱ..........
   *  077CF815  00 00 00 00 0A 00 00 00 00 00 00 00 00 00 00 00  ................
   *  077CF825  00 00 00 00 00 00 00 00 00 00 00 00 16 00 00 00  ...............
   *
   *  Sample game: 花嫁と魔王WEB専用体験版, text in arg1+0x10
   *  06B0FFFC  2D 00 00 00 04 00 B1 06 E8 A5 01 00 40 00 00 00  -....ｱ隘.@...
   *  06B1000C  9C 08 B1 06 65 00 00 00 40 00 B1 06 C3 6D B4 06  ・ｱe...@.ｱﾃmｴ
   *  06B1001C  01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00  ..............
   *  06B1002C  E0 86 42 07 E8 A5 01 00 40 00 00 00 9C 08 B1 06  煕B隘.@...・ｱ
   *  06B1003C  65 00 00 00 78 04 B1 06 CF 91 B4 06 9C 08 B1 06  e...xｱﾏ其・ｱ
   *  06B1004C  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
   *  06B1005C  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
   *  06B1006C  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
   *  06B1007C  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
   *  06B1008C  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
   *  06B1009C  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
   */
  struct HookArgument
  {
    ulong split;
    //ulong unknown1[3];
    //LPCSTR text1; // 0x10 only for old games
    ulong unknown[7];
    LPCSTR text; // 0x20

    bool isValid() const { return Engine::isAddressWritable(text) && *text; }

    Engine::TextRole role() const
    {
      if (split >= 0xff)
        return Engine::OtherRole;
      static ulong maxSplit_ = 0;
      if (split > maxSplit_)
        maxSplit_ = split;
      if (split == maxSplit_)
        return Engine::ScenarioRole;
      return Engine::NameRole; // scenario role is larger than name role
    }
  };
  bool hookBefore(winhook::hook_stack *s)
  {
    static QByteArray data_;
    auto arg = (HookArgument *)s->stack[1];
    if ((long)arg == -1 || !Engine::isAddressWritable(arg) || !arg->isValid())
      return true;
    auto trimmedText = ltrim(arg->text);
    auto role = arg->role();
    auto sig = Engine::hashThreadSignature(role, arg->split);
    QByteArray oldData = trimmedText,
               newData = EngineController::instance()->dispatchTextA(oldData, role, sig);
    if (newData == oldData)
      return true;
    if (trimmedText != arg->text)
      newData.prepend(arg->text, trimmedText - arg->text);
    data_ = newData;
    arg->text = data_.constData();
    return true;
  }
} // namespace Private

/** jichi 7/23/2015 Escude
 *  Sample game: Re;Lord ～ヘルフォルトの魔女とぬいぐるみ～
 *  See: http://capita.tistory.com/m/post/210
 *
 *  ENCODEKOR,FORCEFONT(5),HOOK(0x0042CB40,TRANS([[ESP+0x4]+0x20],PTRCHEAT,PTRBACKUP,SAFE),RETNPOS(SOURCE)),FONT(Malgun Gothic,-13)
 *
 *  GDI functions: TextOutA, GetTextExtentPoint32A
 *  It requires changing function to MS Gothic using configure.exe
 *
 *  Text in arg1 + 0x20
 *
 *  0042CB3C   CC               INT3
 *  0042CB3D   CC               INT3
 *  0042CB3E   CC               INT3
 *  0042CB3F   CC               INT3
 *  0042CB40   56               PUSH ESI
 *  0042CB41   8B7424 08        MOV ESI,DWORD PTR SS:[ESP+0x8]
 *  0042CB45   8B06             MOV EAX,DWORD PTR DS:[ESI]
 *  0042CB47   50               PUSH EAX
 *  0042CB48   E8 53FC0A00      CALL .004DC7A0
 *  0042CB4D   8B56 04          MOV EDX,DWORD PTR DS:[ESI+0x4]
 *  0042CB50   83C4 04          ADD ESP,0x4
 *  0042CB53   5E               POP ESI
 *  0042CB54   85D2             TEST EDX,EDX
 *  0042CB56   74 7E            JE SHORT .0042CBD6
 *  0042CB58   85C0             TEST EAX,EAX
 *  0042CB5A   74 07            JE SHORT .0042CB63
 *  0042CB5C   8B08             MOV ECX,DWORD PTR DS:[EAX]
 *  0042CB5E   8B49 04          MOV ECX,DWORD PTR DS:[ECX+0x4]
 *  0042CB61   EB 02            JMP SHORT .0042CB65
 *  0042CB63   33C9             XOR ECX,ECX
 *  0042CB65   890A             MOV DWORD PTR DS:[EDX],ECX
 *  0042CB67   85C0             TEST EAX,EAX
 *  0042CB69   74 07            JE SHORT .0042CB72
 *  0042CB6B   8B08             MOV ECX,DWORD PTR DS:[EAX]
 *  0042CB6D   8B49 08          MOV ECX,DWORD PTR DS:[ECX+0x8]
 *  0042CB70   EB 02            JMP SHORT .0042CB74
 *  0042CB72   33C9             XOR ECX,ECX
 *  0042CB74   894A 04          MOV DWORD PTR DS:[EDX+0x4],ECX
 *  0042CB77   85C0             TEST EAX,EAX
 *  0042CB79   74 08            JE SHORT .0042CB83
 *  0042CB7B   8B08             MOV ECX,DWORD PTR DS:[EAX]
 *  0042CB7D   0FB749 0E        MOVZX ECX,WORD PTR DS:[ECX+0xE]
 *  0042CB81   EB 02            JMP SHORT .0042CB85
 *  0042CB83   33C9             XOR ECX,ECX
 *  0042CB85   0FB7C9           MOVZX ECX,CX
 *  0042CB88   894A 08          MOV DWORD PTR DS:[EDX+0x8],ECX
 *  0042CB8B   85C0             TEST EAX,EAX
 *  0042CB8D   74 19            JE SHORT .0042CBA8
 *  0042CB8F   8B08             MOV ECX,DWORD PTR DS:[EAX]
 *  0042CB91   8379 04 00       CMP DWORD PTR DS:[ECX+0x4],0x0
 *  0042CB95   76 11            JBE SHORT .0042CBA8
 *  0042CB97   8B49 08          MOV ECX,DWORD PTR DS:[ECX+0x8]
 *  0042CB9A   85C9             TEST ECX,ECX
 *  0042CB9C   76 0A            JBE SHORT .0042CBA8
 *  0042CB9E   49               DEC ECX
 *  0042CB9F   0FAF48 0C        IMUL ECX,DWORD PTR DS:[EAX+0xC]
 *  0042CBA3   0348 04          ADD ECX,DWORD PTR DS:[EAX+0x4]
 *  0042CBA6   EB 02            JMP SHORT .0042CBAA
 *  0042CBA8   33C9             XOR ECX,ECX
 *  0042CBAA   894A 0C          MOV DWORD PTR DS:[EDX+0xC],ECX
 *  0042CBAD   85C0             TEST EAX,EAX
 *  0042CBAF   74 16            JE SHORT .0042CBC7
 *  0042CBB1   8B48 0C          MOV ECX,DWORD PTR DS:[EAX+0xC]
 *  0042CBB4   F7D9             NEG ECX
 *  0042CBB6   894A 10          MOV DWORD PTR DS:[EDX+0x10],ECX
 *  0042CBB9   8B00             MOV EAX,DWORD PTR DS:[EAX]
 *  0042CBBB   83C0 28          ADD EAX,0x28
 *  0042CBBE   8942 14          MOV DWORD PTR DS:[EDX+0x14],EAX
 *  0042CBC1   B8 01000000      MOV EAX,0x1
 *  0042CBC6   C3               RETN
 *  0042CBC7   33C9             XOR ECX,ECX
 *  0042CBC9   F7D9             NEG ECX
 *  0042CBCB   894A 10          MOV DWORD PTR DS:[EDX+0x10],ECX
 *  0042CBCE   8B00             MOV EAX,DWORD PTR DS:[EAX]
 *  0042CBD0   83C0 28          ADD EAX,0x28
 *  0042CBD3   8942 14          MOV DWORD PTR DS:[EDX+0x14],EAX
 *  0042CBD6   B8 01000000      MOV EAX,0x1
 *  0042CBDB   C3               RETN
 *  0042CBDC   CC               INT3
 *  0042CBDD   CC               INT3
 *  0042CBDE   CC               INT3
 *  0042CBDF   CC               INT3
 *
 *  Sample game: 花嫁と魔王WEB専用体験版
 *  0042CB3E   CC               INT3
 *  0042CB3F   CC               INT3
 *  0042CB40   56               PUSH ESI
 *  0042CB41   8B7424 08        MOV ESI,DWORD PTR SS:[ESP+0x8]
 *  0042CB45   8B06             MOV EAX,DWORD PTR DS:[ESI]
 *  0042CB47   50               PUSH EAX
 *  0042CB48   E8 53FC0A00      CALL .004DC7A0
 *  0042CB4D   8B56 04          MOV EDX,DWORD PTR DS:[ESI+0x4]
 *  0042CB50   83C4 04          ADD ESP,0x4
 *  0042CB53   5E               POP ESI
 *  0042CB54   85D2             TEST EDX,EDX
 *  0042CB56   74 7E            JE SHORT .0042CBD6
 *  0042CB58   85C0             TEST EAX,EAX
 *  0042CB5A   74 07            JE SHORT .0042CB63
 *  0042CB5C   8B08             MOV ECX,DWORD PTR DS:[EAX]
 *  0042CB5E   8B49 04          MOV ECX,DWORD PTR DS:[ECX+0x4]
 *  0042CB61   EB 02            JMP SHORT .0042CB65
 *  0042CB63   33C9             XOR ECX,ECX
 *  0042CB65   890A             MOV DWORD PTR DS:[EDX],ECX
 *  0042CB67   85C0             TEST EAX,EAX
 *  0042CB69   74 07            JE SHORT .0042CB72
 *  0042CB6B   8B08             MOV ECX,DWORD PTR DS:[EAX]
 *  0042CB6D   8B49 08          MOV ECX,DWORD PTR DS:[ECX+0x8]
 *  0042CB70   EB 02            JMP SHORT .0042CB74
 *  0042CB72   33C9             XOR ECX,ECX
 *  0042CB74   894A 04          MOV DWORD PTR DS:[EDX+0x4],ECX
 *  0042CB77   85C0             TEST EAX,EAX
 *  0042CB79   74 08            JE SHORT .0042CB83
 *  0042CB7B   8B08             MOV ECX,DWORD PTR DS:[EAX]
 *  0042CB7D   0FB749 0E        MOVZX ECX,WORD PTR DS:[ECX+0xE]
 *  0042CB81   EB 02            JMP SHORT .0042CB85
 *  0042CB83   33C9             XOR ECX,ECX
 *  0042CB85   0FB7C9           MOVZX ECX,CX
 *  0042CB88   894A 08          MOV DWORD PTR DS:[EDX+0x8],ECX
 *  0042CB8B   85C0             TEST EAX,EAX
 *  0042CB8D   74 19            JE SHORT .0042CBA8
 *  0042CB8F   8B08             MOV ECX,DWORD PTR DS:[EAX]
 *  0042CB91   8379 04 00       CMP DWORD PTR DS:[ECX+0x4],0x0
 *  0042CB95   76 11            JBE SHORT .0042CBA8
 *  0042CB97   8B49 08          MOV ECX,DWORD PTR DS:[ECX+0x8]
 *  0042CB9A   85C9             TEST ECX,ECX
 *  0042CB9C   76 0A            JBE SHORT .0042CBA8
 *  0042CB9E   49               DEC ECX
 *  0042CB9F   0FAF48 0C        IMUL ECX,DWORD PTR DS:[EAX+0xC]
 *  0042CBA3   0348 04          ADD ECX,DWORD PTR DS:[EAX+0x4]
 *  0042CBA6   EB 02            JMP SHORT .0042CBAA
 *  0042CBA8   33C9             XOR ECX,ECX
 *  0042CBAA   894A 0C          MOV DWORD PTR DS:[EDX+0xC],ECX
 *  0042CBAD   85C0             TEST EAX,EAX
 *  0042CBAF   74 16            JE SHORT .0042CBC7
 *  0042CBB1   8B48 0C          MOV ECX,DWORD PTR DS:[EAX+0xC]
 *  0042CBB4   F7D9             NEG ECX
 *  0042CBB6   894A 10          MOV DWORD PTR DS:[EDX+0x10],ECX
 *  0042CBB9   8B00             MOV EAX,DWORD PTR DS:[EAX]
 *  0042CBBB   83C0 28          ADD EAX,0x28
 *  0042CBBE   8942 14          MOV DWORD PTR DS:[EDX+0x14],EAX
 *  0042CBC1   B8 01000000      MOV EAX,0x1
 *  0042CBC6   C3               RETN
 *  0042CBC7   33C9             XOR ECX,ECX
 *  0042CBC9   F7D9             NEG ECX
 *  0042CBCB   894A 10          MOV DWORD PTR DS:[EDX+0x10],ECX
 *  0042CBCE   8B00             MOV EAX,DWORD PTR DS:[EAX]
 *  0042CBD0   83C0 28          ADD EAX,0x28
 *  0042CBD3   8942 14          MOV DWORD PTR DS:[EDX+0x14],EAX
 *  0042CBD6   B8 01000000      MOV EAX,0x1
 *  0042CBDB   C3               RETN
 *  0042CBDC   CC               INT3
 *  0042CBDD   CC               INT3
 */

bool attach(ulong startAddress, ulong stopAddress)
{
  const uint8_t bytes[] = {
    0x76, 0x0a,             // 0042cb9c   76 0a            jbe short .0042cba8
    0x49,                   // 0042cb9e   49               dec ecx
    0x0f,0xaf,0x48, 0x0c    // 0042cb9f   0faf48 0c        imul ecx,dword ptr ds:[eax+0xc]
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
} // unnamed namespace

bool EscudeEngine::attach()
{
  ulong startAddress, stopAddress;
  if (!Engine::getProcessMemoryRange(&startAddress, &stopAddress))
    return false;
  if (!ScenarioHook::attach(startAddress, stopAddress))
    return false;
  HijackManager::instance()->attachFunction((ulong)::TextOutA);
  HijackManager::instance()->attachFunction((ulong)::GetTextExtentPoint32A);
  return true;
}

/**
 *  Example:
 *
 *  その日、彼の言葉に耳を傾ける者はいなかった。
 *  ザールラント歴七九〇年　二ノ月二十日<r>グローセン州　ヘルフォルト区郊外
 *
 *  僅かな震動の後、<r><ruby text='まぶた'>瞼</ruby>の裏を焼く陽光に気付いた。
 *
 *  気怠く重い<ruby text='まぶた'>瞼</ruby>を開けば、<r>見覚えのある輪郭が瞳に映り込む。
 *
 *  その日、彼の言葉に耳を傾ける者はいなかった。――尊厳を捨てて媚びる。それが生きることか？――我々はいつ敗北したのだ？誰しも少年の声を聞かず、蔑み、そして冷笑していた。安寧の世がいつまでも続くと信じていたから。それでも、私は――。ザールラント歴七九〇年　二ノ月二十日<r>グローセン州　ヘルフォルト区郊外僅かな震動の後、<r><ruby text='まぶた'>瞼</ruby>の裏を焼く陽光に気付いた。気怠く重い<ruby text='まぶた'>瞼</ruby>を開けば、<r>見覚えのある輪郭が瞳に映り込む
 */
QString EscudeEngine::rubyCreate(const QString &rb, const QString &rt)
{
  static QString fmt = "<ruby text='%2'>%1</ruby>";
  return fmt.arg(rb, rt);
}

// Remove furigana in scenario thread.
QString EscudeEngine::rubyRemove(const QString &text)
{
  if (!text.contains("<ruby"))
    return text;
  static QRegExp rx("<ruby.*>(.*)</ruby>");
  if (!rx.isMinimal())
    rx.setMinimal(true);
  return QString(text).replace(rx, "\\1");
}

// EOF
