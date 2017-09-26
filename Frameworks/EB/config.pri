# config.pri
# 9/3/2011 jichi

## Locations

ROOTDIR = $$PWD
BUILDDIR = $$ROOTDIR/build

PYDIR   = $$ROOTDIR/site-packages
SRCDIR  = $$ROOTDIR/src
LIBDIR  = $$SRCDIR/lib
MODULEDIR  = $$SRCDIR/modules
#PLUGINDIR  = $$SRCDIR/plugins

DESTDIR         = $$BUILDDIR
#win32:  DESTDIR_TARGET  = $$BUILDDIR/release.win
#unix:   DESTDIR_TARGET  = $$BUILDDIR/release.unix
#mac:    DESTDIR_TARGET  = $$BUILDDIR/release.mac

LIBS            += -L$$DESTDIR
mac:  LIBS      += -F$$DESTDIR

INCLUDEPATH += \
  $$SRCDIR \
  $$SRCDIR/lib \
  $$SRCDIR/modules \
  $$SRCDIR/plugins

## Compiling options

mac:    CONFIG -= ppc ppc64
win32: DEFINES += UNICODE

#CONFIG += x86 x86_64 ppc64

# C++11
win32:  QMAKE_CXXFLAGS += -Zc:auto
unix:   QMAKE_CXXFLAGS += -std=c++0x
mac    {
  # Enable TR1 such as tuple
  # Clang is required to take place of llvm gcc, which uses /usr/lib/libstdc++.dylib
  #QMAKE_CXXFLAGS += -stdlib=libc++
  #QMAKE_LFLAGS += -stdlib=libc++
}

# MSVC
win32 {
  # Disable checked iterator and compiler warning.
  # SCL: http://msdn.microsoft.com/en-us/library/aa985896.aspx
  # SCL Warning: http://msdn.microsoft.com/en-us/library/aa985974.aspx
  # Performance comparison: http://askldjd.wordpress.com/2009/09/13/stl-performance-comparison-vc71-vc90-and-stlport/
  DEFINES += _SECURE_SCL=0 _SCL_SECURE_NO_WARNINGS

  # Disable CRT string function warnings
  DEFINES += _CRT_SECURE_NO_WARNINGS

  # Disable CRT posix warnings
  #DEFINES += _CRT_NONSTDC_NO_DEPRECATE

  QMAKE_CXXFLAGS += -wd4819 # ignore warning on Japanese characters
}

# GCC

#QMAKE_LFLAGS +=

## External Libraries

win32 {
  DEV_HOME      = c:/dev
  BOOST_HOME    = $$DEV_HOME/boost
  #PYTHON_HOME  = $$ROOTDIR/../Python
  PYTHON_HOME   = C:/Python
  PYSIDE_HOME   = $$PYTHON_HOME/Lib/site-packages/PySide
  ZLIB_HOME     = $$DEV_HOME/zlib

  DIRENT_HOME   = $$DEV_HOME/dirent
  INTTYPES_HOME = $$DEV_HOME/inttypes
}
mac {
  MACPORTS_HOME = /opt/local
  BOOST_HOME    = $$MACPORTS_HOME
  PYTHON_HOME   = $$MACPORTS_HOME/Library/Frameworks/Python.framework/Versions/Current
  PYSIDE_HOME   = $$MACPORTS_HOME
  ZLIB_HOME     = $$MACPORTS_HOME

  DIRENT_HOME   = /usr
  INTTYPES_HOME = /usr
}

win32: INCLUDEPATH += $$INTTYPES_HOME/include

## Config

CONFIG(release) {
  #DEFINES += QT_NO_DEBUG_OUTPUT QT_NO_WARNING_OUTPUT
  message(CONFIG release)
}

CONFIG(noqt) {
  message(CONFIG noqt)
  CONFIG += noqtcore noqtgui
  CONFIG -= qt
}
CONFIG(noqtcore) {
  message(CONFIG noqtcore)
  QT     -= core
  LIBS   -= -lQtCore
}
CONFIG(noqtgui) {
  message(CONFIG noqtgui)
  QT     -= gui
  LIBS   -= -lQtGui
  mac: CONFIG -= app_bundle
}

CONFIG(nocrt) {
  message(CONFIG nocrt)
  win32 {
    QMAKE_CFLAGS                -= -MD -MDd
    QMAKE_CFLAGS_DEBUG          -= -MD -MDd
    QMAKE_CFLAGS_RELEASE        -= -MD -MDd
    QMAKE_CFLAGS_RELEASE_WITH_DEBUGINFO -= -MD -MDd
    QMAKE_CXXFLAGS              -= -MD -MDd
    QMAKE_CXXFLAGS_DEBUG        -= -MD -MDd
    QMAKE_CXXFLAGS_RELEASE      -= -MD -MDd
    QMAKE_CXXFLAGS_RELEASE_WITH_DEBUGINFO -= -MD -MDd

    #QMAKE_LFLAGS                += -NODEFAULTLIB:msvcrt.lib \
    #                               -NODEFAULTLIB:msvcrtd.lib
  }
}

CONFIG(pyplugin) {
  message(CONFIG pyplugin)
  INCLUDEPATH   += $$PYTHON_HOME/include/python2.7 $$PYTHON_HOME/include

  unix:   LIBS  += -L$$PYTHON_HOME/lib -lpython2.7
  win32:  LIBS 	+= -L$$PYTHON_HOME/libs -lpython27

  win32: CONFIG += dll
  unix:  QMAKE_EXTENSION_SHLIB = so
  win32: QMAKE_EXTENSION_SHLIB = pyd
}

## Translation

CODECFORTR = UTF-8
#CODECFORSRC = UTF-8    # there are sources in SJIS encoding

# EOF
