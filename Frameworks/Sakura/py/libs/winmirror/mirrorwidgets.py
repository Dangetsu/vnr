# coding: utf8
# mirrorwidgets.py
# 5/11/2012 jichi
# Windows only
#
# This file is unfinished

__all__ = 'MirroredWindow',

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import win32api, win32con, win32gui, ctypes
from functools import partial
from sakurakit import skwin, skwinapi, qtwin
from sakurakit.skclass import Q_Q, memoizedproperty
from sakurakit.skdebug import dwarn
from PySide.QtCore import Qt, QTimer
from PySide.QtGui import QPainter, QPixmap
from Qt5.QtWidgets import QWidget

WINDOW_TITLEBAR_HEIGHT = 24

@Q_Q
class _MirroredWindow:
  def __init__(self):
    self.wid = 0

  @memoizedproperty
  def repaintTimer(self):
    q = self.q
    ret = QTimer(q)
    ret.setInterval(200)
    ret.timeout.connect(q.repaint)
    return ret

  @memoizedproperty
  def resizeTimer(self):
    ret = QTimer(self.q)
    ret.setSingleShot(True)
    ret.setInterval(200)
    ret.timeout.connect(self.updateSize)
    return ret

  def updateSize(self):
    hwnd = self.wid
    if not hwnd:
      return
    q = self.q
    if q.isMaximized() or q.isFullScreen():
      return

    w0, h0 = skwin.get_window_size(hwnd)
    h0 -= WINDOW_TITLEBAR_HEIGHT
    if w0 <= 0 or h0 <= 0:
      return
    ratio = w0/float(h0)

    sz = q.size()
    w, h = sz.width(), sz.height()

    ww = int(h * ratio)
    EPS = 2
    if w > ww + EPS:
      q.resize(ww, h)
    elif w < ww - EPS:
      q.resize(w, w/ratio)

class MirroredWindow(QWidget):
  def __init__(self, parent=None, f=0):
    """
    @param  parent  QWidget
    @param  f  Qt.WindowFlags
    """
    #if not f:
    #  f = Qt.SplashScreen | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
    super(MirroredWindow, self).__init__(parent, f)
    self.__d = _MirroredWindow(self)
    #self.setStyleSheet("QWidget{background-color:black}")
    #self.setMouseTracking(True)

    #self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint|Qt.Dialog)
    #self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint|Qt.Dialog)
    #self.setStyleSheet("background: transparent; border: none")
    #self.setAttribute(Qt.WA_TranslucentBackground)
    #self.setAttribute(Qt.WA_TransparentForMouseEvents)
    #self.setEnabled(False)
    hwnd = skwin.hwnd_from_wid(self.winId())
    styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, styles | win32con.WS_EX_TRANSPARENT)

  ## Properties ##
  def mirroredWinId(self): return self.__d.wid
  def setMirroredWinId(self, v): self.__d.wid = v

  #def winEvent(self, message, result):
  #  """@reimp
  #  """
  #  if 'HitTestCode' in message.__str__():
  #    #HTNOWHERE
  #    return True
  #  return super(MirroredWindow, self).winEvent(message, result)

  # TODO: Update QIcon from HICON got from GetWindowLong
  # http://stackoverflow.com/questions/15306866/hicon-hbitmap-to-qicon-qpixmap-qimage-anything-with-a-q-in-it

  def start(self): self.__d.repaintTimer.start(); self.repaint()
  def stop(self): self.__d.repaintTimer.stop()

  ## Events ##

  def setVisible(self, v):
    """@reimp
    @param  v  bool
    """
    if v:
      self.__d.updateSize()
    super(MirroredWindow, self).setVisible(v)

  #def mouseDoubleClickEvent(self, event):
  #def mouseMoveEvent(self, event):
  #def moveEvent(self,  event):
  #def mouseReleaseEvent(seslf, event):

  #def keyPressEvent(self, event):
  #  """@reimp
  #  @param  event  QKeyEvent
  #  """
  #  hwnd = self.__d.wid
  #  if not hwnd:
  #    return
  #  win32gui.SetForegroundWindow(hwnd)

  def keyPressEvent(self, event):
    hwnd = self.__d.wid
    if not hwnd:
      return
    win32gui.SetForegroundWindow(hwnd)

    vk = qtwin.vkey_from_qkey(event.key())
    if not vk:
      return
    #skwin.post_key(hwnd, vk)

    inp = skwinapi.INPUT(
      type = win32con.INPUT_MOUSE,
      ki = skwinapi.KEYBDINPUT(
        wVk = vk,
      ),
    )
    sz = ctypes.sizeof(inp)
    skwinapi.SendInput(1, inp, sz)
    #inp.ki.dwFlags = win32con.KEYEVENTF_KEYUP
    #skwinapi.SendInput(1, inp, sz)


    #QTimer.singleShot(500, partial(f, vk))

    # http://stackoverflow.com/questions/1823762/sendkeys-for-python-3-1-on-windows
    #win32gui.SetFocus((hwnd)
    #def f(vk):
    #  inp = skwinapi.INPUT(
    #    type = win32con.INPUT_MOUSE,
    #    ki = skwinapi.KEYBDINPUT(
    #      wVk = vk,
    #    ),
    #  )
    #  sz = ctypes.sizeof(inp)
    #  skwinapi.SendInput(1, inp, sz)
    #  inp = skwinapi.INPUT(
    #    type = win32con.INPUT_MOUSE,
    #    ki = skwinapi.KEYBDINPUT(
    #      wVk = win32con.KEYEVENTF_KEYUP,
    #    ),
    #  )
    #  sz = ctypes.sizeof(inp)
    #  skwinapi.SendInput(1, inp, sz)


    #QTimer.singleShot(500, partial(f, vk))

    #if f:
    #  QTimer.singleShot(500,
    #      partial(win32gui.SetFocus, f))

  def mouseMoveEvent_disabled(self, event):
    """@reimp
    @param  event  QMouseEvent
    """
    hwnd = self.__d.wid
    if not hwnd:
      return

    left, top, right, bottom = skwin.get_window_rect(hwnd)
    w0, h0 = right - left, bottom - top - WINDOW_TITLEBAR_HEIGHT
    if w0 <= 0 or h0 <= 0:
      return
    sz = self.size()
    w, h = sz.width(), sz.height()
    if w <= 0 or h <= 0:
      return

    x, y = event.x(), event.y()

    x0 = left + w0 * x / w
    y0 = top + WINDOW_TITLEBAR_HEIGHT + h0 * y / h
    print x0, y0

    # http://stackoverflow.com/questions/2086017/how-to-simulate-mousemove-event-from-one-window-to-another
    #pos = event.globalPos()
    #skwin.post_mouse_move(x0 - pos.x(), y0 - pos.y())
    #skwin.post_mouse_click()
    #skwin.post_mouse_move(pos.x() - x0, pos.y() - y0)
    #import functools
    #QTimer.singleShot(0, functools.partial(skwin.post_mouse_move,
    #  - x0 + pos.x(), - y0 + pos.y(), relative=True))
    #skwin.post_mouse_move(event.x(), event.y())

    #win32api.SendMessage(hwnd, win32con.WM_NCHITTEST, 0, win32api.MAKELONG(x0, y0))
    #win32api.SendMessage(hwnd, win32con.WM_SETCURSOR, hwnd, win32api.MAKELONG(win32con.HTCLIENT, win32con.WM_MOUSEMOVE))
    #dw = win32api.MAKELONG(x0 - left, y0 - top)
    dw = win32api.MAKELONG(x0 - left, y0 - top)
    win32gui.SetCapture(hwnd)
    win32api.SendMessage(hwnd, win32con.WM_NCHITTEST, 0, dw)
    #win32api.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, dw)
    #win32api.SendMessage(hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, dw)
    #win32api.SendMessage(hwnd, win32con.WM_NCHITTEST, 0, dw)
    #win32gui.ReleaseCapture()

  def mouseReleaseEvent(self, event):
    """@reimp
    @param  event  QMouseEvent
    """
    hwnd = self.__d.wid
    if not hwnd:
      return

    left, top, right, bottom = skwin.get_window_rect(hwnd)
    w0, h0 = right - left, bottom - top - WINDOW_TITLEBAR_HEIGHT
    if w0 <= 0 or h0 <= 0:
      return
    sz = self.size()
    w, h = sz.width(), sz.height()
    if w <= 0 or h <= 0:
      return

    x, y = event.x(), event.y()

    x0 = left + w0 * x / w
    y0 = top + WINDOW_TITLEBAR_HEIGHT + h0 * y / h
    print x0, y0

    # http://stackoverflow.com/questions/2086017/how-to-simulate-mousemove-event-from-one-window-to-another
    import win32api, win32con, win32gui
    #pos = event.globalPos()
    #skwin.post_mouse_move(x0 - pos.x(), y0 - pos.y())
    #skwin.post_mouse_click()
    #skwin.post_mouse_move(pos.x() - x0, pos.y() - y0)
    #import functools
    #QTimer.singleShot(0, functools.partial(skwin.post_mouse_move,
    #  - x0 + pos.x(), - y0 + pos.y(), relative=True))
    #skwin.post_mouse_move(event.x(), event.y())

    #win32api.SendMessage(hwnd, win32con.WM_NCHITTEST, 0, win32api.MAKELONG(x0, y0))
    #win32api.SendMessage(hwnd, win32con.WM_SETCURSOR, hwnd, win32api.MAKELONG(win32con.HTCLIENT, win32con.WM_MOUSEMOVE))
    #dw = win32api.MAKELONG(x0 - left, y0 - top)
    #pos = event.globalPos()
    gp = x0, y0
    #hwnd = win32gui.WindowFromPoint(gp)
    #hwnd = win32gui.ChildWindowFromPoint(hwnd, gp)
    #hwnd = skwin.get_window_parent(hwnd)
    #print hwnd
    if hwnd:
      print hwnd
      dw = win32api.MAKELONG(*gp)
      #win32gui.SetCapture(hwnd)
      #win32api.SendMessage(hwnd, win32con.WM_NCHITTEST, 0, dw)
      win32api.PostMessage(hwnd, win32con.WM_MOUSEMOVE, 0, dw)
      win32api.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, 0, dw)
      win32api.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, dw)
      #win32api.SendMessage(hwnd, win32con.WM_NCHITTEST, 0, dw)
      #win32gui.ReleaseCapture()
    #import ctypes
    #from sakurakit import skwinapi
    #inp = skwinapi.INPUT(
    #  type = win32con.INPUT_MOUSE,
    #  mi = skwinapi.MOUSEINPUT(
    #    dx = x0,
    #    dy = y0,
    #    dwFlags = win32con.MOUSEEVENTF_ABSOLUTE | win32con.MOUSEEVENTF_MOVE,
    #  ),
    #)
    #sz = ctypes.sizeof(inp)
    #skwinapi.SendInput(1, inp, sz)

    #pos = event.globalPos()
    #inp = skwinapi.INPUT(
    #  type = win32con.INPUT_MOUSE,
    #  mi = skwinapi.MOUSEINPUT(
    #    dx = pos.x(),
    #    dy = pos.y(),
    #    dwFlags = win32con.MOUSEEVENTF_ABSOLUTE | win32con.MOUSEEVENTF_MOVE,
    #  ),
    #)
    #skwinapi.SendInput(1, inp, sz)

  # http://stackoverflow.com/questions/7259847/forcing-an-aspect-ratio-when-resizing-a-main-window
  def resizeEvent(self, event) :
    """@reimp
    @param  event  QResizeEvent
    """
    self.__d.resizeTimer.start()

  def paintEvent(self, event):
    """@reimp
    @param  event  QPaintEvent
    """
    hwnd = self.__d.wid
    if not hwnd:
      return

    wid = skwin.wid_from_hwnd(hwnd)
    pm = QPixmap.grabWindow(wid)
    if pm.isNull():
      return

    sz = self.size()
    if sz != pm.size():
      pm = pm.scaled(sz, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    painter = QPainter(self)
    painter.drawPixmap(0, 0, pm)

if __name__ == "__main__":
  from PySide.QtGui import *
  a = QApplication(sys.argv)
  w = MirroredWindow()
  w.show()
  a.exec_()

# EOF
