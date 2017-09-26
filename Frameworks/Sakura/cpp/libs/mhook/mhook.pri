# mhook.pri
# 6/1/2014 jichi
# See also: detours, MinHook
# Source: https://github.com/martona/mhook/
# Version: http://codefromthe70s.org/mhook24.aspx

win32 {
DEFINES += WITH_LIB_MHOOK
#DEFINES += _M_IX86 # only for x86 machine

DEPENDPATH += $$PWD

HEADERS += $$PWD/mhook.h
SOURCES += $$PWD/mhook.cpp
}

# EOF
