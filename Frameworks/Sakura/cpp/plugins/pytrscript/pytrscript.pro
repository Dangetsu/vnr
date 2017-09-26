# pytrscript.pro
# 9/21/2014 jichi
# Build pytrscript.pyd
#
# Though Qt is not indispensible, shiboken could save me some time for development.
# Switch to pure PyC and get rid of QStringList if it becomes a performance bottle neck.

CONFIG += pyplugin shiboken noqt
include(../../../config.pri)
include($$LIBDIR/trrender/trrender.pri)
include($$LIBDIR/trscript/trscript.pri)

INCLUDEPATH += $$LIBDIR/trscript # needed by shiboken generated code

## Sources

SRCPATH = binding/pytrscript
INCLUDEPATH += $SRCPATH
DEPENDPATH += $SRCPATH

TEMPLATE = lib
TARGET = pytrscript

HEADERS += \
  pytrscript_config.h \
  $$SRCPATH/pytrscript_python.h \
  $$SRCPATH/translationscriptperformer_wrapper.h

SOURCES += \
  $$SRCPATH/pytrscript_module_wrapper.cpp \
  $$SRCPATH/translationscriptperformer_wrapper.cpp

#!wince*: LIBS += -lshell32
#RC_FILE += trscript.rc

OTHER_FILES += \
  typesystem_trscript.xml \
  update_binding.cmd

# EOF
