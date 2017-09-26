# coding: utf8
# splashscreen.py
# 1/10/2014 jichi

from PySide.QtGui import QPixmap
from Qt5.QtWidgets import QSplashScreen
from sakurakit.skdebug import dprint
import rc

class StartupSplashScreen(QSplashScreen):
  def __init__(self):
    img = QPixmap(rc.image_path('splash-wait'))
    super(StartupSplashScreen, self).__init__(img)
    dprint("pass")

  def finishLater(self, timeout=0):
    from sakurakit import skevents
    img = QPixmap(rc.image_path('splash-ready'))
    self.setPixmap(img)
    skevents.runlater(self.finishWindow, timeout)
    dprint("pass")

  def finishWindow(self):
    import windows
    self.finish(windows.top())
    dprint("pass")


# EOF
