# coding: utf8
# gesturefilter.py
# 4/5/2012 jichi
# See: http://doc.qt.nokia.com/qq/qq18-mousegestures.html

__all__ = 'MouseGestureFilter',

from math import fabs
from itertools import izip
from PySide.QtCore import Qt, QObject, QEvent
from sakurakit.skdebug import dprint

from gesture import MouseGesture

class MouseGestureFilter(QObject): # QObject is needed for the eventFilter

  def __init__(self, parent=None, buttons=Qt.RightButton, modifiers=Qt.NoModifier):
    super(MouseGestureFilter, self).__init__(parent)
    self.__d = _MouseGestureFilter(buttons=buttons, modifiers=modifiers)

  def isActive(self): return self.__d.active

  def add(self, gesture):
    """
    @param  gesture.MouseGesture
    """
    self.__d.gestures.append(gesture)

  def clear(self): # also delete the gesetures owned by the object
    d = self.__d
    if d.gestures:
      d.abortGesture()
      for it in d.gestures:
        if d.parent() is self:
          d.setParent(None)
      d.gestures = []
      d.active = False

  # Protected:

  def eventFilter(self, obj, ev): # override  QObject, QEvent -> bool
    t = ev.type()
    if t == QEvent.MouseButtonPress:
      ret = self.mousePressEventFilter(ev)
    elif t == QEvent.MouseButtonRelease:
      ret = self.mouseReleaseEventFilter(ev)
    elif t == QEvent.MouseMove:
      ret = self.mouseMoveEventFilter(ev)
    elif t == QEvent.ContextMenu:
      d = self.__d
      ret = d.cancelContextMenu and bool(d.buttons & Qt.RightButton)
      d.cancelContextMenu = False
      dprint("contextMenu: ret = %s" % ret)
    else:
      ret = False
    return ret or super(MouseGestureFilter, self).eventFilter(obj, ev)

  def mousePressEventFilter(self, ev): # QMouseEvent -> bool
    d = self.__d
    if (ev.button() & d.buttons) and ev.modifiers() == d.modifiers:
      d.beginGesture((ev.x(), ev.y()))
      d.active = True
    else:
      return False

  def mouseReleaseEventFilter(self, ev): # QMouseEvent -> bool
    d = self.__d
    if d.active and (ev.button() & d.buttons) and ev.modifiers() == d.modifiers:
      d.cancelContextMenu = d.endGesture((ev.x(), ev.y())) # cancel context menu if triggered
      d.active = False
      return True
    else:
      return False

  def mouseMoveEventFilter(self, ev): # QMouseEvent -> bool
    d = self.__d
    if d.active:
      d.addPoint((ev.x(), ev.y()))
      return True
    else:
      return False

  #def bool contextMenuEventFilter(self, ev): # QContextMenuEvent -> bool
  #  return True

class _MouseGestureFilter:
  MIN_MOVE2 = 5     # int
  MIN_MATCH = 0.9   # qreal

  def __init__(self, buttons, modifiers):
    self.gestures = [] # QList<MouseGesture *> gestures_
    self.buttons = buttons # Qt::MouseButtons buttons_
    self.modifiers = modifiers # Qt::KeyboardModifiers modifiers_
    self.active = False # bool
    self.cancelContextMenu = False # bool

    self._positions = [] # [int x, int y]

  def abortGesture(self):
    if self._positions:
      self._positions = []

  def beginGesture(self, pos):
    """
    @param  (int x, int y)
    """
    self._positions.append(pos)

  def endGesture(self, pos):
    """
    @param  (int x, int y)
    """
    triggered = False
    if self._positions and  pos != self._positions[-1]:
      self._positions.append(pos)
    if len(self._positions) > 1: # at least two positions to make a gesture
      triggered = self.triggerGesture()
    else:
      triggered = False
    self._positions = []
    return triggered;

  def addPoint(self, pos):
    """
    @param  (int x, int y)
    """
    if not self._positions:
      self.beginGesture(pos)
    dx, dy = _subtract(pos, self._positions[-1]) # QPoint
    if dx*dx + dy*dy >= self.MIN_MOVE2:
      self._positions.append(pos)

  # Complicated implementation of trigger gesture

  def triggerGesture(self):
    directions = self._joinDirections(self._toDirections(self._positions))
    minLength = self._directionLength(directions) * self.MIN_MATCH

    while directions and self._directionLength(directions) > minLength:
      for g in self.gestures:
        if len(directions) == len(g.directions):
          match = True
          for gi, (px,py) in izip(g.directions, directions):
            if gi == MouseGesture.Up:
              if py >= 0: match = False
            elif gi == MouseGesture.Down:
              if py <= 0: match = False
            elif gi == MouseGesture.Left:
              if px >= 0: match = False
            elif gi == MouseGesture.Right:
              if px <= 0: match = False
            elif gi == MouseGesture.Horizontal:
              if px == 0: match = False
            elif gi == MouseGesture.Vertical:
              if py == 0: match = False
            #elif gi == MouseGesture.NoMatch:
            else: match = False
            if not match:
              break

          if match:
            g.trigger()
            dprint("exit: ret = true, matched")
            return True

      self._removeShortest(directions)
      directions = self._joinDirections(directions)

    for g in self.gestures:
      if len(g.directions) == 1 and g.directions[0] == MouseGesture.NoMatch:
        g.trigger()
        dprint("exit: ret = true, NoMatch")
        return False # triggered, but not matched
    dprint("exit: ret = false")
    return False

  @staticmethod
  def _toDirections(positions):
    """
    @param  positions  [int x, int y]
    @return  [int dx, int dy]

    Limits the directions of a list to up, down, left or right.
    Notice! This function converts the list to a set of relative moves instead of a set of screen coordinates.
    """
    ret = []
    last = lastY = 0
    for i,(x,y) in enumerate(positions):
      if i: # skip the first one
        dx, dy = x - lastX, y - lastY
        if fabs(dx) > fabs(dy):
          dy = 0
        else:
          dx = 0
        ret.append((dx, dy))
      lastX, lastY = x, y
    return ret

  @staticmethod
  def _joinDirections(positions):
    """
    @param  positions  [int x, int y]
    @return  [int dx, int dy]

    Joins together contignous movements in the same direction.
    Notice! This function expects a list of limited directions.
    """
    ret = []
    lastX = lastY = 0
    for i, pos in enumerate(positions):
      if not i: # the first one
        lastX, lastY = pos
      else:
        joined = False
        if lastX > 0 and pos[0] > 0 or lastX < 0 and pos[0] < 0:
          lastX += pos[0]
          joined = True
        if lastY > 0 and pos[1] > 0 or lastY < 0 and pos[1] < 0:
          lastY += pos[1]
          joined = True

        if not joined:
          ret.append((lastX, lastY))
          lastX, lastY = pos

    if lastX or lastY:
      ret.append((lastX, lastY));
    return ret;

  @staticmethod
  def _removeShortest(positions):
    """
    @param  positions  [int x, int y]

    Removes the shortest segment from a list of movements.
    If there are several equally short segments, the first one is removed.
    """
    import sys
    shortestLength = sys.maxint
    shortest = -1
    for i,(x,y) in enumerate(positions):
      length = x*x + y*y
      if length < shortestLength:
        shortestLength = length
        shortest = i

    if shortest != -1:
      del positions[shortest]

  @staticmethod
  def _directionLength(positions):
    """
    @param  positions  [int x, int y]
    @return  int

    Calculates the total length of the movements from a list of relative movements.
    """
    return sum(fabs(x)+fabs(y) for x,y in positions) # pos.manhattanLength()


# Helpers

def _subtract((x1,y1), (x2,y2)):
  """
  A replacement of numpy.subtract
  See: http://stackoverflow.com/questions/17418108/elegant-way-to-perform-tuple-arithmetic
  """
  return x1 - x2, y1 - y2

# EOF
