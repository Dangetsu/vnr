# wintts.pri
# 4/7/2013 jichi
win32 {

DEFINES += WITH_LIB_WINTTS

INCLUDEPATH += $$SAPI_HOME/include
LIBS  += -lole32

DEPENDPATH += $$PWD

HEADERS += $$PWD/wintts.h
SOURCES += $$PWD/wintts.cc
}

# EOF
