# qtdyncodec.pri
# 6/3/2015 jichi

DEFINES += WITH_LIB_QTDYNCODEC

QT += core

DEPENDPATH += $$PWD

HEADERS += \
  $$PWD/qtdynsjis.h

SOURCES += \
  $$PWD/qtdynsjis.cc

# EOF
