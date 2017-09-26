# coding: utf8
# bracket.py
# 10/14/2014 jichi

import re
from PySide.QtCore import Qt
from PySide.QtGui import QTextCharFormat
from Qt5.QtWidgets import QSyntaxHighlighter


class _BracketHighlighter:

  def __init__(self):
    self.start = 0
    self.stop = 0

    f = self.highlightFormat = QTextCharFormat()
    f.setForeground(Qt.blue)
    #f.setFontWeight(QFont.Bold) // this will cause text width change
    f.setFontUnderline(True)
    f.setUnderlineColor(Qt.red)
    f.setUnderlineStyle(QTextCharFormat.DashUnderline)

    f = self.openFormat = self.closeFormat = QTextCharFormat()
    f.setForeground(Qt.red)

class BracketHighlighter(QSyntaxHighlighter):
  openBracket = '['  # str
  closeBracket = ']' # str

  def __init__(self, parent=None):
    """
    @param  parent  QObject or QTextDocument or QTextEdit or None
    """
    super(BracketHighlighter, self).__init__(parent)
    self.__d = _BracketHighlighter()

  def setOpenBracket(self, v): self.openBracket = v
  def setCloseBracket(self, v): self.openBracket = v

  def setStartPosition(self, v): self.__d.start = v
  def setStopPosition(self, v): self.__d.stop = v

  def highlightBlock(self, text):
    """@reimp @protected"""
    d = self.__d
    start = d.start
    stop = d.stop
    if (not text
        or start < 0
        or stop >= len(text)
        or start > stop
        or self.openBracket not in text
        or self.closeBracket not in text):
      return

    rightCount = 0
    right = text[stop:]
    for c in right:
      if c == self.closeBracket:
        rightCount += 1
        if rightCount == 1:
          break
      if c == self.openBracket:
        rightCount -= 1
      stop += 1

    leftCount = 0
    for c in reversed(text[:start]):
      if c == self.openBracket:
        leftCount += 1
        if leftCount == 1:
          break
      if c == self.closeBracket:
        leftCount -= 1
      start -= 1

    if leftCount == 1 and start > 0:
      self.setFormat(start - 1, 1, d.openFormat)
    if rightCount == 1 and stop < len(text):
      self.setFormat(stop, 1, d.openFormat)

    if leftCount == 1 or rightCount == 1:
      if rightCount == 1 or stop >= len(text):
        stop -= 1
      #if start > 0:
      #  start -= 1 # include the left-most '('
      length = stop - start + 1
      if length > 0:
        self.setFormat(start, length, d.highlightFormat)

class ParenthesisHighlighter(BracketHighlighter):
  openBracket = '(' # override
  closeBracket = ')' # override

  def __init__(self, parent=None):
    """
    @param  parent  QObject or QTextDocument or QTextEdit or None
    """
    super(ParenthesisHighlighter, self).__init__(parent)

# EOF
