# coding: utf8
# googletts.py
# 11/25/2012 jichi
#
# Example: http://translate.google.com/translate_tts?tl=ja&q=hello

from sakurakit.sknetio import topercentencoding

DEFAULT_API = "http://translate.google.com/translate_tts"
API = DEFAULT_API

def defaultapi(): return DEFAULT_API
def setapi(url): global API; API = url

#def url(text, language, encoding='UTF-8'):
def url(text, language, encoding=None): # encoding is not needed
  """
  @param  text  unicode  not None
  @param  language  str  not None
  @param* encoding  utf8 or UTF-8 or None
  @return  unicode or str not None
  """
  if language:
    if encoding:
      text = topercentencoding(text, encoding)
    if text:
      if encoding:
        return API + "?client=t&ie=%s&tl=%s&q=%s" % (encoding, language, text)
      else:
        return API + "?client=t&tl=%s&q=%s" % (language, text)
  return ''

#if __name__ == '__main__':
#  import sys
#  sys.path.append("..") # debug only

#from PySide.QtCore import QUrl
#from sakurakit.skdebug import dprint

#GOOGLE_TTS_API = defaulturl()
#
#class _GoogleTtsPlayer(object):
#  def __init__(self, type, parent=None):
#    self.type = type
#    self.parent = parent
#    self.warmed = False
#    self._qtplayer = None
#
#  @property
#  def qtplayer(self):
#    if not self._qtplayer:
#      from qtbrowser.qtplayer import HiddenPlayer
#      self._qtplayer = HiddenPlayer(self.parent)
#    return self._qtplayer
#
#  def stop(self):
#    if self.type == qt:
#      if self._qtplayer:
#        self._qtplayer.stop()
#
#  def setParent(self, v):
#    self.parent = v
#    if self._qtplayer:
#      self._qtplayer.stop()
#
#  # Qt
#  def qtspeak(self, text, language):
#    """
#    @param  text  str
#    @param  language  str
#    """
#    self.qtplayer.play(GOOGLE_TTS_API, tl=language, q=text)
#
#  def qtwarmup(self):
#    self.qtspeak(" ", language='ja') # hardcode language is bad
#
#class GoogleTtsPlayer(object):
#  TYPES = (
#    'qt',   # QuickTime
#    'wmp',  # Windows Media Player
#  )
#
#  def __init__(self, parent=None, type=TYPES[0]):
#    """
#    @param* type  str
#    @param* parent  QWidget
#    """
#    self.__d = _GoogleTtsPlayer(type=type, parent=parent)
#
#  def parentWidget(self):
#    """
#    @return  QWidget or None
#    """
#    return self.__d.parent
#
#  def setParentWidget(self, value):
#    """
#    @param  widget  QWidget or None
#    """
#    self.__d.setParent(value)
#
#  def type(self): return self.__d.type # -> str
#  def setType(self, v): self.__d.type = v # str ->
#
#  def stop(self):
#    self.__d.stop()
#
#  def warmup(self):
#    d = self.__d
#    if not d.warmed:
#      if d.type == 'qt':
#        d.qtwarmup()
#      d.warmed = True
#
#  def speak(self, text, language='ja'):
#    """
#    @param  text  str or unicode
#    @param  language  str  two-characters lcode such as 'en' or 'ja'
#    """
#    if len(language) > 2:
#      language = language[:2]
#    d = self.__d
#    if d.type == 'qt':
#      d.qtspeak(text, language)
#    else:
#      d.wmpspeak(text, language)

if __name__ == '__main__':
  import sys

  from PySide.QtCore import QTimer
  from PySide.QtGui import QApplication
  from PySide.QtWebKit import QWebView

  #q = u"ももももももももももまたもももももももももももともももいろいろ"
  #q = u"にゃにゃめにゃにゃじゅうにゃにゃどのにゃらびでにゃくにゃくいにゃにゃくにゃにゃはんにゃにゃだいにゃんにゃくにゃらべてにゃがにゃがめ"
  q = u"お花の匂い"

  def test_native():
    #url = 'http://translate.google.com/translate_tts'
    url = 'http://translate.google.com/translate_tts?tl=ja'
    url = QUrl(url)
    url.addEncodedQueryItem('q', QUrl.toPercentEncoding(q))
    print url.toString()

    update_web_settings()

    a = QApplication(sys.argv)
    w = QWebView()
    w.load(url)
    w.show()

    ret = a.exec_()

  def test_qt():
    a = QApplication(sys.argv)
    w = QWebView()
    w.show()

    g = GoogleTtsPlayer('qt')
    g.setParentWidget(w)
    QTimer.singleShot(1000, lambda: g.speak(q, language='ja'))

    ret = a.exec_()
    print "leave: ret = %i" % ret

  test_native()

# EOF
