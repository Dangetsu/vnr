# winasm.pri
# 5/25/2013 jichi
win32 {

DEFINES += WITH_LIB_WINASM

DEPENDPATH += $$PWD

HEADERS += \
  $$PWD/winasm.h \
  $$PWD/winasmdef.h \
  $$PWD/winasmutil.h
#SOURCES += $$PWD/winasm.cc
}

# EOF
