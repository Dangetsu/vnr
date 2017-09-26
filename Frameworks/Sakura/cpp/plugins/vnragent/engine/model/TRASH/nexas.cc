// nexas.cc
// 7/6/2014 jichi
#include "engine/model/nexas.h"
#include "engine/enginecontroller.h"
#include "engine/enginedef.h"
#include "engine/enginehash.h"
#include "engine/engineutil.h"
#include "memdbg/memsearch.h"
#include <qt_windows.h>
#include <QtCore/QStringList>

#define DEBUG "nexas"
#include "sakurakit/skdebug.h"

namespace { // unnamed

//typedef int (__thiscall *hook_fun_t)(void *);
// Use __fastcall to completely forward ecx and edx
typedef int (__fastcall *hook_fun_t)(void *, void *);
hook_fun_t oldHookFun;

/**
 *  Observations from BALDRSKYZERO_EXTREME
 *  - Return: text
 *  - Text is calculated from arg1
 */
int __fastcall newHookFun(void *ecx, void *edx)
{
  Q_UNUSED(edx);
  //auto q = EngineController::instance();
  //QByteArray data = q->dispatchTextA("hello", Engine::ScenarioRole, Engine::ScenarioThreadSignature);
  return oldHookFun(ecx, edx);
}

} // unnamed namespace

/**
 *  jichi 7/6/2014: NeXAS from GIGA
 *
 *  004fffec     cc             int3
 *  004fffed     cc             int3
 *  004fffee     cc             int3
 *  004fffef     cc             int3
 *  004ffff0  /$ 55             push ebp
 *  004ffff1  |. 8bec           mov ebp,esp
 *  004ffff3  |. 83e4 f8        and esp,0xfffffff8
 *  004ffff6  |. 8b4e 04        mov ecx,dword ptr ds:[esi+0x4]
 *  004ffff9  |. 53             push ebx
 *  004ffffa  |. 33db           xor ebx,ebx
 *  004ffffc  |. 57             push edi
 *  004ffffd  |. 3bcb           cmp ecx,ebx
 *  004fffff  |. 0f84 b8000000  je bszex.005000bd
 *  00500005  |. 8b01           mov eax,dword ptr ds:[ecx]
 *  00500007  |. 8b90 f8000000  mov edx,dword ptr ds:[eax+0xf8]
 *  0050000d  |. ffd2           call edx
 *  0050000f  |. 84c0           test al,al
 *  00500011  |. 0f84 82000000  je bszex.00500099
 *  00500017  |. 8bbe a0010000  mov edi,dword ptr ds:[esi+0x1a0]
 *  0050001d  |. 899e 38010000  mov dword ptr ds:[esi+0x138],ebx
 *  00500023  |. 899e 3c010000  mov dword ptr ds:[esi+0x13c],ebx
 *  00500029  |. 3bbe a4010000  cmp edi,dword ptr ds:[esi+0x1a4]
 *  0050002f  |. 74 5b          je short bszex.0050008c
 *  00500031  |> 8b07           /mov eax,dword ptr ds:[edi]
 *  00500033  |. 50             |push eax                                ; /arg1
 *  00500034  |. e8 e7350000    |call bszex.00503620                     ; \bszex.00503620
 *  00500039  |. 8b07           |mov eax,dword ptr ds:[edi]
 *  0050003b  |. 8b88 e8010000  |mov ecx,dword ptr ds:[eax+0x1e8]
 *  00500041  |. 8988 54010000  |mov dword ptr ds:[eax+0x154],ecx
 *  00500047  |. 8998 9c010000  |mov dword ptr ds:[eax+0x19c],ebx
 *  0050004d  |. 8b17           |mov edx,dword ptr ds:[edi]
 *  0050004f  |. 8b86 38010000  |mov eax,dword ptr ds:[esi+0x138]
 *  00500055  |. 8b8a cc010000  |mov ecx,dword ptr ds:[edx+0x1cc]
 *  0050005b  |. 3bc1           |cmp eax,ecx
 *  0050005d  |. 7f 02          |jg short bszex.00500061
 *  0050005f  |. 8bc1           |mov eax,ecx
 *  00500061  |> 8986 38010000  |mov dword ptr ds:[esi+0x138],eax
 *  00500067  |. 8b0f           |mov ecx,dword ptr ds:[edi]
 *  00500069  |. 8b86 3c010000  |mov eax,dword ptr ds:[esi+0x13c]
 *  0050006f  |. 8b89 d0010000  |mov ecx,dword ptr ds:[ecx+0x1d0]
 *  00500075  |. 3bc1           |cmp eax,ecx
 *  00500077  |. 7f 02          |jg short bszex.0050007b
 *  00500079  |. 8bc1           |mov eax,ecx
 *  0050007b  |> 83c7 04        |add edi,0x4
 *  0050007e  |. 8986 3c010000  |mov dword ptr ds:[esi+0x13c],eax
 *  00500084  |. 3bbe a4010000  |cmp edi,dword ptr ds:[esi+0x1a4]
 *  0050008a  |.^75 a5          \jnz short bszex.00500031
 *  0050008c  |> 8b4e 04        mov ecx,dword ptr ds:[esi+0x4]
 *  0050008f  |. 8b11           mov edx,dword ptr ds:[ecx]
 *  00500091  |. 8b82 fc000000  mov eax,dword ptr ds:[edx+0xfc]
 *  00500097  |. ffd0           call eax
 *  00500099  |> 8b8e 38010000  mov ecx,dword ptr ds:[esi+0x138]
 *  0050009f  |. 8b96 3c010000  mov edx,dword ptr ds:[esi+0x13c]
 *  005000a5  |. 899e 18020000  mov dword ptr ds:[esi+0x218],ebx
 *  005000ab  |. 899e 1c020000  mov dword ptr ds:[esi+0x21c],ebx
 *  005000b1  |. 898e 20020000  mov dword ptr ds:[esi+0x220],ecx
 *  005000b7  |. 8996 24020000  mov dword ptr ds:[esi+0x224],edx
 *  005000bd  |> 5f             pop edi
 *  005000be  |. 5b             pop ebx
 *  005000bf  |. 8be5           mov esp,ebp
 *  005000c1  |. 5d             pop ebp
 *  005000c2  \. c3             retn
 *  005000c3     cc             int3
 *  005000c4     cc             int3
 */
static ulong searchNeXAS(ulong startAddress, ulong stopAddress, int *stackSize)
{
  const BYTE bytes[] = {
      //0x55,                             // 0093f9b0  /$ 55             push ebp  ; jichi: hook here
      //0x8b,0xec,                        // 0093f9b1  |. 8bec           mov ebp,esp
      //0x83,0xec, 0x08,                  // 0093f9b3  |. 83ec 08        sub esp,0x8
      //0x83,0x7d, 0x10, 0x00,            // 0093f9b6  |. 837d 10 00     cmp dword ptr ss:[ebp+0x10],0x0
      //0x53,                             // 0093f9ba  |. 53             push ebx
      //0x8b,0x5d, 0x0c,                  // 0093f9bb  |. 8b5d 0c        mov ebx,dword ptr ss:[ebp+0xc]
      //0x56,                             // 0093f9be  |. 56             push esi
      //0x57,                             // 0093f9bf  |. 57             push edi
      0x75, 0x0f,                       // 0093f9c0  |. 75 0f          jnz short silkys.0093f9d1
      0x8b,0x45, 0x08,                  // 0093f9c2  |. 8b45 08        mov eax,dword ptr ss:[ebp+0x8]
      0x8b,0x48, 0x04,                  // 0093f9c5  |. 8b48 04        mov ecx,dword ptr ds:[eax+0x4]
      0x8b,0x91, 0x90,0x00,0x00,0x00    // 0093f9c8  |. 8b91 90000000  mov edx,dword ptr ds:[ecx+0x90]
  };
  //enum { hook_offset = 0xc };
  //ulong range = qMin(stopAddress - startAddress, Engine::MaximumMemoryRange);
  ulong addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  //ITH_GROWL_DWORD(reladdr);
  //reladdr = 0x2f9b0; // 愛姉妹4
  //reladdr = 0x2f0f0; // SEXティーチャー剛史 trial

  enum : BYTE { push_ebp = 0x55 };
  for (int i = 0; i < 0x20; i++, addr--) // value of i is supposed to be 0xc or 0x10
    if (*(BYTE *)addr == push_ebp) { // beginning of the function
      // 012df0f0  /$ 55             push ebp   ; funtion starts
      // 012df0f1  |. 8bec           mov ebp,esp
      // 012df0f3  |. 83ec 10        sub esp,0x10
      // 012df0f6  |. 837d 0c 00     cmp dword ptr ss:[ebp+0xc],0x0
      *stackSize = ((BYTE *)addr)[5];
      return addr;
    }
  return 0;
}

bool NeXASEngine::attach()
{
  ulong startAddress,
        stopAddress;
  if (!Engine::getProcessMemoryRange(&startAddress, &stopAddress))
    return false;

  //ulong addr = ::searchNeXAS(startAddress, stopAddress, &stackSize);
  ulong addr = 0x4ffff0; // BALDRSKYZERO_EXTREME
  return ::oldHookFun = Engine::replaceFunction<hook_fun_t>(addr, ::newHookFun);
}

ulong NeXASEngine::search(ulong startAddress, ulong stopAddress)
{
  return 0x4ffff0; // BALDRSKYZERO_EXTREME
}

// caller: 503620: [esi] -> eax
// ushort char = [arg1 + 0x1a8]
// arg1 = eax = [edi]
// edi = [esi+0x1a0] # stack size 4x3
// ecx is a linked list
// data structure: edi = (char *)[] # pointers of wordsjjj
//
// esi is needed to be preserved
void NeXASEngine::hook(HookStack *stack)
{
#define deref(x) *(DWORD *)(x)
  DWORD edi = deref(stack->esi + 0x1a0); // edi = [esi+0x1a0]
  DOUT(edi);
  DWORD eax = deref(edi); // eax = [edi]
  LPCSTR ch = (char *)(eax + 0x1a8); // lea eax+0x1a8
  QString text = QString::fromLocal8Bit(ch);
  EngineController::instance()->dispatchTextW(text, Engine::ScenarioRole, Engine::ScenarioThreadSignature);
  //dmsg(QString::fromLocal8Bit(ret));
 // stack->args[2] = (DWORD)data_.constData(); // reset arg3
#undef deref
}

// EOF
