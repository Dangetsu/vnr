# vertest.pro
# 9/5/2014

include(../../../config.pri)
include($$LIBDIR/winversion/winversion.pri)

# Source

TEMPLATE = app
TARGET = vertest

DEPENDPATH += .
INCLUDEPATH += .

#HEADERS += main.h
SOURCES += main.cc

# EOF
