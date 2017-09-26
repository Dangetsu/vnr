# coding: utf8
# lang.py
# 11/10/2012 jichi

from PySide.QtCore import Qt, QRegExp
from PySide.QtGui import QColor, QFont, QTextCharFormat
from Qt5.QtWidgets import QSyntaxHighlighter

HLS_COMMENT_COLOR = Qt.darkGreen
HLS_PRAGMA_COLOR = QColor('purple')
HLS_LITERAL_COLOR = Qt.red
HLS_KEYWORD_COLOR = Qt.darkBlue
HLS_FUNCTION_COLOR = Qt.blue
HLS_CLASS_COLOR = Qt.darkMagenta
HLS_TYPE_COLOR = Qt.darkYellow
HLS_TODO_COLOR = Qt.yellow

HLS_DOXY_PATTERNS = (
  r"@param\b",
  r"@return\b",
)

HLS_TODO_PATTERNS = (
  r"\bXXX\b",
  r"\bTODO\b",
  r"\bFIXME\b",
)

# See: http://qt.gitorious.org/pyside/pyside-examples
class CppHighlighter(QSyntaxHighlighter):

  KEYWORD_PATTERNS = (
    r"\bcase\b",
    r"\bclass\b",
    r"\bdefault\b",
    r"\benum\b",
    r"\bexplicit\b",
    r"\bfriend\b",
    r"\bfor\b",
    r"\belse\b",
    r"\bif\b",
    r"\binline\b",
    r"\bnamespace\b",
    r"\boperator\b",
    r"\bprivate\b",
    r"\bprotected\b",
    r"\bpublic\b",
    r"\breturn\b",
    r"\bswitch\b",
    r"\bstruct\b",
    r"\btemplate\b",
    r"\btypedef\b",
    r"\btypename\b",
    r"\bunion\b",
    r"\bvirtual\b",
    r"\bvolatile\b",
  )

  TYPE_PATTERNS = (
    r"\bchar\b",
    r"\bconst\b",
    r"\bdouble\b",
    r"\bexplicit\b",
    r"\bint\b",
    r"\blong\b",
    r"\bshort\b",
    r"\bfloat\b",
    r"\bdouble\b",
    r"\bsignals\b",
    r"\bsigned\b",
    r"\bslots\b",
    r"\bstatic\b",
    r"\bstruct\b",
    r"\bunsigned\b",
  )

  CONSTANT_PATTERNS = (
    r"\btrue\b",
    r"\bfalse\b",
  )

  def __init__(self, parent=None):
    """
    @param  parent  QObject or QTextDocument or QTextEdit or None
    """
    super(CppHighlighter, self).__init__(parent)

    keywordFormat = QTextCharFormat()
    keywordFormat.setForeground(HLS_KEYWORD_COLOR)
    keywordFormat.setFontWeight(QFont.Bold)
    self.highlightingRules = [(QRegExp(pattern), keywordFormat)
        for pattern in self.KEYWORD_PATTERNS]

    typeFormat = QTextCharFormat()
    typeFormat.setForeground(HLS_TYPE_COLOR)
    typeFormat.setFontWeight(QFont.Bold)
    self.highlightingRules.extend([(QRegExp(pattern), typeFormat)
        for pattern in self.TYPE_PATTERNS])

    constantFormat = QTextCharFormat()
    constantFormat.setForeground(HLS_LITERAL_COLOR)
    self.highlightingRules.extend([(QRegExp(pattern), constantFormat)
        for pattern in self.CONSTANT_PATTERNS])

    classFormat = QTextCharFormat()
    classFormat.setFontWeight(QFont.Bold)
    classFormat.setForeground(HLS_CLASS_COLOR)
    self.highlightingRules.append((QRegExp(r"\bQ[A-Za-z]+\b"),
        classFormat))

    functionFormat = QTextCharFormat()
    functionFormat.setFontItalic(True)
    functionFormat.setForeground(HLS_FUNCTION_COLOR)
    self.highlightingRules.append((QRegExp(r"\b[A-Za-z0-9_]+(?=\()"),
        functionFormat))

    quotationFormat = QTextCharFormat()
    quotationFormat.setForeground(HLS_LITERAL_COLOR)
    self.highlightingRules.append((QRegExp(r'"[^"]*"'), quotationFormat))

    # This must comes before the line comments since they conficts
    pragmaFormat = QTextCharFormat()
    pragmaFormat.setForeground(HLS_PRAGMA_COLOR)
    self.highlightingRules.append((QRegExp(r"#[^\n]*"),
        pragmaFormat))

    self.multiLineCommentFormat = QTextCharFormat()
    self.multiLineCommentFormat.setForeground(HLS_COMMENT_COLOR)

    singleLineCommentFormat = QTextCharFormat()
    singleLineCommentFormat.setForeground(HLS_COMMENT_COLOR)
    self.highlightingRules.append((QRegExp("//[^\n]*"),
        singleLineCommentFormat))

    self.commentStartExpression = QRegExp(r"/\*")
    self.commentEndExpression = QRegExp(r"\*/")

  def highlightBlock(self, text):
    """@reimp @protected"""
    for pattern, format in self.highlightingRules:
      expression = QRegExp(pattern)
      index = expression.indexIn(text)
      while index >= 0:
        length = expression.matchedLength()
        self.setFormat(index, length, format)
        index = expression.indexIn(text, index + length)

    self.setCurrentBlockState(0)

    startIndex = 0
    if self.previousBlockState() != 1:
      startIndex = self.commentStartExpression.indexIn(text)

    while startIndex >= 0:
      endIndex = self.commentEndExpression.indexIn(text, startIndex +1)

      if endIndex == -1:
        self.setCurrentBlockState(1)
        commentLength = len(text) - startIndex
      else:
        commentLength = endIndex - startIndex + self.commentEndExpression.matchedLength()

      self.setFormat(startIndex, commentLength,
          self.multiLineCommentFormat)
      startIndex = self.commentStartExpression.indexIn(text,
          startIndex + commentLength);

class JsHighlighter(QSyntaxHighlighter):

  KEYWORD_PATTERNS = (
    r"\bbreak\b",
    r"\bcase\b",
    r"\bclass\b",
    r"\bcontinue\b",
    r"\bdo\b",
    r"\belse\b",
    r"\bfor\b",
    r"\bfunction\b",
    r"\bif\b",
    r"\bin\b",
    r"\breturn\b",
    r"\bswitch\b",
    r"\btype\b",
    r"\bvar\b",
    r"\bwhile\b",
  )

  TYPE_PATTERNS = (
    r"\bboolean\b",
    r"\bdouble\b",
    r"\bid\b",
    r"\bint\b",
    r"\blong\b",
    r"\bstring\b",
  )

  CONSTANT_PATTERNS = (
    r"\btrue\b",
    r"\bfalse\b",
  )

  def __init__(self, parent=None):
    """
    @param  parent  QObject or QTextDocument or QTextEdit or None
    """
    super(JsHighlighter, self).__init__(parent)

    keywordFormat = QTextCharFormat()
    keywordFormat.setForeground(HLS_KEYWORD_COLOR)
    keywordFormat.setFontWeight(QFont.Bold)
    self.highlightingRules = [(QRegExp(pattern), keywordFormat)
        for pattern in self.KEYWORD_PATTERNS]

    typeFormat = QTextCharFormat()
    typeFormat.setForeground(HLS_TYPE_COLOR)
    typeFormat.setFontWeight(QFont.Bold)
    self.highlightingRules.extend([(QRegExp(pattern), typeFormat)
        for pattern in self.TYPE_PATTERNS])

    constantFormat = QTextCharFormat()
    constantFormat.setForeground(HLS_LITERAL_COLOR)
    self.highlightingRules.extend([(QRegExp(pattern), constantFormat)
        for pattern in self.CONSTANT_PATTERNS])

    classFormat = QTextCharFormat()
    classFormat.setFontWeight(QFont.Bold)
    classFormat.setForeground(HLS_CLASS_COLOR)
    self.highlightingRules.append((QRegExp(r"\bQ[A-Za-z]+\b"),
        classFormat))

    functionFormat = QTextCharFormat()
    functionFormat.setFontItalic(True)
    functionFormat.setForeground(HLS_FUNCTION_COLOR)
    self.highlightingRules.append((QRegExp(r"\b[A-Za-z0-9_]+(?=\()"),
        functionFormat))

    quotationFormat = QTextCharFormat()
    quotationFormat.setForeground(HLS_LITERAL_COLOR)
    self.highlightingRules.append((QRegExp(r'"[^"]*"'), quotationFormat))
    self.highlightingRules.append((QRegExp(r"'[^']*'"), quotationFormat))

    singleLineCommentFormat = QTextCharFormat()
    singleLineCommentFormat.setForeground(HLS_COMMENT_COLOR)
    self.highlightingRules.append((QRegExp("//[^\n]*"),
        singleLineCommentFormat))

    self.multiLineCommentFormat = QTextCharFormat()
    self.multiLineCommentFormat.setForeground(HLS_COMMENT_COLOR)

    self.commentStartExpression = QRegExp(r"/\*")
    self.commentEndExpression = QRegExp(r"\*/")

    todoFormat = QTextCharFormat()
    todoFormat.setBackground(HLS_TODO_COLOR)
    self.postHighlightingRules = [(QRegExp(pattern), todoFormat)
        for pattern in HLS_TODO_PATTERNS]

    doxyFormat = QTextCharFormat()
    doxyFormat.setForeground(HLS_COMMENT_COLOR)
    doxyFormat.setFontWeight(QFont.Bold)
    self.postHighlightingRules.extend([(QRegExp(pattern), doxyFormat)
        for pattern in HLS_DOXY_PATTERNS])

  def highlightBlock(self, text):
    """@reimp @protected"""
    for pattern, format in self.highlightingRules:
      expression = QRegExp(pattern)
      index = expression.indexIn(text)
      while index >= 0:
        length = expression.matchedLength()
        self.setFormat(index, length, format)
        index = expression.indexIn(text, index + length)

    self.setCurrentBlockState(0)

    startIndex = 0
    if self.previousBlockState() != 1:
      startIndex = self.commentStartExpression.indexIn(text)

    while startIndex >= 0:
      endIndex = self.commentEndExpression.indexIn(text, startIndex +1)

      if endIndex == -1:
        self.setCurrentBlockState(1)
        commentLength = len(text) - startIndex
      else:
        commentLength = endIndex - startIndex + self.commentEndExpression.matchedLength()

      self.setFormat(startIndex, commentLength,
          self.multiLineCommentFormat)
      startIndex = self.commentStartExpression.indexIn(text,
          startIndex + commentLength);

    for pattern, format in self.postHighlightingRules:
      expression = QRegExp(pattern)
      index = expression.indexIn(text)
      while index >= 0:
        length = expression.matchedLength()
        self.setFormat(index, length, format)
        index = expression.indexIn(text, index + length)

class PyHighlighter(QSyntaxHighlighter):

  KEYWORD_PATTERNS = (
    r"\bbreak\b",
    r"\bclass\b",
    r"\bcontinue\b",
    r"\bdef\b",
    r"\bdo\b",
    r"\belif\b",
    r"\belse\b",
    r"\bfor\b",
    r"\bfunction\b",
    r"\bid\b",
    r"\bif\b",
    r"\bimport\b",
    r"\bin\b",
    r"\bprint\b",
    r"\breturn\b",
    r"\btype\b",
    r"\bwhile\b",
  )

  TYPE_PATTERNS = (
    r"\bbool\b",
    r"\bdouble\b",
    r"\bint\b",
    r"\blong\b",
    r"\bprint\b",
    r"\bstr\b",
    r"\bunicode\b",
  )

  CONSTANT_PATTERNS = (
    r"\bTrue\b",
    r"\bFalse\b",
  )

  def __init__(self, parent=None):
    """
    @param  parent  QObject or QTextDocument or QTextEdit or None
    """
    super(PyHighlighter, self).__init__(parent)

    keywordFormat = QTextCharFormat()
    keywordFormat.setForeground(HLS_KEYWORD_COLOR)
    keywordFormat.setFontWeight(QFont.Bold)
    self.highlightingRules = [(QRegExp(pattern), keywordFormat)
        for pattern in self.KEYWORD_PATTERNS]

    typeFormat = QTextCharFormat()
    typeFormat.setForeground(HLS_TYPE_COLOR)
    typeFormat.setFontWeight(QFont.Bold)
    self.highlightingRules.extend([(QRegExp(pattern), typeFormat)
        for pattern in self.TYPE_PATTERNS])

    constantFormat = QTextCharFormat()
    constantFormat.setForeground(HLS_LITERAL_COLOR)
    self.highlightingRules.extend([(QRegExp(pattern), constantFormat)
        for pattern in self.CONSTANT_PATTERNS])

    classFormat = QTextCharFormat()
    classFormat.setFontWeight(QFont.Bold)
    classFormat.setForeground(HLS_CLASS_COLOR)
    self.highlightingRules.append((QRegExp(r"\bQ[A-Za-z]+\b"),
        classFormat))

    functionFormat = QTextCharFormat()
    functionFormat.setFontItalic(True)
    functionFormat.setForeground(HLS_FUNCTION_COLOR)
    self.highlightingRules.append((QRegExp(r"\b[A-Za-z0-9_]+(?=\()"),
        functionFormat))

    quotationFormat = QTextCharFormat()
    quotationFormat.setForeground(HLS_LITERAL_COLOR)
    self.highlightingRules.append((QRegExp(r'"[^"]*"'), quotationFormat))
    self.highlightingRules.append((QRegExp(r'u"[^"]*"'), quotationFormat))
    self.highlightingRules.append((QRegExp(r"'[^']*'"), quotationFormat))
    self.highlightingRules.append((QRegExp(r"u'[^']*'"), quotationFormat))

    singleLineCommentFormat = QTextCharFormat()
    singleLineCommentFormat.setForeground(HLS_COMMENT_COLOR)
    self.highlightingRules.append((QRegExp("#[^\n]*"), singleLineCommentFormat))

    self.multiLineCommentFormat = QTextCharFormat()
    self.multiLineCommentFormat.setForeground(HLS_COMMENT_COLOR)

    self.commentStartExpression = QRegExp(r'"""')
    self.commentEndExpression = QRegExp(r'"""')

    todoFormat = QTextCharFormat()
    todoFormat.setBackground(HLS_TODO_COLOR)
    self.postHighlightingRules = [(QRegExp(pattern), todoFormat)
        for pattern in HLS_TODO_PATTERNS]

    doxyFormat = QTextCharFormat()
    doxyFormat.setForeground(HLS_COMMENT_COLOR)
    doxyFormat.setFontWeight(QFont.Bold)
    self.postHighlightingRules.extend([(QRegExp(pattern), doxyFormat)
        for pattern in HLS_DOXY_PATTERNS])

  def highlightBlock(self, text):
    """@reimp @protected"""
    for pattern, format in self.highlightingRules:
      expression = QRegExp(pattern)
      index = expression.indexIn(text)
      while index >= 0:
        length = expression.matchedLength()
        self.setFormat(index, length, format)
        index = expression.indexIn(text, index + length)

    self.setCurrentBlockState(0)

    startIndex = 0
    if self.previousBlockState() != 1:
      startIndex = self.commentStartExpression.indexIn(text)

    while startIndex >= 0:
      endIndex = self.commentEndExpression.indexIn(text, startIndex +1)

      if endIndex == -1:
        self.setCurrentBlockState(1)
        commentLength = len(text) - startIndex
      else:
        commentLength = endIndex - startIndex + self.commentEndExpression.matchedLength()

      self.setFormat(startIndex, commentLength,
          self.multiLineCommentFormat)
      startIndex = self.commentStartExpression.indexIn(text,
          startIndex + commentLength);

    for pattern, format in self.postHighlightingRules:
      expression = QRegExp(pattern)
      index = expression.indexIn(text)
      while index >= 0:
        length = expression.matchedLength()
        self.setFormat(index, length, format)
        index = expression.indexIn(text, index + length)

# EOF
