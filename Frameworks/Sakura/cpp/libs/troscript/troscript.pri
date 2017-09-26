# trscript.pri
# 9/20/2014 jichi

DEFINES += WITH_LIB_TRSCRIPT

DEPENDPATH += $$PWD

LIBS += -lboost_regex$$BOOST_VARIANT

#QT += core

HEADERS += \
  $$PWD/trexp.h \
  $$PWD/troscript.h \
  $$PWD/trrule.h

SOURCES += \
  $$PWD/trexp.cc \
  $$PWD/troscript.cc \
  $$PWD/trrule.cc

OTHER_FILES += example.txt

# EOF
