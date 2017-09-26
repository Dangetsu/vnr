#ifndef CONFIG_H
#define CONFIG_H

#ifdef __clang__
# pragma clang diagnostic ignored "-Wsign-compare"      // compare ssize_t and size_t
# pragma clang diagnostic ignored "-Wunused-parameter"  // "self" not used
# pragma clang diagnostic ignored "-Wunused-variable"   // "i" in eb_bind_booklist
#endif // __clang__

#ifdef _MSC_VER
# pragma warning (disable:4018)   // C4018: signed/unsined mismatch
# pragma warning (disable:4101)   // C4101: unreferenced local variable, "i" in eb_bind_booklist
# pragma warning (disable:4996)   // C4996: use POSIX function
#endif // _MSC_VER

// config.h
// 3/28/2013 jichi
#include "eb/sysdefs.h"

#endif // CONFIG_H
