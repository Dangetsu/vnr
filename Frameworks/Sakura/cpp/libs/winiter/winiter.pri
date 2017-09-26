# winiter.pri
# 4/29/2014 jichi
win32 {

DEFINES += WITH_LIB_WINITER

LIBS  += -lkernel32 -luser32 -lpsapi

DEPENDPATH += $$PWD

HEADERS += \
  $$PWD/winiter.h \
  $$PWD/winiterps.h \
  $$PWD/winitertl.h
SOURCES += \
  $$PWD/winiter.cc \
  $$PWD/winiterps.cc \
  $$PWD/winitertl.cc
}

# EOF
