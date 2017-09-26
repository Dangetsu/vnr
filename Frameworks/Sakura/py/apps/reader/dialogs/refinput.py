# coding: utf8
# refinput.py
# 7/21/2013 jichi

if __name__ == '__main__':
  import sys
  sys.path.append('..')
  import debug
  debug.initenv()

from functools import partial
from PySide.QtCore import Qt, QObject, QTimer, Slot, Signal, Property, QRegExp, \
                          QAbstractListModel, QModelIndex
from Qt5 import QtWidgets
from Qt5.QtCore import QSortFilterProxyModel
from sakurakit import skclip, skdatetime, skevents, skqss
from sakurakit.skclass import Q_Q, memoizedproperty
from sakurakit.skdebug import dprint
#from sakurakit.skqml import QmlObject
#from sakurakit.skmvc import SkMultiFilterProxyModel
from sakurakit.sktr import tr_
from sakurakit.skwidgets import shortcut
from mytr import my, mytr_
import i18n, growl, dataman, refman, rc

class _ReferenceModel:

  @staticmethod
  def textOf(kw):

    ts = kw.get('date')
    date = i18n.timestamp2date(ts) if ts else kw.get('year') or tr_("unknown")

    title = kw.get('title')
    brand = kw.get('brand') or tr_("unknown")
    price = kw.get('price') or tr_("unknown")
    return u"%s: %s (@%s ￥%s)"% (date, title, brand, price)

    if price:
      ret += u"￥%s" %price

  @staticmethod
  def tipOf(kw):
    ret = u"同人" if kw.get('doujin') else u"企業"
    l = kw.get('creators')
    if l: ret += ', ' + ', '.join(l)
    l = kw.get('keywords')
    if l: ret += ', ' + ', '.join(l)
    return ret

class ReferenceModel(QAbstractListModel):
  def __init__(self, parent=None):
    super(ReferenceModel, self).__init__(parent)
    d = self.__d = _ReferenceModel()
    d.data = [] # [kw]
    d.locked = False  # bool

  def rowCount(self, parent=QModelIndex()):
    """@reimp @public"""
    return len(self.__d.data)

  def data(self, index, role):
    """@reimp @public"""
    if index.isValid():
      row = index.row()
      if row >= 0 and row < self.rowCount():
        if role == Qt.DisplayRole:
          return _ReferenceModel.textOf(self.get(row))
        elif role == Qt.ToolTipRole:
          return _ReferenceModel.tipOf(self.get(row))
        #elif role == Qt.UserRole:
        #  return self.get(row)

  #@Slot(int, result=dict)
  def get(self, row):
    """
    @param  row  int
    @return  {kw}
    """
    try: return self.__d.data[row]
    except IndexError: pass

  def isSearching(self): return self.__d.locked

  def search(self, text, type):
    """
    @param  text  unicode
    """
    d = self.__d
    if d.locked:
      dprint("locked")
      return
    d.locked = True
    self.beginResetModel()
    d.data = refman.manager().query(
        text=text, type=type,
        cache=False) if text else []
    dprint("data size = %s" % len(d.data))
    self.endResetModel()
    d.locked = False

@Q_Q
class _ReferenceInput(object):
  def __init__(self, q, readonly=False):
    self._createUi(q, readonly=readonly)

    shortcut('alt+s', self._save, parent=q)
    shortcut('alt+o', self._browse, parent=q)
    shortcut('alt+e', self.searchEdit.setFocus, parent=q)
    shortcut('alt+f', self.filterEdit.setFocus, parent=q)

    shortcut('alt+1', self.trailersButton.click, parent=q)
    shortcut('alt+2', self.scapeButton.click, parent=q)
    shortcut('alt+3', self.holysealButton.click, parent=q)
    shortcut('alt+4', self.freemButton.click, parent=q)

    shortcut('alt+5', self.getchuButton.click, parent=q)
    shortcut('alt+6', self.melonButton.click, parent=q)
    shortcut('alt+7', self.gyuttoButton.click, parent=q)
    shortcut('alt+8', self.digiketButton.click, parent=q)
    shortcut('alt+9', self.dmmButton.click, parent=q)
    shortcut('alt+0', self.dlsiteButton.click, parent=q)

    #shortcut('alt+0', self.amazonButton.click, parent=q)
    #shortcut('alt+0', self.steamButton.click, parent=q)

  def _createUi(self, q, readonly):

    layout = QtWidgets.QVBoxLayout()

    # Header
    row = QtWidgets.QHBoxLayout()
    row.addWidget(self.searchEdit)
    row.addWidget(self.searchLabel)
    row.addWidget(self.searchButton)
    row.addWidget(self.pasteButton)
    layout.addLayout(row)

    # Site
    grid = QtWidgets.QGridLayout()
    r = c = 0
    grid.addWidget(self.trailersButton, r, c)
    c += 1
    grid.addWidget(self.scapeButton, r, c)
    c += 1
    grid.addWidget(self.holysealButton, r, c)
    c += 1
    grid.addWidget(self.freemButton, r, c)

    r += 1; c = 0
    grid.addWidget(self.getchuButton, r, c)
    c += 1
    grid.addWidget(self.melonButton, r, c)
    c += 1
    grid.addWidget(self.gyuttoButton, r, c)
    c += 1
    grid.addWidget(self.digiketButton, r, c)
    c += 1
    grid.addWidget(self.dmmButton, r, c)
    c += 1
    grid.addWidget(self.dlsiteButton, r, c)

    r += 1; c = 0
    grid.addWidget(self.amazonButton, r, c)
    c += 1
    grid.addWidget(self.steamButton, r, c)

    layout.addLayout(grid)

    # Body
    layout.addWidget(self.modelView)

    # Footer
    row = QtWidgets.QHBoxLayout()
    row.addWidget(self.filterEdit)
    row.addWidget(self.filterLabel)
    row.addWidget(self.browseButton)
    if not readonly:
      row.addWidget(self.saveButton)
    layout.addLayout(row)

    q.setLayout(layout)

  @memoizedproperty
  def searchTimer(self):
    ret = QTimer(self.q)
    ret.setInterval(3000)
    ret.timeout.connect(self._search)
    ret.setSingleShot(True)
    return ret

  @memoizedproperty
  def trailersButton(self):
    ret = QtWidgets.QRadioButton("ErogeTrailers")
    ret.setChecked(True) # default
    ret.setToolTip("erogetrailers.co.jp (Alt+1)")
    ret.toggled.connect(self._searchLater)
    return ret

  @memoizedproperty
  def scapeButton(self):
    ret = QtWidgets.QRadioButton("ErogameScape")
    ret.setToolTip("erogamescape.dyndns.org (Alt+2)")
    ret.toggled.connect(self._searchLater)
    return ret

  @memoizedproperty
  def holysealButton(self):
    ret = QtWidgets.QRadioButton("Holyseal")
    ret.setToolTip("holyseal.net (Alt+3)")
    ret.toggled.connect(self._searchLater)
    return ret

  @memoizedproperty
  def getchuButton(self):
    ret = QtWidgets.QRadioButton("Getchu")
    ret.setToolTip("getchu.com (Alt+5)")
    ret.toggled.connect(self._searchLater)
    return ret

  @memoizedproperty
  def melonButton(self):
    ret = QtWidgets.QRadioButton("Melon")
    ret.setToolTip("melonbooks.co.jp (Alt+6)")
    ret.toggled.connect(self._searchLater)
    return ret

  @memoizedproperty
  def amazonButton(self):
    ret = QtWidgets.QRadioButton("Amazon")
    ret.setToolTip("amazon.co.jp")
    ret.toggled.connect(self._searchLater)
    return ret

  @memoizedproperty
  def dmmButton(self):
    ret = QtWidgets.QRadioButton("DMM")
    ret.setToolTip("dmm.co.jp (Alt+9)")
    ret.toggled.connect(self._searchLater)
    return ret

  @memoizedproperty
  def dlsiteButton(self):
    ret = QtWidgets.QRadioButton("DLsite")
    ret.setToolTip("dlsite.com (Alt+0)")
    ret.toggled.connect(self._searchLater)
    return ret

  @memoizedproperty
  def digiketButton(self):
    ret = QtWidgets.QRadioButton("DiGiket")
    ret.setToolTip("digiket.com (Alt+8)")
    ret.toggled.connect(self._searchLater)
    return ret

  @memoizedproperty
  def gyuttoButton(self):
    ret = QtWidgets.QRadioButton("Gyutto")
    ret.setToolTip("gyutto.com (Alt+7)")
    ret.toggled.connect(self._searchLater)
    return ret

  @memoizedproperty
  def freemButton(self):
    ret = QtWidgets.QRadioButton("FreeM")
    ret.setToolTip("freem.ne.jp (Alt+4)")
    ret.toggled.connect(self._searchLater)
    return ret

  @memoizedproperty
  def steamButton(self):
    ret = QtWidgets.QRadioButton("Steam")
    ret.setToolTip("steampowered.com")
    ret.toggled.connect(self._searchLater)
    return ret

  def _selectedType(self):
    return (
        'trailers' if self.trailersButton.isChecked() else
        'scape' if self.scapeButton.isChecked() else
        'holyseal' if self.holysealButton.isChecked() else
        'melon' if self.melonButton.isChecked() else
        'getchu' if self.getchuButton.isChecked() else
        'gyutto' if self.gyuttoButton.isChecked() else
        'dmm' if self.dmmButton.isChecked() else
        'amazon' if self.amazonButton.isChecked() else
        'dlsite' if self.dlsiteButton.isChecked() else
        'digiket' if self.digiketButton.isChecked() else
        'freem' if self.freemButton.isChecked() else
        'steam' if self.steamButton.isChecked() else
        None) # This should never happen

  @memoizedproperty
  def searchEdit(self):
    ret = QtWidgets.QLineEdit()
    #skqss.class_(ret, 'normal')
    ret.setPlaceholderText(my.tr("Type part of the game title or game ID or URL of the webpage"))
    ret.setToolTip(ret.placeholderText() +  " (Alt+E)")
    ret.textChanged.connect(self._searchLater)
    #ret.returnPressed.connect(self._search)
    return ret

  @memoizedproperty
  def searchLabel(self):
    ret = QtWidgets.QLabel()
    ret.setToolTip(tr_("Status"))
    return ret

  @memoizedproperty
  def filterLabel(self):
    ret = QtWidgets.QLabel()
    ret.setToolTip(tr_("Status"))
    self.proxyModel.rowsInserted.connect(self._refreshFilterLabel)
    self.proxyModel.rowsRemoved.connect(self._refreshFilterLabel)
    return ret

  @memoizedproperty
  def searchButton(self):
    ret = QtWidgets.QPushButton(tr_("Search"))
    skqss.class_(ret, 'btn btn-success')
    ret.setToolTip(tr_("Search") + " (Enter)")
    #ret.setStatusTip(ret.toolTip())
    ret.clicked.connect(self._search)
    return ret

  @memoizedproperty
  def pasteButton(self):
    ret = QtWidgets.QPushButton(tr_("Paste"))
    skqss.class_(ret, 'btn btn-default')
    ret.setToolTip(tr_("Paste"))
    #ret.setStatusTip(ret.toolTip())
    ret.clicked.connect(self._paste)
    return ret

  def _paste(self):
    t = skclip.gettext().strip()
    if t:
      self.searchEdit.setText(t)

  @memoizedproperty
  def filterEdit(self):
    ret = QtWidgets.QLineEdit()
    #skqss.class_(ret, 'normal')
    ret.setPlaceholderText("%s ... (%s, %s)" %
        (tr_("Filter"), tr_("regular expression"), tr_("case-insensitive")))
    ret.setToolTip("%s ... (%s, %s, Alt+F)" %
        (tr_("Filter"), tr_("regular expression"), tr_("case-insensitive")))
    ret.textChanged.connect(lambda t:
      self.proxyModel.setFilterRegExp(
        QRegExp(t.strip(), Qt.CaseInsensitive) if t else None))
    return ret

  @memoizedproperty
  def saveButton(self):
    ret = QtWidgets.QPushButton(tr_("Add"))
    skqss.class_(ret, 'btn btn-primary')
    ret.setToolTip(tr_("Save") + " (Alt+S)")
    #ret.setStatusTip(ret.toolTip())
    ret.clicked.connect(self._save)
    ret.setEnabled(False)
    return ret

  @memoizedproperty
  def browseButton(self):
    ret = QtWidgets.QPushButton(tr_("Browse"))
    skqss.class_(ret, 'btn btn-info')
    ret.setToolTip(tr_("Browse") + " (Alt+O)")
    #ret.setStatusTip(ret.toolTip())
    ret.clicked.connect(self._browse)
    ret.setEnabled(False)
    return ret

  @memoizedproperty
  def modelView(self):
    ret = QtWidgets.QListView()
    ret.setModel(self.proxyModel)
    ret.setAlternatingRowColors(True)

    sel = self._selectionModel = ret.selectionModel() # increase reference count
    sel.currentChanged.connect(self._refreshFooterButtons)
    return ret

  @memoizedproperty
  def proxyModel(self):
    #ret = SkMultiFilterProxyModel(roles=(
    #  Qt.DisplayRole, Qt.ToolTipRole,
    #))
    ret = QSortFilterProxyModel()
    ret.setDynamicSortFilter(True)
    ret.setSortCaseSensitivity(Qt.CaseInsensitive)
    ret.setSourceModel(self.sourceModel)
    ret.modelReset.connect(self._refreshFooterButtons)
    return ret

  @memoizedproperty
  def sourceModel(self):
    ret = ReferenceModel()
    return ret

  def _save(self):
    item = self._currentItem()
    if item: #and item.get('type') == self._selectedType():
      dprint("key: %s, title: %s" % (item['key'], item['title']))
      type = item['type']
      if type in ('digiket', 'gyutto', 'holyseal', 'melon', 'stream'):
        skevents.runlater(partial(self._saveNew, item), 200) # runlater so that it won't block GUI
      else:
        self.q.itemSelected.emit(item)

  def _saveNew(self, item):
    """
    @param  item  kw
    """
    kw = refman.manager().queryOne(type=item['type'], key=item['key'])
    self.q.itemSelected.emit(kw or item)

  def _browse(self):
    item = self._currentItem()
    if item and item.get('url'):
      import osutil
      osutil.open_url(item['url'])
      #key = item.get('asin')
      #if key:
      #  url = 'http://amazon.co.jp/dp/%s' % key
      #  import osutil
      #  osutil.open_url(url)

  def _searchLater(self): self.searchTimer.start()

  def _search(self):
    if self.sourceModel.isSearching():
      dprint("searching")
      return
    t = self.searchEdit.text().strip()
    #if t:
    self.searchLabel.setText("%s ..." % tr_("Searching"))
    skqss.class_(self.searchLabel, 'text-info')
    self.sourceModel.search(t, type=self._selectedType())

    count = self.sourceModel.rowCount()
    if count:
      tip = "#%s" % count
      style = 'text-info'
    else:
      tip = "%s ><" % tr_("Empty")
      style = 'text-error'
    skqss.class_(self.searchLabel, style)
    self.searchLabel.setText(tip)

  def _refreshFooterButtons(self):
    ok = bool(self.proxyModel.rowCount() and self._currentItem())
    self.saveButton.setEnabled(ok)
    self.browseButton.setEnabled(ok)

  def _refreshFilterLabel(self):
    t = self.filterEdit.text().strip()
    if not t:
      self.filterLabel.setText('')
    else:
      count = self.proxyModel.rowCount()
      if count:
        tip = "#%s" % count
      else:
        tip = "%s ><" % tr_("Empty")
      self.filterLabel.setText(tip)

  def _currentItem(self):
    """
    @return  {kw} or None
    """
    index = self.modelView.currentIndex()
    if not index.isValid():
      return
    row = index.row();
    col = 0
    index = index.sibling(row, col);
    if not index.isValid():
      return
    index = index.model().mapToSource(index) # index.model() is the same as d.proxyModel
    if index.isValid():
      return index.model().get(index.row()) # model is ReferenceModel
    #item = index.internalPointer()
    #if item:
    #  return item.dataAt(role=Qt.UserRole)

class ReferenceInput(QtWidgets.QDialog):

  def __init__(self, parent=None, readonly=False):
    WINDOW_FLAGS = Qt.Dialog|Qt.WindowMinMaxButtonsHint
    super(ReferenceInput, self).__init__(parent, WINDOW_FLAGS)
    skqss.class_(self, 'texture')
    self.__d = _ReferenceInput(self, readonly=readonly)
    #self.statusBar() # show status bar
    self.resize(500, 300)

    self.itemSelected.connect(self.hide)

  itemSelected = Signal(dict) # {kw}

  def defaultText(self): return self.__d.searchEdit.text()
  def setDefaultText(self, v): self.__d.searchEdit.setText(v)
  #def search(self): self.__d._search()

## QML ##

@Q_Q
class _QmlRefrenceInput(object):

  def __init__(self):
    self.gameId = 0 # long

  @memoizedproperty
  def dialog(self):
    import main
    m = main.manager()
    ret = ReferenceInput(m.normalWindow())
    m.hideWindowRequested.connect(ret.hide)
    ret.itemSelected.connect(self._submitItem)
    return ret

  def _submitItem(self, kw, gameId=None):
    if not gameId:
      gameId = self.gameId
    if not gameId:
      return
    r = dataman.Reference.create(
        userId=dataman.manager().user().id,
        gameId=self.gameId,
        timestamp=skdatetime.current_unixtime(),
        **kw)

    self.q.referenceSelected.emit(r)

    if r.type == 'scape':
      rm = refman.manager()
      #if r.trailers:
      #  kw = rm.queryOne(type='trailers', key=r.trailers)
      #  if kw:
      #    self._submitItem(kw, gameId=gameId)
      for type in 'dmm', 'digiket', 'gyutto':
        key = getattr(r, type)
        if key:
          kw = rm.queryOne(type=type, key=key)
          if kw:
            self._submitItem(kw, gameId=gameId)
      if r.dlsiteUrl:
        kw = rm.queryOne(type='dlsite', key=r.dlsiteUrl)
        if kw:
          self._submitItem(kw, gameId=gameId)

    elif r.type == 'trailers':
      rm = refman.manager()
      for type in 'dmm', 'amazon', 'getchu', 'gyutto', 'holyseal', 'scape':
        pty = 'erogamescape' if type == 'scape' else type
        key = getattr(r, pty)
        if key:
          kw = rm.queryOne(type=type, key=key)
          if kw:
            self._submitItem(kw, gameId=gameId)

    #elif r.type == 'trailers':
    #  rm = refman.manager()
    #  for type in 'dmm', 'amazon', 'getchu', 'scape':
    #    pty = 'erogamescape' if type == 'scape' else type
    #    key = getattr(r, pty)
    #    if key:
    #      kw = rm.queryOne(type=type, key=key)
    #      if kw:
    #        self._submitItem(kw, gameId=gameId)

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
    #winutil.set_foreground_widget(w)

class GameFinder(ReferenceInput):
  def __init__(self, parent=None):
    super(GameFinder, self).__init__(parent=parent, readonly=True)
    self.setWindowTitle(mytr_("Game Finder"))
    self.setWindowIcon(rc.icon('window-gamefinder'))

#@QmlObject
class QmlReferenceInput(QObject):
  def __init__(self, parent=None):
    super(QmlReferenceInput, self).__init__(parent)
    self.__d = _QmlRefrenceInput(self)

  referenceSelected = Signal(QObject)

  #@Slot()
  #def show(self):
  #  d = self.__d
  #  d.showWindow(d.dialog)


  @staticmethod
  def _getGameIcon(gameId):
    import dataman
    return dataman.manager().queryGameIcon(id=gameId)

  @staticmethod
  def _getGameName(gameId):
    import dataman
    dm = dataman.manager()
    for it in dm.queryReferenceData(gameId=gameId, online=False):
      if it.title:
        return it.title
    return dm.queryGameName(id=gameId)

  @Slot(int)
  def showGame(self, gameId):
    if not gameId:
      growl.notify(my.tr("Unknown game. Please try updating the database."))
      return
    d = self.__d
    d.gameId = gameId

    import dataman
    dm = dataman.manager()

    name = self._getGameName(gameId)

    title =  my.tr("Please select the game title")
    if name:
      title += " - " + name

    w = d.dialog
    w.setWindowTitle(title)

    icon = self._getGameIcon(gameId)
    w.setWindowIcon(icon or rc.icon('window-refinput'))
    if name:
      w.setDefaultText(name)
    d.showWindow(w)

  #def setGameId(self, v): self.__d.gameId = v
  #gameIdChanged = Signal(int)
  #gameId = Property(int,
  #    lambda self: self.__d.gameId,
  #    setGameId, notify=gameIdChanged)

if __name__ == '__main__':
  a = debug.app()
  w = ReferenceInput()
  w.show()
  a.exec_()

# EOF
