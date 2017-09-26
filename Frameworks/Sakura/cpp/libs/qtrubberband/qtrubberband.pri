# qtrubberband.pri
# 8/21/2014 jichi
win32 {

DEFINES += WITH_LIB_QTRUBBERBAND

QT += core gui

DEPENDPATH += $$PWD

HEADERS += $$PWD/mouserubberband.h
SOURCES += $$PWD/mouserubberband.cc
}

# EOF
