# coding: utf8
# ttsman.py
# 4/7/2013 jichi

from functools import partial
from PySide.QtCore import QObject, QTimer
#from sakurakit import skevents, skthreads
from sakurakit import skos
from sakurakit.skdebug import dwarn, dprint
from sakurakit.skclass import Q_Q, memoized, memoizedproperty
#from sakurakit.skqml import QmlObject
from i18n import i18n
import growl, settings
import _ttsman #textutil

class TtsManager(QObject):

  def __init__(self, parent=None):
    super(TtsManager, self).__init__(parent)
    d = self.__d = _TtsManager(self)

  def stop(self):
    if self.__d.enabled:
      self.__d.stop()

  def isEnabled(self): return self.__d.enabled
  def setEnabled(self, t): self.__d.enabled = t

  def defaultEngine(self): return self.__d.defaultEngineKey
  def setDefaultEngine(self, key):
    """
    @param  key  unicode
    """
    d = self.__d
    if d.defaultEngineKey != key:
      d.defaultEngineKey = key
      #settings.reader().setTtsEngine(key)

  def getSpeed(self, v):
    return self.__d.getSpeed(v)
  def setSpeed(self, key, v):
    """
    @param  value  int in [-10,10]
    """
    self.__d.setSpeed(key, v)

  def getPitch(self, v):
    return self.__d.getPitch(v)
  def setPitch(self, key, v):
    """
    @param  value  int in [-10,10]
    """
    self.__d.setPitch(key, v)

  def speak(self, text, interval=100, **kwargs):
    self.__d.speakLater(text, interval=interval, **kwargs)

  def yukariLocation(self): return self.__d.yukariEngine.getPath()
  def zunkoLocation(self): return self.__d.zunkoEngine.getPath()

  def runYukari(self): return self.__d.yukariEngine.run()
  def runZunko(self): return self.__d.zunkoEngine.run()

  def isAvailable(self):
    if not skos.WIN:
      return False
    d = self.__d
    for it in d.yukariEngine, d.zunkoEngine, d.googleEngine:
      if it.isValid():
        return True
    import sapiman
    return bool(sapiman.voices())

  def availableEngines(self):
    """
    @return  [unicode]
    """
    ret = []
    d = self.__d
    for it in d.yukariEngine, d.zunkoEngine:
      if it.isValid():
        ret.append(it.key)
    import sapiman
    ret.extend(it.key for it in sapiman.voices())
    return ret

@memoized
def manager(): return TtsManager()

def speak(*args, **kwargs): manager().speak(*args, **kwargs)
def stop(): manager().stop()

#@Q_Q
class _TtsManager(object):

  def __init__(self, q):
    self.enabled = True
    self.defaultEngineKey = '' # str
    self._speakTask = None   # partial function object

    self._googleEngine = None # _ttsman.GoogleEngine
    self._yukariEngine = None # _ttsman.YukariEngine
    self._zunkoEngine = None  # _ttsman.ZunkoEngine
    self._sapiEngines = {}    # {str key:_ttsman.SapiEngine}

    #self.defaultEngineKey = 'wrong engine'
    #self.defaultEngineKey = 'VW Misaki'
    #self.defaultEngineKey = 'VW Show'
    #self.defaultEngineKey = 'zunko'
    #self.defaultEngineKey = 'yukari'

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
    # TODO
    #if key in ('zunko', 'yukari'):
    #  ret = textutil.repair_voceroid_text(key)
    return ret

  def iterActiveEngines(self):
    """
    @yield  engine
    """
    for it in self._yukariEngine, self._zunkoEngine, self._googleEngine: # Google is disabled
      if it and it.isValid():
        yield it
    for it in self._sapiEngines.itervalues():
      if it.isValid():
        yield it

  def stop(self):
    for it in self.iterActiveEngines():
      it.stop()

  def speakLater(self, text, interval, **kwargs):
    if self.enabled:
      self._speakTask = partial(self._speak, text, **kwargs)
      self._speakTimer.start(interval)

  def _speak(self, text, engine='', language='', verbose=True):
    """
    @param  text  unicode
    @param* engine  str
    @param* language  unicode
    @param* verbose  bool  whether warn on error
    """
    if not text:
      return

    eng = self.getEngine(engine) if engine else None
    if not eng and self.defaultEngineKey and self.defaultEngineKey != engine:
      eng = self.getEngine(self.defaultEngineKey)

    if not eng:
      if verbose:
        growl.warn(i18n.tr("TTS is not available in Preferences"))
      dprint("missing engine: %s" % (engine or self.defaultEngineKey))
      return
    if not eng.isValid():
      #if verbose:
      # Always warn
      growl.warn('<br/>'.join((
        i18n.tr("TTS is not available"),
        eng.name,
      )))
      dprint("invalid engine: %s" % (eng.key))
      return
    if language and language[:2] != eng.language[:2]:
      dprint("language mismatch: %s != %s" % (language, eng.language))
      return

    # Even if text is empty, trigger stop tts
    #if not text:
    #  return
    text = self._repairText(text, eng.key)
    eng.speak(text)

    #skevents.runlater(partial(eng.speak, text))

  # Voice engines

  @property
  def googleEngine(self):
    if not self._googleEngine:
      ss = settings.global_()
      self._googleEngine = _ttsman.GoogleEngine()
          #online=self._online,
          #language='ja', # force Japanese language at this point
      #ss.googleTtsLanguageChanged.connect(self._googleEngine.setLanguage)
    return self._googleEngine

  # Voiceroid

  @property
  def yukariEngine(self):
    if not self._yukariEngine:
      ss = settings.reader()
      eng = self._yukariEngine = _ttsman.YukariEngine(path=ss.yukariLocation())
      ss.yukariLocationChanged.connect(eng.setPath)
      growl.msg(' '.join((
        i18n.tr("Load TTS"),
        eng.name,
      )))
    return self._yukariEngine

  @property
  def zunkoEngine(self):
    if not self._zunkoEngine:
      ss = settings.reader()
      eng = self._zunkoEngine = _ttsman.ZunkoEngine(path=ss.zunkoLocation())
      ss.zunkoLocationChanged.connect(eng.setPath)
      growl.msg(' '.join((
        i18n.tr("Load TTS"),
        eng.name,
      )))
    return self._zunkoEngine

  # SAPI

  def getSapiEngine(self, key):
    ret = self._sapiEngines.get(key)
    if not ret:
      ret = _ttsman.SapiEngine(key=key,
        speed=self.getSpeed(key),
        pitch=self.getPitch(key),
      )
      if ret.isValid():
        growl.msg(' '.join((
          i18n.tr("Load TTS"),
          ret.name,
        )))
        self._sapiEngines[key] = ret
      else:
        growl.warn(' '.join((
          i18n.tr("Failed to load TTS"),
          key,
        )))
        ret = None
    return ret

  def getPitch(self, key):
    """
    @param  key  str
    @return  int
    """
    try: return int(settings.reader().ttsPitches().get(key) or 0)
    except (ValueError, TypeError): return 0

  def setPitch(self, key, v):
    """
    @param  key  str
    @param  v  int
    """
    ss = settings.reader()
    m = ss.ttsPitches()
    if v != m.get(key):
      m[key] = v
      ss.setTtsPitches(m)
      eng = self._sapiEngines.get(key)
      if eng:
        eng.setPitch(v)

  def getSpeed(self, key):
    """
    @param  key  str
    @return  int
    """
    try: return int(settings.reader().ttsSpeeds().get(key) or 0)
    except (ValueError, TypeError): return 0

  def setSpeed(self, key, v):
    """
    @param  key  str
    @param  v  int
    """
    ss = settings.reader()
    m = ss.ttsSpeeds()
    if v != m.get(key):
      m[key] = v
      ss.setTtsSpeeds(m)
      eng = self._sapiEngines.get(key)
      if eng:
        eng.setSpeed(v)

  # Actions

  def getEngine(self, key):
    """
    @return  _ttsman.VoiceEngine or None
    """
    if key == 'zunkooffline':
      return None # zunko is not implemented yet
      #return self.zunkoEngine
    if key == 'yukarioffline':
      return self.yukariEngine
    if key == 'google':
      return self.googleEngine
    return self.getSapiEngine(key)

  def _doSpeakTask(self):
    if self._speakTask:
      try: apply(self._speakTask)
      except Exception, e: dwarn(e)
      self._speakTask = None

# EOF
