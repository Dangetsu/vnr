# coding: utf8
# mttest.py
# 11/20/2013 jichi
# Machine translation tester.

__all__ = 'MTTester',

if __name__ == '__main__':
  import sys
  sys.path.append('..')
  import debug
  debug.initenv()

from functools import partial
from PySide.QtCore import Qt
from Qt5 import QtWidgets
from sakurakit import skqss, skwidgets
from sakurakit.skclass import memoizedproperty
from sakurakit.skdebug import dprint
from sakurakit.sktr import tr_
from mytr import my, mytr_
from share.mt import mtinfo
import config, dataman, evalutil, i18n, rc, richutil, settings, textutil, termman, trman

class MTTester(QtWidgets.QDialog):

  def __init__(self, parent=None):
    WINDOW_FLAGS = Qt.Dialog|Qt.WindowMinMaxButtonsHint
    super(MTTester, self).__init__(parent)
    skqss.class_(self, 'texture')
    self.setWindowFlags(WINDOW_FLAGS)
    self.setWindowTitle(mytr_("Test Machine Translation"))
    self.setWindowIcon(rc.icon('window-mttest'))
    self.__d = _MTTester(self)
    #self.setContentsMargins(9, 9, 9, 9)
    self.resize(800, 300)
    dprint("pass")

# http://www.alanwood.net/unicode/arrows.html
_LEFTARROW = u'<span style="color:blue">←</span>'
_RIGHTARROW = u'<span style="color:blue">→</span>'
_UPARROW = u'<span style="color:blue">↑</span>'
_DOWNARROW = u'<span style="color:blue">↓</span>'

_EQ_LABEL = u'<span style="color:blue">＝</span>'
_NE_LABEL = u'<span style="color:red">≠</span>'

_EMPTY_TEXT = "(%s)" % tr_("Not changed")
_DISABLED_TEXT = "(%s)" % tr_("Disabled")
#_LANGUAGE_STAR = '<span style="color:green">+</span>' # plus
_TERM_STAR = '<span style="color:red">*</span>' # star

_TEXTEDIT_MINWIDTH = 120
_TEXTEDIT_MINHEIGHT = 200

class _MTTester(object):

  def __init__(self, q):
    self._createUi(q)

    tm = trman.manager()

    tm.languagesReceived.connect(lambda fr, to: (
        self.setFromLanguageLabelText(fr),
        self.setToLanguageLabelText(to)))
    tm.normalizedTextReceived.connect(lambda t:
        self.normalizedTextEdit.setPlainText(t or _EMPTY_TEXT))
    tm.inputTextReceived.connect(lambda t:
        self.inputTextEdit.setPlainText(t or _EMPTY_TEXT))
    tm.encodedTextReceived.connect(lambda t:
        self.encodedTextEdit.setPlainText(t or _EMPTY_TEXT))
    tm.delegateTextReceived.connect(lambda t:
        self.delegateTextEdit.setPlainText(t or _EMPTY_TEXT))

    tm.splitTextsReceived.connect(lambda l:
        self.splitTextEdit.setPlainText('\n--------\n'.join(l) if l else _EMPTY_TEXT))

    tm.delegateTranslationReceived.connect(lambda t:
        self.delegateTranslationEdit.setPlainText(t or _EMPTY_TEXT))
    tm.jointTranslationReceived.connect(lambda t:
        self.jointTranslationEdit.setPlainText(t or _EMPTY_TEXT))

    tm.outputSyntacticTranslationReceived.connect(lambda t:
        self.outputSyntacticTranslationEdit.setHtml(t or _EMPTY_TEXT))
    tm.decodedTranslationReceived.connect(lambda t:
        self.decodedTranslationEdit.setHtml(t or _EMPTY_TEXT))
    tm.outputTranslationReceived.connect(lambda t:
        self.outputTranslationEdit.setHtml(t or _EMPTY_TEXT))

    tm.splitTranslationsReceived.connect(lambda l:
        self.splitTranslationEdit.setHtml('<br/>--------<br/>'.join(l) if l else _EMPTY_TEXT))

  def _createUi(self, q):
    layout = QtWidgets.QVBoxLayout()

    row = QtWidgets.QHBoxLayout()
    row.addWidget(self.translateButton)
    row.addWidget(self.pasteButton)
    row.addWidget(self.speakButton)
    row.addWidget(self.translatorEdit)
    row.addWidget(self.fromLanguageEdit)
    row.addWidget(QtWidgets.QLabel(_RIGHTARROW))
    row.addWidget(self.toLanguageEdit)

    row.addWidget(QtWidgets.QLabel("("))
    row.addWidget(self.translatorLabel)
    #row.addWidget(QtWidgets.QLabel(":"))
    row.addWidget(self.fromLanguageLabel)
    row.addWidget(QtWidgets.QLabel(_RIGHTARROW))
    row.addWidget(self.toLanguageLabel)
    row.addWidget(QtWidgets.QLabel(")"))
    #row.addWidget(QtWidgets.QLabel(my.tr("Current game") + ":"))
    #row.addWidget(QtWidgets.QLabel("#"))
    row.addWidget(self.gameLabel)
    row.addStretch()
    row.addWidget(self.markButton)
    layout.addLayout(row)

    # First row
    grid = QtWidgets.QGridLayout()
    r = 0
    c = 0
    cell = QtWidgets.QVBoxLayout()
    cell.addWidget(self.textLabel)
    cell.addWidget(self.textEdit)
    grid.addLayout(cell, r, c)

    c += 1
    grid.addWidget(QtWidgets.QLabel(_RIGHTARROW), r, c)
    c += 1
    cell = QtWidgets.QVBoxLayout()
    row = QtWidgets.QHBoxLayout()
    row.addWidget(self.gameTextButton)
    row.addWidget(self.gameTextLabel)
    row.addStretch()
    cell.addLayout(row)
    cell.addWidget(self.gameTextEdit)
    grid.addLayout(cell, r, c)

    c += 2 # skip two columns

    c += 1
    grid.addWidget(QtWidgets.QLabel(_RIGHTARROW), r, c)
    c += 1
    cell = QtWidgets.QVBoxLayout()
    row = QtWidgets.QHBoxLayout()
    row.addWidget(self.normalizedTextButton)
    row.addWidget(self.normalizedTextLabel)
    row.addStretch()
    cell.addLayout(row)
    cell.addWidget(self.normalizedTextEdit)
    grid.addLayout(cell, r, c)

    c += 1
    grid.addWidget(QtWidgets.QLabel(_RIGHTARROW), r, c)
    c += 1
    cell = QtWidgets.QVBoxLayout()
    cell.addWidget(self.inputTextLabel)
    cell.addWidget(self.inputTextEdit)
    grid.addLayout(cell, r, c)

    c += 1
    grid.addWidget(QtWidgets.QLabel(_RIGHTARROW), r, c)
    c += 1
    cell = QtWidgets.QVBoxLayout()
    cell.addWidget(self.encodedTextLabel)
    cell.addWidget(self.encodedTextEdit)
    grid.addLayout(cell, r, c)

    c += 1
    grid.addWidget(QtWidgets.QLabel(_RIGHTARROW), r, c)
    c += 1
    cell = QtWidgets.QVBoxLayout()
    cell.addWidget(self.delegateTextLabel)
    cell.addWidget(self.delegateTextEdit)
    grid.addLayout(cell, r, c)

    c += 1
    grid.addWidget(QtWidgets.QLabel(_RIGHTARROW), r, c)
    c += 1
    cell = QtWidgets.QVBoxLayout()
    cell.addWidget(self.splitTextLabel)
    cell.addWidget(self.splitTextEdit)
    grid.addLayout(cell, r, c)

    # Second row

    r += 1
    c = 0
    label = QtWidgets.QLabel(_DOWNARROW)
    label.setAlignment(Qt.AlignCenter)
    grid.addWidget(label, r, c)

    c = 6 * 2 - 2 # totally six columns
    label = QtWidgets.QLabel(_DOWNARROW)
    label.setAlignment(Qt.AlignCenter)
    grid.addWidget(label, r, c)

    # Third row
    r += 1
    c = 0
    cell = QtWidgets.QVBoxLayout()
    cell.addWidget(self.directTranslationLabel)
    cell.addWidget(self.directTranslationEdit)
    grid.addLayout(cell, r, c)

    c += 1
    grid.addWidget(self.equalLabel, r, c)

    c += 1
    cell = QtWidgets.QVBoxLayout()
    cell.addWidget(self.finalTranslationLabel)
    cell.addWidget(self.finalTranslationEdit)
    grid.addLayout(cell, r, c)

    c += 1
    grid.addWidget(QtWidgets.QLabel(_LEFTARROW), r, c)
    c += 1
    cell = QtWidgets.QVBoxLayout()
    cell.addWidget(self.outputTranslationLabel)
    cell.addWidget(self.outputTranslationEdit)
    grid.addLayout(cell, r, c)

    c += 1
    grid.addWidget(QtWidgets.QLabel(_LEFTARROW), r, c)
    c += 1
    cell = QtWidgets.QVBoxLayout()
    cell.addWidget(self.decodedTranslationLabel)
    cell.addWidget(self.decodedTranslationEdit)
    grid.addLayout(cell, r, c)

    c += 1
    grid.addWidget(QtWidgets.QLabel(_LEFTARROW), r, c)
    c += 1
    cell = QtWidgets.QVBoxLayout()
    cell.addWidget(self.outputSyntacticTranslationLabel)
    cell.addWidget(self.outputSyntacticTranslationEdit)
    grid.addLayout(cell, r, c)

    c += 1
    grid.addWidget(QtWidgets.QLabel(_LEFTARROW), r, c)
    c += 1
    cell = QtWidgets.QVBoxLayout()
    cell.addWidget(self.delegateTranslationLabel)
    cell.addWidget(self.delegateTranslationEdit)
    grid.addLayout(cell, r, c)

    c += 1
    grid.addWidget(QtWidgets.QLabel(_LEFTARROW), r, c)
    c += 1
    cell = QtWidgets.QVBoxLayout()
    cell.addWidget(self.jointTranslationLabel)
    cell.addWidget(self.jointTranslationEdit)
    grid.addLayout(cell, r, c)

    c += 1
    grid.addWidget(QtWidgets.QLabel(_LEFTARROW), r, c)
    c += 1
    cell = QtWidgets.QVBoxLayout()
    cell.addWidget(self.splitTranslationLabel)
    cell.addWidget(self.splitTranslationEdit)
    grid.addLayout(cell, r, c)

    layout.addLayout(grid)
    # Footer
    layout.addWidget(QtWidgets.QLabel("%s: %s" % (tr_("Note"),
        my.tr("Procedures marked as {0} would utilize Shared Dictionary.").format(_TERM_STAR))))
        #my.tr("Procedures marked as {0} behave differently for different user languages.").format(_LANGUAGE_STAR))))))

    q.setLayout(layout)

  def _clearTranslations(self):
    for it in (
        #self.textEdit,
        self.directTranslationEdit,
        self.gameTextEdit,
        self.normalizedTextEdit,
        self.inputTextEdit,
        self.encodedTextEdit,
        self.delegateTextEdit,
        self.splitTextEdit,
        self.splitTranslationEdit,
        self.jointTranslationEdit,
        self.delegateTranslationEdit,
        self.outputSyntacticTranslationEdit,
        self.decodedTranslationEdit,
        self.outputTranslationEdit,
        self.finalTranslationEdit,
      ):
      it.setPlainText(_EMPTY_TEXT)

  def _currentText(self):
    return self.textEdit.toPlainText().strip()
  def _currentFromLanguage(self):
    return config.LANGUAGES[self.fromLanguageEdit.currentIndex()]
  #def _currentToLanguage(self):
  #  return config.LANGUAGES[self.toLanguageEdit.currentIndex()]
  def _currentTranslator(self):
    return dataman.Term.HOSTS[self.translatorEdit.currentIndex()]

  def _isGameTermsEnabled(self): return self.gameTextButton.isChecked()
  def _isTranslationScriptEnabled(self): return self.normalizedTextButton.isChecked()

  def _isMarkEnabled(self): return self.markButton.isChecked()

  def _speak(self):
    t = self._currentText()
    if t:
      lang = self._currentFromLanguage()
      import ttsman
      ttsman.speak(t, language=lang)

  def _paste(self):
    from sakurakit import skclip
    t = skclip.gettext().strip()
    if t:
      self.textEdit.setPlainText(t)

  def _translate(self):
    t = self._currentText()
    if t:
      dprint("enter")
      self._clearTranslations()
      self.translatorLabel.setText(self.translatorEdit.currentText())
      fr = self._currentFromLanguage()
      scriptEnabled = self._isTranslationScriptEnabled()
      params = {
        'fr': fr,
        'engine': self._currentTranslator(),
        #'ehndEnabled': scriptEnabled, # no longer change ehndEnabled
      }
      raw = trman.manager().translateTest(t, **params)
      if raw:
        self.directTranslationEdit.setPlainText(raw)

      if self._isGameTermsEnabled():
        #to = self._currentToLanguage()
        tt = textutil.normalize_punct(t)
        tt = termman.manager().applyGameTerms(tt, fr=fr) #, to=to)
        if tt != t:
          t = tt
          self.setGameTextEditText(t or _EMPTY_TEXT)
        else:
          self.setGameTextEditText(_EMPTY_TEXT)
      else:
        self.gameTextEdit.setPlainText(_DISABLED_TEXT)
      if t:
        mark = self._isMarkEnabled()
        t = trman.manager().translate(t, emit=True, mark=mark, scriptEnabled=scriptEnabled, **params)
        if t:
          if settings.global_().isTermRubyEnabled():
            t = richutil.renderRubyToPlainText(t)
          self.finalTranslationEdit.setHtml(t)
      dprint("leave")

  @memoizedproperty
  def markButton(self):
    ret = QtWidgets.QCheckBox(my.tr("Underline modified translation"))
    ret.setToolTip(my.tr("Underline modified translation when possible."))
    ret.setChecked(True)
    return ret

  @memoizedproperty
  def equalLabel(self):
    ret = QtWidgets.QLabel(_EQ_LABEL)
    ret.setToolTip(my.tr("Equal"))
    return ret

  def _refreshEqualLabel(self):
    eq = self.directTranslationEdit.toPlainText() == self.finalTranslationEdit.toPlainText()
    self.equalLabel.setText(_EQ_LABEL if eq else _NE_LABEL)
    self.equalLabel.setToolTip(my.tr("Equal") if eq else my.tr("Not equal"))

  @memoizedproperty
  def gameLabel(self):
    import dataman
    dm = dataman.manager()
    ret = QtWidgets.QLabel()
    ret.setToolTip(my.tr("Current game for game-specific definitions in the Shared Dictionary"))
    def _refresh():
      ret.setText('#' + (dm.currentGameName() or my.tr("Unknown game")))
      skqss.class_(ret, 'text-error' if dm.currentGame() else 'text-info')
    _refresh()
    dm.currentGameChanged.connect(_refresh)
    return ret

  @memoizedproperty
  def pasteButton(self):
    ret = QtWidgets.QPushButton(tr_("Paste"))
    skqss.class_(ret, 'btn btn-success')
    ret.setToolTip(tr_("Paste"))
    ret.clicked.connect(self._paste)
    return ret

  @memoizedproperty
  def speakButton(self):
    ret = QtWidgets.QPushButton(mytr_("Speak"))
    skqss.class_(ret, 'btn btn-default')
    ret.setToolTip(mytr_("Speak"))
    ret.clicked.connect(self._speak)
    return ret

  @memoizedproperty
  def translateButton(self):
    ret = QtWidgets.QPushButton(tr_("Translate"))
    skqss.class_(ret, 'btn btn-primary')
    ret.setToolTip(tr_("Translate"))
    ret.clicked.connect(self._translate)
    return ret

  @memoizedproperty
  def translatorEdit(self):
    ret = QtWidgets.QComboBox()
    ret.setEditable(False)
    ret.addItems(dataman.Term.TR_HOSTS)
    ret.setMaxVisibleItems(ret.count())
    ret.currentIndexChanged.connect(self._onTranslatorChanged)
    return ret

  def _onTranslatorChanged(self):
    key = self._currentTranslator()
    #ehnd = key == 'eztrans'
    tah = mtinfo.test_script(key)
    self.normalizedTextButton.setEnabled(tah) # or ehnd
    self.normalizedTextLabel.setEnabled(tah) # or ehnd
    self.normalizedTextEdit.setEnabled(tah)

  @memoizedproperty
  def fromLanguageEdit(self):
    ret = QtWidgets.QComboBox()
    ret.setToolTip(my.tr("Text language"))
    ret.setEditable(False)
    ret.addItems(map(i18n.language_name2, config.LANGUAGES))
    ret.setMaxVisibleItems(ret.count())
    return ret

  @memoizedproperty
  def toLanguageEdit(self):
    ret = QtWidgets.QLabel()
    ret.setToolTip(my.tr("User language"))
    ss = settings.global_()
    ret.setText(i18n.language_name2(ss.userLanguage()))
    ss.userLanguageChanged.connect(lambda lang:
        ret.setText(i18n.language_name2(lang)))
    return ret

  @memoizedproperty
  def translatorLabel(self):
    ret = QtWidgets.QLabel()
    ret.setText(self.translatorEdit.currentText())
    ret.setToolTip(my.tr("Current translator"))
    skqss.class_(ret, 'text-info')
    return ret

  @memoizedproperty
  def fromLanguageLabel(self):
    ret = QtWidgets.QLabel()
    ret.setText(self.fromLanguageEdit.currentText())
    ret.setToolTip(my.tr("Language adjusted for the translator"))
    skqss.class_(ret, 'text-info')
    return ret

  @memoizedproperty
  def toLanguageLabel(self):
    ret = QtWidgets.QLabel()
    ret.setText(self.toLanguageEdit.text())
    ret.setToolTip(my.tr("Language adjusted for the translator"))
    skqss.class_(ret, 'text-info')
    return ret

  def setFromLanguageLabelText(self, lang):
    """
    @param  lang  unicode
    """
    label = self.fromLanguageLabel
    edit = self.fromLanguageEdit
    t = i18n.language_name2(lang) #+ _LANGUAGE_STAR
    label.setText(t)
    skqss.class_(label, 'text-info' if t == edit.currentText() else 'text-error')

  def setToLanguageLabelText(self, lang):
    """
    @param  lang  unicode
    """
    label = self.toLanguageLabel
    edit = self.toLanguageEdit
    t = i18n.language_name2(lang)
    label.setText(t)
    skqss.class_(label, 'text-info' if t == edit.text() else 'text-error')

  # Text edits

  @classmethod
  def _createTextLabel(cls, edit, text='', tip=''):
    """
    @param  edit  QTextEdit
    @param* text  unicode
    @param* tip  unicode
    @return  QLabel
    """
    text = text or edit.toolTip()
    tip = tip or edit.toolTip()
    ret = QtWidgets.QLabel()
    ret.setText(text)
    ret.setToolTip(tip)
    edit.textChanged.connect(partial(cls._refreshTextLabel, ret, edit, text))
    return ret

  @staticmethod
  def _refreshTextLabel(label, edit, text):
    """
    @param  label  QLabel
    @param  edit  QTextEdit
    @param* text  unicode
    """
    t = edit.toPlainText().strip()
    if not t or t in (_EMPTY_TEXT, _DISABLED_TEXT):
      labelText = text
      skqss.class_(edit, 'text-muted')
    else:
      labelText = '%s (<span style="color:purple">%s</span>)' % (text, len(t))
      #skqss.class_(edit, 'readonly')
      skqss.class_(edit, '')
    label.setText(labelText)

  @staticmethod
  def _createTextView(tip='', rich=False):
    """
    @param* tip  unicode
    @param* rich  enable richText
    @return  QTextEdit
    """
    if rich:
      #ret = QtWidgets.QTextEdit(_EMPTY_TEXT)
      ret = skwidgets.SkTextEditWithAnchor(_EMPTY_TEXT)
      ret.anchorClicked.connect(evalutil.evalurl)
    else:
      ret = QtWidgets.QPlainTextEdit(_EMPTY_TEXT)
    ret.setMinimumWidth(_TEXTEDIT_MINWIDTH)
    ret.setMinimumHeight(_TEXTEDIT_MINHEIGHT)
    if tip:
      ret.setToolTip(tip)
    #ret.setAcceptRichText(False)
    #ret.setReadOnly(True)
    skqss.class_(ret, 'text-muted')
    #ret.resize(300, 200)
    return ret

  @memoizedproperty
  def textLabel(self):
    text = my.tr("Original text")
    ret = QtWidgets.QLabel()
    ret.setText('<span style="color:blue">%s</span>' % text)
    ret.setToolTip(my.tr("Original text to translate"))
    self.textEdit.textChanged.connect(lambda:
        ret.setText(
          '<span style="color:blue">%s</span> (<span style="color:purple">%s</span>)' % (
          text,
          len(self.textEdit.toPlainText().strip()),
        )))
    return ret
  @memoizedproperty
  def textEdit(self):
    ret = QtWidgets.QPlainTextEdit()
    ret.setMinimumWidth(_TEXTEDIT_MINWIDTH)
    ret.setMinimumHeight(_TEXTEDIT_MINHEIGHT)
    ret.setToolTip(my.tr("Original text to translate"))
    #ret.setAcceptRichText(False)
    skqss.class_(ret, 'normal')
    ret.setPlainText(
      u"【爽】「悠真くんを攻略すれば２１０円か。なるほどなぁ…」"
      #u"「ごめんなさい。こう言う時どんな顔すればいいのか分からないの。」【綾波レイ】"
    )
    #ret.resize(300, 200)
    return ret

  @memoizedproperty
  def gameTextButton(self):
    ret = QtWidgets.QCheckBox()
    ret.setChecked(True)
    return ret
  @memoizedproperty
  def gameTextLabel(self):
    return self._createTextLabel(self.gameTextEdit, my.tr("Apply game rules") + _TERM_STAR)
  @memoizedproperty
  def gameTextEdit(self):
    return self._createTextView(my.tr("Apply game definitions in the Shared Dictionary to correct game text"))
  def setGameTextEditText(self, t):
    e = self.gameTextEdit
    e.setPlainText(t)
    skqss.class_(e, 'text-muted' if t in (_EMPTY_TEXT, _DISABLED_TEXT) else '')

  @memoizedproperty
  def directTranslationLabel(self):
    return self._createTextLabel(self.directTranslationEdit, my.tr("Direct translation"))
  @memoizedproperty
  def directTranslationEdit(self):
    ret = self._createTextView(my.tr("Direct translation without modifications by VNR"))
    ret.textChanged.connect(self._refreshEqualLabel)
    return ret

  @memoizedproperty
  def jointTranslationLabel(self):
    return self._createTextLabel(self.jointTranslationEdit, my.tr("Concatenated translation"))
  @memoizedproperty
  def jointTranslationEdit(self):
    return self._createTextView(my.tr("Join split translations"), rich=True)

  @memoizedproperty
  def finalTranslationLabel(self):
    return self._createTextLabel(self.finalTranslationEdit, my.tr("Final translation"))
  @memoizedproperty
  def finalTranslationEdit(self):
    ret = self._createTextView(my.tr("Actual translation used by VNR"), rich=True)
    ret.textChanged.connect(self._refreshEqualLabel)
    return ret

  @memoizedproperty
  def normalizedTextButton(self):
    ret = QtWidgets.QCheckBox();
    ret.setChecked(True)
    return ret
  @memoizedproperty
  def normalizedTextLabel(self):
    return self._createTextLabel(self.normalizedTextEdit, my.tr("Apply translation script"))
  @memoizedproperty
  def normalizedTextEdit(self):
    return self._createTextView(my.tr("Rewrite Japanese according to the rules in TAH script"))

  @memoizedproperty
  def inputTextLabel(self):
    return self._createTextLabel(self.inputTextEdit, my.tr("Apply input rules") + _TERM_STAR)
  @memoizedproperty
  def inputTextEdit(self):
    return self._createTextView(my.tr("Apply input definitions in the Shared Dictionary to correct input text"))

  @memoizedproperty
  def encodedTextLabel(self):
    return self._createTextLabel(self.encodedTextEdit, my.tr("Encode translations") + _TERM_STAR)
  @memoizedproperty
  def encodedTextEdit(self):
    return self._createTextView(my.tr("Apply name and translation definitions in Shared Dictionary"))

  @memoizedproperty
  def delegateTextLabel(self):
    return self._createTextLabel(self.delegateTextEdit, my.tr("Delegate translation roles") + _TERM_STAR)
  @memoizedproperty
  def delegateTextEdit(self):
    return self._createTextView(my.tr("Apply proxy definitions in the Shared Dictionary to hide translation replacement"))

  @memoizedproperty
  def delegateTranslationLabel(self):
    return self._createTextLabel(self.delegateTranslationEdit, my.tr("Undelegate translation roles") + _TERM_STAR)
  @memoizedproperty
  def delegateTranslationEdit(self):
    return self._createTextView(my.tr("Recover applied proxy definitions in the Shared Dictionary"))

  @memoizedproperty
  def decodedTranslationLabel(self):
    return self._createTextLabel(self.decodedTranslationEdit, my.tr("Decode translations") + _TERM_STAR)
  @memoizedproperty
  def decodedTranslationEdit(self):
    return self._createTextView(my.tr("Recover applied name and translation definitions in the Shared Dictionary"),
        rich=True)

  @memoizedproperty
  def outputSyntacticTranslationLabel(self):
    return self._createTextLabel(self.outputSyntacticTranslationEdit, my.tr("Apply output rules w/ grammar") + _TERM_STAR)
  @memoizedproperty
  def outputSyntacticTranslationEdit(self):
    return self._createTextView(my.tr("Apply output definitions with grammatic roles in the Shared Dictionary to correct output translations"),
        rich=True)

  @memoizedproperty
  def outputTranslationLabel(self):
    return self._createTextLabel(self.outputTranslationEdit, my.tr("Apply output rules w/o grammar") + _TERM_STAR)
  @memoizedproperty
  def outputTranslationEdit(self):
    return self._createTextView(my.tr("Apply output definitions without grammatic roles in the Shared Dictionary to correct output translations"),
        rich=True)

  @memoizedproperty
  def splitTextLabel(self):
    return self._createTextLabel(self.splitTextEdit, my.tr("Split by punctuations"))
  @memoizedproperty
  def splitTextEdit(self):
    return self._createTextView(my.tr("Split either by sentences for offline Latin languages or by paragraphs otherwise"))

  @memoizedproperty
  def splitTranslationLabel(self):
    return self._createTextLabel(self.splitTranslationEdit, my.tr("Separated translations"))
  @memoizedproperty
  def splitTranslationEdit(self):
    return self._createTextView(my.tr("Translations for split texts"), rich=True)

if __name__ == '__main__':
  a = debug.app()
  w = MTTester()
  w.show()
  a.exec_()

# EOF
