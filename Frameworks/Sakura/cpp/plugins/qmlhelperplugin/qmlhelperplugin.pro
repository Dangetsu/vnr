# qmlhelperplugin.pro
# 11/12/2011 jichi
# Build qmlhelper plugin

CONFIG += qmlplugin
include(../../../config.pri)
include($$LIBDIR/qtprivate/d/d.pri)
include($$LIBDIR/qtmeta/qtmeta.pri)

## Sources

TEMPLATE = lib
TARGET = qmlhelperplugin

HEADERS += \
  qmlhelperplugin.h \
  qmlhelper_p.h \
  qthelper_p.h
SOURCES += \
  qmlhelperplugin.cc \
  qmlhelper_p.cc \
  qthelper_p.cc

QT += core gui declarative

#!wince*: LIBS += -lshell32
#RC_FILE += qmlhelperplugin.rc

OTHER_FILES += qmldir

# EOF
