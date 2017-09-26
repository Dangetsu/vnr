# modiocr.pri
# 8/11/2014 jichi
win32 {

DEFINES += WITH_LIB_MODIOCR

INCLUDEPATH += $$SAPI_HOME/include
LIBS  += -lole32

DEPENDPATH += $$PWD

HEADERS += $$PWD/modiocr.h
SOURCES += $$PWD/modiocr.cc
}

# EOF
