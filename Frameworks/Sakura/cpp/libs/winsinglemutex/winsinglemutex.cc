// winsinglemutex.cc
// 2/28/2013 jichi
// See: http://bcbjournal.org/articles/vol3/9911/Single-instance_applications.htm
#include "winsinglemutex/winsinglemutex.h"
#include <windows.h>

#ifdef _MSC_VER
# pragma warning (disable:4800)   // C4800: forcing BOOL to bool
#endif // _MSC_VER

namespace { // unnamed

class Singleton
{
  HANDLE hMutex_; // mutex handle

public:
  Singleton() : hMutex_(nullptr) {}
  ~Singleton() { destroy(); }

  bool create(const char *name)
  {
    if (!hMutex_) {
      if (HANDLE h = ::OpenMutexA(MUTEX_ALL_ACCESS, FALSE, name))
        ::CloseHandle(h);
      else
        hMutex_ = ::CreateMutexA(nullptr, FALSE, name);
    }
    return hMutex_;
  }

  void destroy()
  {
    if (hMutex_) {
      ::ReleaseMutex(hMutex_);
      hMutex_ = nullptr;
    }
  }

} singleton;

} // unnamed namespace

// Public namespace

bool WinSingleMutex::acquire(const char *name)
{ return ::singleton.create(name); }

void WinSingleMutex::release()
{ ::singleton.destroy(); }

// EOF
