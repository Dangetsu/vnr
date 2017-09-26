# pyvnrmem.pro
# 2/1/2013 jichi

CONFIG += pysideplugin noqtgui
include(../../../config.pri)
include($$LIBDIR/vnrsharedmemory/vnrsharedmemory.pri)

INCLUDEPATH += $$LIBDIR/vnrsharedmemory # needed by shiboken generated code

## Libraries

QT += core network
QT -= gui

INCLUDEPATH += $$PYSIDE_HOME/include/PySide/QtCore

## Sources

TEMPLATE = lib
TARGET = pyvnrmem

SRCPATH = binding/pyvnrmem
INCLUDEPATH += $SRCPATH
DEPENDPATH += $SRCPATH

HEADERS += \
  pyvnrmem_config.h \
  $$SRCPATH/pyvnrmem_python.h \
  $$SRCPATH/vnrsharedmemory_wrapper.h

SOURCES += \
  $$SRCPATH/pyvnrmem_module_wrapper.cpp \
  $$SRCPATH/vnrsharedmemory_wrapper.cpp

#!wince*: LIBS += -lshell32
#RC_FILE += reader.rc

OTHER_FILES += \
  typesystem_vnrmem.xml \
  update_binding.cmd

# EOF
