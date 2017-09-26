# pytest.pro
# 2/25/2014

CONFIG += console noqt nocrt noeh #nosafeseh
include(../../../config.pri)
#include($$LIBDIR/winseh/winseh_safe.pri)

INCLUDEPATH   += $$PYTHON_HOME/include/python2.7 $$PYTHON_HOME/include
unix:   LIBS  += -L$$PYTHON_HOME/lib -lpython2.7
win32:  LIBS  += -L$$PYTHON_HOME/libs -lpython27

#LIBS += -luser32

# Source

TEMPLATE = app
TARGET = pytest

DEPENDPATH += .
INCLUDEPATH += .

SOURCES += main.cc

# EOF
