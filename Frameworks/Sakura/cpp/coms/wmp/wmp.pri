# wmp.pri
# 10/5/2014 jichi

win32 {
DEFINES += WITH_COM_WMP

WMP_VERSION = 12.0
INCLUDEPATH += $$PWD/$$WMP_VERSION
DEPENDPATH  += $$PWD

HEADERS += \
  $$PWD/wmp.h \
  $$PWD/$$WMP_VERSION/wmp.tlh
}

# EOF
