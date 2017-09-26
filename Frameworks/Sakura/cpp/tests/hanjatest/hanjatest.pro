# hanjatest.pro
# 8/14/2014

CONFIG += noqtgui
include(../../../config.pri)
include($$LIBDIR/hanjaconv/hanjaconv.pri)
include($$LIBDIR/unistr/unistr.pri)

# Source

TEMPLATE = app
TARGET = hanjatest

DEPENDPATH += .
INCLUDEPATH += .

#HEADERS += main.h
SOURCES += main.cc

# EOF
