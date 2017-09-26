# coding: utf8
# _ttsman.py
# 4/7/2013 jichi

import os
from time import time
from functools import partial
from PySide.QtCore import QThread, Signal, Qt, QMutex
from sakurakit import skfileio, skwincom
from sakurakit.skdebug import dwarn
from sakurakit.sktr import tr_
from opencc.opencc import ja2zht, zht2zhs
import voiceroid.online as vrapi
import voicetext.online as vtapi
from mytr import my, mytr_
import growl, rc

## Voice engines ##

class VoiceEngine(object):
  key = ''          # str
  language = 'ja'   # str
  name = tr_('Unknown') # unicode
  #gender = 'f'  # str
  online = False # bool  whether it is an online engine

  def isValid(self): return True
  def speak(self, text, language=None, gender=''): pass
  def stop(self): pass

  def setGender(self, v): pass # dummy

# Offline engines

OfflineEngine = VoiceEngine

class SapiEngine(OfflineEngine):

  def __init__(self, key, speed=0, pitch=0, volume=100):
    #super(SapiEngine, self).__init__()
    self.key = key # str
    self.speed = speed  # int
    self.pitch = pitch  # int
    self.volume = volume  # int
    self._speaking = False
    self._valid = False
    #self.mutex = QMutex() # speak mutex

    import sapi.engine, sapi.registry
    kw = sapi.registry.query(key=self.key)
    self.engine = sapi.engine.SapiEngine(speed=speed, pitch=pitch, volume=volume, **kw) if kw else None
    if self.engine:
      self.language = self.engine.language or 'ja' # override
      self.name = self.engine.name or tr_('Unknown')
      #self.gender = self.engine.gender or 'f'

  def setSpeed(self, v):
    """
    @param  v  int  [-10,10]
    """
    if self.speed != v:
      self.speed = v
      e = self.engine
      if e:
        e.speed = v

  def setPitch(self, v):
    """
    @param  v  int  [-10,10]
    """
    if self.pitch != v:
      self.pitch = v
      e = self.engine
      if e:
        e.pitch = v

  def setVolume(self, v):
    """
    @param  v  int  [0,100]
    """
    if self.volume != v:
      self.volume = v
      e = self.engine
      if e:
        e.volume = v

  def isValid(self):
    """"@reimp"""
    if not self._valid:
      self._valid = bool(self.engine) and self.engine.isValid()
    return self._valid

  #def speak(self, text, language=None, gender=''):
  #  """@remip"""
  #  skthreads.runasync(partial(self._speakasync, text))

  #def _speakasync(self, text):
  #  e = self.engine
  #  if e:
  #    with SkCoInitializer(threading=True):
  #      if self._speaking:
  #        e.stop()
  #      else:
  #        self._speaking = True
  #      e.speak(text)
  #      #e.speak(text, async=False) # async=False, or it might crash?

  def speak(self, text, language=None, gender=''):
    """@remip"""
    e = self.engine
    if e:
      if self._speaking:
        e.stop()
      else:
        self._speaking = True
      if language and language.startswith('zh'):
        text = ja2zht(text)
        if language == 'zht':
          text = zht2zhs(text)
      e.speak(text)

  def stop(self):
    """@remip"""
    if self._speaking:
      self._speaking = False
      e = self.engine
      if e:
        e.stop()

# Vocalroids

class VocalroidEngine(OfflineEngine):

  def __init__(self, voiceroid, path=''):
    #super(VocalroidEngine, self).__init__()
    self.path = path # unicode
    self._engine = None # VocalroidController
    self._speaking = False
    self.voiceroid = voiceroid # Voiceroid
    self.key = voiceroid.key + 'offline'
    self.name = voiceroid.name

  def getPath(self):
    return self.path or self.voiceroid.getPath()

  def setPath(self, v):
    if v != self.path:
      self.path = v
      if self._engine:
        self._engine.setPath(path)

  @property
  def engine(self):
    if not self._engine:
      path = self.path or self.voiceroid.getPath()
      if path and os.path.exists(path):
        import voiceroid.bottle
        self._engine = voiceroid.bottle.VoiceroidController(self.voiceroid, path=path)
    return self._engine

  def isValid(self):
    """"@reimp"""
    return bool(self.engine)

  def run(self):
    e = self.engine
    if e:
      growl.msg(' '.join((
        my.tr("Activate Voiceroid+"),
        self.name,
      )))
      e.run()
    else:
      growl.warn(' '.join((
        my.tr("Cannot find Voiceroid+"),
        self.name,
      )))

  def speak(self, text, language=None, gender=''):
    """@reimp@"""
    e = self.engine
    if e:
      if self._speaking:
        e.stop()
      else:
        self._speaking = True
      e.speak(text)

  def stop(self):
    """@reimp@"""
    if self._speaking:
      self._speaking = False
      e = self.engine
      #if e:
      if e:
        e.stop()

class YukariEngine(VocalroidEngine):
  def __init__(self, **kwargs):
    import voiceroid.apps
    v = voiceroid.apps.Yukari()
    super(YukariEngine, self).__init__(v, **kwargs)

#class ZunkoEngine(VocalroidEngine):
#  def __init__(self, **kwargs):
#    import voiceroid.apps
#    v = voiceroid.apps.Zunko()
#    super(ZunkoEngine, self).__init__(v, **kwargs)

class ZunkoEngine(VoiceEngine):
  key = 'zunkooffline' # str
  name = u"東北ずん子" # unicode

  def __init__(self, volume=100, mutex=None):
    self.engine = self.createengine(volume/100.0)
    self.mutex = mutex or QMutex() # speak mutex

  @classmethod
  def createengine(cls, volume):
    #import settings
    #from sakurakit import skpaths
    #skpaths.prepend_path(settings.global_().zunkoLocation())

    from voiceroid.zunko import ZunkoTalk
    #AUDIO_BUFFER_SIZE = 0x1000000 # 1MB, default is 0x158880 == 159k
    #AUDIO_BUFFER_SIZE = 0x500000 # 0.5MB
    AUDIO_BUFFER_SIZE = 0x300000 # 0.3MB
    ret = ZunkoTalk(volume=volume, audioBufferSize=AUDIO_BUFFER_SIZE)
    ok = ret.load()
    if ok:
      growl.msg(my.tr("Load {0}").format(cls.name))
    else:
      growl.error(my.tr("Failed to load {0}. Please check Preferences/Location").format(cls.name))
    return ret

  def setVolume(self, v):
    if self.mutex.tryLock():
      self.engine.setVolume(v/100.0)
      self.mutex.unlock()
    else:
      dwarn("ignored due to thread contention")

  def isValid(self):
    """"@reimp"""
    return self.engine.isValid()

  def speak(self, text, language=None, gender=''):
    """"@reimp"""
    if self.mutex.tryLock():
      self.engine.speak(text)
      self.mutex.unlock()
    else:
      dwarn("ignored due to thread contention")

  def stop(self):
    """"@reimp"""
    if self.mutex.tryLock():
      self.engine.stop()
      self.mutex.unlock()
    else:
      dwarn("ignored due to thread contention")

  def setPath(self, path):
    if path and os.path.exists(path):
      from sakurakit import skpaths
      #skpaths.prepend_path(path)
      skpaths.append_path(path)
      if not self.engine.isValid():
        self.engine.load()

# Online engines

class _OnlineThread:
  def __init__(self):
    self.playing = False
    self.downloadCount = 0 # int
    self.time = 0 # float

  def run(self, q):
    from pywmp import WindowsMediaPlayer
    self.wmp = WindowsMediaPlayer()

    from qtrequests import qtrequests
    from PySide.QtNetwork import QNetworkAccessManager
    nam = QNetworkAccessManager()
    self.session = qtrequests.Session(nam, abortSignal=q.abortSignal)

    q.abortSignalRequested.connect(q.abortSignal, Qt.QueuedConnection)

    q.playRequested.connect(self.play, Qt.QueuedConnection)
    q.stopRequested.connect(self.stop, Qt.QueuedConnection)

  def play(self, engine, text, language, gender, time):
    if time < self.time: # outdated
      return
    if not text:
      self.stop(time)
      return
    url = engine.createUrl(text, language, gender)
    if not url:
      self.stop(time)
      return
    if time < self.time: # outdated
      return

    path = rc.tts_path(url)

    if os.path.exists(path):
      self.playing = engine.playFile(path, self.wmp)
    else:
      self._retainDownloads()
      url = engine.resolveUrl(url, self.session)
      self._releaseDownloads()

      if time < self.time or not url: # outdated
        return

      self._retainDownloads()
      r = self.session.get(url)
      self._releaseDownloads()

      if r.content and len(r.content) > 500: # Minimum TTS file size is around 1k for MP3
        if time < self.time: # outdated
          return
        if skfileio.writefile(path, r.content, mode='wb'):
          if time < self.time: # outdated
            return
          self.playing = engine.playFile(path, self.wmp)

  def stop(self, time): # float ->
    if time < self.time: # outdated
      return
    if self.playing:
      self.wmp.stop()
      self.playing = False

  def _retainDownloads(self):
    self.downloadCount += 1
  def _releaseDownloads(self):
    c = self.downloadCount - 1
    if c >= 0:
      self.downloadCount = c

class OnlineThread(QThread):
  playRequested = Signal(object, unicode, str, str, float) # OnlineEngine, text, language, gender, time
  stopRequested = Signal(float) # time
  abortSignal = Signal()
  abortSignalRequested = Signal()

  def __init__(self, parent=None):
    super(OnlineThread, self).__init__(parent)
    self.__d = _OnlineThread()

  def run(self):
    """@reimp"""
    skwincom.coinit(threading=True) # critical to use WMP
    self.__d.run(self)
    self.exec_()

  def destroy(self):
    self.abortSignalRequested.emit()
    self.quit()
    #skwincom.couninit() # never invoked

  # Actions

  def requestPlay(self, engine, text, language, gender): # OnlineTask ->
    now = time()
    d = self.__d
    d.time = now
    if d.downloadCount > 0:
      self.abortSignalRequested.emit()

    self.playRequested.emit(engine, text, language, gender, now)

  def requestStop(self):
    d = self.__d
    now = time()
    d.time = now
    if d.downloadCount > 0:
      self.abortSignalRequested.emit()
    if d.playing:
      self.stopRequested.emit(now)

class OnlineEngine(VoiceEngine):
  language = '*' # override
  online = True # override

  ENGINES = 'baidu', 'google', 'bing', 'naver'

  @staticmethod
  def create(key, **kwargs): # str -> OnlineEngine
    if key == BaiduEngine.key:
      return BaiduEngine(**kwargs)
    if key == BingEngine.key:
      return BingEngine(**kwargs)
    if key == GoogleEngine.key:
      return GoogleEngine(**kwargs)
    if key == NaverEngine.key:
      return NaverEngine(**kwargs)
    if key in VoiceroidOnlineEngine.VOICES:
      return VoiceroidOnlineEngine(key, **kwargs)
    if key in VoiceTextOnlineEngine.VOICES:
      return VoiceTextOnlineEngine(key, **kwargs)

  _thread = None
  @classmethod
  def thread(cls): # -> OnlineThread not None
    if not cls._thread:
      t = cls._thread = OnlineThread()
      t.start()

      from PySide.QtCore import QCoreApplication
      qApp = QCoreApplication.instance()
      qApp.aboutToQuit.connect(t.destroy)

      growl.msg(my.tr("Load {0} for TTS").format("Windows Media Player"))
    return cls._thread

  def __init__(self, volume=100, speed=0, pitch=0, gender=''):
    #super(OnlineEngine, self).__init__()
    self.speed = speed # int
    self.pitch = pitch # int
    self.volume = volume # int
    self.gender = gender # str

  def setSpeed(self, v): self.speed = v
  def setPitch(self, v): self.pitch = v
  def setVolume(self, v): self.volume = v
  def setGender(self, v): self.gender = v

  _valid = None
  def isValid(self):
    """@reimp"""
    if not OnlineEngine._valid:
      import libman
      OnlineEngine._valid = libman.wmp().exists()
    return OnlineEngine._valid

  def speak(self, text, language=None, gender=''):
    """@reimp@"""
    if not self.isValid():
      growl.warn(my.tr("Missing Windows Media Player needed by text-to-speech"))
    else:
      language = language[:2] if language else 'ja'
      OnlineEngine.thread().requestPlay(self, text, language, gender)

  def stop(self):
    """@reimp@"""
    if self._thread:
      self._thread.requestStop()

  def createUrl(self, text, language, gender):
    """Create initial query URL
    @param  text
    @param  language
    @return  unicode or None
    """
    pass

  def resolveUrl(self, url, session):
    """Resolve real temporary mp3 url
    @param  url  unicode
    @param  session  requests or requests.Session or qtrequests.Session
    @return  unicode or None
    """
    return url

  def playFile(self, path, wmp):
    """Play the MP3 file locally
    @param  path
    @param  wmp  pywmp.WindowsMediaPlayer
    @return  bool
    """
    speed = self.speed
    speed = pow(1.1, speed) if speed else 1
    wmp.setSpeed(speed)
    wmp.setVolume(self.volume)
    return wmp.play(path)

class GoogleEngine(OnlineEngine):
  key = 'google' # override
  name = 'Google.com' # override

  def __init__(self, *args, **kwargs):
    super(GoogleEngine, self).__init__(*args, **kwargs)

  def createUrl(self, text, language, gender):
    """@reimp@"""
    from google import googletts
    return googletts.url(text, language) # encoding is not needed

class BaiduEngine(OnlineEngine):
  key = 'baidu' # override
  name = mytr_("Baidu") + ".com" # override

  def __init__(self, *args, **kwargs):
    super(BaiduEngine, self).__init__(*args, **kwargs)

  def createUrl(self, text, language, gender):
    """@reimp@"""
    from baidu import baidutts
    return baidutts.url(text, language)

class BingEngine(OnlineEngine):
  key = 'bing' # override
  name = 'Bing.com' # override

  def __init__(self, *args, **kwargs):
    super(BingEngine, self).__init__(*args, **kwargs)
    import bingman
    self.createUrl = bingman.manager().tts # override

class NaverEngine(OnlineEngine):
  key = 'naver' # override
  name = "Naver.com" # override

  def __init__(self, *args, **kwargs):
    super(NaverEngine, self).__init__(*args, **kwargs)

  def createUrl(self, text, language, gender):
    """@reimp@"""
    from naver import navertts
    pitch = 100 + self.pitch * 10 # 100 by default
    return navertts.url(text, language, pitch=pitch, gender=gender or self.gender)

class VoiceroidOnlineEngine(OnlineEngine):
  language = 'ja' # override
  #key = 'voiceroid' # override
  #name = u'VOICEROID+' # override

  VOICES = vrapi.VOICES

  def __init__(self, key, **kwargs):
    voice = self.VOICES[key]
    self.voice = voice
    self.key = voice.key # override
    self.name = voice.name # override
    super(VoiceroidOnlineEngine, self).__init__(**kwargs)

  def createUrl(self, text, language, gender):
    """@override"""
    pitch = self.pitch
    pitch = pow(1.1, pitch) if pitch else 1 # 1.0 by default, 0.5 ~ 2.0
    return vrapi.createdata(self.voice.id, text, pitch=pitch)

  def resolveUrl(self, url, session):
    """@override"""
    return vrapi.resolveurl(url, session)

class VoiceTextOnlineEngine(OnlineEngine):
  #key = 'voicetext' # override
  #name = u'VoiceText' # override

  VOICES = vtapi.VOICES

  def __init__(self, key, **kwargs):
    voice = self.VOICES[key]
    self.voice = voice
    self.key = voice.key # override
    self.name = voice.name # override
    self.language = voice.language # override
    super(VoiceTextOnlineEngine, self).__init__(**kwargs)

  def createUrl(self, text, language, gender):
    """@override"""
    pitch = 100 + self.pitch * 10 # 100 by default
    return vtapi.createdata(self.voice.id, self.voice.dic, text, pitch=pitch)

  def resolveUrl(self, url, session):
    """@override"""
    return vtapi.resolveurl(url, session)

ONLINE_ENGINES = list(OnlineEngine.ENGINES)
ONLINE_ENGINES.extend(VoiceroidOnlineEngine.VOICES.iterkeys())
ONLINE_ENGINES.extend(VoiceTextOnlineEngine.VOICES.iterkeys())

# EOF
