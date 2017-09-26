#pragma once
// kstl/core.h
// Kernel extensions.
// 12/7/2011 jichi

#ifdef __cplusplus
extern "C" {
#endif // __cplusplus

// start/stop kernel extension service
void __cdecl kstl_core_load();
void __cdecl kstl_core_unload();

#ifdef __cplusplus
} // extern "C"
#endif // __cplusplus

#ifdef __cplusplus
#include "kstl/new.h"
class kstl_atexit
{
  typedef kstl_atexit Self;
public:
  typedef void (__cdecl *function_t)();

  static bool add(function_t f) { return new Self(f); }
  static void clear() { while (current_) delete current_; }

protected:
  explicit kstl_atexit(function_t f) : f_(f), next_(current_) { current_ = this; }
  ~kstl_atexit() { f_(); current_ = next_; }

private:
  function_t f_;
  Self *next_;
  static Self *current_;
};
#endif // __cplusplus

// EOF
