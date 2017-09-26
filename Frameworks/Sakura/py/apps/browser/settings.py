# coding: utf8
# settings.py
# 12/13/2012 jichi

from PySide.QtCore import QSettings, Signal
from sakurakit.skclass import memoized
from sakurakit.sktypes import to_int, to_unicode
import config

@memoized
def global_(): return Settings()

@memoized
def reader(): return ReaderSettings()

def to_bool(value): return value == True or value  == 'true'

def to_dict(value):
  """
  @param  dict or None
  @return  dict
  """
  return value if isinstance(value, dict) else {}

class Settings(QSettings):

  def __init__(self):
    super(Settings, self).__init__(
        QSettings.NativeFormat, QSettings.UserScope,
        config.VERSION_DOMAIN, config.VERSION_NAME)

  def setVersion(self, value): self.setValue('Version', value)
  def version(self): return to_int(self.value('Version'))

  def setWindowWidth(self, value): self.setValue("WindowWidth", value)
  def windowWidth(self): return to_int(self.value("WindowWidth"))

  def setWindowHeight(self, value): self.setValue("WindowHeight", value)
  def windowHeight(self): return to_int(self.value("WindowHeight"))

  def setLanguage(self, value): self.setValue('UserLanguage', value)
  def language(self): return to_unicode(self.value('UserLanguage'))

  def setPlayerActivated(self, value): self.setValue("PlayerActivated", value)
  def isPlayerActivated(self): return to_bool(self.value("PlayerActivated", True))

  def setReaderActivated(self, value): self.setValue("ReaderActivated", value)
  def isReaderActivated(self): return to_bool(self.value("ReaderActivated", True))

  def setRubyEnabled(self, value): self.setValue("RubyEnabled", value)
  def isRubyEnabled(self): return to_bool(self.value("RubyEnabled"))

  ttsEnabledChanged = Signal(bool)
  def isTtsEnabled(self): return to_bool(self.value("TtsEnabled"))
  def setTtsEnabled(self, value):
    if value != self.isTtsEnabled():
      self.setValue("TtsEnabled", value)
      self.ttsEnabledChanged.emit(value)

  fullTranslationEnabledChanged = Signal(bool)
  def isFullTranslationEnabled(self): return to_bool(self.value("FullTranslationEnabled"))
  def setFullTranslationEnabled(self, value):
    if value != self.isFullTranslationEnabled():
      self.setValue("FullTranslationEnabled", value)
      self.fullTranslationEnabledChanged.emit(value)

  translationTipEnabledChanged = Signal(bool)
  def isTranslationTipEnabled(self): return to_bool(self.value("TranslationTipEnabled"))
  def setTranslationTipEnabled(self, value):
    if value != self.isTranslationTipEnabled():
      self.setValue("TranslationTipEnabled", value)
      self.translationTipEnabledChanged.emit(value)

  # Translators

  infoseekEnabledChanged = Signal(bool)
  def isInfoseekEnabled(self):
    return to_bool(self.value('InfoseekEnabled'))
  def setInfoseekEnabled(self, value):
    if value != self.isInfoseekEnabled():
      self.setValue('InfoseekEnabled', value)
      self.infoseekEnabledChanged.emit(value)

  exciteEnabledChanged = Signal(bool)
  def isExciteEnabled(self):
    return to_bool(self.value('ExciteEnabled'))
  def setExciteEnabled(self, value):
    if value != self.isExciteEnabled():
      self.setValue('ExciteEnabled', value)
      self.exciteEnabledChanged.emit(value)

  googleEnabledChanged = Signal(bool)
  def isGoogleEnabled(self):
    return to_bool(self.value('GoogleEnabled'))
  def setGoogleEnabled(self, value):
    if value != self.isGoogleEnabled():
      self.setValue('GoogleEnabled', value)
      self.googleEnabledChanged.emit(value)

  bingEnabledChanged = Signal(bool)
  def isBingEnabled(self):
    return to_bool(self.value('BingEnabled', True)) # the only one enabled
  def setBingEnabled(self, value):
    if value != self.isBingEnabled():
      self.setValue('BingEnabled', value)
      self.bingEnabledChanged.emit(value)

  baiduEnabledChanged = Signal(bool)
  def isBaiduEnabled(self):
    return to_bool(self.value('BaiduEnabled'))
  def setBaiduEnabled(self, value):
    if value != self.isBaiduEnabled():
      self.setValue('BaiduEnabled', value)
      self.baiduEnabledChanged.emit(value)

  lecOnlineEnabledChanged = Signal(bool)
  def isLecOnlineEnabled(self):
    return to_bool(self.value('LecOnlineEnabled'))
  def setLecOnlineEnabled(self, value):
    if value != self.isLecOnlineEnabled():
      self.setValue('LecOnlineEnabled', value)
      self.lecOnlineEnabledChanged.emit(value)

  transruEnabledChanged = Signal(bool)
  def isTransruEnabled(self):
    return to_bool(self.value('TransruEnabled'))
  def setTransruEnabled(self, value):
    if value != self.isTransruEnabled():
      self.setValue('TransruEnabled', value)
      self.transruEnabledChanged.emit(value)

  hanVietEnabledChanged = Signal(bool)
  def isHanVietEnabled(self):
    return to_bool(self.value('HanVietEnabled'))
  def setHanVietEnabled(self, value):
    if value != self.isHanVietEnabled():
      self.setValue('HanVietEnabled', value)
      self.hanVietEnabledChanged.emit(value)

  atlasEnabledChanged = Signal(bool)
  def isAtlasEnabled(self):
    return to_bool(self.value('AtlasEnabled'))
  def setAtlasEnabled(self, value):
    if value != self.isAtlasEnabled():
      self.setValue('AtlasEnabled', value)
      self.atlasEnabledChanged.emit(value)

  lecEnabledChanged = Signal(bool)
  def isLecEnabled(self):
    return to_bool(self.value('LecEnabled'))
  def setLecEnabled(self, value):
    if value != self.isLecEnabled():
      self.setValue('LecEnabled', value)
      self.lecEnabledChanged.emit(value)

  jbeijingEnabledChanged = Signal(bool)
  def isJBeijingEnabled(self):
    return to_bool(self.value('JBeijingEnabled'))
  def setJBeijingEnabled(self, value):
    if value != self.isJBeijingEnabled():
      self.setValue('JBeijingEnabled', value)
      self.jbeijingEnabledChanged.emit(value)

  fastaitEnabledChanged = Signal(bool)
  def isFastaitEnabled(self):
    return to_bool(self.value('FastAITEnabled'))
  def setFastaitEnabled(self, value):
    if value != self.isFastaitEnabled():
      self.setValue('FastAITEnabled', value)
      self.fastaitEnabledChanged.emit(value)

  dreyeEnabledChanged =Signal(bool)
  def isDreyeEnabled(self):
    return to_bool(self.value('DreyeEnabled'))
  def setDreyeEnabled(self, value):
    if value != self.isDreyeEnabled():
      self.setValue('DreyeEnabled', value)
      self.dreyeEnabledChanged.emit(value)

  ezTransEnabledChanged = Signal(bool)
  def isEzTransEnabled(self):
    return to_bool(self.value('ezTransEnabled'))
  def setEzTransEnabled(self, value):
    if value != self.isEzTransEnabled():
      self.setValue('ezTransEnabled', value)
      self.ezTransEnabledChanged.emit(value)

# VNR's settings

class ReaderSettings(QSettings):

  def __init__(self):
    super(ReaderSettings, self).__init__(
        QSettings.NativeFormat, QSettings.UserScope,
        config.VERSION_DOMAIN, "reader")

  def version(self): return to_int(self.value('Version'))
  def updateTime(self): return to_int(self.value('UpdateTime'))

  def userLanguage(self): return self.value('UserLanguage')

  def isMainlandChina(self): return to_bool(self.value('MainlandChina'))

  def isCursorThemeEnabled(self): return to_bool(self.value('CursorThemeEnabled', True))

  def wallpaperUrl(self): return to_unicode(self.value('SpringBoardWallpaperUrl'))

  ## MeCab

  def rubyType(self): return self.value('JapaneseRubyType', 'hira')
  def isMeCabEnabled(self): return to_bool(self.value('JapaneseRuby'))

  ## TTS

  ttsEngineChanged = Signal(unicode)
  def ttsEngine(self): return to_unicode(self.value('TTSEngine'))

  zunkoLocationChanged = Signal(unicode)
  def zunkoLocation(self): return to_unicode(self.value('ZunkoLocation'))

  yukariLocationChanged = Signal(unicode)
  def yukariLocation(self): return to_unicode(self.value('YukariLocation'))

  def ttsSpeeds(self):
    """
    @return  {str ttskey:int speed}
    """
    return to_dict(self.value('TTSSpeeds'))

  def ttsPitches(self):
    """
    @return  {str ttskey:int pitch}
    """
    return to_dict(self.value('TTSPitches'))

  ## Translators

  def jbeijingLocation(self): return to_unicode(self.value('JBeijingLocation'))
  def fastaitLocation(self): return to_unicode(self.value('FastAITLocation'))
  def ezTransLocation(self): return to_unicode(self.value('ezTransLocation'))
  def dreyeLocation(self): return to_unicode(self.value('DreyeLocation'))
  def atlasLocation(self): return to_unicode(self.value('AtlasLocation'))
  def lecLocation(self): return to_unicode(self.value('LecLocation'))

# EOF
