# pytexthook.pro
# 10/13/2011 jichi
# Build pytexthook.pyd for texthook.dll

CONFIG += pysideplugin noqtgui
include(../../../config.pri)

#DEFINES += TEXTHOOK_BUILD_LIB
include(../texthook/texthook.pri)
#include(../texthook/texthook_static.pri)

## Libraries

QT += core
QT -= gui

# QtGui header is needed for WId
INCLUDEPATH += \
  $$PYSIDE_HOME/include/PySide/QtCore \
  $$PYSIDE_HOME/include/PySide/QtGui

## Sources

TEMPLATE = lib
TARGET = pytexthook

SRCPATH = binding/pytexthook
INCLUDEPATH += $SRCPATH
DEPENDPATH += $SRCPATH

HEADERS += \
  pytexthook_config.h \
  $$SRCPATH/pytexthook_python.h \
  $$SRCPATH/texthook_wrapper.h

SOURCES += \
  $$SRCPATH/pytexthook_module_wrapper.cpp \
  $$SRCPATH/texthook_wrapper.cpp

#!wince*: LIBS += -lshell32
#RC_FILE += texthook.rc

OTHER_FILES += \
  typesystem_texthook.xml \
  update_binding.cmd

# EOF
