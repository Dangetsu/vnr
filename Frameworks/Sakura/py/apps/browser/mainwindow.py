# coding: utf8
# mainwindow.py
# 12/13/2012 jichi

__all__ = 'MainWindow',

from itertools import imap
from PySide.QtCore import QTimer
from sakurakit import skos, skqss
from sakurakit.skclass import memoizedproperty, Q_Q
from sakurakit.sktr import tr_
from browserui import WebBrowser
import config, rc, ui

@Q_Q
class _MainWindow(object):

  @memoizedproperty
  def statusBarTimer(self):
    q = self.q
    ret = QTimer(q)
    ret.setSingleShot(True)
    ret.setInterval(5000)
    ret.timeout.connect(q.statusBar().hide)
    return ret

  @staticmethod
  def styleClass(): # -> str
    ret = 'main texture-inverse'

    if skos.MAC:
      ret += ' mac'
    elif skos.LINUX:
      ret += ' linux'
    elif skos.WIN:
      ret += ' win'
      if skos.WINXP:
        ret += ' winxp'
      elif skos.WIN7:
        ret += ' win7'
      elif skos.WIN8:
        ret += ' win8'

    #if ui.DWM_ENABLED:
    #  ret += ' aero'
    #else:
    #  ret += ' notaero'
    return ret

class MainWindow(WebBrowser):
  def __init__(self, parent=None):
    #WINDOW_FLAGS = (
    #  Qt.Window
    #  | Qt.CustomizeWindowHint
    #  | Qt.WindowTitleHint
    #  | Qt.WindowSystemMenuHint
    #  | Qt.WindowMinMaxButtonsHint
    #  | Qt.WindowCloseButtonHint
    #)
    super(MainWindow, self).__init__(parent)
    skqss.addclass(self, _MainWindow.styleClass())

    self.setStyleSheet(''.join(imap(rc.qss, config.QT_STYLESHEETS)))
    #self.setStyleSheet(rc.qss('browser'))

    self.setWindowTitle(u"Kagami (α)")
    self.setWindowIcon(rc.icon('logo-browser'))
    #ui.glassifyWidget(self)
    self.__d = _MainWindow(self)

    b = self.statusBar()
    b.setGraphicsEffect(ui.createGlowEffect(b))

    self.messageReceived.connect(self.showStatusMessage)
    #self.showStatusMessage(tr_("Ready"))
    self.statusBar().hide()

  def showStatusMessage(self, t, type='message'):
    """@reimp
    @param  t  unicode
    @param  type  'message', 'warning', or 'error'
    """
    b = self.statusBar()
    #b.setStyleSheet(SS_STATUSBAR_MESSAGE);
    b.showMessage(t)
    if t:
      b.show()
      self.__d.statusBarTimer.start()

# EOF
