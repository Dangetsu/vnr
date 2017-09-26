# pytroscript.pro
# 9/21/2014 jichi
# Build pytrscript.pyd
#
# Though Qt is not indispensible, shiboken could save me some time for development.
# Switch to pure PyC and get rid of QStringList if it becomes a performance bottle neck.

CONFIG += pyplugin shiboken noqt
include(../../../config.pri)
include($$LIBDIR/trrender/trrender.pri)
include($$LIBDIR/troscript/troscript.pri)
include($$LIBDIR/trsym/trsym.pri)

INCLUDEPATH += $$LIBDIR/troscript # needed by shiboken generated code

## Sources

SRCPATH = binding/pytroscript
INCLUDEPATH += $SRCPATH
DEPENDPATH += $SRCPATH

TEMPLATE = lib
TARGET = pytroscript

HEADERS += \
  pytroscript_config.h \
  $$SRCPATH/pytroscript_python.h \
  $$SRCPATH/translationoutputscriptperformer_wrapper.h

SOURCES += \
  $$SRCPATH/pytroscript_module_wrapper.cpp \
  $$SRCPATH/translationoutputscriptperformer_wrapper.cpp

#!wince*: LIBS += -lshell32
#RC_FILE += troscript.rc

OTHER_FILES += \
  typesystem_troscript.xml \
  update_binding.cmd

# EOF
