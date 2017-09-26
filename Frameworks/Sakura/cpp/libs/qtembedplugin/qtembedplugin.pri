# qtembedplugin.pri
# 2/1/2013 jichi
#
# Motivations:
# http://stackoverflow.com/questions/2150488/using-a-qt-based-dll-in-a-non-qt-application
# http://stackoverflow.com/questions/1786438/qt-library-event-loop-problems

DEFINES += WITH_LIB_QTEMBEDPLUGIN

QT += core

DEPENDPATH += $$PWD

HEADERS += \
  $$PWD/codecmanager.h \
  $$PWD/pluginmanager.h \
  $$PWD/qtembedplugin.h

SOURCES += \
  $$PWD/codecmanager.cc \
  $$PWD/pluginmanager.cc

# EOF
