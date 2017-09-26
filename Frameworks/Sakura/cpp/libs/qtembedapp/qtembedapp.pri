# qtembedapp.pri
# 2/1/2013 jichi
#
# Motivations:
# http://stackoverflow.com/questions/2150488/using-a-qt-based-dll-in-a-non-qt-application
# http://stackoverflow.com/questions/1786438/qt-library-event-loop-problems

DEFINES += WITH_LIB_QTEMBEDAPP

QT += core

DEPENDPATH += $$PWD

HEADERS += \
  $$PWD/applicationrunner.h \
  $$PWD/qtembedapp.h

win32: SOURCES += $$PWD/applicationrunner_win.cc

# EOF
