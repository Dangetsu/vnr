// keyboardhook.cc
// 7/20/2011

#include "keyboardhook/keyboardhook.h"
#include <windows.h>

const kbhook_fun_t kbhook_fun_null; // global variable

namespace { // unnamed

struct KeyboardHookPrivate
{
  HHOOK hook;

  kbhook_fun_t onkeydown, onkeyup;

  KeyboardHookPrivate() : hook(nullptr) {}
};

typedef KeyboardHookPrivate D;
D *d_; // global, never deleted after allocated

LRESULT CALLBACK KeyboardProc(__in int nCode, __in WPARAM wparam, __in LPARAM lparam)
{
  // nCode can only be HC_ACTION(0) or HC_NOREMOVE (3)
  // See: http://msdn.microsoft.com/en-us/library/ms644988(v=vs.85).aspx
  if (nCode >= 0 && d_ && d_->hook) {
    // typedef struct tagKBDLLHOOKSTRUCT {
    //   DWORD     vkCode;
    //   DWORD     scanCode;
    //   DWORD     flags;
    //   DWORD     time;
    //   ULONG_PTR dwExtraInfo;
    // } KBDLLHOOKSTRUCT, *PKBDLLHOOKSTRUCT, *LPKBDLLHOOKSTRUCT;
    LPKBDLLHOOKSTRUCT e = (LPKBDLLHOOKSTRUCT)lparam; // it is actually MOUSEHOOKSTRUCTLL
    kbhook_fun_t callback;
    switch (wparam) {
    case WM_KEYDOWN: case WM_SYSKEYDOWN: // with ALT
      callback = d_->onkeydown; break;
    case WM_KEYUP: case WM_SYSKEYUP: // with ALT
      callback = d_->onkeyup; break;
    }
    if (callback && callback(e->vkCode))
      return TRUE; // return non-zero value to eat the event
  }
  HHOOK hook = d_ ? d_->hook : nullptr;
  return ::CallNextHookEx(hook, nCode, wparam, lparam);
}

} // unnamed namespace

bool kbhook_active() { return d_ && d_->hook; }

void kbhook_start()
{
  if (!d_)
    d_ = new D;
  if (!d_->hook)
    //enum { hInstance = nullptr, dwThreadId = 0};
    d_->hook = ::SetWindowsHookExA(WH_KEYBOARD_LL, KeyboardProc, nullptr, 0);
}

void kbhook_stop()
{
  if (d_ && d_->hook) {
    ::UnhookWindowsHookEx(d_->hook);
    d_->hook = nullptr;
  }
}

void kbhook_restart()
{
  kbhook_stop();
  kbhook_start();
}

void kbhook_onkeydown(kbhook_fun_t v)
{
  if (!d_)
    d_ = new D;
  d_->onkeydown = v;
}

void kbhook_onkeyup(kbhook_fun_t v)
{
  if (!d_)
    d_ = new D;
  d_->onkeyup = v;
}

// EOF
