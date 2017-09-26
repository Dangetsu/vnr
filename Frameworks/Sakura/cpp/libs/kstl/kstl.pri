# kstl.pri
# 12/9/2011 jichi
# Windows kernel template library
win32 {

DEFINES += WITH_LIB_KSTL

HEADERS += \
  $$PWD/algorithm     $$PWD/algorithm.h $$PWD/move.h \
  $$PWD/core          $$PWD/core.h $$PWD/win.h \
  $$PWD/cstdlib       $$PWD/stdlib.h \
  $$PWD/debug         $$PWD/debug.h \
  $$PWD/iterator      $$PWD/iterator.h $$PWD/iterator_types.h $$PWD/iterator_funcs.h \
  $$PWD/list          $$PWD/list.h \
  $$PWD/macros        $$PWD/macros.h \
  $$PWD/mutex         $$PWD/mutex.h \
  $$PWD/tree          $$PWD/tree.h \
  $$PWD/type          $$PWD/type.h \
  $$PWD/memory        $$PWD/memory.h $$PWD/allocator.h $$PWD/new_allocator.h \
  $$PWD/new           $$PWD/new.h

SOURCES += \
  $$PWD/msvcrt/except.c \
  $$PWD/msvcrt/rtti.c \
  $$PWD/core.cc \
  $$PWD/stdlib.cc
}
# EOF
