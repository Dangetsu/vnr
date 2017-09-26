# coding: utf8
# srman.py
# 11/1/2014 jichi

from functools import partial
from time import time
from PySide.QtCore import Qt, QObject, QThread, Signal, Slot, Property
from sakurakit import skthreads
from sakurakit.skclass import memoized, Q_Q
from sakurakit.skdebug import dprint, dwarn
from google import googledef
from mytr import my
import growl

@memoized
def manager(): return SpeechRecognitionManager()

MAX_AUDIO_SIZE = 2000 * 1000 # max is 2MB, a sentence is normally 100k

#QmlObject
class SpeechRecognitionBean(QObject):
  def __init__(self, parent=None):
    super(SpeechRecognitionBean, self).__init__(parent)

    m = manager()
    m.activeChanged.connect(self.activeChanged)
    m.singleShotChanged.connect(self.singleShotChanged)

  @Slot()
  def stop(self): manager().stop()

  activeChanged = Signal(bool)
  active = Property(bool,
      lambda _: manager().isActive(),
      lambda _, t: manager().setActive(t),
      notify=activeChanged)

  singleShotChanged = Signal(bool)
  singleShot = Property(bool,
      lambda _: manager().isSingleShot(),
      lambda _, t: manager().setSingleShot(t),
      notify=singleShotChanged)

class SpeechRecognitionManager(QObject):

  def __init__(self, parent=None):
    super(SpeechRecognitionManager, self).__init__(parent)
    self.__d = _SpeechRecognitionManager(self)

  activeChanged = Signal(bool)
  singleShotChanged = Signal(bool)
  textRecognized = Signal(unicode)
  recognitionFinished = Signal()

  def isActive(self): return self.__d.active
  def setActive(self, t):
    dprint(t)
    if t:
      self.start()
    else:
      self.abort()

  def start(self):
    d = self.__d
    if not d.active:
      d.active = True
      self.activeChanged.emit(True)
      d.thread().requestListen()
      dprint("pass")

  def stop(self):
    if self.__d._thread:
      self.__d._thread.stop()
    dprint("pass")

  def abort(self):
    d = self.__d
    if d.active:
      d.active = False
      if d._thread:
        d._thread.abort()
      self.activeChanged.emit(False)
      dprint("pass")

  def isOnline(self): return self.__d.online
  def setOnline(self, t):
    if t != self.__d.online:
      self.__d.setOnline(t)

  def deviceIndex(self): return self.__d.deviceIndex
  def setDeviceIndex(self, v):
    if v != self.__d.deviceIndex:
      self.__d.setDeviceIndex(v)
      dprint(v)

  def language(self): return self.__d.language
  def setLanguage(self, v):
    if v != self.__d.language:
      self.__d.setLanguage(v)
      dprint(v)

  def detectsQuiet(self): return self.__d.detectsQuiet
  def setDetectsQuiet(self, t):
    if t != self.__d.detectsQuiet:
      self.__d.setDetectsQuiet(t)

  def isSingleShot(self): return self.__d.singleShot
  def setSingleShot(self, t):
    if t != self.__d.singleShot:
      self.__d.setSingleShot(t)
      self.singleShotChanged.emit(t)
      dprint(t)

@Q_Q
class _SpeechRecognitionManager(object):
  def __init__(self):
    self.active = False
    self.detectsQuiet = True # bool
    self.singleShot = True # bool
    self.online = True # bool
    self.language = 'ja' # str
    self.deviceIndex = 0 # int
    self._thread = None # SpeechRecognitionThread

  def thread(self): # -> QThread
    if not self._thread:
      t = self._thread = SpeechRecognitionThread()
      t.setOnline(self.online)
      t.setLanguage(self.language)
      t.setDeviceIndex(self.deviceIndex)
      t.setDetectsQuiet(self.detectsQuiet)
      t.setSingleShot(self.singleShot)

      q = self.q
      t.textRecognized.connect(q.textRecognized, Qt.QueuedConnection)
      t.recognitionFinished.connect(self.onRecognitionFinished, Qt.QueuedConnection)

      from PySide.QtCore import QCoreApplication
      qApp = QCoreApplication.instance()
      qApp.aboutToQuit.connect(t.destroy)

      t.start()
      dprint("create thread")
    return self._thread

  def onRecognitionFinished(self):
    q = self.q
    if self.singleShot and self.active:
      self.active = False
      q.activeChanged.emit(False)
    q.recognitionFinished.emit()

  def setOnline(self, t):
    self.online = t
    if self._thread:
      self._thread.setOnline(t)

  def setLanguage(self, v):
    self.language = v
    if self._thread:
      self._thread.setLanguage(v)

  def setDetectsQuiet(self, t):
    self.detectsQuiet = t
    if self._thread:
      self._thread.setDetectsQuiet(t)

  def setSingleShot(self, t):
    self.singleShot = t
    if self._thread:
      self._thread.setSingleShot(t)

  def setDeviceIndex(self, v):
    self.deviceIndex = v
    if self._thread:
      self._thread.setDeviceIndex(v)

class SpeechRecognitionThread(QThread):
  listenRequested = Signal(float) # time
  textRecognized = Signal(unicode) # text
  recognitionFinished = Signal()

  def __init__(self, parent=None):
    super(SpeechRecognitionThread, self).__init__(parent)
    self.__d = _SpeechRecognitionThread(self)

  def run(self):
    """@reimp"""
    d = self.__d
    self.listenRequested.connect(d.listen, Qt.QueuedConnection)
    self.exec_()

  def requestListen(self):
    now = time()
    d = self.__d
    d.time = now
    d.aborted = False
    self.listenRequested.emit(now)

  def stop(self):
    d = self.__d
    #d.time = time()
    d.recognizer.stopped = True

  def abort(self):
    d = self.__d
    d.time = time()
    d.aborted = d.recognizer.stopped = True

  def destroy(self):
    self.abort()
    self.quit()

  def setOnline(self, t):
    self.__d.enabled = t

  def setDeviceIndex(self, v):
    self.__d.deviceIndex = v

  def setSingleShot(self, t):
    self.__d.singleShot = t

  def setLanguage(self, v):
    d = self.__d
    if d.language != v:
      d.language = v
      if d._recognizer:
        d._recognizer.language = googledef.lang2locale(v)

  def setDetectsQuiet(self, t):
    d = self.__d
    if d.detectsQuiet != t:
      d.detectsQuiet = t
      if d._recognizer:
        d._recognizer.detects_quiet = t

@Q_Q
class _SpeechRecognitionThread(object):
  def __init__(self):
    self.time = 0 # float
    self.enabled = True
    self.singleShot = True
    self.aborted = False
    self.deviceIndex = 0 # int or None

    self._recognizer = None # googlesr.Recognizer
    self.language = 'en'
    self.detectsQuiet = True

  @property
  def recognizer(self):
    if not self._recognizer:
      dprint("create speech recognizer")
      from google import googlesr
      r = self._recognizer = googlesr.Recognizer()
      r.language = googledef.lang2locale(self.language)
      r.detects_quiet = self.detectsQuiet
    return self._recognizer

  def listen(self, time):
    if time < self.time: # aborted
      return
    q = self.q
    r = self.recognizer
    while self.enabled:
      try:
        from google import googlesr
        with googlesr.Microphone(device_index=self.deviceIndex) as source:
          dprint("listen start")
          r.stopped = False
          audio = r.listen(source)
          dprint("listen stop")
      except Exception, e:
        dwarn("audio device error", e)
        q.recognitionFinished.emit()
        return

      if time < self.time or self.aborted or not self.enabled: # aborted
        return

      if audio and len(audio.data) < MAX_AUDIO_SIZE:
        skthreads.runasync(partial(self.recognize, audio))
      else:
        q.recognitionFinished.emit()

      if time < self.time or self.aborted or self.singleShot:
        return

  def recognize(self, audio):
    """
    @param  audio  googlesr.AudioData
    """
    if time < self.time or self.aborted or not self.enabled: # aborted
      return
    q = self.q
    dprint("recognize start")
    text = None
    try:
      text = self.recognizer.recognize(audio)

      if time < self.time or self.aborted or not self.enabled: # aborted
        return
      if text:
        q.textRecognized.emit(text)
    except Exception, e:
      dwarn("network error", e)
    dprint("recognize stop")

    q.recognitionFinished.emit()

    if time < self.time or self.aborted or not self.enabled: # aborted
      return

    if not text and self.singleShot:
      dwarn("nothing recognized")
      growl.msg(my.tr("Failed to recognize speech"), async=True)

# EOF
