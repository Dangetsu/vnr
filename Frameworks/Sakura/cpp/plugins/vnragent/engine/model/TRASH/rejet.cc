// rejet.cc
// 5/25/2014 jichi
#include "engine/model/rejet.h"
#include "engine/enginedef.h"
#include "engine/enginehash.h"
#include "engine/engineutil.h"
#include "detoursutil/detoursutil.h"
#include "memdbg/memsearch.h"
#include <qt_windows.h>
#include <QtCore/QStringList>

//#define DEBUG "rejet"
#include "sakurakit/skdebug.h"

// Used to get function's return address
// http://stackoverflow.com/questions/8797943/finding-a-functions-address-in-c
//#pragma intrinsic(_ReturnAddress)

/** Private data */

namespace { // unnamed

/**
 *  Sample game: 剣が君
 *  ITH hooked relative address: b3578
 *  Function relative address: b3550
 *
 *  The address to the character is saved in ecx
 *
 *  base: 0x11c0000
 *
 *  Another recursive function found during debug: 51c60
 *  It is called by sub 53c70.
 *  53c70 must be invoked in spinning loop.
 *  When there are texts, it will send the text to 51c60.
 *  It keeps checking ecx[0x4] until it becomes 1.
 *  Then, it will fetch and paint character by character.
 *
 *  Sample ecx:
 *  - 04C51B08  AC 1E 6A 01 01 00 00 00  ｬj...
 *  - 04C51B10  D2 22 22 6C 31 31 00 8C  ﾒ""l11.・
 *
 *  jichi 5/31/2014: This might be a function in D3D DLLs.
 */
typedef int (__stdcall *hook_fun_t)(LPCSTR, LPCSTR, LPCSTR, LPCSTR, int);
hook_fun_t oldHookFun;

int __stdcall newHookFun(LPCSTR text1, LPCSTR text2, LPCSTR text3, LPCSTR text4, int size5)
{
  //return 0;
  //return oldHookFun(text1, text2, text3, text4, size5);
  // Compute ITH signature
  //DWORD returnAddress = (DWORD)_ReturnAddress();
  //      //split = splitOf((DWORD *)fontName1); split is not used
  //auto signature = Engine::hashThreadSignature(returnAddress);
  enum { role = Engine::ScenarioRole, signature = 1 }; // dummy signature
#ifdef DEBUG
  qDebug() << QString::fromLocal8Bit(text1) << ":"
           << QString::fromLocal8Bit(text2) << ":"
           << QString::fromLocal8Bit(text3) << ":"
           << QString::fromLocal8Bit(text4) << ":"
           << size5 << ";"
           << " signature: " << QString::number(signature, 16);
#endif // DEBUG
  //return oldHookFun(text1, text2, text3, text4, size5);
  auto q = AbstractEngine::instance();
  QByteArray data = q->dispatchTextA(text1, role, signature);
  if (!data.isEmpty())
    return oldHookFun(data, text2, text3, text4, size5);
  else
    return 0; // TODO: investigate the return value
}

} // unnamed namespace

/** Public class */

bool RejetEngine::match()
{ return Engine::exists(QStringList() << "gd.dat" << "pf.dat" << "sd.dat"); }

bool RejetEngine::attach()
{
  DWORD startAddress,
        stopAddress;
  if (!Engine::getProcessMemoryRange(&startAddress, &stopAddress))
    return false;
  //enum { sub_esp = 0xec81 }; // caller pattern: sub esp = 0x81,0xec
  //DWORD addr = MemDbg::findCallerAddress((DWORD)::TextOutA, sub_esp, startAddress, stopAddress);
  //DWORD addr = startAddress + 0x4d620; // 剣が君
  //DWORD addr = startAddress + 0xb3578; // 剣が君
  DWORD addr = startAddress + 0xb3550; // 剣が君
  if (!addr)
    return false;
  return ::oldHookFun = detours::replace<hook_fun_t>(addr, ::newHookFun);
}

// EOF

/**
 *  Sample game: 剣が君
 *  .text:0044D620 ; int __stdcall sub_44D620(int, void *, unsigned __int8 *, void *, int)
 *  .text:0044D620 sub_44D620      proc near               ; CODE XREF: sub_438C30+96p
 *  .text:0044D620                                         ; sub_45A190+8Cp
 *  Observations from 剣が君:
 *  - arg1: Scenario text containing HTML tags
 *  - arg2: role name
 *  - arg3: unknown string
 *  - arg4: role name
 *  - arg5: size or width, not sure
 *  - return: unknown
 *
 *  5/25/2014: This is not the correct function to inject
 *  This function is found using Cheat Engine
 *  Two other places found accessing the memory address are:
 *  - ntdll::memmove (modify), the caller of this might be the right function to hijact
 *  - boost xml archive (read-only)
 *
 */
