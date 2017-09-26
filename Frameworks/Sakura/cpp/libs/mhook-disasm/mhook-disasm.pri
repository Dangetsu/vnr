# mhook.pri
# 6/1/2014 jichi
# See also: detours, MinHook
# Source: https://github.com/martona/mhook/
# Version: http://codefromthe70s.org/mhook24.aspx

win32 {
DEFINES += WITH_LIB_MHOOK

DEPENDPATH += $$PWD

HEADERS += \
  $$PWD/cpu.h \
  $$PWD/disasm.h \
  $$PWD/disasm_x86.h \
  $$PWD/disasm_x86_tables \
  $$PWD/misc.h

SOURCES += \
  $$PWD/cpu.c \
  $$PWD/disasm.c \
  $$PWD/disasm_x86.c \
  $$PWD/misc.c
}

# EOF
