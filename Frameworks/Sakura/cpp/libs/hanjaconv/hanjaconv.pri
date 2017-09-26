# hanjaconv.pri
# 1/6/2015 jichi

DEFINES += WITH_LIB_HANJACONV

DEPENDPATH += $$PWD

#QT += core

HEADERS += \
  $$PWD/hangul2hanja.h \
  $$PWD/hangul2hanja_p.h \
  $$PWD/hanjadef_p.h \
  $$PWD/hanja2hangul.h \
  $$PWD/hanja2hangulchar.h \
  $$PWD/hanja2hangulword.h
SOURCES += \
  $$PWD/hangul2hanja.cc \
  $$PWD/hangul2hanja_p.cc \
  $$PWD/hanjadef_p.cc \
  $$PWD/hanja2hangul.cc \
  $$PWD/hanja2hangulchar.cc \
  $$PWD/hanja2hangulword.cc

# EOF
