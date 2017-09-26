// krkrz.cc
// 6/15/2015 jichi
// About MES and Silky's arc
// See: http://www.dsl.gr.jp/~sage/mamitool/case/elf/aishimai.html
// MES: http://tieba.baidu.com/p/2068362185
#include "engine/model/elf.h"
#include "engine/enginecontroller.h"
#include "engine/enginedef.h"
#include "engine/engineutil.h"
#include "hijack/hijackmanager.h"
#include "winhook/hookcode.h"
#include "memdbg/memsearch.h"
#include "winasm/winasmdef.h"
#include <qt_windows.h>

#define DEBUG "krkrz"
#include "sakurakit/skdebug.h"

namespace { // unnamed
namespace ScenarioHook {
namespace Private {

  struct TextArgument
  {
    DWORD _unknown1[5];

    DWORD scenarioFlag;  // +4*5, 0 if it is scenario
    DWORD _unknown2[2];
    LPCSTR scenarioText; // +4*5+4*3, could be bad address though
    DWORD _unknown3;

    DWORD nameFlag;      // +4*10, 0 if it is name
    DWORD _unknown4[2];
    char nameText[1];    // +4*10+4*3, could be bad address though
  };

  QByteArray data_;
  TextArgument *scenarioArg_,
               *nameArg_;
  LPCSTR scenarioText_;

  enum { MaxNameSize = 100 };
  char nameText_[MaxNameSize + 1];

  bool hookBefore(winhook::hook_stack *s)
  {
    auto arg = (TextArgument *)s->stack[0]; // arg1 on the top of the stack
    auto q = EngineController::instance();

    // Scenario
    if (arg->scenarioFlag == 0) {
      enum { role = Engine::ScenarioRole };
      // Text from scenario could be bad when open backlog while the character is speaking
      auto text = arg->scenarioText;
      if (!Engine::isAddressReadable(text))
        return true;
      data_ = q->dispatchTextA(text, role);
      scenarioArg_ = arg;
      scenarioText_ = arg->scenarioText;
      arg->scenarioText = (LPCSTR)data_.constData();
    // Name
    // FIXME: The name has to be truncated
    } else if (arg->nameFlag == 0) {
      enum { role = Engine::NameRole };
      auto text = arg->nameText;
      QByteArray oldData = text,
                 newData = q->dispatchTextA(oldData, role);
      if (!newData.isEmpty()) {
        nameArg_ = arg;
        ::memcpy(nameText_, oldData.constData(), qMin(oldData.size() + 1, MaxNameSize));
        ::memcpy(text, newData.constData(), qMin(newData.size() + 1, MaxNameSize));
      }
      //  ::memcpy(text, newData.constData(), qMin(oldData.size(), newData.size()));
      //int left = oldData.size() - newData.size();
      //if (left > 0)
      //  ::memset(text + oldData.size() - left, 0, left);
    }
    return true;
  }

  bool hookAfter(winhook::hook_stack *)
  {
    if (scenarioArg_) {
      scenarioArg_->scenarioText = scenarioText_;
      scenarioArg_ = nullptr;
    }
    if (nameArg_) {
      ::strcpy(nameArg_->nameText, nameText_);
      nameArg_ = nullptr;
    }
    return true;
  }

} // namespace Private

/**
 *  jichi 5/31/2014: elf's
 *  Type1: SEXティーチャー剛史 trial, reladdr = 0x2f0f0, 2 parameters
 *  Type2: 愛姉妹4, reladdr = 0x2f9b0, 3 parameters
 */
bool attach()
{
  ulong startAddress, stopAddress;
  if (!Engine::getProcessMemoryRange(&startAddress, &stopAddress))
    return false;

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
  ulong addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  int count = 0;
  auto fun = [&count](ulong addr) -> bool {
    count += winhook::hook_both(addr, Private::hookBefore, Private::hookAfter);
    return true; // replace all functions
  };
  MemDbg::iterNearCallAddress(fun, addr, startAddress, stopAddress);
  DOUT("call number =" << count);
  return count;

  //lastCaller = MemDbg::findEnclosingAlignedFunction(lastCaller);
  //Private::attached_ = false;
  //return winhook::hook_before(lastCaller, [=](winhook::hook_stack *s) -> bool {
  //  if (Private::attached_)
  //    return true;
  //  Private::attached_ = true;
  //  if (ulong addr = MemDbg::findEnclosingAlignedFunction(s->stack[0])) {
  //    DOUT("dynamic pattern found");
  //    Private::oldHookFun = (Private::hook_fun_t)winhook::replace_fun(addr, (ulong)Private::newHookFun);
  //  }
  //  return true;
  //});
}

} // namespace ScenarioHook
} // unnamed namespace

bool KiriKiriZEngine::attach()
{
  if (!ScenarioHook::attach())
    return false;
  HijackManager::instance()->attachFunction((ulong)::TextOutA);
  return true;
}

/**
 * Pattern: 〈(.*?)〉：?([^〈]+?)(?=〈|$
 * Format: L"【\1】\2"
 */
QString KiriKiriZEngine::textFilter(const QString &text, int role)
{
  if (role != Engine::ScenarioRole)
    return text;
  const wchar_t
    w_angle_open = 0x3008,    /* 〈 */
    w_angle_close = 0x3009,   /* 〉 */
    w_square_open = 0x3010,   /* 【 */
    w_square_close = 0x3011,  /* 】 */
    w_colon = 0xff1a;         /* ： */
  if (text.isEmpty() || text[0] != w_angle_open)
    return text;
  int pos = text.indexOf(w_angle_close);
  if (pos == -1)
    return text;
  QString ret = text;
  ret[0] = w_square_open;
  ret[pos] = w_square_close;
  if (pos + 1 < ret.size() && ret[pos + 1] == w_colon)
    ret.remove(pos + 1, 1);
  return ret;
}

// EOF
