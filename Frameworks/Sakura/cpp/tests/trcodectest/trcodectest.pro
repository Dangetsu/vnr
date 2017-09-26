# trcodectest.pro
# 9/21/2014

CONFIG += noqtgui
include(../../../config.pri)
include($$LIBDIR/trcodec/trcodec.pri)
include($$LIBDIR/trrender/trrender.pri)
include($$LIBDIR/trsym/trsym.pri)

# Source

TEMPLATE = app
TARGET = trcodectest

DEPENDPATH += .
INCLUDEPATH += .

#HEADERS += main.h
SOURCES += main.cc

# EOF
