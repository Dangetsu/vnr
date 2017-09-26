# ttstest.pro
# 6/15/2014

include(../../../config.pri)
include($$LIBDIR/wintts/wintts.pri)

# Source

TEMPLATE = app
TARGET = ttstest

DEPENDPATH += .
INCLUDEPATH += .

#HEADERS += main.h
SOURCES += main.cc

# EOF
