# coding: utf8
# _ttsman.py
# 4/7/2013 jichi

import os
from sakurakit.skclass import memoizedproperty
from sakurakit.sktr import tr_
from i18n import i18n
import growl # dummy

## Voice engines ##

class VoiceEngine(object):
  key = ''      # str
  language = 'ja'   # str
  name = tr_('Unknown') # unicode
  #gender = 'f'  # str

  def setLanguage(self, v): self.language = v
  def isValid(self): return True
  def speak(self, text): pass
  def stop(self): pass

class GoogleEngine(VoiceEngine):
  key = 'google' # override
  name = u'Google TTS' # override

  def __init__(self, online=True, language='ja', parent=None):
    self._valid = False     # bool
    self.online = online    # bool
    self.language = language # str
    self.parentWidget = parent # QWidget or None

  def setOnline(self, v): self.online = v
  def isOnline(self): return self.online

  def isValid(self):
    """"@reimp"""
    return False # CHECKPOINT: Always disable Google engine

    if not self._valid:
      import libman
      self._valid = libman.quicktime().exists()
    return self._valid

  @memoizedproperty
  def engine(self):
    from google.googletts import GoogleTtsPlayer
    return GoogleTtsPlayer(self.parentWidget)

  def speak(self, text, language=None):
    """@reimp@"""
    if self.isOnline():
      if not self.isValid():
        growl.warn(my.tr("Missing QuickTime needed by text-to-speech"))
      else:
        self.engine.speak(text, language=language or self.language)

class VocalroidEngine(VoiceEngine):

  def __init__(self, voiceroid, path=''):
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
        i18n.tr("Activate Voiceroid+"),
        self.name,
      )))
      e.run()
    else:
      growl.warn(' '.join((
        i18n.tr("Cannot find Voiceroid+"),
        self.name,
      )))

  def speak(self, text):
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
      if e:
        e.stop()

class YukariEngine(VocalroidEngine):
  def __init__(self, **kwargs):
    import voiceroid.apps
    v = voiceroid.apps.Yukari()
    super(YukariEngine, self).__init__(v, **kwargs)

class ZunkoEngine(VocalroidEngine):
  def __init__(self, **kwargs):
    import voiceroid.apps
    v = voiceroid.apps.Zunko()
    super(ZunkoEngine, self).__init__(v, **kwargs)

class SapiEngine(VoiceEngine):
  def __init__(self, key, speed=0, pitch=0):
    self.key = key      # str
    self.speed = speed  # int
    self.pitch = pitch  # int
    self._speaking = False
    self._valid = False

    import sapi.engine, sapi.registry
    kw = sapi.registry.query(key=self.key)
    self.engine = sapi.engine.SapiEngine(speed=speed, pitch=pitch, **kw) if kw else None
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

  def isValid(self):
    """"@reimp"""
    if not self._valid:
      self._valid = bool(self.engine) and self.engine.isValid()
    return self._valid

  def speak(self, text):
    """@remip"""
    e = self.engine
    if e:
      if self._speaking:
        e.stop()
      else:
        self._speaking = True
      e.speak(text)

  def stop(self):
    """@remip"""
    if self._speaking:
      self._speaking = False
      e = self.engine
      if e:
        e.stop()

# EOF
