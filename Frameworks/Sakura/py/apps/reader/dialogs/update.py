# coding: utf8
# update.py
# 12/9/2014 jichi

__all__ = 'UpdateDialog',

if __name__ == '__main__':
  import sys
  sys.path.append('..')
  import debug
  debug.initenv()

from PySide.QtCore import Qt
from Qt5 import QtWidgets
from sakurakit import skqss
from sakurakit.skclass import Q_Q
from sakurakit.sktr import tr_
from mytr import my
import info, osutil, rc

class UpdateDialog(QtWidgets.QDialog):
  def __init__(self, parent=None):
    WINDOW_FLAGS = Qt.Dialog|Qt.WindowMinMaxButtonsHint
    super(UpdateDialog, self).__init__(parent, WINDOW_FLAGS)
    skqss.class_(self, 'texture')
    self.__d = _UpdateDialog(self)
    self.setWindowIcon(rc.icon('window-update'))
    self.setWindowTitle(tr_("Software Update"))
    self.resize(220, 120)

class _UpdateDialog:
  def __init__(self, q):
    self._createUi(q)

  def openUpdate(self):
    osutil.open_location(rc.app_path('updater'))

  def openChanges(self):
    url = 'http://sakuradite.com/changes/vnr'
    osutil.open_url(url)

  def _createUi(self, q):
    layout = QtWidgets.QVBoxLayout()
    b = cancelButton = QtWidgets.QPushButton(tr_("Cancel"))
    skqss.class_(b, 'btn btn-default')
    b.clicked.connect(q.hide)

    b = updateButton = QtWidgets.QPushButton(tr_("Update"))
    b.setToolTip(tr_("Update"))
    skqss.class_(updateButton, 'btn btn-primary')
    b.clicked.connect(q.hide)
    b.clicked.connect(self.openUpdate)
    b.setDefault(True)

    infoLabel = QtWidgets.QLabel(my.tr(
"""Found new updates for Visual Novel Reader.
Do you want to update now?
You can find recent changes here:"""))
    layout.addWidget(infoLabel)

    linkstyle = 'color:#428bca' # bootstrap btn-link
    url = 'http://sakuradite.com/changes/vnr'
    changesLabel = QtWidgets.QLabel(
        '<a href="{1}" style="{0}">{1}</a>'.format(linkstyle, url))
    changesLabel.setOpenExternalLinks(True)
    changesLabel.setAlignment(Qt.AlignHCenter)
    changesLabel.setToolTip(tr_("Recent changes"))
    layout.addWidget(changesLabel)

    layout.addStretch()

    row = QtWidgets.QHBoxLayout()
    row.addStretch()
    row.addWidget(cancelButton)
    row.addWidget(updateButton)
    layout.addLayout(row)

    q.setLayout(layout)

if __name__ == '__main__':
  a = debug.app()
  w = UpdateDialog()
  w.show()
  a.exec_()

# EOF
