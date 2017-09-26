# sehpatcher.pro
# 10/2/2013

CONFIG += console noqt #nocrt
include(../../../config.pri)
LIBS += -luser32

# Source

TEMPLATE = app
TARGET = sehpatcher

DEPENDPATH += .
INCLUDEPATH += .

SOURCES += main.cc

# EOF
