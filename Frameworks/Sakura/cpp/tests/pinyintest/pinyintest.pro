# pinyintest.pro
# 1/7/2015

CONFIG += noqtgui
include(../../../config.pri)
include($$LIBDIR/pinyinconv/pinyinconv.pri)

# Source

TEMPLATE = app
TARGET = pinyintest

DEPENDPATH += .
INCLUDEPATH += .

#HEADERS += main.h
SOURCES += main.cc

# EOF
