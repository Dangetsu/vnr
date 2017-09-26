# coding: utf8
# topicedit.py
# 11/27/2014 jichi

__all__ = 'TopicEditorManager', 'TopicEditorManagerBean'

if __name__ == '__main__':
  import sys
  sys.path.append('..')
  import debug
  debug.initenv()

import json, os
from collections import OrderedDict
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
class _TopicEditor(object):
  def __init__(self, q):
    self.imageEnabled = True

    self.topicId = 0 # long
    self.subjectId = 0 # long
    self.subjectType = 'subject' # str
    self.topicType = 'review' # str
    self.userName = '' # unicode
    self.topicLanguage = ''
    self.topicTitle = ''
    self.topicContent = ''
    self.scores = {} # {str key:int value}

    self.imageId = 0
    self.imageTitle = ''
    self.imagePath = ''

    self._createUi(q)
    self.contentEdit.setFocus()

    skwidgets.shortcut('ctrl+s', self._save, parent=q)

  def _createUi(self, q):
    layout = QtWidgets.QVBoxLayout()

    layout.addWidget(self.scoreRow)

    row = QtWidgets.QHBoxLayout()
    row.addWidget(self.typeEdit)
    row.addWidget(self.titleEdit)
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
  def scoreRow(self):
    row = QtWidgets.QHBoxLayout()
    for w in self.scoreEdits.itervalues():
      row.addWidget(w)
    row.addStretch()
    row.setContentsMargins(0, 0, 0, 0)
    return skwidgets.SkLayoutWidget(row)

  @memoizedproperty
  def scoreEdits(self):
    return OrderedDict((
      ('overall', self._createScoreEdit(tr_("Score"))),
      ('ecchi', self._createScoreEdit(mytr_("Ecchi"))),
     ))

  def _createScoreEdit(self, name):
    ret = QtWidgets.QSpinBox()
    ret.setToolTip("%s [0,10]" % name)
    ret.setRange(0, 10)
    ret.setSingleStep(1)
    ret.setPrefix(name + " ")
    ret.valueChanged.connect(self._refreshSaveButton)
    return ret

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
  def titleEdit(self):
    ret = QtWidgets.QLineEdit()
    skqss.class_(ret, 'editable')
    ret.setPlaceholderText(tr_("Title"))
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

  @memoizedproperty
  def typeEdit(self):
    ret = QtWidgets.QComboBox()
    ret.setEditable(False)
    ret.addItems(map(i18n.topic_type_name, defs.TOPIC_TYPES))
    ret.setMaxVisibleItems(ret.count())
    ret.currentIndexChanged.connect(self._refreshSaveButton)
    return ret

  def _getType(self): # -> str
    return defs.TOPIC_TYPES[self.typeEdit.currentIndex()]
  def _getLanguage(self): # -> str
    return config.language2htmllocale(config.LANGUAGES[self.languageEdit.currentIndex()])
  def _getContent(self): # -> unicode
    return self.contentEdit.toPlainText().strip()
  def _getTitle(self): # -> unicode
    return self.titleEdit.text().strip()
  def _getImageTitle(self): # -> unicode
    return self.imageTitleEdit.text().strip()
  def _getScores(self): # -> {str k:int v}
    ret = {}
    for k,v in self.scoreEdits.iteritems():
      score = v.value()
      if score:
        ret[k] = score
    return ret

  def _isChanged(self):
    t = self._getContent()
    if bool(t) and t != self.topicContent:
      return True
    t = self._getTitle()
    if bool(t) and t != self.topicTitle:
      return True
    if self.topicLanguage != self._getLanguage():
      return True
    if self.topicType == 'review' and self.scores != self._getScores():
      return True
    if self.topicType != 'review' and self.topicType != self._getType():
      return True
    return False

  def _refreshSaveButton(self):
    self.saveButton.setEnabled(self._canSave())

  def _canSave(self): # -> bool
    changed = False

    t = self._getTitle()
    if len(t) < defs.TOPIC_TITLE_MIN_LENGTH or len(t) > defs.TOPIC_TITLE_MAX_LENGTH:
      return False
    if not changed and t != self.topicTitle:
      changed = True

    t = self._getContent()
    if len(t) < defs.TOPIC_CONTENT_MIN_LENGTH or len(t) > defs.TOPIC_CONTENT_MAX_LENGTH:
      return False
    if not changed and t != self.topicContent:
      changed = True

    if (self.imagePath or self.imageId):
      imageTitle = self._getImageTitle()
      if not imageTitle:
        return False
      if not changed and imageTitle != self.imageTitle:
        changed = True

    if not changed and self.topicLanguage != self._getLanguage():
      changed = True
    if not changed and bool(self.imageTitle) != bool(self.imageId):
      changed = True
    if not changed and self.imagePath:
      changed = True
    if not changed and self.topicType == 'review' and self.scores != self._getScores():
      changed = True
    if not changed and self.topicType != 'review' and self.topicType != self._getType():
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
    topic = {}

    v = self._getTitle()
    if v and v != self.topicTitle:
      topic['title'] = self.topicTitle = v

    v = self._getContent()
    if v and v != self.topicContent:
      topic['content'] = self.topicContent = v

    v = self._getLanguage()
    if v != self.topicLanguage:
      topic['lang'] = self.topicLanguage = v

    if self.topicType != 'review':
      v = self._getType()
      if v != self.topicType:
        topic['type'] = self.topicType = v

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
          topic['imageTitle'] = v
      else:
        topic['image'] = 0

    ticketData = ''
    if self.topicType == 'review':
      scores = self._getScores()
      if scores and scores != self.scores:
        ticketData = json.dumps(scores)

        topic['updateScore'] = True
        try:
          for k in scores.iterkeys():
            if not self.scores or not self.scores.get(k):
              topic['newScore'] = True
              break
        except Exception, e:
          dwarn(e)

    if topic or imageData or ticketData:
      topic['id'] = self.topicId
      topic['userName'] = self.userName
      topic['subjectId'] = self.subjectId
      topic['subjectType'] = self.subjectType

      topicData = json.dumps(topic)

      self.q.topicChanged.emit(topicData, imageData, ticketData)

      growl.msg(my.tr("Edit submitted"))

  def refresh(self):
    self.titleEdit.setText(self.topicTitle)
    self.contentEdit.setPlainText(self.topicContent)
    self.imageTitleEdit.setText(self.imageTitle)

    enabled = bool(self.imageId)
    self.removeImageButton.setVisible(enabled)
    self.imageTitleEdit.setVisible(enabled)

    try: langIndex = config.LANGUAGES.index(config.htmllocale2language(self.topicLanguage))
    except ValueError: langIndex = 1 # 'en'
    self.languageEdit.setCurrentIndex(langIndex)

    if self.topicType != 'review':
      try: typeIndex = defs.TOPIC_TYPES.index(self.topicType)
      except ValueError: typeIndex = 0 # 'chat'
      self.typeEdit.setCurrentIndex(typeIndex)

    self.spellHighlighter.setLanguage(self.topicLanguage) # must after lang

    for w in self._iterImageWidgets():
      w.setEnabled(self.imageEnabled)

    scoreEdits = self.scoreEdits
    for v in scoreEdits.itervalues():
      v.setValue(0)

    scoreEnabled = self.topicType == 'review'
    self.scoreRow.setVisible(scoreEnabled)
    self.typeEdit.setVisible(not scoreEnabled)
    if scoreEnabled and self.scores:
      try:
        for k,v in self.scores.iteritems():
          w = scoreEdits.get(k)
          if w:
            w.setValue(v)
      except Exception, e:
        dwarn(e)

    self.saveButton.setEnabled(False)

class TopicEditor(QtWidgets.QDialog):

  topicChanged = Signal(unicode, unicode, unicode) # json topic, json image, json tickets

  def __init__(self, parent=None):
    WINDOW_FLAGS = Qt.Dialog|Qt.WindowMinMaxButtonsHint
    super(TopicEditor, self).__init__(parent, WINDOW_FLAGS)
    skqss.class_(self, 'texture')
    self.setWindowTitle(mytr_("Topic Editor"))
    self.setWindowIcon(rc.icon('window-textedit'))
    self.__d = _TopicEditor(self)
    #self.statusBar() # show status bar

  def setTopic(self, id, subjectId=0, subjectType='subject', scores=None, type='', userName='', language='', lang='', title='', content='', image=None, **ignored):
    d = self.__d
    d.topicId = id
    d.topicType = type
    d.subjectId = subjectId
    d.subjectType = subjectType
    d.userName = userName
    d.topicLanguage = language or lang
    d.topicTitle = title
    d.topicContent = content
    d.scores = scores or {}

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
    super(TopicEditor, self).setVisible(value)

  def imageEnabled(self): return self.__d.imageEnabled
  def setImageEnabled(self, t): self.__d.imageEnabled = t

class _TopicEditorManager:
  def __init__(self):
    self.dialogs = []
    self.imageEnabled = True

  @staticmethod
  def _createDialog():
    import windows
    parent = windows.top()
    ret = TopicEditor(parent)
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
    ret.topicChanged.connect(q.topicChanged)
    return ret

#@Q_Q
class TopicEditorManager(QObject):
  def __init__(self, parent=None):
    super(TopicEditorManager, self).__init__(parent)
    self.__d = _TopicEditorManager()

    from PySide.QtCore import QCoreApplication
    qApp = QCoreApplication.instance()
    qApp.aboutToQuit.connect(self.hide)

    import dataman
    dataman.manager().loginChanged.connect(lambda name: name or name == 'guest' or self.hide())

    #import netman
    #netman.manager().onlineChanged.connect(lambda t: t or self.hide())

  topicChanged = Signal(unicode, unicode, unicode) # json topic, json image, json tickets

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

  def editTopic(self, **topic):
    w = self.__d.getDialog(self)
    w.setTopic(**topic)
    w.show()

  def isImageEnabled(self): return self.__d.imageEnabled
  def setImageEnabled(self, t): self.__d.imageEnabled = t

#@memoized
#def manager(): return TopicEditorManager()

#@QmlObject
class TopicEditorManagerBean(QObject):
  def __init__(self, parent=None, manager=None):
    super(TopicEditorManagerBean, self).__init__(parent)
    self.manager = manager or TopicEditorManager(self)
    self.manager.topicChanged.connect(self.topicChanged)

  topicChanged = Signal(unicode, unicode, unicode) # json topic, json image, json tickets

  imageEnabledChanged = Signal(bool)
  imageEnabled = Property(bool,
      lambda self: self.manager.isImageEnabled(),
      lambda self, t: self.manager.setImageEnabled(t),
      notify=imageEnabledChanged)

  @Slot(unicode)
  def editTopic(self, data): # json ->
    try:
      topic = json.loads(data)
      topic['id'] = long(topic['id'])
      self.manager.editTopic(**topic)
    except Exception, e: dwarn(e)

if __name__ == '__main__':
  a = debug.app()
  m = TopicEditorManager()
  m.editTopic(id=123, title="hello", content="123", lang='en')
  a.exec_()

# EOF
