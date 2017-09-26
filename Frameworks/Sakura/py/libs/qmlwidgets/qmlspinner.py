# coding: utf8
# qmlspinner.py
# 2/10/2013 jichi
# See: http://qt-project.org/wiki/Busy-Indicator-for-QML

__all__ = 'QmlGradientSpinner',

if __name__ == '__main__':
  import sys
  sys.path.append('..')

from PySide.QtCore import Property, Signal, Qt, QPointF
from PySide.QtGui import QColor, QPixmap, QPixmapCache, QPainter, QPainterPath, QConicalGradient
from Qt5.QtQuick1 import QDeclarativeItem
from Qt5.QtWidgets import QGraphicsItem
from sakurakit.skclass import Q_Q

## Components ##

@Q_Q
class _QmlGradientSpinner(object):
  def __init__(self):
    self.innerRadius = 0.8
    self.outerRadius = 1.0
    self.actualInnerRadius = 90.0
    self.actualOuterRadius = 100.0
    self.backgroundColor = QColor(177, 210, 143, 70)
    self.foregroundColor = QColor(119, 183, 83, 255)
    self.invalidateHash()

  def invalidateHash(self): self._hash = None

  @property
  def hash(self):
    """
    @return str
    """
    if not self._hash:
      self._hash = "QmlGradientSpinner-%s-%s-%s-%s-%s-%s" % (
        self.innerRadius, self.outerRadius,
        self.actualInnerRadius, self.actualOuterRadius,
        self.foregroundColor, self.backgroundColor,
      )
    return self._hash

  def updateRadius(self):
    q = self.q
    sz = min(q.width(), q.height())
    coef = 0.5 * sz
    self.actualInnerRadius = coef * self.innerRadius
    self.actualOuterRadius = coef * self.outerRadius
    self.invalidateHash()
    q.actualInnerRadiusChanged.emit(self.actualInnerRadius)
    q.actualOuterRadiusChanged.emit(self.actualOuterRadius)

# http://qt-project.org/wiki/Busy-Indicator-for-QML
#@QmlItem
class QmlGradientSpinner(QDeclarativeItem):

  def __init__(self, parent=None):
    super(QmlGradientSpinner, self).__init__(parent)
    self.__d = _QmlGradientSpinner(self)
    self.widthChanged.connect(self.__d.updateRadius)
    self.heightChanged.connect(self.__d.updateRadius)
    self.innerRadiusChanged.connect(self.__d.updateRadius)
    self.outerRadiusChanged.connect(self.__d.updateRadius)
    self.backgroundColorChanged.connect(self.__d.invalidateHash)
    self.foregroundColorChanged.connect(self.__d.invalidateHash)

    self.setFlag(QGraphicsItem.ItemHasNoContents, False) # enable paint function

  def setInnerRadius(self, value):
    self.__d.innerRadius = value
    self.innerRadiusChanged.emit(value)
  innerRadiusChanged = Signal(float)
  innerRadius = Property(float,
    lambda self: self.__d.innerRadius,
    setInnerRadius,
    notify=innerRadiusChanged)

  def setOuterRadius(self, value):
    self.__d.outerRadius = value
    self.outerRadiusChanged.emit(value)
  outerRadiusChanged = Signal(float)
  outerRadius = Property(float,
    lambda self: self.__d.outerRadius,
    setOuterRadius,
    notify=outerRadiusChanged)

  actualInnerRadiusChanged = Signal(float)
  actualInnerRadius = Property(float,
    lambda self: self.__d.actualInnerRadius,
    notify=actualInnerRadiusChanged)

  actualOuterRadiusChanged = Signal(float)
  actualOuterRadius = Property(float,
    lambda self: self.__d.actualOuterRadius,
    notify=actualOuterRadiusChanged)

  def setBackgroundColor(self, value):
    if value != self.backgroundColor:
      self.__d.backgroundColor = value
      self.backgroundColorChanged.emit(value)
  backgroundColorChanged = Signal(QColor)
  backgroundColor = Property(QColor,
    lambda self: self.__d.backgroundColor,
    setBackgroundColor,
    notify=backgroundColorChanged)

  def setForegroundColor(self, value):
    if value != self.foregroundColor:
      self.__d.foregroundColor = value
      self.foregroundColorChanged.emit(value)
  foregroundColorChanged = Signal(QColor)
  foregroundColor = Property(QColor,
    lambda self: self.__d.foregroundColor,
    setForegroundColor,
    notify=foregroundColorChanged)

  def paint(self, painter, option, widget=None):
    """@reimp @public
    virtual void paint(QPainter *painter, const QStyleOptionGraphicsItem *option, QWidget *widget = 0)
    """
    #Q_UNUSED(option)
    #Q_UNUSED(widget)
    d = self.__d
    key = d.hash
    pm = QPixmap()
    if not QPixmapCache.find(key, pm):
      # Set up a convenient path
      path = QPainterPath()
      path.setFillRule(Qt.OddEvenFill)
      path.addEllipse(QPointF(d.actualOuterRadius, d.actualOuterRadius), d.actualOuterRadius, d.actualOuterRadius)
      path.addEllipse(QPointF(d.actualOuterRadius, d.actualOuterRadius), d.actualInnerRadius, d.actualInnerRadius)

      nActualDiameter = 2.0 * d.actualOuterRadius
      pm = QPixmap(nActualDiameter, nActualDiameter)
      pm.fill(Qt.transparent)
      p = QPainter(pm)

      # Draw the ring background
      p.setPen(Qt.NoPen)
      p.setBrush(d.backgroundColor)
      p.setRenderHint(QPainter.Antialiasing)
      p.drawPath(path)

      # Draw the ring foreground
      # TODO: Expose this gradient as Qml Property
      gradient = QConicalGradient(d.actualOuterRadius, d.actualOuterRadius, 0.0)
      gradient.setColorAt(0.0, Qt.transparent)
      gradient.setColorAt(0.05, d.foregroundColor)
      gradient.setColorAt(0.8, Qt.transparent)

      p.setBrush(gradient)
      p.drawPath(path)
      p.end()

      QPixmapCache.insert(key, pm)

    # Draw pixmap at center of item
    w, h = self.width(), self.height()
    sz = min(w, h)
    painter.drawPixmap(0.5 * (w - sz), 0.5 * (h - sz), pm)

# EOF
