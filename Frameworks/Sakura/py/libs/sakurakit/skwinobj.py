# coding: utf8
# skwinobj.py
# 10/21/2012 jichi
# Windows only
__all__ = (
  'SkWindowPyObject', 'SkWindowObject',
  'SkTaskBarPyObject', 'SkTaskBarObject',
)

from functools import partial
from PySide.QtCore import Signal, Property, QObject, Qt, QTimer
import skevents, skos
from skclass import Q_Q

if skos.WIN:
  import skwin, qtwin
  from skdebug import dprint

  # Windows

  class SkWindowPyObject(object):
    """Wrapper of window handle
    The type of a window handle is the same as WId in <QtGui/qwindowdefs.h> and HWND in <windefs.h>
    """
    def __init__(self, handle=0):
      self.__h = handle

    @property
    def handle(self): return self.__h
    @handle.setter
    def handle(self, val): self.__h = val

    @property
    def valid(self): return bool(self.__h) and skwin.is_window(self.__h)
    @property
    def title(self): return skwin.get_window_text(self.__h) if self.valid else ""
    @property
    def visible(self): return self.valid and skwin.is_window_visible(self.__h)
    @property
    def minimized(self): return self.valid and skwin.is_window_minimized(self.__h)
    @property
    def fullscreen(self): return self.valid and skwin.is_window_fullscreen(self.__h)

    @property
    def rect(self):
      """
      @return  (int left, int top, int right, int bottom)
      """
      return skwin.get_window_rect(self.__h) if self.valid else (0, 0, 0, 0)

    @property
    def contentsize(self):
      """
      @return  (int w, int h)
      """
      return skwin.get_content_size(self.__h) if self.valid else (0, 0)

    @property
    def x(self): return self.rect[0] # left,_,_,_

    @property
    def y(self): return self.rect[1] # _,top,_,_

    @property
    def width(self): left,_,right,_ = self.rect; return right - left

    @property
    def height(self): _,top,_,bottom = self.rect; return bottom - top

    @property
    def contentwidth(self): return self.contentsize[0]

    @property
    def contentheight(self): return self.contentsize[1]

    @property
    def contentborderwidth(self): return (self.width - self.contentwidth)/2

    @property
    def titlebarheight(self): return self.height - self.contentborderwidth

  @Q_Q
  class _SkWindowObject(object):
    def __init__(self, q, wid=0, pyobj=None):
      if not pyobj:
        pyobj = SkWindowPyObject(wid)
      self.obj = pyobj
      self.valid = self.obj.valid

      # Refresh timer
      self.refreshTimer = QTimer(q)
      self.refreshTimer.setInterval(200)
      self.refreshTimer.timeout.connect(q.refresh)

      self.refreshCount = 0 # int

    def reset(self):
      """Reset cached fields"""
      self.valid = False
      if hasattr(self, 'geometry'):
        del self.geometry
      if hasattr(self, 'visible'):
        del self.visible
      if hasattr(self, 'windowState'):
        del self.windowState
      if hasattr(self, 'contentSize'):
        del self.contentSize

    def updateWindowState(self):
      self.windowState = (Qt.WindowFullScreen if self.obj.fullscreen else
                          Qt.WindowMinimized if self.obj.minimized else
                          Qt.WindowNoState)

  class SkWindowObject(QObject):
    """ Wrapper to monitor window state changes.
    The interface of this class comply with QWidget class.
    """
    def __init__(self, parent=None, winId=0, pyObject=None):
      super(SkWindowObject, self).__init__(parent)
      d = self.__d = _SkWindowObject(self, winId, pyObject)
      if winId:
        d.refreshTimer.start()

    ## WId ##

    def setWinId(self, handle):
      d = self.__d
      if d.obj.handle != handle:
        d.obj.handle = handle
        if handle and not d.refreshTimer.isActive():
          d.refreshTimer.start()
        elif not handle and d.refreshTimer.isActive():
          d.refreshTimer.stop()
          d.reset()
        self.winIdChanged.emit(handle)
        self.activeChanged.emit(bool(handle))
        if not handle:
          self.windowClosed.emit()
        skevents.runlater(self.refresh)

        # Make sure to always emit full screen signal after opening games
        if handle and self.fullScreen:
          skevents.runlater(partial(
            self.fullScreenChanged.emit, self.fullScreen))

    # FIXME: PySide handle is not long type! This would crash QML
    winIdChanged = Signal(long)
    winId = Property(long,
        lambda self: self.__d.obj.handle,
        setWinId,
        notify=winIdChanged)

    activeChanged = Signal(long)
    active = Property(bool,
        lambda self: bool(self.__d.obj.handle),
        notify=activeChanged)

    windowClosed = Signal()

    def isValid(self):
      self.__d.valid = self.__d.obj.valid
      return self.__d.valid
    validChanged = Signal(bool)
    valid = Property(bool, isValid, notify=validChanged)

    def startRefresh(self): self.__d.refreshTimer.start()
    def stopRefresh(self): self.__d.refreshTimer.stop()

    def refresh(self):
      d = self.__d
      d.refreshCount = (d.refreshCount + 1) % 1000 # prevent from being too large

      old = d.valid
      new = self.valid
      if old != new:
        self.validChanged.emit(new)

      old = self.isVisible()
      new = d.visible = d.obj.visible
      if old != new:
        self.visibleChanged.emit(new)

      old = self.geometry()
      new = qtwin.qrect_from_rect(d.obj.rect)
      if old != new:
        d.geometry = new
        if old.x() != new.x():
          self.xChanged.emit(new.x())
        if old.y() != new.y():
          self.yChanged.emit(new.y())
        if old.width() != new.width():
          self.widthChanged.emit(new.width())
        if old.height() != new.height():
          self.heightChanged.emit(new.height())

        # Only update content size when geometry changed
        #old = self.contentSize()
        #new = d.obj.contentsize
        #if old != new:
        #  d.contentSize = new
        #  if old[0] != new[0]:
        #    self.contentWidthChanged.emit(new[0])
        #  if old[1] != new[1]:
        #    self.contentHeightChanged.emit(new[1])

        # Only update window state when geometry changed
        old = self.windowState()
        d.updateWindowState()
        new = d.windowState
        if old != new:
          dprint("window state changed")
          self.windowStateChanged.emit(new, old)
          if old & Qt.WindowFullScreen != new & Qt.WindowFullScreen:
            self.fullScreenChanged.emit(bool(new & Qt.WindowFullScreen))
          if old & Qt.WindowMinimized != new & Qt.WindowMinimized:
            self.minimizedChanged.emit(bool(new & Qt.WindowMinimized))

      # I am not sure if this could cause slowdown in Rance, but the contentWidth might change when geometry not changed
      # Slowdown the refresh rate and see if it could work
      #elif d.refreshCount % 5 == 0: # refresh every 1 second = 200 * 5
      old = self.contentSize()
      new = d.obj.contentsize
      if old != new:
        d.contentSize = new
        if old[0] != new[0]:
          self.contentWidthChanged.emit(new[0])
        if old[1] != new[1]:
          self.contentHeightChanged.emit(new[1])

    def refreshInterval(self):
      """Default is 200 msecs"""
      return self.__d.refreshTimer.interval()

    def setRefreshInterval(self, msecs):
      self.__d.refreshTimer.setInterval(msecs)

    #- Title ##
    windowTitle = Property(unicode,
        lambda self: self.__d.obj.title)

    ## States ##

    def isVisible(self): # Result is cached
      try: return self.__d.visible
      except AttributeError:
        ret = self.__d.visible = self.__d.obj.visible
        return ret
    visibleChanged = Signal(bool)
    visible = Property(bool, isVisible, notify=visibleChanged)

    def isMinimized(self): return self.__d.obj.minimized
    minimizedChanged = Signal(bool)
    minimized = Property(bool, isMinimized, notify=minimizedChanged)

    def isFullScreen(self): return self.__d.obj.fullscreen
    fullScreenChanged = Signal(bool)
    fullScreen = Property(bool, isFullScreen, notify=fullScreenChanged)

    windowStateChanged = Signal(Qt.WindowState, Qt.WindowState) # (new, old)
    def windowState(self): # Result is cached
      try: return self.__d.windowState
      except AttributeError:
        self.__d.updateWindowState()
        return self.__d.windowState

    ## Geometry ##

    def geometry(self): # Result is cached
      """
      @return  QRect
      """
      try: return self.__d.geometry
      except AttributeError:
        ret = self.__d.geometry = qtwin.qrect_from_rect(self.__d.obj.rect)
        return ret

    def contentSize(self): # Result is cached
      """
      @return  (int width, int height)
      """
      try: return self.__d.contentSize
      except AttributeError:
        ret = self.__d.contentSize = self.__d.obj.contentsize
        return ret

    def pos(self): return self.geometry().topLeft()

    def size(self): return self.geometry().size()

    xChanged = Signal(int)
    x = Property(int,
        lambda self: self.geometry().x(),
        notify=xChanged)

    yChanged = Signal(int)
    y = Property(int,
        lambda self: self.geometry().y(),
        notify=yChanged)

    widthChanged = Signal(int)
    width = Property(int,
        lambda self: self.geometry().width(),
        notify=widthChanged)

    heightChanged = Signal(int)
    height = Property(int,
        lambda self: self.geometry().height(),
        notify=heightChanged)

    contentWidthChanged = Signal(int)
    contentWidth = Property(int,
        lambda self: self.contentSize()[0],
        notify=contentWidthChanged)

    contentHeightChanged = Signal(int)
    contentHeight = Property(int,
        lambda self: self.contentSize()[1],
        notify=contentHeightChanged)

  class SkTaskBarPyObject(SkWindowPyObject):
    def __init__(self):
      handle = skwin.get_taskbar_window()
      super(SkTaskBarPyObject, self).__init__(handle)

    @property
    def autoHide(self):
      return skwin.is_taskbar_autohide(self.handle)

    @autoHide.setter
    def autoHide(self, t):
      skwin.set_taskbar_autohide(t, self.handle)

    @property
    def visible(self):
      """@reimp"""
      return self.valid and skwin.is_taskbar_visible(self.handle)

    @property
    def minimized(self):
      """@reimp"""
      return False

    @property
    def fullscreen(self):
      """@reimp"""
      return False

  class SkTaskBarObject(SkWindowObject):
    def __init__(self, parent=None):
      pyobj = SkTaskBarPyObject()
      super(SkTaskBarObject, self).__init__(parent, pyObject=pyobj)

    def setAutoHide(self, t):
      obj = self.__d.obj
      if t != obj.autoHide:
        obj.autoHide = t
        self.autoHideChanged.emit(t)
    autoHideChanged = Signal(bool)
    autoHide = Property(bool,
        lambda self: self.__d.obj.autoHide,
        setAutoHide,
        notify=autoHideChanged)

else: # dummy
  from PySide import QtCore
  DEBUG = skos.MAC

  class SkWindowPyObject(object):
    def __init__(self, handle=0):
      self.handle = 0
      self.valid = False
      self.title = ""
      self.visible = False
      self.minimized = False
      self.fullscreen = False
      self.rect = 0, 0, 0, 0
      self.x = self.y = self.width = self.height = 0

  class SkWindowObject(QObject):
    def __init__(self, parent=None, winId=0, pyObject=None):
      super(SkWindowObject, self).__init__(parent)

    def winId(self): return 0
    def setWinId(self, handle): pass
    winIdChanged = Signal(long)
    winId = Property(long, winId, setWinId, notify=winIdChanged)
    windowClosed = Signal()

    def isValid(self): return False
    validChanged = Signal(bool)
    valid = Property(bool, isValid, notify=validChanged)

    def refresh(self): pass

    def refreshInterval(self): return 0
    def setRefreshInterval(self, msecs): pass

    ## Title ##

    def windowTitle(self): return ""
    windowTitle = Property(unicode, windowTitle)

    ## States ##

    def isVisible(self): return True if DEBUG else False
    visibleChanged = Signal(bool)
    visible = Property(bool, isVisible, notify=visibleChanged)

    def isMinimized(self): return False
    minimizedChanged = Signal(bool)
    minimized = Property(bool, isMinimized, notify=minimizedChanged)

    def isFullScreen(self): return False
    fullScreenChanged = Signal(bool)
    fullScreen = Property(bool, isFullScreen, notify=fullScreenChanged)

    windowStateChanged = Signal(Qt.WindowState, Qt.WindowState)
    def windowState(self): return Qt.WindowNoState

    def geometry(self): return QtCore.QRect()
    def pos(self): return QtCore.QPoint()
    def size(self): return QtCore.QSize()

    def x(self): return 200 if DEBUG else 0
    xChanged = Signal(int)
    x = Property(int, x, notify=xChanged)

    def y(self): return 100 if DEBUG else 0
    yChanged = Signal(int)
    y = Property(int, y, notify=yChanged)

    def width(self): return 600 if DEBUG else 0
    widthChanged = Signal(int)
    width = Property(int, width, notify=widthChanged)

    def height(self): return 400 if DEBUG else 0
    heightChanged = Signal(int)
    height = Property(int, height, notify=heightChanged)

  class SkTaskBarPyObject(SkWindowPyObject):
    def __init__(self):
      super(SkTaskBarPyObject, self).__init__()
      self.autoHide = False

  class SkTaskBarObject(SkWindowObject):
    def __init__(self, parent=None):
      super(SkTaskBarObject, self).__init__(parent)

    def setAutoHide(self, t): pass
    autoHideChanged = Signal(bool)
    autoHide = Property(bool,
        lambda self: False,
        setAutoHide,
        notify=autoHideChanged)

# EOF
