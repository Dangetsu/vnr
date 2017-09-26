# qtkbsignal.pri
# 9/9/2014 jichi
win32 {

DEFINES += WITH_LIB_QTKBSIGNAL

QT += core

DEPENDPATH += $$PWD

HEADERS += \
  $$PWD/keyboardsignal_p.h \
  $$PWD/keyboardsignal.h
SOURCES += \
  $$PWD/keyboardsignal.cc
}

# EOF
