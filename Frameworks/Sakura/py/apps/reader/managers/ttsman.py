# coding: utf8
# ttsman.py
# 4/7/2013 jichi

__all__ = 'TtsQmlBean', 'TtsCoffeeBean'

#from sakurakit.skprof import SkProfiler

from functools import partial
from PySide.QtCore import QObject, Slot, QTimer, QMutex
#from sakurakit import skevents, skthreads
from sakurakit.skdebug import dwarn, dprint
from sakurakit.skclass import memoized
#from sakurakit.skqml import QmlObject
from unitraits import jpchars, unilang
from mytr import my
import features, growl, settings, termman, textutil
import _ttsman

#@Q_Q
class _TtsManager(object):

  def __init__(self, q):
    self.defaultEngineKey = '' # str
    self._online = True     # bool
    self._speakTask = None   # partial function object

    self._zunkoEngine = None  # _ttsman.ZunkoEngine
    self._zunkoMutex = QMutex()

    self._yukariEngine = None # _ttsman.YukariEngine
    self._sapiEngines = {}    # {str key:_ttsman.SapiEngine}
    self._onlineEngines = {}  # {str key:_ttsman.OnlineEngine}
    self._voiceroidEngines = {}  # {str key:_ttsman.VoiceroidEngine}
    self._voicetextEngines = {}  # {str key:_ttsman.VoiceTextEngine}

    #self.defaultEngineKey = 'wrong engine'
    #self.defaultEngineKey = 'VW Misaki'
    #self.defaultEngineKey = 'VW Show'
    #self.defaultEngineKey = 'zunko'
    #self.defaultEngineKey = 'yukari'
    #self.defaultEngineKey = 'google'

    t = self._speakTimer = QTimer(q)
    t.setSingleShot(True)
    t.timeout.connect(self._doSpeakTask)

  @staticmethod
  def _repairText(text, key=''):
    """
    @param  text  unicode
    @param* key  str  engine key
    @return  unicode
    """
    ret = text.replace(u'…', '.') # てんてんてん
    #if key == 'zunko.offline':
    #  ret = textutil.repair_zunko_text(ret)
    return ret

  def iterActiveEngines(self):
    """
    @yield  engine
    """
    if self._online:
      for it in self._onlineEngines.itervalues():
        if it.isValid():
          yield it
      for it in self._voiceroidEngines.itervalues():
        if it.isValid():
          yield it
      for it in self._voicetextEngines.itervalues():
        if it.isValid():
          yield it
    for it in self._zunkoEngine, self._yukariEngine:
      if it and it.isValid():
        yield it
    for it in self._sapiEngines.itervalues():
      if it.isValid():
        yield it

  def stop(self):
    for it in self.iterActiveEngines():
      #if it.type != 'sapi': # do not disable sapi TTS to make it faster
      it.stop()

  def speakLater(self, text, interval, **kwargs): # unicode, long ->
    self._speakTask = partial(self.speak, text, **kwargs)
    self._speakTimer.start(interval)

  def speak(self, text, engine='', termEnabled=False, language='', gender='', verbose=True):
    """
    @param  text  unicode
    @param* engine  str
    @param* termEnabled  bool  whether apply game-specific terms
    @param* language  str
    @param* gender  str
    @param* verbose  bool  whether warn on error
    """
    #if not features.TEXT_TO_SPEECH:
    if not text or jpchars.allpunct(text):
      #self.stop() # stop is not needed for games
      return

    eng = self.getEngine(engine)
    if not eng and self.defaultEngineKey and self.defaultEngineKey != engine:
      eng = self.getEngine(self.defaultEngineKey)

    if not eng:
      if verbose:
        growl.warn(my.tr("TTS is not available in Preferences"))
      dprint("missing engine: %s" % (engine or self.defaultEngineKey))
      return
    if not eng.isValid():
      #if verbose:
      # Always warn
      growl.warn('<br/>'.join((
        my.tr("TTS is not available"),
        eng.name,
      )))
      dprint("invalid engine: %s" % eng.key)
      return

    if eng.online and not self._online:
      dprint("ignore when offline: %s" % eng.key)
      return

    if language == '?': #
      language = unilang.guess_language(text) or 'ja'

    if language and eng.language and eng.language != '*' and language[:2] != eng.language[:2]:
      #if verbose:
      #  growl.notify("<br/>".join((
      #      my.tr("TTS languages mismatch"),
      #      "%s: %s != %s" % (eng.key, language, eng.language))))
      dprint("language mismatch: %s != %s" % (language, eng.language))
      eng = self.getAvailableEngine(language)
      if not eng:
        return

    if termEnabled: #and (not language or language == 'ja'):
      text = termman.manager().applyTtsTerms(text, language)
    # Even if text is empty, trigger stop tts
    #if not text:
    #  return
    text = self._repairText(text, eng.key) # always apply no matter terms are enabled or not

    #if eng.type == 'sapi':
    #  eng.speak(text, async=True)
    #else:
    #with SkProfiler():
    if text:
      eng.speak(text, language, gender) # 0.007 ~ 0.009 seconds for SAPI
    else:
      eng.stop()

    #skevents.runlater(partial(eng.speak, text))

  def getAvailableEngine(self, language):
    """
    @param  language  str
    @return  _ttsman.VoiceEngine or None
    """
    if not self.online:
      dprint("ignore when offline")
      return None
    key = 'naver' if language == 'ja' else 'baidu' if language.startswith('zh') else 'google'
    return self.getEngine(key)

  @property
  def online(self): return self._online
  @online.setter
  def online(self, v):
    if v != self._online:
      self._online = v

  # Voiceroid

  @property
  def yukariEngine(self):
    if not self._yukariEngine:
      ss = settings.global_()
      eng = self._yukariEngine = _ttsman.YukariEngine(path=ss.yukariLocation())
      ss.yukariLocationChanged.connect(eng.setPath)
      growl.msg(' '.join((
        my.tr("Load TTS"),
        eng.name,
      )))
    return self._yukariEngine

  @property
  def zunkoEngine(self):
    if not self._zunkoEngine:
      if self._zunkoMutex.tryLock():
        eng = self._zunkoEngine = _ttsman.ZunkoEngine(
            mutex = self._zunkoMutex,
            volume=self.getVolume(_ttsman.ZunkoEngine.key))
        settings.global_().zunkoLocationChanged.connect(eng.setPath)
        #growl.msg(' '.join((
        #  my.tr("Load TTS"),
        #  eng.name,
        #)))
        self._zunkoMutex.unlock()
      else:
        dwarn("ignored due to thread contention")
    return self._zunkoEngine

  # Online

  def getOnlineEngine(self, key):
    ret = self._onlineEngines.get(key)
    if not ret and key in _ttsman.ONLINE_ENGINES:
      ret = _ttsman.OnlineEngine.create(key)
      if ret:
        ret.speed = self.getSpeed(key)
        ret.pitch = self.getPitch(key)
        ret.volume = self.getVolume(key)
        ret.gender = self.getGender(key)
      if ret and ret.isValid():
        self._onlineEngines[key] = ret
        growl.msg(' '.join((
          my.tr("Load TTS"),
          ret.name,
        )))
      else:
        ret = None
        growl.warn(' '.join((
          my.tr("Failed to load TTS"),
          key,
        )))
    return ret

  # SAPI

  def getSapiEngine(self, key):
    ret = self._sapiEngines.get(key)
    if not ret:
      ret = _ttsman.SapiEngine(key=key,
        speed=self.getSpeed(key),
        pitch=self.getPitch(key),
        volume=self.getVolume(key),
        #gender=self.getGender(key),
      )
      if ret.isValid():
        self._sapiEngines[key] = ret
        growl.msg(' '.join((
          my.tr("Load TTS"),
          ret.name,
        )))
      else:
        ret = None
        growl.warn(' '.join((
          my.tr("Failed to load TTS"),
          key,
        )))
    return ret

  def getPitch(self, key):
    """
    @param  key  str
    @return  int
    """
    try: return int(settings.global_().ttsPitches().get(key) or 0)
    except (ValueError, TypeError): return 0

  def setPitch(self, key, v):
    """
    @param  key  str
    @param  v  int
    """
    ss = settings.global_()
    m = ss.ttsPitches()
    if v != m.get(key):
      m[key] = v
      ss.setTtsPitches(m)
      eng = self.getCreatedEngine(key)
      if eng:
        eng.setPitch(v)

  def getVolume(self, key):
    """
    @param  key  str
    @return  int
    """
    try: return int(settings.global_().ttsVolumes().get(key) or 100)
    except (ValueError, TypeError): return 100

  def setVolume(self, key, v):
    """
    @param  key  str
    @param  v  int
    """
    ss = settings.global_()
    m = ss.ttsVolumes()
    if v != m.get(key):
      m[key] = v
      ss.setTtsVolumes(m)
      eng = self.getCreatedEngine(key)
      if eng:
        eng.setVolume(v)

  def getSpeed(self, key):
    """
    @param  key  str
    @return  int
    """
    try: return int(settings.global_().ttsSpeeds().get(key) or 0)
    except (ValueError, TypeError): return 0

  def setSpeed(self, key, v):
    """
    @param  key  str
    @param  v  int
    """
    ss = settings.global_()
    m = ss.ttsSpeeds()
    if v != m.get(key):
      m[key] = v
      ss.setTtsSpeeds(m)
      eng = self.getCreatedEngine(key)
      if eng:
        eng.setSpeed(v)

  def getGender(self, key):
    """
    @param  key  str
    @return  str
    """
    try: return settings.global_().ttsGenders().get(key) or 'f'
    except (ValueError, TypeError): return 'f'

  def setGender(self, key, v):
    """
    @param  key  str
    @param  v  str
    """
    ss = settings.global_()
    m = ss.ttsGenders()
    if v != m.get(key):
      m[key] = v
      ss.setTtsGenders(m)
      eng = self.getCreatedEngine(key)
      if eng:
        eng.setGender(v)

  # Actions

  def getEngine(self, key):
    """
    @return  _ttsman.VoiceEngine or None
    """
    if not key:
      return None
    if key == 'zunkooffline':
      return self.zunkoEngine
    if key == 'yukarioffline':
      return self.yukariEngine
    return self.getOnlineEngine(key) or self.getSapiEngine(key)

  def getCreatedEngine(self, key):
    """
    @return  _ttsman.VoiceEngine or None
    """
    if not key:
      return None
    if key == 'zunkooffline':
      return self._zunkoEngine
    if key == 'yukarioffline':
      return self._yukariEngine
    return self._onlineEngines.get(key) or self._voiceroidEngines.get(key) or self._voicetextEngines.get(key) or self._sapiEngines.get(key)

  #@memoizedproperty
  #def speakTimer(self):
  #  ret = QTimer(self.q)
  #  ret.setSingleShot(True)
  #  ret.timeout.connect(self._doSpeakTask)
  #  return ret

  def _doSpeakTask(self):
    if self._speakTask:
      try: self._speakTask()
      except Exception, e: dwarn(e)
      self._speakTask = None

class TtsManager(QObject):

  def __init__(self, parent=None):
    super(TtsManager, self).__init__(parent)
    d = self.__d = _TtsManager(self)

  def isOnline(self): return self.__d.online
  def setOnline(self, v): self.__d.online = v

  def stop(self):
    #if not features.TEXT_TO_SPEECH:
    #  return
    #with SkProfiler(): # 0.002 ~ 0.004 seconds when speaking with SAPI
    self.__d.stop()

  def defaultEngine(self): return self.__d.defaultEngineKey
  def setDefaultEngine(self, key):
    """
    @param  key  unicode
    """
    d = self.__d
    if d.defaultEngineKey != key:
      d.defaultEngineKey = key
      settings.global_().setTtsEngine(key)

  def getSpeed(self, v):
    return self.__d.getSpeed(v)
  def setSpeed(self, key, v):
    """
    @param  key  str
    @param  v  int in [-10,10]
    """
    self.__d.setSpeed(key, v)

  def getPitch(self, v):
    return self.__d.getPitch(v)
  def setPitch(self, key, v):
    """
    @param  key  str
    @param  v  int in [-10,10]
    """
    self.__d.setPitch(key, v)

  def getGender(self, v):
    return self.__d.getGender(v)
  def setGender(self, key, v):
    """
    @param  key  str
    @param  v  'f' or 'm'
    """
    self.__d.setGender(key, v)

  def getVolume(self, v):
    return self.__d.getVolume(v)
  def setVolume(self, key, v):
    """
    @param  key  str
    @param  v  int in [0,100]
    """
    self.__d.setVolume(key, v)

  def speak(self, text, interval=100, **kwargs):
    #if not features.TEXT_TO_SPEECH:
    #  return
    text = text.strip()
    if not text:
      return
    if interval:
      self.__d.speakLater(text, interval=interval, **kwargs)
    else:
      self.__d.speak(text, **kwargs)

  def getEngineLanguage(self, key): # str  engine key -> str not None
    eng = self.__d.getEngine(key)
    return eng.language if eng else ''

  def defaultEngineLanguage(self): # -> str not None
    return self.getEngineLanguage(self.__d.defaultEngineKey)

  def yukariLocation(self): return self.__d.yukariEngine.getPath()
  #def zunkoLocation(self): return self.__d.zunkoEngine.getPath()

  def runYukari(self): return self.__d.yukariEngine.run()
  #def runZunko(self): return self.__d.zunkoEngine.run()

  def availableEngines(self):
    """
    @return  [unicode]
    """
    d = self.__d
    import sapiman
    ret = [it.key for it in sapiman.voices()]
    for it in d.zunkoEngine, d.yukariEngine:
      if it.isValid():
        ret.append(it.key)
    ret.extend(_ttsman.ONLINE_ENGINES)
    return ret

@memoized
def manager(): return TtsManager()

def speak(*args, **kwargs): manager().speak(*args, **kwargs)
def warmup(): manager().warmup()
def stop(): manager().stop()

## Beans ##

#@QmlObject
class TtsQmlBean(QObject):
  def __init__(self, parent=None):
    super(TtsQmlBean, self).__init__(parent)

  @Slot(unicode, unicode)
  def speak(self, text, language):
    speak(text, language=language, termEnabled=False, verbose=False)
    dprint("pass")

  @Slot(result=unicode)
  def availableEngines(self):
    """
    @return  unicode  csv
    """
    return ',' + ','.join(manager().availableEngines())

class TtsCoffeeBean(QObject):
  def __init__(self, parent=None):
    super(TtsCoffeeBean, self).__init__(parent)

  @Slot(result=bool)
  def isEnabled(self):
    return bool(manager().defaultEngine())

  @Slot(unicode)
  def speak(self, text):
    speak(text, termEnabled=False, verbose=False)
    dprint("pass")

  #@Slot()
  #def stop(self): stop()

# EOF
