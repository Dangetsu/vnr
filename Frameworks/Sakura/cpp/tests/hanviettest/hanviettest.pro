# hanviettest.pro
# 8/14/2014

CONFIG += noqtgui
include(../../../config.pri)
include($$LIBDIR/hanviet/hanviet.pri)

# Source

TEMPLATE = app
TARGET = hanviettest

DEPENDPATH += .
INCLUDEPATH += .

#HEADERS += main.h
SOURCES += main.cc

# EOF
