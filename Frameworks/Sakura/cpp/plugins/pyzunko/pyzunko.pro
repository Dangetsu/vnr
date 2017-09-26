# pyzunko.pro
# 10/12/2014 jichi
# Build pyzunko.pyd

CONFIG += pyplugin shiboken noqt
include(../../../config.pri)
include($$LIBDIR/voiceroid/aitalked/aitalked.pri)

INCLUDEPATH += $$LIBDIR/voiceroid/aitalked # needed by shiboken generated code

## Sources

SRCPATH = binding/pyzunko
INCLUDEPATH += $SRCPATH
DEPENDPATH += $SRCPATH

TEMPLATE = lib
TARGET = pyzunko

HEADERS += \
  pyzunko_config.h \
  $$SRCPATH/pyzunko_python.h \
  $$SRCPATH/aitalksynthesizer_wrapper.h

SOURCES += \
  $$SRCPATH/pyzunko_module_wrapper.cpp \
  $$SRCPATH/aitalksynthesizer_wrapper.cpp

#!wince*: LIBS += -lshell32
#RC_FILE += zunko.rc

OTHER_FILES += \
  typesystem_zunko.xml \
  update_binding.cmd

# EOF
