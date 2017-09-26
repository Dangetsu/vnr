# qtmousesel.pri
# 8/21/2014 jichi
win32 {

DEFINES += WITH_LIB_QTMOUSESEL

QT += core gui

DEPENDPATH += $$PWD

HEADERS += \
  $$PWD/mouseselector_p.h \
  $$PWD/mouseselector.h
SOURCES += \
  $$PWD/mouseselector.cc
}

# EOF
