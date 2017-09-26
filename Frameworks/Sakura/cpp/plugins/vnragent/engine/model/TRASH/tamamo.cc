// tamamo.cc
// 8/23/2015 jichi
#include "engine/model/tamamo.h"
#include "engine/enginecontroller.h"
#include "engine/enginedef.h"
#include "engine/engineutil.h"
#include "hijack/hijackmanager.h"
#include "util/textutil.h"
#include "memdbg/memsearch.h"
#include "winhook/hookcode.h"
#include <qt_windows.h>
#include <cstdint>

#define DEBUG "model/tamamo"
#include "sakurakit/skdebug.h"

/** Private data */

namespace { // unnamed

namespace ScenarioHook { // for new Tamamo2
namespace Private {
  bool hookBefore(winhook::hook_stack *s)
  {
    static QByteArray data_; // persistent storage, which makes this function not thread-safe
    auto text = (LPCSTR)s->stack[1]; // arg2
    int size = s->stack[2]; // arg3
    if (size <= 0 || !text || ::strlen(text) != size)
      return true;

    auto retaddr = s->stack[6]; // parent function retaddr, pseudo arg7
    if (retaddr == 0x12fc38)
      return true;
    // 00187E7F  |. E8 CCDAFBFF    CALL play.00145950
    // 00187E84  |> 8A45 0C        MOV AL,BYTE PTR SS:[EBP+0xC]
    auto role = Engine::OtherRole;
    QByteArray oldData = text,
               newData = EngineController::instance()->dispatchTextA(oldData, role, retaddr);
    if (newData == oldData)
      return true;
    data_ = newData;
    s->stack[1] = (ulong)data_.constData(); // arg2
    s->stack[2] = data_.size(); // arg3
    return true;
  }
} // namespace Private

/**
 *  Sample game: 閃光の騎士 ～カリスティアナイト～ Ver1.03
 *
 *  Debugging method: insert hw breakpoint to the text in memory
 *
 *  006107A6   76 08            JBE SHORT .006107B0
 *  006107A8   3BF8             CMP EDI,EAX
 *  006107AA   0F82 68030000    JB .00610B18
 *  006107B0   0FBA25 F88E7300 >BT DWORD PTR DS:[0x738EF8],0x1
 *  006107B8   73 07            JNB SHORT .006107C1
 *  006107BA   F3:A4            REP MOVS BYTE PTR ES:[EDI],BYTE PTR DS:[>	; jichi: accessed here
 *  006107BC   E9 17030000      JMP .00610AD8
 *  006107C1   81F9 80000000    CMP ECX,0x80
 *  006107C7   0F82 CE010000    JB .0061099B
 *  006107CD   8BC7             MOV EAX,EDI
 *  006107CF   33C6             XOR EAX,ESI
 *  006107D1   A9 0F000000      TEST EAX,0xF
 *  006107D6   75 0E            JNZ SHORT .006107E6
 *
 *  0012FD7C   0012FE1C
 *  0012FD80   00000059
 *  0012FD84   0051C298  RETURN to .0051C298 from .00610790
 *  0012FD88   0207E490	; jichi: target
 *  0012FD8C   0C0BE768	; jichi: source text
 *  0012FD90   00000059	; jichi: source size
 *  0012FD94   002A7C58
 *  0012FD98   0C1E7338
 *  0012FD9C   0012FE1C
 *  0012FDA0  /0012FDC0
 *  0012FDA4  |0056A83F  RETURN to .0056A83F from .0051C1C0
 *  0012FDA8  |0C1E733C
 *  0012FDAC  |00000000
 *  0012FDB0  |FFFFFFFF
 *  0012FDB4  |020EDAD0
 *  0012FDB8  |0220CC28
 *  0012FDBC  |020EDAD0
 *  0012FDC0  ]0012FE44
 *  0012FDC4  |0055EF84  RETURN to .0055EF84 from .0056A7B0
 *  0012FDC8  |0012FE1C
 *  0012FDCC  |ED1BC1C5
 *  0012FDD0  |020EDAD0
 *  0012FDD4  |002998A8
 *  0012FDD8  |020EDAD0
 *
 *  Hooked call:
 *  0051C283   5D               POP EBP
 *  0051C284   C2 0C00          RETN 0xC
 *  0051C287   8BD6             MOV EDX,ESI
 *  0051C289   85FF             TEST EDI,EDI
 *  0051C28B   74 0E            JE SHORT .0051C29B
 *  0051C28D   57               PUSH EDI
 *  0051C28E   8D040B           LEA EAX,DWORD PTR DS:[EBX+ECX]
 *  0051C291   50               PUSH EAX
 *  0051C292   52               PUSH EDX
 *  0051C293   E8 F8440F00      CALL .00610790    ; jichi: copy invoked here
 *  0051C298   83C4 0C          ADD ESP,0xC
 *  0051C29B   837E 14 10       CMP DWORD PTR DS:[ESI+0x14],0x10
 *  0051C29F   897E 10          MOV DWORD PTR DS:[ESI+0x10],EDI
 *  0051C2A2   72 0F            JB SHORT .0051C2B3
 *  0051C2A4   8B06             MOV EAX,DWORD PTR DS:[ESI]
 *  0051C2A6   C60438 00        MOV BYTE PTR DS:[EAX+EDI],0x0
 *  0051C2AA   8BC6             MOV EAX,ESI
 *  0051C2AC   5F               POP EDI
 *  0051C2AD   5E               POP ESI
 *  0051C2AE   5B               POP EBX
 *  0051C2AF   5D               POP EBP
 *  0051C2B0   C2 0C00          RETN 0xC
 *  0051C2B3   8BC6             MOV EAX,ESI
 *
 *  Sample text with new lines:
 *
 *  0C0BE748  70 00 69 00 2E 00 64 00 6C 00 6C 00 00 00 6C 00  p.i...d.l.l...l.
 *  0C0BE758  00 00 00 00 0F 00 00 00 8B 91 3F 66 00 00 00 88  .......拒?f...・
 *  0C0BE768  83 4E 83 8B 83 67 83 93 81 75 8E 84 82 C9 82 CD  クルトン「私には
 *  0C0BE778  95 90 91 95 82 AA 82 C2 82 A2 82 C4 82 A2 82 DC  武装がついていま
 *  0C0BE788  82 B9 82 F1 82 A9 82 E7 81 41 0D 0A 81 40 8D 55  せんから、..　攻
 *  0C0BE798  82 DF 82 C4 82 B1 82 E7 82 EA 82 BD 82 E7 82 D0  めてこられたらひ
 *  0C0BE7A8  82 C6 82 BD 82 DC 82 E8 82 E0 82 A0 82 E8 82 DC  とたまりもありま
 *  0C0BE7B8  82 B9 82 F1 81 76 3C 65 3E 00 3E 00 3E 00 00 00  せん」<e>.>.>...
 *  0C0BE7C8  9E 91 3F 66 99 82 00 88 83 53 83 8D 81 5B 83 93  梠?f凾.・Sローン
 *  0C0BE7D8  8C 5A 81 75 82 D6 82 D6 81 42 95 D4 82 B5 82 C4  兄「へへ。返して
 *  0C0BE7E8  82 D9 82 B5 82 AF 82 E8 82 E1 82 C2 82 A2 82 C4  ほしけりゃついて
 *  0C0BE7F8  82 AB 82 C8 81 42 83 49 83 8C 82 B3 82 DC 82 CC  きな。オレさまの
 */
bool attach(ulong startAddress, ulong stopAddress)
{
  const uint8_t bytes[] = {
    0x8b,0xd6,      // 0051c287   8bd6             mov edx,esi
    0x85,0xff,      // 0051c289   85ff             test edi,edi
    0x74, 0x0e,     // 0051c28b   74 0e            je short .0051c29b
    0x57,           // 0051c28d   57               push edi
    0x8d,0x04,0x0b, // 0051c28e   8d040b           lea eax,dword ptr ds:[ebx+ecx]
    0x50,           // 0051c291   50               push eax
    0x52,           // 0051c292   52               push edx
    0xe8 //f8440f00 // 0051c293   e8 f8440f00      call .00610790    ; jichi: copy invoked here
  };
  enum { addr_offset = sizeof(bytes) - 1 };
  ulong addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  return addr && winhook::hook_before(addr + addr_offset, Private::hookBefore);
}
} // namespace ScenarioHook

} // unnamed namespace

/** Public class */

bool TamamoEngine::attach()
{
  ulong startAddress, stopAddress;
  if (!Engine::getProcessMemoryRange(&startAddress, &stopAddress))
    return false;
  if (!ScenarioHook::attach(startAddress, stopAddress))
    return true;
  HijackManager::instance()->attachFunction((ulong)::GetGlyphOutlineA);
  return true;
}

// EOF
