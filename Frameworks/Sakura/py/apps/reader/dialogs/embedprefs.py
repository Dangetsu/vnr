# coding: utf8
# embedprefs.py
# 11/5/2012 jichi

__all__ = 'TextPrefsDialog',

if __name__ == '__main__':
  import sys
  sys.path.append('..')
  import debug
  debug.initenv()

import os
from functools import partial
from itertools import imap
from PySide.QtCore import Signal, Qt, QSize
from PySide.QtGui import QIcon
from Qt5 import QtWidgets
from sakurakit import skevents, skqss, skwidgets
from sakurakit.skclass import Q_Q, memoizedproperty, hasmemoizedproperty
from sakurakit.skdebug import dprint
from sakurakit.sktr import tr_
#from sakurakit.skunicode import u
from mytr import my, mytr_
import config, defs, gameagent,growl, i18n, rc, textman, textutil

TEXTEDIT_MAX_HEIGHT = 80
TEXTEDIT_MIN_WIDTH = 400
THREADLAYOUT_COLUMN_COUNT = 2

SS_TEXTEDIT_SCENE = "QPlainTextEdit{color:blue}" # btn-primary
SS_TEXTEDIT_NAME = "QPlainTextEdit{color:green}" # btn-success
#SS_TEXTEDIT_OTHER = "QPlainTextEdit{color:steelblue}" # btn-info
#SS_TEXTEDIT_IGNORED = "QPlainTextEdit{text-decoration:line-through}" # btn-danger
SS_TEXTEDIT_IGNORED = "" # btn-danger
SS_TEXTEDIT_HOOK = "QPlainTextEdit{color:red}"
SS_TEXTEDIT_HOOK_IGNORED = SS_TEXTEDIT_HOOK
#SS_TEXTEDIT_HOOK_IGNORED = "QPlainTextEdit{color:red;text-decoration:line-through}"

#SS_LABELS = {
#  defs.HOOK_THREAD_TYPE: "QLabel{color:red}",
#  defs.ENGINE_THREAD_TYPE: "QLabel{color:blue}",
#  defs.CUI_THREAD_TYPE: "QLabel{color:gray}",
#  defs.GUI_THREAD_TYPE: "",
#  defs.NULL_THREAD_TYPE: "",   # should never happen!
#}

READONLY = True

def _gameprofile():
  """
  @return  gameman.GameProfile
  """
  import gameman
  return gameman.manager().currentGame()

## Text thread view ##

class TextThreadView(QtWidgets.QWidget):
  """View of one thread"""
  def __init__(self, signature, parent=None):
    super(TextThreadView, self).__init__(parent)
    self.__d = _TextThreadView(self, signature)

  def setText(self, text):
    e = self.__d.textEdit
    e.setPlainText(text)
    e.moveCursor(QtWidgets.QTextCursor.End)

  def appendText(self, text):
    e = self.__d.textEdit
    e.appendPlainText(text)
    e.moveCursor(QtWidgets.QTextCursor.End)

  def hasText(self):
    e = self.__d.textEdit
    return bool(e.toPlainText())

  #def clearText(self):
  #  self.__d.textEdit.clear()

  roleChanged = Signal(int, long) # type, signature

  def role(self): # -> int
    row = self.__d.buttonRow.currentIndex()
    return (defs.SCENARIO_TEXT_ROLE if row == _TextThreadView.SCENARIO_BUTTON_ROW else
            defs.NAME_TEXT_ROLE if row == _TextThreadView.NAME_BUTTON_ROW else
            #defs.OTHER_TEXT_ROLE if row == _TextThreadView.OTHER_BUTTON_ROW else
            defs.UNKNOWN_TEXT_ROLE)

  def setRole(self, role):
    """
    @param  role  int
    """
    if role != self.role():
      self.__d.buttonRow.setCurrentIndex(
        _TextThreadView.SCENARIO_BUTTON_ROW if role == defs.SCENARIO_TEXT_ROLE else
        _TextThreadView.NAME_BUTTON_ROW if role == defs.NAME_TEXT_ROLE else
        #_TextThreadView.OTHER_BUTTON_ROW if role == defs.OTHER_TEXT_ROLE else
        _TextThreadView.IGNORE_BUTTON_ROW
      )
      self.__d.updateStyleSheet()

@Q_Q
class _TextThreadView(object):
  SCENARIO_BUTTON_ROW = 0
  NAME_BUTTON_ROW = 1
  #OTHER_BUTTON_ROW = 2
  IGNORE_BUTTON_ROW = 2

  def __init__(self, q, signature):
    self.signature = signature
    self._createUi(q)
    #self.updateStyleSheet()

  def _createUi(self, q):
    layout = QtWidgets.QVBoxLayout()

    #tt = defs.threadtype(self.name)
    #ttip = i18n.threadtip(tt)

    #if self.name == defs.HCODE_THREAD_NAME:
    #  n = mytr_("H-code")
    #elif self.name in defs.CAONIMAGEBI_ENGINES:
    #  n = self.name + '<span style="color:red">%s</span>' % defs.CAONIMAGEBI_USERNAME
    #elif self.name in defs.OK123_ENGINES:
    #  n = self.name + '<span style="color:red">%s</span>' % defs.OK123_USERNAME
    #else:
    #  n = self.name

    title = """<span style="color:gray">%x</span>""" % self.signature
    #title = """%s <span style="color:gray">%x</span>""" % (n, self.signature)
    #enc = config.guess_thread_encoding(self.name)
    #if enc:
    #  title += """ <span style="color:#333">%s</span>""" % enc

    label = QtWidgets.QLabel(title)
    #label.setStyleSheet(SS_LABELS[tt])
    #label.setToolTip(ttip)

    # Must be consist with button rows
    self.buttonRow = skwidgets.SkButtonRow()

    b = self.buttonRow.addButton(mytr_("dialog"),
        tip=my.tr("This is main scenario"))   # scenario
    skqss.class_(b, 'btn btn-default btn-sm')
    b.toggled.connect(partial(lambda b, value:
        skqss.toggleclass(b, 'btn-primary', value),
        b))

    b = self.buttonRow.addButton(mytr_("name"),
        tip=my.tr("These are character names"))   # scenario
    skqss.class_(b, 'btn btn-default btn-sm')
    b.toggled.connect(partial(lambda b, value:
        skqss.toggleclass(b, 'btn-success', value),
        b))

    #b = self.buttonRow.addButton(tr_("other"),
    #    tip=my.tr("This is extra scenario"))   # other
    #skqss.class_(b, 'btn btn-default btn-sm')
    #b.toggled.connect(partial(lambda b, value:
    #    skqss.toggleclass(b, 'btn-info', value),
    #    b))

    #b = self.buttonRow.addButton(tr_("ignore"),
    #    tip=my.tr("Don't translate the text")) # ignored
    b = self.buttonRow.addButton(tr_("other"),
        tip=my.tr("This is extra scenario"))   # other
    skqss.class_(b, 'btn btn-default btn-sm')
    b.toggled.connect(partial(lambda b, value:
        skqss.toggleclass(b, 'btn-info', value),
        b))
    self.buttonRow.setCurrentIndex(_TextThreadView.IGNORE_BUTTON_ROW)
    self.buttonRow.currentIndexChanged.connect(self._onSelectedRoleChanged)
    self.buttonRow.currentIndexChanged.connect(self.updateStyleSheet)

    self.textEdit = QtWidgets.QPlainTextEdit()
    #self.textEdit.setToolTip(mytr_("Game text"))
    #self.textEdit.setToolTip(ttip)
    self.textEdit.setReadOnly(True)
    self.textEdit.setMaximumHeight(TEXTEDIT_MAX_HEIGHT)
    self.textEdit.setMinimumWidth(TEXTEDIT_MIN_WIDTH)
    #self.textEdit.setStyleSheet(
    #    SS_TEXTEDIT_HOOK_IGNORED if self.name == defs.HCODE_THREAD_NAME else
    #    SS_TEXTEDIT_IGNORED)

    header = QtWidgets.QHBoxLayout()
    header.addWidget(self.buttonRow)
    header.addStretch()
    header.addWidget(label)
    layout.addLayout(header)
    layout.addWidget(self.textEdit)
    q.setLayout(layout)

  def _onSelectedRoleChanged(self):
    q = self.q
    q.roleChanged.emit(q.role(), self.signature)

  def updateStyleSheet(self):
    row = self.buttonRow.currentIndex()
    #if self.name == defs.HCODE_THREAD_NAME:
    #  if row == _TextThreadView.IGNORE_BUTTON_ROW:
    #    ss = SS_TEXTEDIT_HOOK_IGNORED
    #  else:
    #    ss = SS_TEXTEDIT_HOOK
    #else:
    ss = (SS_TEXTEDIT_SCENE if row == _TextThreadView.SCENARIO_BUTTON_ROW else
          SS_TEXTEDIT_NAME if row == _TextThreadView.NAME_BUTTON_ROW else
          #SS_TEXTEDIT_OTHER if row == _TextThreadView.OTHER_BUTTON_ROW else
          SS_TEXTEDIT_IGNORED)
    self.textEdit.setStyleSheet(ss)

## Text tab ##

class TextTab(QtWidgets.QWidget):
  def __init__(self, parent=None):
    super(TextTab, self).__init__(parent)
    self.__d = _TextTab(self)

  warning = Signal(unicode)
  message = Signal(unicode)

  sizeChanged = Signal()
  #hookChanged = Signal(str)
  languageChanged = Signal(unicode)
  scenarioThreadChanged = Signal(long, unicode, unicode) # signature, name, encoding
  nameThreadChanged = Signal(long, unicode) # signature, name
  nameThreadDisabled = Signal()
  #otherThreadsChanged = Signal(dict) # {long signature:str name}

  def clear(self): self.__d.clear()
  def load(self): self.__d.load()
  def unload(self): self.__d.unload()
  def setActive(self, value): self.__d.setActive(value)

  def sizeHint(self):
    """@reimp @public"""
    n = self.__d.threadLayout.count()
    #w = 500; h = 150
    w = 500; h = 165
    if n <= 0:
      pass
    elif n < THREADLAYOUT_COLUMN_COUNT:
      h += 120 * 2
    else:
      row = 1 + (n - 1) / THREADLAYOUT_COLUMN_COUNT
      h += 125 * (1 + min(row, 3.5)) # max row count is 3
      w += -290 + 350 * THREADLAYOUT_COLUMN_COUNT
      if row > 2:
        w += 20
    return QSize(w, h)

@Q_Q
class _TextTab(object):

  def __init__(self, q):
    self._active = False # bool
    self._threadViews = {} # {long signature:TextThreadView}

    self._lastEncoding = 'sjift-jis' # str
    self._lastScenarioSignature = 0 # long
    self._lastNameSignature = 0 # long

    self._createUi(q)

  def _createUi(self, q):
    #hookPrefsButton = QtWidgets.QPushButton(my.tr("Edit /H Hook Code"))
    #skqss.class_(hookPrefsButton, 'btn btn-info')
    #hookPrefsButton.setToolTip(my.tr("Modify the game-specific ITH hook code") + " (Alt+H)")
    #hookPrefsButton.setStatusTip(hookPrefsButton.toolTip())
    #hookPrefsButton.clicked.connect(self._showHookPrefs)

    helpButton = QtWidgets.QPushButton(tr_("Help"))
    helpButton.setToolTip(tr_("Help"))
    skqss.class_(helpButton, 'btn btn-success')
    helpButton.clicked.connect(lambda: self.helpDialog.show())

    #wikiButton = QtWidgets.QPushButton(tr_("Wiki"))
    #wikiButton.setToolTip(tr_("Wiki"))
    #skqss.class_(wikiButton, 'btn btn-default')
    #import main
    #wikiButton.clicked.connect(lambda: main.manager().openWiki('VNR/Text Settings'))

    #cancelButton = QtWidgets.QPushButton(tr_("Cancel"))
    #cancelButton.clicked.connect(self.q.hide)

    threadArea = QtWidgets.QScrollArea()
    threadArea.setWidget(skwidgets.SkLayoutWidget(self.threadLayout))
    threadArea.setWidgetResizable(True)

    threadGroup = QtWidgets.QGroupBox()
    threadGroup.setTitle(mytr_("Text threads"))
    threadGroup.setLayout(skwidgets.SkWidgetLayout(threadArea))
    #threadGroup.setLayout(self.threadLayout)

    info = QtWidgets.QGroupBox("%s (%s)" % (
      tr_("Information"),
      tr_("read-only"),
    ))
    infoLayout = QtWidgets.QVBoxLayout()
    row = QtWidgets.QHBoxLayout()
    row.addWidget(QtWidgets.QLabel(mytr_("Game engine") + ":"))
    row.addWidget(self.engineLabel)
    row.addStretch()
    infoLayout.addLayout(row)
    info.setLayout(infoLayout)

    option = QtWidgets.QGroupBox(tr_("Options"))
    optionLayout = QtWidgets.QVBoxLayout()
    row = QtWidgets.QHBoxLayout()
    row.addWidget(QtWidgets.QLabel(mytr_("Game language")+ ":"))
    row.addWidget(self.languageEdit)
    row.addStretch()
    row.addWidget(QtWidgets.QLabel(tr_("Text encoding") + ":"))
    row.addWidget(self.encodingEdit)
    optionLayout.addLayout(row)
    option.setLayout(optionLayout)

    layout = QtWidgets.QVBoxLayout()
    row = QtWidgets.QHBoxLayout()
    if not READONLY:
      row.addWidget(self.saveButton)

    #row.addWidget(hookPrefsButton)
    row.addWidget(self.resetButton)
    #row.addWidget(wikiButton)
    if not READONLY:
      row.addWidget(helpButton)
    #row.addWidget(QtWidgets.QLabel(
    #  " <= " + my.tr("click help if you have questions")
    #))
    row.addStretch()
    layout.addLayout(row)

    col = QtWidgets.QVBoxLayout()
    col.addWidget(info)
    col.addWidget(option)
    row = QtWidgets.QHBoxLayout()
    row.addLayout(col)
    row.addStretch()
    layout.addLayout(row)

    layout.addWidget(threadGroup)

    msg = QtWidgets.QLabel("%s: %s" % (
        tr_("Note"),
        my.tr("All settings are read-only.")))
    skqss.class_(msg, "text-error")
    layout.addWidget(msg)

    #buttons = QtWidgets.QHBoxLayout()
    #buttons.addStretch()
    #buttons.addWidget(cancelButton)
    #buttons.addWidget(self.saveButton)
    #layout.addLayout(buttons)
    #layout.addWidget(introLabel)

    #layout.setContentsMargins(18, 18, 18, 9) # left, top, right, bottom
    #self.q.setCentralWidget(skwidgets.SkLayoutWidget(layout))

    q.setLayout(layout)

    #skwidgets.shortcut('alt+h', self._showHookPrefs, parent=q)

  @memoizedproperty
  def saveButton(self):
    ret = QtWidgets.QPushButton(tr_("Save"))
    ret.setToolTip(tr_("Save"))
    ret.setStatusTip(tr_("Save"))
    skqss.class_(ret, 'btn btn-primary')
    ret.setToolTip(my.tr("Apply text thread and encoding settings"))
    ret.clicked.connect(self._save)
    return ret

  @memoizedproperty
  def resetButton(self):
    ret = QtWidgets.QPushButton(tr_("Reset"))
    ret.setToolTip(tr_("Reset"))
    ret.setStatusTip(tr_("Reset"))
    skqss.class_(ret, 'btn btn-inverse')
    ret.setToolTip(my.tr("Reset to last saved settings"))
    ret.clicked.connect(self._reset)
    return ret

  @memoizedproperty
  def encodingEdit(self):
    ret = QtWidgets.QComboBox()
    ret.setEditable(False)
    ret.setToolTip(tr_("Text encoding"))
    ret.setStatusTip(tr_("Text encoding"))
    ret.addItems(map(i18n.encoding_desc, config.ENCODINGS))
    ret.setMaxVisibleItems(ret.count())
    ret.currentIndexChanged.connect(self._onSelectedEncodingChanged)
    return ret

  @memoizedproperty
  def languageEdit(self):
    ret = QtWidgets.QComboBox()
    ret.setEditable(False)
    ret.addItems(map(i18n.language_name2, config.LANGUAGES))
    ret.setMaxVisibleItems(ret.count())
    ret.currentIndexChanged.connect(self._refreshLanguageEdit)
    return ret

  @memoizedproperty
  def engineLabel(self):
    ret = QtWidgets.QLabel()
    skqss.class_(ret, 'text-info')
    return ret

  #def _refreshKeepsHookButton(self):
  #  self.keepsHookButton.setEnabled(bool(texthook.global_().currentHookCode()))

  @memoizedproperty
  def threadLayout(self): return QtWidgets.QGridLayout()

  #@memoizedproperty
  #def hookPrefsDialog(self):
  #  q = self.q
  #  import hookprefs
  #  ret = hookprefs.HookPrefsDialog(q)
  #  ret.hookCodeEntered.connect(q.hookChanged)
  #  ret.hookCodeDeleted.connect(partial(
  #      q.hookChanged.emit, ""))

  #  # Automatically hide me when game exit
  #  gameagent.global_().processDetached.connect(ret.hide)

  #  h = self._deletedHookCode()
  #  ret.setDeletedHook(h)
  #  return ret

  #def _showHookPrefs(self): self.hookPrefsDialog.show()

  #def _refreshHookDialog(self):
  #  if hasmemoizedproperty(self, 'hookPrefsDialog'):
  #    h = self._deletedHookCode()
  #    self.hookPrefsDialog.setDeletedHook(h)

  #@staticmethod
  #def _deletedHookCode():
  #  """
  #  @return  str not None
  #  """
  #  g = _gameprofile()
  #  return g.deletedHook if g else ""

  @memoizedproperty
  def helpDialog(self):
    import help
    return help.EmbeddedTextSettingsHelpDialog(self.q)

  def setActive(self, active):
    if self._active != active:
      import rpcman
      rpc = rpcman.manager()
      if active:
        rpc.engineTextReceived.connect(self._addText)
      else:
        rpc.engineTextReceived.disconnect(self._addText)
      self._active = active

  #def _transformText(self, text):
  #  """
  #  @param  text  unicode
  #  @return  unicode
  #  """
  #  return text

  def _canSave(self):
    g = _gameprofile()
    agent = gameagent.global_()
    if not g or not g.hasThread() or not agent.isConnected() or not agent.engine():
      self.q.warning.emit(my.tr("No running game"))
      return False
    if not self._scenarioSignature():
      self.q.warning.emit(my.tr("Missing major text thread"))
      return False

    self.q.message.emit(my.tr("Press SAVE to save changes"))
    return True

  def _reset(self):
    #textman.manager().removeIgnoredThreads()
    self.clear()
    self.load()

  def _save(self):
    if not self._canSave():
      return
    q = self.q

    tm = textman.manager()

    agent = gameagent.global_()
    engine = agent.engine()
    engineName = defs.to_ith_engine_name(engine)

    scenesig = self._scenarioSignature()
    namesig = self._nameSignature()
    enc = self._encoding()
    lang = self._language()
    #threads = tm.threadsBySignature()
    changed = False
    if scenesig:
      if lang != tm.gameLanguage():
        dprint("language changed")
        changed = True
        skevents.runlater(partial(
            q.languageChanged.emit,
            lang))
      if scenesig != self._lastScenarioSignature or enc != self._lastEncoding:
        dprint("scenario thread changed")
        changed = True
        self._lastScenarioSignature = scenesig
        self._lastEncoding = enc
        agent.setEncoding(enc)
        agent.setScenarioSignature(scenesig)
        #name = threads[sig].name
        skevents.runlater(partial(
            q.scenarioThreadChanged.emit,
            scenesig, engineName, enc))

    if namesig != self._lastNameSignature:
      dprint("name thread changed")
      changed = True
      self._lastNameSignature = namesig
      agent.setNameSignature(namesig)
      if not namesig:
        skevents.runlater(q.nameThreadDisabled.emit)
      else:
        #name = threads[namesig].name
        skevents.runlater(partial(
            q.nameThreadChanged.emit,
            namesig, engineName))

    #sig_set = set(self._otherSignatures())
    #if sig_set != tm.otherSignatures():
    #  dprint("other threads changed")
    #  changed = True
    #  skevents.runlater(partial(
    #      q.otherThreadsChanged.emit,
    #      {sig:threads[sig].name for sig in sig_set}))

    msg = (my.tr("Text settings are saved") if changed else
           my.tr("Text settings are not changed"))
    q.message.emit(msg)
    growl.msg(msg)

    dprint("pass")

  def clear(self):
    if self._threadViews:
      self._threadViews.clear()
      skwidgets.clear_layout(self.threadLayout, delwidget=True)
      #self.q.centralWidget().show()

  #def _updateThread(self, thread, encoding=None, ignoreType=False):
  #  """
  #  @param  thread  textman.TextThread
  #  @param  ignoreType  bool
  #  """
  #  encoding = encoding or self._encoding()
  #  try:
  #    view = self._threadViews[thread.signature]
  #    if not ignoreType:
  #      view.setThreadType(thread.type)
  #  except KeyError:
  #    skevents.runlater(self.q.sizeChanged.emit)
  #    view = self._threadViews[thread.signature] = TextThreadView(
  #        name=thread.name, signature=thread.signature)
  #    if not ignoreType:
  #      view.setThreadType(thread.type)
  #    view.threadTypeChanged.connect(self._setThreadType)
  #    view.threadTypeChanged.connect(self._refreshSaveButton)

  #    n = self.threadLayout.count()
  #    row = n / THREADLAYOUT_COLUMN_COUNT
  #    col = n % THREADLAYOUT_COLUMN_COUNT
  #    self.threadLayout.addWidget(view, row, col)

  #  f = lambda it: self._transformText(textutil.to_unicode(it, encoding))
  #  text = '\n\n'.join(imap(f, thread.data))
  #  view.setText(text)

  def _setRole(self, role, signature):
    for sig, view in self._threadViews.iteritems():
      if sig == signature:
        view.setRole(role)
      else:
        for t in defs.SCENARIO_TEXT_ROLE, defs.NAME_TEXT_ROLE: # unique threads
          if role == t and role == view.role():
            view.setRole(defs.UNKNOWN_TEXT_ROLE)

  def _refreshEncodingEdit(self):
    if self._encoding() in ('shift-jis', 'utf-16'):
      skqss.removeclass(self.encodingEdit, 'warning')
    else:
      skqss.addclass(self.encodingEdit, 'warning')

  def _refreshLanguageEdit(self):
    if self._language() == 'ja':
      skqss.removeclass(self.languageEdit, 'warning')
    else:
      skqss.addclass(self.languageEdit, 'warning')

  def unload(self):
    agent = gameagent.global_()
    #if self._lastEncoding:
    agent.setEncoding(self._lastEncoding)
    if self._lastScenarioSignature:
      agent.setScenarioSignature(self._lastScenarioSignature)
    #if self._lastNameSignature:
    agent.setNameSignature(self._lastNameSignature)

  def load(self):
    tm = textman.manager()
    lang = tm.gameLanguage()
    try: langIndex = config.LANGUAGES.index(lang)
    except ValueError: langIndex = 0
    self.languageEdit.setCurrentIndex(langIndex)

    enc = tm.encoding()
    self._setEncoding(enc)

    self._lastEncoding = enc
    self._lastScenarioSignature = tm.scenarioThreadSignature()
    self._lastNameSignature = tm.nameThreadSignature()

    self._refreshSaveButton()
    self._refreshEngineLabel()

    #self._refreshHookDialog()

    for role,sig in (
        (defs.SCENARIO_TEXT_ROLE, self._lastScenarioSignature),
        (defs.NAME_TEXT_ROLE, self._lastNameSignature),
      ):
      if sig and sig not in self._threadViews:
        self._createView(signature=sig, role=role)

  def _refreshEngineLabel(self):
    engine = gameagent.global_().engine()
    if not engine:
      msg = tr_('Unknown') # This should never happen
    else:
      tip = config.guess_thread_encoding(engine)
      if engine in config.EMBEDDED_EN_GAME_ENGINES:
        if tip:
          tip += ", "
        tip += '<span style="color:purple">%s</span>' % my.tr("English-only")
      if tip:
        msg = "%s (%s)" % (engine, tip)
      else:
        msg = engine
    self.engineLabel.setText(msg)

  def _refreshSaveButton(self):
    self.saveButton.setEnabled(self._canSave())

  def _onSelectedEncodingChanged(self):
    gameagent.global_().setEncoding(self._encoding())
    self._refreshSaveButton()
    self._refreshEncodingEdit()

  def _addText(self, text, _, signature, role): #, needsTranslation
    """
    @param  text  unicode
    @param  _  str or int64  hash of the text
    @param  signature  long
    @param  role  int
    """
    #dprint("name = %s" % name)
    view = self._threadViews.get(signature) or self._createView(
        signature=signature, text=text, role=role)

    if view.hasText():
      view.appendText('\n' + text)
    else:
      view.setText(text)

  def _createView(self, signature, role, text=''):
    """
    @param  text  unicode
    @param  signature  long
    @param  role  int
    @return  TextThreadView
    """
    skevents.runlater(self.q.sizeChanged.emit)
    view = self._threadViews[signature] = TextThreadView(signature=signature)
    if role and role != defs.OTHER_TEXT_ROLE:
      view.setRole(role)
    #if not ignoreType:
    #  view.setThreadType(thread.type)
    view.roleChanged.connect(self._setRole)
    view.roleChanged.connect(self._refreshSaveButton)

    n = self.threadLayout.count()
    row = n / THREADLAYOUT_COLUMN_COUNT
    col = n % THREADLAYOUT_COLUMN_COUNT
    self.threadLayout.addWidget(view, row, col)

    if text:
      view.setText(text)
    return view

  def _scenarioSignature(self):
    for sig, view in self._threadViews.iteritems():
      if view.role() == defs.SCENARIO_TEXT_ROLE:
        return sig
    return 0

  def _nameSignature(self):
    for sig, view in self._threadViews.iteritems():
      if view.role() == defs.NAME_TEXT_ROLE:
        return sig
    return 0

  #def _otherSignatures(self):
  #  return [sig
  #    for sig, view in self._threadViews.iteritems()
  #    if view.threadType() == textman.OTHER_THREAD_TYPE
  #  ]

  def _encoding(self):
    return config.ENCODINGS[self.encodingEdit.currentIndex()]
    #return self.encodingEdit.currentText().lower()

  def _language(self):
    return config.LANGUAGES[self.languageEdit.currentIndex()]

  def _setEncoding(self, value): # str ->
    try: index = config.ENCODINGS.index(value)
    except ValueError: index = 0
    self.encodingEdit.setCurrentIndex(index)

## Information tab ##

#@Q_Q
#class InfoTab(QtWidgets.QWidget):
#  def __init__(self, parent=None):
#    super(InfoTab, self).__init__(parent)
#    self.__d = _InfoTab(self)
#
#  warning = Signal(unicode)
#  message = Signal(unicode)
#
#  def clear(self): self.__d.clear()
#  def load(self): self.__d.load()
#
#  def sizeHint(self):
#    """@reimp"""
#    return QSize(500, 380)

## Main window ##

# Use main window for status bar
class TextPrefsDialog(QtWidgets.QMainWindow):
  def __init__(self, parent=None):
    WINDOW_FLAGS = Qt.Dialog|Qt.WindowMinMaxButtonsHint
    super(TextPrefsDialog, self).__init__(parent, WINDOW_FLAGS)
    skqss.class_(self, 'texture')
    self.setWindowTitle("%s (%s)" % (
      mytr_("Text Settings"),
      my.tr("Engine: VNR"),
    ))
    self.__d = _TextPrefsDialog(self)
    dprint("pass")

  visibleChanged = Signal(bool)

  #hookChanged = Signal(str)
  #launchPathChanged = Signal(unicode)
  #loaderChanged = Signal(unicode)
  languageChanged = Signal(unicode)
  scenarioThreadChanged = Signal(long, unicode, unicode) # signature, name, encoding
  nameThreadChanged = Signal(long, unicode) # signature, name
  nameThreadDisabled = Signal()
  #otherThreadsChanged = Signal(dict) # {long signature:str name}

  def updateSize(self):
    sz = self.sizeHint()
    self.setMinimumSize(sz)
    self.resize(sz)

  def setVisible(self, visible):
    """@reimp @public"""
    d = self.__d
    if visible:
      g = _gameprofile()
      icon = g.icon() if g else None
      if not icon or icon.isNull():
        icon = rc.icon('logo-reader')
      self.setWindowIcon(icon)

      title = "%s (%s)" % (
        mytr_("Text Settings"),
        my.tr("Engine: VNR"),
      )

      name = g.name() if g else None
      if name:
        title = "%s - %s" % (name, title)
      self.setWindowTitle(title)

    update = visible != self.isVisible()
    if update:
      if visible:
        d.clear()
        d.load()
        #self.updateEnabled()
        skevents.runlater(self.updateSize)
      else:
        d.unload()
    #texthook.global_().setWhitelistEnabled(not visible)

    d.setActive(visible)
    super(TextPrefsDialog, self).setVisible(visible)

    if update:
      self.visibleChanged.emit(visible)

  #def updateEnabled(self):
  #  g = _gameprofile()
  #  self.setEnabled(bool(g))

  def clear(self):
    if self.isVisible():
      self.setWindowIcon(QIcon())
      self.setWindowTitle(mytr_("Text Settings"))
    self.__d.clear()

  def sizeHint(self):
    """@reimp @public"""
    return self.centralWidget().sizeHint()

@Q_Q
class _TextPrefsDialog(object):

  def __init__(self, q):
    self._createUi(q)

  def _createUi(self, q):
    #q.addTab(self.textTab, tr_("Text"), rc.icon('pref-text'),
    #         tip=my.tr("Text thread and hook"))
    #q.addTab(self.infoTab, tr_("Properties"), rc.icon('pref-config'),
    #         tip=my.tr("Game names and locations"))
    q.setCentralWidget(self.textTab)

  @memoizedproperty
  def textTab(self):
    q = self.q
    ret = TextTab()
    ret.message.connect(self.showMessage)
    ret.warning.connect(self.showWarning)
    ret.sizeChanged.connect(q.updateSize)
    #ret.hookChanged.connect(q.hookChanged)
    ret.languageChanged.connect(q.languageChanged)
    ret.scenarioThreadChanged.connect(q.scenarioThreadChanged)
    ret.nameThreadChanged.connect(q.nameThreadChanged)
    ret.nameThreadDisabled.connect(q.nameThreadDisabled)
    #ret.otherThreadsChanged.connect(q.otherThreadsChanged)
    return ret

  #@memoizedproperty
  #def infoTab(self):
  #  ret = InfoTab()
  #  ret.message.connect(self.showMessage)
  #  ret.warning.connect(self.showWarning)
  #  ret.launchPathChanged.connect(self.q.launchPathChanged)
  #  ret.loaderChanged.connect(self.q.loaderChanged)
  #  return ret

  #def itertabs(self):
  #  yield self.textTab
  #  #yield self.infoTab

  def clear(self):
    self.textTab.clear()
    #for t in self.itertabs():
    #  t.clear()

  def load(self):
    self.textTab.load()
    #for t in self.itertabs():
    #  t.load()

  def unload(self):
    self.textTab.unload()
    #for t in self.itertabs():
    #  t.unload()

  def setActive(self, value):
    self.textTab.setActive(value)

  def showWarning(self, text):
    bar = self.q.statusBar()
    skqss.class_(bar, 'warning')
    bar.showMessage(text)

  def showMessage(self, text):
    bar = self.q.statusBar()
    skqss.class_(bar, 'message')
    bar.showMessage(text)

if __name__ == '__main__':
  a = debug.app()
  w = TextPrefsDialog()
  w.show()
  a.exec_()

# EOF
