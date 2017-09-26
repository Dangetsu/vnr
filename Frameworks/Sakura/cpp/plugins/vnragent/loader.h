#pragma once

// loader.h
// 1/31/2013 jichi
// No Qt can appear in this file.

#include <windows.h>

namespace Loader {

/**
 *  Invoked when attached to the process
 *  @param  hInstance  the main dll instance
 *  @return  if OK
 */
void initWithInstance(HINSTANCE hInstance);

/**
 *  Invoked when detached from the process
 */
void destroy();

} // namespace Main

// EOF
