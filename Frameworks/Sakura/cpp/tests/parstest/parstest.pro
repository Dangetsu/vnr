# parstest.pro
# 1/20/2015

CONFIG += console noqt
include(../../../config.pri)

# Source

TEMPLATE = app
TARGET = parstest

DEPENDPATH += .
INCLUDEPATH += .

#HEADERS += main.h
SOURCES += main.cc

# EOF
