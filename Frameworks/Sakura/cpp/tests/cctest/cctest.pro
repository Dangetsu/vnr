# cctest.pro
# 9/21/2014

CONFIG += noqtgui
include(../../../config.pri)
include($$LIBDIR/simplecc/simplecc.pri)

# Source

TEMPLATE = app
TARGET = cctest

DEPENDPATH += .
INCLUDEPATH += .

#HEADERS += main.h
SOURCES += main.cc

# EOF
