# coding: utf8
# textprefs.py
# 11/5/2012 jichi

__all__ = 'TextPrefsDialog',

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
from texthook import texthook
from mytr import my, mytr_
import config, defs, growl, i18n, rc, textman, textutil

TEXTEDIT_MAX_HEIGHT = 80
TEXTEDIT_MIN_WIDTH = 400
THREADLAYOUT_COLUMN_COUNT = 2

SS_TEXTEDIT_SCENE = "QPlainTextEdit{color:blue}" # btn-primary
SS_TEXTEDIT_NAME = "QPlainTextEdit{color:green}" # btn-success
SS_TEXTEDIT_OTHER = "QPlainTextEdit{color:steelblue}" # btn-info
#SS_TEXTEDIT_IGNORED = "QPlainTextEdit{text-decoration:line-through}" # btn-danger
SS_TEXTEDIT_IGNORED = "" # btn-danger
SS_TEXTEDIT_HOOK = "QPlainTextEdit{color:red}"
SS_TEXTEDIT_HOOK_IGNORED = SS_TEXTEDIT_HOOK
#SS_TEXTEDIT_HOOK_IGNORED = "QTextEdit{color:red;text-decoration:line-through}"

SS_LABELS = {
  defs.HOOK_THREAD_TYPE: "QLabel{color:red}",
  defs.ENGINE_THREAD_TYPE: "QLabel{color:blue}",
  defs.CUI_THREAD_TYPE: "QLabel{color:gray}",
  defs.GUI_THREAD_TYPE: "",
  defs.NULL_THREAD_TYPE: "QLabel{color:orange}",
}

def _gameprofile():
  """
  @return  gameman.GameProfile
  """
  import gameman
  return gameman.manager().currentGame()

## Text tab ##

@Q_Q
class _TextThreadView(object):
  SCENARIO_BUTTON_ROW = 0
  NAME_BUTTON_ROW = 1
  OTHER_BUTTON_ROW = 2
  IGNORE_BUTTON_ROW = 3

  def __init__(self, q, name, signature):
    self.name = name
    self.signature = signature
    self.keepsThreads = False
    self._createUi(q)
    #self.updateStyleSheet()

  def _createUi(self, q):
    layout = QtWidgets.QVBoxLayout()

    tt = defs.threadtype(self.name)
    ttip = i18n.threadtip(tt)

    if self.name == defs.NULL_THREAD_NAME:
      n = tr_("Not specified")
    elif self.name == defs.HCODE_THREAD_NAME:
      n = mytr_("H-code")
    elif self.name in defs.CAONIMAGEBI_ENGINES:
      n = self.name + '<span style="color:red">%s</span>' % defs.CAONIMAGEBI_USERNAME
    elif self.name in defs.OK123_ENGINES:
      n = self.name + '<span style="color:red">%s</span>' % defs.OK123_USERNAME
    #elif self.name.startswith('sce') or self.name in config.PSP_ALL_TEXT_THREADS:
    #  n = self.name + '<span style="color:gray">=0.9.x</span>' # no need to show
    elif self.name in config.PSP_099_TEXT_THREADS:
      n = self.name + '<span style="color:red">=0.9.9</span>'
    elif self.name in config.PSP_098_TEXT_THREADS:
      n = self.name + '<span style="color:purple">=0.9.8</span>'
    else:
      n = self.name
    if config.game_thread_embeddable(self.name):
      t = mytr_("embeddable")
      if self.name in config.EMBEDDED_EN_GAME_ENGINES:
        t += ', <span style="color:purple">%s</span>' % my.tr("English-only")
      n += ' <span style="color:darkgreen">(%s)</span>' % t
    title = '%s <span style="color:gray">%x</span>' % (n, self.signature)
    enc = config.guess_thread_encoding(self.name)
    if enc:
      title += ' <span style="color:#333">%s</span>' % enc
    elif self.name and self.name not in (defs.HCODE_THREAD_NAME, defs.NULL_THREAD_NAME) and 'PSP' not in self.name:
      title += '<br/><span style="color:red;font-weight:bold">(%s)</span>' % my.tr("Not supported, please update VNR")

    label = QtWidgets.QLabel(title)
    label.setStyleSheet(SS_LABELS[tt])
    label.setToolTip(ttip)

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

    b = self.buttonRow.addButton(tr_("other"),
        tip=my.tr("This is extra scenario"))   # other
    skqss.class_(b, 'btn btn-default btn-sm')
    b.toggled.connect(partial(lambda b, value:
        skqss.toggleclass(b, 'btn-info', value),
        b))

    b = self.buttonRow.addButton(tr_("ignore"),
        tip=my.tr("Don't translate the text")) # ignored
    skqss.class_(b, 'btn btn-default btn-sm')
    b.toggled.connect(partial(lambda b, value:
        skqss.toggleclass(b, 'btn-danger', value),
        b))

    self.buttonRow.setCurrentIndex(_TextThreadView.IGNORE_BUTTON_ROW)
    self.buttonRow.currentIndexChanged.connect(self._emitThreadType)
    self.buttonRow.currentIndexChanged.connect(self.updateStyleSheet)

    self.textEdit = QtWidgets.QPlainTextEdit()
    #self.textEdit.setToolTip(mytr_("Game text"))
    self.textEdit.setToolTip(ttip)
    self.textEdit.setReadOnly(True)
    self.textEdit.setMaximumHeight(TEXTEDIT_MAX_HEIGHT)
    self.textEdit.setMinimumWidth(TEXTEDIT_MIN_WIDTH)
    self.textEdit.setStyleSheet(
        SS_TEXTEDIT_HOOK_IGNORED if self.name == defs.HCODE_THREAD_NAME else
        SS_TEXTEDIT_IGNORED)

    header = QtWidgets.QHBoxLayout()
    header.addWidget(self.buttonRow)
    header.addStretch()
    header.addWidget(label)
    layout.addLayout(header)
    layout.addWidget(self.textEdit)
    q.setLayout(layout)

  def _emitThreadType(self):
    q = self.q
    q.threadTypeChanged.emit(q.threadType(), self.signature)

  def updateStyleSheet(self):
    row = self.buttonRow.currentIndex()
    if self.name == defs.HCODE_THREAD_NAME:
      if not self.keepsThreads and row == _TextThreadView.IGNORE_BUTTON_ROW:
        ss = SS_TEXTEDIT_HOOK_IGNORED
      else:
        ss = SS_TEXTEDIT_HOOK
    else:
      ss = (SS_TEXTEDIT_SCENE if row == _TextThreadView.SCENARIO_BUTTON_ROW else
            SS_TEXTEDIT_NAME if row == _TextThreadView.NAME_BUTTON_ROW else
            SS_TEXTEDIT_OTHER if row == _TextThreadView.OTHER_BUTTON_ROW else
            SS_TEXTEDIT_IGNORED)
    self.textEdit.setStyleSheet(ss)

class TextThreadView(QtWidgets.QWidget):
  """View of one thread"""
  def __init__(self, name, signature, parent=None):
    super(TextThreadView, self).__init__(parent)
    self.__d = _TextThreadView(self, name=name, signature=signature)

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

  def setKeepsThreads(self, val):
    self.__d.keepsThreads = val
    self.__d.updateStyleSheet()

  threadTypeChanged = Signal(int, long) # type, signature

  def threadType(self):
    row = self.__d.buttonRow.currentIndex()
    return (textman.SCENARIO_THREAD_TYPE if row == _TextThreadView.SCENARIO_BUTTON_ROW else
            textman.NAME_THREAD_TYPE if row == _TextThreadView.NAME_BUTTON_ROW else
            textman.OTHER_THREAD_TYPE if row == _TextThreadView.OTHER_BUTTON_ROW else
            textman.IGNORED_THREAD_TYPE)

  def setThreadType(self, type):
    """
    @param  type  int
    """
    if type != self.threadType():
      self.__d.buttonRow.setCurrentIndex(
        _TextThreadView.SCENARIO_BUTTON_ROW if type == textman.SCENARIO_THREAD_TYPE else
        _TextThreadView.NAME_BUTTON_ROW if type == textman.NAME_THREAD_TYPE else
        _TextThreadView.OTHER_BUTTON_ROW if type == textman.OTHER_THREAD_TYPE else
        _TextThreadView.IGNORE_BUTTON_ROW
      )
      self.__d.updateStyleSheet()

@Q_Q
class _TextTab(object):

  def __init__(self, q):
    self._active = False
    self.currentIgnoresRepeat = False # backup
    self.currentKeepsSpace = False # backup
    self._threadViews = {} # {long signature:TextThreadView}
    self._createUi(q)

  def _createUi(self, q):
    hookPrefsButton = QtWidgets.QPushButton(my.tr("Edit /H Hook Code"))
    skqss.class_(hookPrefsButton, 'btn btn-info')
    hookPrefsButton.setToolTip(my.tr("Modify the game-specific ITH hook code") + " (Alt+H)")
    hookPrefsButton.setStatusTip(hookPrefsButton.toolTip())
    hookPrefsButton.clicked.connect(self._showHookPrefs)

    helpButton = QtWidgets.QPushButton(tr_("Help"))
    helpButton.setToolTip(tr_("Help"))
    skqss.class_(helpButton, 'btn btn-success')
    helpButton.clicked.connect(lambda: self.helpDialog.show())

    wikiButton = QtWidgets.QPushButton(tr_("Wiki"))
    wikiButton.setToolTip(tr_("Wiki"))
    skqss.class_(wikiButton, 'btn btn-default')
    import main
    wikiButton.clicked.connect(lambda: main.manager().openWiki('VNR/Text Settings'))

    #cancelButton = QtWidgets.QPushButton(tr_("Cancel"))
    #cancelButton.clicked.connect(self.q.hide)

    threadArea = QtWidgets.QScrollArea()
    threadArea.setWidget(skwidgets.SkLayoutWidget(self.threadLayout))
    threadArea.setWidgetResizable(True)

    threadGroup = QtWidgets.QGroupBox()
    threadGroup.setTitle(mytr_("Text threads"))
    threadGroup.setLayout(skwidgets.SkWidgetLayout(threadArea))
    #threadGroup.setLayout(self.threadLayout)

    option = QtWidgets.QGroupBox(tr_("Options"))
    optionLayout = QtWidgets.QVBoxLayout()
    row = QtWidgets.QHBoxLayout()
    row.addWidget(QtWidgets.QLabel(mytr_("Game language")+ ":"))
    row.addWidget(self.languageEdit)
    row.addStretch()
    row.addWidget(QtWidgets.QLabel(tr_("Text encoding") + ":"))
    row.addWidget(self.encodingEdit)
    optionLayout.addLayout(row)
    optionLayout.addWidget(self.keepsThreadsButton)
    optionLayout.addWidget(self.removesRepeatButton)
    optionLayout.addWidget(self.ignoresRepeatButton)
    optionLayout.addWidget(self.keepsSpaceButton)
    option.setLayout(optionLayout)

    layout = QtWidgets.QVBoxLayout()
    row = QtWidgets.QHBoxLayout()
    row.addWidget(self.saveButton)
    row.addWidget(hookPrefsButton)
    row.addWidget(self.resetButton)
    row.addWidget(wikiButton)
    row.addWidget(helpButton)
    #row.addWidget(QtWidgets.QLabel(
    #  " <= " + my.tr("click help if you have questions")
    #))
    row.addStretch()
    layout.addLayout(row)

    row = QtWidgets.QHBoxLayout()
    row.addWidget(option)
    row.addStretch()
    layout.addLayout(row)

    layout.addWidget(threadGroup)

    #msg = QtWidgets.QLabel(my.tr("WARNING: PLEASE DO NOT TURN ON REPETITION FILTERS UNLESS THERE ARE REPETITIONS!"))
    msgLabel = QtWidgets.QLabel(my.tr("Don't forget to maximize the text speed (see Help)."))
    skqss.class_(msgLabel, "text-success")
    layout.addWidget(msgLabel)

    wikiLabel = QtWidgets.QLabel(my.tr('Please check this <a href="http://sakuradite.com/wiki/en/VNR/Game_Settings">Game Settings</a> wiki if there is no correct text.'))
    wikiLabel.setOpenExternalLinks(True)
    #skqss.class_(wikiLabel, "text-info")
    layout.addWidget(wikiLabel)

    #buttons = QtWidgets.QHBoxLayout()
    #buttons.addStretch()
    #buttons.addWidget(cancelButton)
    #buttons.addWidget(self.saveButton)
    #layout.addLayout(buttons)
    #layout.addWidget(introLabel)

    #layout.setContentsMargins(18, 18, 18, 9) # left, top, right, bottom
    #self.q.setCentralWidget(skwidgets.SkLayoutWidget(layout))

    q.setLayout(layout)

    skwidgets.shortcut('alt+h', self._showHookPrefs, parent=q)

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
    ret.currentIndexChanged.connect(self._refresh)
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
  def keepsSpaceButton(self):
    ret = QtWidgets.QCheckBox(
        my.tr("Insert spaces between words") +
        " (%s: %s)" % (tr_("for example"), "Howareyou! => How are you!"))
    #skqss.class_(ret, 'text-error')
    #ret.toggled.connect(lambda t:
    #    skqss.class_(ret, 'error' if t else 'text-error'))
    ret.setToolTip(my.tr("Preserve spaces between (English) words"))
    ret.toggled.connect(lambda t:
        t and self._confirmKeepSpace())
    ret.toggled.connect(texthook.global_().setKeepsSpace) # this is after confirmation
    return ret

  @memoizedproperty
  def removesRepeatButton(self):
    ret = QtWidgets.QCheckBox(
        my.tr("Eliminate finite repetition in the text") +
        " (%s: %s)" % (tr_("for example"), "YYeess!!NoNo! => Yes!No!"))
    skqss.class_(ret, 'text-error')
    ret.toggled.connect(lambda t:
        skqss.class_(ret, 'error' if t else 'text-error'))
    ret.setToolTip(my.tr("Warning: Please do not turn on repetition filters unless there are repetitions!"))
    ret.toggled.connect(lambda t:
        t and self._confirmRemoveRepeat(ret))
    return ret

  @memoizedproperty
  def ignoresRepeatButton(self):
    ret = QtWidgets.QCheckBox(
        my.tr("Ignore infinite cyclic repetition in the text") +
        " (%s: %s)" % (tr_("for example"), "YesYesYes... => Yes"))
    skqss.class_(ret, 'text-error')
    ret.toggled.connect(lambda t:
        skqss.class_(ret, 'error' if t else 'text-error'))
    ret.setToolTip(my.tr("Warning: Please do not turn on repetition filters unless there are repetitions!"))
    ret.toggled.connect(lambda t:
        t and self._confirmRemoveRepeat(ret))
    ret.toggled.connect(texthook.global_().setRemovesRepeat) # this is after confirmation
    return ret

  def _confirmRemoveRepeat(self, w):
    """
    @param  w  QAbstractButton
    """
    window = self.q.parentWidget()
    if window and window.isVisible():
      import prompt
      if not prompt.confirmRemoveRepeat():
        w.toggle()

  def _confirmKeepSpace(self):
    window = self.q.parentWidget()
    if window and window.isVisible():
      import prompt
      if not prompt.confirmKeepSpace():
        self.keepsSpaceButton.toggle()

  def _confirmKeepThreads(self):
    window = self.q.parentWidget()
    if window and window.isVisible():
      import prompt
      if not prompt.confirmKeepThreads():
        self.keepsThreadsButton.toggle()

  @memoizedproperty
  def keepsThreadsButton(self):
    ret = QtWidgets.QCheckBox(
        my.tr("Keep all threads from the selected dialog engine"))
    ret.toggled.connect(lambda t:
        skqss.class_(ret, 'error' if t else ''))
    ret.toggled.connect(self._refresh)
    ret.toggled.connect(lambda t:
        t and self._confirmKeepThreads())
    return ret

  #def _refreshKeepsHookButton(self):
  #  self.keepsHookButton.setEnabled(bool(texthook.global_().currentHookCode()))

  @memoizedproperty
  def threadLayout(self): return QtWidgets.QGridLayout()

  @memoizedproperty
  def hookPrefsDialog(self):
    q = self.q
    import hookprefs
    ret = hookprefs.HookPrefsDialog(q)
    ret.hookCodeEntered.connect(q.hookChanged)
    ret.hookCodeDeleted.connect(partial(
        q.hookChanged.emit, ""))

    # Automatically hide me when game exit
    texthook.global_().processDetached.connect(ret.hide)

    h = self._deletedHookCode()
    ret.setDeletedHook(h)
    return ret

  def _showHookPrefs(self): self.hookPrefsDialog.show()

  def _refreshHookDialog(self):
    if hasmemoizedproperty(self, 'hookPrefsDialog'):
      h = self._deletedHookCode()
      self.hookPrefsDialog.setDeletedHook(h)

  @staticmethod
  def _deletedHookCode():
    """
    @return  str not None
    """
    g = _gameprofile()
    return g.deletedHook if g else ""
    #if gp:
    #  import dataman
    #  g = dataman.manager().queryGame(md5=gp.md5)
    #  if g:
    #    return g.deletedHook
    #return ''

  @memoizedproperty
  def helpDialog(self):
    import help
    return help.TextSettingsHelpDialog(self.q)

  def setActive(self, active):
    if self._active != active:
      th = texthook.global_()
      if active:
        th.dataReceived.connect(self._addText)
        #th.hookCodeChanged.connect(self._refreshKeepsHookButton)
        #self._refreshKeepsHookButton()
      else:
        th.dataReceived.disconnect(self._addText)
        #th.hookCodeChanged.disconnect(self._refreshKeepsHookButton)
      self._active = active

  def _keepsSpace(self):
    """
    @return  bool
    """
    return self.keepsSpaceButton.isChecked()

  def _removesRepeat(self):
    """
    @return  bool
    """
    return self.removesRepeatButton.isChecked()

  def _ignoresRepeat(self):
    """
    @return  bool
    """
    return self.ignoresRepeatButton.isChecked()

  def _keepsThreads(self):
    """
    @return  bool
    """
    return self.keepsThreadsButton.isChecked()

  def _transformText(self, text):
    """
    @param  text  unicode
    @return  unicode
    """
    return textutil.remove_repeat_text(text) if self._removesRepeat() else text

  def _canSave(self):
    g = _gameprofile()
    if not g or not g.hasThread():
      self.q.warning.emit(my.tr("No running game"))
      return False
    if not self._scenarioSignature():
      self.q.warning.emit(my.tr("Missing major text thread"))
      return False

    self.q.message.emit(my.tr("Press SAVE to save changes"))
    return True

  def _reset(self):
    textman.manager().removeIgnoredThreads()
    self.clear()
    self.load()

  def _save(self):
    if not self._canSave():
      return
    q = self.q

    tm = textman.manager()
    sig = self._scenarioSignature()
    namesig = self._nameSignature()
    enc = self._encoding()
    lang = self._language()
    threads = tm.threadsBySignature()
    changed = False
    if sig:
      if lang != tm.gameLanguage():
        dprint("language changed")
        changed = True
        skevents.runlater(partial(
            q.languageChanged.emit,
            lang))
      if sig != tm.scenarioSignature() or enc != tm.encoding():
        dprint("scenario thread changed")
        changed = True
        name = threads[sig].name if sig in threads else defs.NULL_THREAD_NAME
        skevents.runlater(partial(
            q.scenarioThreadChanged.emit,
            sig, name, enc))

    if namesig != tm.nameSignature():
      dprint("name thread changed")
      changed = True
      if not namesig or namesig not in threads:
        skevents.runlater(q.nameThreadDisabled.emit)
      else:
        name = threads[namesig].name
        skevents.runlater(partial(
            q.nameThreadChanged.emit,
            namesig, name))

    sig_set = set(self._otherSignatures())
    if sig_set != tm.otherSignatures():
      dprint("other threads changed")
      changed = True
      skevents.runlater(partial(
          q.otherThreadsChanged.emit,
          {sig:threads[sig].name for sig in sig_set}))

    if sig:
      if self._removesRepeat() != tm.removesRepeatText():
        changed = True
        skevents.runlater(partial(
            q.removesRepeatTextChanged.emit,
            self._removesRepeat()))

      if self._ignoresRepeat() != self.currentIgnoresRepeat:
        self.currentIgnoresRepeat = self._ignoresRepeat()
        changed = True
        skevents.runlater(partial(
            q.ignoresRepeatTextChanged.emit,
            self.currentIgnoresRepeat))

      if self._keepsSpace() != self.currentKeepsSpace:
        self.currentKeepsSpace = self._keepsSpace()
        changed = True
        skevents.runlater(partial(
            q.keepsSpaceChanged.emit,
            self.currentKeepsSpace))

      if self._keepsThreads() != tm.keepsThreads():
        changed = True
        skevents.runlater(partial(
            q.keepsThreadsChanged.emit,
            self._keepsThreads()))

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

  def _updateThread(self, thread, encoding=None, ignoreType=False):
    """
    @param  thread  textman.TextThread
    @param  ignoreType  bool
    """
    encoding = encoding or self._encoding()
    keepsThreads = self._keepsThreads()
    try:
      view = self._threadViews[thread.signature]
      if not ignoreType:
        view.setThreadType(thread.type)
      view.setKeepsThreads(keepsThreads)
    except KeyError:
      skevents.runlater(self.q.sizeChanged.emit)
      view = self._threadViews[thread.signature] = TextThreadView(
          name=thread.name, signature=thread.signature)
      if not ignoreType:
        view.setThreadType(thread.type)
      if keepsThreads:
        view.setKeepsThreads(keepsThreads)
      view.threadTypeChanged.connect(self._setThreadType)
      view.threadTypeChanged.connect(self._refreshSaveButton)

      n = self.threadLayout.count()
      row = n / THREADLAYOUT_COLUMN_COUNT
      col = n % THREADLAYOUT_COLUMN_COUNT
      self.threadLayout.addWidget(view, row, col)

    f = lambda it: self._transformText(textutil.to_unicode(it, encoding))
    text = '\n\n'.join(imap(f, thread.data))
    view.setText(text)

  def _setThreadType(self, type_, signature):
    for sig, view in self._threadViews.iteritems():
      if sig == signature:
        view.setThreadType(type_)
      else:
        for t in textman.SCENARIO_THREAD_TYPE, textman.NAME_THREAD_TYPE: # unique threads
          if type_ == t and type_ == view.threadType():
            view.setThreadType(textman.IGNORED_THREAD_TYPE)

  def _refreshEncodingEdit(self):
    if self._encoding() in ('shift-jis', 'utf-16', 'utf-8'):
      skqss.removeclass(self.encodingEdit, 'warning')
    else:
      skqss.addclass(self.encodingEdit, 'warning')

  def _refreshLanguageEdit(self):
    if self._language() == 'ja':
      skqss.removeclass(self.languageEdit, 'warning')
    else:
      skqss.addclass(self.languageEdit, 'warning')

  def unload(self):
    texthook.global_().setRemovesRepeat(self.currentIgnoresRepeat)
    texthook.global_().setKeepsSpace(self.currentKeepsSpace)

  def load(self):
    th = texthook.global_()

    self.currentIgnoresRepeat = th.removesRepeat()
    self.ignoresRepeatButton.setChecked(self.currentIgnoresRepeat)

    self.currentKeepsSpace = th.keepsSpace()
    self.keepsSpaceButton.setChecked(self.currentKeepsSpace)

    tm = textman.manager()
    self.removesRepeatButton.setChecked(tm.removesRepeatText())

    self.keepsThreadsButton.setChecked(tm.keepsThreads())
    #self.keepsThreadsButton.setEnabled(bool(texthook.global_().currentHookCode()))

    lang = tm.gameLanguage()
    try: langIndex = config.LANGUAGES.index(lang)
    except ValueError: langIndex = 0
    self.languageEdit.setCurrentIndex(langIndex)

    enc = tm.encoding()
    self._setEncoding(enc)


    nullThreadFound = False
    for t in tm.threads():
      if t.name == defs.NULL_THREAD_NAME:
        nullThreadFound = True
      self._updateThread(t, encoding=enc)

    if not nullThreadFound:
      t = textman.TextThread(name=defs.NULL_THREAD_NAME, signature=defs.NULL_THREAD_SIGNATURE)
      self._updateThread(t, encoding=enc)

    self._refreshSaveButton()

    self._refreshHookDialog()

  def _refreshSaveButton(self):
    self.saveButton.setEnabled(self._canSave())

  def _refresh(self):
    enc = self._encoding()

    tm = textman.manager()
    for t in tm.threads():
      self._updateThread(t, encoding=enc, ignoreType=True)

    self._refreshSaveButton()
    self._refreshEncodingEdit()

  def _addText(self, _, data, signature, name):
    """
    @param  _  bytearray  raw data
    @param  data  bytearray  rendered data
    @param  signature  long
    @param  name  str
    """
    #dprint("name = %s" % name)
    view = self._threadViews.get(signature)
    if not view:
      tm = textman.manager()
      try: tt = textman.manager().threadsBySignature()[signature].type
      except KeyError: tt = textman.IGNORED_THREAD_TYPE

      # If old scenario signature is different from current, ignore the old one
      if tt == textman.SCENARIO_THREAD_TYPE:
        ss = self._scenarioSignature()
        if ss and ss != signature:
          tt = textman.IGNORED_THREAD_TYPE
      self._updateThread(textman.TextThread(
        name=name, signature=signature, data=[data], type=tt))
      view = self._threadViews[signature]

    text = self._transformText(textutil.to_unicode(data, self._encoding()))
    if view.hasText():
      view.appendText('\n' + text)
    else:
      view.setText(text)

  def _scenarioSignature(self):
    for sig, view in self._threadViews.iteritems():
      if view.threadType() == textman.SCENARIO_THREAD_TYPE:
        return sig
    return 0

  def _nameSignature(self):
    for sig, view in self._threadViews.iteritems():
      if view.threadType() == textman.NAME_THREAD_TYPE:
        return sig
    return 0

  def _otherSignatures(self):
    return [sig
      for sig, view in self._threadViews.iteritems()
      if view.threadType() == textman.OTHER_THREAD_TYPE
    ]

  def _encoding(self):
    return config.ENCODINGS[self.encodingEdit.currentIndex()]
    #return self.encodingEdit.currentText().lower()

  def _language(self):
    return config.LANGUAGES[self.languageEdit.currentIndex()]

  def _setEncoding(self, value): # str ->
    try: index = config.ENCODINGS.index(value)
    except ValueError: index = 0
    self.encodingEdit.setCurrentIndex(index)

class TextTab(QtWidgets.QWidget):
  def __init__(self, parent=None):
    super(TextTab, self).__init__(parent)
    self.__d = _TextTab(self)

  warning = Signal(unicode)
  message = Signal(unicode)

  sizeChanged = Signal()
  hookChanged = Signal(str)
  languageChanged = Signal(unicode)
  removesRepeatTextChanged = Signal(bool)
  ignoresRepeatTextChanged = Signal(bool)
  keepsSpaceChanged = Signal(bool)
  keepsThreadsChanged = Signal(bool)
  scenarioThreadChanged = Signal(long, unicode, unicode) # signature, name, encoding
  nameThreadChanged = Signal(long, unicode) # signature, name
  nameThreadDisabled = Signal()
  otherThreadsChanged = Signal(dict) # {long signature:str name}

  def clear(self): self.__d.clear()
  def load(self): self.__d.load()
  def unload(self): self.__d.unload()
  def setActive(self, value): self.__d.setActive(value)

  def sizeHint(self):
    """@reimp @public"""
    n = self.__d.threadLayout.count()
    #w = 500; h = 150
    #w = 500; h = 165 # + 15 for msg
    w = 500; h = 195  # + 20*2 for 2 msg labels
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
    ret.hookChanged.connect(q.hookChanged)
    ret.languageChanged.connect(q.languageChanged)
    ret.scenarioThreadChanged.connect(q.scenarioThreadChanged)
    ret.nameThreadChanged.connect(q.nameThreadChanged)
    ret.nameThreadDisabled.connect(q.nameThreadDisabled)
    ret.otherThreadsChanged.connect(q.otherThreadsChanged)
    ret.removesRepeatTextChanged.connect(q.removesRepeatTextChanged)
    ret.ignoresRepeatTextChanged.connect(q.ignoresRepeatTextChanged)
    ret.keepsSpaceChanged.connect(q.keepsSpaceChanged)
    ret.keepsThreadsChanged.connect(q.keepsThreadsChanged)
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
  #  yield self.infoTab

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

# Use main window for status bar
#class TextPrefsDialog(skwidgets.SkTabPane):
class TextPrefsDialog(QtWidgets.QMainWindow):
  def __init__(self, parent=None):
    WINDOW_FLAGS = Qt.Dialog|Qt.WindowMinMaxButtonsHint
    super(TextPrefsDialog, self).__init__(parent, WINDOW_FLAGS)
    skqss.class_(self, 'texture')
    self.setWindowTitle("%s (%s)" % (
      mytr_("Text Settings"),
      my.tr("Engine: ITH"),
    ))
    self.__d = _TextPrefsDialog(self)
    dprint("pass")

  hookChanged = Signal(str)
  #launchPathChanged = Signal(unicode)
  #loaderChanged = Signal(unicode)
  languageChanged = Signal(unicode)
  scenarioThreadChanged = Signal(long, unicode, unicode) # signature, name, encoding
  nameThreadChanged = Signal(long, unicode) # signature, name
  nameThreadDisabled = Signal()
  otherThreadsChanged = Signal(dict) # {long signature:str name}
  removesRepeatTextChanged = Signal(bool)
  ignoresRepeatTextChanged = Signal(bool)
  keepsSpaceChanged = Signal(bool)
  keepsThreadsChanged = Signal(bool)

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
        my.tr("Engine: ITH"),
      )

      name = g.name() if g else None
      if name:
        title = "%s - %s" % (name, title)
      self.setWindowTitle(title)

    if visible:
      texthook.global_().hijackProcess()

    if visible != self.isVisible():
      if visible:
        d.clear()
        d.load()
        self.updateEnabled()
        skevents.runlater(self.updateSize)
      else:
        d.unload()

    texthook.global_().setWhitelistEnabled(not visible)

    d.setActive(visible)
    super(TextPrefsDialog, self).setVisible(visible)

  def updateEnabled(self):
    g = _gameprofile()
    self.setEnabled(bool(g))

  def clear(self):
    if self.isVisible():
      self.setWindowIcon(QIcon())
      self.setWindowTitle(mytr_("Text Settings"))
    self.__d.clear()

  def sizeHint(self):
    """@reimp @public"""
    return self.centralWidget().sizeHint()
    #i = self.currentIndex()
    #try:
    #  if i == PREFS_TEXT_INDEX: # user prefs pane
    #    return self.__d.textTab.sizeHint()
    #  #elif i == PREFS_INFO_INDEX: # plugin prefs pane
    #  #  return self.__d.infoTab.sizeHint()
    #except AttributeError: pass # __d has not been initialized yet
    #return super(TextPrefsDialog, self).sizeHint()

# EOF
