# winime.pri
# 4/1/2013 jichi
win32 {

DEFINES += WITH_LIB_WINIME

INCLUDEPATH += $$MSIME_HOME/include
LIBS += -lole32

DEPENDPATH += $$PWD

HEADERS += $$PWD/winime.h
SOURCES += $$PWD/winime.cc
}

# EOF
