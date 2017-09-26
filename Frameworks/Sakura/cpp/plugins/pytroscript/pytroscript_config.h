// pytroscript_config.h
// 9/11/2014 jichi

// See: http://qt-project.org/wiki/PySide_Binding_Generation_Tutorial%3A_Module_4_The_Global_Header
#undef QT_NO_STL
#undef QT_NO_STL_WCHAR

#ifndef NULL
# define NULL 0
#endif // NULL

#ifdef __clang__
# pragma clang diagnostic ignored "-Wmissing-field-initializers"
# pragma clang diagnostic ignored "-Wunused-parameter"
#endif // __clang__

//#include <PySide/globalreceiver.h>
//#include <pyside_global.h>  // Essential for Qt applications
//#include <QtCore>
#include "troscript/troscript.h"

// EOF
