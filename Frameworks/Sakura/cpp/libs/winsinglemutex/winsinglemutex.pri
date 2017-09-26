# winsinglemutex.pri
# 2/28/2013 jichi
# Currently, only implemented for windows
win32 {

DEFINES += WITH_LIB_WINSINGLEMUTEX

DEPENDPATH += $$PWD

HEADERS += $$PWD/winsinglemutex.h
win32: SOURCES += $$PWD/winsinglemutex.cc

#LIBS    += -lkernel32 -luser32

} # windows

# EOF
