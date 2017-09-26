# coding: utf8
# skrubberband.py
# 3/28/2014 jichi

import skos
from PySide.QtCore import Qt, Signal
from PySide.QtGui import QColor
from Qt5.QtWidgets import QApplication, QRubberBand, QGraphicsColorizeEffect

class SkColorizedRubberBand(QRubberBand):
  def __init__(self,shape, parent=None, color=None, strength=1):
    super(SkColorizedRubberBand, self).__init__(shape, parent)
    self.__color = None # QColor
    self.__strength = strength
    if color:
      self.setColor(color)

  def strength(self): return self.__strength
  def setStrength(self, v): self.__strength = v # effect not changed

  colorChanged = Signal(QColor)
  def color(self): return self.__color # QColor
  def setColor(self, color):
    if not color:
      color = QColor()
    elif not isinstance(color, QColor):
      color = QColor(color)
    if self.__color != color:
      self.__color = color

      effect = None
      if color.isValid():
        effect = self.graphicsEffect()
        if not effect or not isinstance(effect, QGraphicsColorizeEffect):
          if effect and effect.parent() == self:
            effect.setParent(None)
          effect = QGraphicsColorizeEffect(self)
          effect.setColor(color)
          effect.setStrength(self.strength())
      self.setGraphicsEffect(effect);
      self.colorChanged.emit(color)

  #if not skos.WIN:
  #  def paintEvent(self, e):
  #    """@reimp
  #    @param  e  QPaintEvent
  #    """
  #    c = self.color()
  #    if c.isValid():
  #      width = 2
  #      alpha = 32
  #      pen = QPen(c, width)
  #      pen.setStyle(Qt.SolidLine)
  #      painter = QPainter(0
  #      painter.begin(self)
  #      painter.setPen(pen)
  #      if self.shape() == QRubberBand.Rectangle:
  #        c.setAlpha(alpha)
  #        brush = QBrush(c)
  #        brush.setStyle(Qt.Dense1Pattern)
  #        painter.setBrush(brush)
  #      painter.drawRect(e.rect())
  #      painter.end()
  #    else:
  #      super(SkColorizedRubberBand, self).paintEvent(e)

#class SkMouseRubberBand(SkColorizedRubberBand):
class SkMouseRubberBand(QRubberBand):

  def __init__(self, *args, **kwargs):
    super(SkMouseRubberBand, self).__init__(*args, **kwargs)
    self.__pressedPos = None # None or (int x, int y)

  selected = Signal(int, int, int, int) # x, y, width, height

  def isPressed(self): return bool(self.__pressedPos)

  def isEmpty(self): return self.size().isEmpty()

  def press(self, x, y):
    self.setGeometry(x, y, 0, 0)
    self.__pressedPos = x, y
    QApplication.setOverrideCursor(Qt.CrossCursor)
    self.show();

  def move(self, x, y):
    if self.isPressed():
      _x, _y = self.__pressedPos
      x1 = min(x, _x)
      x2 = max(x, _x)
      y1 = min(y, _y)
      y2 = max(y, _y)
      self.setGeometry(x1, y1, x2 - x1, y2 - y1)

  def release(self):
    self.cancel()
    r = self.geometry() # QRect
    if not r.isEmpty():
      self.selected.emit(r.x(), r.y(), r.width(), r.height())

  def cancel(self):
    self.hide()
    if QApplication.overrideCursor():
      QApplication.restoreOverrideCursor()
    self.__pressedPos = None

  #void pressGlobal(const QPoint &globalPos) { press(mapFromGlobal(globalPos) - mapFromGlobal(QPoint())); }
  #void dragGlobal(const QPoint &globalPos) { drag(mapFromGlobal(globalPos) - mapFromGlobal(QPoint())); }

# EOF
