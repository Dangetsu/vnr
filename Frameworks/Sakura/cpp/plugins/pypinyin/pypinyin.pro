# pypinyin.pro
# 10/18/2014 jichi
# Build pypinyin.pyd
#
# Though Qt is not indispensible, shiboken could save me some time for development.
# Switch to pure PyC and get rid of QStringList if it becomes a performance bottle neck.

CONFIG += pyplugin shiboken noqt
include(../../../config.pri)
include($$LIBDIR/pinyinconv/pinyinconv.pri)

INCLUDEPATH += $$LIBDIR/pinyinconv # needed by shiboken generated code

## Sources

SRCPATH = binding/pypinyin
INCLUDEPATH += $SRCPATH
DEPENDPATH += $SRCPATH

TEMPLATE = lib
TARGET = pypinyin

HEADERS += \
  pypinyin_config.h \
  $$SRCPATH/pypinyin_python.h \
  $$SRCPATH/pinyinconverter_wrapper.h

SOURCES += \
  $$SRCPATH/pypinyin_module_wrapper.cpp \
  $$SRCPATH/pinyinconverter_wrapper.cpp

#!wince*: LIBS += -lshell32
#RC_FILE += pinyin.rc

OTHER_FILES += \
  typesystem_pinyin.xml \
  update_binding.cmd

# EOF
