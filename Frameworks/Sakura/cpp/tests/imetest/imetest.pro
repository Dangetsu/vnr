# imetest.pro
# 1/5/2015

include(../../../config.pri)
include($$LIBDIR/winime/winime.pri)

LIBS += -lole32

# Source

TEMPLATE = app
TARGET = imetest

DEPENDPATH += .
INCLUDEPATH += .

#HEADERS += main.h
SOURCES += main.cc

# EOF
