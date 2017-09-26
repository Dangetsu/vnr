# coding: utf8
# skqml.py
# 10/5/2012 jichi

__all__ = (
  'SkClipboardProxy',
  'SkDeclarativeDragDropEventFilter',
  'SkDeclarativeView',
  'SkDesktopProxy',
  'SkValueObject',
)

from PySide.QtCore import Property, Signal, Slot, Qt, QObject, QCoreApplication
from Qt5.QtQuick1 import QDeclarativeView
from Qt5.QtWidgets import QApplication
import skos
from skclass import Q_Q
from skdebug import dprint

if skos.WIN:
  import win32api, win32con # used to modify window ex style
  import skwin

## Containers ##

class SkValueObject(QObject):
  def __init__(self, value=None, parent=None):
    super(SkValueObject, self).__init__(parent)
    self._value = value

  #def __del__(self): print "deleted"

  def value(self): return self._value
  def setValue(self, v): self._value = v

  @Slot(result=unicode)
  def toString(self):
    try: return "%s" % self._value
    except: return 0

  @Slot(result=int)
  def toInt(self):
    try: return int(self._value)
    except: return 0

## Views ##

#@Q_Q
class _SkDeclarativeView:
  def __init__(self):
    self.draggable = False # bool
    self.dragPos = None # QPoint or None
    self.fullScreen = False # bool
    self.ignoresCloseEvent = False # bool
    self.imageProviders = None # [QDeclarativeImageProvider]

  #def setPropertyWindowVisible(self, value):
  #  root = self.q.rootObject()
  #  root.setProperty('windowVisible', value)

class SkDeclarativeView(QDeclarativeView):
  def __init__(self, source, parent=None, imageProviders=[], contextProperties=[]):
    """
    @param  source  QUrl or None
    @param  parent  QObject or None
    @param  imageProviders  [(int providerId, QDeclarativeImageProvider object)]
    @param  contextProperties  [(String key, QObject value)]
    """
    super(SkDeclarativeView, self).__init__(parent)

    if imageProviders:
      for providerId, providerObject in imageProviders:
        self.engine().addImageProvider(providerId, providerObject)

    #ctx = (
    #  ('qApp', QCoreApplication.instance()),
    #)
    self.rootContext().setContextProperty('qApp', QCoreApplication.instance())
    if contextProperties:
      for var, value in contextProperties:
        self.rootContext().setContextProperty(var, value)

    if source:
      self.setSource(source)

    self.__d = _SkDeclarativeView()
    self.__d.imageProviders = imageProviders # retain reference count of the image provider

    # Resize view to window
    self.setResizeMode(QDeclarativeView.SizeRootObjectToView)

    self.engine().quit.connect(self.hide)

    root = self.rootObject()
    if root:
      if root.property('translucent'):
        self.setTranslucent()

      var = root.property('windowVisible')
      if var is not None:
        assert isinstance(var, bool), "check type"
        #self.setVisible(var) # note: the initial value is ignored
        # Double-binded property
        self.visibleChanged.connect(self.updateVisible)
        root.windowVisibleChanged.connect(self.updateWindowVisible)

      var = root.property('windowFlags')
      if var is not None:
        assert isinstance(var, (int, long)), "check type" # Qt.WindowFlags
        self.setWindowFlags(var)
        root.windowFlagsChanged.connect(self.updateWindowFlags)

      var = root.property('windowTitle')
      if var is not None:
        assert isinstance(var, unicode), "check type"
        self.setWindowTitle(var)
        root.windowTitleChanged.connect(self.updateWindowTitle)

      var = root.property('draggable')
      if var is not None:
        assert isinstance(var, bool), "check type"
        self.setDraggable(var)
        root.draggableChanged.connect(self.updateDraggable)

      var = root.property('fullScreen')
      if var is not None:
        assert isinstance(var, bool), "check type"
        self.setNeedsFullScreen(var)
        root.fullScreenChanged.connect(self.updateNeedsFullScreen)

      var = root.property('ignoresCloseEvent')
      if var is not None:
        assert isinstance(var, bool), "check type"
        self.setIgnoresCloseEvent(var)
        root.ignoresCloseEventChanged.connect(self.updateIgnoresCloseEvent)

      var = root.property('ignoresFocus')
      if var is not None:
        assert isinstance(var, bool), "check type"
        self.setIgnoresFocus(var)
        root.ignoresFocusChanged.connect(self.updateIgnoresFocus)

  ## Properties ##

  def updateVisible(self):
    t = self.isVisible()
    if self.rootObject().property('windowVisible') != t:
      self.rootObject().setProperty('windowVisible', t)

  def updateWindowVisible(self):
    t = self.rootObject().property('windowVisible')
    if self.isVisible() != t:
      self.setVisible(t)
      dprint("visible = %s" % t)

  def updateWindowFlags(self):
    self.setWindowFlags(self.rootObject().property('windowFlags'))

  def updateWindowTitle(self):
    self.setWindowTitle(self.rootObject().property('windowTitle'))

  def isDraggable(self):
    return self.__d.draggable
  def setDraggable(self, value):
    self.__d.draggable = value
  def updateDraggable(self):
    self.setDraggable(self.rootObject().property('draggable'))

  def needsFullScreen(self):
    return self.__d.fullScreen
  def setNeedsFullScreen(self, value):
    self.__d.fullScreen = value
  def updateNeedsFullScreen(self):
    self.setNeedsFullScreen(self.rootObject().property('fullScreen'))

  def ignoresCloseEvent(self):
    return self.__d.ignoresCloseEvent
  def setIgnoresCloseEvent(self, value):
    self.__d.ignoresCloseEvent = value
  def updateIgnoresCloseEvent(self):
    self.setIgnoresCloseEvent(self.rootObject().property('ignoresCloseEvent'))

  def ignoresFocus(self):
    if skos.WIN:
      hwnd = skwin.hwnd_from_wid(self.winId())
      style = win32api.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
      return bool(style & win32con.WS_EX_NOACTIVATE)
    else:
      return False

  def setIgnoresFocus(self, value):
    if skos.WIN:
      dprint("value = %s" % value)
      hwnd = skwin.hwnd_from_wid(self.winId())
      style = win32api.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
      if value != bool(style & win32con.WS_EX_NOACTIVATE):
        style = (style | win32con.WS_EX_NOACTIVATE if value else
                 style & ~win32con.WS_EX_NOACTIVATE)
        #win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
        win32api.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style)
        #win32gui.ShowWindow(hwnd, win32con.SW_SHOW)

  def updateIgnoresFocus(self):
    self.setIgnoresFocus(self.rootObject().property('ignoresFocus'))

  # Cannot be reverted
  def setTranslucent(self):
    self.setAttribute(Qt.WA_TranslucentBackground)
    #skqss.class_(self, 'transp')
    self.setStyleSheet("QDeclarativeView{background-color:transparent}")

  ## Events ##

  visibleChanged = Signal(bool)
  def setVisible(self, value):
    """@reimp @public @slot"""
    super(SkDeclarativeView, self).setVisible(value)
    self.visibleChanged.emit(value)

  def closeEvent(self, event):
    """@reimp @protected"""
    if self.ignoresCloseEvent() and self.isVisible():
      event.ignore()
    else:
      super(SkDeclarativeView, self).closeEvent(event)

  def show(self):
    """@reimp* @public
    show is not virtual in Qt, while setVisible is not overridden.
    Expect bug in the future
    """
    if self.needsFullScreen():
      self.showFullScreen()
    else:
      super(SkDeclarativeView, self).show()
    self.raise_()

  def showFullScreen(self):
    """@reimp* @public
    showFullScreen is not virtual in Qt. Should override changeEvent
    """
    if skos.POSIX:
      rect = (QApplication.desktop().screenGeometry(self) if skos.MAC else
              QApplication.desktop().availableGeometry(self)) # linux
      self.setGeometry(rect)
      self.move(0, 0)
      super(SkDeclarativeView, self).show()
    else:
      super(SkDeclarativeView, self).showFullScreen()

  def mousePressEvent(self, event):
    """@reimp @protected"""
    if (self.__d.draggable and
        not(self.windowFlags() & (Qt.WindowMaximized | Qt.WindowFullScreen)) and
        event.button() == Qt.LeftButton and self.__d.dragPos is None):
      self.__d.dragPos = event.globalPos() - self.frameGeometry().topLeft()
      event.accept()
    super(SkDeclarativeView, self).mousePressEvent(event)

  def mouseMoveEvent(self, event):
    """@reimp @protected"""
    if (self.__d.draggable and
        not(self.windowFlags() & (Qt.WindowMaximized | Qt.WindowFullScreen)) and
        (event.buttons() & Qt.LeftButton) and self.__d.dragPos is not None):
      self.move(event.globalPos() - self.__d.dragPos)
      event.accept()
    super(SkDeclarativeView, self).mouseMoveEvent(event)

  def mouseReleaseEvent(self, event):
    """@reimp @protected"""
    self.__d.dragPos = None
    super(SkDeclarativeView, self).mouseReleaseEvent(event)

## Proxies ##

@Q_Q
class _SkClipboardProxy(object):
  def __init__(self):
    QApplication.clipboard().dataChanged.connect(
        self._onDataChanged)

  def _onDataChanged(self):
    q = self.q
    q.textChanged.emit(q.text)

#@QmlObject
class SkClipboardProxy(QObject):
  def __init__(self, parent=None):
    super(SkClipboardProxy, self).__init__(parent)
    self.__d = _SkClipboardProxy(self)

    QApplication.clipboard().dataChanged.connect(lambda:
        self.textChanged.emit(self.text))

  textChanged = Signal(unicode)
  text = Property(unicode,
      lambda _: QApplication.clipboard().text(),
      lambda _, v: QApplication.clipboard().setText(v),
      notify=textChanged)

#@QmlObject
class SkDesktopProxy(QObject):
  def __init__(self, parent=None):
    super(SkDesktopProxy, self).__init__(parent)
    d = QCoreApplication.instance().desktop()
    d.resized.connect(self.refresh)

  def refresh(self):
    self.xChanged.emit(self.x)
    self.yChanged.emit(self.y)
    self.widthChanged.emit(self.width)
    self.heightChanged.emit(self.height)
    dprint("pass")

  def __property(type, method):
    """
    @param  type  type
    @param  method  method
    """
    sig = Signal(type)
    prop = Property(type, method, notify=sig)
    return prop, sig

  x, xChanged = __property(int,
      lambda _: QCoreApplication.instance().desktop().x())
  y, yChanged = __property(int,
      lambda _: QCoreApplication.instance().desktop().y())
  width, widthChanged = __property(int,
      lambda _: QCoreApplication.instance().desktop().width())
  height, heightChanged = __property(int,
      lambda _: QCoreApplication.instance().desktop().height())

# EOF

#def QmlObjectInit(init):
#  """
#  @param  init  must be __init__(self, ...)
#  """
#  # wraps is disabled, because it is only used to get __doc__, and could cause trouble when no __init__ is defined
#  #@wraps(init)
#  #def retain(self):
#  #  if shiboken.isValid(self):
#  #    self.setParent(QCoreApplication.instance())
#
#  def newinit(*args, **kwargs):
#    assert args, "the first argument of a class must be self"
#    init(*args, **kwargs)
#    self = args[0]
#    assert isinstance(self, QObject), "qmlobject must be an qobject"
#    if not QObject.parent(self):
#      qApp = QCoreApplication.instance()
#      self.setParent(qApp)
#    #  QCoreApplication.instance().aboutToQuit.connect(partial(retain, self))
#  return newinit
#
#def QmlPersistentObject(cls):
#  """
#  @param  cls  QObject
#  """
#  assert issubclass(cls, QObject), "qmlobject must be a qobject"
#  cls.__init__ = QmlObjectInit(cls.__init__)
#  return cls

# Helpers -

#from functools import partial, wraps
#import shiboken
#from PySide import shiboken
#
#def QmlItem(cls):
#  """
#  @param  cls  QDeclarativeItem
#  """
#  assert issubclass(cls, QDeclarativeItem), "qmlitem must be a graphics item"
#  return cls

# See: https://bitbucket.org/gregschlom/qml-drag-drop
#class SkDeclarativeDragDropEventFilter(QObject):
#  def __init__(self, parent):
#    super(SkDeclarativeDragDropEventFilter, self).__init__(parent)
#
#  def eventFilter(self, watched, event):
#    """@override @public"""
#    if isinstance(event, QGraphicsSceneDragDropEvent):
#      pass
#    return super(SkDeclarativeDragDropEventFilter, self).eventFilter(watched, event)

