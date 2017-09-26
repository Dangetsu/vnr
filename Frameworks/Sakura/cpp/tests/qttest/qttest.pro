# uitest.pro
# 4/5/2014

include(../../../config.pri)
#include($$LIBDIR/qteffects/qteffects.pri)

# Source

INCLUDEPATH     += $$QT_SRC

TEMPLATE = app
TARGET = qttest

DEPENDPATH += .
INCLUDEPATH += .

SOURCES += main.cc

# EOF
