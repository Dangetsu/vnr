# vnragent.pro
# 1/22/2013 jichi

CONFIG += noqtgui dll
include(../../../config.pri)
#include($$LIBDIR/detoursutil/detoursutil.pri)
include($$LIBDIR/disasm/disasm.pri)
include($$LIBDIR/dyncodec/dyncodec.pri)
include($$LIBDIR/libqxt/libqxt.pri)
include($$LIBDIR/memdbg/memdbg.pri)
#include($$LIBDIR/mhook/mhook.pri)
#include($$LIBDIR/mhook-disasm/mhook-disasm.pri)
include($$LIBDIR/ntinspect/ntinspect.pri)
#include($$LIBDIR/qtembedapp/qtembedapp.pri) # needed by app runner
include($$LIBDIR/qtembedplugin/qtembedplugin.pri)
#include($$LIBDIR/qtmetacall/qtmetacall.pri)
include($$LIBDIR/qtjson/qtjson.pri)
include($$LIBDIR/qtdyncodec/qtdyncodec.pri)
include($$LIBDIR/qtrichruby/qtrichruby.pri)
include($$LIBDIR/qtsocketsvc/qtsocketpack.pri)
include($$LIBDIR/qtsocketsvc/qtsocketpipe.pri)
include($$LIBDIR/qtsocketsvc/qtlocalcli.pri)
#include($$LIBDIR/qtsocketsvc/qttcpcli.pri)
include($$LIBDIR/sakurakit/sakurakit.pri)
include($$LIBDIR/vnrsharedmemory/vnrsharedmemory.pri)
include($$LIBDIR/mono/mono.pri)
include($$LIBDIR/windbg/windbg.pri)
#include($$LIBDIR/winevent/winevent.pri)
include($$LIBDIR/winkey/winkey.pri)
include($$LIBDIR/winhook/winhook.pri)
include($$LIBDIR/winiter/winiter.pri)
include($$LIBDIR/winquery/winquery.pri)
#include($$LIBDIR/wintimer/wintimer.pri)
include($$LIBDIR/winmutex/winmutex.pri)
include($$LIBDIR/winsinglemutex/winsinglemutex.pri)

#DEFINES += WINHOOK_NO_LIBC # needed to hijack memcpy in nova.cc

#include($$LIBDIR/vnragent/vnragent.pri)

# Services
#HEADERS += $$SERVICEDIR/reader/metacall.h

## Libraries

#CONFIG  += noqt
QT      += core network
QT      -= gui

#INCLUDEPATH += $$D3D_HOME/include
#LIBS    += -ld3d9 -L$$D3D_HOME/lib/x86

#LIBS    += -lkernel32
#LIBS    += -luser32
#LIBS    += -lpsapi
#LIBS    += -ladvapi32   # needed by RegQueryValueEx
LIBS    += -lgdi32      # needed by game engines
LIBS    += -lshell32    # needed by get system path

## Sources

TEMPLATE = lib
TARGET  = vnragent

HEADERS += \
  driver/maindriver.h \
  driver/maindriver_p.h \
  driver/rpcclient.h \
  driver/rpcclient_p.h \
  driver/settings.h \
  embed/embeddriver.h \
  embed/embedmanager.h \
  embed/embedmemory.h \
  engine/enginecontroller.h \
  engine/enginedef.h \
  engine/enginefactory.h \
  engine/enginehash.h \
  engine/enginemodel.h \
  engine/enginesettings.h \
  engine/engineutil.h \
  engine/util/textcache.h \
  engine/util/textunion.h \
  hijack/hijackdriver.h \
  hijack/hijackfuns.h \
  hijack/hijackmanager.h \
  hijack/hijackmodule.h \
  hijack/hijackmodule_p.h \
  hijack/hijackhelper.h \
  hijack/hijacksettings.h \
  window/windowdriver.h \
  window/windowdriver_p.h \
  window/windowhash.h \
  window/windowmanager.h \
  util/codepage.h \
  util/dyncodec.h \
  util/i18n.h \
  util/location.h \
  util/msghandler.h \
  util/textutil.h \
  config.h \
  debug.h \
  growl.h \
  loader.h

SOURCES += \
  driver/maindriver.cc \
  driver/rpcclient.cc \
  driver/settings.cc \
  embed/embeddriver.cc \
  embed/embedmanager.cc \
  embed/embedmemory.cc \
  engine/enginecontroller.cc \
  engine/enginefactory.cc \
  engine/engineutil.cc \
  hijack/hijackdriver.cc \
  hijack/hijackfuns.cc \
  hijack/hijackmanager.cc \
  hijack/hijackmodule.cc \
  hijack/hijackmodule_kernel32.cc \
  hijack/hijackmodule_user32.cc \
  hijack/hijackhelper.cc \
  window/windowdriver.cc \
  window/windowdriver_p.cc \
  window/windowmanager.cc \
  util/codepage.cc \
  util/dyncodec.cc \
  util/i18n.cc \
  util/location.cc \
  util/msghandler.cc \
  util/textutil.cc \
  growl.cc \
  loader.cc \
  main.cc

# Engine models
HEADERS += \
  engine/model/age.h \
  engine/model/aoi.h \
  engine/model/bgi.h \
  engine/model/circus.h \
  engine/model/cmvs.h \
  engine/model/cotopha.h \
  engine/model/cs2.h \
  engine/model/debonosu.h \
  engine/model/elf.h \
  engine/model/escude.h \
  engine/model/fvp.h \
  engine/model/gxp.h \
  engine/model/lcse.h \
  engine/model/leaf.h \
  engine/model/lucifen.h \
  engine/model/luna.h \
  engine/model/malie.h \
  engine/model/minori.h \
  engine/model/mono.h \
  engine/model/nexton.h \
  engine/model/nitro.h \
  engine/model/pal.h \
  engine/model/pensil.h \
  engine/model/qlie.h \
  engine/model/retouch.h \
  engine/model/rgss.h \
  engine/model/rio.h \
  engine/model/siglus.h \
  engine/model/silkys.h \
  engine/model/system4.h \
  engine/model/taskforce.h \
  engine/model/unicorn.h \
  engine/model/waffle.h \
  engine/model/will.h \
  engine/model/wolf.h
  #engine/model/systemc.h
  #engine/model/horkeye.h
  #engine/model/majiro.h
  #engine/model/sideb.h
  #engine/model/tamamo.h
  ##engine/model/nexas.h
  #engine/model/rejet.h
  #engine/model/yuka.h
SOURCES += \
  engine/model/age.cc \
  engine/model/aoi.cc \
  engine/model/bgi.cc \
  engine/model/circus.cc \
  engine/model/cmvs.cc \
  engine/model/cotopha.cc \
  engine/model/cs2.cc \
  engine/model/debonosu.cc \
  engine/model/elf.cc \
  engine/model/escude.cc \
  engine/model/fvp.cc \
  engine/model/gxp.cc \
  engine/model/lcse.cc \
  engine/model/leaf.cc \
  engine/model/lucifen.cc \
  engine/model/luna.cc \
  engine/model/malie.cc \
  engine/model/minori.cc \
  engine/model/mono.cc \
  engine/model/nexton.cc \
  engine/model/nitro.cc \
  engine/model/pal.cc \
  engine/model/pensil.cc \
  engine/model/qlie.cc \
  engine/model/retouch.cc \
  engine/model/rgss.cc \
  engine/model/rio.cc \
  engine/model/siglus.cc \
  engine/model/silkys.cc \
  engine/model/system4.cc \
  engine/model/system43.cc \
  engine/model/system44.cc \
  engine/model/taskforce.cc \
  engine/model/unicorn.cc \
  engine/model/waffle.cc \
  engine/model/will.cc \
  engine/model/wolf.cc
  #engine/model/systemc.cc
  #engine/model/horkeye.cc
  #engine/model/majiro.cc
  #engine/model/sideb.cc
  #engine/model/tamamo.cc
  #engine/model/nexas.cc
  #engine/model/rejet.cc
  #engine/model/yuka.cc

HEADERS += \
  engine/model/lova.h
SOURCES += \
  engine/model/lova.cc

#!wince*: LIBS += -lshell32
#RC_FILE += vnragent.rc

OTHER_FILES += vnragent.rc

# EOF
