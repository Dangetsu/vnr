# coding: utf8
# __main__.py
# 10/5/2012 jichi
#
# Top-level root objects (root object = object that do not have parent)
# - app.Application
# - main.MainObject: Root of all non-widget qobject

def print_help():
  print """\
usage: python . location vid1 ...

Launch the app.

options:
  --debug   Print debug output
  --help    Print help"""

def main():
  """
  @return  int
  """
  import os, sys
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
  print >> sys.stderr, "reader: debug = %s" % skdebug.DEBUG

  from sakurakit.skdebug import dprint, dwarn
  dprint("enter")

  if '--help' in sys.argv:
    print_help()
    dprint("exit: help")
    #sys.exit(os.EX_USAGE)
    return 0

  dprint("create app")
  import app
  a = app.Application(sys.argv)

  #dprint("set max thread count")
  #from PySide.QtCore import QThreadPool
  #if QThreadPool.globalInstance().maxThreadCount() < config.QT_THREAD_COUNT:
  #  QThreadPool.globalInstance().setMaxThreadCount(config.QT_THREAD_COUNT)

  dprint("create main object")

  import main
  m = main.MainObject(a)
  #m.run(a.arguments()) # arguments differs on different system
  m.run(a.arguments())

  dprint("exec")
  returnCode = a.exec_()
  #skos.kill_my_process()
  return returnCode

if __name__ == '__main__':
  import sys
  print >> sys.stderr, "download: enter"
  #print __file__
  import initrc
  initrc.initenv()
  initrc.probemod()
  #initrc.checkintegrity()

  ret = main()
  print >> sys.stderr, "download: leave, ret =", ret
  sys.exit(ret)

# EOF
