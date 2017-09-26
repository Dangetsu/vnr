# qmltext.pri
# 4/5/2014 jichi
#include(../../../config.pri)
#include($$LIBDIR/qtimage/qtimage.pri)
DEFINES += WITH_LIB_QMLTEXT

DEPENDPATH += $$PWD

QT += core gui declarative

HEADERS += \
  $$PWD/contouredtextedit.h

SOURCES += \
  $$PWD/contouredtextedit.cc

#INCLUDEPATH     += $$QT_SRC

# EOF
