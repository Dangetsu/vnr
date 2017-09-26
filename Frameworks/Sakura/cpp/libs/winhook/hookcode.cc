// hookcode.cc
// 5/25/2015 jichi
// Note: FlushInstructionCache is not invoked, which seems is not needed
#include "winhook/hookcode.h"
#include "winhook/hookutil.h"
#include "winhook/hookutil_p.h"
#include "disasm/disasm.h"
#include "ccutil/ccmacro.h"
#include <windows.h>
#include <list>

#ifdef _MSC_VER
# pragma warning(disable:4800) // C4800: forcing value to bool 'true' or 'false'
#endif // _MSC_VER

namespace { // unnamed

namespace detail = winhook::detail; // import detail namespace

// Hook manager

class HookRecord
{
  typedef HookRecord Self;

  DWORD address_,        // the address being hooked
        originalSize_;   // actual size of the instruction at the address
  BYTE *originalCode_,   // original code data as backup, allocated using new
       *hookCode_;       // code data to jump to, allocated with VirtualAlloc
  winhook::hook_function before_, // called before instruction
                         after_;  // called after instruction

  //static void __thiscall callback(Self *self, DWORD esp) // callback from the function
  static void __fastcall callBefore(Self *ecx, void *edx, DWORD esp)
  {
    CC_UNUSED(edx);
    if (ecx->before_)
      ecx->before_((winhook::hook_stack *)esp);
  }

  static void __fastcall callAfter(Self *ecx, void *edx, DWORD esp)
  {
    CC_UNUSED(edx);
    if (ecx->after_)
      ecx->after_((winhook::hook_stack *)esp);
  }

  /**
   *  @param  address  instruction to hook
   *  @param  originalSize  total size of the instruction to replace
   *  @param  self  callback ecx
   *  @param  before  callback before
   *  @param  after  callback after
   *  @return  code data created using VirtualAlloc
   */
  static BYTE *create_hook_code(DWORD address, DWORD originalSize, DWORD self, DWORD before, DWORD after);

public:
  /**
   *  @param  address   address to hook
   *  @param  before   hook function
   *  @param  after   hook function
   */
  HookRecord(DWORD address, const winhook::hook_function &before, const winhook::hook_function &after)
    : address_(address)
    , originalSize_(0)
    , originalCode_(nullptr)
    , hookCode_(nullptr)
    , before_(before)
    , after_(after)
  {
    while (originalSize_ < jmp_ins_size) {
      size_t size = ::disasm(LPCVOID(address + originalSize_));
      if (!size) // failed to decode instruction
        return;
      originalSize_ += size;
    }
    originalCode_ = new BYTE[originalSize_];
    winhook::memcpy_(originalCode_, (LPCVOID)address, originalSize_);
    hookCode_ = create_hook_code(address, originalSize_, (DWORD)this, (DWORD)&Self::callBefore, (DWORD)&Self::callAfter);
  }

  ~HookRecord()
  {
    if (originalCode_) delete originalCode_;
    if (hookCode_) ::VirtualFree(hookCode_, 0, MEM_RELEASE);
  }

  bool isValid() const { return address_ && hookCode_; }

  DWORD address() const { return address_; }

  bool hook() const // assume is valid
  {
    //assert(valid());
    BYTE *jmpCode = new BYTE[originalSize_];
    jmpCode[0] = s1_jmp_;
    *(DWORD *)(jmpCode + 1) = (DWORD)hookCode_ - (address_ + jmp_ins_size);
    if (originalSize_ > jmp_ins_size)
      winhook::memset_(jmpCode + jmp_ins_size, s1_nop, originalSize_ - jmp_ins_size); // patch nop

    bool ret = winhook::csmemcpy((LPVOID)address_, jmpCode, originalSize_);
    delete jmpCode;
    return ret;
  }

  bool unhook() const // assume is valid
  { return winhook::csmemcpy((LPVOID)address_, originalCode_, originalSize_); }
};

BYTE *HookRecord::create_hook_code(DWORD address, DWORD originalSize, DWORD self, DWORD before, DWORD after)
{
// Beginning of the hooked code
#define tpl_init \
    s1_pushad       /* 0 */ \
  , s1_pushfd       /* 1 */ \
  , s1_push_esp     /* 2 */ \
  , s1_mov_ecx_0d   /* 3    ecx = $this */ \
  , s1_call_0d      /* 8    call @hook */ \
  , s1_popfd        /* 13 */ \
  , s1_popad        /* 14 */
  enum {
    tpl_ecx_offset = 3       // offset of s1_mov_ecx_0d
    , tpl_call_offset = 8    // offset of s1_call_0d
  };

// Ending of the hooked code, with the original instruction in the middle
//#define epilog_init
//  s1_jmp_0d // jmp 0,0,0,0

  DWORD instructionSize = ::disasm((LPVOID)address);

  static const BYTE tpl[] = { tpl_init };
  enum { tpl_size = sizeof(tpl) };  // size of the tpl code

  size_t codeSize = tpl_size + originalSize + tpl_size + jmp_ins_size;
  if (codeSize % 2)
    codeSize++; // round code size to 2, patch int3

  BYTE *code = (BYTE *)::VirtualAlloc(nullptr, codeSize, MEM_COMMIT, PAGE_EXECUTE_READWRITE);

  winhook::memcpy_(code, tpl, tpl_size);
  *(DWORD *)(code + tpl_ecx_offset + 1) = self;
  detail::set_call_ins(code + tpl_call_offset, before);

  {
    BYTE *data = code + tpl_size;
    winhook::memcpy_(data, (LPCVOID)address, instructionSize);
    detail::move_code(data, instructionSize, address, (DWORD)data);
  }

  {
    BYTE *data = code + tpl_size + instructionSize;
    winhook::memcpy_(data, tpl, tpl_size);
    *(DWORD *)(data + tpl_ecx_offset + 1) = self;
    detail::set_call_ins(data + tpl_call_offset, after);
  }

  if (instructionSize < originalSize) {
    BYTE *data = code + tpl_size + instructionSize + tpl_size;
    winhook::memcpy_(data, (LPCVOID)(address + instructionSize), originalSize - instructionSize);
    detail::move_code(data, originalSize - instructionSize, address, (DWORD)data);
  }

  detail::set_jmp_ins(code + tpl_size + originalSize + tpl_size, address + originalSize);

  if (codeSize % 2)
    code[codeSize - 1] = s1_nop; // patch the last byte with int3 to be aligned;

  return code;
#undef tpl_init
}

class HookManager
{
  std::list<HookRecord *> hooks_; // not thread-safe

  HookRecord *lookupHookRecord(DWORD address) const
  {
    for (auto it = hooks_.begin(); it != hooks_.end(); ++it) {
      HookRecord *p = *it;
      if (p->address() == address)
        return p;
    }
    return nullptr;
  }

public:
  HookManager() {}
  ~HookManager() {} // HookRecord on heap are not deleted

  bool isAddressHooked(DWORD address) const { return lookupHookRecord(address); }

  bool hook(DWORD address, const winhook::hook_function &before, const winhook::hook_function &after)
  {
    HookRecord *h = new HookRecord(address, before, after);
    if (!h->isValid() || !h->hook()) {
      delete h;
      return false;
    }
    hooks_.push_back(h);
    return true;
  }

  bool unhook(DWORD address)
  {
    for (auto it = hooks_.begin(); it != hooks_.end(); ++it) {
      HookRecord *p = *it;
      if (p->address() == address) {
        bool ret = p->isValid() && p->unhook();
        hooks_.erase(it);
        delete p; // this will crash if the hook code is being executed
        return ret;
      }
    }
    return false;
  }
};

// Global variable
HookManager *hookManager;

} // unnamed namespace

WINHOOK_BEGIN_NAMESPACE

bool hook_before(ulong address, const hook_function &before)
{
  hook_function after;
  return hook_both(address, before, after);
}

bool hook_after(ulong address, const hook_function &after)
{
  hook_function before;
  return hook_both(address, before, after);
}

bool hook_both(ulong address, const hook_function &before, const hook_function &after)
{
  if (!::hookManager)
    ::hookManager = new HookManager;
  //return ::hookManager->hook(address, callback);
  return ::hookManager->hook(address, before, after);
}

bool unhook(ulong address)
{ return ::hookManager && ::hookManager->unhook(address); }

bool hook_contains(ulong address)
{ return ::hookManager && ::hookManager->isAddressHooked(address); }

WINHOOK_END_NAMESPACE

// EOF
