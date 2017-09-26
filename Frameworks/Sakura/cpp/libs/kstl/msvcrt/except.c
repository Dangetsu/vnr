// msvcrt/except.c
// 12/17/2011 jichi
// See: msvcrt/cppexcept.c from wine

#include "kstl/win.h"

// ExceptionCode in the exception record for C++ exceptions
#define CXX_EXCEPTION    0xe06d7363
// ExceptionInformation[0] in the exception record for C++ exceptions
#define CXX_FRAME_MAGIC  0x19930520

// - __CxxFrameHandler -

void __cdecl _global_unwind2(void * pRegistFrame);

typedef void (__cdecl *_se_translator_function)(unsigned int, struct _EXCEPTION_POINTERS*);

_se_translator_function _se_translator;

_se_translator_function __cdecl _set_se_translator(_se_translator_function _new_se_translator)
{
  _se_translator_function _prev_se_translator = _se_translator;
  _se_translator = _new_se_translator;
  return _prev_se_translator;
}

/*
 * The exception frame, used for registering exception handlers
 * Win32 cares only about this, but compilers generally emit
 * larger exception frames for their own use.
 */

struct __EXCEPTION_FRAME;

typedef EXCEPTION_DISPOSITION (__stdcall *PEXCEPTION_HANDLER)(PEXCEPTION_RECORD,struct __EXCEPTION_FRAME*,
                 PCONTEXT,struct __EXCEPTION_FRAME **);

typedef struct __EXCEPTION_FRAME
{
  struct __EXCEPTION_FRAME *Prev;
  PEXCEPTION_HANDLER     Handler;
} EXCEPTION_FRAME, *PEXCEPTION_FRAME;

/*
 * From OS/2 2.0 exception handling
 * Win32 seems to use the same flags as ExceptionFlags in an EXCEPTION_RECORD
 */

#define EH_NONCONTINUABLE   0x01
#define EH_UNWINDING    0x02
#define EH_EXIT_UNWIND    0x04
#define EH_STACK_INVALID  0x08
#define EH_NESTED_CALL    0x10

typedef void (*vtable_ptr)();

/* the object the typeid operator returns a reference to */
typedef struct _type_info
{
  vtable_ptr *vtable;  /* pointer to the objects vtable */
  void     *data;  /* unused in drivers, dynamically allocated undecorated type name in Win32 */
  char    name[1]; /* decorated (raw) type name */
} type_info;

/* the extended exception frame used by C++ */
typedef struct _cxx_exception_frame
{
  EXCEPTION_FRAME frame;  /* the standard exception frame */
  int       trylevel; /* current trylevel */
  ULONG       ebp;    /* saved ebp */
} cxx_exception_frame;

/* info about a single catch {} block */
typedef struct _catchblock_info
{
  unsigned int flags;    /* flags (see TYPE_FLAG_* flags below) */
  type_info   *type_info;  /* C++ type caught by this block */
  int      offset;   /* stack offset to copy exception object to */
  void     (*handler)(); /* catch block handler code */
} catchblock_info;

#define TYPE_FLAG_CONST    1
#define TYPE_FLAG_VOLATILE   2
#define TYPE_FLAG_REFERENCE  8

/* info about a single try {} block */
typedef struct _tryblock_info
{
  int        start_level;    /* start trylevel of that block */
  int        end_level;    /* end trylevel of that block */
  int        catch_level;    /* initial trylevel of the catch block */
  int        catchblock_count; /* count of catch blocks in array */
  catchblock_info *catchblock;     /* array of catch blocks */
} tryblock_info;

/* info about the unwind handler for a given trylevel */
typedef struct _unwind_info
{
  int  prev;     /* prev trylevel unwind handler, to run after this one */
  void (*handler)(); /* unwind handler */
} unwind_info;

/* descriptor of all try blocks of a given function */
typedef struct _cxx_function_descr
{
  unsigned int   magic;      /* must be CXX_FRAME_MAGIC */
  int      unwind_count;   /* number of unwind handlers */
  unwind_info   *unwind_table;   /* array of unwind handlers */
  unsigned int   tryblock_count; /* number of try blocks */
  tryblock_info *tryblock;     /* array of try blocks */
  unsigned int   unknown[3];
} cxx_function_descr;

typedef void (*cxx_copy_ctor)(void);

/* complete information about a C++ type */
typedef struct _cxx_type_info
{
  unsigned int  flags;      /* flags (see CLASS_* flags below) */
  type_info  *type_info;    /* C++ type info */
  int       this_offset;    /* offset of base class this pointer from start of object */
  int       vbase_descr;    /* offset of virtual base class descriptor */
  int       vbase_offset;   /* offset of this pointer offset in virtual base class descriptor */
  size_t    size;       /* object size */
  cxx_copy_ctor copy_constructor; /* copy constructor */
} cxx_type_info;

#define CLASS_IS_SIMPLE_TYPE      1
#define CLASS_HAS_VIRTUAL_BASE_CLASS  4

/* table of C++ types that apply for a given object */
typedef struct _cxx_type_info_table
{
  unsigned int     count;      /* number of types */
  const cxx_type_info *cxx_type_info[1]; /* array of types */
} cxx_type_info_table;

/* type information for an exception object */
typedef struct _cxx_exception_type
{
  unsigned int         flags;       /* TYPE_FLAG_* flags */
  void           (*destructor)();   /* exception object destructor */
  void*            custom_handler;  /* custom handler for this exception */
  const cxx_type_info_table *type_info_table; /* list of types for this exception object */
} cxx_exception_type;

/* installs a new exception handler */
#define cxx_push_handler(handler) __asm {   \
  __asm push offset handler         \
  __asm mov  eax, dword ptr fs:[0]    \
  __asm push eax              \
  __asm mov  dword ptr fs:[0], esp    \
}

/* restores the previous exception handler */
#define cxx_pop_handler() __asm {       \
  __asm mov eax, dword ptr [esp]      \
  __asm mov dword ptr fs:[0], eax     \
  __asm add esp, 8            \
}

/* called when an unrecoverable error has been detected */
void terminate()
{
  DbgPrint("terminate was called\n");
  KeBugCheck(STATUS_DRIVER_INTERNAL_ERROR);
}

/* exception handler for unexpected exceptions thrown while handling an exception */
static EXCEPTION_DISPOSITION __stdcall unexpected_handler(PEXCEPTION_RECORD rec, PEXCEPTION_FRAME frame,
                              PCONTEXT context, void *dispatch)
{
  DbgPrint("unexpected exception\n");
  KeBugCheck(STATUS_DRIVER_INTERNAL_ERROR);
  return ExceptionContinueSearch;
}

/* frame pointer register 'ebp' modified by inline assembly code */
#pragma warning(disable:4731)

/* call a function with a given ebp */
static void *cxx_call_handler(void *func, void *func_ebp)
{
  void *result;

  __asm
  {
    mov  eax, func
    push ebp
    mov  ebp, func_ebp
    call eax
    pop  ebp
    mov  result, eax
  }

  return result;
}

#pragma warning(default:4731)

/* call a copy constructor */
static void cxx_call_copy_constructor(void *func, void *object, void *src_object,
                    int has_vbase)
{
  __asm
  {
    mov  ecx, object
    cmp  has_vbase, 0
    je   no_vbase
    push 1
no_vbase:
    push src_object
    call func
  }
}

/* call the destructor of an object */
static void cxx_call_destructor(void *func, void *object)
{
  __asm
  {
    mov  ecx, object
    call func
  }
}

/* compute the this pointer for a base class of a given type */
static void *get_this_pointer(const cxx_type_info *type, void *object)
{
  void *this_ptr;
  int *offset_ptr;

  if (!type || !object) return NULL;
  this_ptr = (char *)object + type->this_offset;
  if (type->vbase_descr >= 0) {
    /* move this ptr to vbase descriptor */
    this_ptr = (char *)this_ptr + type->vbase_descr;
    /* and fetch additional offset from vbase descriptor */
    offset_ptr = (int *)(*(char **)this_ptr + type->vbase_offset);
    this_ptr = (char *)this_ptr + *offset_ptr;
  }
  return this_ptr;
}

/* check if the exception type is caught by a given catch block, and
   return the type that matched */
static const cxx_type_info *find_caught_type(cxx_exception_type *exception_type,
                       catchblock_info *catchblock)
{
  unsigned int i;

  if (!catchblock->type_info)
    return exception_type->type_info_table->cxx_type_info[0]; /* catch(...) matches any type */


  for (i = 0; i < exception_type->type_info_table->count; i++) {
    const cxx_type_info *type = exception_type->type_info_table->cxx_type_info[i];

    if (catchblock->type_info != type->type_info &&
        strcmp(catchblock->type_info->name, type->type_info->name)) continue;

    /* type is the same, now check the flags */
    if ((exception_type->flags & TYPE_FLAG_CONST) &&
      !(catchblock->flags & TYPE_FLAG_CONST)) continue;
    if ((exception_type->flags & TYPE_FLAG_VOLATILE) &&
      !(catchblock->flags & TYPE_FLAG_VOLATILE)) continue;
    return type;  /* it matched */
  }

  return NULL;
}

/* copy the exception object where the catch block wants it */
static void copy_exception(void *object, cxx_exception_frame *frame,
               catchblock_info *catchblock, const cxx_type_info *type)
{
  void **dest_ptr;

  if (!catchblock->type_info || !catchblock->type_info->name[0]) return;
  if (!catchblock->offset) return;
  dest_ptr = (void **)((char *)&frame->ebp + catchblock->offset);

  if (catchblock->flags & TYPE_FLAG_REFERENCE)
    *dest_ptr = get_this_pointer(type, object);
  else if (type->flags & CLASS_IS_SIMPLE_TYPE) {
    memcpy(dest_ptr, object, type->size);
    /* if it is a pointer, adjust it */
    if (type->size == sizeof(void *)) *dest_ptr = get_this_pointer(type, *dest_ptr);
  } else { /* copy the object */
    if (type->copy_constructor) {
      cxx_push_handler(unexpected_handler);
      cxx_call_copy_constructor(type->copy_constructor, dest_ptr, get_this_pointer(type, object),
        (type->flags & CLASS_HAS_VIRTUAL_BASE_CLASS));
      cxx_pop_handler();
    } else
      memcpy(dest_ptr, get_this_pointer(type, object), type->size);

  }
}

/* unwind the local function up to a given trylevel */
static void cxx_local_unwind(cxx_exception_frame *frame, cxx_function_descr *descr,
               int last_level)
{
  while (frame->trylevel != last_level) {
    if (frame->trylevel < 0 || frame->trylevel >= descr->unwind_count)
      terminate();

    if (descr->unwind_table[frame->trylevel].handler) {
      cxx_push_handler(unexpected_handler);
      cxx_call_handler(descr->unwind_table[frame->trylevel].handler, &frame->ebp);
      cxx_pop_handler();
    }
    frame->trylevel = descr->unwind_table[frame->trylevel].prev;
  }
}

/* global unwind */
static void cxx_global_unwind(PEXCEPTION_FRAME last_frame)
{
  PEXCEPTION_FRAME frame, current_frame, stack_base, stack_top;
  PEXCEPTION_RECORD rec;
  PCONTEXT context;

  __asm
  {
    mov  eax, dword ptr fs:[0]
    mov  dword ptr [current_frame], eax

    mov  eax, dword ptr fs:[4]
    mov  dword ptr [stack_top], eax

    mov  eax, dword ptr fs:[8]
    mov  dword ptr [stack_base], eax
  }

  rec = ExAllocatePool(NonPagedPool, sizeof(EXCEPTION_RECORD));
  memset(rec, 0, sizeof(EXCEPTION_RECORD));
  //rec->ExceptionCode = STATUS_UNWIND;
  rec->ExceptionFlags = EH_UNWINDING;
  rec->ExceptionAddress = 0;
  rec->ExceptionRecord = 0;

  context = ExAllocatePool(NonPagedPool, sizeof(CONTEXT));
  memset(context, 0, sizeof(CONTEXT));

  for (frame = current_frame; frame != last_frame; frame = frame->Prev) {
    //check for possible stack corruption
    if (frame < stack_base ||
        frame + sizeof(EXCEPTION_FRAME) > stack_top ||
        frame > last_frame ||
        (frame->Prev != (PEXCEPTION_FRAME) -1 && frame > frame->Prev))
      terminate();

    cxx_push_handler(unexpected_handler);
    (*frame->Handler)(rec, frame, context, 0);
    cxx_pop_handler();
  }

  ExFreePool(rec);
  ExFreePool(context);

  __asm
  {
    mov  eax, dword ptr [last_frame]
    mov  dword ptr fs:[0], eax
  }
}

/* exception handler for exceptions thrown from a catch block */
static EXCEPTION_DISPOSITION __stdcall catch_block_protector(PEXCEPTION_RECORD rec, PEXCEPTION_FRAME frame,
                               PCONTEXT context, void *dispatch)
{
  if (!(rec->ExceptionFlags & (EH_UNWINDING | EH_EXIT_UNWIND))) {
    /* get the previous exception saved on the stack */
    void* exception_object = (void*) ((ULONG*)frame)[2];
    cxx_exception_type* exception_type = (cxx_exception_type*) ((ULONG*)frame)[3];

    if (rec->ExceptionCode == CXX_EXCEPTION &&
        rec->NumberParameters == 3 &&
        rec->ExceptionInformation[0] == CXX_FRAME_MAGIC &&
        rec->ExceptionInformation[1] == 0 &&
        rec->ExceptionInformation[2] == 0) {
      /* rethrow the previous exception */
      rec->ExceptionInformation[1] = (ULONG) exception_object;
      rec->ExceptionInformation[2] = (ULONG) exception_type;
    } else if (exception_object && exception_type->destructor) { /* throw of new exception, delete the previous exception object */
      cxx_push_handler(unexpected_handler);
      cxx_call_destructor(exception_type->destructor, exception_object);
      cxx_pop_handler();
    }
  }
  return ExceptionContinueSearch;
}

/* find and call the appropriate catch block for an exception */
/* returns the address to continue execution to after the catch block was called */
static void *call_catch_block(PEXCEPTION_RECORD rec, cxx_exception_frame *frame,
                cxx_function_descr *descr)
{
  unsigned int i;
  int j;
  void *ret_addr;
  void *exception_object = (void *) rec->ExceptionInformation[1];
  cxx_exception_type *exception_type = (cxx_exception_type *) rec->ExceptionInformation[2];
  int trylevel = frame->trylevel;

  for (i = 0; i < descr->tryblock_count; i++) {
    tryblock_info *tryblock = &descr->tryblock[i];

    if (trylevel < tryblock->start_level) continue;
    if (trylevel > tryblock->end_level) continue;

    /* got a try block */
    for (j = 0; j < tryblock->catchblock_count; j++) {
      catchblock_info *catchblock = &tryblock->catchblock[j];
      const cxx_type_info *type = find_caught_type(exception_type, catchblock);
      if (!type) continue;

      /* copy the exception to its destination on the stack */
      copy_exception(exception_object, frame, catchblock, type);

      /* unwind the stack */
      _global_unwind2(frame);
      //cxx_global_unwind((PEXCEPTION_FRAME)frame);
      cxx_local_unwind(frame, descr, tryblock->start_level);

      frame->trylevel = tryblock->end_level + 1;

      /* call the catch block */
      __asm push exception_type
      __asm push exception_object
      cxx_push_handler(catch_block_protector);
      ret_addr = cxx_call_handler(catchblock->handler, &frame->ebp);
      cxx_pop_handler();
      __asm add esp, 8

      /* delete the exception object */
      if (exception_object && exception_type->destructor) {
        cxx_push_handler(unexpected_handler);
        cxx_call_destructor(exception_type->destructor, exception_object);
        cxx_pop_handler();
      }
      return ret_addr;
    }
  }
  return NULL;
}

static EXCEPTION_DISPOSITION cxx_frame_handler(PEXCEPTION_RECORD rec, cxx_exception_frame *frame,
                         PCONTEXT context, void *dispatch,
                         cxx_function_descr *descr)
{
  if (descr->magic != CXX_FRAME_MAGIC)
    return ExceptionContinueSearch;

  /* stack unwinding */
  if (rec->ExceptionFlags & (EH_UNWINDING | EH_EXIT_UNWIND)) {
    if (frame->trylevel >= descr->unwind_count) //stack corruption
      terminate();
    if (descr->unwind_count)
      cxx_local_unwind(frame, descr, -1);
  } else if (rec->ExceptionCode != CXX_EXCEPTION) { /* non C++ exception */
    if (_se_translator) {
      EXCEPTION_POINTERS ep = {rec, context};
      (*_se_translator)(rec->ExceptionCode, &ep);
    }
  } else if (rec->NumberParameters == 3 &&
      rec->ExceptionInformation[0] == CXX_FRAME_MAGIC &&
      rec->ExceptionInformation[1] != 0 &&
      rec->ExceptionInformation[2] != 0) { /* C++ exception */

    if (void *ret_addr = call_catch_block(rec, frame, descr)) {
      rec->ExceptionFlags &= ~EH_NONCONTINUABLE;
      context->Eip = (ULONG)ret_addr;
      context->Ebp = (ULONG)&frame->ebp;
      context->Esp = ((ULONG*)frame)[-1];
      return ExceptionContinueExecution;
    }
  }
  return ExceptionContinueSearch;
}

__declspec (naked)
EXCEPTION_DISPOSITION __cdecl __CxxFrameHandler3(
  PEXCEPTION_RECORD     rec,
  PEXCEPTION_FRAME      frame,
  PCONTEXT              context,
  PVOID                 dispatch
)
{
  __asm
  {
    push ebp
    mov  ebp, esp
    cld
    push eax
    push dispatch
    push context
    push frame
    push rec
    call cxx_frame_handler
    mov  esp, ebp
    pop  ebp
    ret  16
  }
}

// - __CxxThrowException -

/*
 * The statement:
 *
 *   throw E();
 *
 * will be translated by the compiler to:
 *
 *   E e = E();
 *   _CxxThrowException(&e, ...);
 *
 * and _CxxThrowException is implemented as:
 *
 *   #define CXX_FRAME_MAGIC 0x19930520
 *   #define CXX_EXCEPTION   0xe06d7363
 *
 *   void _CxxThrowException(void *object, cxx_exception_type *type)
 *   {
 *       ULONG args[3];
 *
 *       args[0] = CXX_FRAME_MAGIC;
 *       args[1] = (ULONG) object;
 *       args[2] = (ULONG) type;
 *
 *       RaiseException(CXX_EXCEPTION, EXCEPTION_NONCONTINUABLE, 3, args);
 *   }
 *
 * so whats left for us to implement is RaiseException
 *
 */
static
VOID
NTAPI
RaiseException(
  ULONG         ExceptionCode,
  ULONG         ExceptionFlags,
  ULONG         NumberParameters,
  _In_ PULONG   ExceptionInformation
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

VOID
_CxxThrowException(PVOID object, cxx_exception_type *type)
{
  ULONG args[3];
  args[0] = CXX_FRAME_MAGIC;
  args[1] = (ULONG) object;
  args[2] = (ULONG) type;
  RaiseException(CXX_EXCEPTION, EXCEPTION_NONCONTINUABLE, 3, args);
}

// EOF
