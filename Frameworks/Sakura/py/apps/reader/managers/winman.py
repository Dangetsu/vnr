# coding: utf8
# winman.py
# 9/6/2014 jichi

from PySide.QtCore import Slot
from sakurakit.skclass import memoized
from sakurakit.skdebug import dprint, dwarn
from sakurakit.skwinobj import SkWindowObject
import windows

class WindowObject(SkWindowObject):
  def __init__(self, *args, **kwargs):
    super(WindowObject, self).__init__(*args, **kwargs)
    self.referenceCount = 1 # int
    #self.visibleChanged.connect(_raise_window) # make sure ocr popup is on top
    self.minimizedChanged.connect(windows.raise_top_window) # make sure ocr popup is on top

  @Slot()
  def release(self): manager().releaseWindowObject(self)

@memoized
def manager(): return WindowManager()

class _WindowManager:
  def __init__(self):
    self.parent = None # QObject
    self.windows = {} # {long wid:SkWindowObject}

  def createWindowObject(self, wid): # long wid -> WindowObject
    return WindowObject(winId=wid, parent=self.parent)

  def destroyWindowObject(self, w): # WindowObject ->
    w.setWinId(0)
    w.setParent(None)

  def findWindowId(self, w): # WindowObject -> long
    for k,v in self.windows.iteritems():
      if v is w:
        return k
    return 0

class WindowManager:
  def __init__(self):
    self.__d = _WindowManager()

  def setParent(self, parent): self.__d.parent = parent

  def createWindowObject(self, wid): # long wid -> WindowObject
    d = self.__d
    w = d.windows.get(wid)
    if w:
      w.referenceCount += 1
      dprint("reuse object, refcount = %i" % w.referenceCount)
    else:
      w = d.windows[wid] = d.createWindowObject(wid)
      dprint("create new object")
    return w

  def releaseWindowObject(self, w): # WindowObject ->
    d = self.__d
    wid = d.findWindowId(w)
    if wid:
      w.referenceCount -= 1
      dprint("release object, refcount = %i" % w.referenceCount)
      if w.referenceCount <= 0:
        dprint("destroy object")
        del d.windows[wid]
        d.destroyWindowObject(w)
    else:
      dwarn("object not exist")

# EOF
