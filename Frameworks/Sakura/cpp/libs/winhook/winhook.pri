# winhook.pri
# 5/25/2015 jichi
win32 {

# This library requires disasm

DEFINES += WITH_LIB_WINHOOK

#LIBS += -lkernel32 -luser32

DEPENDPATH += $$PWD

HEADERS += \
  $$PWD/hookcall.h \
  $$PWD/hookcode.h \
  $$PWD/hookdef.h \
  $$PWD/hookfun.h \
  $$PWD/hookutil.h \
  $$PWD/hookutil_p.h
SOURCES += \
  $$PWD/hookcall.cc \
  $$PWD/hookcode.cc \
  $$PWD/hookfun.cc \
  $$PWD/hookutil.cc \
  $$PWD/hookutil_p.cc
}

# EOF
