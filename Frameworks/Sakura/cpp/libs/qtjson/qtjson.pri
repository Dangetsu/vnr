# qtjson.pri
# 4/21/2014 jichi
#
# See:
# http://dev.libqxt.org/libqxt/src
# https://github.com/da4c30ff/qt-json/blob/master/json.cpp

DEFINES += WITH_LIB_QTJSON

QT += core

DEPENDPATH += $$PWD

HEADERS += $$PWD/qtjson.h
SOURCES += $$PWD/qtjson.cc

# EOF
