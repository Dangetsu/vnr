# qmlgradient.pri
# 9/14/2014 jichi
#include(../../../config.pri)
DEFINES += WITH_LIB_QMLGRADIENT

DEPENDPATH += $$PWD

QT += core gui declarative

HEADERS += \
  $$PWD/lineargradient.h

SOURCES += \
  $$PWD/lineargradient.cc

#INCLUDEPATH     += $$QT_SRC

# EOF
