# avtest.pro
# 10/27/2014

include(../../../config.pri)
include($$LIBDIR/avrec/avrec.pri)

QT += core gui
LIBS += -lavcodec -lavformat -lavutil -lswscale

# Source

TEMPLATE = app
TARGET = avtest

DEPENDPATH += .
INCLUDEPATH += .

HEADERS += main.h
SOURCES += main.cc

# EOF
