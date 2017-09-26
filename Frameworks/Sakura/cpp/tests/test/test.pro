# test.pro
# 12/2/2013

CONFIG += console
include(../../../config.pri)
#include($$LIBDIR/winseh/winseh_safe.pri)
include($$LIBDIR/vnrsharedmemory/vnrsharedmemory.pri)

# Source

TEMPLATE = app
TARGET = test

DEPENDPATH += .
INCLUDEPATH += .

SOURCES += main.cc

# EOF
