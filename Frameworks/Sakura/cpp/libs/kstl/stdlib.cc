// kstl/stdlib.cc
// 12/9/2011 jichi
#include "kstl/stdlib.h"
#include "kstl/core.h"
extern "C" {
#include <ntifs.h>
} // extern "C"

//
// The run-time support for RTTI uses malloc and free so we include them here.
//
extern "C"
void * __cdecl malloc(size_t size)
{ return size ? ExAllocatePool(NonPagedPool, size) : 0; }

extern "C"
void __cdecl free(void *p)
{ if (p) ExFreePool(p); }

//
// Simple class to keep track of functions registred to be called when
// unloading the driver. Since we only use this internaly from the load
// and unload functions it doesn't need to be thread safe.
//

//
// Registers a function to be called when unloading the driver. If memory
// couldn't be allocated the function is called immediately since it never
// will be called otherwise.
//
extern "C"
int __cdecl atexit(void (__cdecl *f)(void))
{ return kstl_atexit::add(f) ? 0 : f(), 1; }

//
// When using exception handling the compiler will generate a call to
// SetUnhandledExceptionFilter to install a function that calls abort.
// In a driver there is no top level C++ exception handler to catch an
// unhandled exception so we ignore these but dummy functions must be
// included to link the driver.
//
void __cdecl abort() { ASSERT(FALSE); }

//PVOID
//NTAPI
//SetUnhandledExceptionFilter(PVOID)
//{ return 0; }

// EOF

/*
extern "C" {
#include <ntddk.h>

NTSYSAPI
VOID
NTAPI
RtlRaiseException (
  _In_ PEXCEPTION_RECORD ExceptionRecord
  );

}

#include <typeinfo>

//const char* type_info::name()const
//{
//  return raw_name();
//}

#include "libcpp.h"
#include "new.h"



//
// The statement:
//
//   throw E();
//
// will be translated by the compiler to:
//
//   E e = E();
//   _CxxThrowException(&e, ...);
//
// and _CxxThrowException is implemented as:
//
//   #define CXX_FRAME_MAGIC 0x19930520
//   #define CXX_EXCEPTION   0xe06d7363
//
//   void _CxxThrowException(void *object, cxx_exception_type *type)
//   {
//     ULONG args[3];
//
//     args[0] = CXX_FRAME_MAGIC;
//     args[1] = (ULONG) object;
//     args[2] = (ULONG) type;
//
//     RaiseException(CXX_EXCEPTION, EXCEPTION_NONCONTINUABLE, 3, args);
//   }
//
// so whats left for us to implement is RaiseException
//
///
VOID
NTAPI
RaiseException (
  ULONG   ExceptionCode,
  ULONG   ExceptionFlags,
  ULONG   NumberParameters,
  PULONG  ExceptionInformation
  )
{
  EXCEPTION_RECORD ExceptionRecord = {
    ExceptionCode,
    ExceptionFlags & EXCEPTION_NONCONTINUABLE,
    NULL,
    RaiseException,
    NumberParameters > EXCEPTION_MAXIMUM_PARAMETERS ? EXCEPTION_MAXIMUM_PARAMETERS : NumberParameters
  };

  RtlCopyMemory(
    ExceptionRecord.ExceptionInformation,
    ExceptionInformation,
    ExceptionRecord.NumberParameters * sizeof(ULONG)
    );

  RtlRaiseException(&ExceptionRecord);
}

//
// Internal function to probe memory.
//
static ULONG NTAPI probe(CONST PVOID Buffer, ULONG Length, LOCK_OPERATION Operation)
{
  PMDL  Mdl;
  ULONG   IsBadPtr;

  Mdl = IoAllocateMdl(Buffer, Length, FALSE, FALSE, 0);

  __try
  {
    MmProbeAndLockPages(Mdl, KernelMode, Operation);
    MmUnlockPages(Mdl);
    IsBadPtr = FALSE;
  }
  __except (EXCEPTION_EXECUTE_HANDLER)
  {
    IsBadPtr = TRUE;
  }

  IoFreeMdl(Mdl);

  return IsBadPtr;
}

//
// Used by the run-time support for exception handling.
//

ULONG NTAPI IsBadReadPtr(CONST PVOID Buffer, ULONG Length)
{
  return probe(Buffer, Length, IoReadAccess);
}

ULONG NTAPI IsBadWritePtr(PVOID Buffer, ULONG Length)
{
  return probe(Buffer, Length, IoWriteAccess);
}

ULONG NTAPI IsBadCodePtr(CONST PVOID Buffer)
{
  return probe(Buffer, 1, IoReadAccess);
}

//
// When using exception handling the compiler will generate a call to
// SetUnhandledExceptionFilter to install a function that calls abort.
// In a driver there is no top level C++ exception handler to catch an
// unhandled exception so we ignore these but dummy functions must be
// included to link the driver.
//

void __cdecl abort()
{
  ASSERT(FALSE);
}

PVOID NTAPI SetUnhandledExceptionFilter(PVOID p)
{
  return 0;
}

} // extern "C"
*/
