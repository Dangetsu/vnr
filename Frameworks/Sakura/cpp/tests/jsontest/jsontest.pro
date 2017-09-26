# jsontest.pro
# 4/21/2014

include(../../../config.pri)
include($$LIBDIR/qtjson/qtjson.pri)

# Source

TEMPLATE = app
TARGET = jsontest

DEPENDPATH += .
INCLUDEPATH += .

#HEADERS += main.h
SOURCES += main.cc

# EOF
