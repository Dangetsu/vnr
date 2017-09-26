// hookfun.cc
// 5/29/2015 jichi
#include "winhook/hookfun.h"
#include "winhook/hookutil.h"
#include "winhook/hookutil_p.h"
#include "disasm/disasm.h"
#include <windows.h>
#include <list>

namespace { // unnamed

namespace detail = winhook::detail; // import detail namespace

// Hook manager

class HookRecord
{
  typedef HookRecord Self;

  DWORD address_;           // the address being hooked
  BYTE *code_;              // code data to jump to, allocated with VirtualAlloc
  DWORD instructionSize_;   // actual size of the instruction at the address
  DWORD callback_; // hook callback

  /**
   *  @param  address  instruction to hook
   *  @param  method  callback method
   *  @param  self  callback ecx
   *  @param  instructionSize
   *  @return  code data created using VirtualAlloc
   */
  static BYTE *create_code(DWORD address, DWORD callback, DWORD instructionSize);

public:
  /**
   *  @param  address   address to hook
   *  @param  instructionSize  size of the instruction at address
   *  @param  fun   hook function
   */
  HookRecord(DWORD address, DWORD instructionSize, DWORD callback)
    : address_(address)
    , instructionSize_(instructionSize)
    , callback_(callback)
  { code_ = create_code(address, callback, instructionSize); }

  ~HookRecord() { if (code_) ::VirtualFree(code_, 0, MEM_RELEASE); }

  bool isValid() const { return code_ && address_ && instructionSize_; }

  DWORD address() const { return address_; }
  DWORD newFunctionAddress() const { return callback_; }
  DWORD oldFunctionAddress() const { return (DWORD)code_ + jmp_ins_size; }

  bool hook() const // assume is valid
  {
    //assert(valid());
    BYTE *jmpCode = new BYTE[instructionSize_];
    jmpCode[0] = s1_jmp_;
    *(DWORD *)(jmpCode + 1) = (DWORD)code_ - (address_ + jmp_ins_size);
    if (instructionSize_ > jmp_ins_size)
      winhook::memset_(jmpCode + jmp_ins_size, s1_nop, instructionSize_ - jmp_ins_size); // patch nop

    bool ok = winhook::csmemcpy((LPVOID)address_, jmpCode, instructionSize_);
    delete jmpCode;
    return ok;
  }

  bool unhook() const // assume is valid
  {
    //assert(valid());
    return winhook::csmemcpy((LPVOID)address_, code_ + jmp_ins_size, instructionSize_);
  }
};

BYTE *HookRecord::create_code(DWORD address, DWORD callback, DWORD instructionSize)
{
// Beginning of the hooked code
//#define prolog_init
//  s1_jmp_0d /* jmp 0,0,0,0 */
// Ending of the hooked code, with the original instruction in the middle
//#define epilog_init
//  s1_jmp_0d // jmp 0,0,0,0

  //static const BYTE prolog[] = { prolog_init };
  //static const BYTE epilog[] = { epilog_init };

  //enum { prolog_size = jmp_ins_size };  // size of the prolog code
  //enum { epilog_size = jmp_ins_size };  // size of the epilog code

  size_t codeSize = jmp_ins_size + instructionSize + jmp_ins_size;
  if (codeSize % 2)
    codeSize++; // round code size to 2, patch int3

  BYTE *code = (BYTE *)::VirtualAlloc(nullptr, codeSize, MEM_COMMIT, PAGE_EXECUTE_READWRITE);

  winhook::memcpy_(code + jmp_ins_size, (LPCVOID)address, instructionSize);

  detail::set_jmp_ins(code, callback); // prologue
  detail::set_jmp_ins(code + jmp_ins_size + instructionSize, address + instructionSize); // epilogue

  if (codeSize % 2)
    code[codeSize - 1] = s1_nop; // patch the last byte with int3 to be aligned;

  return code;
//#undef prolog_init
//#undef epilog_init
}

class HookManager
{
  std::list<HookRecord *> hooks_; // not thread-safe

public:
  HookManager() {}
  ~HookManager() {} // HookRecord on heap are not deleted

  DWORD hook(DWORD address, DWORD callback)
  {
    size_t instructionSize = 0;
    while (instructionSize < jmp_ins_size) {
      size_t size = ::disasm(LPCVOID(address + instructionSize));
      if (!size) // failed to decode instruction
        return 0;
      instructionSize += size;
    }
    HookRecord *h = new HookRecord(address, instructionSize, callback);
    if (!h->isValid() || !h->hook()) {
      delete h;
      return 0;
    }
    hooks_.push_back(h);
    return h->oldFunctionAddress();
  }

  DWORD unhook(DWORD address)
  {
    for (auto it = hooks_.begin(); it != hooks_.end(); ++it) {
      HookRecord *p = *it;
      if (p->address() == address) {
        DWORD ret = p->newFunctionAddress();
        if (p->isValid())
          p->unhook();
        hooks_.erase(it);
        delete p; // this will crash if the hook code is being executed
        return ret;
      }
    }
    return 0;
  }
};

// Global variable
HookManager *hookManager;

} // unnamed namespace

WINHOOK_BEGIN_NAMESPACE

ulong replace_fun(ulong oldfun, ulong newfun)
{
  if (!::hookManager)
    ::hookManager = new HookManager;
  return ::hookManager->hook(oldfun, newfun);
}

ulong restore_fun(ulong address)
{
  if (!::hookManager)
   return 0;
  return ::hookManager->unhook(address);
}

WINHOOK_END_NAMESPACE

// EOF
