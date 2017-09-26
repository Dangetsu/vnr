# keyboardhook.pri
# 7/20/2011 jichi
win32 {

DEFINES += WITH_LIB_KEYBOARDHOOK

DEPENDPATH += $$PWD

LIBS += -luser32 # for hook functions

HEADERS += $$PWD/keyboardhook.h
SOURCES += $$PWD/keyboardhook.cc
}

# EOF
