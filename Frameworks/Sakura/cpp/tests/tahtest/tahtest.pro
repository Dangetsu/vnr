# tahtest.pro
# 8/14/2014

CONFIG += noqtgui
include(../../../config.pri)
include($$LIBDIR/tahscript/tahscript.pri)

# Source

TEMPLATE = app
TARGET = tahtest

DEPENDPATH += .
INCLUDEPATH += .

#HEADERS += main.h
SOURCES += main.cc

# EOF
