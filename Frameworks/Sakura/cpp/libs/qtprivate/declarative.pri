# declarative.pri
# 4/5/2014 jichi
#include(../../../config.pri)
DEFINES += WITH_LIB_QTPRIVATE_DECLARATIVE

DEPENDPATH += $$PWD

# FIXME: dynamic QT_SRC does not work
win32:  QT_SRC  = c:/qt
mac:    QT_SRC  = /Users/jichi/src
#mac:    QT_SRC  = ${HOME}/src

#QT_DECLARATIVE_SRC = $$PWD
QT_DECLARATIVE_SRC = $$QT_SRC/qt/src/declarative

INCLUDEPATH += $$QT_SRC
#QT += core gui declarative

INCLUDEPATH += \
  $$QT_SRC \
  $$QT_SRC/qt/src/3rdparty/harfbuzz/src # fro harfbuzz-shaper.h

HEADERS += \
  $$QT_DECLARATIVE_SRC/graphicsitems/qdeclarativeimplicitsizeitem_p.h \
  $$QT_DECLARATIVE_SRC/graphicsitems/qdeclarativeimplicitsizeitem_p_p.h \
  $$QT_DECLARATIVE_SRC/graphicsitems/qdeclarativepainteditem_p.h \
  $$QT_DECLARATIVE_SRC/graphicsitems/qdeclarativepainteditem_p_p.h \
  $$QT_DECLARATIVE_SRC/graphicsitems/qdeclarativetextedit_p.h \
  $$QT_DECLARATIVE_SRC/graphicsitems/qdeclarativetextedit_p_p.h

SOURCES += \
  $$QT_DECLARATIVE_SRC/graphicsitems/qdeclarativeimplicitsizeitem.cpp \
  $$QT_DECLARATIVE_SRC/graphicsitems/qdeclarativepainteditem.cpp \
  $$QT_DECLARATIVE_SRC/graphicsitems/qdeclarativetextedit.cpp

# EOF
