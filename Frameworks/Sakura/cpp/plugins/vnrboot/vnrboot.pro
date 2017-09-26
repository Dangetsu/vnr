# vnrboot.pro
# 1/22/2013 jichi

CONFIG += noqt dll
include(../../../config.pri)
include($$LIBDIR/disasm/disasm.pri)
include($$LIBDIR/winhook/winhook.pri)
#include($$LIBDIR/windbg/windbg.pri)
#include($$LIBDIR/winiter/winiter.pri)
include($$LIBDIR/winsinglemutex/winsinglemutex.pri)

INCLUDEPATH += $$D3D_HOME/include
#LIBS    += -ld3d9 -L$$D3D_HOME/lib/x86

#LIBS    += -lkernel32
LIBS    += -luser32

## Sources

TEMPLATE = lib
TARGET  = vnrboot

HEADERS += \
  debug.h \
  profile.h

SOURCES += \
  main.cc \
  profile.cc

HEADERS += \
  profile/d3dx.h
  #profile/locale.h

SOURCES += \
  profile/d3dx.cc
  #profile/locale.cc

#!wince*: LIBS += -lshell32
#RC_FILE += vnrboot.rc

OTHER_FILES += vnrboot.rc

# EOF
