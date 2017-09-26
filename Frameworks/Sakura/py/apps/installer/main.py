# coding: utf8
# main.py
# 12/13/2012 jichi

__all__ = 'MainObject',

from PySide.QtCore import QCoreApplication, QObject
from sakurakit import skevents
from sakurakit.skdebug import dprint, dwarn, debugmethod
import config

# MainObject private data
class _MainObject(object):
  def __init__(self):
    self.hasQuit = False # if the application has quit
    #q.destroyed.connect(self._onDestroyed)

  #def _onDestroyed(self):
  #  if self.q is MainObject.instance:
  #    MainObject.instance = None

  #def __del__(self):
  #  self._rootWindow.deleteLater() # Enforce closing root window

  ## Windows ##

  @property
  def wizard(self):
    try: return self._wizard
    except AttributeError:
      import appwiz
      ret = self._wizard = appwiz.AppWizard()
      return ret

  rootWindow = wizard

  ## Actions ##

  @debugmethod
  def quit(self):
    if self.hasQuit:
      return

    self.hasQuit = True

    dprint("schedule to kill all python instances in a few seconds")
    skevents.runlater(lambda:
        os.system("taskkill /f /IM pythonw & taskkill /f /IM python"),
        config.QT_QUIT_TIMEOUT + config.QT_THREAD_TIMEOUT)

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

class MainObject(QObject):
  """Root of most objects"""
  instance = None

  # Supposed to be top-level, no parent allowed
  def __init__(self):
    dprint('enter')
    super(MainObject, self).__init__()
    self.__d = _MainObject()
    MainObject.instance = self

    dprint('leave')

  def run(self, args):
    """Starting point for the entire app"""
    dprint("enter: args =", args)
    d = self.__d

    dprint("show root window")
    d.wizard.show()

    dprint("leave")

  ## Actions ##

  def showWizard(self):
    w = self.__d.wizard
    if w.isMaximized() and w.isMinimized():
      w.showMaximized()
    elif w.isMinimized():
      w.showNormal()
    else:
      w.show()
    w.raise_()
    dprint("pass")

  ## Show ##

  def activate(self):
    """Supposed to show and raise the main window"""
    self.showWizard()

  ## Quit ##

  def hasQuit(self):
    return self.__d.hasQuit

  def quit(self, interval=200):
    dprint("enter: interval = %i" % interval)
    d = self.__d
    if d.hasQuit:
      dprint("leave: has quit")
      return

    d.wizard.hide()

    skevents.runlater(self.__d.quit, interval)
    dprint("leave")

  def confirmQuit(self):
    from Qt5.QtWidgets import QMessageBox
    yes = QMessageBox.Yes
    no = QMessageBox.No
    sel = QMessageBox.question(self.__d.rootWindow,
        self.tr("Visual Novel Reader"),
        self.tr("Quit the wizard?"),
        yes|no, no)
    if sel == yes:
      self.quit()

# EOF
