# coding: utf8
# monitor.py
# 10/28/2012 jichi

from PySide.QtCore import Signal, Slot, Property, QObject, QTimer, QThreadPool
from sakurakit import skos, skwin
from sakurakit.skclass import Q_Q
#from sakurakit.skqml import QmlObject
import dataman, features, gameman, netman, settings

@Q_Q
class _SystemStatus(object):

  def onLoginChanged(self):
    q = self.q
    q.loginChanged.emit(q.login)
    q.userIdChanged.emit(q.userId)
    q.userTermLevelChanged.emit(q.userTermLevel)
    q.userCommentLevelChanged.emit(q.userCommentLevel)
    q.userNameChanged.emit(q.userName)
    q.userPasswordChanged.emit(q.userPassword)

  def onProcessChanged(self):
    q = self.q
    q.gameAttachedChanged.emit(q.gameAttached)

#@QmlObject
class SystemStatus(QObject):
  def __init__(self, parent=None):
    super(SystemStatus, self).__init__(parent)
    d = self.__d = _SystemStatus(self)

    netman.manager().onlineChanged.connect(self.onlineChanged)
    gameman.manager().processChanged.connect(d.onProcessChanged)
    dataman.manager().loginChanged.connect(d.onLoginChanged)
    settings.global_().userLanguageChanged.connect(self.userLanguageChanged)
    settings.global_().userIdChanged.connect(self.userIdChanged)

  wineChanged = Signal(bool)
  wine = Property(bool,
      lambda _: features.WINE,
      notify=wineChanged)

  adminChanged = Signal(int)
  admin = Property(int,
      lambda _: 1 if features.ADMIN == True else 0 if features.ADMIN == False else -1,
      notify=adminChanged)

  onlineChanged = Signal(bool)
  online = Property(bool,
      lambda _: netman.manager().isOnline(),
      notify=onlineChanged)

  loginChanged = Signal(bool)
  login = Property(bool,
      lambda _: dataman.manager().isLogin(),
      notify=loginChanged)

  userNameChanged = Signal(unicode)
  userName = Property(unicode,
      lambda _: dataman.manager().user().name,
      notify=userNameChanged)

  userPasswordChanged = Signal(unicode)
  userPassword = Property(unicode,
      lambda _: dataman.manager().user().password,
      notify=userPasswordChanged)

  userIdChanged = Signal(int)
  userId = Property(int,
      lambda _: dataman.manager().user().id,
      notify=userIdChanged)

  userLanguageChanged = Signal(unicode)
  userLanguage = Property(unicode,
      lambda _: settings.global_().userLanguage(),
      notify=userLanguageChanged)

  userTermLevelChanged = Signal(int)
  userTermLevel= Property(int,
      lambda _: dataman.manager().user().termLevel,
      notify=userTermLevelChanged)

  userCommentLevelChanged = Signal(int)
  userCommentLevel= Property(int,
      lambda _: dataman.manager().user().commentLevel,
      notify=userCommentLevelChanged)

  gameAttachedChanged = Signal(bool)
  gameAttached = Property(bool,
      lambda _: bool(gameman.manager().currentGame()),
      notify=gameAttachedChanged)
  
  userAccessChanged = Signal(str)
  userAccess = Property(unicode,
      lambda _: dataman.manager().user().access,
      notify=userAccessChanged)

  @Slot(result=bool)
  def isKeyControlPressed(self):
    return skos.WIN and skwin.is_key_control_pressed()

  @Slot(result=bool)
  def isKeyShiftPressed(self):
    return skos.WIN and skwin.is_key_shift_pressed()

  @Slot(result=bool)
  def isKeyAltPressed(self):
    return skos.WIN and skwin.is_key_alt_pressed()

@Q_Q
class _ThreadPoolStatus(object):
  def __init__(self, q):
    self.activeThreadCount = 0
    self.refreshTimer = QTimer(q)
    self.refreshTimer.setInterval(500)
    self.refreshTimer.timeout.connect(self.refresh)
    self.refreshTimer.start()

  def refresh(self):
    value = QThreadPool.globalInstance().activeThreadCount()
    if self.activeThreadCount != value:
      self.activeThreadCount = value
      self.q.threadCountChanged.emit(value)

#@QmlObject
class ThreadPoolStatus(QObject):
  def __init__(self, parent=None):
    super(ThreadPoolStatus, self).__init__(parent)
    self.__d = _ThreadPoolStatus(self)

  threadCountChanged = Signal(int)
  threadCount = Property(int,
      lambda self: self.__d.activeThreadCount,
      notify=threadCountChanged)

# EOF
