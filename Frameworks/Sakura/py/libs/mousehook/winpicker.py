# coding: utf8
# winpicker.py
# 10/6/2012 jichi
# Windows only
# See: http://sourceforge.net/apps/mediawiki/pyhook/index.php?title=PyHook_Tutorial

# On mouse click warning:
# See: http://sourceforge.net/tracker/?func=detail&aid=2986042&group_id=235202&atid=1096323
# func = self.keyboard_funcs.get(msg)
# => func = self.keyboard_funcs.get( int(str(msg)) )

__all__ = 'WindowPicker',

if __name__ == '__main__':
  import sys
  sys.path.append('..')

from PySide.QtCore import QObject, Signal
from sakurakit import skos
from sakurakit.skclass import Q_Q, memoizedproperty
from sakurakit.skdebug import dprint
from sakurakit.skunicode import u

if skos.WIN:

  @Q_Q
  class _WindowPicker(object):

    def __init__(self):
      self.singleShot = True # bool
      self.active = False # bool

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
      ret.MouseLeftDown = \
      ret.MouseRightDown = \
      ret.MouseMiddleDown = \
        self._onMousePress
      return ret

    def _clickWindow(self, hwnd, title):
      if self.active:
        if self.singleShot:
          self.unhook()
          self.active = False
        self.q.windowClicked.emit(hwnd, title)

    def _onMousePress(self, event):
      """
      @param  event  pyHook.HookManager.MouseEvent
      @return  bool  Whether pass the event to other handlers
      """
      dprint("enter")
      if self.active:
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
        title = u(event.WindowName)
        if hwnd:
          dprint("found hwnd")
          self._clickWindow(hwnd, title)
          dprint("leave: active")
          return False # eat the event
      dprint("leave: not active")
      return True # return True to pass the event to other handlers

  class WindowPicker(QObject):
    def __init__(self, parent=None):
      super(WindowPicker, self).__init__(parent)
      self.__d = _WindowPicker(self)

    windowClicked = Signal(long, unicode)

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

else: # dummy

  class WindowPicker(QObject):

    windowClicked = Signal(long, unicode) # hwnd, title

    def isSingleShot(self): return False
    def setSingleShot(self, t): pass

    def isActive(self): return False
    def start(self): pass
    def stop(self): pass

# Debug entry
if __name__ == '__main__':
  # Start event loop and block the main thread
  import sys
  import pythoncom

  w = WindowPicker()
  w.windowClicked.connect(lambda: sys.exit(0))
  w.start()
  pythoncom.PumpMessages() # wait forever

# EOF
