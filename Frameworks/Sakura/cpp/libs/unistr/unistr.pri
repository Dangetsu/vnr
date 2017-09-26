# unistr.pri
# 2/2/2015 jichi

DEFINES += WITH_LIB_UNISTR

DEPENDPATH += $$PWD

HEADERS += \
  $$PWD/unichar.h \
  $$PWD/uniiter.h \
  $$PWD/unistr.h

SOURCES += \
  $$PWD/uniiter.cc

# EOF
