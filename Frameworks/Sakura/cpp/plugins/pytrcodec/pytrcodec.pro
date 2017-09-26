# pytrcodec.pro
# 9/21/2014 jichi
# Build pytrcodec.pyd
#
# Though Qt is not indispensible, shiboken could save me some time for development.
# Switch to pure PyC and get rid of QStringList if it becomes a performance bottle neck.

CONFIG += pyplugin shiboken noqt
include(../../../config.pri)
include($$LIBDIR/trcodec/trcodec.pri)
include($$LIBDIR/trrender/trrender.pri)
include($$LIBDIR/trsym/trsym.pri)

INCLUDEPATH += $$LIBDIR/trcodec # needed by shiboken generated code

## Sources

SRCPATH = binding/pytrcodec
INCLUDEPATH += $SRCPATH
DEPENDPATH += $SRCPATH

TEMPLATE = lib
TARGET = pytrcodec

HEADERS += \
  pytrcodec_config.h \
  $$SRCPATH/pytrcodec_python.h \
  $$SRCPATH/translationcoder_wrapper.h

SOURCES += \
  $$SRCPATH/pytrcodec_module_wrapper.cpp \
  $$SRCPATH/translationcoder_wrapper.cpp

#!wince*: LIBS += -lshell32
#RC_FILE += trcodec.rc

OTHER_FILES += \
  typesystem_trcodec.xml \
  update_binding.cmd

# EOF
