# coding: utf8
# main.py
# 12/13/2012 jichi

__all__ = 'MainObject',

from PySide.QtCore import QCoreApplication, QObject
from sakurakit import skevents, skos
from sakurakit.skdebug import dprint, dwarn, debugmethod
from sakurakit.skclass import Q_Q, memoizedproperty
from i18n import i18n
import config, settings

#def global_(): return MainObject.instance

class MainObject(QObject):
  """Root of most objects"""
  #instance = None

  # Supposed to be top-level, no parent allowed
  def __init__(self):
    dprint('enter')
    super(MainObject, self).__init__()
    self.__d = _MainObject(self)
    #MainObject.instance = self

    dprint('leave')

  def run(self, args):
    """Starting point for the entire app"""
    dprint("enter: args =", args)
    d = self.__d

    dprint("create managers")
    d.ttsManager
    d.translatorManager
    d.beanManager
    d.jlpManager
    d.cacheManager
    d.siteManager

    dprint("show root window")
    w = d.mainWindow

    #d.ttsManager.setParentWidget(w)

    urls = [it for it in args if not it.startswith('-')]
    args_offset = 2 if skos.WIN else 1
    urls = urls[args_offset:]
    if urls:
      w.openUrls(urls)
    elif not w.loadTabs():
      w.openDefaultPage()

    ss = settings.global_()
    width = ss.windowWidth()
    height = ss.windowHeight()
    desktop = QCoreApplication.instance().desktop()
    if width < 200 or width > desktop.width() or height < 200 or height > desktop.height():
      width, height = 1000, 600
    w.resize(width, height)

    w.show()

    dprint("leave")

  ## Quit ##

  def quit(self, interval=200):
    dprint("enter: interval = %i" % interval)
    d = self.__d
    if d.hasQuit:
      dprint("leave: has quit")
      return

    d.mainWindow.hide()

    skevents.runlater(self.__d.quit, interval)
    dprint("leave")

  def confirmQuit(self):
    from Qt5.QtWidgets import QMessageBox
    yes = QMessageBox.Yes
    no = QMessageBox.No
    sel = QMessageBox.question(self.__d.rootWindow,
        u"Website Reader",
        i18n.tr("Quit the Website Reader?"),
        yes|no, no)
    if sel == yes:
      self.quit()

  #def showAbout(self): _MainObject.showWindow(self.__d.aboutDialog)
  #def showHelp(self): _MainObject.showWindow(self.__d.helpDialog)
  #about = showAbout
  #help = showHelp

# MainObject private data
@Q_Q
class _MainObject(object):
  def __init__(self):
    self.hasQuit = False # if the application has quit
    self.widgets = [] # [QWidget]
    #q.destroyed.connect(self._onDestroyed)

  # Helpers
  @staticmethod
  def showWindow(w):
    """
    @param  w  QWidget
    """
    if w.isMaximized() and w.isMinimized():
      w.showMaximized()
    elif w.isMinimized():
      w.showNormal()
    else:
      w.show()
    w.raise_()
    #if not features.WINE:
    #  w.raise_()
    #  winutil.set_foreground_widget(w)

  ## Windows ##

  @memoizedproperty
  def mainWindow(self):
    import mainwindow
    ret = mainwindow.MainWindow()
    ret.quitRequested.connect(self.quit)
    return ret

  # Managers

  @memoizedproperty
  def beanManager(self):
    dprint("create bean manager")
    import beans
    ret = beans.manager()
    ret.setParent(self.q)
    return ret

  @memoizedproperty
  def jlpManager(self):
    dprint("create jlp manager")
    import jlpman
    ret = jlpman.manager()

    reader = settings.reader()
    ret.setRubyType(reader.rubyType())

    dic = 'unidic' if reader.isMeCabEnabled() else '' # always unidic
    ret.setMeCabDicType(dic)
    return ret

  @memoizedproperty
  def cacheManager(self):
    dprint("create cache manager")
    import cacheman
    ret = cacheman.manager()
    #ret.setParent(self.q)

    #ret.setEnabled(self.networkManager.isOnline())
    #self.networkManager.onlineChanged.connect(ret.setEnabled)

    ret.clearTemporaryFiles()
    return ret

  @memoizedproperty
  def siteManager(self):
    dprint("create site manager")
    import siteman
    return siteman.manager()

  @memoizedproperty
  def translatorManager(self):
    dprint("create translator manager")
    import trman
    ret = trman.manager()
    ret.setParent(self.q)

    ss = settings.global_()
    reader = settings.reader()

    if not reader.jbeijingLocation() and ss.isJBeijingEnabled():
      ss.setJBeijingEnabled(False)

    if not reader.fastaitLocation() and ss.isFastaitEnabled():
      ss.setFastaitEnabled(False)

    if not reader.ezTransLocation() and ss.isEzTransEnabled():
      ss.setEzTransEnabled(False)

    if not reader.dreyeLocation() and ss.isDreyeEnabled():
      ss.setDreyeEnabled(False)

    if not reader.atlasLocation() and ss.isAtlasEnabled():
      ss.setAtlasEnabled(False)

    if not reader.lecLocation() and ss.isLecEnabled():
      ss.setLecEnabled(False)

    ret.setInfoseekEnabled(ss.isInfoseekEnabled())
    ss.infoseekEnabledChanged.connect(ret.setInfoseekEnabled)

    ret.setExciteEnabled(ss.isExciteEnabled())
    ss.exciteEnabledChanged.connect(ret.setExciteEnabled)

    ret.setBingEnabled(ss.isBingEnabled())
    ss.bingEnabledChanged.connect(ret.setBingEnabled)

    ret.setGoogleEnabled(ss.isGoogleEnabled())
    ss.googleEnabledChanged.connect(ret.setGoogleEnabled)

    ret.setTransruEnabled(ss.isTransruEnabled())
    ss.transruEnabledChanged.connect(ret.setTransruEnabled)

    ret.setBaiduEnabled(ss.isBaiduEnabled())
    ss.baiduEnabledChanged.connect(ret.setBaiduEnabled)

    ret.setLecOnlineEnabled(ss.isLecOnlineEnabled())
    ss.lecOnlineEnabledChanged.connect(ret.setLecOnlineEnabled)

    #ret.setYoudaoEnabled(ss.isYoudaoEnabled())
    #ss.youdaoEnabledChanged.connect(ret.setYoudaoEnabled)

    ret.setHanVietEnabled(ss.isHanVietEnabled())
    ss.hanVietEnabledChanged.connect(ret.setHanVietEnabled)

    ret.setJBeijingEnabled(ss.isJBeijingEnabled())
    ss.jbeijingEnabledChanged.connect(ret.setJBeijingEnabled)

    ret.setFastaitEnabled(ss.isFastaitEnabled())
    ss.fastaitEnabledChanged.connect(ret.setFastaitEnabled)

    ret.setDreyeEnabled(ss.isDreyeEnabled())
    ss.dreyeEnabledChanged.connect(ret.setDreyeEnabled)

    ret.setEzTransEnabled(ss.isEzTransEnabled())
    ss.ezTransEnabledChanged.connect(ret.setEzTransEnabled)

    ret.setAtlasEnabled(ss.isAtlasEnabled())
    ss.atlasEnabledChanged.connect(ret.setAtlasEnabled)

    ret.setLecEnabled(ss.isLecEnabled())
    ss.lecEnabledChanged.connect(ret.setLecEnabled)

    #ret.setEnabled(ss.isTranslationEnabled())
    #ss.translationEnabledChanged.connect(ret.setEnabled)
    return ret

  @memoizedproperty
  def ttsManager(self):
    dprint("create tts manager")
    import ttsman
    ret = ttsman.manager()
    ret.setParent(self.q)
    #ret.setParentWidget(self.mainWindow)

    ss = settings.global_()

    if ss.isTtsEnabled() and not ret.isAvailable():
      ss.setTtsEnabled(False)

    ret.setEnabled(ss.isTtsEnabled())
    ss.ttsEnabledChanged.connect(ret.setEnabled)

    #ret.setOnline(self.networkManager.isOnline())
    #self.networkManager.onlineChanged.connect(ret.setOnline)

    reader = settings.reader()
    ret.setDefaultEngine(reader.ttsEngine())
    reader.ttsEngineChanged.connect(ret.setDefaultEngine)
    return ret

  # Dialogs

  #@memoizedproperty
  #def aboutDialog(self):
  #  import about
  #  ret = about.AboutDialog(self.mainWindow)
  #  self.widgets.append(ret)
  #  return ret

  #@memoizedproperty
  #def helpDialog(self):
  #  import help
  #  ret = help.AppHelpDialog(self.mainWindow)
  #  self.widgets.append(ret)
  #  return ret

  ## Actions ##

  @debugmethod
  def quit(self):
    if self.hasQuit:
      return

    self.hasQuit = True

    import curtheme
    curtheme.unload()

    for w in self.widgets:
      if w.isVisible():
        w.hide()

    # wait for for done or kill all threads
    from PySide.QtCore import QThreadPool
    if QThreadPool.globalInstance().activeThreadCount():
      dwarn("warning: wait for active threads")
      QThreadPool.globalInstance().waitForDone(config.QT_THREAD_TIMEOUT)
      dprint("leave qthread pool")

    dprint("send quit signal to qApp")
    qApp = QCoreApplication.instance()

    # Make sure settings.sync is the last signal conneced with aboutToQuit
    #qApp.aboutToQuit.connect(self.settings.sync)

    skevents.runlater(qApp.quit)

# EOF
