# coding: utf8
# dictest.py
# 2/16/2014 jichi

__all__ = 'DictionaryTester',

if __name__ == '__main__':
  import sys
  sys.path.append('..')
  import debug
  debug.initenv()

from functools import partial
from PySide.QtCore import Qt #, Signal
from Qt5 import QtWidgets
from sakurakit import skqss
from sakurakit.skclass import memoizedproperty
from sakurakit.sktr import tr_
from mytr import mytr_
import dictman, rc

DEFAULT_INPUT = u"万歳"
EMPTY_PLACEHOLDER = tr_("Empty") + "! ><"

CSS_TEXTEDIT = """\
QTextEdit {
  font-size: 13px;
}
"""

#@Q_Q
class _DictionaryTester(object):
  def __init__(self, q):
    self._createUi(q)

  def _createUi(self, q):
    layout = QtWidgets.QVBoxLayout()

    row = QtWidgets.QHBoxLayout()
    row.addWidget(self.inputEdit)
    row.addWidget(self.submitButton)
    row.addWidget(self.pasteButton)
    row.addWidget(self.clearButton)
    row.addWidget(self.speakButton)
    layout.addLayout(row)

    layout.addWidget(self.resultEdit)

    q.setLayout(layout)

  @memoizedproperty
  def submitButton(self):
    ret = QtWidgets.QPushButton(tr_("Lookup"))
    ret.setToolTip(tr_("Lookup"))
    ret.setDefault(True)
    skqss.class_(ret, 'btn btn-primary')
    ret.clicked.connect(self.submit)
    return ret

  @memoizedproperty
  def speakButton(self):
    ret = QtWidgets.QPushButton(mytr_("Speak"))
    ret.setToolTip(mytr_("Speak"))
    skqss.class_(ret, 'btn btn-inverse')
    ret.clicked.connect(self._speak)
    return ret

  @memoizedproperty
  def clearButton(self):
    ret = QtWidgets.QPushButton(tr_("Clear"))
    ret.setToolTip(tr_("Clear"))
    skqss.class_(ret, 'btn btn-inverse')
    ret.clicked.connect(self._clear)
    return ret

  @memoizedproperty
  def pasteButton(self):
    ret = QtWidgets.QPushButton(tr_("Paste"))
    ret.setToolTip(tr_("Paste"))
    skqss.class_(ret, 'btn btn-success')
    ret.clicked.connect(self._paste)
    return ret

  @memoizedproperty
  def inputEdit(self):
    ret = QtWidgets.QLineEdit()
    ret.setText(DEFAULT_INPUT)
    #skqss.class_(ret, 'normal')
    skqss.class_(ret, 'texture-inverse')
    ret.setPlaceholderText(tr_("Japanese"))
    ret.setToolTip(ret.placeholderText())
    ret.textChanged.connect(self.refresh)
    ret.returnPressed.connect(self.submit)
    return ret

  @memoizedproperty
  def resultEdit(self):
    ret = QtWidgets.QTextBrowser()
    ret.setAcceptRichText(False)
    skqss.class_(ret, 'texture-inverse')
    #skqss.class_(ret, 'texture')
    #skqss.class_(ret, 'normal')
    #ret.setToolTip(tr_("Result"))
    ret.setReadOnly(True)
    ret.setPlainText(EMPTY_PLACEHOLDER)
    ret.setStyleSheet(CSS_TEXTEDIT)
    import osutil
    ret.anchorClicked.connect(osutil.open_url)
    return ret

  def _speak(self):
    t = self._getInputText()
    if t:
      import ttsman
      ttsman.speak(t, language='?')

  def _paste(self):
    from sakurakit import skclip
    t = skclip.gettext().strip()
    if t:
      self.inputEdit.setText(t)

  def _clear(self):
    self.inputEdit.clear()

  def _getInputText(self): return self.inputEdit.text().strip()

  def refresh(self):
    t = self._getInputText()
    ok = bool(t)
    for w in self.submitButton, self.speakButton:
      w.setEnabled(ok)

    #if not self.inputEdit.toPlainText():
    #  self.inputEdit.setPlainText(tr_("Empty") + "! ><")

  def submit(self):
    t = self._getInputText()
    if t:
      h = dictman.manager().renderJapanese(t)
      self.resultEdit.setHtml(h)

class DictionaryTester(QtWidgets.QDialog):
  #termEntered = Signal(QtCore.QObject) # Term

  def __init__(self, parent=None):
    WINDOW_FLAGS = Qt.Dialog|Qt.WindowMinMaxButtonsHint
    super(DictionaryTester, self).__init__(parent, WINDOW_FLAGS)
    skqss.class_(self, 'texture-inverse')
    self.setWindowTitle(mytr_("Japanese Dictionary"))
    self.setWindowIcon(rc.icon('window-jdict'))
    self.__d = _DictionaryTester(self)
    #self.__d.refresh()
    self.resize(400, 300)

  def lookup(self, v): # unicode
    if v:
      d = self.__d
      d.inputEdit.setText(v)
      d.refresh()
      d.submit()

if __name__ == '__main__':
  a = debug.app()
  w = DictionaryTester()
  w.show()
  a.exec_()

# EOF
