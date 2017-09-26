# coding: utf8
# textspy.py
# 6/30/2013 jichi

from PySide.QtCore import Signal, Slot, QObject, QTimer
from sakurakit import skwin
from sakurakit.skclass import Q_Q, memoized, memoizedproperty, hasmemoizedproperty
from sakurakit.skdebug import dprint
#from sakurakit.skqml import QmlObject
from mytr import my
import growl, procutil

def _textat(x, y):
  """
  @param  x  int
  @param  y  int
  @return  unicode or None
  """
  hwnd = skwin.get_window_at(x, y)
  if hwnd and not procutil.is_my_window(hwnd):
    # This might cause issue on Windows 10
    # http://sakuradite.com/topic/639
    from wintext import wintext
    return wintext.textat(x, y) or skwin.get_window_text(hwnd)

@Q_Q
class _TextSpy(object):
  def __init__(self):
    self.hoverEnabled = True
    self._lastPos = None # int, int
    self._lastPosFinished = False

  @memoizedproperty
  def hoverTimer(self):
    ret = QTimer(self.q)
    ret.setInterval(400)
    ret.setSingleShot(False)
    ret.timeout.connect(self._hover)
    return ret

  def _hover(self):
    pos = skwin.get_mouse_pos()
    if pos != self._lastPos:
      self._lastPos = pos
      self._lastPosFinished = False
      return
    if self._lastPosFinished:
      return
    self._lastPosFinished = True
    t = _textat(*pos)
    if t:
      t = t.strip()
      if t:
        self.q.textReceived.emit(t)

class TextSpy(QObject):
  def __init__(self, parent=None):
    super(TextSpy, self).__init__(parent)
    self.__d = _TextSpy(self)

  textReceived = Signal(unicode)

  def isHoverEnabled(self, val): return self.__d.hoverEnabled
  def setHoverEnabled(self, val): self.__d.hoverEnabled = val

  def start(self):
    d = self.__d
    if d.hoverEnabled and not d.hoverTimer.isActive():
      d.hoverTimer.start()
      growl.msg(my.tr("Start translating hovered text"))
    dprint("pass")

  def stop(self):
    d = self.__d
    if hasmemoizedproperty(d, 'hoverTimer') and  d.hoverTimer.isActive():
      d.hoverTimer.stop()
      growl.msg(my.tr("Stop translating hovered text"))
    dprint("pass")

@memoized
def manager(): return TextSpy()

#@QmlObject
class TextSpyProxy(QObject):
  def __init__(self, parent=None):
    super(TextSpyProxy, self).__init__(parent)

  @Slot()
  def start(self): manager().start()
  @Slot()
  def stop(self): manager().stop()

# EOF
