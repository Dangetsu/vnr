# winshell.pri
# 4/7/2013 jichi
win32 {
DEFINES += WITH_LIB_DETOURSUTIL

DEPENDPATH += $$PWD

HEADERS += $$PWD/detoursutil.h
SOURCES += $$PWD/detoursutil.cc

INCLUDEPATH += $$DETOURS_HOME/include
LIBS    += -ldetours -L$$DETOURS_HOME/lib
}

# EOF
