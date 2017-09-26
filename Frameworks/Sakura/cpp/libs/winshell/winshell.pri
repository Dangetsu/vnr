# winshell.pri
# 4/7/2013 jichi
win32 {
DEFINES += WITH_LIB_WINSHELL

LIBS += -lshell32 -lole32

DEPENDPATH += $$PWD

HEADERS += $$PWD/winshell.h
SOURCES += $$PWD/winshell.cc
}

# EOF
