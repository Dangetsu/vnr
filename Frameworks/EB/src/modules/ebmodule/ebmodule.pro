# ebmodule.pro
# 3/28/2013 jichi
# Build ebmodule.pyd
#
# Source: https://github.com/aehlke/ebmodule
# Checkout: 3/18/2013

CONFIG += pyplugin noqt nocrt
include(../../../config.pri)

win32:  include($$MODULEDIR/eb/static.pri)
unix:   include($$MODULEDIR/eb/shared.pri)

win32:  DEFINES += EB_EXPORT=__declspec(dllexport)
unix:   DEFINES += EB_EXPORT=

## Sources

TEMPLATE = lib
TARGET = ebmodule

INCLUDEPATH += src
DEPENDPATH += src

SOURCES += src/ebmodule.c

#!wince*: LIBS += -lshell32
#RC_FILE += ebmodule.rc

OTHER_FILES += ChangeLog README

# EOF

