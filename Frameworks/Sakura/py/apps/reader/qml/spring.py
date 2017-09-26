# coding: utf8
# spring.py
# 10/5/2012 jichi

import os
from functools import partial
from sakurakit import skevents
from sakurakit.skclass import Q_Q
from sakurakit.skdebug import dprint, derror
from sakurakit.skqml import SkDeclarativeView
from sakurakit.skwidgets import shortcut
import growl, settings

# Also used in Preferences
IMAGE_SUFFICES = frozenset((
  'bmp',
  'gif',
  'jpg', 'jpeg',
  'png',
  'svg',
  'tiff',
))

@Q_Q
class _SpringBoard(object):

  def __init__(self):
    self.createShortcuts()
    self.loadSize()

  def createShortcuts(self):
    q = self.q
    import main
    m = main.manager()
    # Must be consistent with springboard/appmenu.qml
    shortcut('alt+q', m.confirmQuit, parent=q)
    shortcut('alt+r', m.confirmRestart, parent=q)
    shortcut('alt+u', m.confirmUpdateGameDatabase, parent=q)
    shortcut('alt+o', m.showPreferences, parent=q) # Does not work on windows?!
    shortcut('alt+s', m.openRunningGame, parent=q)
    shortcut('alt+n', m.showGameWizard, parent=q)
    shortcut('alt+f', m.showGameBoard, parent=q)

  def loadSize(self):
    w, h = settings.global_().springBoardSize()
    if w > 100 and w < 1200 and h > 100 and h < 900:
      self.q.resize(w, h)

  def saveSize(self):
    q = self.q
    if not q.isMaximized() and not q.isMinimized():
      settings.global_().setSpringBoardSize(q.size())

  @staticmethod
  def isSupportedMimeData(mime):
    """
    @param  mime  QMimeData or None
    @return  bool
    """
    if not mime or not mime.hasUrls() or len(mime.urls()) != 1:
      return False
    url = mime.urls()[0]
    return _SpringBoard._isSupportedUrl(url)

  @staticmethod
  def _isSupportedUrl(url):
    """
    @param  url  QUrl
    @return  bool
    """
    if not url or not url.isLocalFile():
      return False
    path = url.toLocalFile()
    suf = os.path.splitext(path)[1]
    if not suf:
      return False
    suf = suf[1:].lower()
    return suf in IMAGE_SUFFICES or suf in ('exe', 'lnk')

  @staticmethod
  def dropMimeData(mime):
    """
    @param  mime  QMimeData
    """
    try:
      url = mime.urls()[0]
      path = url.toLocalFile()
      suf = os.path.splitext(path)[1]
      suf = suf[1:].lower()
      if suf in IMAGE_SUFFICES:
        dprint("drop image")
        settings.global_().setSpringBoardWallpaperUrl(url.toString())
      elif suf in ('exe', 'lnk'):
        dprint("drop game")

        import main
        #m = main.manager()
        #f = m.openGame if settings.global_().springBoardLaunchesGame() else m.addGame
        skevents.runlater(partial(main.manager().addGame, path=path), 200)
      else:
        derror("unreachable unknown suffix: %s" % suf)
    except (AttributeError, IndexError): pass

class SpringBoard(SkDeclarativeView):
  def __init__(self, parent=None):
    import qmldialog, qmlrc, rc
    ips = (
      qmlrc.ResourceImageProvider,
      qmlrc.FileImageProvider,
      qmlrc.SpringImageProvider,
    )
    ctx = (
      ('gComet', qmldialog.Kagami.instance.globalComet),
    )
    super(SpringBoard, self).__init__(rc.qml_url('springboard'), parent,
        imageProviders=[(ip.PROVIDER_ID, ip()) for ip in ips],
        contextProperties=ctx)
    self.__d = _SpringBoard(self)

    #self.setAcceptDrops(True)
    self.rootObject().setAcceptDrops(True)

    #from sakurakit import skwin
    #hwnd = skwin.hwnd_from_wid(self.winId())
    #skwin.enable_drop_event(hwnd)
    dprint("pass")

  def setVisible(self, visible):
    """@override @public"""
    if not visible and self.isVisible():
      self.__d.saveSize()
    super(SpringBoard, self).setVisible(visible)

  ## Drag-drop events ##

  def dragEnterEvent(self, event):
    """@override @protected
    @param  event  QDragEnterEvent
    """
    dprint("enter")
    if _SpringBoard.isSupportedMimeData(event.mimeData()):
      dprint("accept")
      event.acceptProposedAction()
    else:
      dprint("rejected")
    dprint("leave")

  def dropEvent(self, event):
    """@override @protected
    @param  event  QDropEvent
    """
    dprint("enter")
    if _SpringBoard.isSupportedMimeData(event.mimeData()):
      dprint("accept")
      event.acceptProposedAction()
      _SpringBoard.dropMimeData(event.mimeData())
    else:
      dprint("rejected")
    dprint("leave")

  #def dragLeaveEvent(self, event):
  #  """@override @protected
  #  @param  event  QDragLeaveEvent
  #  """
  #  dprint("enter")
  #  event.accept()
  #  super(SpringBoard, self).dragLeaveEvent(event)
  #  dprint("leave")

# EOF
