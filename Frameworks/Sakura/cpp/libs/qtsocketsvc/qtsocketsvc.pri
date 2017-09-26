# qtsocketsvc.pri
# 4/29/2014 jichi
# Socket service client.
#include(../../../config.pri)
DEFINES += WITH_LIB_QTSOCKETCLI

DEPENDPATH += $$PWD

QT += core network

HEADERS += \
  $$PWD/bufferedlocalsocketclient.h \
  $$PWD/bufferedtcpsocketclient.h \
  $$PWD/localsocketclient.h \
  $$PWD/queuedlocalsocketclient.h \
  $$PWD/queuedtcpsocketclient.h \
  $$PWD/socketdef.h \
  $$PWD/socketio_p.h \
  $$PWD/socketpack.h \
  $$PWD/socketpipe.h \
  $$PWD/tcpsocketclient.h

SOURCES += \
  $$PWD/bufferedlocalsocketclient.cc \
  $$PWD/bufferedtcpsocketclient.cc \
  $$PWD/localsocketclient.cc \
  $$PWD/queuedlocalsocketclient.cc \
  $$PWD/queuedtcpsocketclient.cc \
  $$PWD/socketio_p.cc \
  $$PWD/socketpack.cc \
  $$PWD/tcpsocketclient.cc

win32 {
  HEADERS += $$PWD/socketpipe_win.h
  SOURCES += $$PWD/socketpipe_win.cc
}

OTHER_FILES += \
  $$PWD/qtlocalcli.pri \
  $$PWD/qtsocketpack.pri \
  $$PWD/qtsocketpipe.pri \
  $$PWD/qttcpcli.pri
  #$$PWD/qtsocketsrv.pri

# EOF
