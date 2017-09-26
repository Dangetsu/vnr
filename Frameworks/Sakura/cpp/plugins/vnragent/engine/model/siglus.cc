// siglus.cc
// 5/25/2014 jichi
//
// Hooking thiscall: http://tresp4sser.wordpress.com/2012/10/06/how-to-hook-thiscall-functions/
#include "engine/model/siglus.h"
#include "engine/enginecontroller.h"
#include "engine/enginedef.h"
#include "engine/enginehash.h"
#include "engine/enginesettings.h"
#include "engine/engineutil.h"
#include "engine/util/textunion.h"
#include "hijack/hijackmanager.h"
#include "winhook/hookcode.h"
#include "winhook/hookfun.h"
#include <qt_windows.h>
#include <cstdint>

#define DEBUG "model/siglus"
#include "sakurakit/skdebug.h"

// Used to get function's return address
// http://stackoverflow.com/questions/8797943/finding-a-functions-address-in-c
//#pragma intrinsic(_ReturnAddress)

namespace { // unnamed
namespace ScenarioHook {
namespace Private {

  enum Type {
    Type1    // Old SiglusEngine2, arg in ecx
    , Type2  // New SiglusENgine2, arg in arg1, since リア充クラスメイト孕ませ催眠 in 9/26/2014
  } type_; // static

  /**
   *  Sample game: 聖娼女 体験版
   *
   *  IDA: sub_4DAC70 proc near ; Attributes: bp-based frame
   *
   *  Observations:
   *  - return: number of bytes = 2 * number of size
   *  - arg1: unknown pointer, remains the same
   *  - arg2: unknown, remains the same
   *  - this (ecx)
   *    - union
   *      - char x 3: if size < (3 * 2 - 1) &&
   *      - pointer x 4
   *        - 0x0: UTF-16 text
   *        - 0x4: the same as 0x0
   *        - 0x8: unknown variate pointer
   *    - 0xc: wchar_t pointer to a flag, the pointed value is zero when union is used as a char
   *    - 0x10: size of the text without null char
   *    - 0x14: unknown size, always slightly larger than size
   *    - 0x18: constant pointer
   *    ...
   *
   *  Sample stack:
   *  0025edf0  a8 f3 13 0a a8 f3 13 0a  ｨ・.ｨ・.   ; jichi: ecx = 0025edf0
   *            LPCWSTR     LPCWSTR
   *  0025edf8  10 ee 25 00 d0 ee 37 01  ・.ﾐ・
   *            LPCWSTR     LPCWSTR
   *  0025ee00  13 00 00 00 17 00 00 00  ...…
   *            SIZE_T      SIZE_T
   *
   *  0025ee08  18 0c f6 09 27 00 00 00  .・'... ; jichi: following three lines are constants
   *  0025ee10  01 00 00 00 01 00 00 00  ......
   *  0025ee18  d2 d9 5d 9f 1c a2 e7 09  ﾒﾙ]・｢・
   *
   *  0025ee20  40 8c 10 07 00 00 00 00  @・....
   *  0025ee28  00 00 00 00 00 00 00 00  ........
   *  0025ee30  b8 ee ce 0c b8 ee ce 0c  ｸ﨩.ｸ﨩.
   *  0025ee38  b8 ee ce 0c 00 00 00 00  ｸ﨩.....
   *  0025ee40  00 00 00 00 01 00 00 00  .......
   *  0025ee48  00 00 00 00 00 00 00 00  ........
   *  0025ee50  00 00 00 00 00 00 00 00  ........
   *  0025ee58  00 00 00 00 00 00 00 00  ........
   *
   *  0025ee60  01 00 00 00 01 00 00 00  ......
   */
  typedef int (__thiscall *hook_fun_t)(DWORD, DWORD, DWORD); // the first pointer is this
  // Use __fastcall to completely forward ecx and edx
  //typedef int (__fastcall *hook_fun_t)(void *, void *, DWORD, DWORD);
  hook_fun_t oldHookFun;

  /**
   *  Hooking thiscall using fastcall: http://tresp4sser.wordpress.com/2012/10/06/how-to-hook-thiscall-functions/
   *  - thiscall: this is in ecx and the first argument
   *  - fastcall: the first two parameters map to ecx and edx
   */
  int __fastcall newHookFun(DWORD ecx, DWORD edx, DWORD arg1, DWORD arg2)
  {
    Q_UNUSED(edx);
    auto arg = (TextUnionW *)(type_ == Type1 ? ecx : arg1);
    if (!arg || !arg->isValid())
      return oldHookFun(ecx, arg1, arg2); // ret = size * 2

    enum { role = Engine::ScenarioRole, sig = 0 };
    //return oldHookFun(arg, arg1, arg2);

    QString oldText = QString::fromWCharArray(arg->getText(), arg->size),
            newText = EngineController::instance()->dispatchTextW(oldText, role, sig);
    if (newText == oldText)
      return oldHookFun(ecx, arg1, arg2); // ret = size * 2
    if (newText.isEmpty())
      return arg->size * 2; // estimated painted bytes

    auto argValue = *arg;

    arg->setLongText(newText);

    int ret = oldHookFun(ecx, arg1, arg2); // ret = size * 2

    // Restoring is indispensible, and as a result, the default hook does not work
    *arg = argValue;
    return ret;
  }

  /**
   *  jichi 8/16/2013: Insert new siglus hook
   *  See (CaoNiMaGeBi): http://tieba.baidu.com/p/2531786952
   *
   *  013bac6e     cc             int3
   *  013bac6f     cc             int3
   *  013bac70  /$ 55             push ebp ; jichi: function starts
   *  013bac71  |. 8bec           mov ebp,esp
   *  013bac73  |. 6a ff          push -0x1
   *  013bac75  |. 68 d8306201    push siglusen.016230d8
   *  013bac7a  |. 64:a1 00000000 mov eax,dword ptr fs:[0]
   *  013bac80  |. 50             push eax
   *  013bac81  |. 81ec dc020000  sub esp,0x2dc
   *  013bac87  |. a1 90f46b01    mov eax,dword ptr ds:[0x16bf490]
   *  013bac8c  |. 33c5           xor eax,ebp
   *  013bac8e  |. 8945 f0        mov dword ptr ss:[ebp-0x10],eax
   *  013bac91  |. 53             push ebx
   *  013bac92  |. 56             push esi
   *  013bac93  |. 57             push edi
   *  013bac94  |. 50             push eax
   *  ...
   *  013baf32  |. 3bd7           |cmp edx,edi ; jichi: ITH hook here, char saved in edi
   *  013baf34  |. 75 4b          |jnz short siglusen.013baf81
   */
  ulong search(ulong startAddress, ulong stopAddress, Type *type)
  {
    ulong addr;
    {
      const uint8_t bytes1[] = {
        0x3b,0xd7, // 013baf32  |. 3bd7       |cmp edx,edi ; jichi: ITH hook here, char saved in edi
        0x75,0x4b  // 013baf34  |. 75 4b      |jnz short siglusen.013baf81
      };
      addr = MemDbg::findBytes(bytes1, sizeof(bytes1), startAddress, stopAddress);
      if (addr && type)
        *type = Type1;
    }
    if (!addr) {
      const uint8_t bytes2[] = { // 81fe0c300000
        0x81,0xfe, 0x0c,0x30,0x00,0x00 // 0114124a   81fe 0c300000    cmp esi,0x300c  ; jichi: hook here
      };
      addr = MemDbg::findBytes(bytes2, sizeof(bytes2), startAddress, stopAddress);
      if (addr && type)
        *type = Type2;
    }
    if (!addr)
      return 0;

    const uint8_t bytes[] = {
      0x55,      // 013bac70  /$ 55       push ebp ; jichi: function starts
      0x8b,0xec, // 013bac71  |. 8bec     mov ebp,esp
      0x6a,0xff  // 013bac73  |. 6a ff    push -0x1
    };
    //enum { range = 0x300 };   // 0x013baf32 - 0x013bac70 = 706 = 0x2c2
    //enum { range = 0x400 };   // 0x013baf32 - 0x013bac70 = 0x36a
    enum { range = 0x500 };     // 0x00b6bcf8 - 0x00b6b880 = 0x478
    return MemDbg::findBytes(bytes, sizeof(bytes), addr - range, addr);
    //if (!reladdr)
    //  //ConsoleOutput("vnreng:Siglus2: pattern not found");
    //  return 0;
    //addr += reladdr;
    //return addr;
  }

} // namespace Private

bool attach(ulong startAddress, ulong stopAddress) // attach scenario
{
  ulong addr = Private::search(startAddress, stopAddress, &Private::type_);
  if (!addr)
    return false;
  return Private::oldHookFun = (Private::hook_fun_t)winhook::replace_fun(addr, (ulong)Private::newHookFun);
}

} // namespace ScenarioHook

namespace OtherHook {
namespace Private {

  TextUnionW *arg_,
             argValue_;
  bool hookBefore(winhook::hook_stack *s)
  {
    static QString text_;
    auto arg = (TextUnionW *)s->stack[0];
    if (!arg || !arg->isValid())
      return true;

    LPCWSTR text = arg->getText();
    // Skip all ascii
    if (!text || !*text || *text <= 127 || arg->size > Engine::MaxTextSize) // there could be garbage
      return true;

    int role = Engine::OtherRole;
    ulong split = s->stack[3];
    if (split <= 0xffff || !Engine::isAddressReadable(split)) { // skip modifying scenario thread
      //role = Engine::ScenarioRole;
      return true;
    } else {
      split = *(DWORD *)split;
      switch (split) {
      case 0x54:
      case 0x26:
        role = Engine::NameRole;
      }
    }
    auto sig = Engine::hashThreadSignature(role, split);

    QString oldText = QString::fromWCharArray(text, arg->size),
            newText = EngineController::instance()->dispatchTextW(oldText, role, sig);
    if (oldText == newText)
      return true;

    arg_ = arg;
    argValue_ = *arg;

    text_ = newText;
    arg->setLongText(text_);
    return true;
  }

  bool hookAfter(winhook::hook_stack *) // this hookAfter is not needed for this other hook
  {
    if (arg_) {
      *arg_ = argValue_;
      arg_ = nullptr;
    }
    return true;
  }

  ulong search(ulong startAddress, ulong stopAddress)
  {
    const uint8_t bytes[] = {
      0xc7,0x47, 0x14, 0x07,0x00,0x00,0x00,   // 0042cf20   c747 14 07000000 mov dword ptr ds:[edi+0x14],0x7
      0xc7,0x47, 0x10, 0x00,0x00,0x00,0x00,   // 0042cf27   c747 10 00000000 mov dword ptr ds:[edi+0x10],0x0
      0x66,0x89,0x0f,                         // 0042cf2e   66:890f          mov word ptr ds:[edi],cx
      0x8b,0xcf,                              // 0042cf31   8bcf             mov ecx,edi
      0x50,                                   // 0042cf33   50               push eax
      0xe8 //XX4                              // 0042cf34   e8 e725f6ff      call .0038f520 ; jichi: hook here
    };
    enum { addr_offset = sizeof(bytes) - 1 }; // +4 for the call address
    ulong addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
    if (!addr)
      return 0;
    return addr + addr_offset;
  }

} // namespace Private

bool attach(ulong startAddress, ulong stopAddress)
{
  ulong addr = Private::search(startAddress, stopAddress);
  return addr && winhook::hook_both(addr, Private::hookBefore, Private::hookAfter);
}

} // namespace OtherHook

} // unnamed namespace

/** Public class */

bool SiglusEngine::attach()
{
  ulong startAddress, stopAddress;
  if (!Engine::getProcessMemoryRange(&startAddress, &stopAddress))
    return false;
  if (!ScenarioHook::attach(startAddress, stopAddress))
    return false;

  if (OtherHook::attach(startAddress, stopAddress))
    DOUT("other hook found");
  else
    DOUT("other hook NOT FOUND");
  // Allow change font
  HijackManager::instance()->attachFunction((ulong)::GetGlyphOutlineW);
  return true;
}

// EOF
