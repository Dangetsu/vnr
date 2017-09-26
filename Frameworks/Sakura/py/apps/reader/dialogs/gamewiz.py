# coding: utf8
# gamewiz.py
# 10/14/2012 jichi

__all__ = 'GameWizard',

import os
from functools import partial
from itertools import imap
from PySide.QtCore import Qt, Signal
from PySide import QtCore, QtGui
from Qt5 import QtWidgets
from sakurakit import skevents, skpaths, skqss, skwidgets
from sakurakit.skclass import memoizedproperty
from sakurakit.skdebug import dprint
from sakurakit.skmvc import SkFilterTableController
from sakurakit.sktr import tr_
#from sakurakit.skunicode import u
from texthook import texthook
from mousehook import winpicker
from gameman import GameProfile
from mytr import my, mytr_
import config, defs, features, growl, i18n, inject, main, procutil, rc, textutil, tray

SS_RADIOBUTTONS = {
  defs.HOOK_THREAD_TYPE: "QRadioButton{color:red}",
  defs.ENGINE_THREAD_TYPE: "QRadioButton{color:blue}",
  defs.CUI_THREAD_TYPE: "QRadioButton{color:gray}",
  defs.GUI_THREAD_TYPE: "",
  defs.NULL_THREAD_TYPE: "",   # should never happen!
}

# Pages

class PAGEID:
  INTRO = -1
  FINAL = -1
  CHOOSE_MEANS = -1
  SELECT_WINDOW = -1
  SELECT_PROCESS = -1
  SELECT_FILE = -1
  CONFIRM_GAME = -1
  SYNC_GAME = -1
  SYNC_THREAD = -1
  SELECT_THREAD = -1

class IntroPage(QtWidgets.QWizardPage):
  def __init__(self, parent=None):
    super(IntroPage, self).__init__(parent)
    self.setTitle(my.tr("Add a new visual novel"))

    url = config.URL_READER_DEMO

    introEdit = QtWidgets.QTextBrowser()
    introEdit.setReadOnly(True)
    introEdit.setOpenExternalLinks(True)
    introEdit.setHtml(my.tr(
"""This wizard will help you add new visual novel step by step.
<br/><br/>

An Internet access is not indispensable, but is recommended.
With the Internet, the wizard will be able to search the online database for game settings, which will save you some time for setting things up,
<br/><br/>

Note:
On Windows Vista or Windows 7 where UAC is enabled,
if the target game is launched with <b>admin privilege</b>
(i.e., when you run the game, the Windows will black out, and ask you blablabla and "YES" or "NO" to continue),
<b>please open Visual Novel Reader as admin as well</b>!
<br/><br/>

Here's a <a href="%s">demo on youtube</a> that might be helpful.""") % url)

    self._onlineLabel = QtWidgets.QLabel()

    onlineLabel = QtWidgets.QLabel(my.tr("Current Internet status") + ": ")
    onlineLabel.setBuddy(self._onlineLabel)

    self._elevateLabel = QtWidgets.QLabel(
        tr_("Not administrator") if features.ADMIN == False else
        tr_("Administrator"))
    skqss.class_(self._elevateLabel, 'warning' if features.ADMIN == False else 'normal')
    elevateLabel = QtWidgets.QLabel(my.tr("Current privileges") + ": ")
    elevateLabel.setBuddy(self._elevateLabel)

    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(introEdit)

    row = QtWidgets.QHBoxLayout()
    row.addWidget(onlineLabel)
    row.addWidget(self._onlineLabel)
    row.addStretch()
    layout.addLayout(row)

    row = QtWidgets.QHBoxLayout()
    row.addWidget(elevateLabel)
    row.addWidget(self._elevateLabel)
    row.addStretch()
    layout.addLayout(row)

    self.setLayout(layout)

  def initializePage(self):
    """@reimp @public"""
    self._refresh()
    dprint("pass")

  def _refresh(self):
    import netman
    online = netman.manager().isOnline()
    self._onlineLabel.setText(tr_("Online") if online  else tr_("Offline"))
    skqss.class_(self._onlineLabel, 'normal' if online else 'error')

class ChooseMeansPage(QtWidgets.QWizardPage):
  def __init__(self, parent=None):
    super(ChooseMeansPage, self).__init__(parent)
    self.setTitle(my.tr("Select how to find the game"))

    introLabel = QtWidgets.QLabel(my.tr("How would you like to select the game?"))
    introLabel.setWordWrap(True)

    self._windowButton = QtWidgets.QRadioButton(my.tr("Select the window of the running game") + " (%s)" % tr_("recommended"))
    self._windowButton.setToolTip("Alt+1")
    self._windowButton.clicked.connect(self.completeChanged)

    self._processButton = QtWidgets.QRadioButton(my.tr("Select the process of the running game"))
    self._processButton.setToolTip("Alt+2")
    self._processButton.clicked.connect(self.completeChanged)

    self._fileButton = QtWidgets.QRadioButton(my.tr("Select the game executable file on the hard drive"))
    self._fileButton.setToolTip("Alt+3")
    self._fileButton.clicked.connect(self.completeChanged)

    skwidgets.shortcut("alt+1", self._windowButton.click)
    skwidgets.shortcut("alt+2", self._processButton.click)
    skwidgets.shortcut("alt+3", self._fileButton.click)

    infoLabel = QtWidgets.QLabel("\n" + my.tr(
      "By the way, you can also drag the game's exe/lnk to the SpringBoard, which is equivalent to #3 (select by file)."
    ))

    infoLabel.setWordWrap(True)

    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(introLabel)
    if not features.WINE:
      layout.addWidget(self._windowButton)
    layout.addWidget(self._processButton)
    layout.addWidget(self._fileButton)
    layout.addWidget(infoLabel)
    self.setLayout(layout)

  def initializePage(self):
    """@reimp @public"""
    dprint("pass")

  def cleanupPage(self):
    """@reimp @public"""
    dprint("pass")

  def isComplete(self):
    """@reimp @public"""
    return (self._processButton.isChecked() or
            self._fileButton.isChecked() or
            self._windowButton.isChecked())

  def nextId(self):
    """@reimp @public"""
    return (PAGEID.SELECT_PROCESS if self._processButton.isChecked() else
            PAGEID.SELECT_FILE if self._fileButton.isChecked() else
            PAGEID.SELECT_WINDOW if self._windowButton.isChecked() else
            PAGEID.CHOOSE_MEANS)

class SelectWindowPage(QtWidgets.QWizardPage):
  def __init__(self, wiz):
    super(SelectWindowPage, self).__init__(wiz)
    self.setTitle(my.tr("Select game window"))

    introLabel = QtWidgets.QLabel(my.tr(
      "Press START and  CLICK the game window, or press the STOP button to cancel."
    ))
    introLabel.setWordWrap(True)

    self._picker = winpicker.WindowPicker(self)
    self._picker.windowClicked.connect(self._onWindowClicked)
    wiz.visibleChanged.connect(self._onVisibleChanged)

    self._windowEdit = QtWidgets.QLineEdit()
    self._windowEdit.setReadOnly(True)
    self._windowEdit.setPlaceholderText(my.tr("Not found, or not a game window"))
    self._windowEdit.setToolTip(my.tr("Game window"))
    windowLabel = QtWidgets.QLabel(my.tr("Game window") + ":")
    windowLabel.setBuddy(self._windowEdit)

    self._nameEdit = QtWidgets.QLineEdit()
    self._nameEdit.setReadOnly(True)
    self._nameEdit.setPlaceholderText(tr_("Not found"))
    self._nameEdit.setToolTip(tr_("Window title"))
    nameLabel = QtWidgets.QLabel("=> " + tr_("Window title") + ":")
    nameLabel.setBuddy(self._nameEdit)

    self._startButton = QtWidgets.QPushButton("\n\n" + tr_("START") + "\n\n")
    self._startButton.clicked.connect(self._start)
    skqss.class_(self._startButton, 'btn btn-primary')

    self._stopButton = QtWidgets.QPushButton("\n\n" + tr_("STOP") + "\n\n")
    self._stopButton.clicked.connect(self._stop)
    skqss.class_(self._stopButton, 'btn btn-danger')

    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(introLabel)
    buttons = QtWidgets.QHBoxLayout()
    buttons.addWidget(self._startButton)
    buttons.addWidget(self._stopButton)
    buttons.setContentsMargins(10,10,10,10)
    layout.addLayout(buttons)

    grid = QtWidgets.QGridLayout()
    # 0
    grid.addWidget(windowLabel, 0, 0)
    grid.addWidget(self._windowEdit, 0, 1)
    # 1
    grid.addWidget(nameLabel)
    grid.addWidget(self._nameEdit)

    layout.addLayout(grid)
    self.setLayout(layout)

  def _onVisibleChanged(self, visible):
    if not visible:
      self._picker.stop()

  def _onWindowClicked(self, hwnd, title):
    dprint("enter: title = %s" % title)
    if self._stopButton.underMouse():
      self._stop()
      dprint("exit: stop")
      return
    profile = self.wizard().profile()
    valid = procutil.may_be_game_window(hwnd)

    profile.windowName = title
    if valid:
      profile.wid = hwnd
      self._stop()
      #theme.beep()
    else:
      profile.wid = 0
      self._start()
    self._refresh()
    self.completeChanged.emit()
    dprint("leave: valid = %s" % valid)

  def nextId(self):
    """@reimp @public"""
    return PAGEID.CONFIRM_GAME

  def isComplete(self):
    """@reimp @public"""
    wid = self.wizard().profile().wid
    return procutil.may_be_game_window(wid)

  def validatePage(self):
    """@reimp @public"""
    self._stop()
    return self.isComplete()

  def initializePage(self):
    """@reimp @public"""
    self._stop()
    self._refresh()
    dprint("pass")

  def cleanupPage(self):
    """@reimp @public"""
    self._stop()
    self._refresh()
    dprint("pass")

  def _start(self):
    self._startButton.setEnabled(False)
    self._stopButton.setEnabled(True)
    self._picker.start()
    qApp = QtCore.QCoreApplication.instance()
    qApp.setOverrideCursor(Qt.ForbiddenCursor)

  def _stop(self):
    self._startButton.setEnabled(True)
    self._stopButton.setEnabled(False)
    self._picker.stop()
    qApp = QtCore.QCoreApplication.instance()
    #qApp.restoreOverrideCursor()
    qApp.setOverrideCursor(Qt.ArrowCursor)

  def _refresh(self):
    valid = self.isComplete()

    t = tr_("Found") if valid else my.tr("Not found, or not a game window")
    self._windowEdit.setText(t)
    skqss.class_(self._windowEdit, 'normal' if valid else 'error')

    title = self.wizard().profile().windowName
    self._nameEdit.setText(title)
    skqss.class_(self._nameEdit, 'normal' if self.isComplete() else 'error')

class SelectProcessPage(QtWidgets.QWizardPage):
  def __init__(self, parent=None):
    super(SelectProcessPage, self).__init__(parent)
    self.setTitle(my.tr("Select game process"))

    introLabel = QtWidgets.QLabel(my.tr("Please select game process"))
    introLabel.setWordWrap(True)

    self._refreshButton = QtWidgets.QPushButton(tr_("Refresh"))
    self._refreshButton.clicked.connect(self._refresh)
    skqss.class_(self._refreshButton, 'btn btn-success')

    self._table = SkFilterTableController(self)
    self._table.currentIndexChanged.connect(self.completeChanged)

    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(introLabel)
    layout.addWidget(self._table.view())
    search = QtWidgets.QHBoxLayout()
    search.addWidget(self._table.filterEdit())
    search.addWidget(self._table.countLabel())
    search.addWidget(self._refreshButton)
    layout.addLayout(search)

    self.setLayout(layout)

  def nextId(self):
    """@reimp @public"""
    return PAGEID.CONFIRM_GAME

  def isComplete(self):
    """@reimp @public"""
    return self._table.hasSelection()

  def initializePage(self):
    """@reimp @public"""
    self._refresh()
    dprint("pass")

  def cleanupPage(self):
    """@reimp @public"""
    dprint("pass")

  _COL_NAME = 0
  _COL_PATH = 1
  _COL_COUNT = 2

  _ROLE_PID = Qt.ToolTipRole

  def _refresh(self):
    cls = SelectProcessPage

    self._table.clear()

    model = self._table.model()
    model.setColumnCount(cls._COL_COUNT)

    model.setHeaderData(cls._COL_NAME, Qt.Horizontal, tr_("Name"), Qt.DisplayRole)
    model.setHeaderData(cls._COL_PATH, Qt.Horizontal, tr_("Location"), Qt.DisplayRole)

    for p in procutil.iterprocess():
      model.insertRow(0)
      icon = rc.file_icon(p.path)
      if icon:
        model.setData(model.index(0, 0), icon, Qt.DecorationRole)
      model.setData(model.index(0, 0), p.pid, cls._ROLE_PID)

      model.setData(model.index(0, cls._COL_NAME), p.name, Qt.DisplayRole)
      model.setData(model.index(0, cls._COL_PATH), p.path, Qt.DisplayRole)

    self._table.sortByColumn(cls._COL_PATH, Qt.DescendingOrder)

  def validatePage(self):
    """@reimp @public"""
    cls = SelectProcessPage
    pid = self._table.currentData(0, cls._ROLE_PID)
    path = self._table.currentData(cls._COL_PATH)
    name = self._table.currentData(cls._COL_NAME)
    if pid and path and name:
      profile = self.wizard().profile()
      profile.clear()
      profile.pid = pid
      profile.processName = name
      profile.path = path
      return True
    return False

class SelectFilePage(QtWidgets.QWizardPage):
  def __init__(self, parent=None):
    super(SelectFilePage, self).__init__(parent)
    self.setTitle(my.tr("Select game executable"))

    introLabel = QtWidgets.QLabel(my.tr("Please select the game executable's location"))
    introLabel.setWordWrap(True)

    self._edit = QtWidgets.QLineEdit()
    self._edit.setPlaceholderText(tr_("Location"))
    self._edit.textChanged.connect(self._validateEdit)
    self._edit.textChanged.connect(self.completeChanged)

    self._browseButton = QtWidgets.QPushButton(tr_("Browse") + " ...")
    skqss.class_(self._browseButton, 'btn btn-info')
    self._browseButton.clicked.connect(self._browse)

    #self._applocButton = QtWidgets.QCheckBox(my.tr("Open in Japanese locale (0x0411) using AppLocale"))
    #self._applocButton.toggled.connect(settings.global_().setApplocEnabled)

    #self._tzButton = QtWidgets.QCheckBox(my.tr("Open in Japanese time zone (+9 Asia/Tokyo)"))
    #self._tzButton.toggled.connect(settings.global_().setTimeZoneEnabled)

    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(introLabel)

    row = QtWidgets.QHBoxLayout()
    row.addWidget(self._edit)
    row.addWidget(self._browseButton)
    layout.addLayout(row)
    #layout.addWidget(self._applocButton)
    #layout.addWidget(self._tzButton)
    self.setLayout(layout)

  def nextId(self):
    """@reimp @public"""
    return PAGEID.CONFIRM_GAME

  def isComplete(self):
    """@reimp @public"""
    f = self._edit.text().strip()
    return bool(f) and os.path.exists(f) and not os.path.isdir(f)

  def _validateEdit(self):
    skqss.class_(self._edit, 'normal' if self.isComplete() else 'error')

  def _browse(self):
    FILTERS = ("%s (*.exe *.lnk);;" "%s(*)"
        % (tr_("Executable"), tr_("All files")))

    if not hasattr(self, '_recentDir'):
      self._recentDir = skpaths.DESKTOP
    path, filter = QtWidgets.QFileDialog.getOpenFileName(
        self, my.tr("Select game executable"), self._recentDir, FILTERS)
    if path:
      self._recentDir = os.path.dirname(path)
      path = QtCore.QDir.toNativeSeparators(path)
      if path.lower().endswith('.lnk'):
        import winutil
        path = winutil.resolve_link(path)
        if not path:
          return
      self._edit.setText(path)

  def _updateEdit(self):
    self._edit.setText(self.wizard().profile().path)

  #def _updateApploc(self):
  #  self._applocButton.setChecked(settings.global_().isApplocEnabled())

  #def _updateTimeZone(self):
  #  self._tzButton.setChecked(settings.global_().isTimeZoneEnabled())

  def initializePage(self):
    """@reimp @public"""
    #self._updateApploc()
    #self._updateTimeZone()
    self._updateEdit()
    dprint("pass")

  def cleanupPage(self):
    """@reimp @public"""
    #self._updateApploc()
    #self._updateTimeZone()
    self._updateEdit()
    dprint("pass")

  def validatePage(self):
    """@reimp @public"""
    t = self._edit.text().strip()
    profile = self.wizard().profile()
    profile.clear()
    profile.path = t
    return bool(t)

class ConfirmGamePage(QtWidgets.QWizardPage):
  def __init__(self, wiz):
    super(ConfirmGamePage, self).__init__(wiz)
    self.setTitle(my.tr("Confirm the game information"))

    wiz.profile().processUpdated.connect(self._refresh)

    introLabel = QtWidgets.QLabel(my.tr("Is this the visual novel you would like to play?"))
    introLabel.setWordWrap(True)

    self._windowEdit = QtWidgets.QLineEdit()
    self._windowEdit.setReadOnly(True)
    self._windowEdit.setPlaceholderText(tr_("Not found"))
    self._windowEdit.setToolTip(my.tr("Process window"))
    windowLabel = QtWidgets.QLabel(my.tr("Active window") + ":")
    windowLabel.setBuddy(self._windowEdit)

    self._processEdit = QtWidgets.QLineEdit()
    self._processEdit.setReadOnly(True)
    self._processEdit.setPlaceholderText(tr_("Not found"))
    self._processEdit.setToolTip(my.tr("Running process"))
    processLabel = QtWidgets.QLabel(my.tr("Running process") + ":")
    processLabel.setBuddy(self._processEdit)

    self._pnameEdit = QtWidgets.QLineEdit()
    self._pnameEdit.setReadOnly(True)
    self._pnameEdit.setPlaceholderText(tr_("Not found"))
    self._pnameEdit.setToolTip(my.tr("Program name"))
    pnameLabel = QtWidgets.QLabel("=> " + my.tr("Process name") + ":")
    pnameLabel.setBuddy(self._pnameEdit)

    self._wnameEdit = QtWidgets.QLineEdit()
    self._wnameEdit.setReadOnly(True)
    self._wnameEdit.setPlaceholderText(tr_("Not found"))
    self._wnameEdit.setToolTip(tr_("Window title"))
    wnameLabel = QtWidgets.QLabel("=> " + tr_("Window title") + ":")
    wnameLabel.setBuddy(self._wnameEdit)

    self._pathEdit = QtWidgets.QLineEdit()
    self._pathEdit.setReadOnly(True)
    self._pathEdit.setPlaceholderText(tr_("Not found"))
    self._pathEdit.setToolTip(my.tr("Executable location") + ":")
    pathLabel = QtWidgets.QLabel(tr_("Location"))
    pathLabel.setBuddy(self._pathEdit)

    self._iconButton = QtWidgets.QPushButton()
    self._iconButton.setToolTip(tr_("Icon"))
    skqss.class_(self._iconButton, 'transp')

    refreshButton = QtWidgets.QPushButton(tr_("Refresh"))
    refreshButton.clicked.connect(self._updateProcess)
    skqss.class_(refreshButton, 'btn btn-success')

    clearProcessButton = QtWidgets.QPushButton(tr_("Clear"))
    clearProcessButton.clicked.connect(self._clearProcess)
    skqss.class_(clearProcessButton, 'btn btn-danger')

    clearWindowButton = QtWidgets.QPushButton(tr_("Clear"))
    clearWindowButton.clicked.connect(self._clearWindow)
    skqss.class_(clearWindowButton, 'btn btn-danger')

    grid = QtWidgets.QGridLayout()
    r=0; grid.addWidget(introLabel, r, 0, 1, 2)
    r+=1; grid.addWidget(pathLabel, r, 0)
    grid.addWidget(self._pathEdit, r, 1)
    grid.addWidget(self._iconButton, r, 2)

    r+=1; grid.addWidget(processLabel, r, 0)
    grid.addWidget(self._processEdit, r, 1)
    grid.addWidget(clearProcessButton, r, 2)

    r+=1; grid.addWidget(pnameLabel, r, 0)
    grid.addWidget(self._pnameEdit, r, 1)

    r+=1; grid.addWidget(windowLabel, r, 0)
    grid.addWidget(self._windowEdit, r, 1)

    r+=1; grid.addWidget(wnameLabel, r, 0)
    grid.addWidget(self._wnameEdit, r, 1)
    grid.addWidget(clearWindowButton, r, 2)

    r+=1; grid.addWidget(refreshButton, r, 2)
    self.setLayout(grid)

  def nextId(self):
    """@reimp @public"""
    return PAGEID.SYNC_GAME

  def _updateProcess(self):
    profile = self.wizard().profile()
    if not profile.hasProcess():
      profile.updateProcess()

  def _clearProcess(self):
    profile = self.wizard().profile()
    profile.pid = 0
    profile.processName = ""
    self._refresh()

  def _clearWindow(self):
    profile = self.wizard().profile()
    profile.wid = 0
    profile.windowName = ""
    self._refresh()

  def _refresh(self):
    profile = self.wizard().profile()

    self._pnameEdit.setText(profile.processName)
    skqss.class_(self._pnameEdit, 'normal' if self._pnameEdit.text() else 'error')

    self._wnameEdit.setText(profile.windowName)
    skqss.class_(self._wnameEdit, 'normal' if self._wnameEdit.text() else 'error')

    self._pathEdit.setText(profile.path)
    skqss.class_(self._pathEdit, 'normal' if self._pathEdit.text() else 'error')

    t = tr_("Found") if profile.wid else ""
    self._windowEdit.setText(t)
    skqss.class_(self._windowEdit, 'normal' if t else 'error')

    t = tr_("Found") if profile.pid else ""
    self._processEdit.setText(t)
    skqss.class_(self._processEdit, 'normal' if t else 'error')
    self._iconButton.setIcon(profile.icon() or QtGui.QIcon())

    self.setFocus()
    self.completeChanged.emit()

  def initializePage(self):
    """@reimp @public"""
    self._updateProcess()
    dprint("pass")

  def cleanupPage(self):
    """@reimp @public"""
    self._refresh()
    dprint("pass")

  def isComplete(self):
    """@reimp @public"""
    return self.wizard().profile().hasProcess()

  def validatePage(self):
    """@reimp @public"""
    return self.isComplete()

class SyncGamePage(QtWidgets.QWizardPage):
  def __init__(self, parent=None):
    super(SyncGamePage, self).__init__(parent)
    self.setTitle(my.tr("Analyzing the game process"))

    introLabel = QtWidgets.QLabel(my.tr("Synchronizing with visual novel") + " ...")
    introLabel.setWordWrap(True)

    self._edit = QtWidgets.QLineEdit()
    self._edit.setReadOnly(True)
    self._edit.setToolTip(tr_("Status"))

    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(introLabel)
    layout.addWidget(self._edit)
    self.setLayout(layout)

  def initializePage(self):
    """@reimp @public"""
    pid = self.wizard().profile().pid
    if pid and pid != texthook.global_().currentPid():
      ok = inject.inject_vnrhook(pid)
      dprint("attached = %s" % ok)

      #if ok:
      #  from gameengine import gameengine
      #  gameengine.inject(pid)
    self._refresh()
    dprint("pass")

  def cleanupPage(self):
    """@reimp @public"""
    self._refresh()
    dprint("pass")

  def _refresh(self):
    self.completeChanged.emit()
    ok = self.isComplete()

    skqss.class_(self._edit, 'normal' if ok else 'error')

    name = self.wizard().profile().processName
    if ok:
      t = my.tr("Successfully synchronized with game") + " => " + name
    else:
      t = my.tr("Failed to synchronize with game") + " => " + name
    self._edit.setText(t)

  def isComplete(self):
    """@reimp @public"""
    return self.wizard().profile().isTextHookAttached() # FIXME: Only texthook is supported

class SyncThreadPage(QtWidgets.QWizardPage):
  def __init__(self, wiz):
    super(SyncThreadPage, self).__init__(wiz)
    self.setTitle(my.tr("Analyzing the game threads"))

    self._complete = False
    wiz.profile().threadUpdated.connect(self._setComplete)

    introLabel = QtWidgets.QLabel(my.tr("Searching for game settings online") + " ...")
    introLabel.setWordWrap(True)

    self._edit = QtWidgets.QLineEdit()
    self._edit.setReadOnly(True)
    self._edit.setToolTip(tr_("Status"))
    self._edit.setText(tr_("Searching") + " ...")

    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(introLabel)
    layout.addWidget(self._edit)
    self.setLayout(layout)

  def initializePage(self):
    """@reimp @public"""
    self._complete = False
    profile = self.wizard().profile()
    if not profile.hasThread():
      skevents.runlater(lambda: (
        profile.updateThread(),
        profile.updateHook(),
      ), 200)
    dprint("pass")

  def cleanupPage(self):
    """@reimp @public"""
    self._setComplete()
    dprint("pass")

  def nextId(self):
    """@reimp @public"""
    return PAGEID.FINAL if self.isCommitPage() else PAGEID.SELECT_THREAD

  def isComplete(self):
    """@reimp @public"""
    return self._complete

  def _setComplete(self):
    self._complete = True
    self.completeChanged.emit()
    self.setCommitPage(self.wizard().profile().hasThread())
    self._refresh()

  def _refresh(self):
    ok = self.isCommitPage()
    skqss.class_(self._edit, 'normal' if ok else 'error')

    name = self.wizard().profile().threadName
    if ok:
      t = my.tr("Successfully synchronized with text thread") + " => " + name
    else:
      t = my.tr("Does not find this game from the online database")
    self._edit.setText(t)

  #def validatePage(self):
  #  """@reimp @public"""
  #  return True

class SelectThreadPage(QtWidgets.QWizardPage):
  class Thread:
    def __init__(self):
      self.name = ""
      self.signature = 0
      self.data = []

  def __init__(self, wiz):
    super(SelectThreadPage, self).__init__(wiz)
    self.setTitle(my.tr("Select the text thread"))
    self.setCommitPage(True)

    self._active = False

    wiz.visibleChanged.connect(self._setActive)
    wiz.visibleChanged.connect(self._clear)

    self._threads = {} # {long signature:TextThread}

    introLabel = QtWidgets.QLabel(my.tr(
      "Please play the game a little bit, and pick one text thread that has the same contents as the game text. If no text thread appears, please try editing the /H hook code for this game."
    ))
    introLabel.setWordWrap(True)

    # grid of thread sources
    self._grid = skwidgets.SkRadioButtonGrid(self, col=2)
    self._grid.currentIndexChanged.connect(self._refresh)
    self._grid.currentIndexChanged.connect(self.completeChanged)
    threadGroup = QtWidgets.QGroupBox()
    threadGroup.setLayout(self._grid.layout())
    threadGroup.setTitle(mytr_("Text threads"))

    self._encodingEdit = QtWidgets.QComboBox()
    self._encodingEdit.setEditable(False)
    self._encodingEdit.setToolTip(tr_("Text encoding"))
    self._encodingEdit.addItems(map(i18n.encoding_desc, config.ENCODINGS))
    self._encodingEdit.currentIndexChanged.connect(self._refresh)

    self._keepsSpaceButton = QtWidgets.QCheckBox(
        my.tr("Insert spaces between words") +
        " (%s: %s)" % (tr_("for example"), "Howareyou! => How are you!"))
    self._keepsSpaceButton.toggled.connect(texthook.global_().setKeepsSpace)

    self._removesRepeatButton = QtWidgets.QCheckBox(
        my.tr("Eliminate finite repetition in the text") +
        " (%s: %s)" % (tr_("for example"), "YYeess!!NoNo! => Yes!No!"))
    self._removesRepeatButton.toggled.connect(self._refresh)

    self._ignoresRepeatButton = QtWidgets.QCheckBox(
        my.tr("Ignore infinite cyclic repetition in the text") +
        " (%s: %s)" % (tr_("for example"), "YesYesYes... => Yes"))
    self._ignoresRepeatButton.toggled.connect(texthook.global_().setRemovesRepeat)

    clearButton = QtWidgets.QPushButton(tr_("Clear"))
    clearButton.clicked.connect(self._clear)
    skqss.class_(clearButton, 'btn btn-danger')

    hookPrefsButton = QtWidgets.QPushButton(my.tr("Edit /H Hook Code"))
    skqss.class_(hookPrefsButton, 'btn btn-info')
    hookPrefsButton.clicked.connect(lambda: self.hookPrefsDialog.show())

    helpButton = QtWidgets.QPushButton(tr_("Help"))
    skqss.class_(helpButton, 'btn btn-success')
    helpButton.clicked.connect(lambda: self.helpDialog.show())

    self._textEdit = QtWidgets.QPlainTextEdit()
    self._textEdit.setReadOnly(True)
    self._textEdit.setToolTip(mytr_("Game text"))
    self._textEdit.setPlainText(my.tr("No game text"))

    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(introLabel)
    row = QtWidgets.QHBoxLayout()
    row.addWidget(self._encodingEdit)
    row.addWidget(clearButton)
    row.addStretch()

    row.addWidget(hookPrefsButton)
    row.addWidget(helpButton)
    layout.addLayout(row)
    layout.addWidget(self._removesRepeatButton)
    layout.addWidget(self._ignoresRepeatButton)
    layout.addWidget(self._keepsSpaceButton)
    layout.addWidget(threadGroup)
    layout.addWidget(self._textEdit)
    self.setLayout(layout)

  @memoizedproperty
  def helpDialog(self):
    import help
    return help.TextSettingsHelpDialog(self)

  @memoizedproperty
  def hookPrefsDialog(self):
    import hookprefs
    ret = hookprefs.HookPrefsDialog(self)
    #ret.seetModel(True)
    ret.hookCodeEntered.connect(self._setHookCode)
    ret.hookCodeDeleted.connect(partial(
        self._setHookCode, ""))
    return ret

  def _setHookCode(self, hcode):
    self.wizard().profile().hook = hcode

  def _setActive(self, active):
    if self._active != active:
      th = texthook.global_()
      if active:
        th.dataReceived.connect(self._addText)
      else:
        th.dataReceived.disconnect(self._addText)
      self._active = active

  def nextId(self):
    """@reimp @public"""
    return PAGEID.FINAL

  def initializePage(self):
    """@reimp @public"""
    #self._load()
    th = texthook.global_()
    th.setWhitelistEnabled(False)
    self._ignoresRepeatButton.setChecked(th.removesRepeat())
    self._keepsSpaceButton.setChecked(th.keepsSpace())
    dprint("pass")

  def cleanupPage(self):
    """@reimp @public"""
    #self._load()
    th = texthook.global_()
    th.setWhitelistEnabled(False)
    self._ignoresRepeatButton.setChecked(th.removesRepeat())
    self._keepsSpaceButton.setChecked(th.keepsSpace())
    dprint("pass")

  def isComplete(self):
    """@reimp @public"""
    return self._grid.hasSelection()

  def validatePage(self):
    """@reimp @public"""
    profile = self.wizard().profile()
    sig = self._currentSignature()
    profile.threadSignature = sig
    if sig:
      profile.threadName = self._threads[sig].name
      profile.encoding = self._currentEncoding()
      profile.removesRepeat = self._removesRepeat()
      profile.ignoresRepeat = self._ignoresRepeat()
      profile.keepsSpace = self._keepsSpace()
    return sig != 0

  def _removesRepeat(self):
    """
    @return  bool
    """
    return self._removesRepeatButton.isChecked()

  def _ignoresRepeat(self):
    """
    @return  bool
    """
    return texthook.global_().removesRepeat()

  def _keepsSpace(self):
    """
    @return  bool
    """
    return texthook.global_().keepsSpace()

  def _transformText(self, text):
    """
    @param  text  unicode
    @return  unicode
    """
    return textutil.remove_repeat_text(text) if self._removesRepeat() else text

  def _clear(self):
    self._textEdit.clear()
    self._grid.clear()
    self._threads.clear()
    self.completeChanged.emit()

  #def _load(self):
  #  sig = self.wizard().profile().threadSignature
  #  if sig in self._threads:
  #    t = self._threads[sig]
  #    src = t.name

  def _refresh(self):
    sig = self._currentSignature()
    if not sig:
      self._textEdit.clear()
    else:
      t = self._threads[sig]
      enc = self._currentEncoding()
      f = lambda it : self._transformText(textutil.to_unicode(it, enc))
      text = "\n\n".join(imap(f, t.data))
      self._textEdit.setPlainText(text)
      self._textEdit.moveCursor(QtWidgets.QTextCursor.End)

  def _addText(self, _, data, signature, name):
    """
    @param  _  bytearray  raw data
    @param  data  bytearray rendered data
    @param  signature  long
    @param  name  str
    """
    if not self.wizard().profile().isTextHookAttached(): # FIXME: only texthook is supported
      return
    dprint("thread name = %s" % name)
    try:
      t = self._threads[signature]
    except KeyError:
      t = SelectThreadPage.Thread()
      t.signature = signature
      t.name = name
      self._threads[signature] = t

      if name == defs.HCODE_THREAD_NAME:
        n = mytr_("H-code")
      elif name in defs.CAONIMAGEBI_ENGINES:
        n = name + defs.CAONIMAGEBI_USERNAME
      elif name in defs.OK123_ENGINES:
        n = name + defs.OK123_USERNAME
      else:
        n = name
      text = "%s %x" % (n, signature)
      enc = config.guess_thread_encoding(name)
      if enc:
        text += " (%s)" % enc
      b = self._grid.addButton(text,
          tip=str(signature),
          value=signature)  # value MUST BE signature, which is used to get the current signature ID

      tt = defs.threadtype(name)
      b.setToolTip(i18n.threadtip(tt))
      b.setStyleSheet(SS_RADIOBUTTONS[tt])

    finally:
      t.data.append(data)

    if signature == self._currentSignature():
      self._refresh()

  def _currentEncoding(self):
    return config.ENCODINGS[self._encodingEdit.currentIndex()]

  def _currentSignature(self):
    sig = self._grid.currentValue() # ASSUME THE VALUE IS THE SIGNATURE
    try: return long(sig)
    except: return 0

class FinalPage(QtWidgets.QWizardPage):
  def __init__(self, parent=None):
    super(FinalPage, self).__init__(parent)
    self.setFinalPage(True)

    self.setTitle(tr_("Finish"))

    introLabel = QtWidgets.QLabel(my.tr(
      "Complete adding visual novel!"
    ))
    introLabel.setWordWrap(True)


    introEdit = QtWidgets.QTextBrowser()
    introEdit.setReadOnly(True)

    mail = config.EMAIL_HELP
    introEdit.setHtml(my.tr(
"""<span style="color:green">
You can change these settings later in <a href="#">Text Settings</a>.
</span>
<br/><br/>

<span style="color:green">
You can access the context menu by right-click the <span style="color:blue">Blue button</span> sitting on the bottom left corner.
</span>
<br/><br/>

<span style="color:brown">
<b>If the game text does not appear</b>, please try adjusting the text threads in <a href="#">Text Settings</a>,
or complain to me by email (<a href="mailto:%s">%s</a>).
</span>
<br/><br/>

It is recommended that you <b>set the Game Text Speed to maximum</b> if possible.
Especially if you would like to translate this game.""") % (mail, mail))
    introEdit.anchorClicked.connect(
        main.manager().showTextSettings)

    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(introLabel)
    layout.addWidget(introEdit)
    self.setLayout(layout)

  def nextId(self):
    """@reimp @public"""
    return -1

  def initializePage(self):
    """@reimp @public"""
    profile = self.wizard().profile()
    assert profile.hasProcess(), "profile should be valid in final page"
    #assert profile.isAttached(), "game process should be attached"
    if profile.isTextHookAttached(): # FIXME: Only texthook is supported
      profile.openGame()

    tray.log(my.tr("I am minimized here!"))
    dprint("pass")

  def cleanupPage(self):
    """@reimp @public"""
    #assert 0, "unreachabe in final page"
    dprint("pass")

# Wizard dialog

class GameWizard(QtWidgets.QWizard):
  def __init__(self, parent=None):
    WINDOW_FLAGS = Qt.Dialog|Qt.WindowMinMaxButtonsHint
    super(GameWizard, self).__init__(parent, WINDOW_FLAGS)
    self.setWindowIcon(rc.icon('window-gamewiz'))
    self.setWindowTitle(mytr_("Game Wizard"))
    #if features.WINE:
    #  self.setWizardStyle(QtWidgets.QWizard.MacStyle)

    self.__profile = GameProfile(self)

    PAGEID.INTRO = self.addPage(IntroPage(self))

    PAGEID.CHOOSE_MEANS = self.addPage(ChooseMeansPage(self))
    PAGEID.SELECT_WINDOW = self.addPage(SelectWindowPage(self))
    PAGEID.SELECT_PROCESS = self.addPage(SelectProcessPage(self))
    PAGEID.SELECT_FILE = self.addPage(SelectFilePage(self))
    PAGEID.CONFIRM_GAME = self.addPage(ConfirmGamePage(self))
    PAGEID.SYNC_GAME = self.addPage(SyncGamePage(self))
    PAGEID.SYNC_THREAD = self.addPage(SyncThreadPage(self))
    PAGEID.SELECT_THREAD = self.addPage(SelectThreadPage(self))

    PAGEID.FINAL = self.addPage(FinalPage(self))

    #self.setStartId(PAGEID.SELECT_THREAD)

    dprint("pass")

  def profile(self):
    """Return current GameProfile"""
    return self.__profile

  visibleChanged = Signal(bool)

  def sizeHint(self):
    """@reimp
    @return  QSize
    """
    return QtCore.QSize(640, 480) # increase size

  def setVisible(self, visible):
    """@reimp @public"""
    if visible and not self.isVisible():
      self.clear()
    if not visible:
      texthook.global_().setWhitelistEnabled(True)
    super(GameWizard, self).setVisible(visible)
    self.visibleChanged.emit(visible)

  def clear(self):
    self.setStartId(PAGEID.INTRO)
    self.profile().clear()
    self.restart()

  def restartWithGameLocation(self, path):
    self.profile().clear()
    self.profile().path = path
    self.setStartId(PAGEID.SELECT_FILE)
    self.restart()

# EOF
