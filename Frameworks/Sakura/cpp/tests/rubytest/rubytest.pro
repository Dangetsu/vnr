# rubytest.pro
# 6/25/2015

include(../../../config.pri)
include($$LIBDIR/qtrichruby/qtrichruby.pri)

# Source

TEMPLATE = app
TARGET = rubytest

DEPENDPATH += .
INCLUDEPATH += .

SOURCES += main.cc

# EOF
