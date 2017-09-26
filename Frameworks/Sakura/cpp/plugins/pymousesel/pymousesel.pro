# pymousesel.pro
# 8/21/2014 jichi
# Build pymousesel.pyd

CONFIG += pysideplugin #noqtgui
include(../../../config.pri)
include($$LIBDIR/mousehook/mousehook.pri)
include($$LIBDIR/qtmousesel/qtmousesel.pri)
include($$LIBDIR/qtrubberband/qtrubberband.pri)

INCLUDEPATH += $$LIBDIR/qtmousesel # needed by shiboken generated code

## Libraries

QT += core gui

# GUI is needed for WId
INCLUDEPATH += $$PYSIDE_HOME/include/PySide/QtCore \
               $$PYSIDE_HOME/include/PySide/QtGui

## Sources

SRCPATH = binding/pymousesel
INCLUDEPATH += $SRCPATH
DEPENDPATH += $SRCPATH

TEMPLATE = lib
TARGET = pymousesel

HEADERS += \
  pymousesel_config.h \
  $$SRCPATH/pymousesel_python.h \
  $$SRCPATH/mouseselector_wrapper.h

SOURCES += \
  $$SRCPATH/pymousesel_module_wrapper.cpp \
  $$SRCPATH/mouseselector_wrapper.cpp

#!wince*: LIBS += -lshell32
#RC_FILE += mousesel.rc

OTHER_FILES += \
  typesystem_mousesel.xml \
  update_binding.cmd

# EOF
