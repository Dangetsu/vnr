# pyreader.pro
# 2/1/2013 jichi

CONFIG += pysideplugin noqtgui
include(../../../config.pri)
include($$LIBDIR/qtmetacall/qtmetacall.pri)
include($$SERVICEDIR/reader/reader.pri)

INCLUDEPATH += $$SERVICEDIR/reader # needed by shiboken
INCLUDEPATH += $$LIBDIR/qtmetacall # needed by shiboken generated code

## Libraries

QT += core network
QT -= gui

INCLUDEPATH += $$PYSIDE_HOME/include/PySide/QtCore

## Sources

TEMPLATE = lib
TARGET = pyreader

SRCPATH = binding/pyreader
INCLUDEPATH += $SRCPATH
DEPENDPATH += $SRCPATH

HEADERS += \
  pyreader_config.h \
  $$SRCPATH/pyreader_python.h \
  $$SRCPATH/metacallpropagator_wrapper.h \
  $$SRCPATH/metacallsocketobserver_wrapper.h \
  $$SRCPATH/readermetacallpropagator_wrapper.h

SOURCES += \
  $$SRCPATH/pyreader_module_wrapper.cpp \
  $$SRCPATH/metacallpropagator_wrapper.cpp \
  $$SRCPATH/metacallsocketobserver_wrapper.cpp \
  $$SRCPATH/readermetacallpropagator_wrapper.cpp

#!wince*: LIBS += -lshell32
#RC_FILE += reader.rc

OTHER_FILES += \
  typesystem_reader.xml \
  update_binding.cmd

# EOF
