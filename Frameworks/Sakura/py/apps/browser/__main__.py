# coding: utf8
# __main__.py
# 12/13/2012 jichi
#
# Top-level root objects (root object = object that do not have parent)
# - app.Application
# - main.MainObject: Root of all non-widget qobject

## MAIN TEMPLATE BEGIN ##

import os, sys

#def u_from_native(s):
#  # Following contents are copied from sakurakit.skunicode
#  import locale
#  lc, enc = locale.getdefaultlocale()
#  return s.decode(enc, errors='ignore')
#u = u_from_native

def print_help():
  print """\
usage: python . [options]

Launch the app.

options:
  --debug   Print debug output
  --help    Print help"""

def main():
  # Use UTF-8 encoding for Qt
  from PySide.QtCore import QTextCodec
  #sys_codec = QTextCodec.codecForLocale()
  u8codec = QTextCodec.codecForName("UTF-8")
  QTextCodec.setCodecForCStrings(u8codec)
  QTextCodec.setCodecForTr(u8codec)

  import config
  from sakurakit import skdebug
  #skdebug.DEBUG = config.APP_DEBUG or '--debug' in sys.argv
  skdebug.DEBUG = '--debug' in sys.argv
  print "browser: debug = %s" % skdebug.DEBUG

  from sakurakit.skdebug import dprint, dwarn
  dprint("enter")

  if '--help' in sys.argv:
    print_help()
    dprint("leave: help")
    return

  dprint("python = %s" % sys.executable)
  #dprint("rootdir = %s" % rootdir)
  #dprint("mecabrc = %s" % mecabrc_path)

  from sakurakit import skos
  if skos.WIN:
    dprint("set app id")
    from sakurakit import skwin
    skwin.set_app_id("org.sakurakit.browser")

  import rc
  for it in (
      rc.DIR_CACHE_DATA,
      rc.DIR_CACHE_HISTORY,
      rc.DIR_CACHE_NETMAN,
      rc.DIR_CACHE_WEBKIT,
    ):
    if not os.path.exists(it):
      try: os.makedirs(it)
      except OSError:
        dwarn("warning: failed to create directory: %s" % it)

  dprint("init opencc")
  from opencc import opencc
  opencc.setdicpaths(config.OPENCC_DICS)

  dprint("create app")
  import app
  a = app.Application(sys.argv)

  dprint("load translations")
  a.loadTranslations()

  # Take the ownership of sakurakit translation
  from sakurakit import sktr
  sktr.manager().setParent(a)

  dprint("load settings")
  import settings
  ss = settings.global_()
  ss.setParent(a)

  reader = settings.reader()
  #reader.setParent(a) # reader does NOT have a app parent

  dprint("update settings")
  ss_version = ss.version()
  if ss_version != config.VERSION_TIMESTAMP:
    dprint("app update detected, migrate settings")

    if ss_version:
      from sakurakit import skfileio

      if ss_version <= 1417339268:
        for it in (
            #rc.DIR_CACHE_DATA,
            rc.DIR_CACHE_HISTORY,
            rc.DIR_CACHE_NETMAN,
            rc.DIR_CACHE_WEBKIT,
          ):
          if os.path.exists(it):
            skfileio.removetree(it)
            try: os.makedirs(it)
            except OSError:
              dwarn("warning: failed to create directory: %s" % it)

      if ss_version <= 1396371158:
        skfileio.removefile(rc.COOKIES_LOCATION)

    ss.setVersion(config.VERSION_TIMESTAMP)
    ss.sync()

  if reader.isCursorThemeEnabled():
    dprint("load cursor theme")
    import curtheme
    curtheme.load()

  from sakurakit import skpaths
  skpaths.append_paths((
    #reader.localeEmulatorLocation(),
    reader.jbeijingLocation(),
    reader.ezTransLocation(),
    reader.atlasLocation(),
    os.path.join(reader.lecLocation(), r"Nova\JaEn") if reader.lecLocation() else "",
    os.path.join(reader.dreyeLocation(), r"DreyeMT\SDK\bin") if reader.dreyeLocation() else "",
  ))

  path = reader.fastaitLocation()
  if path:
    path = os.path.join(path, "GTS")
    if os.path.exists(path):
      from sakurakit import skfileio
      dllpaths = skfileio.listdirs(path)
      if dllpaths:
        skpaths.append_paths(dllpaths)

  dprint("set max thread count")
  from PySide.QtCore import QThreadPool
  if QThreadPool.globalInstance().maxThreadCount() < config.QT_THREAD_COUNT:
    QThreadPool.globalInstance().setMaxThreadCount(config.QT_THREAD_COUNT)

  dprint("load web settings")
  import webrc
  webrc.update_web_settings()

  if reader.isMainlandChina():
    dprint("set up proxy")
    from google import googletts
    googletts.setapi(config.PROXY_GOOGLE_TTS)
    import googleman
    googleman.setapi(config.PROXY_GOOGLE_TRANS)

  dprint("create main object")
  import main
  m = main.MainObject()
  m.run(a.arguments())

  dprint("exec")
  sys.exit(a.exec_())

if __name__ == '__main__':
  import sys
  print >> sys.stderr, "browser: enter"
  #print __file__
  import initrc
  initrc.initenv()
  initrc.probemod()
  #initrc.checkintegrity()

  ret = main()
  print >> sys.stderr, "browser: leave, ret =", ret
  sys.exit(ret)
  #assert False, "unreachable"
  assert False, "unreachable"

# EOF
