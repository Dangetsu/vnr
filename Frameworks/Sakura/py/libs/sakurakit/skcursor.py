# coding: utf8
# skcursor.py
# 2/27/2013 jichi

from PySide.QtCore import Qt
from Qt5.QtWidgets import QApplication

class SkAutoCursor(object):

  def __init__(self, shape):
    """
    @param  shape  Qt.CursorShape
    """
    QApplication.setOverrideCursor(shape)

  def __del__(self):
    QApplication.restoreOverrideCursor()

class SkAutoWaitCursor(SkAutoCursor):
  def __init__(self):
    super(SkAutoWaitCursor, self).__init__(Qt.WaitCursor)

class SkAutoBusyCursor(SkAutoCursor):
  def __init__(self):
    super(SkAutoBusyCursor, self).__init__(Qt.BusyCursor)

# EOF
