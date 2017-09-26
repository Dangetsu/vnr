# coding: utf8
# appwiz.py
# 12/13/2012 jichi

__all__ = 'AppWizard',

from functools import partial
from PySide.QtCore import Qt, Signal
from PySide import QtCore
from Qt5 import QtWidgets
from sakurakit import skthreads, skqss
from sakurakit.skdebug import dprint
from sakurakit.sktr import tr_
import appman, osutil, rc

# Helpers

class AppSelection:
  def __init__(self):
    self.readerChecked = True
    self.playerChecked = True

# Pages

class PAGEID:
  INTRO = -1
  SELECT = -1
  CONFIRM = -1
  FINAL = -1

class IntroPage(QtWidgets.QWizardPage):
  def __init__(self, parent=None):
    super(IntroPage, self).__init__(parent)
    self.setTitle(self.tr("Add or remove features"))

    introLabel = QtWidgets.QLabel(self.tr("""\
This wizard will direct you to add or remove features.

You can remove the features you don't need to save disk space.
Internet access is needed if you want to add new features.
"""))
    introLabel.setWordWrap(True)

    self._onlineLabel = QtWidgets.QLabel()

    onlineLabel = QtWidgets.QLabel(self.tr("Current Internet status") + ": ")
    onlineLabel.setBuddy(self._onlineLabel)

    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(introLabel)

    row = QtWidgets.QHBoxLayout()
    row.addWidget(onlineLabel)
    row.addWidget(self._onlineLabel)
    row.addStretch()
    layout.addLayout(row)

    self.setLayout(layout)

  def initializePage(self):
    """@reimp @public"""
    self._refresh()
    dprint("pass")

  def _refresh(self):
    online = osutil.is_online()
    self._onlineLabel.setText(tr_("Online") if online  else tr_("Offline"))
    skqss.class_(self._onlineLabel, 'normal' if online else 'warning')

class SelectPage(QtWidgets.QWizardPage):
  def __init__(self, parent=None):
    super(SelectPage, self).__init__(parent)
    self.setTitle(self.tr("Select apps"))

    introLabel = QtWidgets.QLabel(self.tr("Select which app to add or remove"))
    introLabel.setWordWrap(True)

    self._playerButton = QtWidgets.QCheckBox(self.tr('"Annot Player" for the anime'))
    self._playerButton.clicked.connect(self.completeChanged)

    self._readerButton = QtWidgets.QCheckBox(self.tr('"Visual Novel Reader" for the visual novel'))
    self._readerButton.clicked.connect(self.completeChanged)

    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(introLabel)
    layout.addWidget(self._readerButton)
    layout.addWidget(self._playerButton)
    self.setLayout(layout)

  def initializePage(self):
    """@reimp @public"""
    self._load()
    dprint("pass")

  #def cleanupPage(self):
  #  """@reimp @public"""
  #  self._load()
  #  dprint("pass")

  def validatePage(self):
    """@reimp @public"""
    self._save()
    dprint("pass")
    return self.isComplete()

  def nextId(self):
    """@reimp @public"""
    return PAGEID.CONFIRM

  def _save(self):
    sel = self.wizard().selection()
    sel.playerChecked = self._playerButton.isChecked()
    sel.readerChecked = self._readerButton.isChecked()

  def _load(self):
    sel = self.wizard().selection()
    p, r = sel.playerChecked, sel.readerChecked
    if not p and not r:
      #p = r = True
      r = True
    self._playerButton.setChecked(p)
    self._readerButton.setChecked(r)

class ConfirmPage(QtWidgets.QWizardPage):
  def __init__(self, parent=None):
    super(ConfirmPage, self).__init__(parent)
    self.setTitle(self.tr("Confirm changes"))
    self.setCommitPage(True)

    self._infoLabel = QtWidgets.QLabel()
    self._infoLabel.setWordWrap(True)

    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(self._infoLabel)
    self.setLayout(layout)

  def nextId(self):
    """@reimp @public"""
    return PAGEID.FINAL

  def initializePage(self):
    """@reimp @public"""
    self._refresh()
    dprint("pass")

  def _refresh(self):
    man = self.wizard().manager()
    sel = self.wizard().selection()
    t = ""

    if (sel.readerChecked, sel.playerChecked)  == (man.isReaderActivated(), man.isPlayerActivated()):
      t = self.tr("No changes")
    else:
      if sel.readerChecked != man.isReaderActivated():
        if sel.readerChecked:
          t += self.tr('Activate "Visual Novel Reader" for the visual novel') + '\n'
        else:
          t += self.tr('Deactivate "Visual Novel Reader" for the visual novel') + '\n'
      if sel.playerChecked != man.isPlayerActivated():
        if sel.playerChecked:
          t += self.tr('Activate "Annot Player" for the anime') + '\n'
        else:
          t += self.tr('Deactivate "Annot Player" for the anime') + '\n'

    self._infoLabel.setText(t)

class FinalPage(QtWidgets.QWizardPage):
  def __init__(self, parent=None):
    super(FinalPage, self).__init__(parent)
    self.setFinalPage(True)

    self.setTitle(tr_("Finish"))

    self._infoLabel = QtWidgets.QLabel()
    self._infoLabel.setWordWrap(True)

    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(self._infoLabel)
    self.setLayout(layout)

  def nextId(self):
    """@reimp @public"""
    return -1

  def initializePage(self):
    """@reimp @public"""
    self._apply()
    self._refresh()
    dprint("pass")

  def _apply(self):
    sel = self.wizard().selection()
    man = self.wizard().manager()

    tasks = []
    if sel.readerChecked != man.isReaderActivated():
      tasks.append(partial(
        man.setReaderActivated, sel.readerChecked))
    if sel.playerChecked != man.isPlayerActivated():
      tasks.append(partial(
        man.setPlayerActivated, sel.playerChecked))
    if tasks:
      self.wizard().hide()
      skthreads.runsync(partial(
        map, apply, tasks))
      self.wizard().show()

  def _refresh(self):
    man = self.wizard().manager()

    t = ""
    if man.isReaderActivated():
      t += self.tr('"Visual Novel Reader" is activated.') + '\n'
    else:
      t += self.tr('"Visual Novel Reader" is deactivated.') + '\n'

    if man.isPlayerActivated():
      t += self.tr('"Annot Player" is activated.') + '\n'
    else:
      t += self.tr('"Annot Player" is deactivated.') + '\n'

    self._infoLabel.setText(t)

# Wizard dialog
#@Q_Q
class _AppWizard:

  def __init__(self, q):
    self.manager = appman.AppManager(q)

    self.sel = AppSelection()
    self.sel.readerChecked = self.manager.isReaderActivated()
    self.sel.playerChecked = self.manager.isPlayerActivated()

class AppWizard(QtWidgets.QWizard):
  def __init__(self, parent=None):
    WINDOW_FLAGS = Qt.Window | Qt.WindowMinMaxButtonsHint
    super(AppWizard, self).__init__(parent, WINDOW_FLAGS)
    self.__d = _AppWizard(self)
    self.setStyleSheet(rc.qss('share'))

    self.setWindowIcon(rc.icon('logo-installer'))
    self.setWindowTitle(self.tr("Add or Remove Features"))
    #self.setWizardStyle(QtWidgets.QWizard.MacStyle)

    PAGEID.INTRO = self.addPage(IntroPage(self))

    PAGEID.SELECT = self.addPage(SelectPage(self))
    PAGEID.CONFIRM = self.addPage(ConfirmPage(self))

    PAGEID.FINAL = self.addPage(FinalPage(self))

    dprint("pass")

  def selection(self):
    """
    @return  AppSelection
    """
    return self.__d.sel

  def manager(self):
    """
    @return  AppManager
    """
    return self.__d.manager

  #visibleChanged = Signal(bool)

  #def setVisible(self, visible):
  #  """@reimp @public"""
  #  super(AppWizard, self).setVisible(visible)
  #  self.visibleChanged.emit(visible)

  def closeEvent(self, event):
    """@reimp @protected"""
    import main
    m = main.MainObject.instance
    if m.hasQuit() or self.currentId() == PAGEID.FINAL:
      super(AppWizard, self).closeEvent(event)
    else:
      event.setAccepted(False)
      m.confirmQuit()
    dprint("pass")

# EOF
