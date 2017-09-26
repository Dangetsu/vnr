# coding: utf8
# youtube.py
# 11/10/2012 jichi

import re
from PySide.QtCore import Qt
from PySide.QtGui import QTextCharFormat
from Qt5.QtWidgets import QSyntaxHighlighter

class YouTubeHighlighter(QSyntaxHighlighter):

  def __init__(self, parent=None):
    """
    @param  parent  QObject or QTextDocument or QTextEdit or None
    """
    super(YouTubeHighlighter, self).__init__(parent)

    self._format = QTextCharFormat()
    self._format.setForeground(Qt.blue)
    #self._format.setFontWeight(QFont.Bold)
    self._format.setFontUnderline(True)
    self._format.setUnderlineColor(Qt.red)
    self._format.setUnderlineStyle(QTextCharFormat.DashUnderline)

  def highlightBlock(self, text):
    """@reimp @protected"""
    for vid in self._itervids(text):
      index = text.index(vid)
      length = len(vid)
      self.setFormat(index, length, self._format)

  @staticmethod
  def _itervids(text):
    """
    @param  text  unicode
    @yield  str
    """
    if text:
      for it in 'http://', 'www.', 'youtu.be', 'youtube.com':
        text = text.replace(it, '')
      for word in re.split(r'\s', text):
        vid = re.sub(r'.*v=([0-9a-zA-Z_-]+).*', r'\1', word)
        if re.match(r'[0-9a-zA-Z_-]+', vid):
          yield vid

# EOF
