# coding: utf8
# qmlutil.py
# 1/6/2013 jichi

import os
from PySide.QtCore import Slot, QObject, QUrl
from PySide.QtGui import QFontMetrics
from sakurakit import skmeta
from sakurakit.skdebug import dwarn
#from sakurakit.skqml import QmlObject
import bbcode, convutil, richutil

#@QmlObject
class BBCodeParser(QObject):
  def __init__(self, parent=None):
    super(BBCodeParser, self).__init__(parent)

  @Slot(unicode, result=unicode)
  def parse(self, text): return bbcode.parse(text)

#@QmlObject
class QmlUtil(QObject):
  def __init__(self, parent=None):
    super(QmlUtil, self).__init__(parent)

  @Slot(unicode, result=bool)
  def fileExists(self, value):
    return bool(value) and os.path.exists(value)

  @Slot(unicode, result=bool)
  def urlExists(self, value):
    if not value:
      return False
    url = QUrl(value)
    if not url.isLocalFile():
      return True
    path = url.toLocalFile()
    return os.path.exists(path)

  @Slot(QObject, unicode, QObject, unicode)
  def bind(self, obj1, pty1, obj2, pty2):
    p = (obj1, pty1, obj2, pty2)
    if all(p):
      skmeta.bind_properties(p)
    else:
      dwarn("null property", p)

class JlpUtil(QObject):
  def __init__(self, parent=None):
    super(JlpUtil, self).__init__(parent)

  #@Slot(unicode, unicode, result=unicode)
  #def kana2yomi(self, text, lang):
  #  return convutil.kana2yomi(text, lang)

  @Slot(unicode, unicode, result=unicode)
  def kana2name(self, text, lang):
    return convutil.kana2name(text, lang)

  @Slot(unicode, unicode, unicode, result=unicode)
  def toalphabet(self, text, to, fr):
    return convutil.toalphabet(text, to=to, fr=fr)

  @Slot(unicode, unicode, result=unicode)
  def toroman(self, text, lang):
    return convutil.toroman(text, lang)

  @Slot(unicode, result=unicode)
  def ja2zhs_name(self, text):
    return convutil.ja2zhs_name(text)

  @Slot(unicode, result=unicode)
  def ja2zht_name(self, text):
    return convutil.ja2zht_name(text)

  @Slot(unicode, result=bool)
  def ja2zh_name_test(self, text):
    return convutil.ja2zh_name_test(text)

  @Slot(unicode, result=unicode)
  def render_hanzi(self, text):
    import dictman
    return '\n'.join(dictman.manager().renderHanzi(text))

class TextUtil(QObject):
  def __init__(self, parent=None):
    super(TextUtil, self).__init__(parent)

  @Slot(unicode, int, QFontMetrics, QFontMetrics, result=unicode)
  def renderRubyToHtmlTable(self, text, width, rbFont, rtFont):
    return richutil.renderRubyToHtmlTable(text, width, rbFont, rtFont)

  @Slot(unicode, result=unicode)
  def renderRubyToPlainText(self, text):
    return richutil.renderRubyToPlainText(text)

# EOF
