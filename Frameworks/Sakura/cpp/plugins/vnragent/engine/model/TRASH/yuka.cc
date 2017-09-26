// yuka.cc
// 7/18/2015 jichi
#include "engine/model/yuka.h"
#include "engine/enginecontroller.h"
#include "engine/enginedef.h"
#include "engine/enginehash.h"
#include "engine/engineutil.h"
//#include "hijack/hijackmanager.h"
#include "memdbg/memsearch.h"
#include "winhook/hookcode.h"
#include <qt_windows.h>
#include <cstdint>

#define DEBUG "model/yuka"
#include "sakurakit/skdebug.h"

/** Private data */

namespace { // unnamed

namespace ScenarioHook {
namespace Private {

  bool hookBefore(winhook::hook_stack *s)
  {
    static QByteArray data_;
    auto text = (LPSTR)s->stack[2]; // text in arg3
    if (!text || !*text)
      return true;
    //if (::strlen(text) <= 3) // || Util::allAscii(text))
    if ((unsigned char)text[0] <= 127) // skip text beginning with ascii
      return true;

    enum { role = Engine::ScenarioRole };
    auto retaddr = s->stack[7];
    auto sig = Engine::hashThreadSignature(role, retaddr);
    sig = retaddr;
    QString oldText = QString::fromUtf8(text),
            newText = EngineController::instance()->dispatchTextW(oldText, role, sig);
    data_ = newText.toUtf8();
    s->stack[2] = (ulong)data_.constData();
    s->stack[3] = data_.size();
    return true;
  }
} // namespace Private

/**
 *  Sample game: セミラミスの天秤 FD
 */
bool attach(ulong startAddress, ulong stopAddress)
{
  const uint8_t bytes[] = {
    0x55,            // 004010e0  /$ 55             push ebp ; jichi; hook here
    0x8b,0xec,       // 004010e1  |. 8bec           mov ebp,esp
    0x8b,0x45, 0x08, // 004010e3  |. 8b45 08        mov eax,dword ptr ss:[ebp+0x8] ; jichi: ebp+0x8 = arg2
    0x8b,0x4d, 0x0c, // 004010e6  |. 8b4d 0c        mov ecx,dword ptr ss:[ebp+0xc]
    0x8a,0x11,       // 004010e9  |. 8a11           mov dl,byte ptr ds:[ecx]
    0x88,0x10,       // 004010eb  |. 8810           mov byte ptr ds:[eax],dl    ; jichi: eax is the address to text
    0x5d,            // 004010ed  |. 5d             pop ebp
    0xc3             // 004010ee  \. c3             retn
  };
  ulong addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  if (!addr)
    return false;
  addr = 0x00416b2e;
  return winhook::hook_before(addr, Private::hookBefore);
}

} // namespace ScenarioHook

} // unnamed namespace

/** Public class */

bool YukaSystemEngine::attach()
{
  ulong startAddress, stopAddress;
  if (!Engine::getProcessMemoryRange(&startAddress, &stopAddress))
    return false;
  if (!ScenarioHook::attach(startAddress, stopAddress))
    return false;
  //HijackManager::instance()->attachFunction((ulong)::GetGlyphOutlineW);
  return true;
}

// EOF
