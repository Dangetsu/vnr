# coding: utf8
# retest.py
# 12/16/2012 jichi

__all__ = 'RegExpTester',

if __name__ == '__main__':
  import sys
  sys.path.append('..')
  import debug
  debug.initenv()

import re
from PySide.QtCore import Qt
from Qt5 import QtWidgets
from sakurakit import skqss
from sakurakit.skclass import memoizedproperty
from sakurakit.skdebug import dprint
from sakurakit.sktr import tr_
from mytr import mytr_
import rc

def create_label(text=""): # unicode -> QLabel
  ret = QtWidgets.QLabel()
  if text:
    ret.setText(text + ":")
  ret.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
  return ret

class _RegExpTester(object):

  def __init__(self, q):
    self._createUi(q)
    self._refresh()

  def _createUi(self, q):
    #url = "http://en.wikipedia.org/wiki/Regular_expression"
    url = "http://www.regular-expressions.info/lookaround.html"
    self.textEdit.appendHtml(
"""You can use this tester to play with the regular expression
(<a href="%s">%s</a>) used in the Shared Dictionary.
<br/><br/>

For example, "regular(?= exp)" will match all "regular" before " exp".
""" % (url, url))

    self.patternEdit.setText("regular(?= exp)")
    self.replaceEdit.setText("HELLO WORLD")

    for sig in (
        self.textEdit.textChanged,
        self.patternEdit.textChanged,
        self.replaceEdit.textChanged,
        self.regexCheckBox.toggled,
        self.icaseCheckBox.toggled,
      ):
      sig.connect(self._refresh)

    layout = QtWidgets.QVBoxLayout()

    grid = QtWidgets.QGridLayout()

    # 0
    grid.addWidget(create_label(tr_("Pattern")), 0, 0)
    grid.addWidget(self.patternEdit, 0, 1)

    # 1
    grid.addWidget(create_label(tr_("Translation")))
    grid.addWidget(self.replaceEdit)

    # 2
    grid.addWidget(create_label(tr_("Status")))
    grid.addWidget(self.messageEdit)

    layout.addLayout(grid)

    row = QtWidgets.QHBoxLayout()
    row.addWidget(self.regexCheckBox)
    row.addWidget(self.icaseCheckBox)
    layout.addLayout(row)

    splitter = QtWidgets.QSplitter(Qt.Vertical)
    splitter.addWidget(self.textEdit)
    splitter.addWidget(self.textView)
    layout.addWidget(splitter)
    q.setLayout(layout)

  def _refresh(self):
    """
    @param  text  unicode
    @return  unicode
    """
    text = self.textEdit.toPlainText()
    pattern = self.patternEdit.text().strip()
    repl = self.replaceEdit.text().strip()
    r = self.regexCheckBox.isChecked()
    i = self.icaseCheckBox.isChecked()
    result = text
    try:
      if r and i:
        rx = re.compile(pattern, re.IGNORECASE|re.DOTALL)
        result = rx.sub(repl, text)
      elif r:
        result = re.sub(pattern, repl, text)
      elif i:
        pattern = re.escape(pattern)
        rx = re.compile(pattern, re.IGNORECASE|re.DOTALL)
        result = rx.sub(repl, text)
      else:
        result = text.replace(pattern, repl)
      matched = result != text
      message = tr_("Found") if matched else tr_("Not found")
      skqss.class_(self.messageEdit, 'default')
      self.messageEdit.setText(message)
    except Exception, e:
      skqss.class_(self.messageEdit, 'error')
      message = e.message or "%s" % e
      self.messageEdit.setText(message)
    self.textView.setHtml(result)

  @memoizedproperty
  def textView(self):
    ret = QtWidgets.QTextBrowser()
    skqss.class_(ret, 'texture')
    ret.setToolTip(tr_("Target"))
    ret.setOpenExternalLinks(True)
    #ret.setAcceptRichText(False)
    return ret

  @memoizedproperty
  def textEdit(self):
    ret = QtWidgets.QPlainTextEdit()
    skqss.class_(ret, 'normal')
    ret.setToolTip(tr_("Source"))
    return ret

  @memoizedproperty
  def patternEdit(self):
    ret = QtWidgets.QLineEdit()
    skqss.class_(ret, 'normal')
    ret.setToolTip(mytr_("Matched text"))
    ret.setPlaceholderText(ret.toolTip())
    return ret

  @memoizedproperty
  def replaceEdit(self):
    ret = QtWidgets.QLineEdit()
    skqss.class_(ret, 'normal')
    ret.setToolTip(mytr_("Replaced text"))
    ret.setPlaceholderText(ret.toolTip())
    return ret

  @memoizedproperty
  def messageEdit(self):
    ret = QtWidgets.QLineEdit()
    ret.setReadOnly(True)
    ret.setToolTip(tr_("Status"))
    ret.setPlaceholderText(ret.toolTip())
    return ret

  @memoizedproperty
  def regexCheckBox(self):
    ret = QtWidgets.QCheckBox()
    ret.setText(tr_("Regular expression"))
    ret.setToolTip(tr_("Regular expression"))
    ret.setChecked(True)
    return ret

  @memoizedproperty
  def icaseCheckBox(self):
    ret = QtWidgets.QCheckBox()
    ret.setText(tr_("Ignore case"))
    ret.setToolTip(tr_("Ignore case"))
    #ret.setChecked(True)
    return ret

# I have to use QMainWindow, or the texture will not work
class RegExpTester(QtWidgets.QDialog):

  def __init__(self, parent=None):
    WINDOW_FLAGS = Qt.Dialog|Qt.WindowMinMaxButtonsHint
    super(RegExpTester, self).__init__(parent, WINDOW_FLAGS)
    skqss.class_(self, 'texture')
    self.__d = _RegExpTester(self)
    self.setWindowTitle(mytr_("Test Regular Expression"))
    self.setWindowIcon(rc.icon('window-regexp'))
    self.resize(380, 350)
    dprint("pass")

if __name__ == '__main__':
  a = debug.app()
  w = RegExpTester()
  w.show()
  a.exec_()

# EOF
