# pywinutil.pro
# 4/7/2013 jichi
# Build pywinutil.pyd
#
# Though Qt is not indispensible, shiboken could save me some time for development.
# Switch to pure PyC and get rid of QStringList if it becomes a performance bottle neck.

CONFIG += pyplugin shiboken noqt
include(../../../config.pri)
include($$LIBDIR/winshell/winshell.pri)

#INCLUDEPATH += $$LIBDIR/winshell # needed by shiboken generated code

## Sources

SRCPATH = binding/pywinutil
INCLUDEPATH += $SRCPATH
DEPENDPATH += $SRCPATH

TEMPLATE = lib
TARGET = pywinutil

HEADERS += \
  pywinutil.h \
  pywinutil_config.h \
  $$SRCPATH/pywinutil_python.h \
  $$SRCPATH/winutil_wrapper.h

SOURCES += \
  pywinutil.cc \
  $$SRCPATH/pywinutil_module_wrapper.cpp \
  $$SRCPATH/winutil_wrapper.cpp

#!wince*: LIBS += -lshell32
#RC_FILE += winutil.rc

OTHER_FILES += \
  typesystem_winutil.xml \
  update_binding.cmd

# EOF
