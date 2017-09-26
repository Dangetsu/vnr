# pymsime.pro
# 4/1/2013 jichi
# Build pymsime.pyd
#
# Though Qt is not indispensible, shiboken could save me some time for development.
# Switch to pure PyC and get rid of QStringList if it becomes a performance bottle neck.

CONFIG += pysideplugin noqtgui
include(../../../config.pri)
include($$LIBDIR/winime/winime.pri)

#INCLUDEPATH += $$LIBDIR/winime # needed by shiboken generated code

## Libraries

QT += core
QT -= gui

INCLUDEPATH += $$PYSIDE_HOME/include/PySide/QtCore

## Sources

SRCPATH = binding/pymsime
INCLUDEPATH += $SRCPATH
DEPENDPATH += $SRCPATH

TEMPLATE = lib
TARGET = pymsime

HEADERS += \
  pymsime.h \
  pymsime_p.h \
  pymsime_config.h \
  $$SRCPATH/msime_wrapper.h \
  $$SRCPATH/pymsime_python.h

SOURCES += \
  pymsime.cc \
  $$SRCPATH/msime_wrapper.cpp \
  $$SRCPATH/pymsime_module_wrapper.cpp

#!wince*: LIBS += -lshell32
#RC_FILE += msime.rc

OTHER_FILES += \
  typesystem_msime.xml \
  update_binding.cmd

# EOF
