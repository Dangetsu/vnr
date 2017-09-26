# static.pro
# 3/28/2013 jichi

include($$PWD/defines.pri)

LIBS    += -leb

INCLUDEPATH += $$ZLIB_HOME/include
LIBS        += -lz -L$$ZLIB_HOME/lib

# EOF
