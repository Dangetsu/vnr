# wmpcli.pri
# 10/5/2014 jichi
win32 {

DEFINES += WITH_LIB_WMPCLI

#INCLUDEPATH += $$WMSDK_HOME/include
LIBS  += -lole32

DEPENDPATH += $$PWD

HEADERS += $$PWD/wmpcli.h
SOURCES += $$PWD/wmpcli.cc
}

# EOF
