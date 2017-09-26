# coding: utf8
# topicinput.py
# 11/27/2014 jichi

__all__ = 'TopicInputManager', 'TopicInputManagerBean'

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
#from sakurakit.skdebug import dwarn
from sakurakit.sktr import tr_
from mytr import mytr_, my
import config, defs, growl, i18n, rc

TEXTEDIT_MINIMUM_HEIGHT = 50

@Q_Q
class _TopicInput(object):
  def __init__(self, q):
    self.imageEnabled = True
    self.clear()

    self._createUi(q)
    self.contentEdit.setFocus()

    skwidgets.shortcut('ctrl+s', self._save, parent=q)

  def clear(self):
    self.subjectId = 0
    self.subjectType = 'subject'
    self.topicType = 'review' # str
    self.topicContent = '' # str
    self.imagePath = '' # unicode

    import dataman
    self.topicLanguage = dataman.manager().user().language

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
    return ret

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
    #ret.currentIndexChanged.connect(self._onTypeChanged)
    return ret

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
    ret.setPlaceholderText(tr_("Title"))
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

  def _refreshSaveButton(self):
    self.saveButton.setEnabled(self._canSave())

  def _canSave(self): # -> bool
    t = self._getTitle()
    if len(t) < defs.TOPIC_TITLE_MIN_LENGTH or len(t) > defs.TOPIC_TITLE_MAX_LENGTH:
      return False
    t = self._getContent()
    if len(t) < defs.TOPIC_CONTENT_MIN_LENGTH or len(t) > defs.TOPIC_CONTENT_MAX_LENGTH:
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
    if not self.subjectId or not self.subjectType:
      return
    topic = {}
    topic['title'] = self.topicContent = self._getTitle()
    topic['content'] = self.topicContent = self._getContent()
    topic['lang'] = self.topicLanguage = self._getLanguage()

    if self.topicType == 'review':
      topic['type'] = self.topicType
    else:
      topic['type'] = self._getType()

    #import dataman
    #user = dataman.manager().user()
    #topic['login'] = user.name
    #topic['pasword'] = user.password

    if topic['content'] and topic['title']:
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

      topic['subjectId'] = self.subjectId
      topic['subjectType'] = self.subjectType

      topicData = json.dumps(topic)

      ticketData = ''
      if self.topicType == 'review':
        tickets = {}
        for k,v in self.scoreEdits.iteritems():
          score = v.value()
          if score:
            tickets[k] = score
        if tickets:
          ticketData = json.dumps(tickets)
      self.q.topicReceived.emit(topicData, imageData, ticketData)
      #self.topicContent = '' # clear content but leave language

      growl.msg(my.tr("Edit submitted"))

  def refresh(self):
    scoreEnabled = self.topicType == 'review'
    self.scoreRow.setVisible(scoreEnabled)
    self.typeEdit.setVisible(not scoreEnabled)

    self.saveButton.setEnabled(False)

    self.contentEdit.setPlainText(self.topicContent)

    try: typeIndex = defs.TOPIC_TYPES.index(self.topicType)
    except ValueError: typeIndex = 0
    self.typeEdit.setCurrentIndex(typeIndex)

    try: langIndex = config.LANGUAGES.index(config.htmllocale2language(self.topicLanguage))
    except ValueError: langIndex = 1 # 'en'
    self.languageEdit.setCurrentIndex(langIndex)

    self.spellHighlighter.setLanguage(self.topicLanguage) # must after lang

    self._refreshImage()

class TopicInput(QtWidgets.QDialog):

  topicReceived = Signal(unicode, unicode, unicode) # json topic, json image, json tickets

  def __init__(self, parent=None):
    WINDOW_FLAGS = Qt.Dialog|Qt.WindowMinMaxButtonsHint
    super(TopicInput, self).__init__(parent, WINDOW_FLAGS)
    skqss.class_(self, 'texture')
    self.setWindowTitle(mytr_("New Topic"))
    self.setWindowIcon(rc.icon('window-textedit'))
    self.__d = _TopicInput(self)
    #self.statusBar() # show status bar

  def imageEnabled(self): return self.__d.imageEnabled
  def setImageEnabled(self, t): self.__d.imageEnabled = t

  def setSubject(self, subjectId, subjectType):
    self.__d.subjectId = subjectId
    self.__d.subjectType = subjectType

  def type(self): return self.__d.topicType
  def setType(self, v): self.__d.topicType = v

  def imagePath(self): return self.__d.imagePath
  def setImagePath(self, v): self.__d.imagePath = v

  #def clear(self): self.__d.clear()

  def setVisible(self, value):
    """@reimp @public"""
    if value and not self.isVisible():
      self.__d.refresh()
    super(TopicInput, self).setVisible(value)

class _TopicInputManager:
  def __init__(self):
    self.dialogs = []
    self.imageEnabled = True

  @staticmethod
  def _createDialog():
    import windows
    parent = windows.top()
    ret = TopicInput(parent)
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
    ret.topicReceived.connect(q.topicReceived)
    return ret

class TopicInputManager(QObject):
  def __init__(self, parent=None):
    super(TopicInputManager, self).__init__(parent)
    self.__d = _TopicInputManager()

    from PySide.QtCore import QCoreApplication
    qApp = QCoreApplication.instance()
    qApp.aboutToQuit.connect(self.hide)

    import dataman
    dataman.manager().loginChanged.connect(lambda name: name or name == 'guest' or self.hide())

    #import netman
    #netman.manager().onlineChanged.connect(lambda t: t or self.hide())

  topicReceived = Signal(unicode, unicode, unicode) # json topic, json image, json tickets

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

  def newTopic(self, type='chat', subjectId=0, subjectType='', imagePath=''):
    """
    @param* type  str  topic type
    @param* subjectId  long
    @param* subjectType  str
    @param* imagePath  unicode
    """
    w = self.__d.getDialog(self)
    w.setSubject(subjectId, subjectType)
    w.setType(type)
    w.setImagePath(imagePath)
    w.show()

  def isImageEnabled(self): return self.__d.imageEnabled
  def setImageEnabled(self, t): self.__d.imageEnabled = t

#@memoized
#def manager(): return TopicInputManager()

#@QmlObject
class TopicInputManagerBean(QObject):
  def __init__(self, parent=None, manager=None):
    super(TopicInputManagerBean, self).__init__(parent)
    self.manager = manager or TopicInputManager(self)
    self.manager.topicReceived.connect(self.topicReceived)

  topicReceived = Signal(unicode, unicode) # json topic, json image

  @Slot(str, long, str)
  def newTopic(self, topicType, subjectId, subjectType):
    self.manager.newTopic(topicType, subjectId=subjectId, subjectType=subjectType)

  imageEnabledChanged = Signal(bool)
  imageEnabled = Property(bool,
      lambda self: self.manager.isImageEnabled(),
      lambda self, t: self.manager.setImageEnabled(t),
      notify=imageEnabledChanged)

if __name__ == '__main__':
  a = debug.app()
  m = TopicInputManager()
  m.newTopic()
  a.exec_()

# EOF
