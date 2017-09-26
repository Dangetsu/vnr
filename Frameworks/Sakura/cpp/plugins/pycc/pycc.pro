# pycc.pro
# 10/18/2014 jichi
# Build pycc.pyd
#
# Though Qt is not indispensible, shiboken could save me some time for development.
# Switch to pure PyC and get rid of QStringList if it becomes a performance bottle neck.

CONFIG += pyplugin shiboken noqt
include(../../../config.pri)
include($$LIBDIR/simplecc/simplecc.pri)

INCLUDEPATH += $$LIBDIR/simplecc # needed by shiboken generated code

## Sources

SRCPATH = binding/pycc
INCLUDEPATH += $SRCPATH
DEPENDPATH += $SRCPATH

TEMPLATE = lib
TARGET = pycc

HEADERS += \
  pycc_config.h \
  $$SRCPATH/pycc_python.h \
  $$SRCPATH/simplechineseconverter_wrapper.h

SOURCES += \
  $$SRCPATH/pycc_module_wrapper.cpp \
  $$SRCPATH/simplechineseconverter_wrapper.cpp

#!wince*: LIBS += -lshell32
#RC_FILE += cc.rc

OTHER_FILES += \
  typesystem_cc.xml \
  update_binding.cmd

# EOF
