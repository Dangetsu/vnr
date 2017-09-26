# dyncodectest.pro
# 6/3/2014

include(../../../config.pri)
include($$LIBDIR/qtdyncodec/qtdyncodec.pri)

# Source

TEMPLATE = app
TARGET = dyncodectest

DEPENDPATH += .
INCLUDEPATH += .

SOURCES += main.cc

# EOF
