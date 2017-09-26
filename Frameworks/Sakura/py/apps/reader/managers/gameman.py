# coding: utf8
# gameman.py
# 10/14/2012 jichi

import operator, os, re
from functools import partial
from PySide import QtCore
from PySide.QtCore import Signal, Slot, Property, Qt
from sakurakit import skcursor, skdatetime, skevents, skos, skpaths, skwin
from sakurakit.skclass import Q_Q, memoized
from sakurakit.skdebug import dprint, dwarn
#from sakurakit.skqml import QmlPersistentObject
from sakurakit.sktr import tr_, notr_
from sakurakit.skunicode import sjis_encodable, u_sjis
from sakurakit.skwinobj import SkWindowObject #, SkTaskBarObject
from texthook import texthook
from mytr import my
import config, dataman, defs, displayutil, features, gameagent, growl, hashutil, inject, netman, osutil, procutil, rc, rpcman, settings, textman, textutil, winutil

PROGRAMFILES = QtCore.QDir.fromNativeSeparators(skpaths.PROGRAMFILES)
PROGRAMFILES_RE = re.compile(re.escape(PROGRAMFILES), re.IGNORECASE)

__re_folder = re.compile(r'[0-9]+$')
def _good_folder_name(path):
  """
  @param  path  unicode
  @return  bool
  """
  return bool(path) and not __re_folder.match(path)

def get_process_by_path(path):
  """
  @param  path  unicode or None
  @return  Process or None
  """
  proc = procutil.get_process_by_path(path)
  if proc:
    return proc
  md5 = hashutil.md5sum(osutil.normalize_path(path))
  if md5:
    return procutil.get_process_by_md5(md5)

## Game window ##

class _GameWindowProxy:
  def __init__(self, q):
    self.displayAspect = False
    self.clearStretched()
    self.clearDisplayStretched()
    q.visibleChanged.connect(self._onVisibleChanged)
    q.fullScreenChanged.connect(self._onFullScreenChanged)
    q.minimizedChanged.connect(self._onMinimizedChanged)

    def _disableStretch():
      if self.stretched:
        self.clearStretched()
        q.stretchedChanged.emit(False)
    q.winIdChanged.connect(_disableStretch)

    def _disableDisplayStretch():
      if self.displayStretched:
        if self.displayResolution:
          skwin.set_display_resolution(self.displayResolution)
        self.clearDisplayStretched()
        q.displayStretchedChanged.emit(False)
    q.winIdChanged.connect(_disableDisplayStretch)

    q.winIdChanged.connect(lambda: q.setKeepsDisplayRatio(False))

  def clearDisplayStretched(self):
    self.displayStretched = False
    self.displayResolution = None # (int w, int h)
    self.displaySize = None # (int w, int h)
    #self.displayMenu = None # HMENU or None

  def clearStretched(self):
    self.stretched = False
    self.stretchedSize = None # (int w, int h) or None
    self.stretchedMenu = None # HMENU or None

  def _onMinimizedChanged(self, t):
    growl.msg(my.tr("Game window is minimized") if t else
              my.tr("Game window is restored"))
    if not t: # restored
      refresh = manager().refreshWindow
      refresh()
      skevents.runlater(refresh, 500)

  def _onVisibleChanged(self, visible):
    growl.msg(my.tr("Found game window") if visible else
              my.tr("Game window closed"))
    if not visible:
      refresh = manager().refreshWindow
      skevents.runlater(refresh, 500)
      skevents.runlater(refresh, 2000)

  def _onFullScreenChanged(self, t):
    t = my.tr("Enter full screen") if t else my.tr("Leave full screen")
    skevents.runlater(partial(
        growl.msg, t),
        1500) # delay 1.5 seconds to avoid crashing

  #def _onStretchedChanged(self, t):
  #  t = my.tr("Stretch game window") if t else my.tr("Leave full screen")
  #  skevents.runlater(partial(
  #      growl.msg, t),
  #      1000) # delay 1 second to avoid crashing

#@QmlObject
class GameWindowProxy(SkWindowObject):
  """Used as delegate of kagami/centralarea.qml"""

  def __init__(self, parent=None):
    super(GameWindowProxy, self).__init__(parent)
    self.__d = _GameWindowProxy(self)
    manager().windowChanged.connect(self.setWinId)

    import windows
    w = windows.top()
    self.fullScreenChanged.connect(w.setStaysOnTop)
    self.fullScreenChanged.connect(w.bringWindowToTop)
    self.minimizedChanged.connect(lambda t: t or w.bringWindowToTop())

    # Restore stretched window on exit.
    qApp = QtCore.QCoreApplication.instance()
    qApp.aboutToQuit.connect(partial(self.setDisplayStretched, False))
    qApp.aboutToQuit.connect(partial(self.setStretched, False))

  @Slot(result=float)
  def getZoomFactor(self):
    """
    @return  float (0.0, 1.0]
    """
    if not self.winId:
      return 1.0
    import sysinfo
    r0 = self.__d.displayResolution or sysinfo.DISPLAY_RESOLUTION
    if r0 == (0,0):
      return 1.0
    r = skwin.get_display_resolution()
    return max(r[0]/float(r0[0]), r[1]/float(r0[1])) if r0 > r else 1.0

  def isDisplayStretched(self): return self.__d.displayStretched
  def setDisplayStretched(self, v):
    d = self.__d
    if v != d.displayStretched:
      d.displayStretched = v
      hwnd = self.winId
      size = None
      if v: # Stretch
        r = d.displayResolution = skwin.get_display_resolution()
        if hwnd:
          size = d.displaySize = skwin.get_window_size(hwnd)
          #menu = d.displayMenu = skwin.get_window_menu(hwnd)
      else:
        r = d.displayResolution
        #menu = d.displayMenu
      if not size:
        size = d.displaySize
      dprint("pass: stretched = %s" % v)
      if hwnd:
        displayutil.stretch_display(hwnd, v, size=size, resolution=r, aspect=d.displayAspect)
      else:
        skwin.set_display_resolution(r)
        d.clearDisplayStretched()
      self.displayStretchedChanged.emit(v)
  displayStretchedChanged = Signal(bool)
  displayStretched = Property(bool,
      isDisplayStretched,
      setDisplayStretched,
      notify=displayStretchedChanged)

  def keepsDisplayRatio(self): return self.__d.displayAspect
  def setKeepsDisplayRatio(self, v):
    d = self.__d
    if v != d.displayAspect:
      d.displayAspect = v
      self.keepsDisplayRatioChanged.emit(v)
  keepsDisplayRatioChanged = Signal(bool)
  keepsDisplayRatio = Property(bool,
      keepsDisplayRatio,
      setKeepsDisplayRatio,
      notify=keepsDisplayRatioChanged)

  def isStretched(self): return self.__d.stretched
  def setStretched(self, v):
    d = self.__d
    if v != d.stretched:
      d.stretched = v
      hwnd = self.winId
      if hwnd:
        if v: # Stretch
          size = d.stretchedSize = skwin.get_window_size(hwnd)
          # Title bar heigh: 26 pixel
          # Menu bar heigh: 20 pixel
          #h1 -= 25 #
          menu = d.stretchedMenu = skwin.get_window_menu(hwnd)
        else:
          size = d.stretchedSize
          menu = d.stretchedMenu
        dprint("pass: stretched = %s" % v)
        displayutil.stretch_window(hwnd, v, size=size, menu=menu)
      else:
        d.clearStretched()
      self.stretchedChanged.emit(v)
  stretchedChanged = Signal(bool)
  stretched = Property(bool,
      isStretched,
      setStretched,
      notify=stretchedChanged)

#@QmlObject
#class TaskBarProxy(SkTaskBarObject):
#  def __init__(self, parent=None):
#    super(TaskBarProxy, self).__init__(parent)
#    self.setRefreshInterval(5000)
#    self.startRefresh()

# Only partially implemented
class _TaskBarProxy:
  def __init__(self):
    if not skos.WIN:
      self.visible = False
      self.height = 0
      return

    self.hwnd = skwin.get_taskbar_window()
    self.visible = skwin.is_taskbar_visible(self.hwnd)

    left, top, right, bottom = skwin.get_window_rect(self.hwnd)
    width = right - left
    height = bottom - top
    self.height = height if height < width and height < top + 4 else 0

    self._autoHide = skwin.is_taskbar_autohide()
    qApp = QtCore.QCoreApplication.instance()
    qApp.aboutToQuit.connect(self._restoreAutoHide)

  def _restoreAutoHide(self):
    if self._autoHide != skwin.is_taskbar_autohide():
      skwin.set_taskbar_autohide(self._autoHide)

#@QmlObject
class TaskBarProxy(QtCore.QObject):
  def __init__(self, parent=None):
    """Set task bar height iff it is in the bottom of the screen"""
    super(TaskBarProxy, self).__init__(parent)
    self.__d = _TaskBarProxy()

  heightChanged = Signal(int)
  height = Property(int,
      lambda self: self.__d.height,
      notify=heightChanged)

  visibleChanged = Signal(bool)
  visible = Property(bool,
      lambda self: self.__d.visible,
      notify=visibleChanged)

  def setAutoHide(self, t):
    #if t != skwin.is_taskbar_autohide():
    skwin.set_taskbar_autohide(t)
    self.autoHideChanged.emit(t)
  autoHideChanged = Signal(bool)
  autoHide = Property(bool,
      lambda _: skwin.is_taskbar_autohide(),
      setAutoHide,
      notify=autoHideChanged)

## Game data types ##

class _GameProfile: pass
class GameProfile(QtCore.QObject):

  def __init__(self, parent=None,
      wid=0, pid=0, path="", launchPath="", processName="", windowName="",
      hook="", deletedHook="", encoding="", threadName="", threadSignature=0,
      linkName="", folderName="", brandName="",
      loader="", language='ja', launchLanguage="",
      removesRepeat=False, ignoresRepeat=False, keepsSpace=False, threadKept=False,
      timeZoneEnabled=None):
    super(GameProfile, self).__init__(parent)
    d = self.__d = _GameProfile()
    d.locked = False

    # Process
    self.wid = wid  # long
    self.pid = pid  # long
    self.path = path    # unicode
    self.language = language # str
    self.launchPath = launchPath  # unicode
    self.processName = processName  # unicode
    self.windowName = windowName    # unicode

    # Thread
    self.encoding = encoding    # str  game encoding
    self.threadSignature = threadSignature  # long
    self.threadName = threadName    # str
    self.removesRepeat = removesRepeat # bool
    self.ignoresRepeat = ignoresRepeat # bool
    self.keepsSpace = keepsSpace # bool
    self.threadKept = threadKept # bool
    self.timeZoneEnabled = timeZoneEnabled # bool

    # {long signature : str name} or None
    #self.otherThreads = None

    # Alias
    self.linkName = linkName        # unicode
    self.folderName = folderName    # unicode
    self.brandName = brandName      # unicode

    # Hook
    self.hook = hook # str
    self.deletedHook = deletedHook # str

    # Launcher
    self.loader = loader # str

    # Game agent
    self.launchLanguage = launchLanguage # str

    # Whether enable vnrboot
    self.vnrboot = False # bool

  def applyHook(self):
    """
    @return  bool  if succeed
    """
    if not self.hook:
      return False
    if self.hook in config.HCODE_BLACKLIST or self.fileName() in config.HCODE_FILE_BLACKLIST:
      self.hook = ""
      return False
    return texthook.global_().setHookCode(self.hook)

  def fileName(self):
    return self.processName or (
        os.path.basename(self.path) if self.path else "")

  def name(self):
    """
    @return  unicode not None
    """
    return self.linkName or self.windowName or self.fileName() or self.folderName

  def icon(self):
    """
    @return  QIcon or None
    """
    return (
      rc.file_icon(self.path) if self.path and os.path.exists(self.path) else
      rc.file_icon(self.launchPath) if self.launchPath else
      None)

  def md5(self):
    """Compute md5 digest for the file at path"""
    return hashutil.md5sum(osutil.normalize_path(self.path)) if self.path else ""

  # This function is only called by gamewizard for text hook
  def isTextHookAttached(self):
    return self.pid and self.pid == texthook.global_().currentPid()

  def isAttached(self):
    return self.pid and self.pid in (
        texthook.global_().currentPid(),
        gameagent.global_().attachedPid())

  def hasProcess(self):
    #return all((self.wid, self.pid, self.path, self.processName, self.windowName))
    return all((self.wid, self.pid, self.path, self.processName)) and skwin.is_process_active(self.pid)

  def hasThread(self):
    return (self.threadSignature != 0 and
            self.threadName != "" and
            self.encoding != "")

  def isLocked(self): return self.__d.locked

  threadUpdated = Signal()
  def updateThread(self, hookEnabled=True):
    """
    @param  hookEnabled  whether automatically apply the hook code
    """
    try:
      md5 = self.md5()
      if not md5:
        dwarn("failed to create md5 digest")
        return

      dprint("md5 = %s" % md5)

      game = dataman.manager().queryGame(md5=md5, online=True)
      if not game:
        dprint("could not find game info")
        return

      self.encoding = game.encoding
      self.threadName = game.threadName
      self.threadSignature = game.threadSignature
      #self.otherThreads = game.otherThreads
      self.removesRepeat = game.removesRepeat
      self.ignoresRepeat = game.ignoresRepeat
      self.keepsSpace = game.keepsSpace
      self.threadKept = game.threadKept

      hooked = False
      if hookEnabled:
        if game.hook and self.hook != game.hook:
          self.hook = game.hook
          hooked = self.applyHook()
      elif game.hook and game.hook != texthook.global_().currentHookCode():
        growl.notify(my.tr("Skip user-defined hook as you wish")
            + "<br/>" + game.hook)

      if not hooked:
        self.hijackProcess()

      dprint("encoding = %s, thread name = %s" % (self.encoding, self.threadName))

    finally:
      self.threadUpdated.emit()

  def hijackProcess(self): return texthook.global_().hijackProcess()

  def updateHook(self):
    """
    @return  bool
    """
    return bool(self.hook) and self.applyHook()
    #ret = True
    #if self.hook: #and not self.hook in config.HCODE_BLACKLIST:
    #  ret = self.applyHook()
    #else:
    #  nm = netman.manager()
    #  if nm.isOnline():
    #    md5 = self.md5()
    #    if md5:
    #      game = nm.queryGame(md5=md5)
    #      if game and game.hook:
    #        #if game.hook in config.HCODE_BLACKLIST:
    #        #  self.hook = game.hook = ''
    #        #else:
    #        self.hook = game.hook
    #        if game.deletedHook:
    #          self.deletedHook = game.deletedHook
    #        ret = self.applyHook()
    #return ret

  #def updateOtherThreads(self):
  #  md5 = self.md5()
  #  if not md5:
  #    dwarn("failed to create md5 digest")
  #    return
  #  game = dataman.manager().queryGame(md5=md5, online=True)
  #  if not game:
  #    dprint("could not find game info")
  #    return
  #  self.otherThreads = game.otherThreads

  def updateGameNames(self):
    self.folderName = ""
    self.brandName = ""

    if not self.path or not PROGRAMFILES:
      return

    path = QtCore.QDir.fromNativeSeparators(self.path)
    if path.lower().startswith(PROGRAMFILES.lower()):
      path = PROGRAMFILES_RE.sub(path, "")
      l = filter(bool, path.split('/')) # filter to skip empty parts
      if l and len(l) <= 3:
        self.folderName = l[1] if len(l) == 3 else l[-1]
        #dprint("game folder = %s" % self.folderName)
        if len(l) >= 2:
          self.brandName = l[0]
          #dprint("game brand = %s" % self.brandName)
    else:
      l = filter(bool, path.split('/')) # filter to skip empty parts
      if len(l) >= 3:
        folderName = l[-2]
        if _good_folder_name(folderName):
          self.folderName = folderName
          #dprint("game folder = %s" % self.folderName)

  def clear(self):
    self.wid = self.pid = 0
    self.path = ""
    self.launchPath = ""
    self.windowName = self.processName = ""
    self.hook = ""
    self.language = "ja"
    self.launchLanguage = ""
    self.threadSignature = 0
    self.threadName = ""
    self.processName = ""
    self.folderName = ""
    self.brandName = ""
    #self.otherThreads = None
    self.loader = "" # apploc, etc

  processUpdated = Signal()

  # Always use apploc when launchLanguage is specified by game agent
  #def usingNoneLoader(self): return self.loader == 'none'
  def usingApploc(self): return self.loader == 'apploc' or not self.loader and settings.global_().isApplocEnabled()
  def usingNtlea(self): return self.loader == 'ntlea' or not self.loader and settings.global_().isNtleaEnabled()
  def usingLocaleSwitch(self): return self.loader == 'lsc' or not self.loader and settings.global_().isLocaleSwitchEnabled()
  def usingLocaleEmulator(self): return self.loader == 'le' or not self.loader and settings.global_().isLocaleEmulatorEnabled()
  def usingNtleas(self): return self.loader == 'ntleas' or not self.loader and settings.global_().isNtleasEnabled()

  def updateProcess(self, retries=2, launch=True):
    """
    @param  int  retries
    @param  bool  launch  whether allows launching the application
    @emit  processUpdated
    """
    if not skos.WIN or retries < 0:
      self.processUpdated.emit()
      return

    def updateLater(verbose=False):
      ret = retries > 0
      if ret:
        if verbose:
          growl.notify(my.tr("Waiting game starts") + " ...")
        skevents.runlater(partial(
            self.updateProcess, launch=False, retries=retries-1),
            7000)
      return ret

    dprint("enter")
    self.__d.locked = True

    if not self.path and self.pid:
      # Native windows query does not work well, as Python does not have sufficient permission
      path = skwin.get_process_path(self.pid)
      self.path = winutil.to_long_path(path) or path

    if not self.pid and self.wid:
      self.pid = skwin.get_window_process_id(self.wid)

    if not self.pid and self.path:
      proc = get_process_by_path(self.path)
      if not proc:
        dprint("launching process path = %s" % self.path)

        launchLanguage = self.launchLanguage or settings.global_().gameLaunchLanguage() #or 'ja'
        dprint("launch language = %s" % launchLanguage)

        usingLocaleSwitch = self.usingLocaleSwitch()
        if features.ADMIN == False and usingLocaleSwitch:
          loader = notr_("LocaleSwitch") if usingLocaleSwitch else notr_("Locale Emulator")
          growl.error(my.tr("{0} requires admin privileges. Please restart VNR as admin").format(loader))
        else:
          tz = self.timeZoneEnabled
          if tz is None:
            tz = settings.global_().isTimeZoneEnabled()
          if tz:
            growl.notify(my.tr("Launch the game in Japan time as you wish"))
            import tzman
            tzman.manager().changeTimeZone()

          # Launch with Locale Emulator
          if self.usingLocaleEmulator():
            path = QtCore.QDir.toNativeSeparators(self.path)
            #path = winutil.to_short_path(path) or path
            proc = get_process_by_path(path)
            if not proc:
              if procutil.is_process_running('LEGUI.exe'):
                growl.notify(my.tr("Launch aborted. Wait for Locale Emulator."))
                self.__d.locked = False
                self.processUpdated.emit()
                return
              elif not self.launchPath or not os.path.exists(self.launchPath):
                if not launch:
                  if updateLater(verbose=True): return
                else:
                  growl.notify(my.tr("Launch the game with {0}").format(notr_("Locale Emulator")))
                  ntpid = procutil.open_executable(path, type='le', language=launchLanguage)
                  #proc = get_process_by_path(path)
                  if not ntpid:
                    growl.error(my.tr("Failed to launch the game with {0}").format(notr_("Locale Emulator")))
                  elif updateLater(): return
              else:
                launchPath = QtCore.QDir.toNativeSeparators(self.launchPath)
                #launchPath = winutil.to_short_path(launchPath) or launchPath
                if get_process_by_path(launchPath):
                  if updateLater(verbose=True): return
                if not launch:
                  if updateLater(verbose=True): return
                else:
                  params = [QtCore.QDir.toNativeSeparators(self.path)]
                  ntpid = procutil.open_executable(launchPath, params=params, type='le', language=launchLanguage)
                  if not ntpid:
                    growl.error(my.tr("Failed to launch the game with {0}").format(notr_("Locale Emulator")))
                  elif updateLater(): return
          # Launch with NTLEAS
          elif self.usingNtleas():
            path = QtCore.QDir.toNativeSeparators(self.path) # maybe not needed by ntleas
            path = winutil.to_short_path(path) or path
            proc = get_process_by_path(path)
            if not proc:
              if not self.launchPath or not os.path.exists(self.launchPath):
                if not launch:
                  if updateLater(verbose=True): return
                else:
                  growl.notify(my.tr("Launch the game with {0}").format(notr_("Ntleas")))
                  ntpid = procutil.open_executable(path, type='ntleas', language=launchLanguage)
                  #proc = get_process_by_path(path)
                  if not ntpid:
                    growl.error(my.tr("Failed to launch the game with {0}").format(notr_("Ntleas")))
                  elif updateLater(): return
              else:
                launchPath = QtCore.QDir.toNativeSeparators(self.launchPath)
                launchPath = winutil.to_short_path(launchPath) or launchPath
                if get_process_by_path(launchPath):
                  if updateLater(): return
                elif not launch:
                  if updateLater(verbose=True): return
                else:
                  params = [QtCore.QDir.toNativeSeparators(self.path)]
                  ntpid = procutil.open_executable(launchPath, params=params, type='ntleas', language=launchLanguage)
                  if not ntpid:
                    growl.error(my.tr("Failed to launch the game with {0}").format(notr_("Ntleas")))
                  elif updateLater(): return
          # Launch with NTLEA
          elif self.usingNtlea():
            path = QtCore.QDir.toNativeSeparators(self.path)
            path = winutil.to_short_path(path) or path
            proc = get_process_by_path(path)
            if not proc:
              if not self.launchPath or not os.path.exists(self.launchPath):
                if not launch:
                  if updateLater(verbose=True): return
                else:
                  growl.notify(my.tr("Launch the game with {0}").format(notr_("NTLEA")))
                  ntpid = procutil.open_executable(path, type='ntlea', language=launchLanguage)
                  #proc = get_process_by_path(path)
                  if not ntpid:
                    growl.error(my.tr("Failed to launch the game with {0}").format(notr_("NTLEA")))
                  elif updateLater(): return
              else:
                launchPath = QtCore.QDir.toNativeSeparators(self.launchPath)
                launchPath = winutil.to_short_path(launchPath) or launchPath
                if get_process_by_path(launchPath):
                  if updateLater(): return
                elif not launch:
                  if updateLater(verbose=True): return
                else:
                  params = [QtCore.QDir.toNativeSeparators(self.path)]
                  ntpid = procutil.open_executable(launchPath, params=params, type='ntlea', language=launchLanguage)
                  if not ntpid:
                    growl.error(my.tr("Failed to launch the game with {0}").format(notr_("NTLEA")))
                  elif updateLater(): return
          # Launch with LocaleSwitch
          elif self.usingLocaleSwitch():
            path = QtCore.QDir.toNativeSeparators(self.path)
            path = winutil.to_short_path(path) or path
            proc = get_process_by_path(path)
            if not proc:
              if not self.launchPath or not os.path.exists(self.launchPath):
                if not launch:
                  if updateLater(verbose=True): return
                else:
                  growl.notify(my.tr("Launch the game with {0}").format(notr_("LocaleSwitch")))
                  ntpid = procutil.open_executable(path, type='lsc', language=launchLanguage)
                  #proc = get_process_by_path(path)
                  if not ntpid:
                    growl.error(my.tr("Failed to launch the game with {0}").format(notr_("LocaleSwitch")))
                  elif updateLater(): return
              else:
                launchPath = QtCore.QDir.toNativeSeparators(self.launchPath)
                launchPath = winutil.to_short_path(launchPath) or launchPath
                if get_process_by_path(launchPath):
                  if updateLater(): return
                elif not launch:
                  if updateLater(verbose=True): return
                else:
                  params = [QtCore.QDir.toNativeSeparators(self.path)]
                  ntpid = procutil.open_executable(launchPath, params=params, type='lsc', language=launchLanguage)
                  if not ntpid:
                    growl.error(my.tr("Failed to launch the game with {0}").format(notr_("LocaleSwitch")))
                  elif updateLater(): return
          else: # Launch with AppLocale
            if not launch:
              if updateLater(verbose=True): return
            else:
              if features.WINE or not self.usingApploc():
                launchLanguage = ''
              if not self.launchPath or not os.path.exists(self.launchPath):
                if self.vnrboot:
                  growl.notify(my.tr("Launch the game with {0}").format(notr_("VNR dlls")))
                elif launchLanguage:
                  growl.notify(my.tr("Launch the game with {0}").format(notr_("AppLocale")))
                elif not features.WINE:
                  growl.notify(my.tr("Launch the game in original Japanese locale"))
                self.pid = procutil.open_executable(self.path, language=launchLanguage, vnrboot=self.vnrboot)
                #vnragent.inject_process(self.pid)
                #rpcman.manager().enableClient()
                if not self.pid:
                  proc = get_process_by_path(self.path)
                if self.pid or proc:
                  if updateLater(): return
              else: # launch the launcher instead of the original ame
                if get_process_by_path(self.launchPath):
                  if updateLater(): return

                #if self.vnrboot:
                #  growl.notify(my.tr("Launch the game with {0}").format(notr_("VNR")))

                params = [QtCore.QDir.toNativeSeparators(self.path)]
                pid = procutil.open_executable(self.launchPath, params=params, language=launchLanguage, vnrboot=self.vnrboot)
                proc = get_process_by_path(self.path)
                if pid or proc:
                  if updateLater(): return
      if proc:
        self.pid = proc.pid
        self.processName = proc.name
        path = proc.path
        self.path = winutil.to_long_path(path) or path

    if not self.wid and self.pid:
      self.wid = procutil.get_process_active_window(self.pid)

    if not self.windowName and self.wid:
      t = skwin.get_window_text(self.wid)
      #t = u_sjis(t) if self.language == 'ja' else u(t)
      if t and not '??' in t and sjis_encodable(t) and not textutil.is_illegal_text(t):
        t = re.sub(r'\s*<.*', '', t)
        if t:
          self.windowName = t

    if not self.processName and self.pid:
      self.processName = skwin.get_process_name(self.pid)

    if not self.path and self.pid:
      path = skwin.get_process_path(self.pid)
      self.path = winutil.to_long_path(path) or path

    self.__d.locked = False
    self.processUpdated.emit()
    dprint("leave")

  def openGame(self):
    manager().openGame(
        wid=self.wid, pid=self.pid, path=self.path, launchPath=self.launchPath, encoding=self.encoding,
        hook=self.hook, threadName=self.threadName, threadSignature=self.threadSignature)
    dprint("pass")

@Q_Q
class _GameProxy(object):

  @property
  def postReturnTimer(self):
    try: return self._postReturnTimer
    except AttributeError:
      q = self.q
      ret = self._postReturnTimer = QtCore.QTimer(q)
      ret.setSingleShot(True)
      ret.timeout.connect(q.postReturn)
      return ret

  def stopPostReturnTimer(self):
    if hasattr(self, '_postReturnTimer') and self._postReturnTimer.isActive():
      self._postReturnTimer.stop()

#@QmlObject
class GameProxy(QtCore.QObject):
  """Proxy to control game process"""
  def __init__(self, parent=None):
    super(GameProxy, self).__init__(parent)
    self.__d = _GameProxy(self)

  # Not used
  #@Slot()
  #def sendReturn(self):
  #  try:
  #    hwnd = manager().currentGame().wid
  #    skwin.send_key_return(hwnd)
  #  except AttributeError: # no current game
  #    pass
  #  except Exception, e: #pywintypes.error, e:
  #    dwarn(e)

  @Slot()
  def postReturn(self):
    try:
      import win32gui
      f = win32gui.GetFocus()
      hwnd = manager().currentGame().wid
      skwin.post_key_return(hwnd)
      self.__d.stopPostReturnTimer()
      if f:
        skevents.runlater(partial(win32gui.SetFocus, f), 500)
    except AttributeError: # no current game
      pass
    except Exception, e: # pywintypes.error
      dwarn(e) # might raise access denied error

  @Slot()
  def postReturnLater(self, interval=500):
    self.__d.postReturnTimer.start(interval)

  #@Slot()
  #def clickWindow(self):
  #  """Send mouse click event"""
  #  pass

  @Slot()
  def captureWindow(self):
    manager().captureWindow()

## Game manager ##

class _GameManager:
  def __init__(self):
    self.game = None # GameProfile
    self.locked = False # bool
    #self.windowHookConnected = False # bool

    # Cached properties
    self.focusEnabled = False

class GameManager(QtCore.QObject):

  def __init__(self, parent=None):
    super(GameManager, self).__init__(parent)
    self.__d = _GameManager()

    for sig in self.cleared, self.threadChanged:
      sig.connect(self._onThreadChanged)

    dprint("pass")

  ## Signals ##

  processDetached = Signal() # either texthook or gameagent is detached

  openingGame = Signal()
  openGameFailed = Signal()
  languageChanged = Signal(unicode)
  threadChanged = Signal(long, unicode) # signature, name, won't emit when game closed
  removesRepeatChanged = Signal(bool)
  ignoresRepeatChanged = Signal(bool)
  keepsSpaceChanged = Signal(bool)
  threadKeptChanged = Signal(bool)
  hookChanged = Signal(unicode) # hook, won't emit when game closed
  encodingChanged = Signal(unicode) # text encoding, won't emit when game closed
  windowChanged = Signal(long) # wid, won't emit when game closed
  processChanged = Signal(long, unicode) # pid, path, won't emit when game closed

  focusEnabledChanged = Signal(bool)

  nameThreadChanged = Signal(long, unicode) # signature, name, won't emit when game closed
  nameThreadDisabled = Signal() # signature, name, won't emit when game closed
  otherThreadsChanged = Signal(dict) # {long signature:str name}

  cleared = Signal()

  ## Properties ##

  def currentGame(self):
    """
    @return  GameProfile or None
    """
    return self.__d.game

  def currentGamePid(self):
    """
    @return  long
    """
    return self.__d.game.pid if self.__d.game else 0

  def currentGameThreadName(self):
    """
    @return  str or ''
    """
    return self.__d.game.threadName if self.__d.game else ''

  def isFocusEnabled(self):
    """
    @return  bool
    """
    return self.__d.focusEnabled

  def _onThreadChanged(self): # invoked whenever the thread name is invoked
    self._updateFocusEnabled()

  def _updateFocusEnabled(self):
    d = self.__d
    t = False
    g = d.game
    threadName = ""
    if g:
      threadName = g.threadName
      if threadName:
        t = threadName in config.FOCUS_GAME_ENGINES
    if t != d.focusEnabled:
      d.focusEnabled = t
      self.focusEnabledChanged.emit(t)
      #if t:
      #  growl.msg(": ".join((
      #    my.tr("Game engine allows full screen"),
      #    threadName,
      #  )))

  ## Actions ##

  def attachTextHook(self): # this function is only called in main.py when GameAgent Failed
    pid = self.currentGamePid()
    if not pid:
      dwarn("game already closed")
      return

    agent = gameagent.global_()
    if agent.isConnected() and agent.hasEngine():
      dwarn("vnragent already have an engine?")
      return

    if pid != texthook.global_().currentPid():
      ok = inject.inject_vnrhook(pid)
      dprint("inject ITH, ok = %s" % ok)

  def clear(self):
    self.__d.game = None
    #self.__d.windowHookConnected = False
    self.cleared.emit()

  def refreshWindow(self):
    g = self.__d.game
    if not g or not g.pid:
      self.windowChanged.emit(0)
      return

    if g.wid and procutil.is_active_window(g.wid):
      # Enforce window visible
      self.windowChanged.emit(g.wid)
      #self.minimizedChanged.emit(self.isMinimized())
      dprint("active window")
      return

    #if not procutil.get_process_by_pid(g.pid):
    if not skwin.is_process_active(g.pid):
      growl.msg(my.tr("Game closed"))
      self.clear()
      self.windowChanged.emit(0)
      return

    wid = procutil.get_process_active_window(g.pid)
    if not wid:
      growl.notify(my.tr("Cannot find game window"))
      self.windowChanged.emit(0)
      return
    g.wid = wid
    self.windowChanged.emit(wid)

  def captureWindow(self):
    import grab
    g = grab.manager()
    hwnd = self.__d.game.wid if self.__d.game else 0
    ok = g.grabWindow(hwnd) if hwnd else g.grabDesktop()
    if ok:
      growl.msg(my.tr("Screenshot saved to clipboard and desktop"))
    else:
      growl.warn(my.tr("Cannot save the screenshot"))

  def openExecutable(self, path, launchPath=""):
    #self.setGame(path=path)
    growl.msg(tr_("Opening") + ":" "<br/>" + path)
    self.openGame(path=path, launchPath=launchPath)
    dprint("pass")

  def openNewGame(self, path, md5=None, **kwargs):
    """
    @param  path  unicode
    """
    if not path:
      return
    dprint("enter: path = %s" % path)

    if procutil.is_blocked_process_path(path):
      dwarn("leave: blocked file name")
      growl.warn(my.tr("Please do not add non-game program to VNR!"))
      return

    d = self.__d
    if d.locked or d.game and d.game.isLocked():
      growl.msg(my.tr("Waiting for game to start"))
      dprint("leave: already running")
      return

    if not md5:
      np = osutil.normalize_path(path)
      md5 = hashutil.md5sum(np)
    if not md5:
      dprint("leave: cannot compute game md5 digest")
      return

    game = dataman.manager().queryGame(md5=md5, online=True)
    if not game:
      #dwarn("leave: warning, cannot find game online")
      #growl.notify(my.tr("Could not found game online, and please manually add game by Game Wizard"))
      #import main
      #m = main.manager()
      #m.showSpringBoard()
      #m.showGameWizard()
      dwarn("unknown game")
      growl.notify("<br/>".join((
          my.tr("It seems to be an unknown game."),
          my.tr("Please manually adjust Text Settings after launching the game."))))
      game = dataman.Game.createEmptyGame(path=path, md5=md5)

    self.openGame(game=game, path=path, **kwargs)
    dprint("leave: path = %s" % path)

  def isOpening(self):
    try: return self.__d.locked or self.__d.game.isLocked()
    except AttributeError: return False

  def openGame(self, pid=0, wid=0, path="", launchPath="", linkName="",
      hook="", threadName="", threadSignature=0, encoding="", language="",
      launchLanguage='',
      game=None):
    """
    @param  game  dataman.Game or None
    """
    dprint("enter: path = %s" % path)
    d = self.__d
    if d.locked or d.game and d.game.isLocked():
      growl.msg(my.tr("Waiting for game to start"))
      dprint("leave: already running")
      return
    cursor = skcursor.SkAutoBusyCursor()
    self.openingGame.emit()

    ss = settings.global_()
    try:
      d.locked = True
      hookEnabled = ss.isHookCodeEnabled()
      removesRepeat = None
      ignoresRepeat = None
      keepsSpace = None
      threadKept = None
      timeZoneEnabled = None
      gameAgentDisabled = False

      #commentCount = 0

      if game:
        path = path or game.path
        launchPath = launchPath or game.launchPath
        launchLanguage = launchLanguage or game.launchLanguage
        hook = hook or game.hook
        encoding = encoding or game.encoding
        threadName = threadName or game.threadName
        threadSignature = threadSignature or game.threadSignature
        removesRepeat = game.removesRepeat
        ignoresRepeat = game.ignoresRepeat
        keepsSpace = game.keepsSpace
        threadKept = game.threadKept
        hookEnabled = not game.hookDisabled
        language = language or game.language
        timeZoneEnabled = game.timeZoneEnabled
        gameAgentDisabled = game.gameAgentDisabled
        #commentCount = game.commentCount

      removesRepeat = bool(removesRepeat)
      ignoresRepeat = bool(ignoresRepeat)
      keepsSpace = bool(keepsSpace)
      loader = game.loader if game else ""

      if path and not launchPath:
        launchPath = defs.recover_exe_bin_suffix(path) or ''

      g = GameProfile(parent=self,
          wid=wid, pid=pid, path=path, launchPath=launchPath, linkName=linkName,
          deletedHook=game.deletedHook if game else "",
          encoding=encoding, hook=hook, threadName=threadName, threadSignature=threadSignature,
          removesRepeat=removesRepeat, ignoresRepeat=ignoresRepeat, keepsSpace=keepsSpace, threadKept=threadKept,
          language=language, launchLanguage=launchLanguage,
          loader=loader, timeZoneEnabled=timeZoneEnabled)

      md5 = g.md5()
      oldGame = dataman.manager().queryGame(md5=md5, online=False)
      if oldGame:
        for pty in 'encoding', 'language', 'launchLanguage', 'loader', 'launchPath', 'keepsSpace', 'removesRepeat': # , 'ignoresRepeat':
          v = getattr(g, pty)
          if not v:
            v = getattr(oldGame, pty)
            setattr(g, pty, v)
        if g.timeZoneEnabled is None:
          g.timeZoneEnabled = oldGame.timeZoneEnabled
        if not game:
          hookEnabled = not oldGame.hookDisabled
          gameAgentDisabled = oldGame.gameAgentDisabled
          #threadKept = oldGame.threadKept
          if oldGame.deletedHook:
            g.deletedHook = oldGame.deletedHook
        #if not commentCount:
        #  commentCount = oldGame.commentCount

      if not g.language:
        g.language = 'ja'

      #if not g.launchLanguage:
      #  g.launchLanguage = 'ja'

      agentEngine = gameagent.global_().guessEngine(pid=pid, path=path)
      if agentEngine:
        dprint("agent engine = %s" % agentEngine.name)
        if gameAgentDisabled or not ss.isGameAgentEnabled():
          agentEngine = None
          growl.notify(my.tr("Disable embedding translation for this game as you wish"))
          dprint("disable game agent")

      g.vnrboot = bool(agentEngine and agentEngine.vnrboot)

      if not g.hasProcess():
        dprint("update process")
        # exec event loop until the process is refreshed

        skevents.runlater(g.updateProcess)
        skevents.waitsignal(g.processUpdated)

        if not g.hasProcess():
          growl.error(my.tr("Cannot find game process. Please retry after game start."))
          self.openGameFailed.emit()
          dwarn("leave: cannot find game process")
          return

      agentConnected = g.pid == gameagent.global_().connectedPid()
      if agentConnected:
        skevents.runlater(gameagent.global_().sendSettings, 3000)

        dprint("disable h-code and repetition elimination as game agent is used")
        hookEnabled = False
        g.removesRepeat = False
        g.ignoresRepeat = False
        #g.keepsSpace = False
        #g.threadKept = False

      # g.hasProcess() must be true here, i.e. processId is valid
      elif not g.isAttached():
        attached = False

        if agentEngine:
          dprint("attach using game agent")
          growl.notify(my.tr("Use VNR's built-in hook instead of ITH"))
          attached = gameagent.global_().attachProcess(g.pid)
          if attached:
            dprint("disable h-code and repetition elimination as game agent is used")

            hookEnabled = False
            g.removesRepeat = False
            g.ignoresRepeat = False
            #g.keepsSpace = False
            #g.threadKept = False

        if not attached: # Use VNR agent or ITH as fallback
          # Enable ITH hook here
          #if features.WINE:
          #  # 9/18/2013: I am not sure if this could help reduce CreateRemoteThread in vnrsys from crashing
          #  skevents.sleep(5000) # Wait for 5 more seconds on Wine
          dprint("attach using text hook")
          #attached = texthook.global_().attachProcess(g.pid, hijack=False) # delay hijack
          attached = inject.inject_vnrhook(g.pid, hijack=False) # delay hijack

          #if attached:
          #  dprint("try game engine")
          #  from gameengine import gameengine
          #  skevents.runlater(partial(
          #      gameengine.inject, g.pid),
          #      3000) # wait for 3 seconds so that the gameengine will not crash the game on the start up (such as BALDR)

        if not attached:
          growl.error(my.tr("Cannot sync with game. Try restarting the game or using Game Wizard to set up connection"))
          self.openGameFailed.emit()
          dwarn("leave: cannot attach to game process")
          return

      if not g.hasThread():
        dprint("update thread")
        g.updateThread(hookEnabled=hookEnabled)

        if not g.hasThread():
          growl.error(my.tr("Cannot find game thread. Try using Game Wizard to set up connection"))
          #self.openGameFailed.emit()
          dwarn("leave: cannot find game thread")
          return

      #if g.otherThreads is None:
      #  dprint("update support threads")
      #  g.updateOtherThreads()
      #  if g.otherThreads is None:
      #    g.otherThreads = {}

      g.updateGameNames()

      if hookEnabled and not g.updateHook():
        if g.hook:
          growl.error("<br/>".join((
            my.tr("Failed to apply hook code"),
            g.hook,
            my.tr("Try adjusting it in Text Settings"),
          )))
        g.hijackProcess()

      #skevents.runlater(self.enableWindowHook, 4000)

      path = skwin.get_process_path(g.pid)
      if path:
        # Enforce long path
        path = winutil.to_long_path(path) or path
        g.path = path
        if not md5: # This happens when game path does not exist in the beginning
          md5 = g.md5()

      if g.path and not g.launchPath:
        g.launchPath = defs.recover_exe_bin_suffix(g.path) or ''

      d.game = g

      if agentEngine and gameagent.global_().isAttached() and not texthook.global_().isAttached():
        engine = gameagent.global_().engine() or agentEngine.name
        engineName = defs.to_ith_engine_name(engine)

        g.threadName = g.nameThreadName = engineName

      self.processChanged.emit(g.pid, g.path)
      self.threadChanged.emit(g.threadSignature, g.threadName)
      self.removesRepeatChanged.emit(bool(g.removesRepeat))
      self.ignoresRepeatChanged.emit(bool(g.ignoresRepeat))
      self.keepsSpaceChanged.emit(bool(g.keepsSpace))
      self.threadKeptChanged.emit(bool(g.threadKept))
      self.encodingChanged.emit(g.encoding)
      self.windowChanged.emit(g.wid)
      self.hookChanged.emit(g.hook)
      self.languageChanged.emit(g.language)

      # Enforce window visible
      #for t in 500, 3000, 5000:
      #  skevents.runlater(self.refreshWindow, t)

      commentCount = 0
      nm = netman.manager()
      if nm.isOnline():
        gameId = dataman.manager().queryGameId(md5)
        onlineGame = nm.queryGame(md5=md5, id=gameId)
        if onlineGame:
          commentCount = onlineGame.commentCount
          if onlineGame.deletedHook:
            g.deletedHook = onlineGame.deletedHook

      #if not hookEnabled:
      #  hook = ""

      gameData = dataman.Game(
          md5=md5,
          encoding=g.encoding, hook=g.hook, threadName=g.threadName, threadSignature=g.threadSignature,
          removesRepeat=g.removesRepeat, ignoresRepeat=g.ignoresRepeat, keepsSpace=keepsSpace, threadKept=g.threadKept,
          windowNames = [g.windowName] if g.windowName else [],
          fileNames = [g.fileName()],
          linkNames = [g.linkName] if g.linkName else [],
          folderNames = [g.folderName] if g.folderName else [],
          brandNames = [g.brandName] if g.brandName else [],
          path=g.path, launchPath=g.launchPath,
          loader=g.loader, hookDisabled=not hookEnabled, deletedHook=g.deletedHook,
          language=g.language, launchLanguage=g.launchLanguage,
          timeZoneEnabled=g.timeZoneEnabled,
          gameAgentDisabled=gameAgentDisabled,
          commentCount=commentCount,
          visitTime=skdatetime.current_unixtime())

      for it in game, oldGame:
        if it:
          if not gameData.launchPath:
            gameData.launchPath = it.launchPath
          if not gameData.otherThreads:
            gameData.otherThreads = it.otherThreads
          if not gameData.nameThreadSignature:
            gameData.nameThreadSignature = it.nameThreadSignature
          if not gameData.nameThreadName:
            gameData.nameThreadName = it.nameThreadName
          if not gameData.nameThreadDisabled:
            gameData.nameThreadDisabled = it.nameThreadDisabled

      self.nameThreadChanged.emit(gameData.nameThreadSignature, gameData.nameThreadName)
      self.otherThreadsChanged.emit(gameData.otherThreads)

      agentAttached = g.pid == gameagent.global_().attachedPid()
      if agentAttached:
        sig = gameData.threadSignature
        gameagent.global_().setScenarioSignature(sig)

        sig = gameData.nameThreadSignature if gameData.nameThreadSignature and not gameData.nameThreadDisabled else 0
        gameagent.global_().setNameSignature(sig)

      task = partial(dataman.manager().loadGame, gameData)
      skevents.runlater(task, 200)

      if agentAttached:
        if g.threadName in config.EMBEDDED_EN_GAME_ENGINES:
          growl.notify(my.tr("Embed translation might only work for English for this game"))
      else:

        if g.threadName in config.REPEAT_GAME_ENGINES:
          growl.notify(my.tr("This game might need turning on repetition elimination"))

        if g.threadName in config.SLOW_GAME_ENGINES:
          growl.notify(my.tr("This game requires the text speed to be either Normal or Slow instead of Fast to work"))
        elif g.threadName in config.FAST_GAME_ENGINES:
          growl.notify(my.tr("This game requires the text speed to be Fast to work"))

        if g.threadName in config.DELAY_GAME_ENGINES:
          growl.notify(my.tr("This game requires opening VNR after starting/loading the game"))

    finally:
      try:
        if g and g is not d.game:
          skevents.runlater(g.deleteLater)
      except NameError: pass
      d.locked = False

  #def isWindowHookConnected(self): return self.__d.windowHookConnected
  #def setWindowHookConnected(self, value): self.__d.windowHookConnected = value

  #def enableWindowHook(self):
  #  if settings.global_().isWindowHookEnabled():
  #    d = self.__d
  #    if d.game and d.game.pid:
  #      growl.msg(my.tr("Translating window text"))
  #      if not d.windowHookConnected and not textman.manager().hasWindowTexts():
  #        dprint("inject vnr agent to the game")
  #        import inject
  #        inject.inject_agent(d.game.pid)
  #      rpcman.manager().enableAgent()

  #def disableWindowHook(self):
  #  d = self.__d
  #  if d.game and d.game.pid:
  #    if d.windowHookConnected or textman.manager().hasWindowTexts():
  #      growl.msg(my.tr("Stop translating window text"))
  #    rpcman.manager().disableAgent()

  def setRemovesRepeat(self, value):
    """
    @param  value  bool or None
    """
    dprint("enter: value = %s" % value)
    g = self.__d.game
    if g and g.removesRepeat != value:
      g.removesRepeat = value
      if value is not None:
        md5 = g.md5()
        if md5:
          gameData = dataman.Game(
            md5=md5,
            removesRepeat=g.removesRepeat)
          task = partial(dataman.manager().updateGame, gameData)
          skevents.runlater(task, 200)

    self.removesRepeatChanged.emit(bool(value))
    dprint("leave")

  def setIgnoresRepeat(self, value):
    """
    @param  value  bool or None
    """
    dprint("enter: value = %s" % value)
    g = self.__d.game
    if g and g.ignoresRepeat != value:
      g.ignoresRepeat = value
      if value is not None:
        md5 = g.md5()
        if md5:
          gameData = dataman.Game(
            md5=md5,
            ignoresRepeat=g.ignoresRepeat)
          task = partial(dataman.manager().updateGame, gameData)
          skevents.runlater(task, 200)

    self.ignoresRepeatChanged.emit(bool(value))
    dprint("leave")

  def setKeepsSpace(self, value):
    """
    @param  value  bool or None
    """
    dprint("enter: value = %s" % value)
    g = self.__d.game
    if g and g.keepsSpace != value:
      g.keepsSpace = value
      if value is not None:
        md5 = g.md5()
        if md5:
          gameData = dataman.Game(
            md5=md5,
            keepsSpace=g.keepsSpace)
          task = partial(dataman.manager().updateGame, gameData)
          skevents.runlater(task, 200)

    self.keepsSpaceChanged.emit(bool(value))
    dprint("leave")

  def setThreadKept(self, value):
    """
    @param  value  bool or None
    """
    dprint("enter: value = %s" % value)
    g = self.__d.game
    if g and g.threadKept != value:
      g.threadKept = value
      if value is not None:
        md5 = g.md5()
        if md5:
          gameData = dataman.Game(
            md5=md5,
            threadKept=g.threadKept)
          task = partial(dataman.manager().updateGame, gameData)
          skevents.runlater(task, 200)

    self.threadKeptChanged.emit(bool(value))
    dprint("leave")

  def setLanguage(self, lang):
    """
    @param  encoding  lang
    """
    if not lang:
      return
    dprint("enter: lang = %s" % lang)
    g = self.__d.game
    if g and g.language != lang:
      g.language = lang
      md5 = g.md5()
      if md5:
        gameData = dataman.Game(
          md5=md5,
          language=lang)
        task = partial(dataman.manager().updateGame, gameData)
        skevents.runlater(task, 200)

        dataman.manager().setGameLanguage(lang, md5)

    self.languageChanged.emit(lang)
    dprint("leave")

  def setCurrentThread(self, signature, name, encoding=None):
    """
    @param  signature  long
    @param  name  str
    @param  encoding  str or None
    """
    if not signature or not name:
      return
    dprint("enter: sig = %i, name = %s, encoding = %s" %(signature, name, encoding))
    g = self.__d.game
    if g:
      g.threadSignature = signature
      g.threadName = name
      if encoding:
        g.encoding = encoding

      md5 = g.md5()
      if md5:
        gameData = dataman.Game(
          md5=md5,
          encoding=encoding, threadName=name, threadSignature=signature)
        task = partial(dataman.manager().updateGame, gameData)
        skevents.runlater(task, 200)

    self.threadChanged.emit(signature, name)
    if encoding:
      self.encodingChanged.emit(encoding)
    dprint("leave")

  def setNameThread(self, signature, name):
    """
    @param  signature  long
    @param  name  str
    """
    dprint("enter")
    g = self.__d.game
    if g:
      md5 = g.md5()
      if md5:
        gameData = dataman.Game(
          md5=md5,
          nameThreadSignature=signature, nameThreadName=name,
          nameThreadDisabled=False)
        task = partial(dataman.manager().updateGame, gameData)
        skevents.runlater(task, 200)
    self.nameThreadChanged.emit(signature, name)
    dprint("leave")

  def disableNameThread(self):
    dprint("enter")
    g = self.__d.game
    if g:
      md5 = g.md5()
      if md5:
        gameData = dataman.Game(
          md5=md5,
          nameThreadDisabled=True)
        task = partial(dataman.manager().updateGame, gameData)
        skevents.runlater(task, 200)
    self.nameThreadDisabled.emit()
    dprint("leave")

  def setOtherThreads(self, threads):
    """
    @param  threads  {long signature:str name} or None
    """
    if threads is None:
      threads = {}
    dprint("enter: totally %i threads" % len(threads))
    g = self.__d.game
    if g:
      md5 = g.md5()
      if md5:
        dataman.manager().setGameOtherThreads(threads, md5=md5)
    self.otherThreadsChanged.emit(threads)
    dprint("leave")

  def setCurrentHook(self, hook):
    dprint("enter: hcode = %s" % hook)
    g = self.__d.game
    if g:
      g.hook = hook
      md5 = g.md5()
      if md5:
        if hook:
          gameData = dataman.Game(md5=md5, hook=hook)
          task = partial(dataman.manager().updateGame, gameData)
        else:
          gameData = dataman.Game(md5=md5)
          task = partial(dataman.manager().updateGame, gameData, deleteHook=True)
        skevents.runlater(task, 200)

    self.hookChanged.emit(hook)
    dprint("leave")

  #def setLaunchPath(self, path):
  #  dprint("enter: path = %s" % path)
  #  g = self.__d.game
  #  if g and g.launchPath != path:
  #    g.launchPath = path
  #    md5 = g.md5()
  #    if md5:
  #      gameData = dataman.Game(md5=md5, launchPath=path)
  #      dataman.manager().updateGame(gameData,
  #          replaceLaunchPath=True, online=False)
  #  #self.launchPathChanged.emit(path)
  #  dprint("leave")

  #def setLoader(self, loader):
  #  dprint("enter: loader = %s" % loader)
  #  g = self.__d.game
  #  if g and g.loader != loader:
  #    g.loader = loader
  #    md5 = g.md5()
  #    if md5:
  #      dataman.manager().setGameLoader(loader, md5=md5)
  #  #self.loaderChanged.emit(path)
  #  dprint("leave")

  @staticmethod
  def findRunningGame(pid=0):
    """
    @param* pid  long  filter pid
    @return  dataman.Game or None
    """
    dm = dataman.manager()
    if dm.hasGames():
      for p in procutil.iterprocess():
        if pid and p.pid != pid:
          continue
        if p.path:
          filename = os.path.basename(p.path).lower()
          for g in dm.games():
            if g.path:
              if filename == os.path.basename(g.path).lower():
                np = osutil.normalize_path(p.path)
                if np == osutil.normalize_path(g.path) or hashutil.md5sum(np) == g.md5:
                  g.path = p.path # update game path in the database
                  return g

  @staticmethod
  def findRunningGamePathByMd5(pid=0):
    """
    @param* pid  long  filter pid
    @return  unicode or None
    """
    dm = dataman.manager()
    if dm.hasGames() or dm.hasGameFiles():
      for p in procutil.iterprocess():
        if pid and p.pid != pid:
          continue
        if p.path:
          np = osutil.normalize_path(p.path)
          md5 = hashutil.md5sum(np)
          if md5 and dm.containsGameMd5(md5):
            return p.path

@memoized
def manager(): return GameManager()

## QML game launcher ##

#@Q_Q
#class _GameManagerProxy(object):
#
#  def __init__(self):
#    m = manager()
#    for sig in m.cleared, m.threadChanged:
#      sig.connect(self.onThreadChanged)
#
#  def onThreadChanged(self):
#    q = self.q
#    t = q.currentGameFocusEnabled
#    dprint("game thread allows focus: %s" % t)
#    q.currentGameFocusEnabledChanged.emit(t)

#@QmlPersistentObject # 10/19/2014: otherwise, it will crash in kagami.qml after the game is closed
class GameManagerProxy(QtCore.QObject):

  def __init__(self, parent=None):
    super(GameManagerProxy, self).__init__(parent)
    #self.__d = _GameManagerProxy(self)

  # Thread name

  #threadNameChanged = Signal(str)
  #threadName = Property(str,
  #    lambda _: manager().currentGame() ? manager().currentGame().threadName : "",
  #    notify=threadNameChanged)

  #currentGameFocusEnabledChanged = Signal(bool)
  #currentGameFocusEnabled = Property(bool,
  #    lambda _: manager().isCurrentGameFocusEnabled(),
  #    notify=currentGameFocusEnabledChanged)

  # Open

  @Slot(unicode, unicode)
  def openLocation(self, path, launchPath):
    manager().openExecutable(path, launchPath=launchPath)

  @Slot(QtCore.QObject)
  def open(self, game):
    if game:
      self.openLocation(game.path, game.launchPath)

  @Slot(QtCore.QObject)
  def remove(self, game):
    import prompt
    if game and prompt.confirmDeleteGame(game):
      dataman.manager().removeGame(md5=game.md5)
      growl.msg(my.tr("Game removed") + "<br/>" + game.path)

  @Slot(QtCore.QObject)
  def openDirectory(self, game):
    if game and game.path:
      path = os.path.dirname(game.path)
      if os.path.exists(path):
        growl.msg(tr_("Opening") + ":" "<br/>" + path)
        osutil.open_location(path)
      else:
        growl.error(my.tr("Location does not exist") + "<br/>" + path)

# EOF
