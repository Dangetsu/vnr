# qmlgradientplugin.pro
# 9/14/2011 jichi
# Build qml gradient plugin

CONFIG += qmlplugin
include(../../../config.pri)
include($$LIBDIR/qmlgradient/qmlgradient.pri)

## Sources


TEMPLATE = lib
TARGET  = qmlgradientplugin

HEADERS += qmlgradientplugin.h
SOURCES += qmlgradientplugin.cc

QT += core gui declarative

#!wince*: LIBS += -lshell32
#RC_FILE += qmlgradientplugin.rc

OTHER_FILES += qmldir

# EOF
