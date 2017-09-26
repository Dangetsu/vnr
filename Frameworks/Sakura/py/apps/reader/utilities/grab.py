# coding: utf8
# grab.py
# 12/6/2012 jichi

import os
from datetime import datetime
from PySide.QtGui import QPixmap
from sakurakit import skclip, skwidgets
from sakurakit.skclass import memoized

@memoized
def manager():
  ret = GrabManager()
  import settings
  ss = settings.global_()
  ret.setLocation(ss.grabLocation())
  ss.grabLocationChanged.connect(ret.setLocation)
  return ret

class _GrabManager:

  def __init__(self):
    self.location = '' # str

  def savePixmap(self, pm, path=None, format='png', clipboard=True, quality=-1):
    """
    @param  pm  QPixmap
    @param* path  unicode
    @param* format  str
    @param* clipboard  bool
    @param* quality  int
    @return  bool
    """
    ok = not pm.isNull()
    if ok:
      if clipboard:
        skclip.setpixmap(pm)
      if not path:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        fileName = "vnr-capture-%ix%i-%s.%s" % (pm.width(), pm.height(), ts, format)

        location = self.location
        if not location or not os.path.exists(location):
          from sakurakit import skpaths
          location = skpaths.DESKTOP
        path = os.path.join(location, fileName)
      ok = pm.save(path, format, quality)
    return ok

class GrabManager:
  def __init__(self):
    self.__d = _GrabManager()

  def location(self): return self.__d.location
  def setLocation(self, v): self.__d.location = v

  def grabWindow(self, wid, x=0, y=0, width=-1, height=-1, **kwargs):
    """
    @param  wid  WID
    @param* x  int
    @param* y  int
    @param* width  int
    @param* height  int

    @param* path  unicode
    @param* format  str
    @param* clipboard  bool  whether save to clipboard
    @param* quality  int
    @return  bool
    """
    if not wid:
      return
    pm = QPixmap.grabWindow(skwidgets.to_wid(wid), x, y, width, height)
    return self.__d.savePixmap(pm, **kwargs)

  def grabWidget(w, x=0, y=0, width=-1, height=-1, **kwargs):
    """
    @param  w  QWidget
    @param* x  int
    @param* y  int
    @param* width  int
    @param* height  int

    @param* path  unicode
    @param* format  str
    @param* clipboard  bool  whether save to clipboard
    @param* quality  int
    @return  bool
    """
    if not w:
      return
    pm = QPixmap.grabWidget(w, x, y, width, height)
    return self.__d.savePixmap(pm, **kwargs)

  def grabDesktop(*args, **kwargs):
    """
    @param* x  int
    @param* y  int
    @param* width  int
    @param* height  int

    @param* path  unicode
    @param* format  str
    @param* clipboard  bool  whether save to clipboard
    @param* quality  int
    @return  bool
    """
    from PySide.QtCore import QApplication
    qApp = QApplication.instance()
    return bool(qApp) and self.grabWindow(qApp.desktop().winId(), *args, **kwargs)

# EOF
