# pysapi.pro
# 4/7/2013 jichi
# Build pysapi.pyd
#
# Though Qt is not indispensible, shiboken could save me some time for development.
# Switch to pure PyC and get rid of QStringList if it becomes a performance bottle neck.

CONFIG += pyplugin shiboken noqt
include(../../../config.pri)
include($$LIBDIR/wintts/wintts.pri)

#INCLUDEPATH += $$LIBDIR/wintts # needed by shiboken generated code

## Sources

SRCPATH = binding/pysapi
INCLUDEPATH += $SRCPATH
DEPENDPATH += $SRCPATH

TEMPLATE = lib
TARGET = pysapi

HEADERS += \
  pysapi.h \
  pysapi_config.h \
  $$SRCPATH/pysapi_python.h \
  $$SRCPATH/sapiplayer_wrapper.h

SOURCES += \
  pysapi.cc \
  $$SRCPATH/pysapi_module_wrapper.cpp \
  $$SRCPATH/sapiplayer_wrapper.cpp

#!wince*: LIBS += -lshell32
#RC_FILE += sapi.rc

OTHER_FILES += \
  typesystem_sapi.xml \
  update_binding.cmd

# EOF
