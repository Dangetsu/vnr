# coding: utf8
# subeditor.py
# 1/23/2013 jichi

__all__ = 'SubtitleEditorManager', 'SubtitleEditorManagerProxy'

from PySide.QtCore import Qt, Slot, QObject
from Qt5 import QtWidgets
from sakurakit import skqss
from sakurakit.skclass import Q_Q, memoized, memoizedproperty
from sakurakit.skdebug import dprint, dwarn, derror
#from sakurakit.skqml import QmlObject
from sakurakit.sktr import tr_
from mytr import mytr_, my
import config, defs, dataman, i18n, netman, rc

TEXTEDIT_MINIMUM_HEIGHT = 50

def create_label(text=""): # unicode -> QLabel
  ret = QtWidgets.QLabel()
  if text:
    ret.setText(text + ":")
  #ret.setAlignment(Qt.AlignRight|Qt.AlignVCenter) # disable alignment
  return ret

@Q_Q
class _SubtitleEditor(object):
  def __init__(self, q):
    self.comment = None # dataman.Comment or None
    self._createUi(q)

  def _createUi(self, q):
    layout = QtWidgets.QVBoxLayout()

    # User

    row = QtWidgets.QHBoxLayout()
    row.addWidget(create_label(tr_("Type")))
    row.addWidget(self.typeEdit)

    row.addWidget(create_label(tr_("Language")))
    row.addWidget(self.languageEdit)

    row.addStretch()

    #row.addWidget(create_label(tr_("User")))
    row.addWidget(self.userNameLabel)
    layout.addLayout(row)

    # Status
    row = QtWidgets.QHBoxLayout()
    row.addWidget(create_label(tr_("Status")))
    row.addWidget(self.enabledButton)
    row.addWidget(self.lockedButton)
    row.addStretch()

    #row.addWidget(create_label(tr_("Date")))
    row.addWidget(self.timestampLabel)
    layout.addLayout(row)

    # Context size
    row = QtWidgets.QHBoxLayout()
    row.addWidget(create_label(mytr_("Context count")))
    row.addWidget(self.contextSizeLabel)
    row.addStretch()
    layout.addLayout(row)

    layout.addWidget(self.textEdit)

    # Context
    layout.addWidget(QtWidgets.QLabel(
      tr_("Context") + " (%s):" % tr_("read-only")
    ))
    layout.addWidget(self.currentContextEdit)

    layout.addWidget(QtWidgets.QLabel(
      mytr_("Previous context") + " (%s):" % tr_("read-only")
    ))
    layout.addWidget(self.previousContextEdit)

    layout.addWidget(create_label(tr_("Comment") ))
    layout.addWidget(self.commentEdit)

    row = QtWidgets.QHBoxLayout()
    row.addWidget(create_label(tr_("Permission")))
    row.addWidget(self.textPermissionLabel)

    row.addWidget(create_label(tr_("Internet status")))
    row.addWidget(self.onlineLabel)

    row.addStretch()
    row.addWidget(self.deleteButton)
    row.addWidget(self.refreshButton)
    layout.addLayout(row)
    q.setLayout(layout)

  @memoizedproperty
  def refreshButton(self):
    ret = QtWidgets.QPushButton(tr_("Refresh"))
    skqss.class_(ret, 'btn btn-success')
    ret.setToolTip(my.tr("Reload information"))
    ret.setDefault(True)
    #ret.setStatusTip(ret.toolTip())
    ret.clicked.connect(self.refresh)
    return ret

  @memoizedproperty
  def deleteButton(self):
    ret = QtWidgets.QPushButton(tr_("Delete"))
    skqss.class_(ret, 'btn btn-danger')
    ret.setToolTip(my.tr("Permanently delete it"))
    ret.clicked.connect(self._confirmDelele)
    return ret

  def _confirmDelele(self):
    import prompt
    if self.comment and prompt.confirmDeleteComment(self.comment):
      self._delele()

  def _delele(self):
    if self.comment and self._canEdit():
      self.comment.deleted = True
      self.q.hide()

  @memoizedproperty
  def textPermissionLabel(self):
    ret = QtWidgets.QLabel()
    ret.setToolTip(tr_("Permission"))
    return ret

  @memoizedproperty
  def onlineLabel(self):
    ret = QtWidgets.QLabel()
    ret.setToolTip(tr_("Internet status"))
    return ret

  @memoizedproperty
  def userNameLabel(self):
    ret = QtWidgets.QLabel()
    ret.setToolTip(tr_("User"))
    skqss.class_(ret, 'readonly')
    return ret

  @memoizedproperty
  def timestampLabel(self):
    ret = QtWidgets.QLabel()
    ret.setToolTip(tr_("Create date"))
    skqss.class_(ret, 'readonly')
    return ret

  @memoizedproperty
  def contextSizeLabel(self):
    ret = QtWidgets.QLabel()
    ret.setToolTip(mytr_("Context count"))
    skqss.class_(ret, 'readonly')
    return ret

  @memoizedproperty
  def typeEdit(self):
    ret = QtWidgets.QComboBox()
    ret.setToolTip(tr_("Type"))
    ret.addItems(dataman.Comment.TR_TYPES)
    ret.setEditable(False)
    ret.currentIndexChanged.connect(self._saveType)
    #skqss.class_(ret, 'normal')
    return ret

  @memoizedproperty
  def enabledButton(self):
    ret = QtWidgets.QCheckBox(tr_("Enabled"))
    ret.setToolTip(my.tr("Whether it is visible to users"))
    ret.toggled.connect(lambda t:
        self.comment and self.comment.setDisabled(not t))
    return ret

  @memoizedproperty
  def lockedButton(self):
    ret = QtWidgets.QCheckBox(tr_("Locked"))
    ret.setToolTip(my.tr("Whether allow others to override it"))
    ret.toggled.connect(lambda t:
        self.comment and self.comment.setLocked(t))
    return ret

  @memoizedproperty
  def textEdit(self):
    #ret = QtWidgets.QPlainTextEdit()
    ret = QtWidgets.QTextEdit() # needed by spell checker
    ret.setAcceptRichText(False)
    ret.setToolTip(tr_("Text"))
    ret.setMinimumHeight(TEXTEDIT_MINIMUM_HEIGHT)
    ret.textChanged.connect(self._saveText)
    return ret

  @memoizedproperty
  def commentEdit(self):
    ret = QtWidgets.QLineEdit()
    ret.setToolTip(tr_("Comment"))
    ret.setPlaceholderText(tr_("Empty"))
    #ret.setMinimumHeight(TEXTEDIT_MINIMUM_HEIGHT)
    ret.textChanged.connect(self._saveComment)
    return ret

  @memoizedproperty
  def spellHighlighter(self):
    import spell
    return spell.SpellHighlighter(self.textEdit)

  def _saveText(self):
    if self.comment and self._canEdit():
      t = self.textEdit.toPlainText().strip()
      if t and t != self.comment.text:
        self.comment.text = t

  def _saveComment(self):
    if self.comment and self._canEdit():
      t = self.commentEdit.text().strip()
      if t and t != self.comment.comment:
        self.comment.comment = t

  def _saveType(self):
    if self.comment and self._canEdit():
      t = dataman.Comment.TYPES[self.typeEdit.currentIndex()]
      if t and t != self.comment.type:
        self.comment.type = t

  @memoizedproperty
  def languageEdit(self):
    ret = QtWidgets.QComboBox()
    ret.setEditable(False)
    ret.addItems(map(i18n.language_name2, config.LANGUAGES))
    ret.setMaxVisibleItems(ret.count())
    ret.currentIndexChanged.connect(self._saveLanguage)
    return ret

  def _saveLanguage(self):
    if self.comment and self._canEdit():
      lang = config.LANGUAGES[self.languageEdit.currentIndex()]
      if lang != self.comment.language:
        self.comment.language = lang
        self.spellHighlighter.setLanguage(lang)

  @memoizedproperty
  def currentContextEdit(self):
    ret = QtWidgets.QPlainTextEdit()
    skqss.class_(ret, 'readonly texture')
    ret.setReadOnly(True)
    ret.setToolTip(mytr_("Game text"))
    ret.setMinimumHeight(TEXTEDIT_MINIMUM_HEIGHT)
    return ret

  @memoizedproperty
  def previousContextEdit(self):
    ret = QtWidgets.QPlainTextEdit()
    skqss.class_(ret, 'readonly texture')
    ret.setReadOnly(True)
    ret.setToolTip(mytr_("Game text"))
    ret.setMinimumHeight(TEXTEDIT_MINIMUM_HEIGHT)
    return ret

  def _canEdit(self):
    userAccess = []
    user = dataman.manager().user()
    if user.access:#Сделал тут такую хуйню, потому что не знаю можно ли делать нормально(лол)
        userAccessMass = user.access.split(',')
        for a in userAccessMass:
            userAccess.append(a)
	# Пришлось вырезать дополнительную проверку, ибо хз как обратиться к dataman за itemId
	# and (self.comment.userId == user.id or (str(self.comment.userId) + ":" + str(self.comment.itemId)) in userAccess) 
    return netman.manager().isOnline() and bool(self.comment) and not self.comment.d.protected

  def refresh(self):
    comment = self.comment
    online = netman.manager().isOnline()
    editable = self._canEdit()

    self.userNameLabel.setText('@' + comment.userName if comment else tr_("Empty"))
    self.contextSizeLabel.setText("%s" % comment.contextSize if comment else tr_("Empty"))
    self.timestampLabel.setText(i18n.timestamp2datetime(comment.timestamp) if comment else tr_("Empty"))

    self.typeEdit.setCurrentIndex(dataman.Comment.TYPES.index(comment.type) if comment else 0)
    self.typeEdit.setEnabled(editable)

    self.enabledButton.setEnabled(bool(comment))
    self.enabledButton.setChecked(bool(comment and not comment.disabled))

    self.lockedButton.setEnabled(bool(comment))
    self.lockedButton.setChecked(bool(comment and comment.locked))

    self.textEdit.setPlainText(comment.text if comment else tr_("empty"))
    self.textEdit.setReadOnly(not editable)
    skqss.class_(self.textEdit, 'normal' if editable else 'readonly')

    self.commentEdit.setText(comment.comment)
    self.commentEdit.setReadOnly(not editable)
    skqss.class_(self.commentEdit, 'normal' if editable else 'readonly')

    self.textPermissionLabel.setText(tr_("Editable") if editable else tr_("Read-only"))
    skqss.class_(self.textPermissionLabel, 'normal' if editable else 'readonly')

    self.deleteButton.setEnabled(editable)

    self.onlineLabel.setText(tr_("Online") if online else tr_("Offline"))
    skqss.class_(self.onlineLabel, 'readonly' if online else 'error')

    try: langIndex = config.LANGUAGES.index(comment.language)
    except ValueError: langIndex = 1 # 'en'
    self.languageEdit.setCurrentIndex(langIndex)
    self.languageEdit.setEnabled(editable)

    self.spellHighlighter.setLanguage(comment.language) # must after lang

    if not comment or not comment.context:
      self.previousContextEdit.setPlainText(tr_("Empty"))
      self.currentContextEdit.setPlainText(tr_("Empty"))
    else:
      ctx = comment.context
      l = ctx.split(defs.CONTEXT_SEP)
      self.currentContextEdit.setPlainText(l[-1] or tr_("Empty"))
      self.previousContextEdit.setPlainText('\n'.join(l[:-1]) or tr_("Empty"))

  def refreshIfVisible(self):
    if self.q.isVisible():
      self.refresh()

class SubtitleEditor(QtWidgets.QDialog):
  def __init__(self, parent=None):
    WINDOW_FLAGS = Qt.Dialog|Qt.WindowMinMaxButtonsHint
    super(SubtitleEditor, self).__init__(parent, WINDOW_FLAGS)
    skqss.class_(self, 'texture')
    self.setWindowTitle(mytr_("Subtitle Editor"))
    self.setWindowIcon(rc.icon('window-textedit'))
    self.__d = _SubtitleEditor(self)
    #self.statusBar() # show status bar

  def setComment(self, c):
    self.__d.comment = c
    if self.isVisible():
      self.__d.refresh()

  def setVisible(self, value):
    """@reimp @public"""
    if value and not self.isVisible():
      self.__d.refresh()
    super(SubtitleEditor, self).setVisible(value)

class _SubtitleEditorManager:
  def __init__(self):
    self.dialogs = []

  @staticmethod
  def _createDialog():
    import windows
    parent = windows.top()
    ret = SubtitleEditor(parent)
    ret.resize(400, 200)
    return ret

  def getDialog(self):
    for w in self.dialogs:
      if not w.isVisible():
        return w
    ret = self._createDialog()
    self.dialogs.append(ret)
    return ret

class SubtitleEditorManager:
  def __init__(self):
    self.__d = _SubtitleEditorManager()

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

  def showComment(self, c):
    w = self.__d.getDialog()
    w.setComment(c)
    w.show()

@memoized
def manager(): return SubtitleEditorManager()

#@QmlObject
#class SubtitleEditorManagerProxy(QObject):
#  def __init__(self, parent=None):
#    super(SubtitleEditorManagerProxy, self).__init__(parent)
#
#  @Slot(QObject) # dataman.Comment
#  def showComment(self, c):
#    manager().showComment(c)

# EOF
