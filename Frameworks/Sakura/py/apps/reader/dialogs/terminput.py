# coding: utf8
# terminput.py
# 2/12/2014 jichi

__all__ = 'TermInput',

if __name__ == '__main__':
  import sys
  sys.path.append('..')
  import debug
  debug.initenv()

import re
from functools import partial
from PySide.QtCore import Qt #, Signal
from Qt5 import QtWidgets
from sakurakit import skdatetime, skevents, skqss
from sakurakit.skclass import Q_Q, memoizedproperty
from sakurakit.skdebug import dwarn
from sakurakit.sktr import tr_
from mytr import my, mytr_
import config, convutil, dataman, growl, i18n, rc, textutil

def create_label(text=""): # unicode -> QLabel
  ret = QtWidgets.QLabel()
  if text:
    ret.setText(text + ":")
  ret.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
  return ret

#COMBOBOX_MAXWIDTH = 100
COMBOBOX_MAXWIDTH = 80

RE_SHORT_HIRAGANA = re.compile(u'^[あ-ん]{1,3}$')

@Q_Q
class _TermInput(object):
  def __init__(self, q):
    self.gameId = 0 # long
    self.blockedLanguages = '' # str
    self._createUi(q)

  def _createUi(self, q):
    layout = QtWidgets.QVBoxLayout()

    # Options
    grid = QtWidgets.QGridLayout()
    r = 0

    grid.addWidget(create_label("From"), r, 0)
    row = QtWidgets.QHBoxLayout()
    row.addWidget(self.sourceLanguageEdit)
    row.addWidget(self._createInfoLabel(my.tr("should always be Japanese for a Japanese game")))
    grid.addLayout(row, r, 1)
    r += 1

    grid.addWidget(create_label("To"), r, 0)
    row = QtWidgets.QHBoxLayout()
    row.addWidget(self.targetLanguageEdit)
    row.addWidget(self._createInfoLabel(my.tr("target language to translate to")))
    grid.addLayout(row, r, 1)
    r += 1
    r += 1

    grid.addWidget(create_label(tr_("Type")), r, 0)
    row = QtWidgets.QHBoxLayout()
    row.addWidget(self.typeEdit)
    row.addWidget(self.typeLabel)
    grid.addLayout(row, r, 1)
    r += 1

    grid.addWidget(create_label(tr_("Context")), r, 0)
    row = QtWidgets.QHBoxLayout()
    row.addWidget(self.contextEdit)
    row.addWidget(self._createInfoLabel(my.tr("only enable under selected context")))
    grid.addLayout(row, r, 1)
    r += 1

    grid.addWidget(create_label(tr_("Translator")), r, 0)
    row = QtWidgets.QHBoxLayout()
    row.addWidget(self.hostEdit)
    row.addWidget(self._createInfoLabel(my.tr("only enable for selected translator")))
    grid.addLayout(row, r, 1)
    r += 1

    grid.addWidget(create_label(tr_("Options")), r, 0)
    grid.addWidget(self.specialButton, r, 1)
    r += 1

    grid.addWidget(self.regexButton, r, 1)
    r += 1

    grid.addWidget(self.phraseButton, r, 1)
    r += 1

    grid.addWidget(self.icaseButton, r, 1)
    r += 1

    #grid.addWidget(self.syntaxButton, r, 1)
    #r += 1

    grid.addWidget(self.privateButton, r, 1)
    r += 1

    grid.addWidget(create_label(tr_("Pattern")), r, 0)
    row = QtWidgets.QHBoxLayout()
    row.addWidget(self.patternEdit)
    row.addWidget(self.patternTtsButton)
    grid.addLayout(row, r, 1)
    r += 1

    grid.addWidget(create_label(tr_("Kanji")), r, 0)
    grid.addWidget(self.kanjiEdit, r, 1) # span for two rows
    r += 1

    grid.addWidget(create_label(tr_("Priority")), r, 0)
    row = QtWidgets.QHBoxLayout()
    row.addWidget(self.priorityEdit)
    row.addWidget(self.priorityLabel)
    grid.addLayout(row, r, 1)
    r += 1

    grid.addWidget(create_label(tr_("Translation")), r, 0)
    row = QtWidgets.QHBoxLayout()
    row.addWidget(self.textEdit)
    row.addWidget(self.textTtsButton)
    grid.addLayout(row, r, 1)
    r += 1

    grid.addWidget(create_label(mytr_("Yomigana")), r, 0)
    grid.addWidget(self.yomiEdit, r, 1) # span for two rows
    r += 1

    grid.addWidget(create_label(mytr_("Ruby")), r, 0)
    grid.addWidget(self.rubyEdit, r, 1) # span for two rows
    r += 1

    grid.addWidget(create_label(tr_("Role")), r, 0)
    grid.addWidget(self.roleEdit, r, 1)
    r += 1

    grid.addWidget(create_label(tr_("Comment")), r, 0)
    grid.addWidget(self.commentEdit, r, 1)
    r += 1

    layout.addLayout(grid)

    # Footer
    layout.addWidget(self.statusLabel)

    row = QtWidgets.QHBoxLayout()
    row.addStretch()
    row.addWidget(self.helpButton)
    row.addWidget(self.cancelButton)
    row.addWidget(self.saveButton)
    layout.addLayout(row)

    q.setLayout(layout)

  @staticmethod
  def _createInfoLabel(text=""): # unicode -> QWidget
    ret = QtWidgets.QLabel()
    if text:
      ret.setText("<= " + text)
    skqss.class_(ret, 'text-primary')
    return ret

  @memoizedproperty
  def helpButton(self):
    ret = QtWidgets.QPushButton(tr_("Help"))
    ret.setToolTip(tr_("Help"))
    skqss.class_(ret, 'btn btn-default')

    import main
    ret.clicked.connect(lambda: main.manager().openWiki("VNR/Shared Dictionary"))
    return ret

  @memoizedproperty
  def cancelButton(self):
    ret = QtWidgets.QPushButton(tr_("Cancel"))
    ret.setToolTip(tr_("Cancel"))
    skqss.class_(ret, 'btn btn-default')
    #ret.setDefault(True)
    ret.clicked.connect(self.q.hide)
    return ret

  @memoizedproperty
  def saveButton(self):
    ret = QtWidgets.QPushButton(tr_("Submit"))
    ret.setToolTip(tr_("Submit"))
    ret.setDefault(True)
    skqss.class_(ret, 'btn btn-primary')
    ret.clicked.connect(self.save)
    return ret

  @memoizedproperty
  def hostEdit(self):
    ret = QtWidgets.QComboBox()
    ret.setEditable(False)
    ret.addItem(tr_('All'))
    ret.addItems(dataman.Term.TR_HOSTS)
    #ret.setCurrentIndex(0) # default index
    ret.setMaxVisibleItems(ret.count())
    ret.setMaximumWidth(COMBOBOX_MAXWIDTH)
    ret.currentIndexChanged.connect(self.refresh)
    return ret

  @memoizedproperty
  def contextEdit(self):
    ret = QtWidgets.QComboBox()
    ret.setEditable(False)
    ret.addItem(tr_('All'))
    ret.addItems(dataman.Term.TR_CONTEXTS)
    #ret.setCurrentIndex(0) # default index
    ret.setMaxVisibleItems(ret.count())
    ret.setMaximumWidth(COMBOBOX_MAXWIDTH)
    ret.currentIndexChanged.connect(self.refresh)
    return ret

  @memoizedproperty
  def typeEdit(self):
    ret = QtWidgets.QComboBox()
    ret.setEditable(False)
    ret.addItems(dataman.Term.TR_TYPES)
    #ret.setCurrentIndex(0) # default index
    ret.setMaxVisibleItems(ret.count())
    ret.setMaximumWidth(COMBOBOX_MAXWIDTH)
    ret.currentIndexChanged.connect(self.refresh)
    return ret

  @memoizedproperty
  def typeLabel(self): return self._createInfoLabel()

  def _refreshTypeLabel(self):
    user = dataman.manager().user()

    tt = self._getType()
    #self.regexButton.setEnabled(tt not in ('suffix', 'macro'))
    #self.regexButton.setEnabled(tt != 'macro')
    #self.syntaxButton.setEnabled(tt == 'trans' and not user.isGuest())

    if tt == 'trans':
      t = my.tr("translate text from input to text language")
    elif tt == 'input':
      t = my.tr("transform text in input langauge before translation")
    elif tt == 'output':
      t = my.tr("transform text in output language after translation")
    elif tt == 'name':
      t = my.tr("a character name")
    elif tt == 'yomi':
      t = my.tr("katagana or hiragana of a name")
    elif tt == 'suffix':
      t = my.tr("a title after names")
    elif tt == 'prefix':
      t = my.tr("a title before names")
    elif tt == 'tts':
      t = my.tr("transform text before TTS")
    elif tt == 'ocr':
      t = my.tr("transform text after OCR")
    elif tt == 'game':
      t = my.tr("transform extracted game text")
    elif tt == 'macro':
      t = my.tr("reusable regular expression pattern")
    elif tt == 'proxy':
      t = my.tr("delegate translation for specific role")
    else:
      t = ''
    if t:
      t = "<= " + t
    self.typeLabel.setText(t)

  @memoizedproperty
  def sourceLanguageEdit(self):
    ret = QtWidgets.QComboBox()
    ret.setEditable(False)
    ret.addItems(map(i18n.language_name, config.LANGUAGES))
    ret.setMaxVisibleItems(ret.count())
    ret.setMaximumWidth(COMBOBOX_MAXWIDTH)
    #ret.setCurrentIndex(0) # Japanese by default
    ret.currentIndexChanged.connect(self._refreshStatus)
    #ret.currentIndexChanged.connect(self._refreshYomi)
    return ret

  @memoizedproperty
  def targetLanguageEdit(self):
    ret = QtWidgets.QComboBox()
    ret.setEditable(False)

    #items = map(i18n.language_name, config.LANGUAGES)
    items = [
      tr_("All languages") if it == 'ja' else i18n.language_name(it)
      for it in config.LANGUAGES
    ]
    ret.addItems(items)
    ret.setMaxVisibleItems(ret.count())
    ret.setMaximumWidth(COMBOBOX_MAXWIDTH)

    index = config.LANGUAGES.index(dataman.manager().user().language)
    ret.setCurrentIndex(index)

    ret.currentIndexChanged.connect(self._refreshStatus)
    ret.currentIndexChanged.connect(self._refreshYomi)
    return ret

  @memoizedproperty
  def regexButton(self):
    return QtWidgets.QCheckBox(tr_("Regular expression"))

  @memoizedproperty
  def phraseButton(self):
    return QtWidgets.QCheckBox(my.tr("Match phrase boundary"))

  @memoizedproperty
  def icaseButton(self):
    return QtWidgets.QCheckBox(tr_("Case-insensitive"))

  #@memoizedproperty
  #def syntaxButton(self):
  #  return QtWidgets.QCheckBox(my.tr("Japanese syntax aware"))

  @memoizedproperty
  def specialButton(self):
    ret = QtWidgets.QCheckBox(mytr_("Series-specific"))
    ret.setChecked(True) # enable series-specific by default
    ret.toggled.connect(self._refreshStatus)
    return ret

  @memoizedproperty
  def privateButton(self):
    ret = QtWidgets.QCheckBox(my.tr("Only visible to yourself"))
    ret.toggled.connect(self._refreshStatus)
    return ret

  @memoizedproperty
  def statusLabel(self):
    ret = QtWidgets.QLabel()
    ret.setToolTip(tr_("Status"))
    ret.setWordWrap(True)
    return ret

  @memoizedproperty
  def yomiEdit(self):
    ret = QtWidgets.QLineEdit()
    #skqss(ret, 'text-primary')
    ret.setToolTip(my.tr("Yomigana of translation"))
    ret.setReadOnly(True)
    #ret.setWordWrap(True)
    return ret

  @memoizedproperty
  def priorityEdit(self):
    ret = QtWidgets.QLineEdit()
    ret.setPlaceholderText(my.tr("Estimated pattern size"))
    ret.setToolTip(my.tr("Estimated number of characters in pattern"))
    #ret.textChanged.connect(self._refreshPriority)
    #ret.textChanged.connect(self._refreshStatus)
    ret.textChanged.connect(self.refresh)
    return ret

  @memoizedproperty
  def priorityLabel(self):
    ret = QtWidgets.QLabel()
    ret.setToolTip(my.tr("Default number of characters in pattern"))
    skqss.class_(ret, 'text-primary')
    return ret

  @memoizedproperty
  def kanjiEdit(self):
    ret = QtWidgets.QLineEdit()
    #skqss(ret, 'text-primary')
    ret.setToolTip(my.tr("Guessed kanji of pattern using MSIME"))
    ret.setReadOnly(True)
    #ret.setWordWrap(True)
    return ret

  @memoizedproperty
  def roleEdit(self):
    ret = QtWidgets.QLineEdit()
    #skqss.class_(ret, 'normal')
    ret.setPlaceholderText(my.tr("Such as x (Phrase) or m (Name)"))
    ret.setToolTip(tr_("Optional"))
    ret.textChanged.connect(self.refresh)
    return ret

  @memoizedproperty
  def rubyEdit(self):
    ret = QtWidgets.QLineEdit()
    skqss.class_(ret, 'normal')
    ret.setPlaceholderText(my.tr("Note above or after the translation"))
    ret.setToolTip(ret.placeholderText())
    ret.textChanged.connect(self.refresh)
    return ret

  @memoizedproperty
  def patternEdit(self):
    ret = QtWidgets.QLineEdit()
    skqss.class_(ret, 'normal')
    ret.setPlaceholderText(mytr_("Matched text"))
    ret.setToolTip(ret.placeholderText())
    ret.textChanged.connect(self.refresh)
    return ret

  @memoizedproperty
  def patternTtsButton(self):
    ret = self._createTtsButton()
    ret.clicked.connect(self._speakPattern)
    return ret
  @memoizedproperty
  def textTtsButton(self):
    ret = self._createTtsButton()
    ret.clicked.connect(self._speakText)
    return ret

  @staticmethod
  def _createTtsButton():
    ret = QtWidgets.QPushButton(u"♪") # おんぷ
    skqss.class_(ret, 'btn btn-default btn-toggle')
    ret.setToolTip(mytr_("TTS"))
    ret.setMaximumWidth(18)
    ret.setMaximumHeight(18)
    return ret

  def _speakPattern(self):
    t = self.patternEdit.text().strip()
    if t:
      import ttsman
      ttsman.speak(t)
  def _speakText(self):
    t = self.textEdit.text().strip()
    if t:
      import ttsman
      ttsman.speak(t)

  @memoizedproperty
  def textEdit(self):
    ret = QtWidgets.QLineEdit()
    skqss.class_(ret, 'normal')
    ret.setPlaceholderText(mytr_("Replaced text"))
    ret.setToolTip(ret.placeholderText())
    ret.textChanged.connect(self.refresh)
    return ret

  @memoizedproperty
  def commentEdit(self):
    ret = QtWidgets.QLineEdit()
    #skqss.class_(ret, 'normal')
    ret.setPlaceholderText(tr_("Comment"))
    ret.setToolTip(tr_("Optional"))
    #ret.textChanged.connect(self.refresh)
    return ret

  def _canSave(self): # -> bool
    return bool(self.patternEdit.text().strip()) and not self._isUseless() and not self._isIncompleted() and not self._isInvalid() and self._isAllowed() and self._checkPriority()

  def _isInvalid(self):
    return not textutil.validate_term_role(self.roleEdit.text().strip())

  def _isIncompleted(self):
    if self._getType() == 'proxy' and (not self.roleEdit.text().strip() or not self.textEdit.text().strip()):
      return True
    return False

  def _isAllowed(self):
    if self._getType() in ('suffix', 'prefix', 'macro', 'proxy'):
      user = dataman.manager().user()
      if user.isGuest():
        return False
    return True

  def _isUseless(self): # -> bool  has no effect
    pattern = self.patternEdit.text().strip()
    ruby = self.rubyEdit.text().strip()
    #if self._getLanguage() not in ('zhs', 'zht', 'ko') or # allow people to force save sth
    if not ruby and self._getType() in ('input', 'output', 'game', 'ocr', 'tts'):
      text = self.textEdit.text().strip()
      if pattern == text:
        return True
    return False

  def _getSourceLanguage(self): # -> str
    return config.LANGUAGES[self.sourceLanguageEdit.currentIndex()]

  def setSourceLanguage(self, v): # str ->
    try:
      index = config.LANGUAGES.index(v)
      self.sourceLanguageEdit.setCurrentIndex(index)
    except ValueError:
      dwarn("unknown language: %s" % v)

  def _getTargetLanguage(self): # -> str
    return config.LANGUAGES[self.targetLanguageEdit.currentIndex()]

  def setTargetLanguage(self, v): # str ->
    try:
      index = config.LANGUAGES.index(v)
      self.targetLanguageEdit.setCurrentIndex(index)
    except ValueError:
      dwarn("unknown language: %s" % v)

  def _getType(self): # -> str
    return dataman.Term.TYPES[self.typeEdit.currentIndex()]

  def _getHost(self): # -> str
    i = self.hostEdit.currentIndex()
    return dataman.Term.HOSTS[i - 1] if i else ''

  def _getContext(self): # -> str
    i = self.contextEdit.currentIndex()
    return dataman.Term.CONTEXTS[i - 1] if i else ''

  def _getPriority(self): # -> float
    t = self.priorityEdit.text().strip()
    if t:
      try: return float(t)
      except: pass
    return 0.0

  def _checkPriority(self): # -> bool
    pass
    t = self.priorityEdit.text().strip()
    if t:
      try:
        t = float(t)
        return True
      except Exception, e:
        dwarn(e)
        return False
    return True

  def setType(self, v): # str ->
    try: index = dataman.Term.TYPES.index(v)
    except ValueError:
      dwarn("unknown term type: %s" % v)
      index = 0
    self.typeEdit.setCurrentIndex(index)

  def save(self):
    if self._canSave():
      dm = dataman.manager()
      user = dm.user()
      if not user.name:
        return
      gameId = self.gameId or dm.currentGameId()
      md5 = dm.currentGameMd5()
      #if not gameId and not md5:
      #  return
      lang = self._getTargetLanguage()
      sourceLang = self._getSourceLanguage()
      type = self._getType()
      host = self._getHost() if type in dataman.Term.HOST_TYPES else ''
      context = self._getContext() if type in dataman.Term.CONTEXT_TYPES else ''
      role = self.roleEdit.text().strip() if type in dataman.Term.ROLE_TYPES else ''
      ruby = self.rubyEdit.text().strip() if type in dataman.Term.RUBY_TYPES else ''
      pattern = self.patternEdit.text().strip()
      comment = self.commentEdit.text().strip()
      text = self.textEdit.text().strip()
      priority = self._getPriority()
      if priority == len(pattern):
        priority = 0.0
      #regex = type == 'macro' or (self.regexButton.isChecked() and type != 'suffix')
      regex = type != 'proxy' and self.regexButton.isChecked() #and type != 'suffix')
      icase = type not in ('macro', 'proxy') and self.icaseButton.isChecked()
      phrase = type not in ('macro', 'proxy') and self.phraseButton.isChecked()
      #syntax = type == 'trans' and self.syntaxButton.isChecked() and not user.isGuest()
      special = self.specialButton.isChecked() and bool(gameId or md5)
      private = (type == 'proxy' or self.privateButton.isChecked()) and not user.isGuest()
      ret = dataman.Term(gameId=gameId, gameMd5=md5,
          userId=user.id,
          language=lang, sourceLanguage=sourceLang, type=type, host=host, context=context, private=private,
          special=special, regex=regex, phrase=phrase, icase=icase, #syntax=syntax,
          timestamp=skdatetime.current_unixtime(),
          priority=priority, pattern=pattern, text=text, ruby=ruby, role=role, comment=comment)

      self.clear()
      self.q.hide()

      skevents.runlater(partial(dm.submitTerm, ret), 200)

      from sakurakit.skstr import escapehtml
      growl.msg('<br/>'.join((
        my.tr("Add new term"),
        "%s = %s" % (escapehtml(pattern), escapehtml(text) or "(%s)" % tr_('empty')),
      )))

  def clear(self):
    for it in self.patternEdit, self.textEdit: #, self.commentEdit, self.rubyEdit:
      it.clear()

  #def autofill(self):
  #  lang = self._getLanguage()
  #  type = 'trans' if config.is_kanji_language(lang) else 'input'
  #  self._setType(type)

  def refresh(self):
    user = dataman.manager().user()
    self.privateButton.setEnabled(not user.isGuest())

    self.saveButton.setEnabled(self._canSave())

    type = self._getType()
    self.hostEdit.setEnabled(type in dataman.Term.HOST_TYPES)
    self.roleEdit.setEnabled(type in dataman.Term.ROLE_TYPES)
    self.rubyEdit.setEnabled(type in dataman.Term.RUBY_TYPES)
    self.contextEdit.setEnabled(type in dataman.Term.CONTEXT_TYPES)

    self._refreshTypeLabel()
    self._refreshPriority()
    self._refreshKanji()
    self._refreshYomi()
    self._refreshStatus()

  def _refreshStatus(self):
    w = self.statusLabel
    pattern = self.patternEdit.text().strip()
    type = self._getType()
    if not pattern:
      skqss.class_(w, 'text-primary')
      w.setText("%s: %s" % (tr_("Note"), my.tr("Missing pattern")))
    elif self._isIncompleted():
      skqss.class_(w, 'text-error')
      w.setText("%s: %s" % (tr_("Error"), my.tr("Missing translation or role.")))
    elif not self._checkPriority():
      skqss.class_(w, 'text-error')
      w.setText("%s: %s" % (tr_("Error"), my.tr("Specified priority is not a valid number.")))
    elif self._isInvalid():
      skqss.class_(w, 'text-error')
      w.setText("%s: %s ([_a-yA-Y0-9])" % (tr_("Error"), my.tr("Invalid translation role.")))
    elif self._isUseless():
      skqss.class_(w, 'text-error')
      w.setText("%s: %s" % (tr_("Warning"), my.tr("The pattern is the same as the translation that is useless.")))
    elif not self._isAllowed():
      skqss.class_(w, 'text-warning')
      w.setText("%s: %s" % (tr_("Warning"), my.tr("Guest user is not allowed to create rules in such type.")))
    elif self._getSourceLanguage() != 'ja':
      skqss.class_(w, 'text-success')
      w.setText("%s: %s" % (tr_("Note"), my.tr("Everything looks OK")))
    elif (self.regexButton.isChecked() and not textutil.validate_regex(pattern)
        or not textutil.validate_macro(self.textEdit.text().strip())
      ):
      skqss.class_(w, 'text-error')
      w.setText("%s: %s" % (tr_("Warning"), my.tr("Parentheses in the regular expression might not match.")))
    elif len(pattern) < 3 and not self.specialButton.isChecked():
      skqss.class_(w, 'text-error')
      w.setText("%s: %s" % (tr_("Warning"), my.tr("The pattern is kind of short. You might want to turn on the series-specific option.")))
    elif not self.textEdit.text().strip():
      skqss.class_(w, 'text-error')
      w.setText("%s: %s" % (tr_("Warning"), my.tr("The translation is empty. VNR will delete the text matched with the pattern.")))
    elif RE_SHORT_HIRAGANA.match(pattern):
      skqss.class_(w, 'text-error')
      w.setText("%s: %s" % (tr_("Warning"), my.tr("The pattern is short and only contains hiragana that could be ambiguous.")))
    elif len(pattern) > 10 and not self.regexButton.isChecked(): # and not self.syntaxButton.isChecked():
      skqss.class_(w, 'text-error')
      w.setText("%s: %s" % (tr_("Warning"), my.tr("The pattern is long. Please DO NOT add subtitles to Shared Dictionary.")))
    #elif type == 'yomi' and self._getTargetLanguage().startswith('zh'):
    #  skqss.class_(w, 'text-error')
    #  w.setText("%s: %s" % (tr_("Warning"), my.tr("Yomi type is useless for Chinese translation.")))
    elif type == 'proxy':
      skqss.class_(w, 'text-success')
      w.setText("%s: %s" % (tr_("Note"), my.tr("Proxy term is private by default. Please debug it again and again before make it public.")))
    else:
      skqss.class_(w, 'text-success')
      w.setText("%s: %s" % (tr_("Note"), my.tr("Everything looks OK")))

  def _refreshPriority(self):
    ok = self._checkPriority()
    skqss.class_(self.priorityEdit, 'text-success' if ok else 'text-error')

    pattern = self.patternEdit.text().strip()
    v = len(pattern)
    t = "(%s: %s)" % (tr_("default"), v)
    self.priorityLabel.setText(t)

  def _refreshYomi(self):
    w = self.yomiEdit
    text = self.textEdit.text().strip()
    if text:
      blans = self.blockedLanguages
      type = self._getType()
      if type == 'yomi':
        skqss.class_(w, 'text-primary')
        w.setEnabled(True)
        t = ', '.join((
          "%s (%s)" % (convutil.kana2name(text, lang), tr_(lang))
          for lang in config.YOMIGANA_LANGUAGES if lang not in blans
        ))
        pattern = self.patternEdit.text().strip()
        if 'zh' not in blans:
          if t:
            t += ', '
          if pattern and convutil.ja2zh_name_test(pattern):
            zhs = convutil.ja2zhs_name(pattern) or tr_("none")
            zht = convutil.ja2zht_name(pattern) or tr_("none")
            t += '%s (%s)' % (zht, tr_('zh'))
            if zhs != zht:
              t += ', %s (%s)' % (zhs, tr_('zhs'))
          else:
            t += '%s (%s)' % (tr_("none"), tr_('zh'))
        if t:
          w.setText(t)
          return

      elif type == 'name':
        lang = self._getTargetLanguage()
        if lang == 'en':
          skqss.class_(w, 'text-primary')
          w.setEnabled(True)
          t = ', '.join((
            "%s (%s)" % (convutil.toalphabet(text, lang), tr_(lang))
            for lang in config.ALPHABET_LANGUAGES if lang not in ('el', 'he') and lang not in blans
          ))
          if t:
            w.setText(t)
            return
        elif lang == 'ru':
          #for to in 'be', 'bg', 'uk':
          to = 'uk'
          if to not in blans:
            skqss.class_(w, 'text-primary')
            w.setEnabled(True)
            t = "%s (%s)" % (convutil.toalphabet(text, to=to, fr=lang), tr_(to))
            w.setText(t)
            return

      # Disabled
      #elif lang == 'uk':
      #  to = 'ru'
      #  if to not in blans:
      #    skqss.class_(w, 'text-primary')
      #    w.setEnabled(True)
      #    t = "%s (%s)" % (convutil.toalphabet(text, to=to, fr=lang), tr_(to))
      #    w.setText(t)
      #    return

    w.setEnabled(False)
    w.setText("(%s)" % tr_("Empty"))
    skqss.class_(w, 'text-muted')

  def _refreshKanji(self):
    w = self.kanjiEdit
    if self._getType() not in ('macro', 'output'):
      text = self.patternEdit.text().strip()
      if text:
        kanji = convutil.yomi2kanji(text)
        if kanji:
          if kanji != text:
            w.setText(kanji)
            skqss.class_(w, 'text-primary')
            w.setEnabled(True)
          else:
            w.setText("(%s)" % tr_("Equal"))
            skqss.class_(w, 'text-muted')
            w.setEnabled(False)
          return

    w.setEnabled(False)
    w.setText("(%s)" % tr_("Empty"))
    skqss.class_(w, 'text-muted')

class TermInput(QtWidgets.QDialog):
  #termEntered = Signal(QtCore.QObject) # Term

  def __init__(self, parent=None):
    WINDOW_FLAGS = Qt.Dialog|Qt.WindowMinMaxButtonsHint
    super(TermInput, self).__init__(parent, WINDOW_FLAGS)
    skqss.class_(self, 'texture')
    self.setWindowTitle(my.tr("Create dictionary entry"))
    self.setWindowIcon(rc.icon('window-dict'))
    self.__d = _TermInput(self)
    #self.__d.autofill()
    #self.resize(300, 270)
    self.resize(280, 320)
    #self.statusBar() # show status bar

    import dataman
    dataman.manager().loginChanged.connect(lambda name: name or self.hide())

    #import netman
    #netman.manager().onlineChanged.connect(lambda t: t or self.hide())

  def blockedLanguages(self): return self.__d.blockedLanguages
  def setBlockedLanguages(self, v): self.__d.blockedLanguages = v

  def setPattern(self, v): self.__d.patternEdit.setText(v)
  def setRuby(self, v): self.__d.rubyEdit.setText(v)
  def setText(self, v): self.__d.textEdit.setText(v)
  def setComment(self, v): self.__d.commentEdit.setText(v)
  def setType(self, v): self.__d.setType(v)
  def setLanguage(self, v): self.__d.setTargetLanguage(v)
  def setSourceLanguage(self, v): self.__d.setSourceLanguage(v)
  def setTokenId(self, v): self.__d.gameId = v # long

  #def autofill(self): self.__d.autofill()

  def setVisible(self, value):
    """@reimp @public"""
    if value and not self.isVisible():
      self.__d.refresh()
    super(TermInput, self).setVisible(value)

if __name__ == '__main__':
  a = debug.app()
  w = TermInput()
  w.show()
  a.exec_()

# EOF
