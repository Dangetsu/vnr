# coding: utf8
# nameinput.py
# 1/3/2015 jichi

__all__ = 'NameInputManager',

if __name__ == '__main__':
  import sys
  sys.path.append('..')
  import debug
  debug.initenv()

import re
from functools import partial
from PySide.QtCore import Qt #, Signal
from Qt5 import QtWidgets
from sakurakit import skqss
from sakurakit.skclass import memoized, memoizedproperty
from sakurakit.sktr import tr_
from sakurakit.skwidgets import SkLayoutWidget
from opencc import opencc
from mytr import my, mytr_
import rc, growl

_RE_NAME_SPLIT = re.compile(u"[ \u3000・=＝]")
def _split_name(s): # unicode -> [unicode]
  return filter(bool, _RE_NAME_SPLIT.split(s))

NAME_EDIT_MIN_WIDTH = 100
INFO_EDIT_MIN_WIDTH = 200

@memoized
def manager(): return NameInputManager()

class NameInputManager:
  def __init__(self, parent=None):
    self.__d = _NameInputManager()

    from PySide.QtCore import QCoreApplication
    qApp = QCoreApplication.instance()
    qApp.aboutToQuit.connect(self.hide)

    import dataman
    dataman.manager().loginChanged.connect(lambda name: name or self.hide())

    #import netman
    #netman.manager().onlineChanged.connect(lambda t: t or self.hide())

  #def clear(self): self.hide()

  def isVisible(self):
    if self.__d.dialogs:
      for w in self.__d.dialogs:
        if w.isVisible():
          return True
    return False

  def hide(self):
    if self.__d.dialogs:
      for w in self.__d.dialogs:
        if w.isVisible():
          w.hide()

  def showGame(self, tokenId=0, itemId=0, info=None):
    """
    @param* tokenId  long
    @param* itemId  long
    @param* info  GameInfo
    """
    if not info:
      import dataman
      info = dataman.manager().queryGameInfo(itemId=itemId, id=tokenId, cache=True)
      if info and not tokenId:
        tokenId = info.gameId

    if not info or not tokenId:
      growl.notify(my.tr("Unknown game"))
      return
    if not info.hasNames():
      growl.notify(my.tr("Game character names not found"))
      return

    w = self.__d.getDialog(tokenId)
    if w and w.isVisible() and w.tokenId() == tokenId:
      w.raise_()
    else:
      w.setGameName(info.title)
      w.setWindowIcon(info.icon or rc.icon('window-name'))
      w.setTokenId(tokenId)
      w.setNames(info.iterNameYomi())
      w.show()

#@Q_Q
class _NameInputManager:
  def __init__(self):
    self.dialogs = []

  @staticmethod
  def _createDialog():
    import windows
    parent = windows.top()
    ret = NameInput(parent)
    ret.resize(640, 480)
    return ret

  def getDialog(self, tokenId): # long -> QWidget
    for w in self.dialogs:
      if w.isVisible() and w.tokenId() == tokenId:
        return w
    for w in self.dialogs:
      if not w.isVisible():
        #w.clear() # use last input
        return w
    ret = self._createDialog()
    self.dialogs.append(ret)
    return ret

#class NameInput(QtWidgets.QDialog):
class NameInput(QtWidgets.QScrollArea):
  #termEntered = Signal(QtCore.QObject) # Term

  def __init__(self, parent=None):
    WINDOW_FLAGS = Qt.Dialog|Qt.WindowMinMaxButtonsHint
    super(NameInput, self).__init__(parent)
    self.setWindowFlags(WINDOW_FLAGS)
    skqss.class_(self, 'texture')
    self.setWindowTitle(my.tr("Create dictionary entry"))
    self.setWindowIcon(rc.icon('window-name'))
    self.setWidgetResizable(True) # automatically stretch widgets
    self.__d = _NameInput(self)

  def clear(self):
    self.__d.clear()

  def setGameName(self, name):
    """
    @param  tokenId  long
    """
    title = my.tr("Create dictionary entry")
    if name:
      self.setWindowTitle("%s - %s" % (title, name))
    else:
      self.setWindowTitle(title)

  def tokenId(self): return self.__d.tokenId
  def setTokenId(self, tokenId):
    """
    @param  tokenId  long
    """
    self.__d.tokenId = tokenId

  def addName(self, name, yomi):
    """
    @param  name  unicode
    @param  yomi  unicode
    """
    d = self.__d
    for it in d.iterNameYomi(name, yomi):
      d.addName(*it)

  def setNames(self, l):
    """
    @param  l  [unicode name, unicode yomi]
    """
    self.clear()
    for name,yomi in l:
      self.addName(name, yomi)

  #def setVisible(self, value):
  #  """@reimp @public"""
  #  if value and not self.isVisible():
  #    self.__d.refresh()
  #  super(NameInput, self).setVisible(value)

#@Q_Q
class _NameInput(object):
  def __init__(self, q):
    self.tokenId = 0 # long

    self.rows = [] # [{'name':unicode, 'yomi':unicode, 'info':unicode, 'nameButton':QPushButton, 'yomiButton':QPushButton, 'nameTtsButton':QPushButton, 'nameEdit':QLabel, 'yomiEdit':QLabel, 'infoEdit':QLabel}]
    self.visibleRowCount = 0 # int

    self.grid = QtWidgets.QGridLayout()

    self._createLayout(q)

  def _createLayout(self, q):
    #q.setLayout(self.grid)
    w = SkLayoutWidget(self.grid)
    q.setWidget(w)

  def clear(self):
    if self.visibleRowCount:
      for i in range(self.visibleRowCount):
        for w in self.rows[i].itervalues():
          if isinstance(w, QtWidgets.QWidget):
            w.hide()
      self.visibleRowCount = 0

  #def refresh(self):
  #  pass

  def iterNameYomi(self, name, yomi):
    """
    @param  name  unicode
    @param  yomi  unicode
    @yield  (unicode name, unicode yomi, unicode info)
    """
    noyomi = not yomi or yomi == name
    info = name
    if not noyomi:
      info += " (%s)" % yomi
    yield name, yomi, info

    namelist = _split_name(name)
    if len(namelist) > 1:
      if noyomi:
        yield namelist[0], None, info
        yield namelist[-1], None, info
      else:
        yomilist = _split_name(yomi)
        if len(namelist) == len(yomilist):
          yield namelist[0], yomilist[0], info
          yield namelist[-1], yomilist[-1], info

  def addName(self, name, yomi, info):
    """
    @param  name  unicode
    @param  yomi  unicode
    @param  info  unicode
    @return  kw
    """
    row = self._getNextRow()
    row['name'] = name
    row['yomi'] = yomi
    row['info'] = info
    row['nameEdit'].setText(name)
    row['yomiEdit'].setText(yomi if yomi and yomi != name else '-')
    row['infoEdit'].setText(info)

  def _getNextRow(self):
    rowCount = len(self.rows)
    if rowCount > self.visibleRowCount:
      row = self.rows[self.visibleRowCount]
      self.visibleRowCount += 1
      for w in row.itervalues():
        if isinstance(w, QtWidgets.QWidget):
          w.show()
    else:
      nameButton = self._createNameButton(rowCount)
      yomiButton = self._createYomiButton(rowCount)

      nameTtsButton = self._createNameTtsButton(rowCount)

      nameEdit = self._createNameEdit()
      yomiEdit = self._createYomiEdit()
      infoEdit = self._createInfoEdit()

      c = 0
      self.grid.addWidget(nameButton, rowCount, c)
      c += 1
      self.grid.addWidget(yomiButton, rowCount, c)
      c += 1
      self.grid.addWidget(nameTtsButton, rowCount, c)
      c += 1
      self.grid.addWidget(nameEdit, rowCount, c)
      c += 1
      self.grid.addWidget(yomiEdit, rowCount, c)
      c += 1
      self.grid.addWidget(infoEdit, rowCount, c)

      row = {
        'name': '',
        'yomi': '',
        'info': '',
        'nameTtsButton': nameTtsButton,
        'nameButton': nameButton,
        'yomiButton': yomiButton,
        'nameEdit': nameEdit,
        'yomiEdit': yomiEdit,
        'infoEdit': infoEdit,
      }

      self.rows.append(row)
      self.visibleRowCount += 1

    return row

  def _createNameTtsButton(self, index): # int ->
    ret = QtWidgets.QPushButton(u"♪") # おんぷ
    skqss.class_(ret, 'btn btn-default btn-toggle')
    ret.setToolTip(mytr_("TTS"))
    ret.setMaximumWidth(18)
    ret.setMaximumHeight(18)
    ret.clicked.connect(partial(self._speakName, index))
    return ret

  def _speakName(self, index):
    row = self.rows[index]
    name = row['name']
    import ttsman
    ttsman.speak(name)

  def _createNameEdit(self):
    return self._createLabel('text-info', tr_("Kanji"), NAME_EDIT_MIN_WIDTH)
  def _createYomiEdit(self):
    return self._createLabel('text-success', mytr_("Yomi"), NAME_EDIT_MIN_WIDTH)
  def _createInfoEdit(self):
    return self._createLabel('text-error', tr_("Comment"), INFO_EDIT_MIN_WIDTH)
  def _createLabel(self, styleclass, tip, minwidth):
    """
    @param  styleClass  str
    @param  minimumWidth  int
    @return  QLineEdit
    """
    ret = QtWidgets.QLineEdit()
    ret.setReadOnly(True)
    ret.setMinimumWidth(minwidth)
    ret.setToolTip(tip)
    skqss.class_(ret, styleclass)
    return ret

  def _createNameButton(self, index): # int -> QPushButton
    ret = QtWidgets.QPushButton(mytr_("Name"))
    skqss.class_(ret, "btn btn-primary")
    ret.setToolTip(my.tr("Add to Shared Dictionary"))
    ret.clicked.connect(partial(self._newName, index))
    return ret
  def _createYomiButton(self, index): # int -> QPushButton
    ret = QtWidgets.QPushButton(mytr_("Yomi"))
    skqss.class_(ret, "btn btn-success")
    ret.setToolTip(my.tr("Add to Shared Dictionary"))
    ret.clicked.connect(partial(self._newYomi, index))
    return ret

  def _newYomi(self, index):
    row = self.rows[index]
    name = row['name']
    yomi = row['yomi'] or name
    info = row['info']

    import main
    main.manager().showTermInput(pattern=name, text=yomi, comment=info,
        type='yomi', language='ja', tokenId=self.tokenId)

  def _newName(self, index):
    import dataman, main

    row = self.rows[index]
    name = row['name']
    #yomi = row['yomi']
    yomi = name
    info = row['info']

    lang = dataman.manager().user().language
    if lang == 'zhs':
      yomi = opencc.ja2zhs(yomi)
    else:
      lang = 'zht'
      yomi = opencc.ja2zht(yomi)

    main.manager().showTermInput(pattern=name, text=yomi, comment=info,
        type='name', language=lang, tokenId=self.tokenId)

if __name__ == '__main__':
  names = [
    (u"桜小路 ルナ", u"さくらこうじ ルナ"),
    (u"エスト・ギャラッハ・アーノッツ", ""),
  ]
  a = debug.app()
  w = NameInput()
  w.setNames(names)
  w.show()
  a.exec_()

# EOF
