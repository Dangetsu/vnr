# coding: utf8
# screenselector.py
# 8/16/2014 jichi
# Windows only
# See: http://sourceforge.net/apps/mediawiki/pyhook/index.php?title=PyHook_Tutorial

# On mouse click warning:
# See: http://sourceforge.net/tracker/?func=detail&aid=2986042&group_id=235202&atid=1096323
# func = self.keyboard_funcs.get(msg)
# => func = self.keyboard_funcs.get( int(str(msg)) )

__all__ = 'ScreenSelector',

if __name__ == '__main__':
  import sys
  sys.path.append('..')

from PySide.QtCore import QObject, Signal
from sakurakit import skos
from sakurakit.skclass import Q_Q, memoizedproperty
from sakurakit.skdebug import dprint
#from sakurakit.skunicode import u

if skos.WIN:

  @Q_Q
  class _ScreenSelector(object):

    def __init__(self):
      self.singleShot = True # bool
      self.active = False # bool
      self.pressed = False # bool
      self.pressCondition = None # -> bool

    def hook(self):
      dprint("pass")
      self.hookManager.HookMouse()
    def unhook(self):
      dprint("pass")
      self.hookManager.UnhookMouse()

    @memoizedproperty
    def hookManager(self): # -> HookManager instance
      dprint("creating pyhook manager")
      import pyHook
      ret = pyHook.HookManager()
      #ret.MouseRightDown =
      #ret.MouseMiddleDown =
      ret.MouseLeftDown = self._onMousePress
      ret.MouseLeftUp = self._onMouseRelease
      ret.MouseMove = self._onMouseMove
      return ret

    def _pressWindow(self, hwnd, x, y):
      """
      @param  hwnd  long
      @param  x  int
      @param  y  int
      """
      #if self.singleShot:
      #  self.unhook()
      #  self.active = False
      self.q.mousePressed.emit(x, y, hwnd)

    def _releaseWindow(self, hwnd, x, y):
      """
      @param  hwnd  long
      @param  x  int
      @param  y  int
      """
      if self.singleShot:
        self.unhook()
        self.active = False
      self.q.mouseReleased.emit(x, y, hwnd)

    def _moveWindow(self, hwnd, x, y):
      """
      @param  hwnd  long
      @param  x  int
      @param  y  int
      """
      self.q.mouseMoved.emit(x, y, hwnd)

    def _onMousePress(self, event):
      """
      @param  event  pyHook.HookManager.MouseEvent
      @return  bool  Whether pass the event to other handlers
      """
      if self.active and not self.pressed and (not self.pressCondition or self.pressCondition()):
        dprint("enter")
        self.pressed = True
        #print "---"
        #print "  message name:", event.MessageName
        #print "  message (MSG):", event.Message
        #print "  event time:", event.Time
        #print "  window (HWND):", event.Window
        #print "  window title:", event.WindowName
        #print "  position:", event.Position
        #print "  wheel:", event.Wheel
        #print "  injected:", event.Injected
        #print "---"

        hwnd = event.Window
        #title = u(event.WindowName)
        self._pressWindow(hwnd, *event.Position)
        dprint("leave: active")
        return False # eat the event
      #dprint("leave: not active")
      return True # return True to pass the event to other handlers

    def _onMouseRelease(self, event):
      """
      @param  event  pyHook.HookManager.MouseEvent
      @return  bool  Whether pass the event to other handlers
      """
      if self.active and self.pressed:
        dprint("enter")
        self.pressed = False
        hwnd = event.Window
        #title = u(event.WindowName)
        self._releaseWindow(hwnd, *event.Position)
        dprint("leave: active")
        return False # eat the event
      #dprint("leave: not active")
      return True # return True to pass the event to other handlers

    def _onMouseMove(self, event):
      """
      @param  event  pyHook.HookManager.MouseEvent
      @return  bool  Whether pass the event to other handlers
      """
      #dprint("enter")
      if self.active and self.pressed:
        hwnd = event.Window
        #title = u(event.WindowName)
        self._moveWindow(hwnd, *event.Position)
        #dprint("leave: active")
        #return False # Always bypass the event
      #dprint("leave: not active")
      return True # return True to pass the event to other handlers

  class ScreenSelector(QObject):
    def __init__(self, parent=None):
      super(ScreenSelector, self).__init__(parent)
      self.__d = _ScreenSelector(self)

    mousePressed = Signal(int, int, long) # x, y, hwnd
    mouseReleased = Signal(int, int, long) # x, y, hwnd
    mouseMoved = Signal(int, int, long) # x, y, hwnd

    def isSingleShot(self): return self.__d.singleShot
    def setSingleShot(self, t): self.__d.singleShot = t

    def isActive(self): return self.__d.active
    def start(self):
      d = self.__d
      if not d.active:
        d.active = True
        d.hook()
    def stop(self):
      d = self.__d
      if d.active:
        d.active = False
        d.unhook()

    def isPressed(self): return self.__d.pressed

    def pressCondition(self): return self.__d.pressCondition
    def setPressCondition(self, callback): # None or -> bool
      self.__d.pressCondition = callback

else: # dummy

  class ScreenSelector(QObject):

    mousePressed = Signal(int, int, long) # x, y, hwnd
    mouseReleased = Signal(int, int, long) # x, y, hwnd
    mouseMoved = Signal(int, int, long) # x, y, hwnd

    def isSingleShot(self): return False
    def setSingleShot(self, t): pass

    def isActive(self): return False
    def start(self): pass
    def stop(self): pass

    def isPressed(self): return False

    def pressCondition(self): return None
    def setPressCondition(self, v): pass

# Debug entry
if __name__ == '__main__':
  # Start event loop and block the main thread
  import sys
  import pythoncom

  w = ScreenSelector()

  from sakurakit import skwin
  w.setPressCondition(skwin.is_key_shift_pressed)

  w.mouseReleased.connect(lambda: sys.exit(0))
  w.start()
  pythoncom.PumpMessages() # wait forever

# EOF
