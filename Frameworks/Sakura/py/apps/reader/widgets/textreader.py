# coding: utf8
# textreader.py
# 6/23/2013 jichi
#
# Signal flow:
# textspy => textreader => kagami.mirage

import re
from PySide.QtCore import Signal, Slot, QObject #, QTimer
from sakurakit import skdatetime, skevents, skstr
from sakurakit.skclass import Q_Q, memoized
#from sakurakit.skqml import QmlObject
from sakurakit.skdebug import dwarn
#from msime import msime
from mytr import my
import defs, growl, settings, textutil, trman

@Q_Q
class _TextReader(object):

  def __init__(self):
    #t = self._speakTextTimer = QTimer(q)
    #t.setSingleShot(True)
    #t.timeout.connect(self._speakText)

    #t = self._speakSubtitleTimer = QTimer(q)
    #t.setSingleShot(True)
    #t.timeout.connect(self._speakSubtitle)

    self.language = 'en' # str, user language
    self.gameLanguage = 'ja' # str, constant
    self.lastText = "" # unicode

    #self.ttsSubtitle = "" # unicode not None, either subtitle or translation
    #self.ttsName = "" # unicode not None, character name
    #self.ttsText = "" # unicode, game text, might be reset
    #self.lastTtsText = "" # unicode, current game text

  #def _correctText(self, text):
  #  """
  #  @param  text  unicode
  #  @return  unicode
  #  """
  #  if settings.global_().isMsimeCorrectionEnabled():
  #    if msime.ja_valid():
  #      return msime.to_kanji(text) or text
  #    else:
  #      growl.warn(my.tr("Microsoft Japanese IME is not installed"))
  #  return text

  def _translateTextAndShow(self, text, time):
    trman.manager().translateApply(self._showTranslation,
        text, self.gameLanguage,
        time=time)

  def _showTranslation(self, sub, language, provider, align, time=0):
    """
    @param  sub  unicode
    @param  language  unicode
    @param  provider  unicode
    @param  align  list  ignored
    @param* long  time
    """
    #sub = userplugin.revise_translation(sub, language)
    if sub:
      self.q.translationReceived.emit(sub, language, provider, time)
      #self._updateTtsSubtitle(sub, language)

  def showText(self, text):
    """
    @param  text  unicode
    """
    q = self.q
    q.pageBreakReceived.emit()

    timestamp = skdatetime.current_unixtime()

    #self._updateTtsText(text)

    #text = self._correctText(text)
    text = textutil.beautify_text(text)
    q.textReceived.emit(text, self.gameLanguage, timestamp)

    self._translateTextAndShow(text, timestamp)

class TextReader(QObject):

  ## Construction ##

  def __init__(self, parent=None):
    super(TextReader, self).__init__(parent)
    self.__d = _TextReader(self)

  pageBreakReceived = Signal()
  textReceived = Signal(unicode, unicode, long)   # text, lang, timestamp
  translationReceived = Signal(unicode, unicode, unicode, long) # text, language, provider, timestamp

  ## Properties ##

  def userLanguage(self): return self.__d.language
  def setUserLanguage(self, value): self.__d.language = value

  #def encoding(self): return self.__d.encoding
  #def setEncoding(self, encoding): self.__d.encoding = encoding

  def gameLanguage(self): return self.__d.gameLanguage
  def setGameLanguage(self, value): self.__d.gameLanguage = value

  ## Actions ##

  def addText(self, text):
    d = self.__d
    if text == d.lastText:
      return
    d.lastText = text
    #if len(text) > defs.MIRAGE_MAX_TEXT_LENGTH:
    #  growl.msg(my.tr("Game text is ignored for being too long"))
    #else:
    d.showText(text)

@memoized
def manager(): return TextReader()

#@QmlObject
class TextReaderProxy(QObject):
  def __init__(self, parent=None):
    super(TextReaderProxy, self).__init__(parent)

  @Slot(unicode)
  def addText(self, text): manager().addText(text)

# EOF
