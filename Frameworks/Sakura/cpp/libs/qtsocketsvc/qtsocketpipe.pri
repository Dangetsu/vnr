# qtsocketpipe.pri
# 5/13/2014 jichi
#include(../../../config.pri)
DEFINES += WITH_LIB_QTSOCKETPIPE

DEPENDPATH += $$PWD

QT += core

HEADERS += $$PWD/socketpipe.h

# Needed to implement windows socket pipe
INCLUDEPATH += $$QT_SRC

win32 {
  HEADERS += $$PWD/socketpipe_win.h
  SOURCES += $$PWD/socketpipe_win.cc
}

# EOF
