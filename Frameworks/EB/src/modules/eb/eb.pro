# eb.pro
# 3/28/2013 jichi
# Build eb.dll
#
# Source: ftp://ftp.sra.co.jp/pub/misc/eb/
# Version: 4.4.3

CONFIG += noqt nocrt
include(../../../config.pri)
include(defines.pri)

## Config

DEFINES += HAVE_CONFIG_H

DEFINES += EB_BUILD_LIBRARY # include "eb.h" instead of "eb/eb.h"

unix:   CONFIG  += dll
win32:  CONFIG  += staticlib

#win32: QMAKE_LFLAGS += /implib:eb.lib
#win32: QMAKE_LINK_SHLIB_CMD += /implib:eb.lib

## Libraries

INCLUDEPATH += $$DIRENT_HOME/include

INCLUDEPATH += $$ZLIB_HOME/include
LIBS        += -lz -L$$ZLIB_HOME/lib

## Sources

TEMPLATE = lib
TARGET  = eb

INCLUDEPATH += src include/eb
DEPENDPATH  += src include/eb

HEADERS += \
  build-post.h \
  build-pre.h \
  config.h \
  include/eb/appendix.h \
  include/eb/binary.h \
  include/eb/booklist.h \
  include/eb/defs.h \
  include/eb/eb.h \
  include/eb/error.h \
  include/eb/font.h \
  include/eb/sysdefs.h \
  include/eb/text.h \
  include/eb/zio.h
  #src/dummyin6.h
  #src/ebnet.h
  #src/getaddrinfo.h
  #src/linebuf.h
  #src/urlparts.h

SOURCES += \
  src/appendix.c \
  src/appsub.c \
  src/bcd.c \
  src/binary.c \
  src/bitmap.c \
  src/book.c \
  src/booklist.c \
  src/copyright.c \
  src/cross.c \
  src/eb.c \
  src/endword.c \
  src/error.c \
  src/exactword.c \
  src/filename.c \
  src/font.c \
  src/hook.c \
  src/jacode.c \
  src/keyword.c \
  src/lock.c \
  src/log.c \
  src/match.c \
  src/menu.c \
  src/multi.c \
  src/narwalt.c \
  src/narwfont.c \
  src/readtext.c \
  src/search.c \
  src/setword.c \
  src/stopcode.c \
  src/subbook.c \
  src/text.c \
  src/widealt.c \
  src/widefont.c \
  src/word.c \
  src/zio.c
  #src/dummyin6.c
  #src/ebnet.c
  #src/getaddrinfo.c
  #src/linebuf.c
  #src/multiplex.c
  #src/urlparts.c

win32: SOURCES += src/strcasecmp.c

#!wince*: LIBS += -lshell32
#RC_FILE += eb.rc

OTHER_FILES += \
  shared.pri \
  static.pri \
  eb.rc \
  ChangeLog \
  COPYING \
  README

# EOF
