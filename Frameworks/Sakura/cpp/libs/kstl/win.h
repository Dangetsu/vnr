#pragma once
// win.h
// 12/13/2011
#ifdef __cplusplus
extern "C" {
#endif // __cplusplus

// - ntifs.h -
#include "ntifs.h"

// - ntddk.h -
extern
NTSYSAPI
VOID
NTAPI
RtlRaiseException (
  _In_ PEXCEPTION_RECORD ExceptionRecord
);

#ifdef __cplusplus
} // extern "C"
#endif // __cplusplus
// EOF
