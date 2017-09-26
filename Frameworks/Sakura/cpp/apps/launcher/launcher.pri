# launcher.pri
# 3/29/2012 jichi

DEFINES     += WITH_SRC_LAUNCHER
INCLUDEPATH += $$PWD/include
DEPENDPATH  += $$PWD/include

# http://stackoverflow.com/questions/20933126/disabling-incremental-linking-when-using-nmake
# Needed to stop the following error:
# LINK : fatal error LNK1123: failure during conversion to COFF: file invalid or corrupt
#CONFIG -= incremental
#QMAKE_LFLAGS_RELEASE += /INCREMENTAL:NO

HEADERS += \
  $$PWD/include/main.tcc \
  $$PWD/include/pymain.tcc

QT      += core

# EOF
