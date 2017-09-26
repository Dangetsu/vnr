# qtrichruby.pri
# 6/25/2015 jichi

DEFINES += WITH_LIB_QTRICHRUBY

QT += core

DEPENDPATH += $$PWD

HEADERS += \
  $$PWD/richrubyconfig.h \
  $$PWD/richrubyparser.h

SOURCES += \
  $$PWD/richrubyparser.cc

# EOF
