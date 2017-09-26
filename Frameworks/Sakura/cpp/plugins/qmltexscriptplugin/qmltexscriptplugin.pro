# qmltexscriptplugin.pro
# 11/12/2011 jichi
# Build qml texscript plugin

CONFIG += qmlplugin
include(../../../config.pri)
include($$LIBDIR/texscript/texscript.pri)

## Sources

TEMPLATE = lib
TARGET  = texscriptplugin

HEADERS += texscriptplugin.h
SOURCES += texscriptplugin.cc

QT += core gui declarative

#!wince*: LIBS += -lshell32
#RC_FILE += qmltexscriptplugin.rc

OTHER_FILES += qmldir

# EOF
