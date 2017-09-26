# winsearch.pri
# 4/21/2014 jichi
win32 {

DEFINES += WITH_LIB_WINSEARCH

DEPENDPATH += $$PWD
LIBS += -lkernel32 -luser32

HEADERS += $$PWD/winquery.h
SOURCES += $$PWD/winquery.cc
}

# EOF
