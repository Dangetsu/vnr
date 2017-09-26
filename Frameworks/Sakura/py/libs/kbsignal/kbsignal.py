# coding: utf8
# kbsignal.py
# 9/9/2014 jichi
# Windows only

__all__ = 'KeyboardSignal',

#from sakurakit.skclass import memoized

from sakurakit import skos
if skos.WIN:
  from pykbsignal import KeyboardSignal

else:
  from PySide.QtCore import Signal, QObject

  class KeyboardSignal(QObject): # dummy
    def __init__(self, parent=None):
      super(KeyboardSignal, self).__init__(parent)

    pressed = Signal(int) # vk
    released = Signal(int) # vk

    def isEnabled(self): return False
    def setEnabled(self, t): pass

    def isKeyEnabled(self, vk): return False
    def setKeyEnabled(self, vk, t): pass

    def refreshInterval(self): return 0
    def setRefreshInterval(self, v): pass

    def isRefreshEnabled(self): return False
    def setRefreshEnabled(self, v): pass

    def refresh(self): pass

#@memoized
#def global_(): return KeyboardSignal()

# EOF
