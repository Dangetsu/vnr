# ceviotest.pro
# 6/15/2014

include(../../../config.pri)
include($$COMDIR/cevio/cevio.pri)
include($$LIBDIR/ceviotts/ceviotts.pri)

# Source

TEMPLATE = app
TARGET = ceviotest

DEPENDPATH += .
INCLUDEPATH += .

#HEADERS += main.h
SOURCES += main.cc

# EOF
