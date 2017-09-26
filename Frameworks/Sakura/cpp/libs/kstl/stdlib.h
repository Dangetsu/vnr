#pragma once
// kstl/stdlib.h
// Kernel extensions.
// 12/7/2011 jichi

#ifdef __cplusplus
extern "C" {
#endif // __cplusplus

void * __cdecl malloc(size_t size);
void __cdecl free(void *p);
int __cdecl atexit(void (__cdecl *f)());
void __cdecl abort(); // work in chk mode only

#ifdef __cplusplus
} // extern "C"
#endif // __cplusplus

// EOF
