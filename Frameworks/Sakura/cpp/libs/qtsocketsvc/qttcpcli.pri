# qttcpcli.pri
# 4/29/2014 jichi
# Socket service client.
#include(../../../config.pri)
DEFINES += WITH_LIB_QTSOCKETCLI

DEPENDPATH += $$PWD

QT += core network

HEADERS += \
  $$PWD/bufferedtcpsocketclient.h \
  $$PWD/queuedtcpsocketclient.h \
  $$PWD/socketdef.h \
  $$PWD/socketio_p.h \
  $$PWD/socketpack.h \
  $$PWD/tcpsocketclient.h

SOURCES += \
  $$PWD/bufferedtcpsocketclient.cc \
  $$PWD/queuedtcpsocketclient.cc \
  $$PWD/socketio_p.cc \
  $$PWD/tcpsocketclient.cc

# EOF
