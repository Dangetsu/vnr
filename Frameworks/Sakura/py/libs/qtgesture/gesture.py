# coding: utf8
# gesture.py
# 4/5/2012 jichi
# See: http://doc.qt.nokia.com/qq/qq18-mousegestures.html

__all__ = 'MouseGesture',

from PySide.QtCore import Qt, QObject, Signal

class MouseGesture(QObject): # QObject is needed for the triggered signal

  #  A Direction can be any of the following:
  #    Up
  #    Down
  #    Left
  #    Right
  #    AnyHorizontal (Left or Right)
  #    AnyVertical (Up or Down)
  #
  #  In addition to these, the NoMatch enum is
  #  available. A gesture holding only the NoMatch
  #  enum is gestured when no other gesture can be
  #enum Direction {
  NoMatch = 0
  Up = 1
  Down = 2
  Left = 3
  Right = 4
  Horizontal = 5
  Vertical = 6

  def __init__(self, directions=[], parent=None):
    super(MouseGesture, self).__init__(parent)
    self.directions = directions # [Direction]

  triggered = Signal()

  def trigger(self):
    self.triggered.emit()
    #DOUT("enter: directions =" << directionsToString(directions_));
    #QString m = tr("mouse gesture") + ": " + directionsToString(directions_);
    #if (!description_.isEmpty())
    #  m.append( "  | " + description_);
    #emit message(m);

# EOF
