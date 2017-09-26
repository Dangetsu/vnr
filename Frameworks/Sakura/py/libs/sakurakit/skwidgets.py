# coding: utf8
# skwidgets.py
# 10/5/2012 jichi

__all__ = (
  'to_wid', 'shortcut', 'clear_layout',
  'SkButtonRow',
  'SkContainerWidget',
  'SkDraggableWidget', 'SkDraggableMainWindow',
  'SkWidgetLayout', 'SkLayoutWidget',
  'SkRadioButtonGrid',
  'SkTabPane',
  'SkTextEditWithAnchor',
  'SkTitlelessDockWidget',
  'SkStyleView',
)

from PySide.QtCore import Qt
from PySide import QtCore, QtGui
from Qt5 import QtWidgets
import skpyapi
from sktr import tr_
from skclass import Q_Q

def to_wid(lp):
  return skpyapi.pycobj_from_lp(lp)

## Helpers ##

def shortcut(key, slot, parent=None):
  """
  @param  key  str or QKeySequence
  @param  slot  function
  @param  parent  QWidget
  @return QShortcut
  """
  if (parent is None and
      hasattr(slot, '__self__') and
      isinstance(slot.__self__, QtWidgets.QWidget)):
    parent = slot.__self__
  if not isinstance(key, QtGui.QKeySequence):
    key = QtGui.QKeySequence(key)
  return QtWidgets.QShortcut(key, parent, slot)

#def del_all(obj):
#  for c in obj.children():
#    del_all(c)
#  del obj

# See: http://doc.qt.digia.com/qt/qlayout.html#takeAt
# See: http://stackoverflow.com/questions/4272196/qt-remove-all-widgets-from-layout
def clear_layout(layout, delwidget=False):
  """
  @param  layout  QLayout
  @param  delwidget  bool
  """
  if layout:
    while not layout.isEmpty():
      item = layout.takeAt(0) # QLayoutItem
      if delwidget:
        widget = item.widget()
        if widget:
          widget.hide() # FIXME: memory leak here
          #del widget
        item_as_layout = item.layout() # cast item to layout
        if item_as_layout:
          clear_layout(item_as_layout, delwidget=delwidget)
      #del item

## Draggable ##

class _SkDraggableWidget:
  def __init__(self):
    self.draggable = True # bool
    self.pos = None # int, int
class SkDraggableWidget(QtWidgets.QWidget):
  def __init__(self, parent=None, f=0):
    super(SkDraggableWidget, self).__init__(parent, f)
    self.__d = _SkDraggableWidget()

  def isDraggable(self): return self.__d.draggable
  def setDraggable(self, t): self.__d.draggable = t

  def mousePressEvent(self, event): # override;
    d = self.__d
    if d.draggable and not d.pos and event.button() == Qt.LeftButton and not self.isMaximized() and not self.isFullScreen():
      d.pos = event.globalPos() - self.frameGeometry().topLeft()
      event.accept()
    super(SkDraggableWidget, self).mousePressEvent(event)

  def mouseMoveEvent(self, event): # override;
    d = self.__d
    if d.draggable and d.pos and not self.isMaximized() and not self.isFullScreen():
      self.move(event.globalPos() - d.pos)
      event.accept()
    super(SkDraggableWidget, self).mouseMoveEvent(event)

  def mouseReleaseEvent(self, event): # override;
    self.__d.pos = None
    super(SkDraggableWidget, self).mouseReleaseEvent(event)

class _SkDraggableMainWindow:
  def __init__(self):
    self.draggable = True # bool
    self.pos = None # int, int
class SkDraggableMainWindow(QtWidgets.QMainWindow):
  def __init__(self, parent=None, f=0):
    super(SkDraggableMainWindow, self).__init__(parent, f)
    self.__d = _SkDraggableMainWindow()

  def isDraggable(self): return self.__d.draggable
  def setDraggable(self, t): self.__d.draggable = t

  def mousePressEvent(self, event): # override;
    d = self.__d
    if d.draggable and not d.pos and event.button() == Qt.LeftButton and not self.isMaximized() and not self.isFullScreen():
      d.pos = event.globalPos() - self.frameGeometry().topLeft()
      event.accept()
    super(SkDraggableMainWindow, self).mousePressEvent(event)

  def mouseMoveEvent(self, event): # override;
    d = self.__d
    if d.draggable and d.pos and not self.isMaximized() and not self.isFullScreen():
      self.move(event.globalPos() - d.pos)
      event.accept()
    super(SkDraggableMainWindow, self).mouseMoveEvent(event)

  def mouseReleaseEvent(self, event): # override;
    self.__d.pos = None
    super(SkDraggableMainWindow, self).mouseReleaseEvent(event)

## Widgets ##

class SkStyleView(QtWidgets.QDialog): # So that it can be stylize
  def __init__(self, parent=None):
    super(SkStyleView, self).__init__(parent, Qt.Window)

class SkTitlelessDockWidget(QtWidgets.QDockWidget):
  def __init__(self, widget=None, parent=None):
    super(SkTitlelessDockWidget, self).__init__(parent)
    self.setTitleBarWidget(QtWidgets.QWidget())
    #self.setContentsMargins(0, 0, 0, 0)
    if widget:
      self.setWidget(widget)

class SkWidgetLayout(QtWidgets.QHBoxLayout):
  def __init__(self, widget, parent=None):
    super(SkWidgetLayout, self).__init__(parent)
    self.addWidget(widget)

class SkLayoutWidget(QtWidgets.QWidget):
  def __init__(self, layout, parent=None):
    super(SkLayoutWidget, self).__init__(parent)
    self.setLayout(layout)

class _SkButtonRow:
  def __init__(self, q):
    self.count = 0
    self.group = QtWidgets.QButtonGroup(q)
    self.group.buttonClicked[int].connect(q.currentIndexChanged)

  #def _updateSize(self):
  #  q = self.q
  #  sz = q.sizeHint()
  #  q.setMinimumSize(sz)
  #  q.resize(sz)

class SkButtonRow(QtWidgets.QToolBar):
  """Static tab widget. Tab bar implemented using tool bar"""

  def __init__(self, parent=None, f=0):
    """
    @param  parent  QWidget or None
    @param  f  Qt.WindowFlags
    """
    super(SkButtonRow, self).__init__(parent, f)
    self.__d = _SkButtonRow(self)

    self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
    self.setFloatable(False)
    self.setMovable(False)

  #def sizeHint(self):
  #  """@reimp @public"""
  #  ret = self.centralWidget().sizeHint()
  #  #ret.setHeight(ret.height + self.statusBar().sizeHint().height())
  #  return ret

  currentIndexChanged = QtCore.Signal(int)

  def addButton(self, text="", icon=None, tip=None, checkable=True, styleClass=None):
    """
    @param* text  unicode
    @param* icon  QIcon or None
    @param* checkable  bool
    @param* styleClass  unicode
    @return QAbstractButton
    """
    d = self.__d
    act = (self.addAction(icon, text) if icon else
           self.addAction(text))
    if checkable:
      act.setCheckable(checkable)
    if tip:
      act.setToolTip(tip)
      act.setStatusTip(tip)
    button = self.widgetForAction(act)
    d.group.addButton(button, d.count)
    d.count += 1
    if d.count == 1:
      act.setChecked(True)
    #shortcut("ctrl+%i" % d.count, button.click)
    return button

  def count(self):
    return self.__d.count

  def currentIndex(self):
    return self.__d.group.checkedId()

  def setCurrentIndex(self, index):
    if index != self.currentIndex():
      b = self.__d.group.button(index)
      if b:
        b.click()

  def currentWidget(self):
    return self.__d.group.checkedButton()

# See: http://www.qtforum.org/article/1045/dynamically-add-widgets-to-layout.html
@Q_Q
class _SkRadioButtonGrid(object):
  def __init__(self, q, col=0):
    self._layout = None
    self.col = col
    self.count = 0

  @property
  def layout(self):
    """
    @return  QGridLayout not None
    """
    if not self._layout:
      self._layout = QtWidgets.QGridLayout()
    return self._layout

  @layout.setter
  def layout(self, value): self._layout = value

  def _onClicked(self):
    self.q.currentIndexChanged.emit(self.q.currentIndex())

  def createItem(self):
    b = QtWidgets.QRadioButton()
    b.clicked.connect(self._onClicked)

    c = self.count % self.col
    r = self.count / self.col
    self.layout.addWidget(b, r, c)
    self.count += 1
    return b

class SkRadioButtonGrid(QtCore.QObject):

  ## Construction ##

  def __init__(self, parent=None, col=1):
    super(SkRadioButtonGrid, self).__init__(parent)
    self.__d = _SkRadioButtonGrid(self, col)

  def setColumnCount(self, count): self.__d.col = count
  def columnCount(self): return self.__d.col

  def setLayout(self, layout): self.__d.layout = layout
  def layout(self): return self.__d.layout

  ## Signals ##

  currentIndexChanged = QtCore.Signal(int)

  ## Queries ##

  def count(self): return self.__d.count
  def isEmpty(self): return self.__d.count == 0

  def hasSelection(self): return self.currentIndex() >= 0

  def currentIndex(self):
    if not self.isEmpty():
      layout = self.layout()
      for i in xrange(self.count()):
        b = layout.itemAt(i).widget()
        if b.isChecked():
          return i
    return -1

  def buttonAt(self, index):
    """
    @return  QPushButton or None
    """
    return self.layout().itemAt(index).widget() if index >= 0 and index < self.count() else None

  def currentButton(self):
    """
    @return  QPushButton or None
    """
    return self.buttonAt(self.currentIndex())

  def currentText(self):
    """
    @return  unicode
    """
    b = self.currentButton()
    return b.text() if b else ""

  def currentToolTip(self):
    """
    @return  unicode
    """
    b = self.currentButton()
    return b.toolTip() if b else ""

  def currentValue(self):
    """
    @return  any
    """
    b = self.currentButton()
    return b.value if b else None

  ## Actions ##

  def setCurrentIndex(self, index):
    b = self.buttonAt(index)
    if b:
      b.click()

  def addButton(self, text="", tip="", value=None):
    """
    @param* text  unicode
    @param* tip  unicode
    @param* value  any
    @return  QRadioButton
    """
    d = self.__d
    if d.count >= d.layout.count():
      b = d.createItem()
    else:
      b = d.layout.itemAt(d.count).widget()
      d.count += 1

    b.value = value
    b.setText(text)
    b.setToolTip(tip)
    b.show()
    return b

  def clear(self):
    layout = self.__d.layout
    for i in xrange(self.count()):
      b = layout.itemAt(i).widget()
      b.hide()
    self.__d.count = 0

@Q_Q
class _SkTabPane(object):
  def __init__(self, q):
    self._createUi(q)

    self.group = QtWidgets.QButtonGroup(q)
    self.group.buttonClicked[int].connect(self.stack.setCurrentIndex)
    self.stack.currentChanged.connect(q.updateSize)
    self.stack.currentChanged.connect(q.currentIndexChanged)

  def _createUi(self, q):
    self.stack = QtWidgets.QStackedWidget()
    self.toolBar = q.addToolBar(tr_("Tab"))
    self.toolBar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
    self.toolBar.setFloatable(False)
    self.toolBar.setMovable(False)

    q.setCentralWidget(self.stack)

class SkTabPane(QtWidgets.QMainWindow):
  """Static tab widget. Tab bar implemented using tool bar"""

  def __init__(self, parent=None, f=0):
    """
    @param  parent  QWidget or None
    @param  f  Qt.WindowFlags
    """
    super(SkTabPane, self).__init__(parent, f)
    self.__d = _SkTabPane(self)

  def sizeHint(self):
    """@reimp @public"""
    ret = self.centralWidget().sizeHint()
    #ret.setHeight(ret.height + self.statusBar().sizeHint().height())
    return ret

  currentIndexChanged = QtCore.Signal(int)

  def addTab(self, tab, text="", icon=None, tip=None):
    """
    @param  tab  QWidget
    @param* text  unicode
    @param* icon  QIcon or None
    @param* tip  unicode or None
    """
    d = self.__d
    act = (d.toolBar.addAction(icon, text) if icon else
           d.toolBar.addAction(text))
    if tip:
      act.setToolTip(tip)
      act.setStatusTip(tip)
    act.setCheckable(True)
    button = d.toolBar.widgetForAction(act)

    d.group.addButton(button, d.stack.count())
    d.stack.addWidget(tab)
    if d.stack.count() == 1:
      act.setChecked(True)
    shortcut("ctrl+%i" % self.count(), button.click)

  def count(self):
    return self.__d.stack.count()

  def currentIndex(self):
    return self.__d.stack.currentIndex()

  def setCurrentIndex(self, index):
    b = self.group.button(index)
    if b:
      b.click()

  def currentWidget(self):
    return self.__d.stack.currentWidget()

  #def setVisible(self, value):
  #  """@reimp @public"""
  #  if value:
  #    skevents.runlater(self.updateSize)
  #  super(SkTabPane, self).setVisible(value)

  def updateSize(self):
    sz = self.sizeHint()
    self.setMinimumSize(sz)
    self.resize(sz)

## Container widget ##

class SkContainerWidget(QtWidgets.QStackedWidget):

  def takeWidget(self):
    """
    @param  remove current widget
    """
    ret = self.currentWidget()
    if ret:
      self.removeWidget(ret)
    return ret

  def setWidget(self, widget):
    """
    @param  widget  QWidget
    """
    if not widget:
      return
    index = self.indexOf(widget)
    if index == -1:
      index = self.addWidget(widget)
    self.setCurrentWidget(widget)

## TextEdit ##

class SkTextEditWithAnchor(QtWidgets.QTextEdit):
  def __init__(self, *args, **kwargs):
    super(SkTextEditWithAnchor, self).__init__(*args, **kwargs)
    #self.setMouseTracking(True) # needed for over event

  anchorClicked = QtCore.Signal(unicode, int, int) # anchor, x, y

  def mouseReleaseEvent(self, ev):
    """@reimp"""
    anchor = self.anchorAt(ev.pos())
    if anchor:
      self.anchorClicked.emit(anchor, ev.globalX(), ev.globalY())
    super(SkTextEditWithAnchor, self).mouseReleaseEvent(ev)

  #def mouseMoveEvent(self, ev):
  #  """@reimp"""
  #  if self.anchorAt(ev.pos()):
  #    QtWidgets.QApplication.setOverrideCursor(Qt.PointingHandCursor)
  #  else:
  #    QtWidgets.QApplication.restoreOverrideCursor()
  #  super(SkTextEditWithAnchor, self).mouseMoveEvent(ev)

# EOF

#
#class SkCheckBox(QtWidgets.QCheckBox):
#  def __init__(self, parent=None):
#    super(SkCheckBox, self).__init__(parent)
#
#  #def __init__(self, text, parent=None):
#  #  super(SkCheckBox, self).__init__(text, parent)
#
#  def enterEvent(self, event):
#    """@reimp @protected"""
#    self.setCursor(Qt.PointingHandCursor)
#    super(SkCheckBox, self).enterEvent(event)
#
#  def leaveEvent(self, event):
#    """@reimp @protected"""
#    self.setCursor(Qt.ArrowCursor)
#    super(SkCheckBox, self).leaveEvent(event)
#
#class SkPushButton(QtWidgets.QPushButton):
#  def __init__(self, parent=None):
#    super(SkPushButton, self).__init__(parent)
#
#  #def __init__(self, text, parent=None):
#  #  super(SkPushButton, self).__init__(text, parent)
#
#  #def __init__(self, icon, text, parent=None):
#  #  super(SkPushButton, self).__init__(icon, text, parent)
#
#  def enterEvent(self, event):
#    """@reimp @protected"""
#    self.setCursor(Qt.PointingHandCursor)
#    super(SkPushButton, self).enterEvent(event)
#
#  def leaveEvent(self, event):
#    """@reimp @protected"""
#    self.setCursor(Qt.ArrowCursor)
#    super(SkPushButton, self).leaveEvent(event)
#
#class SkRadioButton(QtWidgets.QRadioButton):
#  def __init__(self, parent=None):
#    super(SkRadioButton, self).__init__(parent)
#
#  #def __init__(self, text, parent=None):
#  #  super(SkRadioButton, self).__init__(text, parent)
#
#  def enterEvent(self, event):
#    """@reimp @protected"""
#    self.setCursor(Qt.PointingHandCursor)
#    super(SkRadioButton, self).enterEvent(event)
#
#  def leaveEvent(self, event):
#    """@reimp @protected"""
#    self.setCursor(Qt.ArrowCursor)
#    super(SkRadioButton, self).leaveEvent(event)
#
#class SkToolButton(QtWidgets.QToolButton):
#  def __init__(self, parent=None):
#    super(SkToolButton, self).__init__(parent)
#
#  def enterEvent(event):
#    """@reimp @protected"""
#    self.setCursor(Qt.PointingHandCursor)
#    super(SkToolButton, self).enterEvent(event)
#
#  def leaveEvent(event):
#    """@reimp @protected"""
#    self.setCursor(Qt.ArrowCursor)
#    super(SkToolButton, self).leaveEvent(event)
#
