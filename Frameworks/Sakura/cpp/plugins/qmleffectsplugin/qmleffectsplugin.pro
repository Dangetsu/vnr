# qmleffectsplugin.pro
# 11/12/2011 jichi
# Build qml effects plugin

CONFIG += qmlplugin
include(../../../config.pri)
include($$LIBDIR/qteffects/qteffects.pri)

## Sources

TEMPLATE = lib
TARGET = qmleffectsplugin

HEADERS += qmleffectsplugin.h
SOURCES += qmleffectsplugin.cc

QT += core gui declarative

#!wince*: LIBS += -lshell32
#RC_FILE += qmleffectsplugin.rc

OTHER_FILES += qmldir

# EOF
