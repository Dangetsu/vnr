# coding: utf8
# submaker.py
# 10/10/2012 jichi
#
# Graffiti backing bean.

from ctypes import c_longlong
from PySide.QtCore import Signal, Slot, QObject
from sakurakit import skdatetime
from sakurakit.skdebug import dprint
#from sakurakit.skqml import QmlObject
from sakurakit.sktr import tr_
from mytr import mytr_
import qmldialog, textman

## Graffiti ##

#@Q_Q
#class _GraffitiBean(object):
#  def __init__(self, q):
#    q.destroyed.connect(self._onDestroyed)
#
#  def _onDestroyed(self):
#    if self.q is GraffitiBean.instance:
#      GraffitiBean.instance = None

#@QmlObject
class GraffitiBean(QObject):

  def __init__(self, parent=None):
    super(GraffitiBean, self).__init__(parent)

    tm = textman.manager()
    tm.cleared.connect(self.clear)
    tm.pageBreakReceived.connect(self.pageBreak)
    tm.rawTextReceived.connect(self.showText)
    tm.translationReceived.connect(self.showTranslation)
    tm.commentReceived.connect(self.showComment)

    dprint("pass")

  clear = Signal()
  pageBreak = Signal()
  showText = Signal(unicode, unicode, c_longlong, int)  # text, lang, ctx hash, ctx size
  showTranslation = Signal(unicode, unicode, unicode)  # text, lang, provider
  showComment = Signal(QObject) # compatible with dataman.Comment

  #connectModel = Signal()
  #disconnectModel = Signal()

  @Slot(result=int)
  def x(self): return qmldialog.SubtitleMaker.instance.x()

  @Slot(result=int)
  def y(self): return qmldialog.SubtitleMaker.instance.y()

#@QmlObject
class SubtitleContextBean(QObject):

  def __init__(self, parent=None):
    super(SubtitleContextBean, self).__init__(parent)

    tm = textman.manager()
    tm.contextChanged.connect(self.refresh)
    tm.cleared.connect(self.refresh)

    dprint("pass")

  refresh = Signal()

  @Slot()
  def read(self):
    tm = textman.manager()
    ctx = tm.contextSize()
    texts = tm.recentTexts()
    if ctx and texts and len(texts) >= ctx:
      t = '\n'.join(texts[-ctx:])
      import ttsman
      ttsman.speak(t)

  @Slot(result=unicode)
  def renderText(self):
    tm = textman.manager()
    ctx = tm.contextSize()
    texts = tm.recentTexts()

    #assert len(texts) >= ctx
    ret = ""
    if not ctx or not texts or len(texts) < ctx:
      ret += '<br/>'.join((
        "<b>%s</b> (%s)" % (tr_("Context"), tr_("read-only")),
        '',
        tr_("Empty"),
      ))
    else:
      cur = texts[-1]
      prev = None
      if ctx > 1:
        prev = texts[-ctx:-1]

      ret += '<br/>'.join((
        "<b>%s</b> (%s)" % (tr_("Context"), tr_("read-only")),
        '',
        cur.replace('\n', '<br/>'),
      ))
      if prev:
        ret += '<br/>'.join((
          '', '', # Two lines
          "<b>%s</b> (%s)" % (mytr_("Previous context"), tr_("read-only")),
          '',
          '<br/>'.join(prev).replace('\n', '<br/>'),
        ))
    return ret

# EOF

#  def showText(self, text, language, ctxhash, ctxsize):
#    try: GraffitiBean.instance.showText.emit(text, language, ctxhash, ctxsize)
#    except AttributeError: pass
#  def showTranslation(self, text, language, provider):
#    try: GraffitiBean.instance.showTranslation.emit(text, language, provider)
#    except AttributeError: pass
#  def showComment(self, comment):
#    try: GraffitiBean.instance.showComment.emit(comment)
#    except AttributeError: pass
