# pyhanja.pro
# 4/1/2013 jichi
# Build pyhanja.pyd
#
# Though Qt is not indispensible, it's containers could same memory.

CONFIG += pysideplugin noqtgui
include(../../../config.pri)
include($$LIBDIR/hanjaconv/hanjaconv.pri)
#include($$LIBDIR/unistr/unistr.pri)

#INCLUDEPATH += $$LIBDIR/hanjaconv # needed by shiboken generated code

## Libraries

QT += core
QT -= gui

#DEFINES += WITHOUT_CXX_CODECVT

INCLUDEPATH += $$PYSIDE_HOME/include/PySide/QtCore

## Sources

SRCPATH = binding/pyhanja
INCLUDEPATH += $SRCPATH
DEPENDPATH += $SRCPATH

TEMPLATE = lib
TARGET = pyhanja

HEADERS += \
  qhangulhanjaconv.h \
  qhangulhanjaconv_p.h \
  qhanjahangulconv.h \
  pyhanja_config.h \
  $$SRCPATH/qhanjahangulconverter_wrapper.h \
  $$SRCPATH/qhangulhanjaconverter_wrapper.h \
  $$SRCPATH/pyhanja_python.h

SOURCES += \
  qhangulhanjaconv.cc \
  qhangulhanjaconv_p.cc \
  qhanjahangulconv.cc \
  $$SRCPATH/qhanjahangulconverter_wrapper.cpp \
  $$SRCPATH/qhangulhanjaconverter_wrapper.cpp \
  $$SRCPATH/pyhanja_module_wrapper.cpp

#!wince*: LIBS += -lshell32
#RC_FILE += hanja.rc

OTHER_FILES += \
  typesystem_hanja.xml \
  update_binding.cmd

# EOF
