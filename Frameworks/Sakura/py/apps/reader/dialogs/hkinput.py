# coding: utf8
# hkinput.py
# 3/15/2014 jichi

__all__ = 'HotkeyInputDialog',

if __name__ == '__main__':
  import sys
  sys.path.append('..')
  import debug
  debug.initenv()

from functools import partial
from PySide.QtCore import Qt, Signal
from Qt5 import QtWidgets
from sakurakit import skqss
from sakurakit.skclass import Q_Q, memoizedproperty
from sakurakit.sktr import tr_
from sakurakit.skwidgets import shortcut
from mytr import mytr_
import i18n, rc
from hkman import packhotkey, unpackhotkey

class HotkeyInputDialog(QtWidgets.QDialog):
  valueChanged = Signal(str) # hotkey

  def __init__(self, parent=None):
    WINDOW_FLAGS = Qt.Dialog|Qt.WindowMinMaxButtonsHint
    super(HotkeyInputDialog, self).__init__(parent, WINDOW_FLAGS)
    skqss.class_(self, 'texture')
    self.setWindowTitle(mytr_("Shortcuts"))
    self.setWindowIcon(rc.icon('window-shortcuts'))
    self.__d = _HotkeyInputDialog(self)
    #self.resize(300, 250)
    #self.statusBar() # show status bar

  def setValue(self, v): # str ->
    self.__d.defaultValue = v

  def setVisible(self, t): # bool ->
    if t:
      self.__d.refresh()
    super(HotkeyInputDialog, self).setVisible(t)

@Q_Q
class _HotkeyInputDialog(object):
  def __init__(self, q):
    self.defaultValue = ''
    self.keyButtons = {
      'key': [], # [QPushButton]
      'modifier': [],
    }
    self._createUi(q)

  def _createUi(self, q):
    grid = QtWidgets.QGridLayout()
    grid.setHorizontalSpacing(0)
    grid.setVerticalSpacing(0)

    # These keys must be consistent with pyhk

    KEYBOARD  = (
      ('Escape',  'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12'), #'Escape'
      ('`',       '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'Back'),
      ('Capital', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[', ']', '\\'),
      (None,      'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';', "'"), # '\n',
      (None,      'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '/'),
      ('Up', 'Down', 'Left', 'Right'),
    )

    r = 0
    for keys in KEYBOARD:
      for col,key in enumerate(keys):
        if key:
          btn = self.createKeyButton(key)
          grid.addWidget(btn, r, col)
      r += 1

    WIDE_COL = 2

    KEYBOARD2  = (
      ('Space', 'Insert', 'Delete', 'Home', 'End', 'Prior', 'Next'),
      ('mouse left', 'mouse middle', 'mouse right'),
    )
    for keys in KEYBOARD2:
      for i,key in enumerate(keys):
        col = i * WIDE_COL
        if key:
          btn = self.createKeyButton(key)
          grid.addWidget(btn, r, col, 1, WIDE_COL)
      r += 1

    MODIFIERS  = 'Ctrl', 'Alt' #, 'Shift'
    for i,key in enumerate(MODIFIERS):
      col = i * WIDE_COL
      if key:
        btn = self.createKeyButton(key, group='modifier', styleClass='btn btn-info')
        grid.addWidget(btn, r, col, 1, WIDE_COL)
    r += 1

    layout = QtWidgets.QVBoxLayout()
    layout.addLayout(grid)

    row = QtWidgets.QHBoxLayout()
    row.addStretch()
    row.addWidget(self.delButton)
    row.addWidget(self.cancelButton)
    row.addWidget(self.saveButton)
    layout.addLayout(row)

    #buttonBox = QtWidgets.QDialogButtonBox()
    #buttonBox.addButton(self.delButton, buttonBox.ResetRole)
    #buttonBox.addButton(self.cancelButton, buttonBox.RejectRole)
    #buttonBox.addButton(self.saveButton, buttonBox.AcceptRole)
    #layout.addWidget(buttonBox)

    q.setLayout(layout)

    shortcut('ctrl+s', self.save, parent=q)

  def createKeyButton(self, key, group='key', styleClass='btn btn-default'): # str -> QPushButton
    ret = QtWidgets.QPushButton(i18n.key_name(key))
    ret.setToolTip(key)
    if styleClass:
      skqss.class_(ret, styleClass)
    ret.setCheckable(True)
    ret.value = key # str
    ret.clicked.connect(partial(lambda ret, key, group:
        self.updateCurrentValue(key, toggled=ret.isChecked(), group=group),
        ret, key, group))
    self.keyButtons[group].append(ret)
    return ret

  @memoizedproperty
  def delButton(self):
    ret = QtWidgets.QPushButton(tr_("Delete"))
    skqss.class_(ret, 'btn btn-danger')
    ret.clicked.connect(self.delete)
    return ret

  @memoizedproperty
  def cancelButton(self):
    ret = QtWidgets.QPushButton(tr_("Cancel"))
    skqss.class_(ret, 'btn btn-default')
    ret.clicked.connect(self.q.hide)
    return ret

  @memoizedproperty
  def saveButton(self):
    ret = QtWidgets.QPushButton(tr_("Save"))
    ret.setToolTip("Ctrl+S")
    skqss.class_(ret, 'btn btn-primary')
    ret.clicked.connect(self.save)
    ret.setDefault(True)
    return ret

  def delete(self):
    self.q.hide()
    if self.currentValue():
      self.q.valueChanged.emit('')

  def save(self):
    self.q.hide()
    v = self.currentValue()
    if self.defaultValue != v:
      self.q.valueChanged.emit(v)

  def currentValue(self): # -> str
    l = []
    for group in 'modifier', 'key': # modifiers at first, key at last
      for it in self.keyButtons[group]:
        if it.isChecked():
          l.append(it.value)
    return packhotkey(l)

  def setCurrentValue(self, value): # str ->
    l = unpackhotkey(value)
    for buttons in self.keyButtons.itervalues():
      for it in buttons:
        it.setChecked(it.value in l)
        #it.setFocus(Qt.MouseFocusReason)

  def _findValue(self, group): # str -> str
    for it in self.keyButtons[group]:
      if it.isChecked():
        return it.value

  def updateCurrentValue(self, value, toggled=True, group='key'): # str ->
    if group == 'modifier' and not self._findValue('key'):
      for it in self.keyButtons['modifier']: # clear modifiers
        it.setChecked(False)
      return

    # Note: Multiple modifiers are not allowed
    modifier = self._findValue('modifier')

    if modifier:
      for it in self.keyButtons[group]:
        it.setChecked(it.value == value)
    elif group != 'modifier' or toggled:
      self.setCurrentValue(value)

  def refresh(self):
    self.setCurrentValue(self.defaultValue)

if __name__ == '__main__':
  a = debug.app()
  w = HotkeyInputDialog()
  w.show()
  a.exec_()

# EOF
