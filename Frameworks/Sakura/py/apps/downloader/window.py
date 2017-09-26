# coding: utf8
# window.py
# 11/29/2013 jichi

__all__ = 'MainWindow',

from itertools import imap
from PySide.QtCore import Signal, Qt
from Qt5 import QtWidgets
from sakurakit import skqss
from sakurakit.skclass import memoizedproperty
from sakurakit.skdebug import dprint
from tr import my
import config, rc

# Base window

def _Window(Base):
  class Window(Base):
    def __init__(self, parent=None):
      super(Window, self).__init__(parent)
      self.setWindowIcon(rc.icon('logo-youtube'))

      appName = QtWidgets.QApplication.instance().applicationName()
      self.setWindowTitle("%s (pre-alpha)" % appName)

      self.setStyleSheet(''.join(imap(rc.qss, (
        'bootstrap',
        'share',
      ))).replace('$PWD', config.root_abspath()))

      dprint("pass")

    closeRequested = Signal()

    ## Events ##

    def closeEvent(self, event):
      event.ignore()
      self.closeRequested.emit()
      dprint("pass: ignored")
  return Window

# MainObject private data

class _MainWindow(object):
  def __init__(self, q):
    self._createUi(q)
    #self.debugButton.clicked.connect(q.debugRequested)

  def _createUi(self, q):
    q.addWidget(self.textEdit)
    q.addWidget(self.addressEdit)
    q.addWidget(self.webView)

  @memoizedproperty
  def addressEdit(self):
    t = my.tr("Connecting to {0}").format('www.clipconverter.com')
    ret = QtWidgets.QLineEdit(t)
    #skqss.class_(ret, 'texture text-info')
    skqss.class_(ret, 'texture')
    ret.setPlaceholderText(t)
    ret.setReadOnly(True)
    return ret

  def _refreshAdressEdit(self):
    title = self.webView.title().replace(' - ClipConverter.cc', "") # remove trailing brand name
    url = self.webView.url().toString()
    self.addressEdit.setToolTip(title)
    self.addressEdit.setText("%s - %s" % (url, title))

  @memoizedproperty
  def webView(self):
    from sakurakit import skwebkit
    ret = skwebkit.SkReadOnlyWebView()
    ret.setContextMenuPolicy(Qt.NoContextMenu)
    #ret.titleChanged.connect(ret.setToolTip)   # tooltip is not visible anyway
    ret.titleChanged.connect(self._refreshAdressEdit)
    ret.urlChanged.connect(self._refreshAdressEdit)
    return ret

  @memoizedproperty
  def textEdit(self):
    ret = QtWidgets.QPlainTextEdit()
    ret.setToolTip(my.tr("Messages"))
    #ret.setAcceptRichText(True)
    ret.setReadOnly(True)
    skqss.class_(ret, 'texture')
    return ret

  @memoizedproperty
  def debugButton(self):
    ret = QtWidgets.QPushButton(my.tr("Debug"))
    ret.setToolTip(my.tr("Show debugging window"))
    skqss.class_(ret, 'btn btn-inverse')
    return ret

  #@memoizedproperty
  #def progressBar(self):
  #  ret = QtWidgets.QProgressBar()
  #  return ret

class MainWindow(_Window(QtWidgets.QSplitter)):
  """Root of most objects"""

  instance = None

  # Supposed to be top-level, no parent allowed
  def __init__(self): # not parent class
    super(MainWindow, self).__init__()
    self.setOrientation(Qt.Vertical)
    self.setChildrenCollapsible(False)
    skqss.class_(self, 'texture')

    self.__d = _MainWindow(self)

    self.resize(600, 700)
    MainWindow.instance = self
    dprint("pass")

  #debugRequested = Signal()

  def webView(self): return self.__d.webView

  def appendNewLine(self):
    self.__d.textEdit.appendPlainText('')

  def appendMessage(self, text):
    """
    @param  text  unicode
    """
    self.__d.textEdit.appendHtml(text)

  def appendWarning(self, text):
    """
    @param  text  unicode
    """
    self.__d.textEdit.appendHtml('<span style="color:brown">%s</span>' % text)

  def appendError(self, text):
    """
    @param  text  unicode
    """
    self.__d.textEdit.appendHtml('<span style="color:red">%s</span>' % text)

  def appendNotification(self, text):
    """
    @param  text  unicode
    """
    self.__d.textEdit.appendHtml('<span style="color:blue">%s</span>' % text)

# EOF
