# coding: utf8
# skmvc.py
# 10/15/2012 jichi

__all__ = (
  #'SkFilterProxyModel',
  'SkMultiFilterProxyModel',
  'SkFilterTableController',
  'SkTreeItem', 'SkTreeModel',
  'SkWidgetTreeController',
)

from PySide import QtCore, QtGui
from PySide.QtCore import Qt
from Qt5.QtCore import QSortFilterProxyModel
from Qt5 import QtWidgets
import skwidgets
from skclass import Q_Q
from sknodebug import dprint # These classes work pretty well. No need for debugging
from sktr import tr_

# Unimplemented
#class SkFilterListController(QtCore.QObject):
#  pass

## SkMultiSortFilterProxyModel ##

#class SkFilterProxyModel(QSortFilterProxyModel):
#
#  def __init__(self, parent=None):
#    super(SkFilterProxyModel, self).__init__(parent)
#
#  def isSortingEnabled(self): return self.__sortingEnabled
#  def setSortingEnabled(self, value): self.__sortingEnabled = value
#
#  def sort(self, column, order=Qt.AscendingOrder):
#    """@reimp @protected"""
#    if self.isSortingEnabled():
#      super(SkFilterProxyModel, self).sort(column, order)

class SkMultiFilterProxyModel(QSortFilterProxyModel):

  def __init__(self, parent=None, roles=(Qt.DisplayRole,)):
    """
    @param  [Qt.ItemDataRole]
    """
    super(SkMultiFilterProxyModel, self).__init__(parent)
    self.__roles = roles

  def roles(self):
    """
    @return  [Qt.ItemDataRole]
    """
    return self.__roles

  def setRoles(self, value): self.__roles = value

  def filterAcceptsRow(self, source_row, source_parent):
    """@reimp @protected
    @param  source_row  int
    @param  source_index  QModelIndex
    @return  bool
    """
    re = self.filterRegExp()
    if re.isEmpty():
      return True
    model = self.sourceModel()
    assert model

    for col in xrange(self.columnCount()):
      index = model.index(source_row, col, source_parent)
      for role in self.__roles:
        text = model.data(index, role)
        if text and re.indexIn(text) != -1:
          return True
      # If this is a tree model
      # See: http://www.qtcentre.org/threads/46471-QTreeView-Filter
      if model.rowCount(index):
        for row in xrange(model.rowCount(index)):
          #childIndex = model.index(row, col, index)
          if row != source_row and self.filterAcceptsRow(row, index):
            return True
    return False

  #def filterAcceptsColumn(self, source_row, source_parent):
  # """@reimp @protected"""
  # Unimplemented

  #def lessThan(self, left, right):
  # """@reimp @protected"""
  # Unimplemented

## SkFilterTableController ##

@Q_Q
class _SkFilterTableController(object):
  def __init__(self, q):
    self.sourceModel = QtGui.QStandardItemModel(q)

    self.proxyModel = SkMultiFilterProxyModel(q)
    self.proxyModel.setDynamicSortFilter(True)
    self.proxyModel.setSortCaseSensitivity(Qt.CaseInsensitive)
    self.proxyModel.setSourceModel(self.sourceModel)

    q_parent = q.parent()
    self._parentWidget = q_parent if isinstance(q_parent, QtWidgets.QWidget) else None
    self.treeView = QtWidgets.QTreeView(self._parentWidget)
    self.treeView.setRootIsDecorated(True)
    self.treeView.setAlternatingRowColors(True)
    self.treeView.setSortingEnabled(True)
    self.treeView.setModel(self.proxyModel)

    self.filterEdit = QtWidgets.QLineEdit()
    self.filterEdit.setPlaceholderText(tr_("Search"))
    self.filterEdit.setToolTip("%s (%s, %s)" %
        (tr_("Search"), tr_("case-insensitive"), tr_("regular expression")))

    self.countLabel = QtWidgets.QLabel()
    #self.countLabel.setToolTip(self.q.tr("Count"))

    # Connections

    # See: http://www.qtcentre.org/threads/2603-currentChanged-protected-slot-cant-get-working
    #self.treeView.activated.connect(q.currentIndexChanged)
    #self.treeView.clicked.connect(q.currentIndexChanged)
    self.selectionModel = self.treeView.selectionModel() # increase reference counting
    self.selectionModel.currentChanged.connect(q.currentIndexChanged)

    self.filterEdit.textChanged.connect(self._updateFilter)
    self.filterEdit.textChanged.connect(self._updateCount)

    self.sourceModel.dataChanged.connect(self._updateCount)

  def _updateFilter(self):
    t = self.filterEdit.text().strip()
    re = QtCore.QRegExp(t, Qt.CaseInsensitive)
    self.proxyModel.setFilterRegExp(re)

  def _updateCount(self):
    total = self.sourceModel.rowCount()
    count = self.proxyModel.rowCount()
    t = str(count) + "/" + str(total)
    self.countLabel.setText(t)

  def clearData(self):
    while self.sourceModel.rowCount():
      sourceModel.removeRow(0)
    self._updateCount()

  def removeCurrentRow(self):
    mi = self.sourceModel.currentIndex()
    if mi.isValid():
      self.proxyModel.removeRow(mi.row())
    self._updateCount()

class SkFilterTableController(QtCore.QObject):
  def __init__(self, parent=None):
    super(SkFilterTableController, self).__init__(parent)
    self.__d = _SkFilterTableController(self)
    self.__d.filterEdit.setFocus()

  ## Signals ##

  # To use the modelindex, don't forget to do index.model().mapToSource(index)
  currentIndexChanged = QtCore.Signal(QtCore.QModelIndex)

  ## Properties ##

  def model(self):
    """@return  QAbstractItemModel"""
    return self.__d.sourceModel

  def view(self):
    """@return  QTreeView"""
    return self.__d.treeView

  def filterEdit(self):
    """@return  QLineEdit"""
    return self.__d.filterEdit

  def countLabel(self):
    """@return  QLabel"""
    return self.__d.countLabel

  ## Status ##

  def isEmpty(self): return self.__d.sourceModel.rowCount() == 0

  def currentIndex(self):
    """@return  QModelIndex"""
    return self.__d.treeView.currentIndex()

  def currentData(self, col, role=Qt.DisplayRole):
    """@return  QVariant or None"""
    index = self.currentIndex()
    if not index.isValid():
      return
    row = index.row()
    index = index.sibling(row, col)
    if not index.isValid():
      return
    return index.data(role)

  def hasSelection(self): return self.currentIndex().isValid()

  ## Actions ##

  def clearSelection(self):
    null = QtCore.QModelIndex()
    self.__d.treeView.setCurrentIndex(null)
    self.currentIndexChanged.emit(null)

  def clear(self):
    """Clear data and header"""
    self.model().clear()
    self.clearSelection()

  def clearData(self):
    """Clear data only. Do not remove model header"""
    self.__d.clearData()

  def removeCurrentRow(self):
    self.__d.removeCurrentRow()

  def sortByColumn(self, col, order=Qt.AscendingOrder):
    self.__d.treeView.sortByColumn(col, order)

## SkTree ##

# See: PySide simpletreemodel example

class _SkTreeItem: pass
class SkTreeItem(object):
  def __init__(self, data, parent=None):
    """
    @param  data  [{Qt.ItemDataRole role:any}] not None
    @param  parent  Self
    """
    d = self.__d = _SkTreeItem()
    d.parentItem = parent   # Self
    d.childItems = []       # [Self]
    d.itemData = data

  def parent(self):
    """
    @return  Self
    """
    return self.__d.parentItem
  def setParent(self, value):
    self.__d.parentItem = value

  def children(self):
    """
    @return  [Self]
    """
    return self.__d.childItems
  def setChildren(self, value):
    self.__d.parentItem = value

  def childCount(self): return len(self.__d.childItems)
  def childAt(self, row):
    try: return self.__d.childItems[row]
    except IndexError: pass

  def appendChild(self, item):
    """
    @param  item Self
    """
    if item:
      item.parentItem = self
    self.__d.childItems.append(item)

  def data(self):
    """
    @return  [{Qt.ItemDataRole role:any}]
    """
    return self.__d.itemData

  def dataAt(self, column=0, role=Qt.DisplayRole):
    """
    """
    try: return self.__d.itemData[column][role]
    except (IndexError, KeyError): pass

  def columnCount(self):
    return len(self.__d.itemData)

  def row(self):
    if self.__d.parentItem:
      return self.__d.parentItem.children().index(self)
    else:
      return 0

class _SkTreeModel: pass
class SkTreeModel(QtCore.QAbstractItemModel):
  def __init__(self, root=None, parent=None):
    """
    @param  root  SkTreeItem
    @param  parent  QObject
    """
    super(SkTreeModel, self).__init__(parent)
    d = self.__d = _SkTreeModel()
    d.rootItem = root # SkTreeModel

  def rootItem(self):
    """
    @return  SkTreeItem
    """
    return self.__d.rootItem

  def setRootItem(self, value):
    self.__d.rootItem = value

  ## Overridden ##

  def columnCount(self, parent):
    """@reimp"""
    return  (parent.internalPointer().columnCount() if parent.isValid()
        else self.rootItem().columnCount() if self.rootItem()
        else 0)

  def data(self, index, role):
    """@reimp"""
    if not index.isValid(): return

    item = index.internalPointer()
    return item.dataAt(column=index.column(), role=role)

  def flags(self, index):
    """@reimp"""
    return Qt.ItemIsEnabled|Qt.ItemIsSelectable if index.isValid() else Qt.NoItemFlags

  def headerData(self, column, orientation, role):
    """@reimp"""
    if orientation == Qt.Horizontal and self.rootItem():
      return self.rootItem().dataAt(column=column, role=role)

  def index(self, row, column, parent):
    """@reimp"""
    if not self.hasIndex(row, column, parent):
      return QtCore.QModelIndex()

    if parent.isValid():
      parentItem = parent.internalPointer()
    elif self.rootItem():
      parentItem = self.rootItem()
    else:
      return QtCore.QModelIndex()

    childItem = parentItem.childAt(row)
    if childItem:
      return self.createIndex(row, column, childItem)
    else:
      return QtCore.QModelIndex()

  def parent(self, index=QtCore.QModelIndex()):
    """@reimp"""
    if not index.isValid():
      return QtCore.QModelIndex()

    childItem = index.internalPointer()
    parentItem = childItem.parent()

    if not parentItem or parentItem == self.rootItem():
      return QtCore.QModelIndex()

    return self.createIndex(parentItem.row(), 0, parentItem)

  def rowCount(self, parent=QtCore.QModelIndex()):
    """@reimp"""
    if parent.column() > 0:
      return 0

    if parent.isValid():
      parentItem = parent.internalPointer()
    elif self.rootItem():
      parentItem = self.rootItem()
    else:
      return 0

    return parentItem.childCount()

## SkWidgetTree ##

@Q_Q
class _SkWidgetTreeController(object):
  def __init__(self, q, data, container=None):
    sortingEnabled = False

    root = _SkWidgetTreeController.parseData(data) if data else None
    self.sourceModel = SkTreeModel(root=root, parent=q)

    self.proxyModel = SkMultiFilterProxyModel(q, roles=(
        Qt.DisplayRole, Qt.ToolTipRole, Qt.StatusTipRole, Qt.UserRole))
    #self.proxyModel.setSortingEnabled(sortingEnabled)
    self.proxyModel.setDynamicSortFilter(sortingEnabled)
    self.proxyModel.setSortCaseSensitivity(Qt.CaseInsensitive)
    self.proxyModel.setSourceModel(self.sourceModel)

    q_parent = q.parent()
    self._parentWidget = q_parent if isinstance(q_parent, QtWidgets.QWidget) else None
    self.treeView = QtWidgets.QTreeView(self._parentWidget)
    self.treeView.setRootIsDecorated(True)
    self.treeView.setAlternatingRowColors(True)
    self.treeView.setSortingEnabled(sortingEnabled)
    self.treeView.setModel(self.proxyModel)

    self.filterEdit = QtWidgets.QLineEdit()
    self.filterEdit.setPlaceholderText(tr_("Search"))
    self.filterEdit.setToolTip("%s (%s, %s)" %
        (tr_("Search"), tr_("case-insensitive"), tr_("regular expression")))

    self.countLabel = QtWidgets.QLabel()
    #self.countLabel.setToolTip(self.q.tr("Count"))

    self.container = container or skwidgets.SkContainerWidget(self._parentWidget)

    # Connections

    #self.treeView.activated.connect(q.currentIndexChanged)
    #self.treeView.clicked.connect(q.currentIndexChanged)
    self.selectionModel = self.treeView.selectionModel() # increase reference counting
    self.selectionModel.currentChanged.connect(self._refresh)
    self.selectionModel.currentChanged.connect(q.currentIndexChanged)

    self.filterEdit.textChanged.connect(self._updateFilter)
    self.filterEdit.textChanged.connect(self._updateCount)

    self.sourceModel.dataChanged.connect(self._updateCount)

    if self.sourceModel.rootItem():
      w = self.sourceModel.rootItem().dataAt(role=SkWidgetTreeController.WidgetRole)
      if w:
        dprint(w.__class__.__name__)
        self._setCurrentWidget(w)

  def _setCurrentWidget(self, w):
    self.container.takeWidget()
    self.container.setWidget(w)

  def _refresh(self):
    w = self.q.currentWidget()
    if w:
      dprint(w.__class__.__name__)
      self._setCurrentWidget(w)

  def _updateFilter(self):
    t = self.filterEdit.text().strip()
    re = QtCore.QRegExp(t, Qt.CaseInsensitive)
    self.proxyModel.setFilterRegExp(re)

  def _updateCount(self):
    total = self.sourceModel.rowCount()
    count = self.proxyModel.rowCount()
    t = str(count) + "/" + str(total)
    self.countLabel.setText(t)

  #def clearData(self):
  #  while self.sourceModel.rowCount():
  #    sourceModel.removeRow(0)
  #  self._updateCount()

  #def removeCurrentRow(self):
  #  mi = self.sourceModel.currentIndex()
  #  if mi.isValid():
  #    self.proxyModel.removeRow(mi.row())
  #  self._updateCount()

  def resetData(self, data):
    model = self.sourceModel
    model.beginResetModel()
    model.setRootItem(_SkWidgetTreeController.parseData(data) if data else None)
    model.endResetModel()

  @classmethod
  def parseData(cls, data):
    if not data:
      return

    m = {}

    try: m[SkWidgetTreeController.WidgetRole] = data['widget']
    except KeyError: pass

    try: m[Qt.UserRole] = data['user']
    except KeyError: pass

    try: m[Qt.DecorationRole] = data['decoration']
    except KeyError:
      try: m[Qt.DisplayRole] = m[SkWidgetTreeController.WidgetRole].windowIcon()
      except (KeyError, TypeError): pass

    try: m[Qt.DisplayRole] = data['display']
    except KeyError:
      try: m[Qt.DisplayRole] = m[SkWidgetTreeController.WidgetRole].windowTitle()
      except (KeyError, TypeError): pass

    try: m[Qt.ToolTipRole] = data['toolTip']
    except KeyError:
      tip = None
      try: tip = m[Qt.ToolTipRole] = m[SkWidgetTreeController.WidgetRole].toolTip()
      except (KeyError, TypeError): pass
      if not tip:
        try: m[Qt.ToolTipRole] = m[Qt.DisplayRole]
        except KeyError: pass

    try: m[Qt.StatusTipRole] = data['statusTip']
    except KeyError:
      tip = None
      try: tip = m[Qt.StatusTipRole] = m[SkWidgetTreeController.WidgetRole].statusTip()
      except (KeyError, TypeError): pass
      if not tip:
        try: m[Qt.StatusTipRole] = m[Qt.ToolTipRole]
        except KeyError: pass

    root = SkTreeItem((m,))

    try:
      for c in data['children']:
        item = cls.parseData(c)
        if item:
          root.appendChild(item)
    except (KeyError, TypeError): pass
    return root

class SkWidgetTreeController(QtCore.QObject):

  WidgetRole = Qt.UserRole + 10

  ROLES = {
    'display': Qt.DisplayRole,
    'toolTip': Qt.ToolTipRole,
    'statusTip': Qt.StatusTipRole,
    'decoration': Qt.DecorationRole,
    'widget': WidgetRole,
    'user': Qt.UserRole,
    'children': 0,
  }

  def __init__(self, data=None, parent=None, container=None):
    """
    @param  data  {key:value}
    @param  container  None, or any widget that has setWidget(QWidget*) and takeWidget() methods
                       Such as SkContainerWidget(default), and QScrollArea
    """
    super(SkWidgetTreeController, self).__init__(parent)
    self.__d = _SkWidgetTreeController(self, data, container)
    self.__d.filterEdit.setFocus()

  def resetData(self, data):
    """
    @param  data  {key:value}
    """
    self.__d.resetData(data)

  ## Signals ##

  # To use the modelindex, don't forget to do index.model().mapToSource(index)
  currentIndexChanged = QtCore.Signal(QtCore.QModelIndex)

  ## Properties ##

  def treeModel(self):
    """@return  QAbstractItemModel"""
    return self.__d.sourceModel

  def treeView(self):
    """@return  QTreeView"""
    return self.__d.treeView

  def widgetView(self):
    """@return  SkContainerWidget"""
    return self.__d.container

  def filterEdit(self):
    """@return  QLineEdit"""
    return self.__d.filterEdit

  def countLabel(self):
    """@return  QLabel"""
    return self.__d.countLabel

  ## Status ##

  def isEmpty(self): return self.__d.sourceModel.rowCount() == 0

  def currentIndex(self):
    """@return  QModelIndex"""
    return self.__d.treeView.currentIndex()

  #def currentData(self, col, role=Qt.DisplayRole):
  #  """@return  QVariant or None"""
  #  index = self.currentIndex()
  #  if not index.isValid():
  #    return
  #  row = index.row()
  #  index = index.sibling(row, col)
  #  if not index.isValid():
  #    return
  #  return index.data(role)

  def currentWidget(self):
    """@return  QWidget or None"""
    index = self.currentIndex()
    if not index.isValid():
      return
    row = index.row()
    col = 0
    index = index.sibling(row, col)
    if not index.isValid():
      return
    index = index.model().mapToSource(index) # index.model() is the same as d.proxyModel
    item = index.internalPointer()
    if item:
      return item.dataAt(role=self.WidgetRole)

  def hasSelection(self): return self.currentIndex().isValid()

  ## Actions ##

  #def clearSelection(self):
  #  null = QtCore.QModelIndex()
  #  self.__d.treeView.setCurrentIndex(null)
  #  self.currentIndexChanged.emit(null)

  #def clear(self):
  #  """Clear data and header"""
  #  self.model().clear()
  #  self.clearSelection()

  #def clearData(self):
  #  """Clear data only. Do not remove model header"""
  #  self.__d.clearData()

  #def removeCurrentRow(self):
  #  self.__d.removeCurrentRow()

  #def sortByColumn(self, col, order=Qt.AscendingOrder):
  #  self.__d.treeView.sortByColumn(col, order)


# EOF
