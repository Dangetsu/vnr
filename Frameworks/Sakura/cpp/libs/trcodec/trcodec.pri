# trcodec.pri
# 9/20/2014 jichi

DEFINES += WITH_LIB_TRCODEC

DEPENDPATH += $$PWD

LIBS += -lboost_regex$$BOOST_VARIANT

HEADERS += \
  $$PWD/trcodec.h \
  $$PWD/trdecode.h \
  $$PWD/trdecoderule.h \
  $$PWD/trdefine.h \
  $$PWD/trencode.h \
  $$PWD/trencoderule.h \
  $$PWD/trrule.h

SOURCES += \
  $$PWD/trcodec.cc \
  $$PWD/trdecode.cc \
  $$PWD/trdecoderule.cc \
  $$PWD/trencode.cc \
  $$PWD/trencoderule.cc

# EOF
