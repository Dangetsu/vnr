# troscripttest.pro
# 5/17/2015

CONFIG += noqtgui
include(../../../config.pri)
include($$LIBDIR/trrender/trrender.pri)
include($$LIBDIR/troscript/troscript.pri)
include($$LIBDIR/trsym/trsym.pri)

# Source

TEMPLATE = app
TARGET = troscripttest

DEPENDPATH += .
INCLUDEPATH += .

#HEADERS += main.h
SOURCES += main.cc

# EOF
