# pyrich.pro
# 6/27/2015 jichi
# Build pyrich.pyd
#
# Though Qt is not indispensible, shiboken could save me some time for development.
# Switch to pure PyC and get rid of QStringList if it becomes a performance bottle neck.

CONFIG += pysideplugin noqtgui
include(../../../config.pri)
include($$LIBDIR/qtrichruby/qtrichruby.pri)

INCLUDEPATH += $$LIBDIR/qtrichruby # needed by shiboken generated code

## Libraries

QT += core gui

INCLUDEPATH += $$PYSIDE_HOME/include/PySide/QtCore \
               $$PYSIDE_HOME/include/PySide/QtGui

## Sources

SRCPATH = binding/pyrich
INCLUDEPATH += $SRCPATH
DEPENDPATH += $SRCPATH

TEMPLATE = lib
TARGET = pyrich

HEADERS += \
  pyrich_config.h \
  $$SRCPATH/pyrich_python.h \
  $$SRCPATH/richrubyparser_wrapper.h

SOURCES += \
  $$SRCPATH/pyrich_module_wrapper.cpp \
  $$SRCPATH/richrubyparser_wrapper.cpp

#!wince*: LIBS += -lshell32
#RC_FILE += rich.rc

OTHER_FILES += \
  typesystem_rich.xml \
  update_binding.cmd

# EOF
