# coding: utf8
# srtest.py
# 11/1/2014 jichi
# Speech recognition tester.

__all__ = 'SpeechRecognitionTester',

if __name__ == '__main__':
  import sys
  sys.path.append('..')
  import debug
  debug.initenv()

from PySide.QtCore import Qt
from Qt5 import QtWidgets
from sakurakit import skqss
from sakurakit.skclass import memoizedproperty
from sakurakit.skdebug import dprint
from sakurakit.sktr import tr_
from mytr import my, mytr_
import audioinfo, config, i18n, rc

class SpeechRecognitionTester(QtWidgets.QDialog):

  def __init__(self, parent=None):
    WINDOW_FLAGS = Qt.Dialog|Qt.WindowMinMaxButtonsHint
    super(SpeechRecognitionTester, self).__init__(parent)
    skqss.class_(self, 'texture')
    self.setWindowFlags(WINDOW_FLAGS)
    self.setWindowTitle(mytr_("Test Speech Recognition"))
    self.setWindowIcon(rc.icon('window-srtest'))
    self.__d = _SpeechRecognitionTester(self)
    #self.setContentsMargins(9, 9, 9, 9)
    self.resize(400, 200)
    dprint("pass")

  def setVisible(self, t):
    """@reimp"""
    if t != self.isVisible() and not t:
       self.__d.abort()
    super(SpeechRecognitionTester, self).setVisible(t)

class _SpeechRecognitionTester:
  def __init__(self, q):
    self.recording = False # bool
    self.createUi(q)
    self.manager.setParent(q)

  def createUi(self, q):
    layout = QtWidgets.QVBoxLayout()

    row = QtWidgets.QHBoxLayout()
    row.addWidget(self.startButton)
    row.addWidget(self.stopButton)
    row.addWidget(self.languageEdit)
    row.addStretch()
    row.addWidget(self.ttsButton)
    layout.addLayout(row)

    row = QtWidgets.QHBoxLayout()
    row.addWidget(self.autoStopButton)
    row.addStretch()
    row.addWidget(self.deviceEdit)
    layout.addLayout(row)

    layout.addWidget(self.textEdit)

    q.setLayout(layout)

  @memoizedproperty
  def manager(self):
    import srman
    ret = srman.SpeechRecognitionManager()
    ret.setDetectsQuiet(True)
    ret.setSingleShot(True)
    ret.textRecognized.connect(self.textEdit.setPlainText)
    ret.recognitionFinished.connect(self.stop)

    ret.setDeviceIndex(self.deviceEdit.currentIndex())
    self.deviceEdit.currentIndexChanged.connect(ret.setDeviceIndex)

    import netman
    nm = netman.manager()
    ret.setOnline(nm.isOnline())
    nm.onlineChanged.connect(ret.setOnline)
    return ret

  @staticmethod
  def createButton(text="", tip="", styleClass="btn btn-default", click=None):
    """
    @param* text  unicode
    @param* tip  unicode
    @param* styleClass  str
    @param* click  function
    """
    return ret

  @memoizedproperty
  def textEdit(self):
    ret = QtWidgets.QPlainTextEdit()
    ret.setToolTip(my.tr("Recognized text"))
    return ret

  @memoizedproperty
  def autoStopButton(self):
    ret = QtWidgets.QCheckBox(my.tr("Automatically stop when silent"))
    ret.setChecked(self.manager.detectsQuiet())
    ret.toggled.connect(self.manager.setDetectsQuiet)
    return ret

  @memoizedproperty
  def languageEdit(self):
    ret = QtWidgets.QComboBox()
    ret.setEditable(False)
    ret.addItems(map(i18n.language_name2, config.LANGUAGES))
    ret.setMaxVisibleItems(ret.count())

    import settings
    try: langIndex = config.LANGUAGES.index(settings.global_().speechRecognitionLanguage())
    except ValueError: langIndex = 0 # 'ja'
    ret.setCurrentIndex(langIndex)

    ret.currentIndexChanged.connect(self._saveLanguage)
    return ret

  @memoizedproperty
  def deviceEdit(self):
    ret = QtWidgets.QComboBox()
    ret.setToolTip(my.tr("Audio device to record"))
    ret.setEditable(False)
    ret.addItems([it['name'] for it in audioinfo.inputdevices()])
    #ret.setMaxVisibleItems(ret.count())

    import settings
    ret.setCurrentIndex(settings.global_().audioDeviceIndex())
    return ret

  def _saveLanguage(self):
    self.manager.setLanguage(self._getLanguage())

  @memoizedproperty
  def startButton(self):
    ret = QtWidgets.QPushButton(tr_("Start"))
    skqss.class_(ret, 'btn btn-primary')
    ret.setToolTip(my.tr("Start recording audio"))
    ret.clicked.connect(self.start)
    return ret

  @memoizedproperty
  def stopButton(self):
    ret = QtWidgets.QPushButton(tr_("Stop"))
    skqss.class_(ret, 'btn btn-danger')
    ret.setToolTip(my.tr("Stop recording audio"))
    ret.clicked.connect(self.stop)
    ret.setEnabled(False)
    return ret

  @memoizedproperty
  def ttsButton(self):
    ret = QtWidgets.QPushButton(mytr_("TTS"))
    skqss.class_(ret, 'btn btn-default')
    ret.setToolTip(my.tr("Read the recognized text"))
    ret.clicked.connect(self._tts)
    return ret

  def start(self):
    if not self.recording:
      self.recording = True
      self.startButton.setEnabled(False)
      self.stopButton.setEnabled(True)

      self.manager.start()
      dprint("pass")

  def stop(self):
    if self.recording:
      self.recording = False
      self.startButton.setEnabled(True)
      self.stopButton.setEnabled(False)

      self.manager.stop()
      dprint("pass")

  def abort(self):
    if self.recording:
      self.recording = False
      self.startButton.setEnabled(True)
      self.stopButton.setEnabled(False)

      self.manager.abort()
      dprint("pass")

  def _tts(self):
    text = self._getText()
    if text:
      lang = self._getLanguage()
      import ttsman
      ttsman.speak(text, language=lang, termEnabled=False)

  def _getText(self): return self.textEdit.toPlainText()
  def _getLanguage(self): return config.LANGUAGES[self.languageEdit.currentIndex()]

if __name__ == '__main__':
  a = debug.app()
  w = SpeechRecognitionTester()
  w.show()
  a.exec_()

# EOF
