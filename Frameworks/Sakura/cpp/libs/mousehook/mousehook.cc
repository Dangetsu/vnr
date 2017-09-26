// mousehook.cc
// 11/26/2011

#include "mousehook/mousehook.h"
#include <windows.h>

const mousehook_fun_t mousehook_fun_null; // global variable

namespace { // unnamed

struct MouseHookPrivate
{
  HHOOK hook;

  mousehook_fun_t onmove, onlbuttondown, onlbuttonup;

  MouseHookPrivate() : hook(nullptr) {}
};

typedef MouseHookPrivate D;
D *d_; // global, never deleted after allocated

LRESULT CALLBACK MouseProc(__in int nCode, __in WPARAM wparam, __in LPARAM lparam)
{
  // nCode can only be HC_ACTION(0) or HC_NOREMOVE (3)
  // See: http://msdn.microsoft.com/en-us/library/ms644988(v=vs.85).aspx
  if (nCode >= 0 && d_ && d_->hook) {
    // typedef struct tagMOUSEHOOKSTRUCT {
    //   POINT     pt;
    //   HWND      hwnd;
    //   UINT      wHitTestCode;
    //   ULONG_PTR dwExtraInfo;
    // } MOUSEHOOKSTRUCT, *PMOUSEHOOKSTRUCT, *LPMOUSEHOOKSTRUCT;
    LPMOUSEHOOKSTRUCT e = (LPMOUSEHOOKSTRUCT)lparam; // it is actually MOUSEHOOKSTRUCTLL
    mousehook_fun_t callback;
    switch (wparam) {
    case WM_MOUSEMOVE: callback = d_->onmove; break;
    case WM_LBUTTONDOWN: callback = d_->onlbuttondown; break;
    case WM_LBUTTONUP: callback = d_->onlbuttonup; break;
    }

    if (callback) {
      LONG x = e->pt.x;
      LONG y = e->pt.y;
      HWND hwnd = e->hwnd; // this could be zero for desktop events: http://stackoverflow.com/questions/8054287/c-sharp-hook-hwnd-is-always-0
      if (callback(x, y, hwnd))
        return TRUE; // return non-zero value to eat the event
    }
  }

  HHOOK hook = d_ ? d_->hook : nullptr;
  return ::CallNextHookEx(hook, nCode, wparam, lparam);
}

} // unnamed namespace

bool mousehook_active() { return d_ && d_->hook; }

void mousehook_start()
{
  if (!d_)
    d_ = new D;
  if (!d_->hook)
    //enum { hInstance = nullptr, dwThreadId = 0};
    d_->hook = ::SetWindowsHookExA(WH_MOUSE_LL, MouseProc, nullptr, 0);
}

void mousehook_stop()
{
  if (d_ && d_->hook) {
    ::UnhookWindowsHookEx(d_->hook);
    d_->hook = nullptr;
  }
}

void mousehook_restart()
{
  mousehook_stop();
  mousehook_start();
}

void mousehook_onmove(mousehook_fun_t v)
{
  if (!d_)
    d_ = new D;
  d_->onmove = v;
}

void mousehook_onlbuttondown(mousehook_fun_t v)
{
  if (!d_)
    d_ = new D;
  d_->onlbuttondown = v;
}

void mousehook_onlbuttonup(mousehook_fun_t v)
{
  if (!d_)
    d_ = new D;
  d_->onlbuttonup = v;
}

// EOF
