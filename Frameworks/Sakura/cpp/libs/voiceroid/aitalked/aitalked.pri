# aitalked.pri
# 10/11/2014 jichi
win32 {

DEFINES += WITH_LIB_AITALKED

AITALKED_SRC = $$PWD/cpp

INCLUDEPATH += $$PWD/..
INCLUDEPATH += $$AITALKED_SRC
DEPENDPATH += $$AITALKED_SRC/aitalk

LIBS += -luser32 # for hook functions

HEADERS += \
    $$PWD/aitalked.h \
    $$AITALKED_SRC/aitalk/_windef.h \
    $$AITALKED_SRC/aitalk/aiaudioapi.h \
    $$AITALKED_SRC/aitalk/aiaudiodef.h \
    $$AITALKED_SRC/aitalk/aitalkapi.h \
    $$AITALKED_SRC/aitalk/aitalkconf.h \
    $$AITALKED_SRC/aitalk/aitalkdef.h \
    $$AITALKED_SRC/aitalk/aitalkmarshal.h \
    $$AITALKED_SRC/aitalk/aitalksettings.h \
    $$AITALKED_SRC/aitalk/aitalkutil.h
SOURCES += \
    $$PWD/aitalked.cc \
    $$AITALKED_SRC/aitalk/aiaudioapi.cc \
    $$AITALKED_SRC/aitalk/aitalkapi.cc \
    $$AITALKED_SRC/aitalk/aitalkmarshal.cc \
    $$AITALKED_SRC/aitalk/aitalkutil.cc
}

# EOF
