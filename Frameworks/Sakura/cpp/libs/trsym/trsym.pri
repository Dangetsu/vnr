# trsym.pri
# 5/18/2015 jichi

DEFINES += WITH_LIB_TRSYM

DEPENDPATH += $$PWD

HEADERS += \
  $$PWD/trsym.h \
  $$PWD/trsymdef.h
SOURCES += \
  $$PWD/trsym.cc

# EOF
