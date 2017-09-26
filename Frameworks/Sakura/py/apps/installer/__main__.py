# coding: utf8
# __main__.py
# 12/13/2012 jichi
#
# Top-level root objects (root object = object that do not have parent)
# - app.Application
# - main.MainObject: Root of all non-widget qobject

import os, sys

def print_help():
  print """\
usage: python . [options]

Launch the app.

options:
  --debug   Print debug output
  --help    Print help"""

def reset_win_path():
  try:
    print "installer:reset_win_path: enter"
    windir = os.environ['windir'] or os.environ['SystemRoot'] or r"C:\Windows"
    path = os.pathsep.join((
      windir,
      os.path.join(windir, 'System32'),
    ))
    os.environ['PATH'] = path
    print "installer:reset_win_path: leave"
  except Exception, e:
    print "installer:reset_win_path: leave, exception =", e

def initenv():
  print "installer:initenv: enter"

  # Add current and parent folder to module path
  mainfile = os.path.abspath(__file__)
  maindir = os.path.dirname(mainfile)

  sys.path.append(maindir)

  if os.name == 'nt':
    reset_win_path()

  # Python chdir is buggy for unicode
  #os.chdir(maindir)

  import config
  map(sys.path.append, config.ENV_PYTHONPATH)

  paths = os.pathsep.join(config.ENV_PATH)
  try:
    os.environ['PATH'] = paths + os.pathsep + os.environ['PATH']
  except KeyError: # PATH does not exists?!
    os.environ['PATH'] = paths

  print "installer:initenv: leave"

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
  print "installer: debug = %s" % skdebug.DEBUG

  from sakurakit.skdebug import dprint, dwarn
  dprint("enter")

  if '--help' in sys.argv:
    print_help()
    dprint("leave: help")
    return

  # Singleton
  #dprint("check single instance")
  #from sakurakit import skipc
  #inst = skipc.SingleInstance()
  #single_app = inst.passed
  #if not single_app:
  #  dprint("multiple instances are running")
  #  sys.exit(-1)

  dprint("python = %s" % sys.executable)
  #dprint("rootdir = %s" % rootdir)
  #dprint("mecabrc = %s" % mecabrc_path)

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

  dprint("update settings")
  if ss.version() != config.VERSION_TIMESTAMP:
    dprint("app update detected, migrate settings")

    ss.setVersion(config.VERSION_TIMESTAMP)
    ss.sync()

  dprint("set max thread count")
  from PySide.QtCore import QThreadPool
  if QThreadPool.globalInstance().maxThreadCount() < config.QT_THREAD_COUNT:
    QThreadPool.globalInstance().setMaxThreadCount(config.QT_THREAD_COUNT)

  dprint("create main object")
  import main
  m = main.MainObject()
  m.run(a.arguments())

  #import netman
  #netman.manager().queryComments(gameId=183)

  #import hashman
  #print hashman.md5sum('/Users/jichi/tmp/t.cpp')
  dprint("exec")
  sys.exit(a.exec_())

if __name__ == '__main__':
  print "installer: enter"
  initenv()
  main()
  print "installer: leave" # unreachable

# EOF
