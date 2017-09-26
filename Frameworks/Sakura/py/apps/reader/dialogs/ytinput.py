# coding: utf8
# ytinput.py
# 11/29/2013 jichi

__all__ = 'YouTubeInput',

if __name__ == '__main__':
  import sys
  sys.path.append('..')
  import debug
  debug.initenv()

import os, re
from Qt5 import QtWidgets
from PySide.QtCore import Qt
from sakurakit import skclip, skpaths, skqss
from sakurakit.skclass import Q_Q, memoizedproperty
from sakurakit.sktr import tr_
from mytr import my, mytr_
import growl, procutil, rc

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

class YouTubeInput(QtWidgets.QDialog):
  def __init__(self, parent=None):
    WINDOW_FLAGS = Qt.Dialog|Qt.WindowMinMaxButtonsHint
    super(YouTubeInput, self).__init__(parent, WINDOW_FLAGS)
    self.setWindowTitle(mytr_("Download YouTube Videos"))
    self.setWindowIcon(rc.icon('logo-youtube'))
    self.__d = _YouTubeInput(self)

@Q_Q
class _YouTubeInput(object):

  def __init__(self, q):
    self._createUi(q)

  def _createUi(self, q):
    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(self.textEdit)

    row = QtWidgets.QHBoxLayout()
    row.addStretch()
    row.addWidget(self.pasteButton)
    row.addWidget(self.saveButton)
    layout.addLayout(row)
    q.setLayout(layout)

  @memoizedproperty
  def textEdit(self):
    placeholder = "http://youtube.com/watch?v=lmOZEAAEMK0"
    #ret = QtWidgets.QPlainTextEdit(placeholder)
    ret = QtWidgets.QTextEdit(placeholder) # QTextEdit is needed for syntax highlighter
    ret.setToolTip(my.tr("Text contains YouTube video IDs"))
    ret.setAcceptRichText(False)
    # Not enabled for performance reason
    #ret.textChanged.connect(self._refreshSaveButton)
    from qthls.youtube import YouTubeHighlighter
    YouTubeHighlighter(ret)
    return ret

  @memoizedproperty
  def saveButton(self):
    ret = QtWidgets.QPushButton(tr_("Download"))
    ret.setToolTip(tr_("Download"))
    skqss.class_(ret, 'btn btn-primary')
    ret.clicked.connect(self._save)
    return ret

  @memoizedproperty
  def pasteButton(self):
    ret = QtWidgets.QPushButton(tr_("Paste"))
    ret.setToolTip(tr_("Paste"))
    skqss.class_(ret, 'btn btn-default')
    ret.clicked.connect(self._paste)
    return ret

  def _paste(self):
    t = skclip.gettext().strip()
    if t:
      self.textEdit.setPlainText(t)

  def _refreshSaveButton(self):
    self.saveButton.setEnabled(self._containsVids())

  def _save(self):
    vids = list(self._iterVids())
    if not vids:
      growl.warn(my.tr("Not found YouTube videos"))
    else:
      growl.msg(my.tr("Found {0} YouTube videos").format(len(vids)))
      path = skpaths.DESKTOP
      if len(vids) > 1:
        path = os.path.join(path, 'YouTube')
      procutil.getyoutube(vids, path=path)
      self.q.hide()

  def _containsVids(self):
    """
    @return  bool
    """
    for it in self._iterVids():
      return True
    return False

  def _iterVids(self):
    """
    @yield  str
    """
    return _itervids(self.textEdit.toPlainText().strip())

if __name__ == '__main__':
  t = """
www.youtube.com/watch?feature=player_embedded&v=VmGK
KbpxutU
"""
  print list(_itervids(t))

  a = debug.app()
  w = YouTubeInput()
  w.show()
  a.exec_()

# EOF
