# coding: utf8
# tray.py
# 10/8/2012 jichi

from PySide.QtCore import QCoreApplication, QObject
from Qt5.QtWidgets import QMenu, QSystemTrayIcon, QWidget
from sakurakit import skos
from sakurakit.skdebug import dprint
from sakurakit.sktr import tr_
from mytr import mytr_
import growl, main, rc

class _TrayIcon:
  def __init__(self, q):
    q_parent = q.parent()
    self._parentWidget = q_parent if isinstance(q_parent, QWidget) else None

    self._createMenu(q)

  def _createMenu(self, q):
    self._menu = menu = QMenu(self._parentWidget)

    m = main.manager()

    menu.addAction(
      mytr_("Spring Board") + " (%s)" % tr_("Double Click")
    ).triggered.connect(m.showSpringBoard)
    menu.addAction(mytr_("Game Board")).triggered.connect(m.showGameBoard)
    menu.addAction(tr_("Preferences")).triggered.connect(m.showPreferences)
    menu.addAction(mytr_("Shared Dictionary")).triggered.connect(m.showTermView)
    menu.addAction(mytr_("Test Machine Translation")).triggered.connect(m.showMachineTranslationTester)
    menu.addAction(mytr_("Text Reader")).triggered.connect(m.showTextReader)

    menu.addSeparator()
    menu.addAction(mytr_("Sync with Running Game")).triggered.connect(m.openRunningGame)
    menu.addAction(mytr_("Game Wizard")).triggered.connect(m.showGameWizard)

    #menu.addSeparator()
    #self._gamePrefsAct = menu.addAction(mytr_("Text Settings"))
    #self._gamePrefsAct.triggered.connect(m.showTextSettings)

    #self._captureAct = menu.addAction(self.q.tr("Game Screenshot"))
    #self._captureAct.triggered.connect(gameman.manager().captureWindow)

    #self._backlogAct = menu.addAction(mytr_("Backlog"))
    #self._backlogAct.triggered.connect(m.showBacklog)

    #self._liveEditAct = menu.addAction(self.q.tr("Edit Subtitles Online "))
    #self._liveEditAct.triggered.connect(m.liveEdit)

    #menu.addSeparator()

    #self._onlineAct = menu.addAction("")
    #self._onlineAct.triggered.connect(netman.manager().updateOnline)

    #menu.addSeparator()
    #menu.addAction(self.q.tr("Growl!")).triggered.connect(growl.show)
    #menu.addAction(self.q.tr("Omajinai☆")).triggered.connect(m.showOmajinai)

    menu.addSeparator()
    menu.addAction(tr_("Check for updates")).triggered.connect(m.checkUpdate)
    menu.addAction(tr_("About")).triggered.connect(m.about)
    menu.addAction(tr_("Wiki")).triggered.connect(lambda: m.openWiki('VNR'))
    menu.addAction(tr_("Credits")).triggered.connect(m.showCredits)
    menu.addSeparator()
    menu.addAction(tr_("Restart")).triggered.connect(m.restart)
    menu.addAction(tr_("Quit")).triggered.connect(m.quit)

    q.setContextMenu(menu)

  #def updateActions(self):
    #online = netman.manager().isOnline()
    #t = tr_("Online") if online else tr_("Offline")
    #t += " (%s)" % tr_("Refresh")
    #self._onlineAct.setText(t)

    #g = gameman.manager().currentGame()
    #hasGame = bool(g)
    #self._gamePrefsAct.setEnabled(hasGame)
    #self._captureAct.setEnabled(hasGame)
    #self._backlogAct.setEnabled(hasGame)
    #self._liveEditAct.setEnabled(hasGame and online)

class TrayIcon(QSystemTrayIcon):
  instance = None

  def __init__(self, parent=None):
    super(TrayIcon, self).__init__(parent)
    self.setIcon(rc.icon('logo-reader'))
    self.setToolTip(QCoreApplication.instance().applicationName())
    self.activated.connect(self.onActivated)

    self.__d = _TrayIcon(self)
    TrayIcon.instance = self

  ## Events ##

  def onActivated(self, reason):
    if reason == QSystemTrayIcon.Context:
      dprint("triggered")
      #self.__d.updateActions()
    elif reason == QSystemTrayIcon.Trigger:
      dprint("clicked")
      #if skos.MAC:
      #  self.__d.updateActions()
      growl.show()
    elif reason == QSystemTrayIcon.DoubleClick:
      dprint("double clicked")
      main.manager().activate()
    elif reason == QSystemTrayIcon.MiddleClick:
      dprint("middle clicked")

def global_(): return TrayIcon.instance

def log(text):
  g = global_()
  if g:
    title = QCoreApplication.instance().applicationName()
    g.showMessage(title, text)

def warn(text):
  g = global_()
  if g:
    title = QCoreApplication.instance().applicationName()
    g.showMessage(title, text, QSystemTrayIcon.Warning)

def error(text):
  g = global_()
  if g:
    title = QCoreApplication.instance().applicationName()
    g.showMessage(title, text, QSystemTrayIcon.Critical)

# EOF
