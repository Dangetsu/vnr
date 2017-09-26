# coding: utf8
# bbtest.py
# 12/16/2012 jichi

__all__ = 'BBCodeTester',

if __name__ == '__main__':
  import sys
  sys.path.append('..')
  import debug
  debug.initenv()

from PySide.QtCore import Qt
from Qt5 import QtWidgets
from sakurakit import skqss
from sakurakit.skdebug import dprint
from mytr import mytr_
import bbcode, rc

class _BBCodeTester:

  def __init__(self, q):
    self._createUi(q)

  def _createUi(self, q):
    textEdit = QtWidgets.QPlainTextEdit()
    textEdit.setToolTip("BBCode")
    #textEdit.setAcceptRichText(False)
    skqss.class_(textEdit, 'normal')

    textView = QtWidgets.QTextBrowser()
    skqss.class_(textView, 'texture')
    textView.setToolTip("HTML")
    textView.setReadOnly(True)
    textView.setOpenExternalLinks(True)

    textEdit.textChanged.connect(lambda:
      textView.setHtml(
        self.toHtml(
          textEdit.toPlainText()
    )))

    textEdit.setPlainText(
"""You can use this [u]tester[/u] to play with [url=http://en.wikipedia.org/wiki/BBCode][color=blue]BBCode[/color][/url]
that you could use to format [color=red]subtitles[/color]."""
)

    #textEdit.resize(300, 200)

    center = QtWidgets.QSplitter(Qt.Vertical)
    center.setChildrenCollapsible(False)
    center.addWidget(textEdit)
    center.addWidget(textView)
    q.setCentralWidget(center)

  @staticmethod
  def toHtml(text):
    """
    @param  text  unicode
    @return  unicode
    """
    return bbcode.parse(text) if '[' in text else text

# I have to use QMainWindow, or the texture will not work
class BBCodeTester(QtWidgets.QMainWindow):

  def __init__(self, parent=None):
    WINDOW_FLAGS = Qt.Dialog|Qt.WindowMinMaxButtonsHint
    super(BBCodeTester, self).__init__(parent)
    skqss.class_(self, 'texture')
    self.setWindowFlags(WINDOW_FLAGS)
    self.setWindowTitle(mytr_("Test BBCode"))
    self.setWindowIcon(rc.icon('window-bbcode'))
    self.__d = _BBCodeTester(self)
    self.setContentsMargins(9, 9, 9, 9)
    self.resize(400, 300)
    dprint("pass")

if __name__ == '__main__':
  a = debug.app()
  w = BBCodeTester()
  w.show()
  a.exec_()

# EOF
