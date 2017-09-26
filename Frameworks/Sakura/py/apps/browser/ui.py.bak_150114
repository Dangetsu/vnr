# coding: utf8
# ui.py
# 12/13/2012 jichi

from PySide.QtCore import Qt
from PySide.QtGui import QColor, QGraphicsDropShadowEffect
from sakurakit import skdwm, skwin, skos

#GLOW_COLOR = 'yellow'
GLOW_COLOR = '#ffffe0' # lightyellow

## Interface ##

def glassifyWidget(w):
  """
  @param  w  QWidget
  """
  if DWM_ENABLED:
    w.setAttribute(Qt.WA_TranslucentBackground)
    w.setAttribute(Qt.WA_NoSystemBackground)
    setWidgetDwmEnabled(w, True);

def glassifyWindow(hwnd):
  """
  @param  hwnd  HWND
  """
  if DWM_ENABLED:
    setWindowDwmEnabled(hwnd, True)

def glowEffect(parent=None, color=GLOW_COLOR, radius=16, offset=1):
  """
  @param* parent  QWidget
  @param* color  QColor or str or None
  @param* radius  int
  @param* offset  int
  @return  QGraphicsEffect
  """
  if skos.MAC: # graphics effect on mac is not observable
    return None
  #from pyeffects import GraphicsTextShadowEffect
  #ret = GraphicsTextShadowEffect(parent)
  ret = QGraphicsDropShadowEffect(parent)
  ret.setBlurRadius(radius)
  ret.setOffset(offset)
  if color:
    if not isinstance(color, QColor):
      color = QColor(color)
    ret.setColor(color)
  return ret

## Implementation ##

DWM_ENABLED = skos.WIN and skdwm.isCompositionEnabled() # bool

def setWidgetDwmEnabled(w, t=True):
  wid = w.winId()
  hwnd = skwin.hwnd_from_wid(wid)
  setWindowDwmEnabled(hwnd, t)

def setWindowDwmEnabled(hwnd, t=True):
  """
  @param  hwnd  HWND
  @param  t  bool
  """
  skdwm.enableBlurBehindWindow(hwnd, t)

  margins = (-1, -1, -1, -1) if t else (0, 0, 0, 0)
  skdwm.extendFrameIntoClientArea(hwnd, *margins)

# EOF
