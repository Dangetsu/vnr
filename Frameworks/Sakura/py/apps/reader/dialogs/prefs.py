# coding: utf8
# prefs.py
# 10/28/2012 jichi

__all__ = 'PrefsDialog',

from PySide.QtCore import Qt
from Qt5 import QtWidgets
from sakurakit import skmvc, skqss
from sakurakit.skdebug import dprint
from sakurakit.sktr import tr_
from sakurakit.skwidgets import shortcut
from mytr import my, mytr_
import rc
import _prefs

# Account

#PREFS_USER_INDEX = 0
#PREFS_LIBRARY_INDEX = 1
#PREFS_HONYAKU_INDEX = 2
#PREFS_TEXT_INDEX = 3
#PREFS_UI_INDEX = 4
#PREFS_FEATURE_INDEX = 5
##PREFS_PLUGIN_INDEX = 6
#
#PREFS_SIZES = {
#  PREFS_USER_INDEX: (360, 545),
#  PREFS_LIBRARY_INDEX: (470, 750),
#  PREFS_HONYAKU_INDEX: (470, 430),
#  PREFS_TEXT_INDEX: (360, 170),
#  PREFS_UI_INDEX: (480, 170),
#  PREFS_FEATURE_INDEX:  (550, 200),
#  #PREFS_PLUGIN_INDEX: (1000, 700),
#}

#@Q_Q
class _PrefsDialog(object):

  @staticmethod
  def _indexWidget(w):
    """
    @param  w  QWidget not None
    @return  unicode
    """
    return "\n".join((
      "\n".join(it.title() for it in w.findChildren(QtWidgets.QGroupBox)),
      "\n".join(it.text() for it in w.findChildren(QtWidgets.QLabel)),
      "\n".join(it.text() for it in w.findChildren(QtWidgets.QAbstractButton)),
    ))

  def __init__(self, q):
    self._createUi(q)

  def _createUi(self, q):
    self.userTab = _prefs.UserTab()
    self.textTab = _prefs.TextTab()
    self.ttsTab = _prefs.TtsTab()
    self.ocrTab = _prefs.OcrTab()
    #self.srTab = _prefs.SrTab()
    self.gameTab = _prefs.GameTab()
    self.shortcutsTab = _prefs.ShortcutsTab()
    self.uiTab = _prefs.UiTab()
    self.recordingsTab = _prefs.RecordingsTab()
    self.i18nTab = _prefs.I18nTab()
    self.engineTab = _prefs.EngineTab()
    self.internetTab = _prefs.InternetTab()
    self.featureTab = _prefs.FeatureTab()
    #self.pluginTab = _prefs.PluginTab()

    self.translationTab = _prefs.TranslationTab()
    self.machineTranslationTab = _prefs.MachineTranslationTab()
    self.dictionaryTranslationTab = _prefs.DictionaryTranslationTab()
    self.romanTranslationTab = _prefs.RomanTranslationTab()
    self.chineseTranslationTab = _prefs.ChineseTranslationTab()
    #self.translationScriptTab = _prefs.TranslationScriptTab()

    self.termTab = _prefs.TermTab()

    self.downloadsTab = _prefs.DownloadsTab()
    self.dictionaryDownloadsTab = _prefs.DictionaryDownloadsTab()
    self.launcherDownloadsTab = _prefs.LauncherDownloadsTab()
    self.fontDownloadsTab = _prefs.FontDownloadsTab()

    self.libraryTab = _prefs.LibraryTab()
    self.localeLibraryTab = _prefs.LocaleLibraryTab()
    self.translatorLibraryTab = _prefs.TranslatorLibraryTab()
    self.dictionaryLibraryTab = _prefs.DictionaryLibraryTab()
    self.ttsLibraryTab = _prefs.TtsLibraryTab()
    self.ocrLibraryTab = _prefs.OcrLibraryTab()

    #for t in self.itertabs():
    #  t.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
    #                  QtWidgets.QSizePolicy.Expanding)

    container = QtWidgets.QScrollArea() # widget container
    container.setWidgetResizable(True) # false by default
    container.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    container.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    #container.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    #container.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

    self.controller = skmvc.SkWidgetTreeController(parent=q, container=container, data={
      'display': tr_("Preferences"),
      'children': [
        { 'widget': self.userTab,
          'user': self._indexWidget(self.userTab),
          'decoration': rc.icon('pref-user'),
          'display': tr_("Account"),
          'toolTip': my.tr("User account"),
        },
        { 'widget': self.engineTab,
          'user': self._indexWidget(self.engineTab),
          #'display': u"%s (α)" % mytr_("Embedded"),
          'display': mytr_("Embedded"),
          'decoration': rc.icon('pref-config'),
          'toolTip': my.tr("Embedded subtitles"),
        },
        { 'widget': self.downloadsTab,
          'user': self._indexWidget(self.downloadsTab),
          'decoration': rc.icon('pref-download'),
          'display': tr_("Downloads"),
          'toolTip': my.tr("Download additional resources"),
          'children': [
            { 'widget': self.launcherDownloadsTab,
              'user': self._indexWidget(self.launcherDownloadsTab),
              'decoration': rc.icon('pref-locale'),
              'display': tr_("Launch"),
              'toolTip': my.tr("Locale changers"),
            },
            { 'widget': self.dictionaryDownloadsTab,
              'user': self._indexWidget(self.dictionaryDownloadsTab),
              'decoration': rc.icon('pref-dict'),
              'display': tr_("Dictionaries"),
              'toolTip': my.tr("Manage dictionaries"),
            },
            { 'widget': self.fontDownloadsTab,
              'user': self._indexWidget(self.fontDownloadsTab),
              'decoration': rc.icon('pref-font'),
              'display': tr_("Fonts"),
              'toolTip': my.tr("Manage fonts"),
            },
          ]
        },
        { 'widget': self.libraryTab,
          'user': self._indexWidget(self.libraryTab),
          'decoration': rc.icon('pref-library'),
          'display': tr_("Locations"),
          'toolTip': my.tr("Locations of external libraries"),
          'children': [
            { 'widget': self.localeLibraryTab,
              'user': self._indexWidget(self.localeLibraryTab),
              'decoration': rc.icon('pref-locale'),
              'display': tr_("Launch"),
              'toolTip': my.tr("Locations of external locale changers"),
            },
            { 'widget': self.translatorLibraryTab,
              'user': self._indexWidget(self.translatorLibraryTab),
              'decoration': rc.icon('pref-tr-path'),
              'display': tr_("Translators"),
              'toolTip': my.tr("Locations of external translators"),
            },
            { 'widget': self.dictionaryLibraryTab,
              'user': self._indexWidget(self.dictionaryLibraryTab),
              'decoration': rc.icon('pref-dict'),
              'display': tr_("Dictionaries"),
              'toolTip': my.tr("Locations of external dictionary"),
            },
            { 'widget': self.ttsLibraryTab,
              'user': self._indexWidget(self.ttsLibraryTab),
              'decoration': rc.icon('pref-tts-path'),
              'display': mytr_("TTS"),
              'toolTip': my.tr("Locations of external TTS"),
            },
            { 'widget': self.ocrLibraryTab,
              'user': self._indexWidget(self.ocrLibraryTab),
              'decoration': rc.icon('pref-ocr-path'),
              'display': mytr_("OCR"),
              'toolTip': my.tr("Locations of external OCR libraries"),
            },
          ]
        },
        { 'widget': self.translationTab,
          'user': self._indexWidget(self.translationTab),
          'decoration': rc.icon('pref-tr'),
          'display': tr_("Translation"),
          'toolTip': my.tr("Machine translators"),
          'children': [
            { 'widget': self.machineTranslationTab,
              'user': self._indexWidget(self.machineTranslationTab),
              'decoration': rc.icon('pref-tr-path'),
              'display': tr_("Translators"),
              'toolTip': my.tr("Preferred machine translators"),
            },
            { 'widget': self.dictionaryTranslationTab,
              'user': self._indexWidget(self.dictionaryTranslationTab),
              'decoration': rc.icon('pref-dict'),
              'display': tr_("Dictionaries"),
              'toolTip': my.tr("Preferred look-up dictionaries"),
            },
            { 'widget': self.romanTranslationTab,
              'user': self._indexWidget(self.romanTranslationTab),
              'decoration': rc.icon('pref-roman'),
              'display': mytr_("C/K Ruby"),
              'toolTip': my.tr("Romanization of texts in Chinese and Korean"),
            },
            { 'widget': self.chineseTranslationTab,
              'user': self._indexWidget(self.chineseTranslationTab),
              'decoration': rc.icon('pref-zh'),
              'display': tr_("Chinese"),
              'toolTip': my.tr("Preferred Chinese variant"),
            },
            #{ 'widget': self.translationScriptTab,
            #  'user': self._indexWidget(self.translationScriptTab),
            #  'decoration': rc.icon('pref-script'),
            #  'display': tr_("Scripts"),
            #  'toolTip': my.tr("Translation replacement scripts"),
            #},
          ]
        },
        { 'widget': self.ttsTab,
          'user': self._indexWidget(self.ttsTab),
          'decoration': rc.icon('pref-tts'),
          'display': mytr_("Text-To-Speech"),
          'toolTip': mytr_("Text-To-Speech") + " (TTS)",
        },
        #{ 'widget': self.srTab,
        #  'user': self._indexWidget(self.srTab),
        #  'decoration': rc.icon('pref-sr'),
        #  'display': u"%s (α)" % mytr_("ASR"),
        #  'toolTip': mytr_("Automatic speech recognition") + " (ASR)",
        #},
        { 'widget': self.ocrTab,
          'user': self._indexWidget(self.ocrTab),
          'decoration': rc.icon('pref-ocr'),
          'display': u"%s (α)" % mytr_("OCR"),
          'toolTip': mytr_("Optical character recognition") + " (OCR)",
        },
        { 'widget': self.textTab,
          'user': self._indexWidget(self.textTab),
          'display': tr_("Font"),
          'decoration': rc.icon('pref-text'),
          'toolTip': my.tr("Text rendering"),
        },
        { 'widget': self.gameTab,
          'user': self._indexWidget(self.gameTab),
          'decoration': rc.icon('pref-app'),
          'display': tr_("Launch"),
          'toolTip': my.tr("Game launch settings"),
        },
        { 'widget': self.shortcutsTab,
          'user': self._indexWidget(self.shortcutsTab),
          'decoration': rc.icon('pref-shortcuts'),
          'display': mytr_("Shortcuts"),
          'toolTip': my.tr("Mouse and keyboard shortcuts"),
        },
        { 'widget': self.recordingsTab,
          'user': self._indexWidget(self.recordingsTab),
          'decoration': rc.icon('pref-rec'),
          'display': mytr_("Recordings"),
          'toolTip': my.tr("Game recordings"),
        },
        { 'widget': self.uiTab,
          'user': self._indexWidget(self.uiTab),
          'decoration': rc.icon('pref-ui'),
          'display': tr_("UI"),
          'toolTip': my.tr("UI Theme"),
        },
        { 'widget': self.i18nTab,
          'user': self._indexWidget(self.i18nTab),
          'display': tr_("i18n"),
          'decoration': rc.icon('pref-i18n'),
          'toolTip': tr_("International"),
        },
        { 'widget': self.termTab,
          'user': self._indexWidget(self.termTab),
          'decoration': rc.icon('pref-share'),
          'display': mytr_("Shared Dictionary"),
          'toolTip': mytr_("Shared Dictionary"),
        },
        { 'widget': self.internetTab,
          'user': self._indexWidget(self.internetTab),
          'decoration': rc.icon('pref-internet'),
          'display': tr_("Internet"),
          'toolTip': my.tr("Internet options"),
        },
        { 'widget': self.featureTab,
          'user': self._indexWidget(self.featureTab),
          'decoration': rc.icon('pref-feature'),
          'display': tr_("Features"),
          'toolTip': my.tr("Application features"),
        },
      ],
    })
    self.controller.treeView().setHeaderHidden(True)
    self.controller.treeView().expandAll()

    left = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(self.controller.treeView())
    row = QtWidgets.QHBoxLayout()
    row.addWidget(self.controller.filterEdit())
    row.addWidget(self.controller.countLabel())
    layout.addLayout(row)
    left.setLayout(layout)
    q.addWidget(left)

    skqss.class_(self.controller.treeView(), 'texture')

    right = self.controller.widgetView()
    #right.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
    #                    QtWidgets.QSizePolicy.Expanding)
    q.addWidget(right)

    self.controller.currentIndexChanged.connect(self._refreshCurrentWidget)

    w = self.controller.filterEdit()
    w.setToolTip("%s (%s, %s, Ctrl+F)" %
        (tr_("Search"), tr_("case-insensitive"), tr_("regular expression")))
    shortcut('ctrl+f', w.setFocus, parent=q)

  def _refreshCurrentWidget(self):
    w = self.controller.currentWidget()
    if w:
      w.refresh()

  def itertabs(self):
    yield self.userTab
    yield self.textTab
    yield self.uiTab
    yield self.ttsTab
    yield self.ocrTab
    #yield self.srTab
    yield self.gameTab
    yield self.shortcutsTab
    yield self.recordingsTab
    yield self.i18nTab
    yield self.internetTab
    yield self.featureTab
    #yield self.pluginTab
    yield self.termTab

    yield self.translationTab
    yield self.machineTranslationTab
    yield self.dictionaryTranslationTab
    yield self.romanTranslationTab
    yield self.chineseTranslationTab
    #yield self.translationScriptTab

    yield self.downloadsTab
    yield self.fontDownloadsTab
    yield self.dictionaryDownloadsTab
    yield self.launcherDownloadsTab

    yield self.libraryTab
    yield self.localeLibraryTab
    yield self.translatorLibraryTab
    yield self.dictionaryLibraryTab
    yield self.ttsLibraryTab
    yield self.ocrLibraryTab

  def stop(self):
    for t in self.itertabs():
      if hasattr(t, 'stop'):
        t.stop()
    dprint("pass")

class PrefsDialog(QtWidgets.QSplitter):
  def __init__(self, parent=None):
    WINDOW_FLAGS = Qt.Dialog|Qt.WindowMinMaxButtonsHint
    super(PrefsDialog, self).__init__(Qt.Horizontal, parent)
    self.setWindowFlags(WINDOW_FLAGS)
    self.setWindowIcon(rc.icon('window-prefs'))
    self.setWindowTitle(tr_("Preferences"))
    self.setChildrenCollapsible(False)
    self.__d = _PrefsDialog(self)

    skqss.class_(self, 'texture')
    for i in xrange(self.count()):
      skqss.class_(self.widget(i), 'texture')

    self.resize(550,555) # large enough that there is no vertical scroll bar
    self.setSizes([170,380]) # 170 + 380 = 550 (width)
    dprint("pass")

  def setVisible(self, visible):
    """@reimp* @public"""
    if visible:
      self.load()
    super(PrefsDialog, self).setVisible(visible)
    if not visible:
      self.save()
      self.__d.stop()

  def load(self):
    for t in self.__d.itertabs():
      t.load()
    dprint("pass")

  def save(self):
    for t in self.__d.itertabs():
      t.save()
    dprint("pass")

  #def sizeHint(self):
  #  """@reimp @public"""
  #  try:
  #    #i = self.currentIndex()
  #    #return QtCore.QSize(*PREFS_SIZES[i])
  #    self.__d.controller.currentWidget().sizeHint()
  #  except KeyError:
  #    return super(PrefsDialog, self).sizeHint()

# EOF

#    q.addTab(self.userTab, text=tr_("User"), icon=rc.icon('pref-user'),
#             tip=my.tr("User account"))
#    q.addTab(self.libraryTab, text=tr_("Location"), icon=rc.icon('pref-config'),
#             tip=my.tr("Locations of external libraries"))
#    q.addTab(self.TranslationTab, text=tr_("Translator"), icon=rc.icon('pref-tr'),
#             tip=my.tr("Machine translators"))
#    q.addTab(self.textTab, text=tr_("Text"), icon=rc.icon('pref-text'),
#             tip=my.tr("Text rendering"))
#    q.addTab(self.uiTab, text=tr_("Theme"), icon=rc.icon('pref-ui'),
#             tip=my.tr("UI Theme"))
#    q.addTab(self.featureTab, text=tr_("Features"), icon=rc.icon('pref-feature'),
#             tip=my.tr("Application features"))
# User-defined plugins
#
#class _PluginTab(object):
#
#  def __init__(self, q):
#    q.addWidget(self.pyPluginPane)
#    q.addWidget(self.jsPluginPane)
#
#  def _confirmReset(self):
#    yes = QtWidgets.QMessageBox.Yes
#    no = QtWidgets.QMessageBox.No
#    window = self.q.parentWidget() or self.q
#    sel = QtWidgets.QMessageBox.question(window,
#        mytr_("Visual Novel Reader"),
#        self.q.tr("Reset to the default settings?"),
#        yes|no, no)
#    return sel == yes
#
#  ## Python plugin ##
#
#  @property
#  def pyPluginPane(self):
#    try: return self._pyPluginPane
#    except AttributeError:
#      self._pyPluginPane = QtWidgets.QGroupBox()
#      self._pyPluginPane.setTitle(self.q.tr("User-defined Python plugin"))
#
#      pathEdit = QtWidgets.QLineEdit(userplugin.USER_PY_PLUGIN_FILE)
#      pathEdit.setReadOnly(True)
#
#      browseButton = QtWidgets.QPushButton(tr_("Show"))
#      browseButton.clicked.connect(self._getPyPlugin)
#
#      enabled = userplugin.manager().userPyPlugin().isEnabled()
#      enableButton = QtWidgets.QCheckBox(tr_("Enable"))
#      enableButton.setChecked(enabled)
#
#      saveButton = QtWidgets.QPushButton(tr_("Save"))
#      saveButton.setToolTip("[%s+S]" % KEY_CTRL)
#      saveButton.clicked.connect(self._savePyPlugin)
#
#      resetButton = QtWidgets.QPushButton(tr_("Default"))
#      resetButton.clicked.connect(self._resetPyPlugin)
#
#      layout =  QtWidgets.QVBoxLayout()
#      pathLayout = QtWidgets.QHBoxLayout()
#      pathLayout.addWidget(pathEdit)
#      pathLayout.addWidget(browseButton)
#      layout.addLayout(pathLayout)
#      layout.addWidget(self.pyPluginEdit)
#
#      buttons = QtWidgets.QHBoxLayout()
#      buttons.addWidget(enableButton)
#      buttons.addWidget(saveButton)
#      buttons.addStretch()
#      buttons.addWidget(resetButton)
#      layout.addLayout(buttons)
#      self._pyPluginPane.setLayout(layout)
#
#      for w in self._pyPluginEdit, pathEdit, browseButton, saveButton, resetButton:
#        enableButton.toggled.connect(w.setEnabled)
#        if not enabled:
#          w.setEnabled(False)
#      enableButton.toggled.connect(userplugin.manager().userPyPlugin().setEnabled)
#
#      self._loadPyPlugin()
#      return self._pyPluginPane
#
#  @property
#  def pyPluginEdit(self):
#    try: return self._pyPluginEdit
#    except AttributeError:
#      self._pyPluginEdit = QtWidgets.QTextEdit()
#      self._pyPluginEdit.setAcceptRichText(False)
#      self._pyPluginEdit.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
#      skhls.SkPyHighlighter(self._pyPluginEdit)
#      return self._pyPluginEdit
#
#  def _loadPyPlugin(self):
#    path = userplugin.USER_PY_PLUGIN_FILE
#    if not os.path.exists(path):
#      path = userplugin.PY_PLUGIN_FILE
#    t = skio.readfile(path)
#    if not t:
#      growl.msg(self.q.tr("Cannot read file") + " %s" % path)
#    else:
#      self.pyPluginEdit.setPlainText(t)
#
#  def _savePyPlugin(self):
#    path = userplugin.USER_PY_PLUGIN_FILE
#    try:
#      with open(path, 'w') as f:
#        f.write(self.pyPluginEdit.toPlainText().encode("utf-8"))
#      plugin = userplugin.manager().userPyPlugin()
#      plugin.reload()
#      plugin.test()
#    except IOError:
#      growl.msg(self.q.tr("Cannot save file") + " %s" % path)
#
#  def _resetPyPlugin(self):
#    if self._confirmReset():
#      userplugin.manager().resetUserPyPlugin()
#      self._loadPyPlugin()
#
#  def _getPyPlugin(self):
#    osutil.open_location(
#        os.path.dirname(userplugin.USER_PY_PLUGIN_FILE))
#
#  ## Javascript plugin ##
#
#  @property
#  def jsPluginPane(self):
#    try: return self._jsPluginPane
#    except AttributeError:
#
#      self._jsPluginPane = QtWidgets.QGroupBox()
#      self._jsPluginPane.setTitle(self.q.tr("User-defined Javascript plugin"))
#
#      pathEdit = QtWidgets.QLineEdit(userplugin.USER_JS_PLUGIN_FILE)
#      pathEdit.setReadOnly(True)
#
#      browseButton = QtWidgets.QPushButton(tr_("Show"))
#      browseButton.clicked.connect(self._getJsPlugin)
#
#      enabled = userplugin.manager().userJsPlugin().isEnabled()
#      enableButton = QtWidgets.QCheckBox(tr_("Enable"))
#      enableButton.setChecked(enabled)
#
#      saveButton = QtWidgets.QPushButton(tr_("Save"))
#      saveButton.setToolTip("[%s+S]" % KEY_CTRL)
#      saveButton.clicked.connect(self._saveJsPlugin)
#
#      resetButton = QtWidgets.QPushButton(tr_("Default"))
#      resetButton.clicked.connect(self._resetJsPlugin)
#
#      layout =  QtWidgets.QVBoxLayout()
#      pathLayout = QtWidgets.QHBoxLayout()
#      pathLayout.addWidget(pathEdit)
#      pathLayout.addWidget(browseButton)
#      layout.addLayout(pathLayout)
#      layout.addWidget(self.jsPluginEdit)
#
#      buttons = QtWidgets.QHBoxLayout()
#      buttons.addWidget(enableButton)
#      buttons.addWidget(saveButton)
#      buttons.addStretch()
#      buttons.addWidget(resetButton)
#      layout.addLayout(buttons)
#      self._jsPluginPane.setLayout(layout)
#
#      for w in self._jsPluginEdit, pathEdit, browseButton, saveButton, resetButton:
#        enableButton.toggled.connect(w.setEnabled)
#        if not enabled:
#          w.setEnabled(False)
#      enableButton.toggled.connect(userplugin.manager().userJsPlugin().setEnabled)
#
#      self._loadJsPlugin()
#      return self._jsPluginPane
#
#  @property
#  def jsPluginEdit(self):
#    try: return self._jsPluginEdit
#    except AttributeError:
#      self._jsPluginEdit = QtWidgets.QTextEdit()
#      self._jsPluginEdit.setAcceptRichText(False)
#      self._jsPluginEdit.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
#      skhls.SkJsHighlighter(self._jsPluginEdit)
#      return self._jsPluginEdit
#
#  def _loadJsPlugin(self):
#    path = userplugin.USER_JS_PLUGIN_FILE
#    if not os.path.exists(path):
#      path = userplugin.JS_PLUGIN_FILE
#    t = skio.readfile(path)
#    if not t:
#      growl.msg(self.q.tr("Cannot read file") + " %s" % path)
#    else:
#      self.jsPluginEdit.setPlainText(t)
#
#  def _saveJsPlugin(self):
#    path = userplugin.USER_JS_PLUGIN_FILE
#    try:
#      with open(path, 'w') as f:
#        f.write(self.jsPluginEdit.toPlainText().encode("utf-8"))
#      plugin = userplugin.manager().userJsPlugin()
#      plugin.reload()
#      plugin.test()
#    except IOError:
#      growl.msg(self.q.tr("Cannot save file") + " %s" % path)
#
#  def _resetJsPlugin(self):
#    if self._confirmReset():
#      userplugin.manager().resetUserJsPlugin()
#      self._loadJsPlugin()
#
#  def _getJsPlugin(self):
#    osutil.open_location(
#        os.path.dirname(userplugin.USER_JS_PLUGIN_FILE))
#
#class PluginTab(QtWidgets.QSplitter):
#  def __init__(self, parent=None):
#    super(PluginTab, self).__init__(Qt.Horizontal, parent)
#    self.__d = _PluginTab(self)
#    self.setChildrenCollapsible(False)
#
#  def load(self): pass
#  def save(self): pass

