# coding: utf8
# debug.py
# 11/16/2012 jichi

import sys, os
def initenv():

  # Add current and parent folder to module path
  mainfile = os.path.abspath(__file__)
  maindir = os.path.dirname(mainfile)

  sys.path.append(maindir)
  os.chdir(maindir)

  import config
  map(sys.path.append, config.ENV_PYTHONPATH)
  if hasattr(config, 'APP_PYTHONPATH'):
    map(sys.path.append, config.APP_PYTHONPATH)

  for it in 'PATH', 'LD_LIBRARY_PATH', 'DYLD_LIBRARY_PATH':
    try: os.environ[it] += os.pathsep + os.pathsep.join(config.ENV_PATH)
    except: pass

def app():
  import app
  a = app.Application(sys.argv)
  #a.loadTranslations()
  return a

def app_exec(timeout=1000):
  from PySide.QtCore import QTimer
  from Qt5.QtWidgets import QApplication
  app = QApplication(sys.argv)
  QTimer.singleShot(timeout, app.quit)
  return app.exec_()

if __name__ == '__main__':
  print "debug: enter"
  initenv()

# EOF
