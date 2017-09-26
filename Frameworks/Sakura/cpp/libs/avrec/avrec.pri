# avrec.pri
# 10/28/2014 jichi

DEFINES += WITH_LIB_AVREC

DEPENDPATH += $$PWD

LIBS += -lavcodec -lavformat -lavutil -lswscale

#QT += core

HEADERS += \
  $$PWD/avrecorder.h \
  $$PWD/avsettings.h

SOURCES += \
  $$PWD/avrecorder.cc

# EOF
