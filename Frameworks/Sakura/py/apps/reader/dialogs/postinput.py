# coding: utf8
# postinput.py
# 8/30/2014 jichi

__all__ = 'PostInputManager', 'PostInputManagerBean'

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
class _PostInput(object):
  def __init__(self, q):
    self.imageEnabled = True
    self.clear()

    self._createUi(q)
    self.contentEdit.setFocus()

    skwidgets.shortcut('ctrl+s', self._save, parent=q)

  def clear(self):
    self.topicId = 0 # long
    self.replyId = 0 # long
    self.postContent = '' # str
    self.postType = 'post' # str
    self.imagePath = '' # unicode

    import dataman
    self.postLanguage = dataman.manager().user().language

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
    ret = QtWidgets.QPushButton(tr_("Submit"))
    skqss.class_(ret, 'btn btn-primary')
    ret.setToolTip(tr_("Submit") + " (Ctrl+S)")
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

  def _refreshSaveButton(self):
    self.saveButton.setEnabled(self._canSave())

  def _canSave(self): # -> bool
    t = self._getContent()
    if len(t) < defs.POST_CONTENT_MIN_LENGTH or len(t) > defs.POST_CONTENT_MAX_LENGTH:
      return False
    if self.imagePath and not self._getImageTitle():
      return False
    return True

  def _onLanguageChanged(self):
    self.spellHighlighter.setLanguage(self._getLanguage())

  def _removeImage(self):
    self.imagePath = ''
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
      self.removeImageButton.setVisible(bool(self.imagePath))
      if self.imagePath:
        name = os.path.basename(self.imagePath)
        title = os.path.splitext(name)[0]
      else:
        title = ''
      self.imageTitleEdit.setText(title)
      self.imageTitleEdit.setVisible(bool(title))

  def _save(self):
    post = {}
    post['content'] = self.postContent = self._getContent()
    post['lang'] = self.postLanguage = self._getLanguage()

    #import dataman
    #user = dataman.manager().user()
    #post['login'] = user.name
    #post['pasword'] = user.password

    if post['content']:
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

      if self.topicId:
        post['topic'] = self.topicId
      if self.replyId:
        post['reply'] = self.replyId
      post['type'] = self.postType
      postData = json.dumps(post)
      self.q.postReceived.emit(postData, imageData)
      #self.postContent = '' # clear content but leave language

      growl.msg(my.tr("Edit submitted"))

  def refresh(self):
    self.saveButton.setEnabled(False)

    self.contentEdit.setPlainText(self.postContent)

    try: langIndex = config.LANGUAGES.index(config.htmllocale2language(self.postLanguage))
    except ValueError: langIndex = 1 # 'en'
    self.languageEdit.setCurrentIndex(langIndex)

    self.spellHighlighter.setLanguage(self.postLanguage) # must after lang

    self._refreshImage()

class PostInput(QtWidgets.QDialog):

  postReceived = Signal(unicode, unicode) # json post, json image

  def __init__(self, parent=None):
    WINDOW_FLAGS = Qt.Dialog|Qt.WindowMinMaxButtonsHint
    super(PostInput, self).__init__(parent, WINDOW_FLAGS)
    skqss.class_(self, 'texture')
    self.setWindowTitle(mytr_("New Post"))
    self.setWindowIcon(rc.icon('window-textedit'))
    self.__d = _PostInput(self)
    #self.statusBar() # show status bar

  def imageEnabled(self): return self.__d.imageEnabled
  def setImageEnabled(self, t): self.__d.imageEnabled = t

  def topicId(self): return self.__d.topicId
  def setTopicId(self, v): self.__d.topicId = v

  def replyId(self): return self.__d.replyId
  def setReplyId(self, v): self.__d.replyId = v

  def type(self): return self.__d.postType
  def setType(self, v): self.__d.postType = v

  def imagePath(self): return self.__d.imagePath
  def setImagePath(self, v): self.__d.imagePath = v

  #def clear(self): self.__d.clear()

  def setVisible(self, value):
    """@reimp @public"""
    if value and not self.isVisible():
      self.__d.refresh()
    super(PostInput, self).setVisible(value)

class _PostInputManager:
  def __init__(self):
    self.dialogs = []
    self.imageEnabled = True

  @staticmethod
  def _createDialog():
    import windows
    parent = windows.top()
    ret = PostInput(parent)
    ret.resize(400, 200)
    return ret

  def getDialog(self, q): # QObject -> QWidget
    for w in self.dialogs:
      if not w.isVisible():
        #w.clear() # use last input
        w.setImageEnabled(self.imageEnabled)
        return w
    ret = self._createDialog()
    ret.setImageEnabled(self.imageEnabled)
    self.dialogs.append(ret)
    ret.postReceived.connect(q.postReceived)
    return ret

#@Q_Q
class PostInputManager(QObject):
  def __init__(self, parent=None):
    super(PostInputManager, self).__init__(parent)
    self.__d = _PostInputManager()

    from PySide.QtCore import QCoreApplication
    qApp = QCoreApplication.instance()
    qApp.aboutToQuit.connect(self.hide)

    import dataman
    dataman.manager().loginChanged.connect(lambda name: name or name == 'guest' or self.hide())

    #import netman
    #netman.manager().onlineChanged.connect(lambda t: t or self.hide())

  postReceived = Signal(unicode, unicode) # json post, json image

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

  def newPost(self, topicId=0, replyId=0, type='post', imagePath=''): # long, unicode ->
    w = self.__d.getDialog(self)
    w.setType(type)
    w.setTopicId(topicId)
    w.setReplyId(replyId)
    w.setImagePath(imagePath)
    w.show()

  def isImageEnabled(self): return self.__d.imageEnabled
  def setImageEnabled(self, t): self.__d.imageEnabled = t

#@memoized
#def manager(): return PostInputManager()

#@QmlObject
class PostInputManagerBean(QObject):
  def __init__(self, parent=None, manager=None):
    super(PostInputManagerBean, self).__init__(parent)
    self.manager = manager or PostInputManager(self)
    self.manager.postReceived.connect(self.postReceived)

  postReceived = Signal(unicode, unicode) # json post, json image

  @Slot(long, str)
  def newPost(self, topicId, postType):
    self.manager.newPost(topicId=topicId, type=postType)

  @Slot(long, long)
  def replyPost(self, topicId, postId):
    self.manager.newPost(topicId=topicId, replyId=postId, type='reply')

  imageEnabledChanged = Signal(bool)
  imageEnabled = Property(bool,
      lambda self: self.manager.isImageEnabled(),
      lambda self, t: self.manager.setImageEnabled(t),
      notify=imageEnabledChanged)

if __name__ == '__main__':
  a = debug.app()
  m = PostInputManager()
  m.newPost()
  a.exec_()

# EOF
