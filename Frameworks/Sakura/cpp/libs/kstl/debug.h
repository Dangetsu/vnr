#pragma once
// kstl/debug.h
// 12/10/2011 jichi

#ifndef kstl_dprint
//#define kstl_dprint KdPrint
# define kstl_dprint DbgPrint
#endif // kstl_dprint

#ifdef DEBUG
# define KDPRINT(_fmt, ...)     kstl_dprint(("%s: " _fmt), DEBUG ": " __FUNCTION__, __VA_ARGS__)
# define KDPRINT_SEPARATOR()    kstl_dprint("################################################################");
#else
# define KDPRINT(_fmt, ...)     (void)0
# define KDPRINT_SEPARATOR()    (void)0
//# pragma warning (disable:4390)   // c4390: empty controlled statement found: is this the intent?
#endif // DEBUG

// EOF
