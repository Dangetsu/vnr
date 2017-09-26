# texscript.pri
# 6/28/2011 jichi

DEFINES += WITH_LIB_TEXSCRIPT

QT += core

DEPENDPATH +=$$PWD

HEADERS += \
  $$PWD/texhtml_p.h \
  $$PWD/texhtml.h \
  $$PWD/textag.h

SOURCES += \
  $$PWD/texhtml_p.cc \
  $$PWD/texhtml.cc

# EOF
