# ceviotts.pri
# 6/15/2014 jichi
win32 {

#include($$COMDIR/cevio/cevio.pri)

DEFINES += WITH_LIB_CEVIOTTS

INCLUDEPATH += $$SAPI_HOME/include
LIBS  += -lole32

DEPENDPATH += $$PWD

HEADERS += $$PWD/ceviotts.h
SOURCES += $$PWD/ceviotts.cc
}

# EOF
