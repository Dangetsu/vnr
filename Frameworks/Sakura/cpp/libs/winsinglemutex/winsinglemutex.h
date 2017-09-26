#pragma once

// winsinglemutex.h
// 2/28/2013 jichi

namespace WinSingleMutex {

bool acquire(const char *name);
void release();

} // namespace WinSingleMutex

// EOF
