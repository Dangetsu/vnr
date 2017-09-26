# hanviet.pri
# 2/2/2015 jichi

DEFINES += WITH_LIB_HANVIET

DEPENDPATH += $$PWD

#QT += core

HEADERS += \
  $$PWD/hanvietconv.h \
  $$PWD/phrasedic.h \
  $$PWD/worddic.h

SOURCES += \
  $$PWD/hanvietconv.cc \
  $$PWD/phrasedic.cc \
  $$PWD/worddic.cc

# EOF
