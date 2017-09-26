#pragma once

// _windef.h
// 10/11/2014 jichi
// Avoid including Windows.h in the header.

// http://stackoverflow.com/questions/2574549/forward-declare-hinstance-and-friends
#ifndef _WINDEF_
struct HINSTANCE__; // Forward or never
typedef HINSTANCE__ *HINSTANCE;

typedef HINSTANCE HMODULE;
#endif // _WINDEF_

#ifndef MAX_PATH
# define MAX_PATH 260 // 0x104  http://msdn.microsoft.com/en-us/library/cc249520.aspx
#endif // MAX_PATH

// EOF
