# coding: utf8
# postedit.py
# 6/30/2014 jichi

__all__ = 'PostEditorManager', 'PostEditorManagerBean'

if __name__ == '__main__':
  import sys
  sys.path.append('..')
  import debug
  debug.initenv()

import json, os
from PySide.QtCore import Qt, Signal, Slot, Property, QObject
from Qt5 import QtWidgets
from sakurakit import skfileio, skqss, skwidgets
from sakurakit.skclass import Q_Q, memoizedproperty
from sakurakit.skdebug import dwarn
from sakurakit.sktr import tr_
from mytr import mytr_, my
import config, defs, growl, i18n, rc

TEXTEDIT_MINIMUM_HEIGHT = 50

@Q_Q
class _PostEditor(object):
  def __init__(self, q):
    self.imageEnabled = True

    self.postId = 0 # long
    self.userName = '' # unicode
    #self.userName = '' # unicode
    self.postLanguage = ''
    self.postContent = ''

    self.imageId = 0
    self.imageTitle = ''
    self.imagePath = ''

    self._createUi(q)
    self.contentEdit.setFocus()

    skwidgets.shortcut('ctrl+s', self._save, parent=q)

  def _createUi(self, q):
    layout = QtWidgets.QVBoxLayout()

    row = QtWidgets.QHBoxLayout()
    row.addStretch()
    row.addWidget(QtWidgets.QLabel(tr_("Language") + ":"))
    row.addWidget(self.languageEdit)
    layout.addLayout(row)

    layout.addWidget(self.contentEdit)

    row = QtWidgets.QHBoxLayout()
    row.addWidget(self.browseImageButton)
    row.addWidget(self.removeImageButton)
    row.addWidget(self.imageTitleEdit)
    row.addStretch()
    #row.addWidget(self.cancelButton)
    row.addWidget(self.saveButton)
    layout.addLayout(row)

    layout.setContentsMargins(5, 5, 5, 5)
    q.setLayout(layout)

  @memoizedproperty
  def saveButton(self):
    ret = QtWidgets.QPushButton(tr_("Save"))
    skqss.class_(ret, 'btn btn-primary')
    ret.setToolTip(tr_("Save") + " (Ctrl+S)")
    ret.setDefault(True)
    ret.clicked.connect(self._save)
    ret.clicked.connect(self.q.hide) # save and hide
    return ret

  @memoizedproperty
  def cancelButton(self):
    ret = QtWidgets.QPushButton(tr_("Cancel"))
    skqss.class_(ret, 'btn btn-default')
    ret.setToolTip(tr_("Cancel"))
    ret.clicked.connect(self.q.hide)
    return ret

  @memoizedproperty
  def browseImageButton(self):
    ret = QtWidgets.QPushButton(tr_("Image"))
    skqss.class_(ret, 'btn btn-info')
    ret.setToolTip(tr_("Upload"))
    ret.clicked.connect(self._browseImage)
    return ret

  @memoizedproperty
  def removeImageButton(self):
    ret = QtWidgets.QPushButton(tr_("Remove"))
    skqss.class_(ret, 'btn btn-danger')
    ret.setToolTip(tr_("Remove"))
    ret.clicked.connect(self._removeImage)
    return ret

  @memoizedproperty
  def imageTitleEdit(self):
    ret = QtWidgets.QLineEdit()
    skqss.class_(ret, 'editable')
    ret.setToolTip(tr_("Title"))
    ret.textChanged.connect(self._refreshSaveButton)
    return ret

  @memoizedproperty
  def contentEdit(self):
    ret = QtWidgets.QTextEdit()
    #skqss.class_(ret, 'texture')
    skqss.class_(ret, 'edit edit-default')
    ret.setToolTip(tr_("Content"))
    ret.setAcceptRichText(False)
    ret.setMinimumHeight(TEXTEDIT_MINIMUM_HEIGHT)
    ret.textChanged.connect(self._refreshSaveButton)
    return ret

  @memoizedproperty
  def spellHighlighter(self):
    import spell
    return spell.SpellHighlighter(self.contentEdit)

  @memoizedproperty
  def languageEdit(self):
    ret = QtWidgets.QComboBox()
    ret.setEditable(False)
    ret.addItems(map(i18n.language_name2, config.LANGUAGES))
    ret.setMaxVisibleItems(ret.count())
    ret.currentIndexChanged.connect(self._onLanguageChanged)
    return ret

  def _getLanguage(self):
    return config.language2htmllocale(config.LANGUAGES[self.languageEdit.currentIndex()])
  def _getContent(self):
    return self.contentEdit.toPlainText().strip()
  def _getImageTitle(self):
    return self.imageTitleEdit.text().strip()

  def _isChanged(self):
    t = self._getContent()
    return bool(t) and t != self.postContent or self.postLanguage != self._getLanguage()

  def _refreshSaveButton(self):
    self.saveButton.setEnabled(self._canSave())

  def _canSave(self): # -> bool
    changed = False

    t = self._getContent()
    if len(t) < defs.POST_CONTENT_MIN_LENGTH or len(t) > defs.POST_CONTENT_MAX_LENGTH:
      return False
    if not changed and t != self.postContent:
      changed = True

    if (self.imagePath or self.imageId):
      imageTitle = self._getImageTitle()
      if not imageTitle:
        return False
      if not changed and imageTitle != self.imageTitle:
        changed = True

    if not changed and self.postLanguage != self._getLanguage():
      changed = True
    if not changed and bool(self.imageTitle) != bool(self.imageId):
      changed = True
    if not changed and self.imagePath:
      changed = True
    return changed

  def _onLanguageChanged(self):
    self.spellHighlighter.setLanguage(self._getLanguage())
    self.saveButton.setEnabled(self._canSave())

  def _removeImage(self):
    self.imagePath = ''
    self.imageId = 0
    #self.imageTitle = ''
    self._refreshImage()

  def _browseImage(self):
    FILTERS = "%s (%s)" % (tr_("Image"), defs.UPLOAD_IMAGE_FILTER)
    path, filter = QtWidgets.QFileDialog.getOpenFileName(self.q,
        my.tr("Select the file to upload"),
        "", FILTERS)
    if path:
      sz = skfileio.filesize(path)
      if sz > defs.MAX_UPLOAD_IMAGE_SIZE:
        growl.warn(my.tr("File to upload is too large")
            + " &gt;= %s" % defs.MAX_UPLOAD_IMAGE_SIZE)
      elif sz:
        self.imagePath = path
        self._refreshImage()

  def _iterImageWidgets(self):
    yield self.browseImageButton
    yield self.removeImageButton
    yield self.imageTitleEdit

  def _refreshImage(self):
    for w in self._iterImageWidgets():
      w.setEnabled(self.imageEnabled)
    if self.imageEnabled:
      enabled = bool(self.imagePath or self.imageId)
      self.removeImageButton.setVisible(enabled)
      self.imageTitleEdit.setVisible(enabled)

      if not self.imageTitle and self.imagePath:
        name = os.path.basename(self.imagePath)
        title = os.path.splitext(name)[0]
        self.imageTitleEdit.setText(title)
      #else:
      #  self.imageTitleEdit.setText('')
      self._refreshSaveButton()

  def _save(self):
    v = self._getContent()
    post = {}
    if v and v != self.postContent:
      post['content'] = self.postContent = v

    v = self._getLanguage()
    if v != self.postLanguage:
      post['lang'] = self.postLanguage = v

    imageData = ''
    if self.imagePath:
      imageTitle = self._getImageTitle()
      if imageTitle:
        image = {
          'filename': self.imagePath,
          'title': imageTitle,
          'size': skfileio.filesize(self.imagePath),
        }
        imageData = json.dumps(image)
    elif self.imageTitle:
      if self.imageId:
        v = self._getImageTitle()
        if v and v != self.imageTitle:
          post['imageTitle'] = v
      else:
        post['image'] = 0

    if post or imageData:
      post['id'] = self.postId
      post['userName'] = self.userName

      postData = json.dumps(post)
      self.q.postChanged.emit(postData, imageData)

      growl.msg(my.tr("Edit submitted"))

  def refresh(self):
    self.contentEdit.setPlainText(self.postContent)
    self.imageTitleEdit.setText(self.imageTitle)

    enabled = bool(self.imageId)
    self.removeImageButton.setVisible(enabled)
    self.imageTitleEdit.setVisible(enabled)

    try: langIndex = config.LANGUAGES.index(config.htmllocale2language(self.postLanguage))
    except ValueError: langIndex = 1 # 'en'
    self.languageEdit.setCurrentIndex(langIndex)

    self.spellHighlighter.setLanguage(self.postLanguage) # must after lang

    for w in self._iterImageWidgets():
      w.setEnabled(self.imageEnabled)

    self.saveButton.setEnabled(False)

class PostEditor(QtWidgets.QDialog):

  postChanged = Signal(unicode, unicode) # json post, json image

  def __init__(self, parent=None):
    WINDOW_FLAGS = Qt.Dialog|Qt.WindowMinMaxButtonsHint
    super(PostEditor, self).__init__(parent, WINDOW_FLAGS)
    skqss.class_(self, 'texture')
    self.setWindowTitle(mytr_("Post Editor"))
    self.setWindowIcon(rc.icon('window-textedit'))
    self.__d = _PostEditor(self)
    #self.statusBar() # show status bar

  def setPost(self, id, userName='', language='', lang='', content='', image=None, **ignored):
    d = self.__d
    d.postId = id
    d.userName = userName
    d.postLanguage = language or lang
    d.postContent = content

    if image:
      d.imageId = image.get('id')
      d.imageTitle = image.get('title')
    else:
      d.imageId = 0
      d.imageTitle = ''
    d.imagePath = ''

    if self.isVisible():
      d.refresh()

  def setVisible(self, value):
    """@reimp @public"""
    if value and not self.isVisible():
      self.__d.refresh()
    super(PostEditor, self).setVisible(value)

  def imageEnabled(self): return self.__d.imageEnabled
  def setImageEnabled(self, t): self.__d.imageEnabled = t

class _PostEditorManager:
  def __init__(self):
    self.dialogs = []
    self.imageEnabled = True

  @staticmethod
  def _createDialog():
    import windows
    parent = windows.top()
    ret = PostEditor(parent)
    ret.resize(400, 200)
    return ret

  def getDialog(self, q): # QObject -> QWidget
    for w in self.dialogs:
      if not w.isVisible():
        w.setImageEnabled(self.imageEnabled)
        return w
    ret = self._createDialog()
    ret.setImageEnabled(self.imageEnabled)
    self.dialogs.append(ret)
    ret.postChanged.connect(q.postChanged)
    return ret

#@Q_Q
class PostEditorManager(QObject):
  def __init__(self, parent=None):
    super(PostEditorManager, self).__init__(parent)
    self.__d = _PostEditorManager()

    from PySide.QtCore import QCoreApplication
    qApp = QCoreApplication.instance()
    qApp.aboutToQuit.connect(self.hide)

    import dataman
    dataman.manager().loginChanged.connect(lambda name: name or name == 'guest' or self.hide())

    #import netman
    #netman.manager().onlineChanged.connect(lambda t: t or self.hide())

  postChanged = Signal(unicode, unicode) # json post, json image

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

  def editPost(self, **post):
    w = self.__d.getDialog(self)
    w.setPost(**post)
    w.show()

  def isImageEnabled(self): return self.__d.imageEnabled
  def setImageEnabled(self, t): self.__d.imageEnabled = t

#@memoized
#def manager(): return PostEditorManager()

#@QmlObject
class PostEditorManagerBean(QObject):
  def __init__(self, parent=None, manager=None):
    super(PostEditorManagerBean, self).__init__(parent)
    self.manager = manager or PostEditorManager(self)
    self.manager.postChanged.connect(self.postChanged)

  postChanged = Signal(unicode, unicode) # json post, json image

  imageEnabledChanged = Signal(bool)
  imageEnabled = Property(bool,
      lambda self: self.manager.isImageEnabled(),
      lambda self, t: self.manager.setImageEnabled(t),
      notify=imageEnabledChanged)

  @Slot(unicode)
  def editPost(self, data): # json ->
    try:
      post = json.loads(data)
      post['id'] = long(post['id'])
      self.manager.editPost(**post)
    except Exception, e: dwarn(e)

if __name__ == '__main__':
  a = debug.app()
  m = PostEditorManager()
  m.editPost(id=123, content="123", lang='en')
  a.exec_()

# EOF
