# zunkotest.pro
# 10/11/2014

#CONFIG += console noqt
CONFIG += console
include(../../../config.pri)
include($$LIBDIR/voiceroid/aitalked/aitalked.pri)

# Source

TEMPLATE = app
TARGET = zunkotest

DEPENDPATH += .
INCLUDEPATH += .

HEADERS += main.h
SOURCES += main.cc

# EOF
