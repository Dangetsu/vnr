# mousehook.pri
# 11/26/2011 jichi
win32 {

DEFINES += WITH_LIB_MOUSEHOOK

DEPENDPATH += $$PWD

LIBS += -luser32 # for hook functions

HEADERS += $$PWD/mousehook.h
SOURCES += $$PWD/mousehook.cc
}

# EOF
