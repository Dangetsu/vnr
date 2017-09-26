# qteffects.pri
# 5/3/2012 jichi
#include(../../../config.pri)
DEFINES += WITH_LIB_QTEFFECT

DEPENDPATH += $$PWD

INCLUDEPATH += $$QT_SRC
QT += core gui

HEADERS += \
  $$PWD/graphicsabstractblureffect_p.h \
  $$PWD/graphicsgloweffect.h \
  $$PWD/graphicsgloweffect2.h \
  $$PWD/graphicstextshadoweffect.h \
  $$PWD/imagefilters.h \
  $$PWD/imagefilters_p.h \
  $$PWD/imagefilters_q.h \
  $$PWD/pixmapabstractblurfilter_p.h \
  $$PWD/pixmapabstractblurfilter_p_p.h \
  $$PWD/pixmapfilter_q.h \
  $$PWD/pixmapglowfilter_p.h \
  $$PWD/pixmapglowfilter2_p.h \
  $$PWD/pixmaptextshadowfilter_p.h \
  $$PWD/qteffects.h

SOURCES += \
  $$PWD/graphicsabstractblureffect_p.cc \
  $$PWD/graphicsgloweffect.cc \
  $$PWD/graphicsgloweffect2.cc \
  $$PWD/graphicstextshadoweffect.cc \
  $$PWD/imagefilters.cc \
  $$PWD/pixmapabstractblurfilter_p.cc \
  $$PWD/pixmapglowfilter_p.cc \
  $$PWD/pixmapglowfilter2_p.cc \
  $$PWD/pixmaptextshadowfilter_p.cc

# EOF
