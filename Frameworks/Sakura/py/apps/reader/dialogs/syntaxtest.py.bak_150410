# coding: utf8
# syntaxtest.py
# 10/4/2014 jichi

__all__ = 'SyntaxTester',

if __name__ == '__main__':
  import sys
  sys.path.append('..')
  import debug
  debug.initenv()

import re
from functools import partial
from PySide.QtCore import Qt
from Qt5 import QtWidgets
from sakurakit import skqss
from sakurakit.skclass import memoizedproperty
from sakurakit.skdebug import dprint, dwarn
from sakurakit.sktr import tr_
import rbmt.api as rbmt
from mytr import my, mytr_
import rc

_EMPTY_TEXT = "(%s)" % tr_("Empty")
_ERROR_TEXT = "(%s)" % tr_("Error")

def create_label(text=""): # unicode -> QLabel
  ret = QtWidgets.QLabel()
  if text:
    ret.setText(text + ":")
  ret.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
  return ret

class _SyntaxTester(object):

  def __init__(self, q):
    self.language = '' # str
    self._createUi(q)

    import settings
    settings.global_().userLanguageChanged.connect(self._reloadLanguage)
    self._reloadLanguage()

    if self.isEnabled():
      self._refreshSyntaxView()
      self._refreshTargetView()

  def _createUi(self, q):
    self.sourceView.setPlainText(u"【綾波レイ】「ごめんなさい。こう言う時どんな顔すればいいのか分からないの。」")
    self.patternEdit.setText(u"($x ない の 。)")
    self.replaceEdit.setText(u"(不 $x 的 。)")

    self.sourceView.textChanged.connect(self._refreshSyntaxView)
    self.sourceView.textChanged.connect(self._refreshTargetView)
    self.patternEdit.textChanged.connect(self._refreshTargetView)
    self.replaceEdit.textChanged.connect(self._refreshTargetView)

    layout = QtWidgets.QVBoxLayout()

    grid = QtWidgets.QGridLayout()

    # 0
    grid.addWidget(create_label(tr_("Pattern")), 0, 0)
    grid.addWidget(self.patternEdit, 0, 1)

    # 1
    grid.addWidget(create_label(tr_("Translation")))
    grid.addWidget(self.replaceEdit)

    # 2
    grid.addWidget(create_label(tr_("Language")))
    grid.addWidget(self.languageLabel)

    layout.addLayout(grid)

    splitter = QtWidgets.QSplitter(Qt.Vertical)
    splitter.addWidget(self.sourceView)
    splitter.addWidget(self.syntaxView)
    splitter.addWidget(self.targetView)
    layout.addWidget(splitter)
    q.setLayout(layout)

  @property
  def cabocha(self):
    import cabochaman
    return cabochaman.cabochaparser()

  @memoizedproperty
  def ma(self):
    return rbmt.MachineAnalyzer(self.cabocha)

  @memoizedproperty
  def mt(self):
    return rbmt.MachineTranslator(self.cabocha, 'zhs')

  def _refreshSyntaxView(self):
    text = self.sourceView.toPlainText().strip()
    if text:
      try:
        text = self.ma.parseToString(text)
        if text:
          self.syntaxView.setPlainText(text or _EMPTY_TEXT)
          return
      except Exception, e:
        dwarn(e)

    self.syntaxView.setPlainText(_EMPTY_TEXT)

  def _refreshTargetView(self):
    source = self.sourceView.toPlainText().strip()
    if source:
      pattern = self.patternEdit.text().strip()
      if pattern:
        try:
          target = self.replaceEdit.text().strip()
          rule = rbmt.createrule(pattern, target, self.language)
          if rule:
            self.mt.setRules([rule])
            target = self.mt.dumpTranslate(source)
            self.targetView.setPlainText(target or _EMPTY_TEXT)
            return
        except Exception, e:
          dwarn(e)

    self.targetView.setPlainText(_EMPTY_TEXT)

  @memoizedproperty
  def languageLabel(self):
    ret = QtWidgets.QLabel()
    skqss.class_(ret, 'text-info')
    ret.setToolTip(tr_("Language"))
    return ret

  def _reloadLanguage(self):
    import dataman, i18n
    lang = dataman.manager().user().language
    if lang != self.language:
      self.language = lang
      self.languageLabel.setText(i18n.language_name(lang))
      sep = '' if lang.startswith('zh') else ' '
      self.mt.setSeparator(sep)
      self.mt.setLanguage(lang)

  @memoizedproperty
  def sourceView(self):
    ret = QtWidgets.QPlainTextEdit()
    skqss.class_(ret, 'normal')
    ret.setToolTip(mytr_("Input"))
    return ret

  @memoizedproperty
  def syntaxView(self):
    ret = QtWidgets.QTextEdit(my.tr("Missing MeCab, CaboCha, or UniDic"))
    ret.setReadOnly(True)
    skqss.class_(ret, 'texture')
    ret.setToolTip(my.tr("Syntax parse tree"))

    from qthls.bracket import ParenthesisHighlighter
    hls = ParenthesisHighlighter(ret)
    ret.cursorPositionChanged.connect(
        partial(self._highlight, ret, hls))
    return ret

  def _highlight(self, edit, hls):
    """
    @param  edit  QTextEdit
    @param  hls  QSyntaxHighlighter
    """
    cur = edit.textCursor()
    if cur.hasSelection():
      hls.setStartPosition(cur.selectionStart())
      hls.setStopPosition(cur.selectionEnd())
    else:
      pos = cur.position()
      hls.setStartPosition(pos)
      hls.setStopPosition(pos)
    hls.rehighlight()

  @memoizedproperty
  def targetView(self):
    ret = QtWidgets.QTextEdit(my.tr("Missing MeCab, CaboCha, or UniDic"))
    ret.setReadOnly(True)
    skqss.class_(ret, 'texture')
    ret.setToolTip(mytr_("Output"))

    from qthls.bracket import ParenthesisHighlighter
    hls = ParenthesisHighlighter(ret)
    ret.cursorPositionChanged.connect(
        partial(self._highlight, ret, hls))
    return ret

  @memoizedproperty
  def patternEdit(self):
    ret = QtWidgets.QLineEdit()
    skqss.class_(ret, 'normal')
    ret.setToolTip(my.tr("Subtree to match"))
    ret.setPlaceholderText(ret.toolTip())
    return ret

  @memoizedproperty
  def replaceEdit(self):
    ret = QtWidgets.QLineEdit()
    skqss.class_(ret, 'normal')
    ret.setToolTip(my.tr("Subtree to replace"))
    ret.setPlaceholderText(ret.toolTip())
    return ret

  def isEnabled(self):
    import settings
    ss = settings.global_()
    return ss.isCaboChaEnabled() and ss.meCabDictionary() == 'unidic'

# I have to use QMainWindow, or the texture will not work
class SyntaxTester(QtWidgets.QDialog):

  def __init__(self, parent=None):
    WINDOW_FLAGS = Qt.Dialog|Qt.WindowMinMaxButtonsHint
    super(SyntaxTester, self).__init__(parent, WINDOW_FLAGS)
    skqss.class_(self, 'texture')
    self.__d = _SyntaxTester(self)
    self.setWindowTitle(mytr_("Test Japanese Syntax Tree"))
    self.setWindowIcon(rc.icon('window-syntax'))
    self.resize(380, 350)
    dprint("pass")

  def setVisible(self, t):
    """@reimp"""
    if t and t != self.isVisible():
      self.setEnabled(self.__d.isEnabled())
    super(SyntaxTester, self).setVisible(t)

if __name__ == '__main__':
  a = debug.app()
  w = SyntaxTester()
  w.show()
  a.exec_()

# EOF
