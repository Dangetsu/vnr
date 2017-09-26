# coding: utf8
# addressui.py
# 12/13/2012 jichi

__all__ = 'WbAddressEdit',

from PySide import QtGui
from PySide.QtCore import Qt, Signal
from Qt5 import QtWidgets
from sakurakit.skclass import Q_Q
import config, rc

class WbAddressEdit(QtWidgets.QComboBox):
  def __init__(self, parent=None):
    super(WbAddressEdit, self).__init__(parent)
    self.__d = _WbAddressEdit(self)
    self.setInsertPolicy(QtWidgets.QComboBox.InsertAtTop)
    self.setEditable(True)

    #self.currentIndexChanged.connect(self.enter) # recursion
    #self.lineEdit().returnPressed.connect(self.enter)

    self.maxCount = config.ADDRESS_HISTORY_SIZE

    self.setToolTip("Ctrl+L, Alt+D")

    completer = self.completer()
    completer.setCaseSensitivity(Qt.CaseInsensitive)
    completer.setCompletionMode(QtWidgets.QCompleter.UnfilteredPopupCompletion)
    completer.setModelSorting(QtWidgets.QCompleter.CaseInsensitivelySortedModel)

  textEntered = Signal(unicode)

  #def enter(self):
  #  t = self.currentText().strip()
  #  if t:
  #    self.setText(t)
  #    self.textEntered.emit(t)

  def focus(self):
    self.setFocus()
    self.lineEdit().selectAll()

  def setText(self, text): # unicode ->
    self.addText(text)
    #self.setEditText(text)
    self.setCurrentIndex(0)

  def addText(self, text): # unicode ->
    index = self.findText(text)
    if index >= 0:
      self.removeItem(index)

    icon = rc.url_icon(text)
    self.insertItem(0, icon, text) # Note: This will change current item!
    if self.count() > self.maxCount:
      self.removeItem(self.maxCount)

  def setProgress(self, v): # int [0,100]
    d = self.__d
    if d.progress != v:
      d.progress = v
      d.refreshPallete()

@Q_Q
class _WbAddressEdit(object):

  def __init__(self, q):
    self.progress = 100 # int [0,100]

    # Enter-pressed or clicked
    q.activated[int].connect(self._activate)

  def _activate(self, index):
    q = self.q
    text = q.itemText(index)
    if text:
      q.setText(text)
      q.setEditText(text) # enforce current text
      q.textEntered.emit(text)

  def refreshPallete(self):
    q = self.q
    if self.progress == 100:
      q.setStyleSheet(q.styleSheet()) # invalidate pallete
    else:
      w = q.width()
      X_INIT = 0.1
      x = X_INIT + self.progress *((1 - X_INIT)/100.0)
      g = QtWidgets.QLinearGradient(0, 0, w*x, 0) # // horizental
      g.setColorAt(0, Qt.transparent)
      g.setColorAt(0.99, QtGui.QColor(113, 201, 244, 180)) # #71c9f4, blue
      g.setColorAt(1, Qt.transparent)
      p = QtWidgets.QPalette()
      p.setBrush(QtWidgets.QPalette.Base, g)
      #q.lineEdit().setPalette(p)
      q.setPalette(p)

# EOF
