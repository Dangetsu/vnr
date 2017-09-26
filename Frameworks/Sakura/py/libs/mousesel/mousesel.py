# coding: utf8
# mousesel.py
# 8/21/2014 jichi
# Windows only

__all__ = 'MouseSelector',

#from sakurakit.skclass import memoized

from sakurakit import skos
if skos.WIN:
  from pymousesel import MouseSelector

else:
  from PySide.QtCore import Signal, QObject

  class MouseSelector(QObject): # dummy
    def __init__(self, parent=None):
      super(MouseSelector, self).__init__(parent)

    selected = Signal(int, int, int, int) # x, y, width, height
    pressed = Signal(int, int) # x, y
    released = Signal(int, int) # x, y

    def isEnabled(self): return False
    def setEnabled(self, t): pass

    def comboKey(self): return 0
    def setComboKey(self, v): pass

    def parentWidget(self): pass
    def setParentWidget(self, v): pass

    def refreshInterval(self): return 0
    def setRefreshInterval(self, v): pass

    def isRefreshEnabled(self): return False
    def setRefreshEnabled(self, v): pass

    def refresh(self): pass

#@memoized
#def global_(): return MouseSelector()

# EOF
