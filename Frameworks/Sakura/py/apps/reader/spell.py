# coding: utf8
# spell.py
# 12/9/2012 jichi
#
# See: http://john.nachtimwald.com/tag/pyqt/

import re, weakref
from PySide.QtCore import Slot, Signal, Property, Qt, QObject
from PySide.QtGui import QTextCharFormat
from Qt5.QtWidgets import QSyntaxHighlighter
from sakurakit.skclass import Q_Q
#from sakurakit.skqml import QmlObject
import rc

class _SpellHighlighter(object):

  def __init__(self):
    self.lang = 'en'

  @property
  def dic(self): return rc.enchant_dict(self.lang)

class SpellHighlighter(QSyntaxHighlighter):

  def __init__(self, *args, **kwargs):
    super(SpellHighlighter, self).__init__(*args, **kwargs)
    self.__d = _SpellHighlighter()

  def language(self): return self.__d.lang
  def setLanguage(self, lang):
    #if lang != self.__d.lang:
    self.__d.lang = lang
    #self.rehighlight()

  def highlightBlock(self, text):
    """@reimp @public"""
    dic = self.__d.dic
    if not dic:
      return

    WORDS = "(?iu)[\w']+"
    #WORDS = "(?iu)[\w]+"    # ' is not considered as part of a world

    fmt = QTextCharFormat()
    fmt.setUnderlineColor(Qt.red)
    fmt.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)

    for word_object in re.finditer(WORDS, text):
      if not dic.check(word_object.group()):
        self.setFormat(word_object.start(),
          word_object.end() - word_object.start(), fmt)

@Q_Q
class _SpellChecker(object):
  def __init__(self):
    self.language = ""  # str
    self.enabled = False

  @property
  def document(self):
    """
    @return  QTextDocument or None
    """
    try: return self._document_ref()
    except (AttributeError, TypeError): pass

  @document.setter
  def document(self, value):
    self._document_ref = weakref.ref(value) if value else None

  @property
  def highlighter(self):
    try: return self._highlighter_ref()
    except AttributeError:
      obj = SpellHighlighter(self.q)
      obj.setLanguage(self.language)
      #obj.setDocument(self.document)
      self._highlighter_ref = weakref.ref(obj)
      return self._highlighter_ref()

  def hasHighlighter(self): return hasattr(self, '_highlighter_ref')

  def clearDocument(self):
    #self.q.setDocument(None)
    self.document = None
    self.highlighter.setDocument(None)
    #self.q.documentChanged.emit(None)

#@QmlObject # jichi: why not needed?!
class SpellChecker(QObject):
  def __init__(self, parent=None):
    super(SpellChecker, self).__init__(parent)
    self.__d = _SpellChecker(self)

  def setDocument(self, doc):
    d = self.__d
    if d.document is not doc:
      if doc:
        doc.destroyed.connect(d.clearDocument)
      d.document = doc
      if d.hasHighlighter():
        d.highlighter.setDocument(doc if d.enabled else None)
      self.documentChanged.emit(doc)

  documentChanged = Signal(QObject) # QtWidgets.QTextDocument
  document = Property(QObject,
      lambda self: self.__d.document,
      setDocument,
      notify=documentChanged)

  def setLanguage(self, lang):
    d = self.__d
    if d.language != lang:
      d.language = lang
      if d.hasHighlighter():
        d.highlighter.setLanguage(lang)
      self.languageChanged.emit(lang)
  languageChanged = Signal(unicode)
  language = Property(unicode,
      lambda self: self.__d.language,
      setLanguage,
      notify=languageChanged)

  def setEnabled(self, value):
    d = self.__d
    if value != d.enabled:
      d.enabled = value
      d.highlighter.setDocument(d.document if value else None)
      self.enabledChanged.emit(value)
  enabledChanged = Signal(bool)
  enabled = Property(bool,
      lambda self: self.__d.enabled,
      setEnabled,
      notify=enabledChanged)

# EOF
