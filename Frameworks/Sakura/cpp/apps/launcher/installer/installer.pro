# installer.pro
# 9/3/2011 jichi

VERSION = 0.1.0.0

CONFIG += noqt nocrt
include(../../../../config.pri)
include(../launcher.pri)

## Libraries

#QT        += core gui

## Sources

TEMPLATE  = app
win32: CONFIG += windows
TARGET    = "[ Setup ]"

HEADERS += config.h
SOURCES += main.cc

OTHER_FILES += \
  installer.rc \
  installer.ico

win32 {
  !wince*: LIBS += -lshell32
  RC_FILE += installer.rc
}

#mac {
#  ICON = app.icns
#  QMAKE_INFO_PLIST = Info.plist
#}


# EOF

