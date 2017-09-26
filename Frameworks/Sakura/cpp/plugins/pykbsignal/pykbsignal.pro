# pykbsignal.pro
# 9/9/2014 jichi
# Build pykbsignal.pyd

CONFIG += pysideplugin noqtgui
include(../../../config.pri)
include($$LIBDIR/keyboardhook/keyboardhook.pri)
include($$LIBDIR/qtkbsignal/qtkbsignal.pri)

INCLUDEPATH += $$LIBDIR/qtkbsignal # needed by shiboken generated code

## Libraries

QT += core
QT -= gui

# GUI is needed for WId
INCLUDEPATH += $$PYSIDE_HOME/include/PySide/QtCore
#INCLUDEPATH += $$PYSIDE_HOME/include/PySide/QtGui

## Sources

SRCPATH = binding/pykbsignal
INCLUDEPATH += $SRCPATH
DEPENDPATH += $SRCPATH

TEMPLATE = lib
TARGET = pykbsignal

HEADERS += \
  pykbsignal_config.h \
  $$SRCPATH/pykbsignal_python.h \
  $$SRCPATH/keyboardsignal_wrapper.h

SOURCES += \
  $$SRCPATH/pykbsignal_module_wrapper.cpp \
  $$SRCPATH/keyboardsignal_wrapper.cpp

#!wince*: LIBS += -lshell32
#RC_FILE += kbsignal.rc

OTHER_FILES += \
  typesystem_kbsignal.xml \
  update_binding.cmd

# EOF
