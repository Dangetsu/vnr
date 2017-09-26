# tahscript.pri
# 8/14/2014 jichi
# See: http://www.hongfire.com/forum/showthread.php/94395-Translation-Aggregator-v0-4-9/page51?p=2269439#post2269439
# See: http://www.hongfire.com/forum/showthread.php/94395-Translation-Aggregator-v0-4-9?p=1811363#post1811363

DEFINES += WITH_LIB_TAHSCRIPT

DEPENDPATH += $$PWD

QT += core

HEADERS += $$PWD/tahscript.h
SOURCES += $$PWD/tahscript.cc

# EOF
