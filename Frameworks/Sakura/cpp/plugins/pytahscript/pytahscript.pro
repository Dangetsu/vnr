# pytahscript.pro
# 8/14/2014 jichi
# Build pytahscript.pyd
#
# Though Qt is not indispensible, shiboken could save me some time for development.
# Switch to pure PyC and get rid of QStringList if it becomes a performance bottle neck.

CONFIG += pysideplugin noqtgui
include(../../../config.pri)
include($$LIBDIR/tahscript/tahscript.pri)

INCLUDEPATH += $$LIBDIR/tahscript # needed by shiboken generated code

## Libraries

QT += core
QT -= gui

INCLUDEPATH += $$PYSIDE_HOME/include/PySide/QtCore

## Sources

SRCPATH = binding/pytahscript
INCLUDEPATH += $SRCPATH
DEPENDPATH += $SRCPATH

TEMPLATE = lib
TARGET = pytahscript

HEADERS += \
  pytahscript_config.h \
  $$SRCPATH/pytahscript_python.h \
  $$SRCPATH/tahscriptmanager_wrapper.h

SOURCES += \
  $$SRCPATH/pytahscript_module_wrapper.cpp \
  $$SRCPATH/tahscriptmanager_wrapper.cpp

#!wince*: LIBS += -lshell32
#RC_FILE += tahscript.rc

OTHER_FILES += \
  typesystem_tahscript.xml \
  update_binding.cmd

# EOF
