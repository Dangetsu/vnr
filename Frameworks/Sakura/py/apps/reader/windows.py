# coding: utf8
# windows.py
# 10/5/2012 jichi
__all__ = 'TopWindow', 'NormalWindow'

from itertools import imap
from PySide.QtCore import Qt, QCoreApplication, QTimer, Signal
from Qt5.QtWidgets import QWidget
from sakurakit.skclass import memoized
from sakurakit.skdebug import dprint
import config, rc, winutil

@memoized
def top(): return TopWindow()
@memoized
def normal(): return NormalWindow()

def raise_top_window(): top().bringWindowToTop()
def raise_normal_window(): normal().bringWindowToTop()

class _Window(QWidget):

  def __init__(self, parent=None, f=0):
    super(_Window, self).__init__(parent, f)
    self.__canClose = False
    self.setWindowIcon(rc.icon('logo-reader'))
    self.setWindowTitle(QCoreApplication.instance().applicationName())
    self.showNothing()

    self.setStyleSheet(''.join(imap(rc.qss, config.QT_STYLESHEETS)))

  closeRequested = Signal()

  def canClose(self): return self.__canClose
  def setCanClose(self, v): self.__canClose = v

  def showNothing(self):
    self.resize(0, 0)
    #self.setWindowOpacity(1.0)

  def showDot(self):
    """Show as a semi-transparent a visible dot in the center of the screen"""
    self.setWindowOpacity(0.01)
    self.resize(1, 1)

  ## Events ##

  def closeEvent(self, event):
    if self.canClose():
      dprint("pass: closing")
      super(_Window, self).closeEvent(event)
      dprint("pass: closed")
    else:
      event.ignore()
      self.closeRequested.emit()
      dprint("pass: ignored")

  ## Properties ##

  def bringWindowToTop(self):
    """Bring window on top of DirectX in full screen mode"""
    #if settings.global_().kagamiIgnoresFocus() and self.isVisible():
    if self.isVisible():
      winutil.raise_widget(self)

class NormalWindow(_Window):

  def __init__(self, parent=None):
    WINDOW_FLAGS = Qt.Window | Qt.CustomizeWindowHint #| Qt.WindowStaysOnTopHint
    super(NormalWindow, self).__init__(parent, WINDOW_FLAGS)

  ## Properties ##

  def staysOnTop(self): return self.__d.staysOnTop()
  def setStaysOnTop(self, value): self.__d.setStaysOnTop(value)

  def refreshInterval(self): return self.__d.staysOnTopTimer.interval()
  def setRefreshInterval(self, msec): self.__d.staysOnTopTimer.setInterval(msec)

# Invisible root widget for all widgets

class _TopWindow:
  def __init__(self, q):
    #self.alwaysStaysOnTop = False
    t = self.staysOnTopTimer = QTimer(q)
    t.setInterval(1000) # 1 second
    t.timeout.connect(q.bringWindowToTop)

  def staysOnTop(self): return self.staysOnTopTimer.isActive()

  def setStaysOnTop(self, value):
    if value != self.staysOnTop():
      dprint("staysOnTop = %s" % value)
      if value:
        self.staysOnTopTimer.start()
      else:
        self.staysOnTopTimer.stop()

class TopWindow(_Window):

  def __init__(self, parent=None):
    WINDOW_FLAGS = Qt.Window | Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint
    super(TopWindow, self).__init__(parent, WINDOW_FLAGS)
    self.__d = _TopWindow(self)

  ## Properties ##

  #def alwaysStaysOnTop(self): return self.__d.alwaysStaysOnTop
  #def setAlwaysStaysOnTop(self, t):
  #  self.alwaysStaysOnTop = t
  #  if t:
  #    self.setStaysOnTop(True)

  def staysOnTop(self): return self.__d.staysOnTop()
  def setStaysOnTop(self, t):
    #if not t and self.__d.alwaysStaysOnTop:
    #  return
    self.__d.setStaysOnTop(t)

  def refreshInterval(self): return self.__d.staysOnTopTimer.interval()
  def setRefreshInterval(self, msec): self.__d.staysOnTopTimer.setInterval(msec)

#class WindowHolder(QWidget):
#  def __init__(self, parent=None):
#    WINDOW_FLAGS = Qt.Dialog | Qt.WindowMinMaxButtonsHint
#    super(WindowHolder, self).__init__(parent, WINDOW_FLAGS)
#    self.setWindowTitle("VNR Window Holder")
#    #self.resize(1, 1)
#    self.move(-9999, -9999) # move out of screen

# EOF

      #if not ok:
      #  # http://www.shloemi.com/2012/09/solved-setforegroundwindow-win32-api-not-always-works/
      #  import ctypes
      #  that = skwin.get_window_thread_id(skwin.get_foreground_window())
      #  this = skwin.get_window_thread_id(hwnd)
      #  ctypes.windll.user32.AttachThreadInput(that, this, 1)
      #  skwin.set_foreground_window(hwnd)
      #  skwin.set_top_window(hwnd)
      #  skwin.set_foreground_window(hwnd)
      #  ctypes.windll.user32.AttachThreadInput(that, this, 0)

      #if not ok:
      #  # http://www.shloemi.com/2012/09/solved-setforegroundwindow-win32-api-not-always-works/
      #  import win32process
      #  that = skwin.get_window_thread_id(skwin.get_foreground_window())
      #  this = skwin.get_window_thread_id(hwnd)
      #  win32process.AttachThreadInput(that, this, True)
      #  ok = skwin.set_top_window(hwnd)
      #  win32process.AttachThreadInput(that, this, False)

      # http://stackoverflow.com/questions/3282328/updating-the-z-order-of-many-windows-using-win32-api
      #try:
      #  import gameman
      #  hwnd = gameman.manager().currentGame().wid
      #  if hwnd:
      #    import win32gui, win32con
      #    winId = skwin.hwnd_from_wid(self.winId())
      #    win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE);
      #    win32gui.SetWindowPos(winId, win32con.HWND_TOP, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE);
      #except Exception, e:
      #  print e

# TODO: create a widget with border and two push buttons
#
# FIXME: top-level border not working on Windows
# Either use QML for rendering or reimplement paintEvent
#class WindowTracker(QWidget):
#  def __init__(self, parent=None):
#    WINDOW_FLAGS = Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
#    super(WindowTracker, self).__init__(parent, WINDOW_FLAGS)
#    self.setAttribute(Qt.WA_TranslucentBackground);
#    self.setStyleSheet("""
#QWidget {
#  background-color: transparent
#  border-color: red
#  border-radius: 1px
#  border-width: 5px
#}
#""")
