# pywmp.pro
# 10/5/2014 jichi
# Build pywmp.pyd

CONFIG += pyplugin shiboken noqt
include(../../../config.pri)
include($$COMDIR/wmp/wmp.pri)
include($$LIBDIR/wmpcli/wmpcli.pri)

#INCLUDEPATH += $$LIBDIR/wmpcli # needed by shiboken generated code

## Sources

SRCPATH = binding/pywmp
INCLUDEPATH += $SRCPATH
DEPENDPATH += $SRCPATH

TEMPLATE = lib
TARGET = pywmp

HEADERS += \
  pywmp.h \
  pywmp_config.h \
  $$SRCPATH/pywmp_python.h \
  $$SRCPATH/windowsmediaplayer_wrapper.h

SOURCES += \
  pywmp.cc \
  $$SRCPATH/pywmp_module_wrapper.cpp \
  $$SRCPATH/windowsmediaplayer_wrapper.cpp

#!wince*: LIBS += -lshell32
#RC_FILE += wmp.rc

OTHER_FILES += \
  typesystem_wmp.xml \
  update_binding.cmd

# EOF
