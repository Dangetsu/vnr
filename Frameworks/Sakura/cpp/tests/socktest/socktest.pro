# socktest.pro
# 4/29/2014

CONFIG += noqtgui
include(../../../config.pri)
include($$LIBDIR/qtsocketsvc/qtsocketsvc.pri)

# Source

TEMPLATE = app
TARGET = socktest

DEPENDPATH += .
INCLUDEPATH += .

SOURCES += main.cc

# EOF
