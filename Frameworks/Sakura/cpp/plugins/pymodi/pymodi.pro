# pymodi.pro
# 8/13/2014 jichi
# Build pymodi.pyd
#
# Though Qt is not indispensible, shiboken could save me some time for development.
# Switch to pure PyC and get rid of QStringList if it becomes a performance bottle neck.

CONFIG += pysideplugin noqtgui
include(../../../config.pri)
include($$COMDIR/modi/modi.pri)
include($$LIBDIR/modiocr/modiocr.pri)

#INCLUDEPATH += $$LIBDIR/modiocr # needed by shiboken generated code

## Libraries

QT += core
QT -= gui

INCLUDEPATH += $$PYSIDE_HOME/include/PySide/QtCore

## Sources

SRCPATH = binding/pymodi
INCLUDEPATH += $SRCPATH
DEPENDPATH += $SRCPATH

TEMPLATE = lib
TARGET = pymodi

HEADERS += \
  pymodi.h \
  pymodi_config.h \
  $$SRCPATH/pymodi_python.h \
  $$SRCPATH/modioreader_wrapper.h

SOURCES += \
  pymodi.cc \
  $$SRCPATH/pymodi_module_wrapper.cpp \
  $$SRCPATH/modireader_wrapper.cpp

#!wince*: LIBS += -lshell32
#RC_FILE += modi.rc

OTHER_FILES += \
  typesystem_modi.xml \
  update_binding.cmd

# EOF
