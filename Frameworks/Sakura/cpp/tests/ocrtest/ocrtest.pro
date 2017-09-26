# ttstest.pro
# 8/11/2014

CONFIG += console
include(../../../config.pri)
include($$COMDIR/modi/modi.pri)
include($$LIBDIR/modiocr/modiocr.pri)

# Source

TEMPLATE = app
TARGET = ocrtest

DEPENDPATH += .
INCLUDEPATH += .

#HEADERS += main.h
SOURCES += main.cc

# EOF
