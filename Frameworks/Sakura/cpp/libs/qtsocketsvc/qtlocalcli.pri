# qtlocalcli.pri
# 4/29/2014 jichi
# Socket service client.
#include(../../../config.pri)
DEFINES += WITH_LIB_QTSOCKETCLI

DEPENDPATH += $$PWD

QT += core network

HEADERS += \
  $$PWD/bufferedlocalsocketclient.h \
  $$PWD/localsocketclient.h \
  $$PWD/queuedlocalsocketclient.h \
  $$PWD/socketdef.h \
  $$PWD/socketio_p.h \
  $$PWD/socketpack.h

SOURCES += \
  $$PWD/bufferedlocalsocketclient.cc \
  $$PWD/localsocketclient.cc \
  $$PWD/queuedlocalsocketclient.cc \
  $$PWD/socketio_p.cc

# EOF
