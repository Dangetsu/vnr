# defines.pri
# 3/28/2013 jichi
#
# See build-pre.h and build-post.h

## Path

INCLUDEPATH += $$PWD/include

## Config

DEFINES += \
  HAVE_ATOLL \

win32: DEFINES += \
  HAVE__GETDCWD \
  HAVE_DIRECT_H \
  DOS_FILE_PATH

unix: DEFINES += \
  HAVE_GETADDRINFO \
  HAVE_GETNAMEINFO \
  HAVE_GAI_STRERROR \
  HAVE_NET_IF \
  HAVE_STRCASECMP \
  HAVE_STRUCT_IN6_ADDR \
  HAVE_STRUCT_SOCKADDR_IN6

#EB_ENABLE_PTHREAD
#ENABLE_PTHREAD
#ENABLE_NLS # <libintl.h> from gettext
#EB_ENABLE_EBNET   # internet access

# EOF
