// system43.cc
// 5/25/2015 jichi
#include "engine/model/system4.h"
#include "engine/engineutil.h"
#include <qt_windows.h>

#define DEBUG "model/system4"
#include "sakurakit/skdebug.h"

static bool getMemoryRange(ulong *startAddress, ulong *stopAddress)
{
  //bool patched = IthCheckFile(L"AliceRunPatch.dll");
  bool patched = ::GetModuleHandleA("AliceRunPatch.dll");
  return patched ?
      Engine::getModuleMemoryRange(L"AliceRunPatch.dll", startAddress, stopAddress) :
      Engine::getProcessMemoryRange(startAddress, stopAddress);
}

bool System4Engine::attach()
{
  ulong startAddress, stopAddress;
  if (!::getMemoryRange(&startAddress, &stopAddress))
    return false;
  if (attachSystem43(startAddress, stopAddress)) {
    name = "EmbedSystem43";
    DOUT("found system43");
  } else if (attachSystem44(startAddress, stopAddress)) {
    name = "EmbedSystem44";
    DOUT("found system44");
  } else
    return false;
  return true;
}

// EOF
