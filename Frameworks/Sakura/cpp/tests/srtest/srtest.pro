# srtest.pro
# 10/8/2014

include(../../../config.pri)

# Source

TEMPLATE = app
TARGET = srtest

LIBS  += -lole32

DEPENDPATH += .
INCLUDEPATH += .

#HEADERS += main.h
SOURCES += main.cc

# EOF
