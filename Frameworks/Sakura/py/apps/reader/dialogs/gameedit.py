# coding: utf8
# GameDialog.py
# 5/15/2013 jichi

__all__ = 'GameEditorManager', 'GameEditorManagerProxy'

import os
from functools import partial
from PySide.QtCore import Qt, Slot
from PySide import QtCore
from Qt5 import QtWidgets
from sakurakit import skqss, skwidgets
from sakurakit.skclass import Q_Q, memoized, memoizedproperty
from sakurakit.skdebug import dprint
#from sakurakit.skqml import QmlObject
from sakurakit.sktr import tr_, notr_
from mytr import my, mytr_
import config, dataman, features, growl, i18n, libman, osutil, rc, settings

@Q_Q
class _GameEditor(object):
  def __init__(self, q):
    self.game = None # dataman.Game, never None when visible
    self._createUi(q)

  def _createUi(self, q):
    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(self.infoGroup)
    layout.addWidget(self.locationGroup)
    layout.addWidget(self.textGroup)
    layout.addWidget(self.hookGroup)
    layout.addWidget(self.embedGroup)
    if not features.WINE:
      layout.addWidget(self.loaderGroup)
    layout.addWidget(self.timeZoneGroup)
    q.setCentralWidget(skwidgets.SkLayoutWidget(layout))

  def refresh(self):
    self.q.setWindowIcon(self.game.icon())
    self._loadName()
    self._loadHook()
    self._loadText()
    self._loadEmbedSettings()
    self._loadLocation()
    self._loadLoader()
    self._loadTimeZone()

    # Enabled
    self.localeEmulatorButton.setEnabled(libman.localeEmulator().exists())
    self.ntleasButton.setEnabled(libman.ntleas().exists())
    self.localeSwitchButton.setEnabled(features.ADMIN != False)

  def showWarning(self, text):
    bar = self.q.statusBar()
    skqss.class_(bar, 'warning')
    bar.showMessage(text)

  def showMessage(self, text):
    bar = self.q.statusBar()
    skqss.class_(bar, 'message')
    bar.showMessage(text)

  ## Basic information ##

  @memoizedproperty
  def infoGroup(self):
    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(self.nameEdit)
    ret = QtWidgets.QGroupBox(my.tr("Dashboard display name"))
    ret.setLayout(layout)
    return ret

  @memoizedproperty
  def nameEdit(self):
    ret = QtWidgets.QLineEdit()
    skqss.class_(ret, 'normal')
    ret.setPlaceholderText(tr_("Not specified"))
    ret.setToolTip(my.tr("The game name displayed on the Spring Board"))
    ret.setStatusTip(ret.toolTip())
    ret.textChanged.connect(self._saveName)
    return ret

  def _loadName(self):
    name = self.game.name
    self.nameEdit.setText(name)
    title = "%s - %s" % (name, mytr_("Game Properties"))
    self.q.setWindowTitle(title)

  def _saveName(self):
    name = self.nameEdit.text().strip()
    dataman.manager().setGameName(name, md5=self.game.md5)
    if name:
      title = "%s - %s" % (name, mytr_("Game Properties"))
      self.q.setWindowTitle(title)
    else:
      self._loadName()

  ## Hook ##

  @memoizedproperty
  def hookGroup(self):
    layout = QtWidgets.QVBoxLayout()

    row = QtWidgets.QHBoxLayout()
    row.addWidget(self.hookEdit)
    row.addWidget(self.hookButton)
    layout.addLayout(row)

    label = QtWidgets.QLabel(my.tr(
      "You can edit hook code in Text Settings after the game is launched."
    ))
    label.setWordWrap(True)
    layout.addWidget(label)

    ret = QtWidgets.QGroupBox("%s (%s)" % (my.tr("Game-specific hook code"), tr_("read-only")))
    ret.setLayout(layout)
    return ret

  @memoizedproperty
  def hookEdit(self):
    ret = QtWidgets.QLineEdit()
    skqss.class_(ret, 'readonly')
    ret.setReadOnly(True)
    ret.setPlaceholderText(tr_("Not specified"))
    ret.setToolTip(tr_("Read-only"))
    ret.setStatusTip(ret.toolTip())
    #ret.setStyleSheet("QLineEdit.disabled { text-decoration:line-through }")
    #ret.textChanged.connect(self._saveHook)
    return ret

  @memoizedproperty
  def hookButton(self):
    ret = QtWidgets.QCheckBox(tr_("Enable"))
    ret.toggled.connect(self._saveHookButton)
    return ret

  def _saveHookButton(self):
    enabled = self.hookButton.isChecked()
    if enabled != (not self.game.hookDisabled):
      dataman.manager().setGameHookEnabled(enabled, md5=self.game.md5)
      self._loadHook()

  def _loadHook(self):
    hook = self.game.hook
    hookEnabled = not self.game.hookDisabled
    self.hookEdit.setText(hook or tr_("Not specified"))
    self.hookEdit.setEnabled(hookEnabled or not hook)
    self.hookButton.setEnabled(bool(hook))
    self.hookButton.setChecked(hookEnabled)

  ## Game agent ##

  @memoizedproperty
  def embedGroup(self):
    layout = QtWidgets.QVBoxLayout()

    row = QtWidgets.QHBoxLayout()
    row.addWidget(self.embedEnableButton)
    layout.addLayout(row)

    ret = QtWidgets.QGroupBox(mytr_("Embed translation"))
    ret.setLayout(layout)

    ss = settings.global_()
    ret.setEnabled(ss.isGameAgentEnabled())
    ss.gameAgentEnabledChanged.connect(ret.setEnabled)
    return ret

  @memoizedproperty
  def embedEnableButton(self):
    ret = QtWidgets.QCheckBox("%s (%s)" % (
        my.tr("Allow embedding translation when possible"),
        tr_("default")))
    ret.clicked.connect(self._saveEmbedSettings)
    return ret

  def _loadEmbedSettings(self):
    self.embedEnableButton.setChecked(not self.game.gameAgentDisabled)

  def _saveEmbedSettings(self):
    t = not self.embedEnableButton.isChecked()
    if t != self.game.gameAgentDisabled:
      dataman.manager().setGameAgentDisabled(t, md5=self.game.md5)

  ## Text ##

  @memoizedproperty
  def textGroup(self):
    layout = QtWidgets.QVBoxLayout()

    row = QtWidgets.QHBoxLayout()
    row.addWidget(QtWidgets.QLabel(tr_("Language") + ":"))
    row.addWidget(self.languageEdit)
    row.addStretch()
    row.addWidget(QtWidgets.QLabel(tr_("Encoding") + ":"))
    row.addWidget(self.encodingEdit)
    layout.addLayout(row)

    ret = QtWidgets.QGroupBox(mytr_("Game language"))
    ret.setLayout(layout)
    return ret

  @memoizedproperty
  def encodingEdit(self):
    ret = QtWidgets.QLineEdit()
    skqss.class_(ret, 'readonly')
    ret.setReadOnly(True)
    ret.setPlaceholderText(tr_("Not specified"))
    ret.setToolTip(tr_("Read-only"))
    ret.setStatusTip(ret.toolTip())
    return ret

  @memoizedproperty
  def languageEdit(self):
    ret = QtWidgets.QComboBox()
    ret.setEditable(False)
    ret.addItems(map(i18n.language_name, config.LANGUAGES))
    ret.setMaxVisibleItems(ret.count())
    ret.currentIndexChanged.connect(self._saveLanguage)
    return ret

  def _loadLanguage(self):
    lang = self.game.language
    try: langIndex = config.LANGUAGES.index(lang)
    except ValueError: langIndex = 0 # 'default'
    w = self.languageEdit
    w.setCurrentIndex(langIndex)
    if lang == 'ja':
      skqss.removeclass(w, 'warning')
    else:
      skqss.addclass(w, 'warning')

  def _saveLanguage(self):
    w = self.languageEdit
    index = w.currentIndex()
    lang = config.LANGUAGES[index]
    if lang != self.game.language:
      dataman.manager().setGameLanguage(lang, md5=self.game.md5)
    if lang == 'ja':
      skqss.removeclass(w, 'warning')
    else:
      skqss.addclass(w, 'warning')

  def _loadText(self):
    self._loadLanguage()

    # Load encoding
    g = self.game
    self.encodingEdit.setText(i18n.encoding_desc(g.encoding))
    #self.languageEdit.setText(i18n.language_name2(g.language))
    if g.encoding in ('shift-jis', 'utf-16'):
      skqss.removeclass(self.encodingEdit, 'warning')
    else:
      skqss.addclass(self.encodingEdit, 'warning')

  ## Location ##

  @memoizedproperty
  def locationGroup(self):
    introLabel = QtWidgets.QLabel(my.tr(
"""You can specify a different executable to launch the game process.
By default it is the same as the executable of the game process."""))
    introLabel.setWordWrap(True)

    #launchLabel = QtWidgets.QLabel(mytr_("Launcher"))
    #launchLabel.setBuddy(self.launchEdit)

    browseLaunchButton = QtWidgets.QPushButton(tr_("Browse"))
    browseLaunchButton.clicked.connect(self._browseLaunchPath)
    skqss.class_(browseLaunchButton, 'btn btn-info')

    layout = QtWidgets.QVBoxLayout()
    launchRow = QtWidgets.QHBoxLayout()
    #launchRow.addWidget(launchLabel)
    launchRow.addWidget(self.launchEdit)
    launchRow.addWidget(browseLaunchButton)
    launchRow.addWidget(self.resetLaunchButton)
    layout.addLayout(launchRow)
    layout.addWidget(introLabel)

    ret = QtWidgets.QGroupBox(my.tr("Alternative launcher location"))
    ret.setLayout(layout)
    return ret

  @memoizedproperty
  def launchEdit(self):
    ret = QtWidgets.QLineEdit()
    ret.setReadOnly(True)
    ret.setPlaceholderText(my.tr("No game path"))
    ret.setToolTip(my.tr("Game launcher location"))
    ret.setStatusTip(ret.toolTip())
    ret.textChanged.connect(self._verifyLaunchEdit)
    ret.textChanged.connect(lambda text:
        self.resetLaunchButton.setEnabled(
          osutil.normalize_path(text) != osutil.normalize_path(self.game.path)))
    return ret

  @memoizedproperty
  def resetLaunchButton(self):
    ret = QtWidgets.QPushButton(tr_("Reset"))
    ret.clicked.connect(self._resetLaunchPath)
    skqss.class_(ret, 'btn btn-danger')
    return ret

  def _resetLaunchPath(self):
    self.launchEdit.setText(self.game.path)

  def _browseLaunchPath(self):
    #FILTERS = ("%s(*.exe);;"     "%s(*.lnk);;"       "%s(*)"
    #    % (tr_("Executables"), tr_("Shortcuts"), tr_("All files")))
    FILTERS = "%s (*.exe)" % tr_("Executables")

    path = self.launchEdit.text().strip()
    cwd = os.path.dirname(path) if path else ""
    if not cwd or not os.path.exists(cwd):
      path = self.game.launchPath or self.game.path
      if path:
        cwd = os.path.dirname(path)
      if not os.path.exists(cwd):
        cwd = ""
    path, filter = QtWidgets.QFileDialog.getOpenFileName(
        self.q, my.tr("Select Executable"), cwd, FILTERS)
    if path:
      path = QtCore.QDir.toNativeSeparators(path)
      self.launchEdit.setText(path)
      #self._verifyLaunchEdit()

  def _verifyLaunchEdit(self):
    path = self.launchEdit.text()
    ok = bool(path) and os.path.exists(path)
    skqss.class_(self.launchEdit, 'normal' if ok else 'error')
    if ok:
      self.showMessage(my.tr("Find game launch file"))
      self._saveLaunchPath()
    else:
      self.showWarning(my.tr("Game launch file does not exist"))

  def _loadLaunchPath(self):
    path = self.game.launchPath or self.game.path or ""
    if path:
      path = QtCore.QDir.toNativeSeparators(path)
    self.launchEdit.setText(path)
    self._verifyLaunchEdit()

  def _saveLaunchPath(self):
    g = self.game
    path = self.launchEdit.text().strip()
    if not path or not os.path.exists(path):
      self.showWarning(my.tr("Game launch file does not exist"))
      return
    if osutil.normalize_path(path) == osutil.normalize_path(g.launchPath):
      return
    if osutil.normalize_path(path) == osutil.normalize_path(g.path):
      path = ""
    else:
      path = QtCore.QDir.toNativeSeparators(path)
    if path != g.launchPath:
      dprint("game launch path changed")
      self.showMessage(my.tr("Game launch path saved"))
      dataman.manager().setGameLaunchPath(path, g.md5)

  _loadLocation =_loadLaunchPath
  _saveLocation = _saveLaunchPath

  ## Loader ##

  @memoizedproperty
  def loaderGroup(self):
    layout = QtWidgets.QVBoxLayout()

    row = QtWidgets.QHBoxLayout()
    row.addWidget(QtWidgets.QLabel(tr_("Locale") + ":"))
    row.addWidget(self.launchLanguageEdit)
    row.addStretch()
    layout.addLayout(row)

    layout.addWidget(self.defaultLoaderButton)
    layout.addWidget(self.disableLoaderButton)
    layout.addWidget(self.applocButton)
    layout.addWidget(self.localeEmulatorButton)
    layout.addWidget(self.ntleasButton)
    layout.addWidget(self.ntleaButton)
    layout.addWidget(self.localeSwitchButton)

    ret = QtWidgets.QGroupBox(my.tr("Preferred game loader"))
    ret.setLayout(layout)
    return ret

  @memoizedproperty
  def defaultLoaderButton(self):
    ret = QtWidgets.QRadioButton("%s (%s)" % (
        my.tr("Launch the game with DEFAULT loader in Preferences"),
        tr_("default")))
    ret.toggled.connect(self._saveLoader)
    return ret

  @memoizedproperty
  def disableLoaderButton(self):
    ret = QtWidgets.QRadioButton("%s (%s)" % (
         my.tr("Launch the game WITHOUT loader"),
         my.tr("for Windows with Japanese locale")))
    ret.toggled.connect(self._saveLoader)
    return ret

  @memoizedproperty
  def applocButton(self):
    ret = QtWidgets.QRadioButton("%s (%s)" % (
        my.tr("Use {0} to change game locale").format(notr_("AppLocale")),
        tr_("download")))
    ret.toggled.connect(self._saveLoader)
    return ret

  @memoizedproperty
  def ntleaButton(self):
    ret = QtWidgets.QRadioButton(
      my.tr("Use {0} to change game locale").format(notr_("NTLEA")))
    ret.toggled.connect(self._saveLoader)
    return ret

  @memoizedproperty
  def localeSwitchButton(self):
    ret = QtWidgets.QRadioButton("%s (%s)" % (
        my.tr("Use {0} to change game locale").format(notr_("LocaleSwitch")),
        my.tr("need admin priv")))
    if features.ADMIN == False:
      skqss.class_(ret, 'warning')
    ret.toggled.connect(self._saveLoader)
    return ret

  @memoizedproperty
  def localeEmulatorButton(self):
    ret = QtWidgets.QRadioButton("%s (%s)" % (
        my.tr("Use {0} to change game locale").format(notr_("Locale Emulator")),
        tr_("download")))
        #tr_("recommended")))
    #if features.ADMIN == False:
    #  skqss.class_(ret, 'warning')
    ret.toggled.connect(self._saveLoader)
    return ret

  @memoizedproperty
  def ntleasButton(self):
    ret = QtWidgets.QRadioButton("%s (%s)" % (
        my.tr("Use {0} to change game locale").format(notr_("Ntleas")),
        tr_("download")))
        #tr_("recommended")))
    #if features.ADMIN == False:
    #  skqss.class_(ret, 'warning')
    ret.toggled.connect(self._saveLoader)
    return ret

  @memoizedproperty
  def launchLanguageEdit(self):
    ret = QtWidgets.QComboBox()
    ret.setEditable(False)
    ret.addItem(tr_("Default"))
    ret.addItems(map(i18n.language_name, config.LANGUAGES))
    ret.setMaxVisibleItems(ret.count())
    ret.currentIndexChanged.connect(self._saveLaunchLanguage)
    return ret

  def _loadLaunchLanguage(self):
    lang = self.game.launchLanguage
    try: langIndex = config.LANGUAGES.index(lang) + 1
    except ValueError: langIndex = 0 # 'default'
    w = self.launchLanguageEdit
    w.setCurrentIndex(langIndex)
    if lang in ('', 'ja'):
      skqss.removeclass(w, 'warning')
    else:
      skqss.addclass(w, 'warning')

  def _saveLaunchLanguage(self):
    w = self.launchLanguageEdit
    index = w.currentIndex()
    if not index:
      lang = ''
    else:
      lang = config.LANGUAGES[index - 1]
    if lang != self.game.launchLanguage:
      dataman.manager().setGameLaunchLanguage(lang, md5=self.game.md5)
    if lang in ('', 'ja'):
      skqss.removeclass(w, 'warning')
    else:
      skqss.addclass(w, 'warning')

  def _loadLoader(self):
    loader = self.game.loader
    b = (self.disableLoaderButton if loader == 'none' else
         self.applocButton if loader == 'apploc' else
         self.ntleaButton if loader == 'ntlea' else
         self.ntleasButton if loader == 'ntleas' else
         self.localeSwitchButton if loader == 'lsc' else
         self.localeEmulatorButton if loader == 'le' else
         self.defaultLoaderButton)
    if not b.isChecked():
      b.setChecked(True)

    self._loadLaunchLanguage()

    t = b is self.disableLoaderButton or b is self.localeEmulatorButton
    self.launchLanguageEdit.setEnabled(not t)

  def _saveLoader(self):
    loader = (
      'none' if self.disableLoaderButton.isChecked() else
      'apploc' if self.applocButton.isChecked() else
      'ntlea' if self.ntleaButton.isChecked() else
      'ntleas' if self.ntleasButton.isChecked() else
      'lsc' if self.localeSwitchButton.isChecked() else
      'le' if self.localeEmulatorButton.isChecked() else
      '')
    #if loader != self.game.loader: # Not needed since they are connected with toggled signal
    dataman.manager().setGameLoader(loader, md5=self.game.md5)

    self.launchLanguageEdit.setEnabled(loader not in ('none', 'le'))

  ## Time zone ##

  @memoizedproperty
  def timeZoneGroup(self):
    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(self.defaultTimeZoneButton)
    layout.addWidget(self.disableTimeZoneButton)
    layout.addWidget(self.enableTimeZoneButton)

    ret = QtWidgets.QGroupBox(my.tr("Preferred time zone"))
    ret.setLayout(layout)
    return ret

  @memoizedproperty
  def defaultTimeZoneButton(self):
    ret = QtWidgets.QRadioButton("%s (%s)" % (
        my.tr("Launch the game under DEFAULT time zone in Preferences"),
        tr_("default")))
    ret.toggled.connect(self._saveTimeZone)
    return ret

  @memoizedproperty
  def enableTimeZoneButton(self):
    ret = QtWidgets.QRadioButton("%s (%s)" % (
        my.tr("Launch the game in Japan time"),
        my.tr("DO change time zone")))
    ret.toggled.connect(self._saveTimeZone)
    return ret

  @memoizedproperty
  def disableTimeZoneButton(self):
    ret = QtWidgets.QRadioButton("%s (%s)" % (
        my.tr("Launch the game in current time"),
        my.tr("do NOT change time zone")))
    ret.toggled.connect(self._saveTimeZone)
    return ret

  def _loadTimeZone(self):
    v = self.game.timeZoneEnabled
    b = (self.enableTimeZoneButton if v == True else
         self.disableTimeZoneButton if v == True else
         self.defaultTimeZoneButton)
    if not b.isChecked():
      b.setChecked(True)

  def _saveTimeZone(self):
    v = (
        True if self.enableTimeZoneButton.isChecked() else
        False if self.disableTimeZoneButton.isChecked() else
        None)
    dataman.manager().setGameTimeZone(v, md5=self.game.md5)

class GameEditor(QtWidgets.QMainWindow):
  def __init__(self, parent=None):
    WINDOW_FLAGS = Qt.Dialog|Qt.WindowMinMaxButtonsHint
    super(GameEditor, self).__init__(parent, WINDOW_FLAGS)
    skqss.class_(self, 'texture')
    #self.setWindowTitle(self.tr("Edit Game Properties"))
    self.__d = _GameEditor(self)
    self.setMinimumWidth(350)

  def game(self): return self.__d.game

  def setGame(self, g):
    self.__d.game = g
    if self.isVisible():
      self.__d.refresh()

  def setVisible(self, value):
    """@reimp @public"""
    if value and not self.isVisible() and self.__d.game:
      self.__d.refresh()
    super(GameEditor, self).setVisible(value)

class _GameEditorManager:
  def __init__(self):
    self.dialogs = []

  @staticmethod
  def _createDialog():
    import windows
    parent = windows.normal()
    ret = GameEditor(parent)
    #ret.resize(400, 200)
    return ret

  def getDialog(self):
    for w in self.dialogs:
      if not w.isVisible():
        return w
    ret = self._createDialog()
    self.dialogs.append(ret)
    return ret

  def findDialog(self, id=None, md5=None):
    for w in self.dialogs:
      if w.game().md5 == md5 or w.game().id == id:
        return w

class GameEditorManager:
  def __init__(self):
    self.__d = _GameEditorManager()

    from PySide.QtCore import QCoreApplication
    qApp = QCoreApplication.instance()
    qApp.aboutToQuit.connect(self.hide)

    #import dataman
    #dataman.manager().loginChanged.connect(lambda name: name or self.hide())

    #import netman
    #netman.manager().onlineChanged.connect(lambda t: t or self.hide())

  def clear(self):
    self.hide()

  def isVisible(self):
    if self.__d.dialogs:
      for w in self.__d.dialogs:
        if w.isVisible():
          return True
    return False

  def hide(self):
    if self.__d.dialogs:
      for w in self.__d.dialogs:
        if w.isVisible():
          w.hide()

  def showGame(self, game=None, id=None, md5=None):
    """
    @param  game  dataman.Game
    @param  id  long
    @param  md5  unicode
    """
    if not game and (md5 or id):
      game = dataman.manager().queryGame(id=id, md5=md5)
    if not game:
      growl.warn(my.tr("Game is not found. Did you delete it?")) # This should seldom happen
    else:
      w = self.__d.findDialog(id=id, md5=md5)
      if not w:
        w = self.__d.getDialog()
      w.setGame(game)
      w.show()
      w.raise_()

@memoized
def manager(): return GameEditorManager()

#@QmlObject
class GameEditorManagerProxy(QtCore.QObject):
  def __init__(self, parent=None):
    super(GameEditorManagerProxy, self).__init__(parent)

  @Slot(unicode)
  def showGame(self, md5):
    manager().showGame(md5=md5)

# EOF
