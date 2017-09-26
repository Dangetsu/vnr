# coding: utf8
# qimp.py
# 11/2/2013 jichi
# Qt image processing utilities

from PySide.QtGui import QColor, QPixmap, QPainter, QLinearGradient

# TODO: pass gradient as parameter
#@memoized
def getgradient(*args):
  ret = QLinearGradient(*args)
  ret.setColorAt(0, QColor(0,0,0))
  ret.setColorAt(.5, QColor(255,255,255))
  #ret.setColorAt(1, QColor(255,255,255))
  return ret

def gradientpixmap(pm):
  """
  @param  pm  QPixmap
  @return  QPixmap
  """
  # http://www.qtcentre.org/threads/4246-QGraphicsPixmapItem-modifying-the-alpha-channel-of-a-QPixmap
  # http://www.qtcentre.org/threads/37866-QPainter-fill-rect-with-gradient
  if not pm.isNull():
    w = pm.width()
    h = pm.height()
    if w and h:
      gr = getgradient(0, 0, w, h)
      #gr = QLinearGradient(alpha.rect().topLeft(), alpha.rect().bottomRight())
      alpha = QPixmap(w, h)
      p = QPainter(alpha)
      p.fillRect(alpha.rect(), gr)
      p.end()
      pm.setAlphaChannel(alpha)

# EOF
