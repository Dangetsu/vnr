# winddk.pri
# 9/22/2013 jichi

DEFINES += WITH_LIB_WINDDK

LIBS += -lntoskrnl

DEPENDPATH += $$PWD

HEADERS += $$PWD/winddk.h

# EOF
