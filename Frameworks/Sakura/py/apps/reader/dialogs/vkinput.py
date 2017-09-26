# coding: utf8
# vkinput.py
# 9/15/2014 jichi

__all__ = 'VirtualKeyInputDialog',

if __name__ == '__main__':
  import sys
  sys.path.append('..')
  import debug
  debug.initenv()

from functools import partial
from PySide.QtCore import Qt, Signal
from Qt5 import QtWidgets
from sakurakit import skqss, skos
from sakurakit.skclass import Q_Q, memoizedproperty
from sakurakit.sktr import tr_
from sakurakit.skwidgets import shortcut
from mytr import mytr_
import rc

if skos.WIN:
   # http://msdn.microsoft.com/en-us/library/windows/desktop/dd375731%28v=vs.85%29.aspx
  import win32con
  VK_VALUES = { # {str name:int vk}
    'F1': win32con.VK_F1,
    'F2': win32con.VK_F2,
    'F3': win32con.VK_F3,
    'F4': win32con.VK_F4,
    'F5': win32con.VK_F5,
    'F6': win32con.VK_F6,
    'F7': win32con.VK_F7,
    'F8': win32con.VK_F8,
    'F9': win32con.VK_F9,
    'F10': win32con.VK_F10,
    'F11': win32con.VK_F11,
    'F12': win32con.VK_F12,

    'Esc': win32con.VK_ESCAPE,
    'Cap': win32con.VK_CAPITAL,
    'Back': win32con.VK_BACK,
    'Enter': win32con.VK_RETURN,
    'Space': win32con.VK_SPACE,
    'Shift': win32con.VK_SHIFT,
    'Ctrl': win32con.VK_CONTROL,
    'Alt': win32con.VK_MENU,
    'PageUp': win32con.VK_PRIOR,
    'PageDown': win32con.VK_NEXT,
    'Home': win32con.VK_HOME,
    'End': win32con.VK_END,
    'Insert': win32con.VK_INSERT,
    'Delete': win32con.VK_DELETE,

    "=": 0xbb, #VK_OEM_PLUS,
    "-": 0xbd, #VK_OEM_MINUMS,
    ",": 0xbc, #VK_OEM_COMMA,
    ".": 0xbe, #VK_OEM_PERIOD,

    ';': 0xba, #VK_OEM_1,
    '/': 0xbf, #VK_OEM_2,
    '`': 0xc0, #VK_OEM_3,
    '[': 0xdb, #VK_OEM_4,
    '\\': 0xdc, #VK_OEM_5,
    ']': 0xdd, #VK_OEM_6,
    "'": 0xde, #VK_OEM_7,
  }
  VK_NAMES = {v:k for k,v in VK_VALUES.iteritems()} # {int vk:str name}

  def vk_value(name): return VK_VALUES.get(name) or ord(name) # str -> int
  def vk_name(vk): return VK_NAMES.get(vk) or chr(vk).upper() # int -> str

class VirtualKeyInputDialog(QtWidgets.QDialog):
  valueChanged = Signal(int) # vk

  def __init__(self, parent=None):
    WINDOW_FLAGS = Qt.Dialog|Qt.WindowMinMaxButtonsHint
    super(VirtualKeyInputDialog, self).__init__(parent, WINDOW_FLAGS)
    skqss.class_(self, 'texture')
    self.setWindowTitle(mytr_("Shortcuts"))
    self.setWindowIcon(rc.icon('window-shortcuts'))
    self.__d = _VirtualKeyInputDialog(self)
    #self.resize(300, 250)
    #self.statusBar() # show status bar

  def setValue(self, v): # int ->
    self.__d.defaultValue = v

  def setDeletable(self, t): # bool ->
    self.__d.deletable = t

  def setVisible(self, t): # bool ->
    if t:
      self.__d.refresh()
    super(VirtualKeyInputDialog, self).setVisible(t)

@Q_Q
class _VirtualKeyInputDialog(object):
  def __init__(self, q):
    self.defaultValue = 0 # int
    self.keyButtons = [] # [QPushButton]
    self.deletable = True # bool
    self._createUi(q)

  def _createUi(self, q):
    grid = QtWidgets.QGridLayout()
    grid.setHorizontalSpacing(0)
    grid.setVerticalSpacing(0)

    # These keys must be consistent with pyhk

    KEYBOARD  = (
      ('Esc',  'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12'), #'Escape'
      ('`',    '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'Back'),
      ('Cap',  'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[', ']', '\\'),
      (None,   'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';', "'"), # 'Enter',
      (None,   'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '/'),
      #('Up', 'Down', 'Left', 'Right'),
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
      ('Shift', 'Ctrl', 'Alt'), # 'Space'
      ('Insert', 'Delete', 'Home', 'End', 'PageUp', 'PageDown'),
      #('mouse left', 'mouse middle', 'mouse right'),
    )
    for keys in KEYBOARD2:
      for i,key in enumerate(keys):
        col = i * WIDE_COL
        if key:
          btn = self.createKeyButton(key)
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

  def createKeyButton(self, key): # str -> QPushButton
    ret = QtWidgets.QPushButton(key)
    ret.setToolTip(key)
    ret.value = vk_value(key) # int
    skqss.class_(ret, 'btn btn-default')
    ret.setCheckable(True)
    ret.clicked.connect(partial(lambda ret:
        self.updateCurrentValue(ret.value, ret.isChecked()),
        ret))
    self.keyButtons.append(ret)
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
      self.q.valueChanged.emit(0)

  def save(self):
    self.q.hide()
    v = self.currentValue()
    if self.defaultValue != v:
      self.q.valueChanged.emit(v)

  def currentValue(self): # -> int
    for it in self.keyButtons:
      if it.isChecked():
        return it.value
    return 0

  def setCurrentValue(self, value): # int ->
    for it in self.keyButtons:
      it.setChecked(it.value == value)

  def updateCurrentValue(self, value, checked): # str, bool ->
    if checked or (not self.deletable and not self.currentValue()):
      self.setCurrentValue(value)

  def refresh(self):
    self.setCurrentValue(self.defaultValue)
    self.delButton.setVisible(self.deletable)

if __name__ == '__main__':
  a = debug.app()
  w = VirtualKeyInputDialog()
  w.setDeletable(False)
  w.show()
  a.exec_()

# EOF
