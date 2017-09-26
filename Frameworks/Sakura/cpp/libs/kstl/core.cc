// kstl/core.cc
// 12/9/2011 jichi
// See: http://wiki.osdev.org/Visual_C%2B%2B_Runtime
#include "kstl/core.h"

// - Constructor loader -

// Linker puts constructors between these sections, and we use them to locate constructor pointers.
#pragma section(".CRT$XIA",long,read)
#pragma section(".CRT$XIZ",long,read)
#pragma section(".CRT$XCA",long,read)
#pragma section(".CRT$XCZ",long,read)
// Put .CRT data into .rdata section
#pragma comment(linker, "-merge:.CRT=.rdata")

namespace { // unnamed

// Constructor prototypes
typedef void (__cdecl *_PVFV)(void);
typedef int  (__cdecl *_PIFV)(void);

// Pointers surrounding constructors
__declspec(allocate(".CRT$XIA")) _PIFV __xi_a[] = { 0 };
__declspec(allocate(".CRT$XIZ")) _PIFV __xi_z[] = { 0 };
__declspec(allocate(".CRT$XCA")) _PVFV __xc_a[] = { 0 };
__declspec(allocate(".CRT$XCZ")) _PVFV __xc_z[] = { 0 };

extern __declspec(allocate(".CRT$XIA")) _PIFV __xi_a[];
extern __declspec(allocate(".CRT$XIZ")) _PIFV __xi_z[];    // C initializers
extern __declspec(allocate(".CRT$XCA")) _PVFV __xc_a[];
extern __declspec(allocate(".CRT$XCZ")) _PVFV __xc_z[];    // C++ initializers


// Call C constructors
inline int _initterm_e(_PIFV *pfbegin, _PIFV *pfend)
{
  int ret = 0;

  // walk the table of function pointers from the bottom up, until
  // the end is encountered.  Do not skip the first entry.  The initial
  // value of pfbegin points to the first valid entry.  Do not try to
  // execute what pfend points to.  Only entries before pfend are valid.
  while (pfbegin < pfend && !ret) {
    if (*pfbegin) // if current table entry is non-NULL, call thru it.
      ret = (**pfbegin)();
    pfbegin++;
  }

  return ret;
}

// Call C++ constructors
inline void _initterm(_PVFV *pfbegin, _PVFV *pfend)
{
  // walk the table of function pointers from the bottom up, until
  // the end is encountered.  Do not skip the first entry.  The initial
  // value of pfbegin points to the first valid entry.  Do not try to
  // execute what pfend points to.  Only entries before pfend are valid.
  while (pfbegin < pfend) {
    if (*pfbegin) // if current table entry is non-NULL, call thru it.
      (**pfbegin)();
     pfbegin++;
  }
}

// Call this function as soon as possible. Basically should be at the moment you
// jump into your C/C++ kernel. But keep in mind that kernel is not yet initialized,
// and you can't use a lot of stuff in your constructors!
inline bool call_ctors_()
{
  // Do C initialization
  if (_initterm_e(__xi_a, __xi_z))
    return false;

   // Do C++ initialization
   _initterm(__xc_a, __xc_z);
   return true;
}

} // unnamed namespace

//
// Data segment with pointers to C++ initializers.
//

// Calls functions the compiler has registred to call constructors
// for global and static objects.
//
extern "C"
void __cdecl kstl_core_load() { call_ctors_(); }

// - Destructor loader -

kstl_atexit *kstl_atexit::current_ = 0;

//
// Calls functions the compiler has registred to call destructors
// for global and static objects.
//
extern "C"
void __cdecl kstl_core_unload() { kstl_atexit::clear(); }

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
// Simple class to keep track of functions registred to be called when
// unloading the driver. Since we only use this internaly from the load
// and unload functions it doesn't need to be thread safe.
//
class AtExitCall {
public:
  AtExitCall(fun_t f) : m_func(f), m_next(m_exit_list) { m_exit_list = this; }
  ~AtExitCall() { m_func(); m_exit_list = m_next; }
  static void run() { while (m_exit_list) delete m_exit_list; }
private:
  fun_t        m_func;
  AtExitCall*     m_next;
  static AtExitCall*  m_exit_list;
};

AtExitCall* AtExitCall::m_exit_list = 0;


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
