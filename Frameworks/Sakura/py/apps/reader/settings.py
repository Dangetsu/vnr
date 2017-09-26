# coding: utf8
# settings.py
# 10/28/2012 jichi

__all__ = 'SettingsProxy',

import json
from PySide.QtCore import Signal, Slot, Property, Qt, QObject, QSettings, QTimer, QSize
from sakurakit.skclass import memoized, memoizedproperty
from sakurakit.skdebug import dwarn
#from sakurakit.skqml import QmlObject
from sakurakit.sktypes import to_int, to_unicode #to_long
import defs, config

# http://msdn.microsoft.com/en-us/library/windows/desktop/dd375731%28v=vs.85%29.aspx
# win32con
VK_SHIFT = 0x10

def parse_json(v): # str -> object or None
  if v:
    try: return json.loads(v)
    except: pass

def unparse_json(v): # object -> str
  return json.dumps(v, ensure_ascii=False)

def to_bool(value):
  return value == True or value  == 'true'

#def to_str(value):
#  return value if isinstance(value, str) else ''
#  return value is None else "%s" % value

def to_float(value, default=0.0):
  try: return float(value)
  except: return default

def to_size(value):
  """
  @param  value  QSize or None
  @return  (int w, int h)
  """
  try: return value.width(), value.height()
  except: return 0,0

def to_list(value):
  """
  @param  value  list or None
  @return  set
  """
  try: return value if isinstance(value, list) else list(value) if value is not None else list()
  except: return list()

def to_set(value):
  """
  @param  value  set or None
  @return  set
  """
  try: return value if isinstance(value, set) else set(value) if value is not None else set()
  except: return set()

def to_dict(value):
  """
  @param  value  dict or None
  @return  dict
  """
  return value if isinstance(value, dict) else {}

def list2string(value, sep=','):
  """
  @param  value  list
  @return  string
  """
  return sep.join(value) if value else ''

def string2list(value, sep=','):
  """
  @param  value  string
  @return  list
  """
  return value.split() if value and isinstance(value, basestring) else list()

class _Settings:

  def __init__(self, q):
    t = self.syncTimer = QTimer(q)
    t.setInterval(config.APP_SAVE_SETTINGS_INTERVAL)
    t.timeout.connect(q.sync)

class Settings(QSettings):

  def __init__(self):
    super(Settings, self).__init__(
        QSettings.NativeFormat, QSettings.UserScope,
        config.VERSION_DOMAIN, config.VERSION_NAME)
    self.__d = _Settings(self)

  def autoSync(self): self.__d.syncTimer.start()

  def setVersion(self, value): self.setValue('Version', value)
  def version(self): return to_int(self.value('Version'))

  def setUpdateTime(self, value): self.setValue('UpdateTime', value)
  def updateTime(self): return to_int(self.value('UpdateTime'))

  def setGreetingTime(self, value): self.setValue('GreetingTime', value)
  def greetingTime(self): return to_int(self.value('GreetingTime'))

  def setGameFilesTime(self, value): self.setValue('GameFilesTime', value)
  def gameFilesTime(self): return to_int(self.value('GameFilesTime'))

  def setGameItemsTime(self, value): self.setValue('GameItemsTime', value)
  def gameItemsTime(self): return to_int(self.value('GameItemsTime'))

  def setUserDigestsTime(self, value): self.setValue('UserDigestsTime', value)
  def userDigestsTime(self): return to_int(self.value('UserDigestsTime'))

  def setTermsTime(self, value): self.setValue('TermsTime', value)
  def termsTime(self): return to_int(self.value('TermsTime'))

  #def setTranslationScriptTime(self, value): self.setValue('TranslationScriptTime', value)
  #def translationScriptTime(self): return to_int(self.value('TranslationScriptTime'))

  ## Window sizes ##

  def setSpringBoardSize(self, value): self.setValue('SpringBoardSize', value)
  def springBoardSize(self): return to_size(self.value('SpringBoardSize'))

  ## Spring board ##
  #def setSpringBoardLaunchesGame(self, value): self.setValue('SpringBoardLaunch', value)
  #def springBoardLaunchesGame(self): return to_bool(self.value('SpringBoardLaunch', False))

  ## Kagami ##

  kagamiFocusEnabledChanged = Signal(bool)
  def isKagamiFocusEnabled(self): return to_bool(self.value('KagamiFocusEnabled', False))
  def setKagamiFocusEnabled(self, value):
    if value != self.isKagamiFocusEnabled():
      self.setValue('KagamiFocusEnabled', value)
      self.kagamiFocusEnabledChanged.emit(value)

  ## User profile ##

  userIdChanged = Signal(int)
  def userId(self): return to_int(self.value('UserId'))
  def setUserId(self, value):
    if value != self.userId():
      self.setValue('UserId', value)
      self.userIdChanged.emit(value)

  def setUserName(self, value): self.setValue('UserName', value)
  def userName(self): return self.value('UserName')

  # TODO: encrypt password
  def setUserPassword(self, value): self.setValue('UserPassword', value)
  def userPassword(self): return self.value('UserPassword')

  loginChanged = Signal(unicode, unicode) # username, password
  def invalidateLogin(self):
    self.loginChanged.emit(self.userName(), self.userPassword())

  def uiLanguage(self): return self.value('Language')
  def setUiLanguage(self, value): self.setValue('Language', value)

  userLanguageChanged = Signal(str)
  def userLanguage(self):
    return self.value('UserLanguage')
  def setUserLanguage(self, value):
    if value != self.userLanguage():
      self.setValue('UserLanguage', value)
      self.userLanguageChanged.emit(value)
  
  userTranslateChanged = Signal(str)
  def translateLanguage(self):
    return self.value('TranslateLanguage')
  def setTranslateLanguage(self, value):
    if value != self.translateLanguage():
      self.setValue('TranslateLanguage', value)
      self.userTranslateChanged.emit(value)

  userGenderChanged = Signal(str)
  def userGender(self):
    return self.value('UserGender')
  def setUserGender(self, value):
    if value != self.userGender():
      self.setValue('UserGender', value)
      self.userGenderChanged.emit(value)

  userCommentLevelChanged = Signal(int)
  def userCommentLevel(self): return to_int(self.value('UserCommentLevel'))
  def setUserCommentLevel(self, value):
    if value != self.userCommentLevel():
      self.setValue('UserCommentLevel', value)
      self.userCommentLevelChanged.emit(value)
  
  userAccessChanged = Signal(str)
  def userAccess(self): return self.value('userAccess')
  def setUserAccess(self, value):
    if value != self.userAccess():
      self.setValue('userAccess', value)
      self.userAccessChanged.emit(value)

  userTermLevelChanged = Signal(int)
  def userTermLevel(self): return to_int(self.value('UserTermLevel'))
  def setUserTermLevel(self, value):
    if value != self.userTermLevel():
      self.setValue('UserTermLevel', value)
      self.userTermLevelChanged.emit(value)

  userColorChanged = Signal(unicode)
  def userColor(self): return self.value('UserColor')
  def setUserColor(self, value):
    if value != self.userColor():
      self.setValue('UserColor', value)
      self.userColorChanged.emit(value)

  userAvatarChanged = Signal(unicode)
  def userAvatar(self): return self.value('UserAvatar')
  def setUserAvatar(self, value):
    if value != self.userAvatar():
      self.setValue('UserAvatar', value)
      self.userAvatarChanged.emit(value)

  def setUserHomepage(self, value): self.setValue('UserHomepage', value)
  def userHomepage(self): return self.value('UserHomepage')

  ## PRC fixes, fxxk CCP ##

  mainlandChinaChanged = Signal(bool)
  def isMainlandChina(self): return to_bool(self.value('MainlandChina'))
  def setMainlandChina(self, value):
    if value != self.isMainlandChina():
      self.setValue('MainlandChina', value)
      self.mainlandChinaChanged.emit(value)

  ## Proxies ##

  proxyScapeChanged = Signal(bool)
  def proxyScape(self): return to_bool(self.value('ProxyScape'))
  def setProxyScape(self, value):
    if value != self.proxyScape():
      self.setValue('ProxyScape', value)
      self.proxyScapeChanged.emit(value)

  proxyBaiduChanged = Signal(bool)
  def proxyBaidu(self): return to_bool(self.value('ProxyBaidu'))
  def setProxyBaidu(self, value):
    if value != self.proxyBaidu():
      self.setValue('ProxyBaidu', value)
      self.proxyBaiduChanged.emit(value)

  ## i18n ##

  blockedLanguagesChanged = Signal(str)
  def blockedLanguages(self): return self.value('BlockedLanguages') or ''
    # http://sakuradite.com/topic/231, prevent strange EOFError
    #try: return to_set(self.value('BlockedLanguages'))
    #except EOFError, e:
    #  dwarn("EOFError")
    #  self.setValue('BlockedLanguages', set())
    #  return set()
  def setBlockedLanguages(self, value):
    if value != self.blockedLanguages():
      self.setValue('BlockedLanguages', value)
      self.blockedLanguagesChanged.emit(value)

  def setBlockedLanguageList(self, v): self.setBlockedLanguages(list2string(v)) # [unicode] ->
  def blockedLanguageList(self): return string2list(self.blockedLanguages()) # -> [unicode]

  growlEnabledChanged = Signal(bool)
  def isGrowlEnabled(self): return to_bool(self.value('Growl', True))
  def setGrowlEnabled(self, t):
    if t != self.isGrowlEnabled():
      self.setValue('Growl', t)
      self.growlEnabledChanged.emit(t)

  ## Romanization for Japanese ##

  romajiMacronEnabledChanged = Signal(bool)
  def isRomajiMacronEnabled(self):
    return to_bool(self.value('RomajiMacron')) # disabled by default
  def setRomajiMacronEnabled(self, value):
    if value != self.isRomajiMacronEnabled():
      self.setValue('RomajiMacron', value)
      self.romajiMacronEnabledChanged.emit(value)

  japaneseRubyInvertedChanged = Signal(bool)
  def isJapaneseRubyInverted(self):
    return to_bool(self.value('JapaneseInvertRuby'))
  def setJapaneseRubyInverted(self, t):
    if t != self.isJapaneseRubyInverted():
      self.setValue('JapaneseInvertRuby', t)
      self.japaneseRubyInvertedChanged.emit(t)

  japaneseRubyTypeChanged = Signal(unicode)
  def japaneseRubyType(self): return self.value('JapaneseRubyType', 'hira')
  def setJapaneseRubyType(self, value):
    if value != self.japaneseRubyType():
      self.setValue('JapaneseRubyType', value)
      self.japaneseRubyTypeChanged.emit(value)

  japaneseRubyEnabledChanged = Signal(bool)
  def isJapaneseRubyEnabled(self): return to_bool(self.value('JapaneseRuby'))
  def setJapaneseRubyEnabled(self, value):
    if value != self.isJapaneseRubyEnabled():
      self.setValue('JapaneseRuby', value)
      self.japaneseRubyEnabledChanged.emit(value)

  japaneseRubyKanaEnabledChanged = Signal(bool)
  def isJapaneseRubyKanaEnabled(self): return to_bool(self.value('JapaneseRubyKana'))
  def setJapaneseRubyKanaEnabled(self, value):
    if value != self.isJapaneseRubyKanaEnabled():
      self.setValue('JapaneseRubyKana', value)
      self.japaneseRubyKanaEnabledChanged.emit(value)

  japaneseRubyHighlightEnabledChanged = Signal(bool)
  def isJapaneseRubyHighlightEnabled(self): return to_bool(self.value('JapaneseRubyHighlight', True))
  def setJapaneseRubyHighlightEnabled(self, t):
    if t != self.isJapaneseRubyHighlightEnabled():
      self.setValue('JapaneseRubyHighlight', t)
      self.japaneseRubyHighlightEnabledChanged.emit(t)

  japaneseRubyAnnotatedChanged = Signal(bool)
  def isJapaneseRubyAnnotated(self): return to_bool(self.value('JapaneseRubyAnnotated', True))
  def setJapaneseRubyAnnotated(self, t):
    if t != self.isJapaneseRubyAnnotated():
      self.setValue('JapaneseRubyAnnotated', t)
      self.japaneseRubyAnnotatedChanged.emit(t)

  ## Romanization for non-Japanese ##

  translatesAlphabetChanged = Signal(bool)
  def translatesAlphabet(self): return to_bool(self.value('TranslateAlphabet'))
  def setTranslatesAlphabet(self, value):
    if value != self.translatesAlphabet():
      self.setValue('TranslateAlphabet', value)
      self.translatesAlphabetChanged.emit(value)

  rubyTextEnabledChanged = Signal(bool)
  def isRubyTextEnabled(self): return to_bool(self.value('RubyText', True))
  def setRubyTextEnabled(self, value):
    if value != self.isRubyTextEnabled():
      self.setValue('RubyText', value)
      self.rubyTextEnabledChanged.emit(value)

  rubyTranslationEnabledChanged = Signal(bool)
  def isRubyTranslationEnabled(self): return to_bool(self.value('RubyTranslation'))
  def setRubyTranslationEnabled(self, value):
    if value != self.isRubyTranslationEnabled():
      self.setValue('RubyTranslation', value)
      self.rubyTranslationEnabledChanged.emit(value)

  rubyInvertedChanged = Signal(bool)
  def isRubyInverted(self):
    return to_bool(self.value('InvertRuby'))
  def setRubyInverted(self, t):
    if t != self.isRubyInverted():
      self.setValue('InvertRuby', t)
      self.rubyInvertedChanged.emit(t)

  chineseRubyTypeChanged = Signal(unicode)
  def chineseRubyType(self): return self.value('ChineseRubyType', 'pinyin')
  def setChineseRubyType(self, value):
    if value != self.chineseRubyType():
      self.setValue('ChineseRubyType', value)
      self.chineseRubyTypeChanged.emit(value)

  chineseRubyEnabledChanged = Signal(bool)
  def isChineseRubyEnabled(self): return to_bool(self.value('ChineseRuby', True))
  def setChineseRubyEnabled(self, value):
    if value != self.isChineseRubyEnabled():
      self.setValue('ChineseRuby', value)
      self.chineseRubyEnabledChanged.emit(value)

  koreanRubyEnabledChanged = Signal(bool)
  def isKoreanRubyEnabled(self): return to_bool(self.value('KoreanRuby', True))
  def setKoreanRubyEnabled(self, value):
    if value != self.isKoreanRubyEnabled():
      self.setValue('KoreanRuby', value)
      self.koreanRubyEnabledChanged.emit(value)

  hanjaRubyEnabledChanged = Signal(bool)
  def isHanjaRubyEnabled(self): return to_bool(self.value('HanjaRuby', True))
  def setHanjaRubyEnabled(self, value):
    if value != self.isHanjaRubyEnabled():
      self.setValue('HanjaRuby', value)
      self.hanjaRubyEnabledChanged.emit(value)

  romajaRubyEnabledChanged = Signal(bool)
  def isRomajaRubyEnabled(self): return to_bool(self.value('RomajaRuby', True))
  def setRomajaRubyEnabled(self, value):
    if value != self.isRomajaRubyEnabled():
      self.setValue('RomajaRuby', value)
      self.romajaRubyEnabledChanged.emit(value)

  ## OCR ##

  ocrEnabledChanged = Signal(bool)
  def isOcrEnabled(self): return to_bool(self.value('OCREnabled'))
  def setOcrEnabled(self, value):
    if value != self.isOcrEnabled():
      self.setValue('OCREnabled', value)
      self.ocrEnabledChanged.emit(value)

  ocrComboKeyChanged = Signal(int)
  def ocrComboKey(self): return to_int(self.value('OCRVirtualKey', VK_SHIFT))
  def setOcrComboKey(self, value):
    if value != self.ocrComboKey():
      self.setValue('OCRVirtualKey', value)
      self.ocrComboKeyChanged.emit(value)

  ocrSpaceEnabledChanged = Signal(bool)
  def isOcrSpaceEnabled(self): return to_bool(self.value('OCRSpace'))
  def setOcrSpaceEnabled(self, value):
    if value != self.isOcrSpaceEnabled():
      self.setValue('OCRSpace', value)
      self.ocrSpaceEnabledChanged.emit(value)

  ocrLanguagesChanged = Signal(list)
  def ocrLanguages(self): return to_list(self.value('OCRLanguages', ['ja','zhs','zht','en']))
  def setOcrLanguages(self, value):
    if value != self.ocrLanguages():
      self.setValue('OCRLanguages', value)
      self.ocrLanguagesChanged.emit(value)

  ocrRefreshIntervalChanged = Signal(int)
  def ocrRefreshInterval(self): return to_int(self.value('OCRRefreshInterval', 1000)) # 1 second by default
  def setOcrRefreshInterval(self, value):
    if value != self.ocrRefreshInterval():
      self.setValue('OCRRefreshInterval', value)
      self.ocrRefreshIntervalChanged.emit(value)

  ## Locale ##

  def gameLaunchLanguage(self):
    return self.value('GameLaunchLanguage', 'ja')
  def setGameLaunchLanguage(self, value):
    self.setValue('GameLaunchLanguage', value)

  #applocEnabledChanged = Signal(bool)
  #def isApplocEnabled(self):
  #  return to_bool(self.value('ApplocEnabled', True))
  #def setApplocEnabled(self, value):
  #  if value != self.isApplocEnabled():
  #    self.setValue('ApplocEnabled', value)
  #    self.applocEnabledChanged.emit(value)
  def isApplocEnabled(self):
    return to_bool(self.value('ApplocEnabled', True))
  def setApplocEnabled(self, value):
    self.setValue('ApplocEnabled', value)

  #timeZoneEnabledChanged = Signal(bool)
  def isTimeZoneEnabled(self):
    return to_bool(self.value('TimeZoneEnabled'))
  def setTimeZoneEnabled(self, value):
    self.setValue('TimeZoneEnabled', value)
  #  if value != self.isTimeZoneEnabled():
  #    self.setValue('TimeZoneEnabled', value)
  #    self.timeZoneEnabledChanged.emit(value)
  #def isTimeZoneEnabled(self): return True

  def isLocaleSwitchEnabled(self):
    return to_bool(self.value('LocaleSwitchEnabled'))
  def setLocaleSwitchEnabled(self, value):
    self.setValue('LocaleSwitchEnabled', value)

  def isNtleaEnabled(self):
    return to_bool(self.value('NtleaEnabled'))
  def setNtleaEnabled(self, value):
    self.setValue('NtleaEnabled', value)

  #def ntleaLocation(self):
  #  return to_unicode(self.value('NtleaLocation'))
  #def setNtleaLocation(self, value):
  #  self.setValue('NtleaLocation', value)

  def isLocaleEmulatorEnabled(self):
    return to_bool(self.value('LocaleEmulatorEnabled'))
  def setLocaleEmulatorEnabled(self, value):
    self.setValue('LocaleEmulatorEnabled', value)

  def localeEmulatorLocation(self):
    return to_unicode(self.value('LocaleEmulatorLocation'))
  def setLocaleEmulatorLocation(self, value):
    self.setValue('LocaleEmulatorLocation', value)

  def isNtleasEnabled(self):
    return to_bool(self.value('NtleasEnabled'))
  def setNtleasEnabled(self, value):
    self.setValue('NtleasEnabled', value)

  def ntleasLocation(self):
    return to_unicode(self.value('NtleasLocation'))
  def setNtleasLocation(self, value):
    self.setValue('NtleasLocation', value)

  ## QuickTime ##

  #def isQuickTimeEnabled(self): return to_bool(self.value('QuickTimeEnabled', True))
  #def setQuickTimeEnabled(self, value): self.setValue('QuickTimeEnabled', value)

  ## UI ##

  #def kagamiIgnoresFocus(self):
  #  return to_bool(self.value('KagamiIgnoresFocus', True))

  #applicationFontFamilyChanged = Signal(str)
  #def applicationFontFamily(self):
  #  return self.value('ApplicationFontFamily') or ''
  #def setApplicationFontFamily(self, value):
  #  if value != self.applicationFontFamily():
  #    self.setValue('ApplicationFontFamily', value)
  #    self.applicationFontFamilyChanged.emit(value)

  cursorThemeEnabledChanged = Signal(bool)
  def isCursorThemeEnabled(self):
    return to_bool(self.value('CursorThemeEnabled', True))
  def setCursorThemeEnabled(self, value):
    if value != self.isCursorThemeEnabled():
      self.setValue('CursorThemeEnabled', value)
      self.cursorThemeEnabledChanged.emit(value)

      import curtheme
      if value: curtheme.load()
      else: curtheme.unload()

  cometCounterVisibleChanged = Signal(bool)
  def isCometCounterVisible(self):
    return to_bool(self.value('CometCounterVisible', True))
  def setCometCounterVisible(self, value):
    if value != self.isCometCounterVisible():
      self.setValue('CometCounterVisible', value)
      self.cometCounterVisibleChanged.emit(value)

  springBoardWallpaperUrlChanged = Signal(unicode)
  def springBoardWallpaperUrl(self):
    return to_unicode(self.value('SpringBoardWallpaperUrl'))
  def setSpringBoardWallpaperUrl(self, value):
    if value != self.springBoardWallpaperUrl():
      self.setValue('SpringBoardWallpaperUrl', value)
      self.springBoardWallpaperUrlChanged.emit(value)

  springBoardSlidesEnabledChanged = Signal(bool)
  def isSpringBoardSlidesEnabled(self):
    return to_bool(self.value('SpringBoardSlidesEnabled', True))
  def setSpringBoardSlidesEnabled(self, value):
    if value != self.isSpringBoardSlidesEnabled():
      self.setValue('SpringBoardSlidesEnabled', value)
      self.springBoardSlidesEnabledChanged.emit(value)

  grimoireFontColorChanged = Signal(str)
  def grimoireFontColor(self):
    return self.value('GrimoireFontColor', config.SETTINGS_FONT_COLOR)
  def setGrimoireFontColor(self, value):
    value = value or config.SETTINGS_SHADOW_COLOR
    if value != self.grimoireFontColor():
      self.setValue('GrimoireFontColor', value)
      self.grimoireFontColorChanged.emit(value)

  grimoireShadowColorChanged = Signal(str)
  def grimoireShadowColor(self):
    return self.value('GrimoireShadowColor', config.SETTINGS_SHADOW_COLOR)
  def setGrimoireShadowColor(self, value):
    value = value or config.SETTINGS_SHADOW_COLOR
    if value != self.grimoireShadowColor():
      self.setValue('GrimoireShadowColor', value)
      self.grimoireShadowColorChanged.emit(value)

  grimoireTextColorChanged = Signal(str)
  def grimoireTextColor(self):
    return self.value('GrimoireTextColor', config.SETTINGS_TEXT_COLOR)
  def setGrimoireTextColor(self, value):
    value = value or config.SETTINGS_TEXT_COLOR
    if value != self.grimoireTextColor():
      self.setValue('GrimoireTextColor', value)
      self.grimoireTextColorChanged.emit(value)

  #grimoireTranslationColorChanged = Signal(str)
  #def grimoireTranslationColor(self):
  #  return self.value('GrimoireTranslationColor', config.SETTINGS_TRANSLATION_COLOR)
  #def setGrimoireTranslationColor(self, value):
  #  value = value or config.SETTINGS_TRANSLATION_COLOR
  #  if value != self.grimoireTranslationColor():
  #    self.setValue('GrimoireTranslationColor', value)
  #    self.grimoireTranslationColorChanged.emit(value)

  grimoireSubtitleColorChanged = Signal(str)
  def grimoireSubtitleColor(self):
    return self.value('GrimoireSubtitleColor', config.SETTINGS_SUBTITLE_COLOR)
  def setGrimoireSubtitleColor(self, value):
    value = value or config.SETTINGS_SUBTITLE_COLOR
    if value != self.grimoireSubtitleColor():
      self.setValue('GrimoireSubtitleColor', value)
      self.grimoireSubtitleColorChanged.emit(value)

  grimoireCommentColorChanged = Signal(str)
  def grimoireCommentColor(self):
    return self.value('GrimoireCommentColor', config.SETTINGS_COMMENT_COLOR)
  def setGrimoireCommentColor(self, value):
    value = value or config.SETTINGS_COMMENT_COLOR
    if value != self.grimoireCommentColor():
      self.setValue('GrimoireCommentColor', value)
      self.grimoireCommentColorChanged.emit(value)

  grimoireDanmakuColorChanged = Signal(str)
  def grimoireDanmakuColor(self):
    return self.value('GrimoireDanmakuColor', config.SETTINGS_DANMAKU_COLOR)
  def setGrimoireDanmakuColor(self, value):
    value = value or config.SETTINGS_DANMAKU_COLOR
    if value != self.grimoireDanmakuColor():
      self.setValue('GrimoireDanmakuColor', value)
      self.grimoireDanmakuColorChanged.emit(value)

  infoseekColorChanged = Signal(str)
  def infoseekColor(self):
    return self.value('InfoseekColor', config.SETTINGS_INFOSEEK_COLOR)
  def setInfoseekColor(self, value):
    value = value or config.SETTINGS_INFOSEEK_COLOR
    if value != self.infoseekColor():
      self.setValue('InfoseekColor', value)
      self.infoseekColorChanged.emit(value)

  exciteColorChanged = Signal(str)
  def exciteColor(self):
    return self.value('ExciteColor', config.SETTINGS_EXCITE_COLOR)
  def setExciteColor(self, value):
    value = value or config.SETTINGS_EXCITE_COLOR
    if value != self.exciteColor():
      self.setValue('ExciteColor', value)
      self.exciteColorChanged.emit(value)

  babylonColorChanged = Signal(str)
  def babylonColor(self):
    return self.value('BabylonColor', config.SETTINGS_BABYLON_COLOR)
  def setBabylonColor(self, value):
    value = value or config.SETTINGS_BABYLON_COLOR
    if value != self.babylonColor():
      self.setValue('BabylonColor', value)
      self.babylonColorChanged.emit(value)

  systranColorChanged = Signal(str)
  def systranColor(self):
    return self.value('SystranColor', config.SETTINGS_SYSTRAN_COLOR)
  def setSystranColor(self, value):
    value = value or config.SETTINGS_SYSTRAN_COLOR
    if value != self.systranColor():
      self.setValue('SystranColor', value)
      self.systranColorChanged.emit(value)

  niftyColorChanged = Signal(str)
  def niftyColor(self):
    return self.value('NiftyColor', config.SETTINGS_NIFTY_COLOR)
  def setNiftyColor(self, value):
    value = value or config.SETTINGS_NIFTY_COLOR
    if value != self.niftyColor():
      self.setValue('NiftyColor', value)
      self.niftyColorChanged.emit(value)

  googleColorChanged = Signal(str)
  def googleColor(self):
    return self.value('GoogleColor', config.SETTINGS_GOOGLE_COLOR)
  def setGoogleColor(self, value):
    value = value or config.SETTINGS_GOOGLE_COLOR
    if value != self.googleColor():
      self.setValue('GoogleColor', value)
      self.googleColorChanged.emit(value)

  bingColorChanged = Signal(str)
  def bingColor(self):
    return self.value('BingColor', config.SETTINGS_BING_COLOR)
  def setBingColor(self, value):
    value = value or config.SETTINGS_BING_COLOR
    if value != self.bingColor():
      self.setValue('BingColor', value)
      self.bingColorChanged.emit(value)

  naverColorChanged = Signal(str)
  def naverColor(self):
    return self.value('NaverColor', config.SETTINGS_NAVER_COLOR)
  def setNaverColor(self, value):
    value = value or config.SETTINGS_NAVER_COLOR
    if value != self.naverColor():
      self.setValue('NaverColor', value)
      self.naverColorChanged.emit(value)

  baiduColorChanged = Signal(str)
  def baiduColor(self):
    return self.value('BaiduColor', config.SETTINGS_BAIDU_COLOR)
  def setBaiduColor(self, value):
    value = value or config.SETTINGS_BAIDU_COLOR
    if value != self.baiduColor():
      self.setValue('BaiduColor', value)
      self.baiduColorChanged.emit(value)

  youdaoColorChanged = Signal(str)
  def youdaoColor(self):
    return self.value('YoudaoColor', config.SETTINGS_YOUDAO_COLOR)
  def setYoudaoColor(self, value):
    value = value or config.SETTINGS_YOUDAO_COLOR
    if value != self.youdaoColor():
      self.setValue('YoudaoColor', value)
      self.youdaoColorChanged.emit(value)

  lecOnlineColorChanged = Signal(str)
  def lecOnlineColor(self):
    return self.value('LecOnlineColor', config.SETTINGS_LECONLINE_COLOR)
  def setLecOnlineColor(self, value):
    value = value or config.SETTINGS_LECONLINE_COLOR
    if value != self.lecOnlineColor():
      self.setValue('LecOnlineColor', value)
      self.lecOnlineColorChanged.emit(value)

  transruColorChanged = Signal(str)
  def transruColor(self):
    return self.value('TransruColor', config.SETTINGS_TRANSRU_COLOR)
  def setTransruColor(self, value):
    value = value or config.SETTINGS_TRANSRU_COLOR
    if value != self.transruColor():
      self.setValue('TransruColor', value)
      self.transruColorChanged.emit(value)

  hanVietColorChanged = Signal(str)
  def hanVietColor(self):
    return self.value('HanVietColor', config.SETTINGS_HANVIET_COLOR)
  def setHanVietColor(self, value):
    value = value or config.SETTINGS_HANVIET_COLOR
    if value != self.hanVietColor():
      self.setValue('HanVietColor', value)
      self.hanVietColorChanged.emit(value)

  vtransColorChanged = Signal(str)
  def vtransColor(self):
    return self.value('VTransColor', config.SETTINGS_VTRANS_COLOR)
  def setVTransColor(self, value):
    value = value or config.SETTINGS_VTRANS_COLOR
    if value != self.vtransColor():
      self.setValue('VTransColor', value)
      self.vtransColorChanged.emit(value)

  romajiColorChanged = Signal(str)
  def romajiColor(self):
    return self.value('RomajiColor', config.SETTINGS_ROMAJI_COLOR)
  def setRomajiColor(self, value):
    value = value or config.SETTINGS_ROMAJI_COLOR
    if value != self.romajiColor():
      self.setValue('RomajiColor', value)
      self.romajiColorChanged.emit(value)

  jbeijingColorChanged = Signal(str)
  def jbeijingColor(self):
    return self.value('JBeijingColor', config.SETTINGS_JBEIJING_COLOR)
  def setJBeijingColor(self, value):
    value = value or config.SETTINGS_JBEIJING_COLOR
    if value != self.jbeijingColor():
      self.setValue('JBeijingColor', value)
      self.jbeijingColorChanged.emit(value)

  fastaitColorChanged = Signal(str)
  def fastaitColor(self):
    return self.value('FastAITColor', config.SETTINGS_FASTAIT_COLOR)
  def setFastaitColor(self, value):
    value = value or config.SETTINGS_FASTAIT_COLOR
    if value != self.fastaitColor():
      self.setValue('FastAITColor', value)
      self.fastaitColorChanged.emit(value)

  dreyeColorChanged = Signal(str)
  def dreyeColor(self):
    return self.value('DreyeColor', config.SETTINGS_DREYE_COLOR)
  def setDreyeColor(self, value):
    value = value or config.SETTINGS_DREYE_COLOR
    if value != self.dreyeColor():
      self.setValue('DreyeColor', value)
      self.dreyeColorChanged.emit(value)

  ezTransColorChanged = Signal(str)
  def ezTransColor(self):
    return self.value('EzTransColor', config.SETTINGS_EZTRANS_COLOR)
  def setEzTransColor(self, value):
    value = value or config.SETTINGS_EZTRANS_COLOR
    if value != self.ezTransColor():
      self.setValue('EzTransColor', value)
      self.ezTransColorChanged.emit(value)

  transcatColorChanged = Signal(str)
  def transcatColor(self):
    return self.value('TransCATColor', config.SETTINGS_TRANSCAT_COLOR)
  def setTranscatColor(self, value):
    value = value or config.SETTINGS_TRANSCAT_COLOR
    if value != self.transcatColor():
      self.setValue('TransCATColor', value)
      self.transcatColorChanged.emit(value)

  atlasColorChanged = Signal(str)
  def atlasColor(self):
    return self.value('AtlasColor', config.SETTINGS_ATLAS_COLOR)
  def setAtlasColor(self, value):
    value = value or config.SETTINGS_ATLAS_COLOR
    if value != self.atlasColor():
      self.setValue('AtlasColor', value)
      self.atlasColorChanged.emit(value)

  lecColorChanged = Signal(str)
  def lecColor(self):
    return self.value('LecColor', config.SETTINGS_LEC_COLOR)
  def setLecColor(self, value):
    value = value or config.SETTINGS_LEC_COLOR
    if value != self.lecColor():
      self.setValue('LecColor', value)
      self.lecColorChanged.emit(value)

  ## Plugin ##

  #def isPyPluginEnabled(self): return to_bool(self.value('PyPluginEnabled'))
  #def setPyPluginEnabled(self, value): self.setValue('PyPluginEnabled', value)

  #def isJsPluginEnabled(self): return to_bool(self.value('JsPluginEnabled'))
  #def setJsPluginEnabled(self, value): self.setValue('JsPluginEnabled', value)

  ## Features ##

  internetConnectionChanged = Signal(str)
  def internetConnection(self): return self.value('InternetConnection', defs.INTERNET_CONNECTION_AUTO)
  def setInternetConnection(self, value):
    if value != self.internetConnection():
      self.setValue('InternetConnection', value)
      self.internetConnectionChanged.emit(value)

  #allowsInternetAccessChanged = Signal(bool)
  #def allowsInternetAccess(self): return to_bool(self.value('InternetEnabled', True))
  #def setAllowsInternetAccess(self, value):
  #  if value != self.allowsInternetAccess():
  #    self.setValue('InternetEnabled', value)
  #    self.allowsInternetAccessChanged.emit(value)

  allowsMachineTranslationChanged = Signal(bool)
  def allowsMachineTranslation(self): return to_bool(self.value('MachineTranslationEnabled', True))
  def setAllowsMachineTranslation(self, value):
    if value != self.allowsMachineTranslation():
      self.setValue('MachineTranslationEnabled', value)
      self.allowsMachineTranslationChanged.emit(value)

  allowsUserCommentChanged = Signal(bool)
  def allowsUserComment(self): return to_bool(self.value('UserCommentEnabled', True))
  def setAllowsUserComment(self, value):
    if value != self.allowsUserComment():
      self.setValue('UserCommentEnabled', value)
      self.allowsUserCommentChanged.emit(value)

  #allowsTextToSpeechChanged = Signal(bool)
  #def allowsTextToSpeech(self): return to_bool(self.value('TextToSpeechEnabled', True))
  #def setAllowsTextToSpeech(self, value):
  #  if value != self.allowsTextToSpeech():
  #    self.setValue('TextToSpeechEnabled', value)
  #    self.allowsTextToSpeechChanged.emit(value)

  ## Shortcuts ##

  ttsHotkeyEnabledChanged = Signal(bool)
  def isTtsHotkeyEnabled(self):
    return to_bool(self.value('TTSHotkeyEnabled', True))
  def setTtsHotkeyEnabled(self, value):
    if value != self.isTtsHotkeyEnabled():
      self.setValue('TTSHotkeyEnabled', value)
      self.ttsHotkeyEnabledChanged.emit(value)

  ttsHotkeyChanged = Signal(str)
  def ttsHotkey(self):
    return self.value('TTSHotkey', 'mouse right') # right click by default
  def setTtsHotkey(self, value):
    if value != self.ttsHotkey():
      self.setValue('TTSHotkey', value)
      self.ttsHotkeyChanged.emit(value)

  # Hot key to enable/disable text extraction
  textHotkeyEnabledChanged = Signal(bool)
  def isTextHotkeyEnabled(self):
    return to_bool(self.value('TextHotkeyEnabled', True))
  def setTextHotkeyEnabled(self, value):
    if value != self.isTextHotkeyEnabled():
      self.setValue('TextHotkeyEnabled', value)
      self.textHotkeyEnabledChanged.emit(value)

  textHotkeyChanged = Signal(str)
  def textHotkey(self):
    return self.value('TextHotkey', 'mouse middle') # middle click by default
  def setTextHotkey(self, value):
    if value != self.textHotkey():
      self.setValue('TextHotkey', value)
      self.textHotkeyChanged.emit(value)

  # Take snapshot
  grabHotkeyEnabledChanged = Signal(bool)
  def isGrabHotkeyEnabled(self):
    return to_bool(self.value('GrabHotkeyEnabled', True))
  def setGrabHotkeyEnabled(self, value):
    if value != self.isGrabHotkeyEnabled():
      self.setValue('GrabHotkeyEnabled', value)
      self.grabHotkeyEnabledChanged.emit(value)

  grabHotkeyChanged = Signal(str)
  def grabHotkey(self):
    return self.value('GrabHotkey', 'Alt\nS') # alt + s, \n = hkman.HOTKEY_DELIM
  def setGrabHotkey(self, value):
    if value != self.grabHotkey():
      self.setValue('GrabHotkey', value)
      self.grabHotkeyChanged.emit(value)

  # OCR
  ocrHotkeyEnabledChanged = Signal(bool)
  def isOcrHotkeyEnabled(self):
    return to_bool(self.value('OCRHotkeyEnabled')) # disable hotkey by default
  def setOcrHotkeyEnabled(self, value):
    if value != self.isOcrHotkeyEnabled():
      self.setValue('OCRHotkeyEnabled', value)
      self.ocrHotkeyEnabledChanged.emit(value)

  ocrHotkeyChanged = Signal(str)
  def ocrHotkey(self):
    return self.value('OCRHotkey', 'Alt\nO') # alt + o, \n = hkman.HOTKEY_DELIM
  def setOcrHotkey(self, value):
    if value != self.ocrHotkey():
      self.setValue('OCRHotkey', value)
      self.ocrHotkeyChanged.emit(value)

  # Speech recognition
  srHotkeyEnabledChanged = Signal(bool)
  def isSrHotkeyEnabled(self):
    return to_bool(self.value('SpeechRecognitionHotkeyEnabled')) # disable hotkey by default
  def setSrHotkeyEnabled(self, value):
    if value != self.isSrHotkeyEnabled():
      self.setValue('SpeechRecognitionHotkeyEnabled', value)
      self.srHotkeyEnabledChanged.emit(value)

  srHotkeyChanged = Signal(str)
  def srHotkey(self):
    return self.value('SpeechRecognitionHotkey', 'Alt\nR') # alt + r, \n = hkman.HOTKEY_DELIM
  def setSrHotkey(self, value):
    if value != self.srHotkey():
      self.setValue('SpeechRecognitionHotkey', value)
      self.srHotkeyChanged.emit(value)

  ## Speech recognition ##

  audioDeviceIndexChanged = Signal(int)
  def audioDeviceIndex(self):
    return to_int(self.value('AudioDeviceIndex', 0))
  def setAudioDeviceIndex(self, value):
    if value != self.audioDeviceIndex():
      self.setValue('AudioDeviceIndex', value)
      self.audioDeviceIndexChanged.emit(value)

  speechRecognitionLanguageChanged = Signal(str)
  def speechRecognitionLanguage(self):
    return self.value('SpeechRecognitionLanguage', 'ja')
  def setSpeechRecognitionLanguage(self, value):
    if value != self.speechRecognitionLanguage():
      self.setValue('SpeechRecognitionLanguage', value)
      self.speechRecognitionLanguageChanged.emit(value)

  ## TTS ##

  speaksGameTextChanged = Signal(bool)
  def speaksGameText(self):
    return to_bool(self.value('SpeakGameText', True))
  def setSpeaksGameText(self, value):
    if value != self.speaksGameText():
      self.setValue('SpeakGameText', value)
      self.speaksGameTextChanged.emit(value)

  voiceCharacterEnabledChanged = Signal(bool)
  def isVoiceCharacterEnabled(self):
    return to_bool(self.value('VoiceCharacter', True))
  def setVoiceCharacterEnabled(self, value):
    if value != self.isVoiceCharacterEnabled():
      self.setValue('VoiceCharacter', value)
      self.voiceCharacterEnabledChanged.emit(value)

  def isSubtitleVoiceEnabled(self): return to_bool(self.value('SubtitleVoice'))

  #googleTtsEnabledChanged = Signal(bool)
  #def isGoogleTtsEnabled(self):
  #  return to_bool(self.value('GoogleTTSEnabled'))
  #def setGoogleTtsEnabled(self, value):
  #  if value != self.isGoogleTtsEnabled():
  #    self.setValue('GoogleTTSEnabled', value)
  #    self.googleTtsEnabledChanged.emit(value)

  #windowsTtsSpeedChanged = Signal(int)
  #def windowsTtsSpeed(self):
  #  return to_int(self.value('WindowsTTSSpeed', 0))
  #def setWindowsTtsSpeed(self, value):
  #  if value != self.windowsTtsSpeed():
  #    self.setValue('WindowsTTSSpeed', value)
  #    self.windowsTtsSpeedChanged.emit(value)

  #windowsTtsEnabledChanged = Signal(bool)
  #def isWindowsTtsEnabled(self):
  #  return to_bool(self.value('WindowsTTSEnabled'))
  #def setWindowsTtsEnabled(self, value):
  #  if value != self.isWindowsTtsEnabled():
  #    self.setValue('WindowsTTSEnabled', value)
  #    self.windowsTtsEnabledChanged.emit(value)

  #windowsTtsEngineChanged = Signal(unicode)
  #def windowsTtsEngine(self):
  #  return to_unicode(self.value('WindowsTTS'))
  #def setWindowsTtsEngine(self, value):
  #  if value != self.windowsTtsEngine():
  #    self.setValue('WindowsTTS', value)
  #    self.windowsTtsEngineChanged.emit(value)

  #maleVoiceJaChanged = Signal(unicode)
  #def maleVoiceJa(self):
  #  return to_unicode(self.value('MaleVoiceJa'))
  #def setMaleVoiceJa(self, value):
  #  if value != self.maleVoiceJa():
  #    self.setValue('MaleVoiceJa', value)
  #    self.maleVoiceJaChanged.emit(value)

  #femaleVoiceJaChanged = Signal(unicode)
  #def femaleVoiceJa(self):
  #  return to_unicode(self.value('FemaleVoiceJa'))
  #def setFemaleVoiceJa(self, value):
  #  if value != self.femaleVoiceJa():
  #    self.setValue('FemaleVoiceJa', value)
  #    self.femaleVoiceJaChanged.emit(value)

  #maleVoiceChanged = Signal(unicode)
  #def maleVoice(self):
  #  return to_unicode(self.value('MaleVoice'))
  #def setMaleVoice(self, value):
  #  if value != self.maleVoice():
  #    self.setValue('MaleVoice', value)
  #    self.maleVoiceChanged.emit(value)

  #femaleVoiceChanged = Signal(unicode)
  #def femaleVoice(self):
  #  return to_unicode(self.value('FemaleVoice'))
  #def setFemaleVoice(self, value):
  #  if value != self.femaleVoice():
  #    self.setValue('FemaleVoice', value)
  #    self.femaleVoiceChanged.emit(value)

  ttsEngineChanged = Signal(unicode)
  def ttsEngine(self):
    return to_unicode(self.value('TTSEngine', 'baidu')) # Baidu by default
  def setTtsEngine(self, value):
    if value != self.ttsEngine():
      self.setValue('TTSEngine', value)
      self.ttsEngineChanged.emit(value)

  #googleTtsLanguageChanged = Signal(str)
  #def googleTtsLanguage(self):
  #  return self.value('GoogleTTSLanguage', 'ja')
  #def setGoogleTtsLanguage(self, value):
  #  if value != self.googleTtsLanguage():
  #    self.setValue('GoogleTTSLanguage', value)
  #    self.googleTtsLanguageChanged.emit(value)

  zunkoLocationChanged = Signal(unicode)
  def zunkoLocation(self):
    return to_unicode(self.value('ZunkoLocation'))
  def setZunkoLocation(self, value):
    if value != self.zunkoLocation():
      self.setValue('ZunkoLocation', value)
      self.zunkoLocationChanged.emit(value)

  yukariLocationChanged = Signal(unicode)
  def yukariLocation(self):
    return to_unicode(self.value('YukariLocation'))
  def setYukariLocation(self, value):
    if value != self.yukariLocation():
      self.setValue('YukariLocation', value)
      self.yukariLocationChanged.emit(value)

  def ttsGenders(self):
    """
    @return  {str ttskey:str 'f' or 'm'}
    """
    return to_dict(self.value('TTSGenders'))
  def setTtsGenders(self, value): self.setValue('TTSGenders', value)

  def ttsSpeeds(self):
    """
    @return  {str ttskey:int speed}
    """
    return to_dict(self.value('TTSSpeeds'))
  def setTtsSpeeds(self, value): self.setValue('TTSSpeeds', value)

  def ttsVolumes(self):
    """
    @return  {str ttskey:int volume}
    """
    return to_dict(self.value('TTSVolumes'))
  def setTtsVolumes(self, value): self.setValue('TTSVolumes', value)

  def ttsPitches(self):
    """
    @return  {str ttskey:int pitch}
    """
    return to_dict(self.value('TTSPitches'))
  def setTtsPitches(self, value): self.setValue('TTSPitches', value)

  ## Game launcher ##

  def isGameDetectionEnabled(self): return to_bool(self.value('GameDetectionEnabled', True))
  def setGameDetectionEnabled(self, value): self.setValue('GameDetectionEnabled', value)

  def isHookCodeEnabled(self):
    #return to_bool(self.value('HookCodeEnabled', True))
    return True # Always enable it
  def setHookCodeEnabled(self, value): self.setValue('HookCodeEnabled', value)

  # Max length of the hooked game text
  gameTextCapacityChanged = Signal(int)
  def gameTextCapacity(self):
    return max(20,
        to_int(self.value('GameTextCapacity', config.SETTINGS_TEXT_CAPACITY)))

  ## Dictionaries ##

  #caboChaEnabledChanged = Signal(bool)
  #def isCaboChaEnabled(self): return to_bool(self.value('CaboChaEnabled')) # Disable cabocha by default as it need dictionary
  #def setCaboChaEnabled(self, v):
  #  if v != self.isCaboChaEnabled():
  #    self.setValue('CaboChaEnabled', v)
  #    self.caboChaEnabledChanged.emit(v)

  #meCabEnabledChanged = Signal(bool)
  #def isMeCabEnabled(self): return bool(self.meCabDictionary())

  # {ipadic, unidic, unidic-mlj}
  #meCabDictionaryChanged = Signal(str)
  #def meCabDictionary(self): return self.value('MeCabDictionary', '')
  #def setMeCabDictionary(self, v):
  #  if v != self.meCabDictionary():
  #    self.setValue('MeCabDictionary', v)
  #    self.meCabEnabledChanged.emit(bool(v)) # This must before mecab dictionary is set
  #    self.meCabDictionaryChanged.emit(v)

  def isEdictEnabled(self): return to_bool(self.value('EdictEnabled'))
  def setEdictEnabled(self, t):
    if t != self.isEdictEnabled():
      self.setValue('EdictEnabled', t)
      self._updateDictionaryEnabled()

  meCabEdictEnabledChanged = Signal(bool)
  def isMeCabEdictEnabled(self): return to_bool(self.value('MeCabEdict'))
  def setMeCabEdictEnabled(self, t):
    if t != self.isMeCabEdictEnabled():
      self.setValue('MeCabEdict', t)
      self.meCabEdictEnabledChanged.emit(t)

  def isKojienEnabled(self): return to_bool(self.value('KojienEnabled'))
  def setKojienEnabled(self, t):
    if t != self.isKojienEnabled():
      self.setValue('KojienEnabled', t)
      self._updateDictionaryEnabled()

  def isDaijirinEnabled(self): return to_bool(self.value('DaijirinEnabled'))
  def setDaijirinEnabled(self, t):
    if t != self.isDaijirinEnabled():
      self.setValue('DaijirinEnabled', t)
      self._updateDictionaryEnabled()

  def isWadokuEnabled(self): return to_bool(self.value('WadokuEnabled'))
  def setWadokuEnabled(self, t):
    if t != self.isWadokuEnabled():
      self.setValue('WadokuEnabled', t)
      self._updateDictionaryEnabled()

  def isZhongriEnabled(self): return to_bool(self.value('ZhongriEnabled'))
  def setZhongriEnabled(self, t):
    if t != self.isZhongriEnabled():
      self.setValue('ZhongriEnabled', t)
      self._updateDictionaryEnabled()

  japaneseRubyLanguagesChanged = Signal(list)
  def japaneseRubyLanguages(self): return to_list(self.value('JapaneseRubyLanguages'))
  def setJapaneseRubyLanguages(self, value):
    if value != self.japaneseRubyLanguages():
      self.setValue('JapaneseRubyLanguages', value)
      self.japaneseRubyLanguagesChanged.emit(value)

  japaneseDictionaryEnabledChanged = Signal(bool)
  def isJapaneseDictionaryEnabled(self):
    return (
        self.isEdictEnabled() or
        self.isZhongriEnabled() or
        self.isKojienEnabled() or
        self.isDaijirinEnabled() or
        self.isWadokuEnabled() or
        self.isJMDictFrEnabled() or
        self.isJMDictRuEnabled() or
        self.isJMDictNlEnabled() or
        self.isLingoesJaZhEnabled() or
        self.isLingoesJaZhGbkEnabled() or
        self.isLingoesJaKoEnabled() or
        self.isLingoesJaEnEnabled() or
        self.isStardictJaViEnabled() or
        self.isStardictHanjaEnabled())
  def _updateDictionaryEnabled(self):
    self.japaneseDictionaryEnabledChanged.emit(self.isJapaneseDictionaryEnabled())

  def kojienLocation(self): return to_unicode(self.value('KojienLocation'))
  def setKojienLocation(self, v): self.setValue('KojienLocation', v)

  def daijirinLocation(self): return to_unicode(self.value('DaijirinLocation'))
  def setDaijirinLocation(self, v): self.setValue('DaijirinLocation', v)

  #def wadokuLocation(self): return to_unicode(self.value('WadokuLocation'))
  #def setWadokuLocation(self, v): self.setValue('WadokuLocation', v)

  def zhongriLocation(self): return to_unicode(self.value('ZhongriLocation'))
  def setZhongriLocation(self, v): self.setValue('ZhongriLocation', v)

  def isKojienEnabled(self): return to_bool(self.value('KojienEnabled'))
  def setKojienEnabled(self, v):
    if v != self.isKojienEnabled():
      self.setValue('KojienEnabled', v)
      self._updateDictionaryEnabled()

  def isDaijirinEnabled(self): return to_bool(self.value('DaijirinEnabled'))
  def setDaijirinEnabled(self, v):
    if v != self.isDaijirinEnabled():
      self.setValue('DaijirinEnabled', v)
      self._updateDictionaryEnabled()

  def isWadokuEnabled(self): return to_bool(self.value('WadokuEnabled'))
  def setWadokuEnabled(self, v):
    if v != self.isWadokuEnabled():
      self.setValue('WadokuEnabled', v)
      self._updateDictionaryEnabled()

  def isLingoesJaZhEnabled(self): return to_bool(self.value('LingoesJaZh'))
  def setLingoesJaZhEnabled(self, v):
    if v != self.isLingoesJaZhEnabled():
      self.setValue('LingoesJaZh', v)
      self._updateDictionaryEnabled()

  def isLingoesJaZhGbkEnabled(self): return to_bool(self.value('LingoesJaZhGbk'))
  def setLingoesJaZhGbkEnabled(self, v):
    if v != self.isLingoesJaZhGbkEnabled():
      self.setValue('LingoesJaZhGbk', v)
      self._updateDictionaryEnabled()

  def isLingoesJaKoEnabled(self): return to_bool(self.value('LingoesJaKo'))
  def setLingoesJaKoEnabled(self, v):
    if v != self.isLingoesJaKoEnabled():
      self.setValue('LingoesJaKo', v)
      self._updateDictionaryEnabled()

  def isLingoesJaEnEnabled(self): return to_bool(self.value('LingoesJaEn'))
  def setLingoesJaEnEnabled(self, v):
    if v != self.isLingoesJaEnEnabled():
      self.setValue('LingoesJaEn', v)
      self._updateDictionaryEnabled()

  def isStardictJaViEnabled(self): return to_bool(self.value('StardictJaVi'))
  def setStardictJaViEnabled(self, v):
    if v != self.isStardictJaViEnabled():
      self.setValue('StardictJaVi', v)
      self._updateDictionaryEnabled()

  def isStardictHanjaEnabled(self): return to_bool(self.value('StardictHanja'))
  def setStardictHanjaEnabled(self, v):
    if v != self.isStardictHanjaEnabled():
      self.setValue('StardictHanja', v)
      self._updateDictionaryEnabled()

  def isLingoesDictionaryEnabled(self, name):
    if name == 'ja-zh':
      return self.isLingoesJaZhEnabled()
    elif name == 'ja-zh-gbk':
      return self.isLingoesJaZhGbkEnabled()
    elif name == 'ja-ko':
      return self.isLingoesJaKoEnabled()
    elif name == 'ja-en':
      return self.isLingoesJaEnEnabled()
    #elif name == 'ja-vi':
    #  return self.isLingoesJaViEnabled()
    return False

  def setLingoesDictionaryEnabled(self, name, v):
    if name == 'ja-zh':
      self.setLingoesJaZhEnabled(v)
    elif name == 'ja-zh-gbk':
      self.setLingoesJaZhGbkEnabled(v)
    elif name == 'ja-ko':
      self.setLingoesJaKoEnabled(v)
    elif name == 'ja-en':
      self.setLingoesJaEnEnabled(v)
    #elif name == 'ja-vi':
    #  self.setLingoesJaViEnabled(v)

  def isStardictDictionaryEnabled(self, name):
    if name == 'ja-vi':
      return self.isStardictJaViEnabled()
    elif name == 'hanja':
      return self.isStardictHanjaEnabled()
    return False

  def setStardictDictionaryEnabled(self, name, v):
    if name == 'ja-vi':
      self.setStardictJaViEnabled(v)
    elif name == 'hanja':
      self.setStardictHanjaEnabled(v)

  # Hanzi

  def isKanjiRadicalEnabled(self): return to_bool(self.value('KanjiRadical'))
  def setKanjiRadicalEnabled(self, t): self.setValue('KanjiRadical', t)

  kanjiHanjaEnabledChanged = Signal(bool)
  def isKanjiHanjaEnabled(self): return to_bool(self.value('KanjiHanja'))
  def setKanjiHanjaEnabled(self, value):
    if value != self.isKanjiHanjaEnabled():
      self.setValue('KanjiHanja', value)
      self.kanjiHanjaEnabledChanged.emit(value)

  # Locations

  grabLocationChanged = Signal(unicode)
  def grabLocation(self):
    return to_unicode(self.value('GrabLocation'))
  def setGrabLocation(self, value):
    if value != self.grabLocation():
      self.setValue('GrabLocation', value)
      self.grabLocationChanged.emit(value)

  # KanjiDic

  kanjiDicLanguagesChanged = Signal(unicode)
  def kanjiDicLanguages(self): return self.value('KanjiDicLanguages') or ''
  def setKanjiDicLanguages(self, v):
    if v != self.kanjiDicLanguages():
      self.setValue('KanjiDicLanguages', v)
      self.kanjiDicLanguagesChanged.emit(v)

  def setKanjiDicLanguageList(self, v): self.setKanjiDicLanguages(list2string(v)) # [unicode] ->
  def kanjiDicLanguageList(self): return string2list(self.kanjiDicLanguages()) # -> [unicode]
  #def removeKanjiDicLanguage(self, v):
  #  l = self.kanjiDicLanguageList()
  #  if l and v in l:
  #    l.remove(v)
  #    self.setKanjiDicLanguageList(v)

  # JMDict

  def isJMDictFrEnabled(self): return to_bool(self.value('JMDictFr'))
  def setJMDictFrEnabled(self, v):
    if v != self.isJMDictFrEnabled():
      self.setValue('JMDictFr', v)
      self._updateDictionaryEnabled()

  def isJMDictRuEnabled(self): return to_bool(self.value('JMDictRu'))
  def setJMDictRuEnabled(self, v):
    if v != self.isJMDictRuEnabled():
      self.setValue('JMDictRu', v)
      self._updateDictionaryEnabled()

  def isJMDictRuEnabledJM(self): return to_bool(self.value('JMDictRuJM'))
  def setJMDictRuEnabledJM(self, v):
    if v != self.isJMDictRuEnabledJM():
      self.setValue('JMDictRuJM', v)
      self._updateDictionaryEnabled()

  def isJMDictNlEnabled(self): return to_bool(self.value('JMDictNl'))
  def setJMDictNlEnabled(self, v):
    if v != self.isJMDictNlEnabled():
      self.setValue('JMDictNl', v)
      self._updateDictionaryEnabled()

  def isJMDictEnabled(self, lang):
    if lang == 'fr':
      return self.isJMDictFrEnabled()
    elif lang == 'ru':
      return self.isJMDictRuEnabled()
    elif lang == 'nl':
      return self.isJMDictNlEnabled()
    else:
      return False

  def setJMDictEnabled(self, lang, v):
    if lang == 'fr':
      self.setJMDictFrEnabled(v)
    elif lang == 'ru':
      self.setJMDictRuEnabled(v)
    elif lang == 'nl':
      self.setJMDictNlEnabled(v)

  ## Machine translation ##

  # "atlas", or "infoseek", or "jbeijing"
  #machineTranslatorChanged = Signal(unicode)
  #def machineTranslator(self):
  #  return self.value('MachineTranslator', 'infoseek')
  #def setMachineTranslator(self, value):
  #  if value != self.machineTranslator():
  #    self.setValue('MachineTranslator', value)
  #    self.machineTranslatorChanged.emit(value)

  #def isMsimeCorrectionEnabled(self): return to_bool(self.value('MsimeCorrectionEnabled'))
  #def setMsimeCorrectionEnabled(self, value): self.setValue('MsimeCorrectionEnabled', value)

  #msimeParserEnabledChanged = Signal(bool)
  #def isMsimeParserEnabled(self):
  #  return to_bool(self.value('MsimeParserEnabled'))
  #def setMsimeParserEnabled(self, value):
  #  if value != self.isMsimeParserEnabled():
  #    self.setValue('MsimeParserEnabled', value)
  #    self.msimeParserEnabledChanged.emit(value)

  def retranslatorSettings(self): return parse_json(self.value('Retranslator'))
  def setRetranslatorSettings(self, v): return self.setValue('Retranslator', unparse_json(v))

  def jbeijingLocation(self):
    return to_unicode(self.value('JBeijingLocation'))
  def setJBeijingLocation(self, path):
    self.setValue('JBeijingLocation', path)

  def fastaitLocation(self):
    return to_unicode(self.value('FastAITLocation'))
  def setFastaitLocation(self, path):
    self.setValue('FastAITLocation', path)

  def ezTransLocation(self):
    return to_unicode(self.value('ezTransLocation'))
  def setEzTransLocation(self, path):
    self.setValue('ezTransLocation', path)

  def transcatLocation(self):
    return to_unicode(self.value('TransCATLocation'))
  def setTranscatLocation(self, path):
    self.setValue('TransCATLocation', path)

  def dreyeLocation(self):
    return to_unicode(self.value('DreyeLocation'))
  def setDreyeLocation(self, path):
    self.setValue('DreyeLocation', path)

  def atlasLocation(self):
    return to_unicode(self.value('AtlasLocation'))
  def setAtlasLocation(self, path):
    self.setValue('AtlasLocation', path)

  def lecLocation(self):
    return to_unicode(self.value('LecLocation'))
  def setLecLocation(self, path):
    self.setValue('LecLocation', path)

  infoseekEnabledChanged = Signal(bool)
  def isInfoseekEnabled(self):
    return to_bool(self.value('InfoseekEnabled'))
  def setInfoseekEnabled(self, value):
    if value != self.isInfoseekEnabled():
      self.setValue('InfoseekEnabled', value)
      self.infoseekEnabledChanged.emit(value)

  infoseekRubyEnabledChanged = Signal(bool)
  def isInfoseekRubyEnabled(self):
    return to_bool(self.value('InfoseekRubyEnabled'))
  def setInfoseekRubyEnabled(self, value):
    if value != self.isInfoseekRubyEnabled():
      self.setValue('InfoseekRubyEnabled', value)
      self.infoseekRubyEnabledChanged.emit(value)

  exciteEnabledChanged = Signal(bool)
  def isExciteEnabled(self):
    return to_bool(self.value('ExciteEnabled'))
  def setExciteEnabled(self, value):
    if value != self.isExciteEnabled():
      self.setValue('ExciteEnabled', value)
      self.exciteEnabledChanged.emit(value)

  babylonEnabledChanged = Signal(bool)
  def isBabylonEnabled(self):
    return to_bool(self.value('BabylonEnabled'))
  def setBabylonEnabled(self, value):
    if value != self.isBabylonEnabled():
      self.setValue('BabylonEnabled', value)
      self.babylonEnabledChanged.emit(value)

  systranEnabledChanged = Signal(bool)
  def isSystranEnabled(self):
    return to_bool(self.value('SystranEnabled'))
  def setSystranEnabled(self, value):
    if value != self.isSystranEnabled():
      self.setValue('SystranEnabled', value)
      self.systranEnabledChanged.emit(value)

  niftyEnabledChanged = Signal(bool)
  def isNiftyEnabled(self):
    return to_bool(self.value('NiftyEnabled'))
  def setNiftyEnabled(self, value):
    if value != self.isNiftyEnabled():
      self.setValue('NiftyEnabled', value)
      self.niftyEnabledChanged.emit(value)

  googleEnabledChanged = Signal(bool)
  def isGoogleEnabled(self):
    return to_bool(self.value('GoogleEnabled'))
  def setGoogleEnabled(self, value):
    if value != self.isGoogleEnabled():
      self.setValue('GoogleEnabled', value)
      self.googleEnabledChanged.emit(value)

  googleRubyEnabledChanged = Signal(bool)
  def isGoogleRubyEnabled(self):
    return to_bool(self.value('GoogleRubyEnabled'))
  def setGoogleRubyEnabled(self, value):
    if value != self.isGoogleRubyEnabled():
      self.setValue('GoogleRubyEnabled', value)
      self.googleRubyEnabledChanged.emit(value)

  bingEnabledChanged = Signal(bool)
  def isBingEnabled(self):
    return to_bool(self.value('BingEnabled', True)) # the only one enabled
  def setBingEnabled(self, value):
    if value != self.isBingEnabled():
      self.setValue('BingEnabled', value)
      self.bingEnabledChanged.emit(value)

  bingRubyEnabledChanged = Signal(bool)
  def isBingRubyEnabled(self):
    return to_bool(self.value('BingRubyEnabled'))
  def setBingRubyEnabled(self, value):
    if value != self.isBingRubyEnabled():
      self.setValue('BingRubyEnabled', value)
      self.bingRubyEnabledChanged.emit(value)

  naverEnabledChanged = Signal(bool)
  def isNaverEnabled(self):
    return to_bool(self.value('NaverEnabled'))
  def setNaverEnabled(self, value):
    if value != self.isNaverEnabled():
      self.setValue('NaverEnabled', value)
      self.naverEnabledChanged.emit(value)

  naverRubyEnabledChanged = Signal(bool)
  def isNaverRubyEnabled(self):
    return to_bool(self.value('NaverRubyEnabled'))
  def setNaverRubyEnabled(self, value):
    if value != self.isNaverRubyEnabled():
      self.setValue('NaverRubyEnabled', value)
      self.naverRubyEnabledChanged.emit(value)

  baiduEnabledChanged = Signal(bool)
  def isBaiduEnabled(self):
    return to_bool(self.value('BaiduEnabled'))
  def setBaiduEnabled(self, value):
    if value != self.isBaiduEnabled():
      self.setValue('BaiduEnabled', value)
      self.baiduEnabledChanged.emit(value)

  baiduRubyEnabledChanged = Signal(bool)
  def isBaiduRubyEnabled(self):
    return to_bool(self.value('BaiduRubyEnabled'))
  def setBaiduRubyEnabled(self, value):
    if value != self.isBaiduRubyEnabled():
      self.setValue('BaiduRubyEnabled', value)
      self.baiduRubyEnabledChanged.emit(value)

  youdaoEnabledChanged = Signal(bool)
  def isYoudaoEnabled(self):
    return to_bool(self.value('YoudaoEnabled'))
  def setYoudaoEnabled(self, value):
    if value != self.isYoudaoEnabled():
      self.setValue('YoudaoEnabled', value)
      self.youdaoEnabledChanged.emit(value)

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

  machineTranslatorChanged = Signal()

  hanVietEnabledChanged = Signal(bool)
  def isHanVietEnabled(self):
    return to_bool(self.value('HanVietEnabled'))
  def setHanVietEnabled(self, value):
    if value != self.isHanVietEnabled():
      self.setValue('HanVietEnabled', value)
      self.hanVietEnabledChanged.emit(value)
      self.machineTranslatorChanged.emit()

  hanVietRubyEnabledChanged = Signal(bool)
  def isHanVietRubyEnabled(self):
    return to_bool(self.value('HanVietRubyEnabled'))
  def setHanVietRubyEnabled(self, value):
    if value != self.isHanVietRubyEnabled():
      self.setValue('HanVietRubyEnabled', value)
      self.hanVietRubyEnabledChanged.emit(value)

  atlasEnabledChanged = Signal(bool)
  def isAtlasEnabled(self):
    return to_bool(self.value('AtlasEnabled'))
  def setAtlasEnabled(self, value):
    if value != self.isAtlasEnabled():
      self.setValue('AtlasEnabled', value)
      self.atlasEnabledChanged.emit(value)
      self.machineTranslatorChanged.emit()

  lecEnabledChanged = Signal(bool)
  def isLecEnabled(self):
    return to_bool(self.value('LecEnabled'))
  def setLecEnabled(self, value):
    if value != self.isLecEnabled():
      self.setValue('LecEnabled', value)
      self.lecEnabledChanged.emit(value)
      self.machineTranslatorChanged.emit()

  vtransEnabledChanged = Signal(bool)
  def isVTransEnabled(self):
    return to_bool(self.value('VTransEnabled'))
  def setVTransEnabled(self, value):
    if value != self.isVTransEnabled():
      self.setValue('VTransEnabled', value)
      self.vtransEnabledChanged.emit(value)
      self.machineTranslatorChanged.emit()

  romajiEnabledChanged = Signal(bool)
  def isRomajiEnabled(self):
    return to_bool(self.value('RomajiEnabled'))
  def setRomajiEnabled(self, value):
    if value != self.isRomajiEnabled():
      self.setValue('RomajiEnabled', value)
      self.romajiEnabledChanged.emit(value)
      self.machineTranslatorChanged.emit()

  romajiRubyTypeChanged = Signal(unicode)
  def romajiRubyType(self): return self.value('RomajiRubyType', 'romaji')
  def setRomajiRubyType(self, value):
    if value != self.romajiRubyType():
      self.setValue('RomajiRubyType', value)
      self.romajiRubyTypeChanged.emit(value)

  jbeijingEnabledChanged = Signal(bool)
  def isJBeijingEnabled(self):
    return to_bool(self.value('JBeijingEnabled'))
  def setJBeijingEnabled(self, value):
    if value != self.isJBeijingEnabled():
      self.setValue('JBeijingEnabled', value)
      self.jbeijingEnabledChanged.emit(value)
      self.machineTranslatorChanged.emit()

  fastaitEnabledChanged = Signal(bool)
  def isFastaitEnabled(self):
    return to_bool(self.value('FastAITEnabled'))
  def setFastaitEnabled(self, value):
    if value != self.isFastaitEnabled():
      self.setValue('FastAITEnabled', value)
      self.fastaitEnabledChanged.emit(value)
      self.machineTranslatorChanged.emit()

  dreyeEnabledChanged = Signal(bool)
  def isDreyeEnabled(self):
    return to_bool(self.value('DreyeEnabled'))
  def setDreyeEnabled(self, value):
    if value != self.isDreyeEnabled():
      self.setValue('DreyeEnabled', value)
      self.dreyeEnabledChanged.emit(value)
      self.machineTranslatorChanged.emit()

  ezTransEnabledChanged = Signal(bool)
  def isEzTransEnabled(self):
    return to_bool(self.value('ezTransEnabled'))
  def setEzTransEnabled(self, value):
    if value != self.isEzTransEnabled():
      self.setValue('ezTransEnabled', value)
      self.ezTransEnabledChanged.emit(value)
      self.machineTranslatorChanged.emit()

  ehndEnabledChanged = Signal(bool)
  def isEhndEnabled(self):
    return to_bool(self.value('EhndEnabled', True))
  def setEhndEnabled(self, value):
    if value != self.isEhndEnabled():
      self.setValue('EhndEnabled', value)
      self.ehndEnabledChanged.emit(value)

  transcatEnabledChanged = Signal(bool)
  def isTranscatEnabled(self):
    return to_bool(self.value('TransCATEnabled'))
  def setTranscatEnabled(self, value):
    if value != self.isTranscatEnabled():
      self.setValue('TransCATEnabled', value)
      self.transcatEnabledChanged.emit(value)
      self.machineTranslatorChanged.emit()

  ## Translation options ##

  atlasScriptEnabledChanged = Signal(bool)
  def isAtlasScriptEnabled(self): return to_bool(self.value('AtlasScriptEnabled', True))
  def setAtlasScriptEnabled(self, value):
    if value != self.isAtlasScriptEnabled():
      self.setValue('AtlasScriptEnabled', value)
      self.atlasScriptEnabledChanged.emit(value)

  lecScriptEnabledChanged = Signal(bool)
  def isLecScriptEnabled(self): return to_bool(self.value('LecScriptEnabled', True))
  def setLecScriptEnabled(self, value):
    if value != self.isLecScriptEnabled():
      self.setValue('LecScriptEnabled', value)
      self.lecScriptEnabledChanged.emit(value)

  lecOnlineScriptEnabledChanged = Signal(bool)
  def isLecOnlineScriptEnabled(self): return to_bool(self.value('LecOnlineScriptEnabled', True))
  def setLecOnlineScriptEnabled(self, value):
    if value != self.isLecOnlineScriptEnabled():
      self.setValue('LecOnlineScriptEnabled', value)
      self.lecOnlineScriptEnabledChanged.emit(value)

  googleScriptEnabledChanged = Signal(bool)
  def isGoogleScriptEnabled(self): return to_bool(self.value('GoogleScriptEnabled', True))
  def setGoogleScriptEnabled(self, value):
    if value != self.isGoogleScriptEnabled():
      self.setValue('GoogleScriptEnabled', value)
      self.googleScriptEnabledChanged.emit(value)

  bingScriptEnabledChanged = Signal(bool)
  def isBingScriptEnabled(self): return to_bool(self.value('BingScriptEnabled', True))
  def setBingScriptEnabled(self, value):
    if value != self.isBingScriptEnabled():
      self.setValue('BingScriptEnabled', value)
      self.bingScriptEnabledChanged.emit(value)

  infoseekScriptEnabledChanged = Signal(bool)
  def isInfoseekScriptEnabled(self): return to_bool(self.value('InfoseekScriptEnabled', True))
  def setInfoseekScriptEnabled(self, value):
    if value != self.isInfoseekScriptEnabled():
      self.setValue('InfoseekScriptEnabled', value)
      self.infoseekScriptEnabledChanged.emit(value)

  exciteScriptEnabledChanged = Signal(bool)
  def isExciteScriptEnabled(self): return to_bool(self.value('ExciteScriptEnabled', True))
  def setExciteScriptEnabled(self, value):
    if value != self.isExciteScriptEnabled():
      self.setValue('ExciteScriptEnabled', value)
      self.exciteScriptEnabledChanged.emit(value)

  babylonScriptEnabledChanged = Signal(bool)
  def isBabylonScriptEnabled(self): return to_bool(self.value('BabylonScriptEnabled', True))
  def setBabylonScriptEnabled(self, value):
    if value != self.isBabylonScriptEnabled():
      self.setValue('BabylonScriptEnabled', value)
      self.babylonScriptEnabledChanged.emit(value)

  systranScriptEnabledChanged = Signal(bool)
  def isSystranScriptEnabled(self): return to_bool(self.value('SystranScriptEnabled', True))
  def setSystranScriptEnabled(self, value):
    if value != self.isSystranScriptEnabled():
      self.setValue('SystranScriptEnabled', value)
      self.systranScriptEnabledChanged.emit(value)

  niftyScriptEnabledChanged = Signal(bool)
  def isNiftyScriptEnabled(self): return to_bool(self.value('NiftyScriptEnabled', True))
  def setNiftyScriptEnabled(self, value):
    if value != self.isNiftyScriptEnabled():
      self.setValue('NiftyScriptEnabled', value)
      self.niftyScriptEnabledChanged.emit(value)

  transruScriptEnabledChanged = Signal(bool)
  def isTransruScriptEnabled(self): return to_bool(self.value('TransruScriptEnabled', True))
  def setTransruScriptEnabled(self, value):
    if value != self.isTransruScriptEnabled():
      self.setValue('TransruScriptEnabled', value)
      self.transruScriptEnabledChanged.emit(value)

  #translationScriptJaEnabledChanged = Signal(bool)
  #def isTranslationScriptJaEnabled(self): return to_bool(self.value('TranslationScriptJaEnabled', True))
  #def setTranslationScriptJaEnabled(self, value):
  #  if value != self.isTranslationScriptJaEnabled():
  #    self.setValue('TranslationScriptJaEnabled', value)
  #    self.translationScriptJaEnabledChanged.emit(value)

  #translationScriptEnEnabledChanged = Signal(bool)
  #def isTranslationScriptEnEnabled(self): return to_bool(self.value('TranslationScriptEnEnabled', True))
  #def setTranslationScriptEnEnabled(self, value):
  #  if value != self.isTranslationScriptEnEnabled():
  #    self.setValue('TranslationScriptEnEnabled', value)
  #    self.translationScriptEnEnabledChanged.emit(value)

  #def isAnyTranslationScriptEnabled(self):
  #  return self.isTranslationScriptJaEnabled() or self.isTranslationScriptEnEnabled()

  copiesGameTextChanged = Signal(bool)
  def copiesGameText(self): return to_bool(self.value('CopyGameText'))

  copiesGameSubtitleChanged = Signal(bool)
  def copiesGameSubtitle(self): return to_bool(self.value('CopyGameSubtitle'))

  convertsChineseChanged = Signal(bool)
  def convertsChinese(self):
    return to_bool(self.value('ConvertsChinese'))
  def setConvertsChinese(self, value):
    if value != self.convertsChinese():
      self.setValue('ConvertsChinese', value)
      self.convertsChineseChanged.emit(value)

  chineseVariantChanged = Signal(str)
  def chineseVariant(self):
    return to_unicode(self.value('ChineseVariant', 'tw')) # Taiwan by default
  def setChineseVariant(self, value):
    if value != self.chineseVariant():
      self.setValue('ChineseVariant', value)
      self.chineseVariantChanged.emit(value)

  yueEnabledChanged = Signal(bool)
  def isYueEnabled(self):
    return to_bool(self.value('YueEnabled'))
  def setYueEnabled(self, value):
    if value != self.isYueEnabled():
      self.setValue('YueEnabled', value)
      self.yueEnabledChanged.emit(value)

  ## Shared Dictionary ##

  termEnabledChanged = Signal(bool)
  def isTermEnabled(self): return to_bool(self.value('TermEnabled', True))

  termMarkedChanged = Signal(bool)
  def isTermMarked(self): return to_bool(self.value('TermMarked', True))
  def setTermMarked(self, t):
    if t != self.isTermMarked():
      self.setValue('TermMarked', t)
      self.termMarkedChanged.emit(t)

  hentaiEnabledChanged = Signal(bool)
  def isHentaiEnabled(self): return to_bool(self.value('Hentai'))
  def setHentaiEnabled(self, t):
    if t != self.isHentaiEnabled():
      self.setValue('Hentai', t)
      self.hentaiEnabledChanged.emit(t)

  termRubyEnabledChanged = Signal(bool)
  def isTermRubyEnabled(self): return to_bool(self.value('TermRuby', True))
  def setTermRubyEnabled(self, t):
    if t != self.isTermRubyEnabled():
      self.setValue('TermRuby', t)
      self.termRubyEnabledChanged.emit(t)

  termKoreanHanjaRubyEnabledChanged = Signal(bool)
  def isTermKoreanHanjaRubyEnabled(self): return to_bool(self.value('TermKoreanHanjaRuby', False))
  def setTermKoreanHanjaRubyEnabled(self, t):
    if t != self.isTermKoreanHanjaRubyEnabled():
      self.setValue('TermKoreanHanjaRuby', t)
      self.termKoreanHanjaRubyEnabledChanged.emit(t)

  termVietnamesePhienamRubyEnabledChanged = Signal(bool)
  def isTermVietnamesePhienamRubyEnabled(self): return to_bool(self.value('TermVietnamesePhienamRuby', False))
  def setTermVietnamesePhienamRubyEnabled(self, t):
    if t != self.isTermVietnamesePhienamRubyEnabled():
      self.setValue('TermVietnamesePhienamRuby', t)
      self.termVietnamesePhienamRubyEnabledChanged.emit(t)

  termChineseRomajiRubyEnabledChanged = Signal(bool)
  def isTermChineseRomajiRubyEnabled(self): return to_bool(self.value('TermChineseRomajiRuby', False))
  def setTermChineseRomajiRubyEnabled(self, t):
    if t != self.isTermChineseRomajiRubyEnabled():
      self.setValue('TermChineseRomajiRuby', t)
      self.termChineseRomajiRubyEnabledChanged.emit(t)

  #translationSyntaxEnabledChanged = Signal(bool)
  #def isTranslationSyntaxEnabled(self): return to_bool(self.value('RBMT'))
  #def setTranslationSyntaxEnabled(self, t):
  #  if t != self.isTranslationSyntaxEnabled():
  #    self.setValue('RBMT', t)
  #    self.translationSyntaxEnabledChanged.emit(t)

  ## Fonts ##

  japaneseFontChanged = Signal(unicode)
  def japaneseFont(self):
    return self.value('JapaneseFont', config.text_font('ja'))
  def setJapaneseFont(self, value):
    if value != self.japaneseFont():
      self.setValue('JapaneseFont', value)
      self.japaneseFontChanged.emit(value)

  englishFontChanged = Signal(unicode)
  def englishFont(self):
    return self.value('EnglishFont', config.text_font('en'))
  def setEnglishFont(self, value):
    if value != self.englishFont():
      self.setValue('EnglishFont', value)
      self.englishFontChanged.emit(value)

  chineseFontChanged = Signal(unicode)
  def chineseFont(self):
    return self.value('ChineseFont', config.text_font('zh'))
  def setChineseFont(self, value):
    if value != self.chineseFont():
      self.setValue('ChineseFont', value)
      self.chineseFontChanged.emit(value)

  #simplifiedChineseFontChanged = Signal(unicode)
  #def simplifiedChineseFont(self):
  #  return self.value('SimplifiedChineseFont', config.FONT_ZHS)
  #def setSimplifiedChineseFont(self, value):
  #  if value != self.simplifiedChineseFont():
  #    self.setValue('SimplifiedChineseFont', value)
  #    self.simplifiedChineseFontChanged.emit(value)

  koreanFontChanged = Signal(unicode)
  def koreanFont(self):
    return self.value('KoreanFont', config.text_font('ko'))
  def setKoreanFont(self, value):
    if value != self.koreanFont():
      self.setValue('KoreanFont', value)
      self.koreanFontChanged.emit(value)

  thaiFontChanged = Signal(unicode)
  def thaiFont(self):
    return self.value('ThaiFont', config.text_font('th'))
  def setThaiFont(self, value):
    if value != self.thaiFont():
      self.setValue('ThaiFont', value)
      self.thaiFontChanged.emit(value)

  vietnameseFontChanged = Signal(unicode)
  def vietnameseFont(self):
    return self.value('VietnameseFont', config.text_font('vi'))
  def setVietnameseFont(self, value):
    if value != self.vietnameseFont():
      self.setValue('VietnameseFont', value)
      self.vietnameseFontChanged.emit(value)

  malaysianFontChanged = Signal(unicode)
  def malaysianFont(self):
    return self.value('MalaysianFont', config.text_font('ms'))
  def setMalaysianFont(self, value):
    if value != self.malaysianFont():
      self.setValue('MalaysianFont', value)
      self.malaysianFontChanged.emit(value)

  indonesianFontChanged = Signal(unicode)
  def indonesianFont(self):
    return self.value('IndonesianFont', config.text_font('id'))
  def setIndonesianFont(self, value):
    if value != self.indonesianFont():
      self.setValue('IndonesianFont', value)
      self.indonesianFontChanged.emit(value)

  hebrewFontChanged = Signal(unicode)
  def hebrewFont(self):
    return self.value('HebrewFont', config.text_font('id'))
  def setHebrewFont(self, value):
    if value != self.hebrewFont():
      self.setValue('HebrewFont', value)
      self.hebrewFontChanged.emit(value)

  bulgarianFontChanged = Signal(unicode)
  def bulgarianFont(self):
    return self.value('BulgarianFont', config.text_font('bg'))
  def setBulgarianFont(self, value):
    if value != self.bulgarianFont():
      self.setValue('BulgarianFont', value)
      self.bulgarianFontChanged.emit(value)

  slovenianFontChanged = Signal(unicode)
  def slovenianFont(self):
    return self.value('SlovenianFont', config.text_font('sl'))
  def setSlovenianFont(self, value):
    if value != self.slovenianFont():
      self.setValue('SlovenianFont', value)
      self.slovenianFontChanged.emit(value)

  tagalogFontChanged = Signal(unicode)
  def tagalogFont(self):
    return self.value('TagalogFont', config.text_font('tl'))
  def setTagalogFont(self, value):
    if value != self.tagalogFont():
      self.setValue('TagalogFont', value)
      self.tagalogFontChanged.emit(value)

  belarusianFontChanged = Signal(unicode)
  def belarusianFont(self):
    return self.value('BelarusianFont', config.text_font('be'))
  def setBelarusianFont(self, value):
    if value != self.belarusianFont():
      self.setValue('BelarusianFont', value)
      self.belarusianFontChanged.emit(value)

  estonianFontChanged = Signal(unicode)
  def estonianFont(self):
    return self.value('EstonianFont', config.text_font('be'))
  def setEstonianFont(self, value):
    if value != self.estonianFont():
      self.setValue('EstonianFont', value)
      self.estonianFontChanged.emit(value)

  latvianFontChanged = Signal(unicode)
  def latvianFont(self):
    return self.value('LatvianFont', config.text_font('be'))
  def setLatvianFont(self, value):
    if value != self.latvianFont():
      self.setValue('LatvianFont', value)
      self.latvianFontChanged.emit(value)

  lithuanianFontChanged = Signal(unicode)
  def lithuanianFont(self):
    return self.value('LithuanianFont', config.text_font('be'))
  def setLithuanianFont(self, value):
    if value != self.lithuanianFont():
      self.setValue('LithuanianFont', value)
      self.lithuanianFontChanged.emit(value)

  czechFontChanged = Signal(unicode)
  def czechFont(self):
    return self.value('CzechFont', config.text_font('cs'))
  def setCzechFont(self, value):
    if value != self.czechFont():
      self.setValue('CzechFont', value)
      self.czechFontChanged.emit(value)

  danishFontChanged = Signal(unicode)
  def danishFont(self):
    return self.value('CzechFont', config.text_font('da'))
  def setDanishFont(self, value):
    if value != self.danishFont():
      self.setValue('DanishFont', value)
      self.danishFontChanged.emit(value)

  greekFontChanged = Signal(unicode)
  def greekFont(self):
    return self.value('GreekFont', config.text_font('el'))
  def setGreekFont(self, value):
    if value != self.greekFont():
      self.setValue('greekFont', value)
      self.greekFontChanged.emit(value)

  finnishFontChanged = Signal(unicode)
  def finnishFont(self):
    return self.value('FinnishFont', config.text_font('fi'))
  def setFinnishFont(self, value):
    if value != self.finnishFont():
      self.setValue('FinnishFont', value)
      self.finnishFontChanged.emit(value)

  hungarianFontChanged = Signal(unicode)
  def hungarianFont(self):
    return self.value('HungarianFont', config.text_font('hu'))
  def setHungarianFont(self, value):
    if value != self.hungarianFont():
      self.setValue('HungarianFont', value)
      self.hungarianFontChanged.emit(value)

  norwegianFontChanged = Signal(unicode)
  def norwegianFont(self):
    return self.value('NorwegianFont', config.text_font('no'))
  def setNorwegianFont(self, value):
    if value != self.norwegianFont():
      self.setValue('NorwegianFont', value)
      self.norwegianFontChanged.emit(value)

  romanianFontChanged = Signal(unicode)
  def romanianFont(self):
    return self.value('RomanianFont', config.text_font('ro'))
  def setRomanianFont(self, value):
    if value != self.romanianFont():
      self.setValue('RomanianFont', value)
      self.romanianFontChanged.emit(value)

  slovakFontChanged = Signal(unicode)
  def slovakFont(self):
    return self.value('SlovakFont', config.text_font('sk'))
  def setSlovakFont(self, value):
    if value != self.slovakFont():
      self.setValue('SlovakFont', value)
      self.slovakFontChanged.emit(value)

  swedishFontChanged = Signal(unicode)
  def swedishFont(self):
    return self.value('SwedishFont', config.text_font('sv'))
  def setSwedishFont(self, value):
    if value != self.swedishFont():
      self.setValue('SwedishFont', value)
      self.swedishFontChanged.emit(value)

  turkishFontChanged = Signal(unicode)
  def turkishFont(self):
    return self.value('TurkishFont', config.text_font('tr'))
  def setTurkishFont(self, value):
    if value != self.turkishFont():
      self.setValue('TurkishFont', value)
      self.turkishFontChanged.emit(value)

  ukrainianFontChanged = Signal(unicode)
  def ukrainianFont(self):
    return self.value('UkrainianFont', config.text_font('uk'))
  def setUkrainianFont(self, value):
    if value != self.ukrainianFont():
      self.setValue('UkrainianFont', value)
      self.ukrainianFontChanged.emit(value)

  arabicFontChanged = Signal(unicode)
  def arabicFont(self):
    return self.value('ArabicFont', config.text_font('ar'))
  def setArabicFont(self, value):
    if value != self.arabicFont():
      self.setValue('ArabicFont', value)
      self.arabicFontChanged.emit(value)

  germanFontChanged = Signal(unicode)
  def germanFont(self):
    return self.value('GermanFont', config.text_font('de'))
  def setGermanFont(self, value):
    if value != self.germanFont():
      self.setValue('GermanFont', value)
      self.germanFontChanged.emit(value)

  frenchFontChanged = Signal(unicode)
  def frenchFont(self):
    return self.value('FrenchFont', config.text_font('fr'))
  def setFrenchFont(self, value):
    if value != self.frenchFont():
      self.setValue('FrenchFont', value)
      self.frenchFontChanged.emit(value)

  italianFontChanged = Signal(unicode)
  def italianFont(self):
    return self.value('ItalianFont', config.text_font('it'))
  def setItalianFont(self, value):
    if value != self.italianFont():
      self.setValue('ItalianFont', value)
      self.italianFontChanged.emit(value)

  spanishFontChanged = Signal(unicode)
  def spanishFont(self):
    return self.value('SpanishFont', config.text_font('es'))
  def setSpanishFont(self, value):
    if value != self.spanishFont():
      self.setValue('SpanishFont', value)
      self.spanishFontChanged.emit(value)

  portugueseFontChanged = Signal(unicode)
  def portugueseFont(self):
    return self.value('PortugueseFont', config.text_font('pt'))
  def setPortugueseFont(self, value):
    if value != self.portugueseFont():
      self.setValue('PortugueseFont', value)
      self.portugueseFontChanged.emit(value)

  russianFontChanged = Signal(unicode)
  def russianFont(self):
    return self.value('RussianFont', config.text_font('ru'))
  def setRussianFont(self, value):
    if value != self.russianFont():
      self.setValue('RussianFont', value)
      self.russianFontChanged.emit(value)

  polishFontChanged = Signal(unicode)
  def polishFont(self):
    return self.value('PolishFont', config.text_font('pl'))
  def setPolishFont(self, value):
    if value != self.polishFont():
      self.setValue('PolishFont', value)
      self.polishFontChanged.emit(value)

  dutchFontChanged = Signal(unicode)
  def dutchFont(self):
    return self.value('DutchFont', config.text_font('nl'))
  def setDutchFont(self, value):
    if value != self.dutchFont():
      self.setValue('DutchFont', value)
      self.dutchFontChanged.emit(value)

  ## Game agent ##

  # Whether allow disabling game launchers
  #def isGameAgentLauncherEnabled(self):
  #  return to_bool(self.value('GameAgentLauncher', True))
  #def setGameAgentLauncherEnabled(self, value):
  #  self.setValue('GameAgentLauncher', value)

  # Convert Chinese kanji to Japanese
  gameAgentConvertsKanjiChanged = Signal(bool)
  def gameAgentConvertsKanji(self):
    return to_bool(self.value('GameAgentConvertsKanji', True)) # enable traditional kanji by default
  def setGameAgentConvertsKanji(self, value):
    if value != self.gameAgentConvertsKanji():
      self.setValue('GameAgentConvertsKanji', value)
      self.gameAgentConvertsKanjiChanged.emit(value)

  # Whether use game agent over texthook
  gameAgentEnabledChanged = Signal(bool)
  def isGameAgentEnabled(self):
    return to_bool(self.value('GameAgent', False)) # disable game agent by default
  def setGameAgentEnabled(self, value):
    if value != self.isGameAgentEnabled():
      self.setValue('GameAgent', value)
      self.gameAgentEnabledChanged.emit(value)

  isGameAgentLauncherNeeded = isGameAgentEnabled # alias for historical reason
  #def isGameAgentLauncherNeeded(self):
  #  return self.isGameAgentEnabled() and (
  #      self.isEmbeddedScenarioTranslationEnabled() or
  #      self.isEmbeddedNameTranslationEnabled() or
  #      self.isEmbeddedOtherTranslationEnabled())

  embeddedScenarioTranslatorChanged = Signal(unicode)
  def embeddedScenarioTranslator(self):
    return to_unicode(self.value('EmbeddedScenarioTranslator'))
  def setEmbeddedScenarioTranslator(self, value):
    if value != self.embeddedScenarioTranslator():
      self.setValue('EmbeddedScenarioTranslator', value)
      self.embeddedScenarioTranslatorChanged.emit(value)

  embeddedScenarioWidthChanged = Signal(int)
  def embeddedScenarioWidth(self):
    return to_int(self.value('EmbeddedScenarioWidth'))
  def setEmbeddedScenarioWidth(self, value):
    if value != self.embeddedScenarioWidth():
      self.setValue('EmbeddedScenarioWidth', value)
      self.embeddedScenarioWidthChanged.emit(value)

  embeddedScenarioWidthEnabledChanged = Signal(bool)
  def isEmbeddedScenarioWidthEnabled(self):
    return to_bool(self.value('EmbeddedScenarioWidthEnabled'))
  def setEmbeddedScenarioWidthEnabled(self, value):
    if value != self.isEmbeddedScenarioWidthEnabled():
      self.setValue('EmbeddedScenarioWidthEnabled', value)
      self.embeddedScenarioWidthEnabledChanged.emit(value)

  embeddedTranslationWaitTimeChanged = Signal(int)
  def embeddedTranslationWaitTime(self):
    return to_int(self.value('EmbeddedTranslationWaitTime', 2000)) # 2 seconds by default
  def setEmbeddedTranslationWaitTime(self, value):
    if value != self.embeddedTranslationWaitTime():
      self.setValue('EmbeddedTranslationWaitTime', value)
      self.embeddedTranslationWaitTimeChanged.emit(value)

  #embeddedTextCancellableByControlChanged = Signal(bool)
  #def isEmbeddedTextCancellableByControl(self):
  #  return to_bool(self.value('EmbeddedTextDetectsCtrl', True))
  #def setEmbeddedTextCancellableByControl(self, value):
  #  if value != self.isEmbeddedTextCancellableByControl():
  #    self.setValue('EmbeddedTextDetectsCtrl', value)
  #    self.embeddedTextCancellableByControlChanged.emit(value)

  # Whether translate window components
  # This implies transcoding enabled
  windowTranslationEnabledChanged = Signal(bool)
  def isWindowTranslationEnabled(self):
    return to_bool(self.value('WindowTranslation', True))
  def setWindowTranslationEnabled(self, value):
    if value != self.isWindowTranslationEnabled():
      self.setValue('WindowTranslation', value)
      self.windowTranslationEnabledChanged.emit(value)

  # Whether display original text after the translation
  # This implies translation enabled
  windowTextVisibleChanged = Signal(bool)
  def isWindowTextVisible(self):
    return to_bool(self.value('WindowTextVisible', True))
  def setWindowTextVisible(self, value):
    if value != self.isWindowTextVisible():
      self.setValue('WindowTextVisible', value)
      self.windowTextVisibleChanged.emit(value)

  # Whether fix window translation encoding
  windowTranscodingEnabledChanged = Signal(bool)
  def isWindowTranscodingEnabled(self):
    return to_bool(self.value('WindowTranscoding')) # disable window transcoding by default
  def setWindowTranscodingEnabled(self, value):
    if value != self.isWindowTranscodingEnabled():
      self.setValue('WindowTranscoding', value)
      self.windowTranscodingEnabledChanged.emit(value)

  # Whether translate embedded scenario text
  embeddedScenarioTranslationEnabledChanged = Signal(bool)
  def isEmbeddedScenarioTranslationEnabled(self):
    return to_bool(self.value('EmbeddedScenarioTranslation', True))
  def setEmbeddedScenarioTranslationEnabled(self, value):
    if value != self.isEmbeddedScenarioTranslationEnabled():
      self.setValue('EmbeddedScenarioTranslation', value)
      self.embeddedScenarioTranslationEnabledChanged.emit(value)

  embeddedScenarioTranscodingEnabledChanged = Signal(bool)
  def isEmbeddedScenarioTranscodingEnabled(self):
    return to_bool(self.value('EmbeddedScenarioTranscoding'))
  def setEmbeddedScenarioTranscodingEnabled(self, value):
    if value != self.isEmbeddedScenarioTranscodingEnabled():
      self.setValue('EmbeddedScenarioTranscoding', value)
      self.embeddedScenarioTranscodingEnabledChanged.emit(value)

  # Whether delete scenario text
  embeddedScenarioVisibleChanged = Signal(bool)
  def isEmbeddedScenarioVisible(self):
    return to_bool(self.value('EmbeddedScenarioVisible', True))
  def setEmbeddedScenarioVisible(self, value):
    if value != self.isEmbeddedScenarioVisible():
      self.setValue('EmbeddedScenarioVisible', value)
      self.embeddedScenarioVisibleChanged.emit(value)

  embeddedScenarioTextVisibleChanged = Signal(bool)
  def isEmbeddedScenarioTextVisible(self):
    return to_bool(self.value('EmbeddedScenarioText'))
  def setEmbeddedScenarioTextVisible(self, value):
    if value != self.isEmbeddedScenarioTextVisible():
      self.setValue('EmbeddedScenarioText', value)
      self.embeddedScenarioTextVisibleChanged.emit(value)

  embeddedNameTextVisibleChanged = Signal(bool)
  def isEmbeddedNameTextVisible(self):
    return to_bool(self.value('EmbeddedNameText', True))
  def setEmbeddedNameTextVisible(self, value):
    if value != self.isEmbeddedNameTextVisible():
      self.setValue('EmbeddedNameText', value)
      self.embeddedNameTextVisibleChanged.emit(value)

  embeddedNameTranslationEnabledChanged = Signal(bool)
  def isEmbeddedNameTranslationEnabled(self):
    return to_bool(self.value('EmbeddedNameTranslation', True))
  def setEmbeddedNameTranslationEnabled(self, value):
    if value != self.isEmbeddedNameTranslationEnabled():
      self.setValue('EmbeddedNameTranslation', value)
      self.embeddedNameTranslationEnabledChanged.emit(value)

  embeddedNameTranscodingEnabledChanged = Signal(bool)
  def isEmbeddedNameTranscodingEnabled(self):
    return to_bool(self.value('EmbeddedNameTranscoding'))
  def setEmbeddedNameTranscodingEnabled(self, value):
    if value != self.isEmbeddedNameTranscodingEnabled():
      self.setValue('EmbeddedNameTranscoding', value)
      self.embeddedNameTranscodingEnabledChanged.emit(value)

  embeddedNameVisibleChanged = Signal(bool)
  def isEmbeddedNameVisible(self):
    return to_bool(self.value('EmbeddedNameVisible', True))
  def setEmbeddedNameVisible(self, value):
    if value != self.isEmbeddedNameVisible():
      self.setValue('EmbeddedNameVisible', value)
      self.embeddedNameVisibleChanged.emit(value)

  embeddedOtherTextVisibleChanged = Signal(bool)
  def isEmbeddedOtherTextVisible(self):
    return to_bool(self.value('EmbeddedOtherText', True))
  def setEmbeddedOtherTextVisible(self, value):
    if value != self.isEmbeddedOtherTextVisible():
      self.setValue('EmbeddedOtherText', value)
      self.embeddedOtherTextVisibleChanged.emit(value)

  embeddedOtherTranslationEnabledChanged = Signal(bool)
  def isEmbeddedOtherTranslationEnabled(self):
    return to_bool(self.value('EmbeddedOtherTranslation', True))
  def setEmbeddedOtherTranslationEnabled(self, value):
    if value != self.isEmbeddedOtherTranslationEnabled():
      self.setValue('EmbeddedOtherTranslation', value)
      self.embeddedOtherTranslationEnabledChanged.emit(value)

  embeddedOtherTranscodingEnabledChanged = Signal(bool)
  def isEmbeddedOtherTranscodingEnabled(self):
    return to_bool(self.value('EmbeddedOtherTranscoding'))
  def setEmbeddedOtherTranscodingEnabled(self, value):
    if value != self.isEmbeddedOtherTranscodingEnabled():
      self.setValue('EmbeddedOtherTranscoding', value)
      self.embeddedOtherTranscodingEnabledChanged.emit(value)

  # This method is not used, though
  embeddedOtherVisibleChanged = Signal(bool)
  def isEmbeddedOtherVisible(self):
    return to_bool(self.value('EmbeddedOtherVisible', True))
  def setEmbeddedOtherVisible(self, value):
    if value != self.isEmbeddedOtherVisible():
      self.setValue('EmbeddedOtherVisible', value)
      self.embeddedOtherVisibleChanged.emit(value)

  embeddedSpaceAlwaysInsertedChanged = Signal(bool)
  def isEmbeddedSpaceAlwaysInserted(self):
    return to_bool(self.value('EmbeddedSpaceAlwaysInserted'))
  def setEmbeddedSpaceAlwaysInserted(self, value):
    if value != self.isEmbeddedSpaceAlwaysInserted():
      self.setValue('EmbeddedSpaceAlwaysInserted', value)
      self.embeddedSpaceAlwaysInsertedChanged.emit(value)

  embeddedSpaceSmartInsertedChanged = Signal(bool)
  def isEmbeddedSpaceSmartInserted(self):
    return to_bool(self.value('EmbeddedSpaceSmartInserted'))
  def setEmbeddedSpaceSmartInserted(self, value):
    if value != self.isEmbeddedSpaceSmartInserted():
      self.setValue('EmbeddedSpaceSmartInserted', value)
      self.embeddedSpaceSmartInsertedChanged.emit(value)

  embeddedSpacePolicyEncodingChanged = Signal(unicode)
  def embeddedSpacePolicyEncoding(self):
    return to_unicode(self.value('EmbeddedSpacePolicyEncoding'))
  def setEmbeddedSpacePolicyEncoding(self, value):
    if value != self.embeddedSpacePolicyEncoding():
      self.setValue('EmbeddedSpacePolicyEncoding', value)
      self.embeddedSpacePolicyEncodingChanged.emit(value)

  embeddedFontEnabledChanged = Signal(bool)
  def isEmbeddedFontEnabled(self):
    return to_bool(self.value('EmbeddedFontEnabled'))
  def setEmbeddedFontEnabled(self, value):
    if value != self.isEmbeddedFontEnabled():
      self.setValue('EmbeddedFontEnabled', value)
      self.embeddedFontEnabledChanged.emit(value)

  embeddedFontFamilyChanged = Signal(unicode)
  def embeddedFontFamily(self):
    return to_unicode(self.value('EmbeddedFontFamily'))
  def setEmbeddedFontFamily(self, value):
    if value != self.embeddedFontFamily():
      self.setValue('EmbeddedFontFamily', value)
      self.embeddedFontFamilyChanged.emit(value)

  embeddedFontWeightEnabledChanged = Signal(bool)
  def isEmbeddedFontWeightEnabled(self):
    return to_bool(self.value('EmbeddedFontWeightEnabled'))
  def setEmbeddedFontWeightEnabled(self, value):
    if value != self.isEmbeddedFontWeightEnabled():
      self.setValue('EmbeddedFontWeightEnabled', value)
      self.embeddedFontWeightEnabledChanged.emit(value)

  embeddedFontWeightChanged = Signal(int)
  def embeddedFontWeight(self):
    return to_int(self.value('EmbeddedFontWeight'))
  def setEmbeddedFontWeight(self, value):
    if value != self.embeddedFontWeight():
      self.setValue('EmbeddedFontWeight', value)
      self.embeddedFontWeightChanged.emit(value)

  embeddedFontScaleEnabledChanged = Signal(bool)
  def isEmbeddedFontScaleEnabled(self):
    return to_bool(self.value('EmbeddedFontScaleEnabled'))
  def setEmbeddedFontScaleEnabled(self, value):
    if value != self.isEmbeddedFontScaleEnabled():
      self.setValue('EmbeddedFontScaleEnabled', value)
      self.embeddedFontScaleEnabledChanged.emit(value)

  embeddedFontScaleChanged = Signal(float)
  def embeddedFontScale(self):
    return to_float(self.value('EmbeddedFontScale', 1.0))
  def setEmbeddedFontScale(self, value):
    if value != self.embeddedFontScale():
      self.setValue('EmbeddedFontScale', value)
      self.embeddedFontScaleChanged.emit(value)

  embeddedFontCharSetEnabledChanged = Signal(bool)
  def isEmbeddedFontCharSetEnabled(self):
    return to_bool(self.value('EmbeddedFontCharSetEnabled', True))
  def setEmbeddedFontCharSetEnabled(self, value):
    if value != self.isEmbeddedFontCharSetEnabled():
      self.setValue('EmbeddedFontCharSetEnabled', value)
      self.embeddedFontCharSetEnabledChanged.emit(value)

  embeddedFontCharSetChanged = Signal(int)
  def embeddedFontCharSet(self):
    return to_int(self.value('EmbeddedFontCharSet'))
  def setEmbeddedFontCharSet(self, value):
    if value != self.embeddedFontCharSet():
      self.setValue('EmbeddedFontCharSet', value)
      self.embeddedFontCharSetChanged.emit(value)

  #windowHookEnabledChanged = Signal(bool)
  #def isWindowHookEnabled(self):
  #  return to_bool(self.value('WindowHookEnabled')) # disabled by default
  #def setWindowHookEnabled(self, value):
  #  if value != self.isWindowHookEnabled():
  #    self.setValue('WindowHookEnabled', value)
  #    self.windowHookEnabledChanged.emit(value)

  # Kagami
  def isGrimoireTextVisible(self):
    return to_bool(self.value('GrimoireText', True))
  def isGrimoireTranslationVisible(self):
    return to_bool(self.value('GrimoireTranslation', True))
  def isGrimoireSubtitleVisible(self):
    return to_bool(self.value('GrimoireSubtitle', True))
  def isGrimoireCommentVisible(self):
    return to_bool(self.value('GrimoireComment', True))
  def isGrimoireDanmakuVisible(self):
    return to_bool(self.value('GrimoireDanmaku', True))
  def isGrimoireNameVisible(self):
    return to_bool(self.value('GrimoireName', True))

@memoized
def global_(): return Settings()

## Kagami settings proxy ##

#def int_property(name, default, notify=None):
#  return Property(int,
#      lambda _: to_int(global_().value(name, default)),
#      lambda _, value: global_().setValue(name, value),
#      notify=notify)

def int_property(name, default, notify=None):
  return Property(int,
      lambda _: to_int(global_().value(name, default)),
      lambda _, value: global_().setValue(name, value),
      notify=notify)

def float_property(name, default, notify=None):
  return Property(float,
      lambda _: to_float(global_().value(name, default), default),
      lambda _, value: global_().setValue(name, value),
      notify=notify)

def bool_property(name, default, notify=None):
  return Property(bool,
      lambda _: to_bool(global_().value(name, default)),
      lambda _, value: global_().setValue(name, value),
      notify=notify)

def unicode_property(name, default="", notify=None):
  return Property(unicode,
      lambda _: to_unicode(global_().value(name, default)),
      lambda _, value: global_().setValue(name, value),
      notify=notify)

#@QmlObject
class SettingsProxy(QObject):

  @Slot()
  def sync(self): global_().sync()

  def __init__(self, parent=None):
    super(SettingsProxy, self).__init__(parent)
    g = global_()
    #g.applocEnabledChanged.connect(self.applocEnabledChanged)
    #g.timeZoneEnabledChanged.connect(self.timeZoneEnabledChanged)
    g.springBoardWallpaperUrlChanged.connect(self.springBoardWallpaperUrlChanged)
    g.springBoardSlidesEnabledChanged.connect(self.springBoardSlidesEnabledChanged)

    g.grimoireFontColorChanged.connect(self.grimoireFontColorChanged)
    g.grimoireShadowColorChanged.connect(self.grimoireShadowColorChanged)
    g.grimoireTextColorChanged.connect(self.grimoireTextColorChanged)
    #g.grimoireTranslationColorChanged.connect(self.grimoireTranslationColorChanged)
    g.grimoireSubtitleColorChanged.connect(self.grimoireSubtitleColorChanged)
    g.grimoireCommentColorChanged.connect(self.grimoireCommentColorChanged)
    g.grimoireDanmakuColorChanged.connect(self.grimoireDanmakuColorChanged)

    g.infoseekColorChanged.connect(self.infoseekColorChanged)
    g.exciteColorChanged.connect(self.exciteColorChanged)
    g.babylonColorChanged.connect(self.babylonColorChanged)
    g.systranColorChanged.connect(self.systranColorChanged)
    g.niftyColorChanged.connect(self.niftyColorChanged)
    g.bingColorChanged.connect(self.bingColorChanged)
    g.googleColorChanged.connect(self.googleColorChanged)
    g.naverColorChanged.connect(self.naverColorChanged)
    g.baiduColorChanged.connect(self.baiduColorChanged)
    g.youdaoColorChanged.connect(self.youdaoColorChanged)
    g.lecOnlineColorChanged.connect(self.lecOnlineColorChanged)
    g.transruColorChanged.connect(self.transruColorChanged)
    g.hanVietColorChanged.connect(self.hanVietColorChanged)
    g.romajiColorChanged.connect(self.romajiColorChanged)
    g.jbeijingColorChanged.connect(self.jbeijingColorChanged)
    g.vtransColorChanged.connect(self.vtransColorChanged)
    g.fastaitColorChanged.connect(self.fastaitColorChanged)
    g.dreyeColorChanged.connect(self.dreyeColorChanged)
    g.ezTransColorChanged.connect(self.ezTransColorChanged)
    g.transcatColorChanged.connect(self.transcatColorChanged)
    g.atlasColorChanged.connect(self.atlasColorChanged)
    g.lecColorChanged.connect(self.lecColorChanged)

    #g.rubyTypeChanged.connect(self.rubyTypeChanged)
    #g.rubyJaInvertedChanged.connect(self.rubyJaInvertedChanged)

    g.convertsChineseChanged.connect(self.convertsChineseChanged)

    #g.baiduRubyEnabledChanged.connect(self.baiduRubyEnabledChanged)
    #g.naverRubyEnabledChanged.connect(self.naverRubyEnabledChanged)

    #g.msimeParserEnabledChanged.connect(self.msimeParserEnabledChanged)
    #g.meCabEnabledChanged.connect(self.meCabEnabledChanged)
    #g.meCabDictionaryChanged.connect(self.meCabDictionaryChanged)
    #g.caboChaEnabledChanged.connect(self.caboChaEnabledChanged)

    g.cometCounterVisibleChanged.connect(self.cometCounterVisibleChanged)

    g.hentaiEnabledChanged.connect(self.hentaiChanged)
    g.growlEnabledChanged.connect(self.growlEnabledChanged)

    self.termEnabledChanged.connect(g.termEnabledChanged)
    #self.termMarkedChanged.connect(g.termMarkedChanged)

    self.copiesGameTextChanged.connect(g.copiesGameTextChanged)
    self.copiesGameSubtitleChanged.connect(g.copiesGameSubtitleChanged)

    #self.windowHookEnabledChanged.connect(g.windowHookEnabledChanged)
    #self.windowTextVisibleChanged.connect(g.windowTextVisibleChanged)

    self.gameTextCapacityChanged.connect(g.gameTextCapacityChanged)

    g.ocrEnabledChanged.connect(self.ocrEnabledChanged)

    #for sig in 'japaneseFontChanged':
    #  getattr(g, sig).connect(
    #      getattr(self, sig))
    g.japaneseFontChanged.connect(self.japaneseFontChanged)
    g.englishFontChanged.connect(self.englishFontChanged)
    g.chineseFontChanged.connect(self.chineseFontChanged)
    #g.simplifiedChineseFontChanged.connect(self.simplifiedChineseFontChanged)
    g.koreanFontChanged.connect(self.koreanFontChanged)
    g.thaiFontChanged.connect(self.thaiFontChanged)
    g.vietnameseFontChanged.connect(self.vietnameseFontChanged)
    g.malaysianFontChanged.connect(self.malaysianFontChanged)
    g.indonesianFontChanged.connect(self.indonesianFontChanged)
    g.hebrewFontChanged.connect(self.hebrewFontChanged)
    g.bulgarianFontChanged.connect(self.bulgarianFontChanged)
    g.slovenianFontChanged.connect(self.slovenianFontChanged)
    g.tagalogFontChanged.connect(self.tagalogFontChanged)
    g.belarusianFontChanged.connect(self.belarusianFontChanged)
    g.estonianFontChanged.connect(self.estonianFontChanged)
    g.latvianFontChanged.connect(self.latvianFontChanged)
    g.lithuanianFontChanged.connect(self.lithuanianFontChanged)
    g.arabicFontChanged.connect(self.arabicFontChanged)
    g.germanFontChanged.connect(self.germanFontChanged)
    g.frenchFontChanged.connect(self.frenchFontChanged)
    g.italianFontChanged.connect(self.italianFontChanged)
    g.spanishFontChanged.connect(self.spanishFontChanged)
    g.portugueseFontChanged.connect(self.portugueseFontChanged)
    g.russianFontChanged.connect(self.russianFontChanged)
    g.polishFontChanged.connect(self.polishFontChanged)
    g.dutchFontChanged.connect(self.dutchFontChanged)

    g.czechFontChanged.connect(self.czechFontChanged)
    g.danishFontChanged.connect(self.danishFontChanged)
    g.greekFontChanged.connect(self.greekFontChanged)
    g.finnishFontChanged.connect(self.finnishFontChanged)
    g.hungarianFontChanged.connect(self.hungarianFontChanged)
    g.norwegianFontChanged.connect(self.norwegianFontChanged)
    g.romanianFontChanged.connect(self.romanianFontChanged)
    g.slovakFontChanged.connect(self.slovakFontChanged)
    g.swedishFontChanged.connect(self.swedishFontChanged)
    g.turkishFontChanged.connect(self.turkishFontChanged)
    g.ukrainianFontChanged.connect(self.ukrainianFontChanged)

    g.voiceCharacterEnabledChanged.connect(self.voiceCharacterEnabledChanged)
    g.speaksGameTextChanged.connect(self.speaksGameTextChanged)

    g.rubyInvertedChanged.connect(self.rubyInvertedChanged)
    g.rubyTextEnabledChanged.connect(self.rubyTextEnabledChanged)
    g.rubyTranslationEnabledChanged.connect(self.rubyTranslationEnabledChanged)

    g.chineseRubyEnabledChanged.connect(self.chineseRubyEnabledChanged)
    g.chineseRubyTypeChanged.connect(self.chineseRubyTypeChanged)

    g.japaneseRubyEnabledChanged.connect(self.japaneseRubyEnabledChanged)
    g.japaneseRubyKanaEnabledChanged.connect(self.japaneseRubyKanaEnabledChanged)
    g.japaneseRubyTypeChanged.connect(self.japaneseRubyTypeChanged)
    g.japaneseRubyHighlightEnabledChanged.connect(self.japaneseRubyHighlightChanged)
    g.japaneseRubyAnnotatedChanged.connect(self.japaneseRubyAnnotatedChanged)
    g.japaneseRubyInvertedChanged.connect(self.japaneseRubyInvertedChanged)

    g.koreanRubyEnabledChanged.connect(self.koreanRubyEnabledChanged)
    g.romajaRubyEnabledChanged.connect(self.romajaRubyEnabledChanged)
    g.hanjaRubyEnabledChanged.connect(self.hanjaRubyEnabledChanged)

    g.blockedLanguagesChanged.connect(self.blockedLanguagesChanged)

    g.termRubyEnabledChanged.connect(self.termRubyEnabledChanged)

  hentaiChanged = Signal(bool)
  hentai = Property(bool,
      lambda _: global_().isHentaiEnabled(),
      lambda _, t: global_().setHentaiEnabled(t),
      notify=hentaiChanged)

  growlEnabledChanged = Signal(bool)
  growlEnabled = Property(bool,
      lambda _: global_().isGrowlEnabled(),
      lambda _, t: global_().setGrowlEnabled(t),
      notify=growlEnabledChanged)

  def setGameTextCapacity(self, value):
    if value != self.gameTextCapacity:
      global_().setValue('GameTextCapacity', value)
      self.gameTextCapacityChanged.emit(value)
  gameTextCapacityChanged = Signal(int)
  gameTextCapacity = Property(int,
      lambda _: global_().gameTextCapacity(),
      setGameTextCapacity,
      notify=gameTextCapacityChanged)

  def setTermEnabled(self, value):
    if value != self.termEnabled:
      global_().setValue('TermEnabled', value)
      self.termEnabledChanged.emit(value)
  termEnabledChanged = Signal(bool)
  termEnabled = Property(bool,
      lambda _: global_().isTermEnabled(),
      setTermEnabled,
      notify=termEnabledChanged)

  #def setTermMarked(self, value):
  #  if value != self.termMarked:
  #    global_().setValue('TermMarked', value)
  #    self.termMarkedChanged.emit(value)
  #termMarkedChanged = Signal(bool)
  #termMarked = Property(bool,
  #    lambda _: global_().isTermMarked(),
  #    setTermMarked,
  #    notify=termMarkedChanged)

  #def setWindowHookEnabled(self, value):
  #  if value != self.windowHookEnabled:
  #    global_().setValue('WindowHookEnabled', value)
  #    self.windowHookEnabledChanged.emit(value)
  #windowHookEnabledChanged = Signal(bool)
  #windowHookEnabled = Property(bool,
  #    lambda _: global_().isWindowHookEnabled(),
  #    setWindowHookEnabled,
  #    notify=windowHookEnabledChanged)

  #def setWindowTextVisible(self, value):
  #  if value != self.windowTextVisible:
  #    global_().setValue('WindowTextVisible', value)
  #    self.windowTextVisibleChanged.emit(value)
  #windowTextVisibleChanged = Signal(bool)
  #windowTextVisible = Property(bool,
  #    lambda _: global_().isWindowTextVisible(),
  #    setWindowTextVisible,
  #    notify=windowTextVisibleChanged)

  speaksGameTextChanged = Signal(bool)
  speaksGameText = Property(bool,
      lambda _: global_().speaksGameText(),
      lambda _, v: global_().setSpeaksGameText(v),
      notify=speaksGameTextChanged)

  voiceCharacterEnabledChanged = Signal(bool)
  voiceCharacterEnabled = Property(bool,
      lambda _: global_().isVoiceCharacterEnabled(),
      lambda _, v: global_().setVoiceCharacterEnabled(v),
      notify=voiceCharacterEnabledChanged)

  subtitleVoiceEnabledChanged = Signal(bool)
  subtitleVoiceEnabled = bool_property('SubtitleVoice', False, notify=subtitleVoiceEnabledChanged)

  termRubyEnabledChanged = Signal(bool)
  termRubyEnabled = unicode_property('TermRuby', True, notify=termRubyEnabledChanged)

  blockedLanguagesChanged = Signal(unicode)
  blockedLanguages = unicode_property('BlockedLanguages', '', notify=blockedLanguagesChanged)
  japaneseFontChanged = Signal(unicode)
  japaneseFont = unicode_property('JapaneseFont', config.text_font('ja'), notify=japaneseFontChanged)
  englishFontChanged = Signal(unicode)
  englishFont = unicode_property('EnglishFont', config.text_font('en'), notify=englishFontChanged)
  chineseFontChanged = Signal(unicode)
  chineseFont = unicode_property('ChineseFont', config.text_font('zh'), notify=chineseFontChanged)
  #simplifiedChineseFontChanged = Signal(unicode)
  #simplifiedChineseFont = unicode_property('SimplifiedChineseFont', config.FONT_ZHS, notify=simplifiedChineseFontChanged)
  koreanFontChanged = Signal(unicode)
  koreanFont = unicode_property('KoreanFont', config.text_font('ko'), notify=koreanFontChanged)
  thaiFontChanged = Signal(unicode)
  thaiFont = unicode_property('ThaiFont', config.text_font('th'), notify=thaiFontChanged)
  vietnameseFontChanged = Signal(unicode)
  vietnameseFont = unicode_property('VietnameseFont', config.text_font('vi'), notify=vietnameseFontChanged)
  malaysianFontChanged = Signal(unicode)
  malaysianFont = unicode_property('MalaysianFont', config.text_font('ms'), notify=malaysianFontChanged)
  indonesianFontChanged = Signal(unicode)
  indonesianFont = unicode_property('IndonesianFont', config.text_font('id'), notify=indonesianFontChanged)
  hebrewFontChanged = Signal(unicode)
  hebrewFont = unicode_property('HebrewFont', config.text_font('he'), notify=hebrewFontChanged)
  bulgarianFontChanged = Signal(unicode)
  bulgarianFont = unicode_property('BulgarianFont', config.text_font('bg'), notify=bulgarianFontChanged)
  slovenianFontChanged = Signal(unicode)
  slovenianFont = unicode_property('SlovenianFont', config.text_font('sl'), notify=slovenianFontChanged)
  tagalogFontChanged = Signal(unicode)
  tagalogFont = unicode_property('TagalogFont', config.text_font('tl'), notify=tagalogFontChanged)
  belarusianFontChanged = Signal(unicode)
  belarusianFont = unicode_property('BelarusianFont', config.text_font('be'), notify=belarusianFontChanged)
  estonianFontChanged = Signal(unicode)
  estonianFont = unicode_property('EstonianFont', config.text_font('et'), notify=estonianFontChanged)
  latvianFontChanged = Signal(unicode)
  latvianFont = unicode_property('LatvianFont', config.text_font('lv'), notify=latvianFontChanged)
  lithuanianFontChanged = Signal(unicode)
  lithuanianFont = unicode_property('LithuanianFont', config.text_font('lt'), notify=lithuanianFontChanged)
  arabicFontChanged = Signal(unicode)
  arabicFont = unicode_property('ArabicFont', config.text_font('ar'), notify=arabicFontChanged)
  germanFontChanged = Signal(unicode)
  germanFont = unicode_property('GermanFont', config.text_font('de'), notify=germanFontChanged)
  frenchFontChanged = Signal(unicode)
  frenchFont = unicode_property('FrenchFont', config.text_font('fr'), notify=frenchFontChanged)
  italianFontChanged = Signal(unicode)
  italianFont = unicode_property('ItalianFont', config.text_font('it'), notify=italianFontChanged)
  spanishFontChanged = Signal(unicode)
  spanishFont = unicode_property('SpanishFont', config.text_font('es'), notify=spanishFontChanged)
  portugueseFontChanged = Signal(unicode)
  portugueseFont = unicode_property('PortugueseFont', config.text_font('pt'), notify=portugueseFontChanged)
  russianFontChanged = Signal(unicode)
  russianFont = unicode_property('RussianFont', config.text_font('ru'), notify=russianFontChanged)
  polishFontChanged = Signal(unicode)
  polishFont = unicode_property('PolishFont', config.text_font('pl'), notify=polishFontChanged)
  dutchFontChanged = Signal(unicode)
  dutchFont = unicode_property('DutchFont', config.text_font('nl'), notify=dutchFontChanged)
  czechFontChanged = Signal(unicode)
  czechFont = unicode_property('CzechFont', config.text_font('cs'), notify=czechFontChanged)
  danishFontChanged = Signal(unicode)
  danishFont = unicode_property('DanishFont', config.text_font('da'), notify=danishFontChanged)
  greekFontChanged = Signal(unicode)
  greekFont = unicode_property('GreekFont', config.text_font('el'), notify=greekFontChanged)
  finnishFontChanged = Signal(unicode)
  finnishFont = unicode_property('FinnishFont', config.text_font('fi'), notify=finnishFontChanged)
  hungarianFontChanged = Signal(unicode)
  hungarianFont = unicode_property('HungarianFont', config.text_font('hu'), notify=hungarianFontChanged)
  norwegianFontChanged = Signal(unicode)
  norwegianFont = unicode_property('NorwegianFont', config.text_font('no'), notify=norwegianFontChanged)
  romanianFontChanged = Signal(unicode)
  romanianFont = unicode_property('RomanianFont', config.text_font('ro'), notify=romanianFontChanged)
  slovakFontChanged = Signal(unicode)
  slovakFont = unicode_property('SlovakFont', config.text_font('sk'), notify=slovakFontChanged)
  swedishFontChanged = Signal(unicode)
  swedishFont = unicode_property('SwedishFont', config.text_font('sv'), notify=swedishFontChanged)
  turkishFontChanged = Signal(unicode)
  turkishFont = unicode_property('TurkishFont', config.text_font('tr'), notify=turkishFontChanged)
  ukrainianFontChanged = Signal(unicode)
  ukrainianFont = unicode_property('UkrainianFont', config.text_font('uk'), notify=ukrainianFontChanged)

  #msimeParserEnabledChanged = Signal(bool)
  #msimeParserEnabled = bool_property('MsimeParserEnabled', False, notify=msimeParserEnabledChanged)

  kagamiClockEnabledChanged = Signal(bool)
  kagamiClockEnabled = bool_property('KagamiClock', False, notify=kagamiClockEnabledChanged)
  kagamiClockXChanged = Signal(int)
  kagamiClockX = int_property('KagamiClockX', 0, notify=kagamiClockXChanged)
  kagamiClockYChanged = Signal(int)
  kagamiClockY = int_property('KagamiClockY', 0, notify=kagamiClockYChanged)

  convertsChineseChanged = Signal(bool)
  convertsChinese = bool_property('ConvertsChinese', False, notify=convertsChineseChanged)

  #meCabEnabledChanged = Signal(bool)
  #meCabEnabled = bool_property('MeCabEnabled', False, notify=meCabEnabledChanged)
  #meCabDictionaryChanged = Signal(unicode)
  #meCabDictionary = unicode_property('MeCabDictionary', '', notify=meCabDictionaryChanged)

  #caboChaEnabledChanged = Signal(bool)
  #caboChaEnabled = bool_property('CaboChaEnabled', '', notify=caboChaEnabledChanged)

  #rubyTypeChanged = Signal(unicode)
  #rubyType = unicode_property('FuriganaType', 'hiragana', notify=rubyTypeChanged)

  #rubyJaInvertedChanged = Signal(bool)
  #rubyJaInverted = bool_property('InvertRubyJa', False, notify=rubyJaInvertedChanged)

  #baiduRubyEnabledChanged = Signal(bool)
  #baiduRubyEnabled = bool_property('BaiduRubyEnabled', True, notify=baiduRubyEnabledChanged)

  #naverRubyEnabledChanged = Signal(bool)
  #naverRubyEnabled = bool_property('NaverRubyEnabled', True, notify=naverRubyEnabledChanged)

  springBoardWallpaperUrlChanged = Signal(unicode)
  springBoardWallpaperUrl = unicode_property('SpringBoardWallpaperUrl', notify=springBoardWallpaperUrlChanged)

  springBoardSlidesEnabledChanged = Signal(bool)
  springBoardSlidesEnabled = bool_property('SpringBoardSlidesEnabled', True, notify=springBoardSlidesEnabledChanged)

  #applocEnabledChanged = Signal(bool)
  #applocEnabled = bool_property('ApplocEnabled', True, notify=applocEnabledChanged)

  #timeZoneEnabledChanged = Signal(bool)
  #timeZoneEnabled = bool_property('TimeZoneEnabled', True, notify=timeZoneEnabledChanged)

  rubyTextEnabledChanged = Signal(bool)
  rubyTextEnabled = bool_property('RubyText', True, notify=rubyTextEnabledChanged)
  rubyTranslationEnabledChanged = Signal(bool)
  rubyTranslationEnabled = bool_property('RubyTranslation', False, notify=rubyTranslationEnabledChanged)

  rubyInvertedChanged = Signal(bool)
  rubyInverted = bool_property('InvertRuby', False, notify=rubyInvertedChanged)

  romajaRubyEnabledChanged = Signal(bool)
  romajaRubyEnabled = bool_property('RomajaRuby', True, notify=romajaRubyEnabledChanged)

  hanjaRubyEnabledChanged = Signal(bool)
  hanjaRubyEnabled = bool_property('HanjaRuby', True, notify=hanjaRubyEnabledChanged)

  koreanRubyEnabledChanged = Signal(bool)
  koreanRubyEnabled = bool_property('KoreanRuby', True, notify=koreanRubyEnabledChanged)

  chineseRubyEnabledChanged = Signal(bool)
  chineseRubyEnabled = bool_property('ChineseRuby', True, notify=chineseRubyEnabledChanged)

  chineseRubyTypeChanged = Signal(unicode)
  chineseRubyType = unicode_property('ChineseRubyType', 'pinyin', notify=chineseRubyTypeChanged)

  japaneseRubyInvertedChanged = Signal(bool)
  japaneseRubyInverted = bool_property('JapaneseInvertRuby', False, notify=japaneseRubyInvertedChanged)

  japaneseRubyEnabledChanged = Signal(bool)
  japaneseRubyEnabled = bool_property('JapaneseRuby', False, notify=japaneseRubyEnabledChanged)

  japaneseRubyKanaEnabledChanged = Signal(bool)
  japaneseRubyKanaEnabled = bool_property('JapaneseRubyKana', False, notify=japaneseRubyKanaEnabledChanged)

  japaneseRubyTypeChanged = Signal(unicode)
  japaneseRubyType = unicode_property('JapaneseRubyType', 'hira', notify=japaneseRubyTypeChanged)

  japaneseRubyHighlightChanged = Signal(bool)
  japaneseRubyHighlight = bool_property('JapaneseRubyHighlight', True, notify=japaneseRubyHighlightChanged)

  japaneseRubyAnnotatedChanged = Signal(bool)
  japaneseRubyAnnotated = bool_property('JapaneseRubyAnnotated', True, notify=japaneseRubyAnnotatedChanged)

  grimoireNormalizedXChanged = Signal(float)
  grimoireNormalizedX = float_property('GrimoireNormalizedX', 0.0, notify=grimoireNormalizedXChanged)
  grimoireNormalizedYChanged = Signal(float)
  grimoireNormalizedY = float_property('GrimoireNormalizedY', 0.0, notify=grimoireNormalizedYChanged)

  grimoireFontColorChanged = Signal(unicode)
  grimoireFontColor = unicode_property('GrimoireFontColor',
      config.SETTINGS_FONT_COLOR,
      notify=grimoireFontColorChanged)
  grimoireShadowColorChanged = Signal(unicode)
  grimoireShadowColor = unicode_property('GrimoireShadowColor',
      config.SETTINGS_SHADOW_COLOR,
      notify=grimoireShadowColorChanged)
  grimoireTextColorChanged = Signal(unicode)
  grimoireTextColor = unicode_property('GrimoireTextColor',
      config.SETTINGS_TEXT_COLOR,
      notify=grimoireTextColorChanged)
  grimoireSubtitleColorChanged = Signal(unicode)
  grimoireSubtitleColor = unicode_property('GrimoireSubtitleColor',
      config.SETTINGS_SUBTITLE_COLOR,
      notify=grimoireSubtitleColorChanged)
  #grimoireTranslationColorChanged = Signal(unicode)
  #grimoireTranslationColor = unicode_property('GrimoireTranslationColor',
  #    config.SETTINGS_TRANSLATION_COLOR,
  #    notify=grimoireTranslationColorChanged)
  grimoireCommentColorChanged = Signal(unicode)
  grimoireCommentColor = unicode_property('GrimoireCommentColor',
      config.SETTINGS_COMMENT_COLOR,
      notify=grimoireCommentColorChanged)
  grimoireDanmakuColorChanged = Signal(unicode)
  grimoireDanmakuColor = unicode_property('GrimoireDanmakuColor',
      config.SETTINGS_DANMAKU_COLOR,
      notify=grimoireDanmakuColorChanged)

  infoseekColorChanged = Signal(unicode)
  infoseekColor = unicode_property('InfoseekColor', config.SETTINGS_INFOSEEK_COLOR, notify=infoseekColorChanged)
  exciteColorChanged = Signal(unicode)
  exciteColor = unicode_property('ExciteColor', config.SETTINGS_EXCITE_COLOR, notify=exciteColorChanged)
  babylonColorChanged = Signal(unicode)
  babylonColor = unicode_property('BabylonColor', config.SETTINGS_BABYLON_COLOR, notify=babylonColorChanged)
  systranColorChanged = Signal(unicode)
  systranColor = unicode_property('SystranColor', config.SETTINGS_SYSTRAN_COLOR, notify=systranColorChanged)
  niftyColorChanged = Signal(unicode)
  niftyColor = unicode_property('NiftyColor', config.SETTINGS_NIFTY_COLOR, notify=niftyColorChanged)
  googleColorChanged = Signal(unicode)
  googleColor = unicode_property('GoogleColor', config.SETTINGS_GOOGLE_COLOR, notify=googleColorChanged)
  bingColorChanged = Signal(unicode)
  bingColor = unicode_property('BingColor', config.SETTINGS_BING_COLOR, notify=bingColorChanged)
  baiduColorChanged = Signal(unicode)
  baiduColor = unicode_property('BaiduColor', config.SETTINGS_BAIDU_COLOR, notify=baiduColorChanged)
  youdaoColorChanged = Signal(unicode)
  youdaoColor = unicode_property('YoudaoColor', config.SETTINGS_YOUDAO_COLOR, notify=youdaoColorChanged)
  naverColorChanged = Signal(unicode)
  naverColor = unicode_property('NaverColor', config.SETTINGS_NAVER_COLOR, notify=naverColorChanged)
  lecOnlineColorChanged = Signal(unicode)
  lecOnlineColor = unicode_property('LecOnlineColor', config.SETTINGS_LECONLINE_COLOR, notify=lecOnlineColorChanged)
  transruColorChanged = Signal(unicode)
  transruColor = unicode_property('TransruColor', config.SETTINGS_TRANSRU_COLOR, notify=transruColorChanged)
  hanVietColorChanged = Signal(unicode)
  hanVietColor = unicode_property('HanVietColor', config.SETTINGS_HANVIET_COLOR, notify=hanVietColorChanged)
  vtransColorChanged = Signal(unicode)
  vtransColor = unicode_property('VTransColor', config.SETTINGS_VTRANS_COLOR, notify=vtransColorChanged)
  romajiColorChanged = Signal(unicode)
  romajiColor = unicode_property('RomajiColor', config.SETTINGS_ROMAJI_COLOR, notify=romajiColorChanged)
  jbeijingColorChanged = Signal(unicode)
  jbeijingColor = unicode_property('JBeijingColor', config.SETTINGS_JBEIJING_COLOR, notify=jbeijingColorChanged)
  fastaitColorChanged = Signal(unicode)
  fastaitColor = unicode_property('FastAITColor', config.SETTINGS_FASTAIT_COLOR, notify=fastaitColorChanged)
  dreyeColorChanged = Signal(unicode)
  dreyeColor = unicode_property('DreyeColor', config.SETTINGS_DREYE_COLOR, notify=dreyeColorChanged)
  ezTransColorChanged = Signal(unicode)
  ezTransColor = unicode_property('EzTransColor', config.SETTINGS_EZTRANS_COLOR, notify=ezTransColorChanged)
  transcatColorChanged = Signal(unicode)
  transcatColor = unicode_property('TransCATColor', config.SETTINGS_TRANSCAT_COLOR, notify=transcatColorChanged)
  atlasColorChanged = Signal(unicode)
  atlasColor = unicode_property('AtlasColor', config.SETTINGS_ATLAS_COLOR, notify=atlasColorChanged)
  lecColorChanged = Signal(unicode)
  lecColor = unicode_property('LecColor', config.SETTINGS_LEC_COLOR, notify=lecColorChanged)

  cometCounterVisibleChanged = Signal(bool)
  cometCounterVisible = bool_property('CometCounterVisible', True, notify=cometCounterVisibleChanged)

  hotkeyEnabled = bool_property('Hotkey', False)

  #grimoireRevertsColor = bool_property('GrimoireRevertsColor', False)
  grimoireShadowEnabled = bool_property('GrimoireShadow', True)
  grimoireHoverEnabled = bool_property('GrimoireHover', False)
  #grimoireReadEnabled = bool_property('GrimoireRead', True)
  #grimoirePopupEnabled = bool_property('GrimoirePopup', True)
  #grimoireCopyEnabled = bool_property('GrimoireCopy', False)
  #grimoireFuriganaEnabled = bool_property('GrimoireFurigana', True)
  grimoireAlignCenter = bool_property('GrimoireAlignCenter', False)
  #gameBorderVisible = bool_property('GameBorderVisible', False)

  grimoireSlimDock = bool_property('GrimoireSlimDock', False)

  grimoireTextVisible = bool_property('GrimoireText', True)
  grimoireTranslationVisible = bool_property('GrimoireTranslation', True)
  grimoireSubtitleVisible = bool_property('GrimoireSubtitle', True)
  grimoireCommentVisible = bool_property('GrimoireComment', True)
  grimoireDanmakuVisible = bool_property('GrimoireDanmaku', True)
  grimoireNameVisible = bool_property('GrimoireName', True)

  ocrZoomFactor = float_property('OCRZoomFactor', 1.0)
  shioriZoomFactor = float_property('ShioriZoomFactor', config.SETTINGS_ZOOM_FACTOR)

  grimoireZoomFactor = float_property('GrimoireZoomFactor', config.SETTINGS_ZOOM_FACTOR)
  grimoireWidthFactor = float_property('GrimoireWidthFactor', config.SETTINGS_WIDTH_FACTOR)
  grimoireShadowOpacity = float_property('GrimoireShadowOpacity', config.SETTINGS_SHADOW_OPACITY)

  grimoireAutoHideDock = bool_property('GrimoireAutoHideDock', True)

  shioriWidth = int_property('DictionaryPopupWidth', config.SETTINGS_DICT_POPUP_WIDTH)

  mirageZoomFactor = float_property('MirageZoomFactor', config.SETTINGS_ZOOM_FACTOR)
  mirageTextVisible = bool_property('MirageText', True)
  mirageTranslationVisible = bool_property('MirageTranslation', True)
  mirageSpeaksText = bool_property('MirageSpeaksText', False)
  mirageSpeaksTranslation = bool_property('MirageSpeaksTranslation', False)
  mirageMouseEnabled = bool_property('MirageMouse', True)
  mirageClipboardEnabled = bool_property('MirageClipboard', True)

  glowIntensity = float_property('GlowIntensity', 1)
  glowRadius = float_property('GlowRadius', 4)

  # Only applied to grimoire, though
  splitsGameText = bool_property('SplitGameText', True)
  splitsTranslation = bool_property('SplitTranslation', False)

  copiesGameTextChanged = Signal(bool)
  copiesGameText = bool_property('CopyGameText', False, notify=copiesGameTextChanged)

  copiesGameSubtitleChanged = Signal(bool)
  copiesGameSubtitle = bool_property('CopyGameSubtitle', False, notify=copiesGameSubtitleChanged)

  kagamiFocusEnabledChanged = Signal(bool)
  kagamiFocusEnabled = bool_property('KagamiFocusEnabled', False, notify=kagamiFocusEnabledChanged)

  ocrEnabledChanged = Signal(bool)
  ocrEnabled = bool_property('OcrEnabled', False, notify=ocrEnabledChanged)

  graffitiCopyEnabled = bool_property('GraffitiCopy', True)
  graffitiHeaderVisible = bool_property('GraffitiHeaderVisible', True)
  #graffitiSpellCheck = bool_property('GraffitiSpellCheck', True)
  #graffitiGroupEnabled = bool_property('GraffitiGroupEnabled', True)

  #graffitiTextVisible = bool_property('GraffitiText', True)
  #graffitiTranslationVisible = bool_property('GraffitiTranslation', True)
  #graffitiSubtitleVisible = bool_property('GraffitiSubtitle', True)
  #graffitiCommentVisible = bool_property('GraffitiComment', True)
  #graffitiDanmakuVisible = bool_property('GraffitiDanmaku', True)

  inputSpellCheck = bool_property('InputSpellCheck', True)
  inputAcceptsReturn = bool_property('InputAcceptsReturn', False)
  inputAcceptsShiftReturn = bool_property('InputAcceptsShiftReturn', False)
  inputLocked = bool_property('InputLocked', False)

# EOF

  #kagamiIgnoresFocusChanged = Signal(bool)
  #kagamiIgnoresFocus = bool_property('KagamiIgnoresFocus', True, notify=kagamiIgnoresFocusChanged)

  #gameDetectionEnabledChanged = Signal(bool)
  #gameDetectionEnabled = bool_property('GameDetectionEnabled', True, notify=gameDetectionEnabledChanged)

  #hookCodeEnabledChanged = Signal(bool)
  #hookCodeEnabled = bool_property('HookCodeEnabled', True, notify=hookCodeEnabledChanged)

  #def setKagamiIgnoresFocus(self, value):
  #  if value != self.kagamiIgnoresFocus:
  #    global_().setValue('KagamiIgnoresFocus', value)
  #    self.kagamiIgnoresFocusChanged.emit(value)
  #kagamiIgnoresFocusChanged = Signal(bool)
  #kagamiIgnoresFocus = Property(bool,
  #    lambda _: global_().kagamiIgnoresFocus(),
  #    notify=kagamiIgnoresFocusChanged)
