# coding: utf8
# main.py
# 10/5/2012 jichi
#
# Signal directions:
# - texthook => textman => kagami
# - gamewiz => gameman => dataman
# - gameman => textman
# - gameman => kagami
#
# Query directions:
# - textman => dataman => netman

__all__ = 'MainObject', 'MainObjectProxy'

import os
from functools import partial
from PySide.QtCore import Property, Signal, Slot, Qt, QCoreApplication, QObject, QTimer, QThreadPool
from sakurakit import skdatetime, skevents, skos
from sakurakit.skclass import Q_Q, memoizedproperty, hasmemoizedproperty
from sakurakit.skdebug import dprint, dwarn, debugmethod
#from sakurakit.skqml import QmlObject
from sakurakit.sktr import tr_
from mytr import my, mytr_
import config, defs, features, growl, libman, prompt, qmldialog, rc, settings, winutil

EXITED = False # whether the application is existing

def _parseargs(args):
  """Parse command line arguments
  @param  args  [str]
  @return  kw not None
  """
  ret = {}
  try:
    for i, it in enumerate(args):
      if it == '--pid':
        ret['pid'] = long(args[i+1])
      elif it == '--minimize':
        ret['minimize'] = True
      elif it == '--nosplash':
        ret['nosplash'] = True
  except Exception, e:
    dwarn("failed to parse command line option", e)
  return ret

# MainObject private data
@Q_Q
class _MainObject(object):
  def __init__(self):
    self.widgets = [] # [QtWidgets.QWidget]
    #self.debug = False # bool
    #q.destroyed.connect(self._onDestroyed)

  #def _onDestroyed(self):
  #  if self.q = MainObject.instance:
  #    MainObject.instance = None

  #def __del__(self):
  #  self._topWindow.deleteLater() # Enforce closing root window

  ## Components ##

  @property
  def topWindow(self):
    import windows
    ret = windows.top()
    if features.WINE:
      ret.closeRequested.connect(self.q.confirmQuit, Qt.QueuedConnection)
      ret.showDot()
    return ret

  @property
  def normalWindow(self):
    import windows
    ret = windows.normal()
    if features.WINE:
      ret.closeRequested.connect(self.q.confirmQuit, Qt.QueuedConnection)
    return ret

  #@property
  #def topWindowHolder(self):
  #  from windows import WindowHolder
  #  ret = WindowHolder(self.topWindow)
  #  self.widgets.append(ret)
  #  return ret

  @memoizedproperty
  def trayIcon(self):
    import tray
    return tray.TrayIcon(self.q)

  @memoizedproperty
  def textHook(self):
    dprint("create text hook")
    from texthook import texthook
    ret = texthook.global_()
    #ret.setDebug(config.APP_DEBUG)
    ret.setParent(self.q)

    ret.setParentWinId(self.topWindow.winId())

    ret.processDetached.connect(ret.clearWhitelist)
    ret.processAttached.connect(lambda:
        ret.setWhitelistEnabled(True)) # Why partial does not work here?!
    ret.hookCodeChanged.connect(lambda hcode:
        hcode and growl.msg(my.tr("Apply user-defined hook") + "<br/>" + hcode))
    ret.removesRepeatChanged.connect(lambda t:
        t and growl.notify(my.tr("Ignore infinite cyclic repetition in the text")))
    ret.keepsSpaceChanged.connect(lambda t:
        t and growl.notify(my.tr("Preserve spaces in the game text")))

    for sig in ret.processAttached, ret.processDetached:
      sig.connect(self.topWindow.bringWindowToTop)

    #ret.setKeepsSpace(True)

    ss = settings.global_()
    ss.gameTextCapacityChanged.connect(ret.setSuggestedDataCapacity)
    ret.setSuggestedDataCapacity(ss.gameTextCapacity())
    return ret

  #@memoizedproperty
  #def nameManager(self):
  #  dprint("create name manager") # Move this upward before kagami
  #  import nameman
  #  ret = nameman.manager()

  #  import settings
  #  ss = settings.global_()

  #  ret.setMeCabDictionary(ss.meCabDictionary())
  #  ss.meCabDictionaryChanged.connect(ret.setMeCabDictionary)
  #  return ret

  #@memoizedproperty
  #def jlpManager(self):
  #  dprint("create jlp manager") # Move this upward before kagami
  #  import jlpman
  #  ret = jlpman.manager()

  #  import settings
  #  ss = settings.global_()
  #  def refresh():
  #    ret.setParserType(
  #        '' if not ss.isMeCabEnabled() else
  #        'cabocha' if ss.isCaboChaEnabled() else
  #        'mecab')
  #  refresh()
  #  for sig in ss.meCabEnabledChanged, ss.caboChaEnabledChanged:
  #    sig.connect(refresh)
  #  return ret

  @memoizedproperty
  def meCabManager(self):
    dprint("create mecab manager") # Move this upward before kagami
    import mecabman
    ret = mecabman.manager()

    import settings
    ss = settings.global_()

    ret.setEdictEnabled(ss.isMeCabEdictEnabled())
    ss.meCabEdictEnabledChanged.connect(ret.setEdictEnabled)

    ret.setTranslateEnabled(bool(ss.japaneseRubyLanguages()))
    ss.japaneseRubyLanguagesChanged.connect(partial(
        lambda ret, l: ret.setTranslateEnabled(bool(l)),
        ret))
    return ret

    # Already connected in gameman
    #self.gameManager.processChanged.connect(ret.clearUserDictionary)

    #ret.setEnabled(ss.isMeCabEnabled())
    #ss.meCabEnabledChanged.connect(ret.setEnabled)

    #ret.setRubyType(ss.rubyType())
    #ss.rubyTypeChanged.connect(ret.setRubyType)

  #@memoizedproperty
  #def caboChaManager(self):
  #  dprint("create cabocha manager") # Move this upward before kagami
  #  import cabochaman
  #  ret = cabochaman.manager()

  #  import settings
  #  ss = settings.global_()

  #  ret.setEnabled(ss.isMeCabEnabled())
  #  ss.meCabEnabledChanged.connect(ret.setEnabled)

  #  ret.setRubyType(ss.rubyType())
  #  ss.rubyTypeChanged.connect(ret.setRubyType)

  #  ret.setDictionaryName(ss.meCabDictionary())
  #  ss.meCabDictionaryChanged.connect(ret.setDictionaryName)

  #  #import _cabochaman
  #  #_cabochaman.CaboChaParser().parser()
  #  return ret

  @memoizedproperty
  def proxyManager(self):
    dprint("create proxy manager")
    import proxy
    ret = proxy.manager()
    ss = settings.global_()
    ret.setEnabled(ss.isMainlandChina())
    ss.mainlandChinaChanged.connect(ret.setEnabled)
    return ret

  @memoizedproperty
  def networkManager(self):
    dprint("create network manager")
    import netman
    ret = netman.manager()
    ret.setParent(self.q)
    ret.setVersion(config.VERSION_TIMESTAMP)

    ss = settings.global_()
    ret.setBlockedLanguages(ss.blockedLanguages())
    ss.blockedLanguagesChanged.connect(ret.setBlockedLanguages)
    return ret

  #@memoizedproperty
  #def cometManager(self):
  #  dprint("create comet manager")
  #  import cometman
  #  ret = cometman.manager()
  #  ret.setParent(self.q)
  #  nm = self.networkManager
  #  ret.setEnabled(nm.isOnline())
  #  nm.onlineChanged.connect(ret.setEnabled)
  #  return ret

  @memoizedproperty
  def dataManager(self):
    dprint("create data manager")
    q = self.q
    import dataman
    ret = dataman.manager()
    ret.setParent(q)
    return ret

  @memoizedproperty
  def dictionaryManager(self):
    dprint("create dictionary manager")
    import dictman
    ret = dictman.manager()
    ss = settings.global_()
    ret.setUserLanguage(ss.userLanguage())
    ss.userLanguageChanged.connect(ret.setUserLanguage)
    ret.setJapaneseLookupEnabled(ss.isJapaneseDictionaryEnabled())
    ss.japaneseDictionaryEnabledChanged.connect(ret.setJapaneseLookupEnabled)
    ret.setJapaneseTranslateLanguages(ss.japaneseRubyLanguages())
    ss.japaneseRubyLanguagesChanged.connect(ret.setJapaneseTranslateLanguages)
    return ret

  @memoizedproperty
  def cacheManager(self):
    dprint("create cache manager")
    import cacheman
    ret = cacheman.manager()
    #ret.setParent(self.q)

    ret.setEnabled(self.networkManager.isOnline())
    self.networkManager.onlineChanged.connect(ret.setEnabled)

    ret.clearTemporaryFiles()
    return ret

  @memoizedproperty
  def ocrManager(self):
    dprint("create ocr manager")
    import ocrman
    ret = ocrman.manager()
    ret.setParent(self.q)
    ret.imageSelected.connect(self.ocrPopup.showPopup)
    ret.regionSelected.connect(self.ocrRegion.showRegion)

    self.gameManager.windowChanged.connect(ret.setSelectedWindow)
    self.gameManager.processDetached.connect(ret.clearRegionItems)

    ret.textRecognized.connect(self.textManager.addRecognizedText)

    ss = settings.global_()
    ret.setEnabled(features.ADMIN != False and ss.isOcrEnabled() and ret.isInstalled())
    ss.ocrEnabledChanged.connect(ret.setEnabled)
    ret.setLanguages(ss.ocrLanguages())
    ss.ocrLanguagesChanged.connect(ret.setLanguages)
    ret.setSpaceEnabled(ss.isOcrSpaceEnabled())
    ss.ocrSpaceEnabledChanged.connect(ret.setSpaceEnabled)
    ret.setRegionOcrInterval(ss.ocrRefreshInterval())
    ss.ocrRefreshIntervalChanged.connect(ret.setRegionOcrInterval)

    return ret

  def initializeOCR(self):
    self.windowManager
    self.ocrManager

  #@memoizedproperty
  #def dataMiner(self):
  #  import datamine
  #  return datamine.DataMiner(self.q)

  @memoizedproperty
  def windowManager(self):
    dprint("create window manager")
    import winman
    ret = winman.manager()
    ret.setParent(self.q)

    return ret

  @memoizedproperty
  def gameManager(self):
    dprint("create game manager")
    import gameman
    ret = gameman.manager()
    ret.setParent(self.q)

    tm = self.textManager
    ret.processDetached.connect(tm.clear)

    ret.languageChanged.connect(tm.setGameLanguage)
    ret.encodingChanged.connect(tm.setEncoding)
    ret.threadChanged.connect(tm.setScenarioThread)

    ret.otherThreadsChanged.connect(tm.setOtherThreads)

    ret.nameThreadChanged.connect(tm.setNameThread)
    ret.nameThreadDisabled.connect(tm.clearNameThread)

    ret.processChanged.connect(tm.clearTranslationCache)
    #ret.processChanged.connect(partial(tm.setEnabled, True))

    #ret.processChanged.connect(self.meCabManager.clearUserDictionary)

    ret.threadKeptChanged.connect(tm.setKeepsThreads)

    ret.removesRepeatChanged.connect(tm.setRemovesRepeatText)

    dm = self.dataManager
    ret.processDetached.connect(dm.clearSubtitles)

    agent = self.gameAgent
    agent.processDetached.connect(ret.processDetached)
    agent.engineChanged.connect(lambda name:
        not name and agent.connectedPid() == ret.currentGamePid() and ret.attachTextHook())
    agent.processAttachTimeout.connect(lambda pid:
        pid == ret.currentGamePid() and ret.attachTextHook())

    th = self.textHook
    th.processDetached.connect(ret.processDetached)

    ret.ignoresRepeatChanged.connect(th.setRemovesRepeat)
    ret.keepsSpaceChanged.connect(th.setKeepsSpace)
    #ret.removesRepeatChanged.connect(lambda value:
    #    self.textHook.setDataCapacity(defs.MAX_REPEAT_DATA_LENGTH if value else defs.MAX_DATA_LENGTH))

    #ret.cleared.connect(tm.clear)
    ret.cleared.connect(self.textHook.detachProcess)
    ret.cleared.connect(self.gameDetectionTimer.start)

    ret.cleared.connect(partial(skevents.runlater,
        self.q.activate, 500)) # since openning SpringBoard is kind of slow

    ret.processChanged.connect(lambda pid:
        pid and self.gameDetectionTimer.stop())

    #ret.processChanged.connect(self._warmupEdictLater)
    #ret.processChanged.connect(lambda:
    #    self.networkManager.isOnline() and self._warmupGoogleTtsLater)

    #settings.global_().windowHookEnabledChanged.connect(lambda enabled:
    #    self.gameManager.enableWindowHook() if enabled else
    #    self.gameManager.disableWindowHook())
    return ret

  #def _warmupEdictLater(self):
  #  # Create EDICT out of QML
  #  # Otherwise it would not be able to find pysqlite2
  #  import edict
  #  skevents.runlater(edict.warmup, 800)

  #def _warmupGoogleTtsLater(self):
  #  if features.TEXT_TO_SPEECH and self.networkManager.isOnline():
  #    skevents.runlater(self.googleTtsEngine.warmup, 2000)

  @memoizedproperty
  def gameAgent(self):
    dprint("create game agent")
    import gameagent
    ret = gameagent.global_()
    ret.setParent(self.q)
    for sig in ret.processAttached, ret.processDetached:
      sig.connect(self.topWindow.bringWindowToTop)
    return ret

  @memoizedproperty
  def textManager(self):
    dprint("create text manager")
    import textman
    ret = textman.manager()
    ret.setParent(self.q)

    ret.setOnline(self.networkManager.isOnline())
    self.networkManager.onlineChanged.connect(ret.setOnline)

    # Text might be sent from different threads? Need Qt.QueuedConnection?
    th = self.textHook
    th.dataReceived.connect(ret.addIthText)

    th.realDataCapacityChanged.connect(ret.setGameTextCapacity)
    ret.setGameTextCapacity(th.realDataCapacity())

    rpc = self.rpcServer
    rpc.windowTextsReceived.connect(ret.addWindowTexts)
    ret.translationCacheCleared.connect(rpc.clearAgentTranslation)
    ret.windowTranslationChanged.connect(rpc.sendWindowTranslation)

    rpc.engineTextReceived.connect(ret.addAgentText)

    agent = self.gameAgent
    ret.agentTranslationProcessed.connect(agent.sendEmbeddedTranslation)
    ret.agentTranslationCancelled.connect(agent.cancelEmbeddedTranslation)

    grimoire = self.grimoire

    ret.cleared.connect(grimoire.clear)
    ret.pageBreakReceived.connect(grimoire.pageBreak)
    ret.textReceived.connect(grimoire.showText)
    ret.translationReceived.connect(grimoire.showTranslation)
    ret.commentReceived.connect(grimoire.showComment)
    ret.subtitleReceived.connect(grimoire.showSubtitle)

    ret.nameTextReceived.connect(grimoire.showNameText)
    ret.nameTranslationReceived.connect(grimoire.showNameTranslation)

    #ret.rawTextReceived.connect(self._speakGameText)

    ret.cleared.connect(self.omajinai.clear)
    ret.commentReceived.connect(self.omajinai.showComment)

    ret.cleared.connect(self.gospel.hide)
    ret.cleared.connect(self.gospel.clear)
    ret.commentReceived.connect(self.gospel.showComment)

    ret.cleared.connect(self.gossip.clear)
    ret.commentReceived.connect(self.gossip.showComment)

    ret.pageBreakReceived.connect(self.topWindow.bringWindowToTop)

    ss = settings.global_()

    ret.setUserLanguage(ss.userLanguage())
    ss.userLanguageChanged.connect(ret.setUserLanguage)

    ret.setBlockedLanguages(ss.blockedLanguages())
    ss.blockedLanguagesChanged.connect(ret.setBlockedLanguages)

    ss.windowTranscodingEnabledChanged.connect(ret.clearWindowTexts)

    dm = self.dataManager
    for sig in (
        ss.machineTranslatorChanged,
        ss.termEnabledChanged,
        ss.termMarkedChanged,
        ss.userLanguageChanged,
        dm.termsChanged,
        #dm.gameFilesChanged, # duplicate with gameItemsChanged
        dm.gameItemsChanged,
        #self.gameManager.processChanged,   # this would cause recursion
      ):
      sig.connect(ret.clearTranslationCache)

    # These should be moved to dataManager. Put here to avoid recursion, moved to gameman

    #for sig in (
    #    ss.termEnabledChanged,
    #    ss.userLanguageChanged,
    #    dm.termsChanged,
    #    #dm.gameFilesChanged, # duplicate with gameItemsChanged
    #    dm.gameItemsChanged,
    #    #self.gameManager.processChanged,   # this would cause recursion, moved to gameman
    #    ):
    #  sig.connect(dm.clearMacroCache)

    #ss.windowTextVisibleChanged.connect(ret.refreshWindowTranslation)
    return ret

  #@memoizedproperty
  #def pluginManager(self):
  #  import userplugin
  #  ret = userplugin.manager()
  #  ret.setParent(self.q)
  #  return ret

  @memoizedproperty
  def referenceManager(self):
    dprint("create reference manager")
    import refman
    ret = refman.manager()
    #ret.setParent(self.q)
    nm = self.networkManager
    ret.setOnline(nm.isOnline())
    nm.onlineChanged.connect(ret.setOnline)
    return ret

  @memoizedproperty
  def trailersManager(self):
    dprint("create trailers manager")
    import refman
    ret = refman.trailers()
    #ret.setParent(self.q)
    nm = self.networkManager
    ret.setOnline(nm.isOnline())
    nm.onlineChanged.connect(ret.setOnline)
    return ret

  #@memoizedproperty
  #def holysealManager(self):
  #  dprint("create holyseal manager")
  #  import refman
  #  ret = refman.holyseal()
  #  ret.setParent(self.q)
  #  nm = self.networkManager
  #  ret.setOnline(nm.isOnline())
  #  nm.onlineChanged.connect(ret.setOnline)
  #  return ret

  @memoizedproperty
  def gyuttoManager(self):
    dprint("create gyutto manager")
    import refman
    ret = refman.gyutto()
    #ret.setParent(self.q)
    nm = self.networkManager
    ret.setOnline(nm.isOnline())
    nm.onlineChanged.connect(ret.setOnline)
    return ret

  @memoizedproperty
  def getchuManager(self):
    dprint("create getchu manager")
    import refman
    ret = refman.getchu()
    #ret.setParent(self.q)
    nm = self.networkManager
    ret.setOnline(nm.isOnline())
    nm.onlineChanged.connect(ret.setOnline)
    return ret

  @memoizedproperty
  def amazonManager(self):
    dprint("create amazon manager")
    import refman
    ret = refman.amazon()
    #ret.setParent(self.q)
    nm = self.networkManager
    ret.setOnline(nm.isOnline())
    nm.onlineChanged.connect(ret.setOnline)
    return ret

  @memoizedproperty
  def scapeManager(self):
    dprint("create scape manager")
    import refman
    ret = refman.scape()
    #ret.setParent(self.q)
    nm = self.networkManager
    ret.setOnline(nm.isOnline())
    nm.onlineChanged.connect(ret.setOnline)
    return ret

  @memoizedproperty
  def dmmManager(self):
    import refman
    dprint("create dmm manager")
    ret = refman.dmm()
    #ret.setParent(self.q)
    nm = self.networkManager
    ret.setOnline(nm.isOnline())
    nm.onlineChanged.connect(ret.setOnline)
    return ret

  @memoizedproperty
  def tokutenManager(self):
    import refman
    dprint("create tokuten manager")
    ret = refman.tokuten()
    #ret.setParent(self.q)
    nm = self.networkManager
    ret.setOnline(nm.isOnline())
    nm.onlineChanged.connect(ret.setOnline)
    return ret

  @memoizedproperty
  def chineseManager(self):
    dprint("create chinese manager")
    import ccman
    ret = ccman.manager()

    ss = settings.global_()
    ret.setVariant(ss.chineseVariant())
    ss.chineseVariantChanged.connect(ret.setVariant)
    return ret

  @memoizedproperty
  def termManager(self):
    dprint("create term manager")
    import termman
    ret = termman.manager()
    ret.setParent(self.q)

    ss = settings.global_()

    ret.setTargetLanguage(ss.userLanguage())
    ss.userLanguageChanged.connect(ret.setTargetLanguage)

    ret.setEnabled(ss.isTermEnabled())
    ss.termEnabledChanged.connect(ret.setEnabled)

    ret.setHentaiEnabled(ss.isHentaiEnabled())
    ss.hentaiEnabledChanged.connect(ret.setHentaiEnabled)

    #ret.setSyntaxEnabled(ss.isTranslationSyntaxEnabled())
    #ss.translationSyntaxEnabledChanged.connect(ret.setSyntaxEnabled)

    ret.setMarked(ss.isTermMarked())
    ss.termMarkedChanged.connect(ret.setMarked)

    ret.setRubyEnabled(ss.isTermRubyEnabled())
    ss.termRubyEnabledChanged.connect(ret.setRubyEnabled)

    ret.setChineseRubyEnabled(ss.isTermChineseRomajiRubyEnabled())
    ss.termChineseRomajiRubyEnabledChanged.connect(ret.setChineseRubyEnabled)

    ret.setKoreanRubyEnabled(ss.isTermKoreanHanjaRubyEnabled())
    ss.termKoreanHanjaRubyEnabledChanged.connect(ret.setKoreanRubyEnabled)

    ret.setVietnameseRubyEnabled(ss.isTermVietnamesePhienamRubyEnabled())
    ss.termVietnamesePhienamRubyEnabledChanged.connect(ret.setVietnameseRubyEnabled)

    from jaconv import jaconv
    jaconv.setopt(macron=ss.isRomajiMacronEnabled())
    ss.romajiMacronEnabledChanged.connect(lambda t: jaconv.setopt(macron=t))

    for sig in (
        ss.userIdChanged, ss.userLanguageChanged,
        ss.hentaiEnabledChanged, #ss.termMarkedChanged,
        ss.termRubyEnabledChanged,
        ss.termChineseRomajiRubyEnabledChanged,
        ss.termKoreanHanjaRubyEnabledChanged,
        ss.termVietnamesePhienamRubyEnabledChanged,
        ss.romajiMacronEnabledChanged,
        #ss.translationSyntaxEnabledChanged,
        self.gameManager.processChanged,
        self.dataManager.termsChanged,
      ):
      sig.connect(ret.invalidateCache)

    self.dataManager.currentGameChanged.connect(ret.warmup, Qt.QueuedConnection)

    #for sig in ss.hentaiEnabledChanged, ss.termMarkedChanged:
    #  sig.connect(self.translatorManager.clearCache)
    #ret.cacheChanged.connect(self.translatorManager.clearCache)
    return ret

  #@memoizedproperty
  #def translationScriptManager(self):
  #  dprint("create translation script manager")
  #  import trscriptman
  #  ret = trscriptman.manager()
  #  ss = settings.global_()
  #  ret.setLanguageEnabled('ja', ss.isTranslationScriptJaEnabled())
  #  ret.setLanguageEnabled('en', ss.isTranslationScriptEnEnabled())
  #  ss.translationScriptJaEnabledChanged.connect(partial(ret.setLanguageEnabled, 'ja'))
  #  ss.translationScriptEnEnabledChanged.connect(partial(ret.setLanguageEnabled, 'en'))
  #  self.dataManager.translationScriptsChanged.connect(ret.reloadScripts)
  #  return ret

  #@memoizedproperty
  #def translationCacheManager(self):
  #  dprint("create translation cache manager")
  #  import trcache
  #  ret = trcache.manager()
  #  ret.setParent(self.q)
  #  return ret

  #@memoizedproperty
  #def tahScriptManager(self):
  #  import tahscript
  #  ret = tahscript.manager()
  #  ss = settings.global_()
  #  ret.setEnabled('atlas', ss.isAtlasScriptEnabled())
  #  ss.atlasScriptEnabledChanged.connect(partial(ret.setEnabled, 'atlas'))
  #  ret.setEnabled('lec', ss.isLecScriptEnabled())
  #  ss.lecScriptEnabledChanged.connect(partial(ret.setEnabled, 'lec'))
  #  return ret

  @memoizedproperty
  def hanziManager(self):
    dprint("create hanzi manager")
    import hanzidict
    ret = hanzidict.manager()
    ss = settings.global_()
    ret.setKanjiDicLanguages(ss.kanjiDicLanguages())
    ss.kanjiDicLanguagesChanged.connect(ret.setKanjiDicLanguages)
    ret.setHanjaEnabled(ss.isKanjiHanjaEnabled())
    ss.kanjiHanjaEnabledChanged.connect(ret.setHanjaEnabled)
    return ret

  @memoizedproperty
  def translatorManager(self):
    dprint("create translator manager")
    import trman
    ret = trman.manager()
    ret.setParent(self.q)

    ret.setOnline(self.networkManager.isOnline())
    self.networkManager.onlineChanged.connect(ret.setOnline)
    
    ss = settings.global_()
    dwarn("Mather FUCK!", ss.translateLanguage())
    if ss.translateLanguage() is None:
        ss.setTranslateLanguage(ss.userLanguage())
    dwarn("Mather FUCK!", ss.translateLanguage())
    ret.setLanguage(ss.translateLanguage())
    ss.userLanguageChanged.connect(ret.setLanguage)

    ret.setMarked(ss.isTermMarked())
    ss.termMarkedChanged.connect(ret.setMarked)

    ret.setRubyEnabled(ss.isTermRubyEnabled())
    ss.termRubyEnabledChanged.connect(ret.setRubyEnabled)

    ret.setConvertsAlphabet(ss.translatesAlphabet())
    ss.translatesAlphabetChanged.connect(ret.setConvertsAlphabet)

    ret.setYueEnabled(ss.isYueEnabled())
    ss.yueEnabledChanged.connect(ret.setYueEnabled)

    ret.setInfoseekEnabled(ss.isInfoseekEnabled())
    ss.infoseekEnabledChanged.connect(ret.setInfoseekEnabled)

    ret.setInfoseekAlignEnabled(ss.isInfoseekRubyEnabled())
    ss.infoseekRubyEnabledChanged.connect(ret.setInfoseekAlignEnabled)

    ret.setInfoseekScriptEnabled(ss.isInfoseekScriptEnabled())
    ss.infoseekScriptEnabledChanged.connect(ret.setInfoseekScriptEnabled)

    ret.setExciteEnabled(ss.isExciteEnabled())
    ss.exciteEnabledChanged.connect(ret.setExciteEnabled)

    ret.setExciteScriptEnabled(ss.isExciteScriptEnabled())
    ss.exciteScriptEnabledChanged.connect(ret.setExciteScriptEnabled)

    ret.setBabylonEnabled(ss.isBabylonEnabled())
    ss.babylonEnabledChanged.connect(ret.setBabylonEnabled)

    ret.setBabylonScriptEnabled(ss.isBabylonScriptEnabled())
    ss.babylonScriptEnabledChanged.connect(ret.setBabylonScriptEnabled)

    ret.setSystranEnabled(ss.isSystranEnabled())
    ss.systranEnabledChanged.connect(ret.setSystranEnabled)

    ret.setSystranScriptEnabled(ss.isSystranScriptEnabled())
    ss.systranScriptEnabledChanged.connect(ret.setSystranScriptEnabled)

    ret.setNiftyEnabled(ss.isNiftyEnabled())
    ss.niftyEnabledChanged.connect(ret.setNiftyEnabled)

    ret.setNiftyScriptEnabled(ss.isNiftyScriptEnabled())
    ss.niftyScriptEnabledChanged.connect(ret.setNiftyScriptEnabled)

    ret.setBingEnabled(ss.isBingEnabled())
    ss.bingEnabledChanged.connect(ret.setBingEnabled)

    ret.setBingAlignEnabled(ss.isBingRubyEnabled())
    ss.bingRubyEnabledChanged.connect(ret.setBingAlignEnabled)

    ret.setBingScriptEnabled(ss.isBingScriptEnabled())
    ss.bingScriptEnabledChanged.connect(ret.setBingScriptEnabled)

    ret.setGoogleEnabled(ss.isGoogleEnabled())
    ss.googleEnabledChanged.connect(ret.setGoogleEnabled)

    ret.setGoogleAlignEnabled(ss.isGoogleRubyEnabled())
    ss.googleRubyEnabledChanged.connect(ret.setGoogleAlignEnabled)

    ret.setGoogleScriptEnabled(ss.isGoogleScriptEnabled())
    ss.googleScriptEnabledChanged.connect(ret.setGoogleScriptEnabled)

    ret.setTransruEnabled(ss.isTransruEnabled())
    ss.transruEnabledChanged.connect(ret.setTransruEnabled)

    ret.setTransruScriptEnabled(ss.isTransruScriptEnabled())
    ss.transruScriptEnabledChanged.connect(ret.setTransruScriptEnabled)

    ret.setNaverEnabled(ss.isNaverEnabled())
    ss.naverEnabledChanged.connect(ret.setNaverEnabled)

    ret.setNaverAlignEnabled(ss.isNaverRubyEnabled())
    ss.naverRubyEnabledChanged.connect(ret.setNaverAlignEnabled)

    ret.setBaiduEnabled(ss.isBaiduEnabled())
    ss.baiduEnabledChanged.connect(ret.setBaiduEnabled)

    ret.setBaiduAlignEnabled(ss.isBaiduRubyEnabled())
    ss.baiduRubyEnabledChanged.connect(ret.setBaiduAlignEnabled)

    ret.setYoudaoEnabled(ss.isYoudaoEnabled())
    ss.youdaoEnabledChanged.connect(ret.setYoudaoEnabled)

    ret.setLecOnlineEnabled(ss.isLecOnlineEnabled())
    ss.lecOnlineEnabledChanged.connect(ret.setLecOnlineEnabled)

    ret.setLecOnlineScriptEnabled(ss.isLecOnlineScriptEnabled())
    ss.lecOnlineScriptEnabledChanged.connect(ret.setLecOnlineScriptEnabled)

    #ret.setYoudaoEnabled(ss.isYoudaoEnabled())
    #ss.youdaoEnabledChanged.connect(ret.setYoudaoEnabled)

    ret.setHanVietEnabled(ss.isHanVietEnabled())
    ss.hanVietEnabledChanged.connect(ret.setHanVietEnabled)

    ret.setHanVietAlignEnabled(ss.isHanVietRubyEnabled())
    ss.hanVietRubyEnabledChanged.connect(ret.setHanVietAlignEnabled)

    ret.setRomajiEnabled(ss.isRomajiEnabled())
    ss.romajiEnabledChanged.connect(ret.setRomajiEnabled)

    ret.setRomajiType(ss.romajiRubyType())
    ss.romajiRubyTypeChanged.connect(ret.setRomajiType)

    ret.setJBeijingEnabled(ss.isJBeijingEnabled())
    ss.jbeijingEnabledChanged.connect(ret.setJBeijingEnabled)

    ret.setTranscatEnabled(ss.isTranscatEnabled())
    ss.transcatEnabledChanged.connect(ret.setTranscatEnabled)

    ret.setVTransEnabled(ss.isVTransEnabled())
    ss.vtransEnabledChanged.connect(ret.setVTransEnabled)

    ret.setFastaitEnabled(ss.isFastaitEnabled())
    ss.fastaitEnabledChanged.connect(ret.setFastaitEnabled)

    ret.setDreyeEnabled(ss.isDreyeEnabled())
    ss.dreyeEnabledChanged.connect(ret.setDreyeEnabled)

    ret.setEzTransEnabled(ss.isEzTransEnabled())
    ss.ezTransEnabledChanged.connect(ret.setEzTransEnabled)
    ret.setEhndEnabled(ss.isEhndEnabled())
    ss.ehndEnabledChanged.connect(ret.setEhndEnabled)

    ret.setAtlasEnabled(ss.isAtlasEnabled())
    ss.atlasEnabledChanged.connect(ret.setAtlasEnabled)

    ret.setAtlasScriptEnabled(ss.isAtlasScriptEnabled())
    ss.atlasScriptEnabledChanged.connect(ret.setAtlasScriptEnabled)

    ret.setLecEnabled(ss.isLecEnabled())
    ss.lecEnabledChanged.connect(ret.setLecEnabled)

    ret.setLecScriptEnabled(ss.isLecScriptEnabled())
    ss.lecScriptEnabledChanged.connect(ret.setLecScriptEnabled)

    for sig in (
        self.termManager.cacheChanged,
        ss.machineTranslatorChanged,
        ss.termEnabledChanged,
        ss.yueEnabledChanged,
        ss.chineseVariantChanged,
        ss.romajiMacronEnabledChanged,
      ):
      sig.connect(ret.clearCache)

    qApp = QCoreApplication.instance()

    tm = self.textManager
    for sig in tm.cleared, tm.pageBreakReceived, qApp.aboutToQuit:
      sig.connect(ret.abort)
    return ret

  @memoizedproperty
  def rpcServer(self):
    q = self.q
    import rpcman
    ret = rpcman.manager()
    ret.setParent(q)
    ret.activated.connect(q.activate, Qt.QueuedConnection)
    #ret.arguments.connect(q.open_, Qt.QueuedConnection)

    #ret.agentConnected.connect(lambda pid:
    #    self.gameManager.setWindowHookConnected(True))

    return ret

  @memoizedproperty
  def coffeeBeanManager(self):
    dprint("create coffeebean manager")
    import coffeebean
    ret = coffeebean.manager()
    ret.setParent(self.q)
    return ret

  @memoizedproperty
  def subtitleEditorManager(self):
    dprint("create subtitle editor manager")
    import subedit
    ret = subedit.manager()
    #ret.setParent(self.q)
    self.gameManager.processChanged.connect(ret.hide)
    return ret

  @memoizedproperty
  def nameInputManager(self):
    dprint("create name input manager")
    import nameinput
    return nameinput.manager()

  #@memoizedproperty
  #def postInputManager(self):
  #  dprint("create post Input manager")
  #  import postinput
  #  ret = postinput.manager()
  #  ret.setParent(self.q)
  #  return ret

  #@memoizedproperty
  #def postEditorManager(self):
  #  dprint("create post editor manager")
  #  import postedit
  #  ret = postedit.manager()
  #  ret.setParent(self.q)
  #  return ret

  @property
  def gameEditorManager(self):
    import gameedit
    return gameedit.manager()

  @property
  def userViewManager(self):
    import userview
    return userview.manager()

  @property
  def gameViewManager(self):
    import gameview
    return gameview.manager()

  @property
  def topicViewManager(self):
    import topicview
    return topicview.manager()

  @property
  def topicsViewManager(self):
    import topicsview
    return topicsview.manager()

  @memoizedproperty
  def aboutDialog(self):
    import about
    ret = about.AboutDialog(self.topWindow)
    self.widgets.append(ret)
    return ret

  @memoizedproperty
  def updateDialog(self):
    import update
    ret = update.UpdateDialog(self.topWindow)
    self.widgets.append(ret)
    return ret

  @memoizedproperty
  def gameBoardDialog(self):
    import webrc
    webrc.init()
    import gameboard
    ret = gameboard.GameBoardDialog(self.normalWindow)
    self.widgets.append(ret)
    return ret

  @memoizedproperty
  def hotkeyManager(self):
    dprint("create hotkey manager")
    import hkman
    ret = hkman.manager()
    ret.setParent(self.q)
    return ret

  @memoizedproperty
  def speechRecognitionManager(self):
    dprint("create speech recognition manager")
    import srman
    ret = srman.manager()
    ret.setParent(self.q)

    ret.setOnline(self.networkManager.isOnline())
    self.networkManager.onlineChanged.connect(ret.setOnline)

    self.gameManager.processDetached.connect(ret.abort)

    ret.textRecognized.connect(self.textManager.addRecognizedText)

    import audioinfo, settings
    ss = settings.global_()
    dev = ss.audioDeviceIndex()
    if dev >= audioinfo.HOST_DEVICE_COUNT:
      ss.setAudioDeviceIndex(dev)
    ret.setDeviceIndex(dev)
    ss.audioDeviceIndexChanged.connect(ret.setDeviceIndex)

    ret.setLanguage(ss.speechRecognitionLanguage())
    ss.speechRecognitionLanguageChanged.connect(ret.setLanguage)
    return ret

  @memoizedproperty
  def ttsManager(self):
    dprint("create tts manager")
    import ttsman
    ret = ttsman.manager()
    ret.setParent(self.q)

    ret.setOnline(self.networkManager.isOnline())
    self.networkManager.onlineChanged.connect(ret.setOnline)

    ss = settings.global_()
    ret.setDefaultEngine(ss.ttsEngine())
    ss.ttsEngineChanged.connect(ret.setDefaultEngine)
    return ret

    #ret.setWindowsEngine(ss.windowsTtsEngine())
    #if ss.windowsTtsEngine() and not ret.windowsEngine():
    #  ss.setWindowsTtsEngine("")
    #ss.windowsTtsEngineChanged.connect(ret.setWindowsEngine)

    #ret.setMaleVoice(ss.maleVoice())
    #ss.maleVoiceChanged.connect(ret.setMaleVoice)
    #ret.setFemaleVoice(ss.femaleVoice())
    #ss.femaleVoiceChanged.connect(ret.setFemaleVoice)

    #ret.setMaleVoiceJa(ss.maleVoiceJa())
    #ss.maleVoiceJaChanged.connect(ret.setMaleVoiceJa)
    #ret.setFemaleVoiceJa(ss.femaleVoiceJa())
    #ss.femaleVoiceJaChanged.connect(ret.setFemaleVoiceJa)

    #ret.setWindowsEnabled(ss.isWindowsTtsEnabled())
    #ss.windowsTtsEnabledChanged.connect(ret.setWindowsEnabled)

    #ret.setGoogleEnabled(ss.isGoogleTtsEnabled())
    #ss.googleTtsEnabledChanged.connect(ret.setGoogleEnabled)

    #ret.setWindowsTtsSpeed(ss.windowsTtsSpeed())
    #ss.windowsTtsSpeedChanged.connect(ret.setWindowsTtsSpeed)

  #def _speakGameText(self, text, language='ja'):
  #  if settings.global_().speaksGameText():
  #    self.ttsManager.speak(text, termEnabled=True, language=language)

  ## Controllers ##

  #@memoizedproperty
  #def graffiti(self):
  #  import submaker
  #  return submaker.GraffitiController()

  @memoizedproperty
  def gospel(self):
    import kagami
    return kagami.GospelController

  @memoizedproperty
  def gossip(self):
    import kagami
    return kagami.GossipController

  @memoizedproperty
  def grimoire(self):
    import kagami
    return kagami.GrimoireController(self.q)

  @memoizedproperty
  def ocrPopup(self):
    import kagami
    return kagami.OcrPopupController() #(self.q)

  @memoizedproperty
  def ocrRegion(self):
    import kagami
    return kagami.OcrRegionController() #(self.q)

  @memoizedproperty
  def omajinai(self):
    import kagami
    return kagami.OmajinaiController(self.q)

  @memoizedproperty
  def mirage(self):
    import kagami
    return kagami.MirageController(self.q)

  @memoizedproperty
  def mirage(self):
    import kagami
    return kagami.MirageController(self.q)

  @memoizedproperty
  def gameFinderDialog(self):
    import refinput
    ret = refinput.GameFinder(self.normalWindow)
    self.widgets.append(ret)
    return ret

  @memoizedproperty
  def textReader(self):
    import textreader
    ret = textreader.manager()
    ret.setParent(self.q)

    m = self.mirage

    #ret.cleared.connect(self.translatorManager.abort)
    ret.pageBreakReceived.connect(self.translatorManager.abort)

    ret.pageBreakReceived.connect(m.pageBreak)
    ret.textReceived.connect(m.showText)
    ret.translationReceived.connect(m.showTranslation)

    ss = settings.global_()
    ret.setUserLanguage(ss.userLanguage())
    ss.userLanguageChanged.connect(ret.setUserLanguage)
    return ret

  @memoizedproperty
  def textSpy(self):
    import textspy
    ret = textspy.manager()
    ret.setParent(self.q)
    ret.textReceived.connect(self.textReader.addText)
    return ret

  ## Dialogs ##

  @memoizedproperty
  def kagamiWindow(self):
    dprint("create kagami")
    ret = qmldialog.Kagami(self.topWindow)
    self.widgets.append(ret)
    assert ret.rootObject(), "unless fail to load kagami.qml"
    return ret

  @memoizedproperty
  def subtitleMakerDialog(self):
    #dprint("create subtitle maker")
    ret = qmldialog.SubtitleMaker(self.topWindow)
    self.widgets.append(ret)

    assert ret.rootObject(), "unless fail to load submaker.qml"

    self.gameManager.processDetached.connect(ret.hide)
    return ret

  @memoizedproperty
  def referenceView(self):
    ret = qmldialog.ReferenceView(self.normalWindow)
    self.widgets.append(ret)
    assert ret.rootObject(), "unless fail to load refview.qml"
    return ret

  @memoizedproperty
  def subtitleView(self):
    ret = qmldialog.SubtitleView(self.normalWindow)
    self.widgets.append(ret)
    assert ret.rootObject(), "unless fail to load subview.qml"
    return ret

  @memoizedproperty
  def termView(self):
    ret = qmldialog.TermView(self.normalWindow)
    #ret.visibleChanged.connect(self.cometManager.subscribeTermTopic)
    self.widgets.append(ret)
    assert ret.rootObject(), "unless fail to load termview.qml"

    ret.visibleChanged.connect(self.dataManager.setTermsEditable)
    return ret

  @memoizedproperty
  def voiceView(self):
    ret = qmldialog.VoiceView(self.topWindow)
    self.gameManager.processDetached.connect(ret.hide)
    self.widgets.append(ret)
    assert ret.rootObject(), "unless fail to load voiceview.qml"
    return ret

  @memoizedproperty
  def gameWizardDialog(self):
    import gamewiz
    ret = gamewiz.GameWizard(self.topWindow)
    self.widgets.append(ret)
    return ret

  def isGameWizardVisible(self):
    return (
      hasmemoizedproperty(self, 'gameWizardDialog') and
      self.gameWizardDialog.isVisible())

  @memoizedproperty
  def prefsDialog(self):
    import prefs
    ret = prefs.PrefsDialog(self.topWindow)
    self.widgets.append(ret)
    return ret

  @memoizedproperty
  def termInputDialog(self):
    import terminput
    ret = terminput.TermInput(self.topWindow)
    self.widgets.append(ret)

    ss = settings.global_()
    ret.setBlockedLanguages(ss.blockedLanguages())
    ss.blockedLanguagesChanged.connect(ret.setBlockedLanguages)
    return ret

  @memoizedproperty
  def youTubeInputDialog(self):
    import ytinput
    return ytinput.YouTubeInput(self.topWindow)

  @memoizedproperty
  def dictionaryTesterDialog(self):
    import dictest
    ret = dictest.DictionaryTester(self.normalWindow)
    self.widgets.append(ret)
    return ret

  @memoizedproperty
  def machineTranslationTesterDialog(self):
    import mttest
    ret = mttest.MTTester(self.normalWindow)
    self.widgets.append(ret)
    return ret

  @memoizedproperty
  def speechRecognitionTesterDialog(self):
    import srtest
    ret = srtest.SpeechRecognitionTester(self.normalWindow)
    self.widgets.append(ret)
    return ret

  @memoizedproperty
  def syntaxTesterDialog(self):
    import syntaxtest
    ret = syntaxtest.SyntaxTester(self.normalWindow)
    self.widgets.append(ret)
    return ret

  @memoizedproperty
  def bbcodeTesterDialog(self):
    import bbtest
    ret = bbtest.BBCodeTester(self.topWindow)
    self.widgets.append(ret)
    return ret

  @memoizedproperty
  def regExpTesterDialog(self):
    import retest
    ret = retest.RegExpTester(self.topWindow)
    self.widgets.append(ret)
    return ret

  @memoizedproperty
  def appHelpDialog(self):
    import help
    ret = help.AppHelpDialog(self.topWindow)
    self.widgets.append(ret)
    return ret

  @memoizedproperty
  def creditsDialog(self):
    import help
    ret = help.CreditsDialog(self.normalWindow)
    self.widgets.append(ret)
    return ret

  @memoizedproperty
  def termHelpDialog(self):
    import help
    ret = help.TermHelpDialog(self.topWindow)
    self.widgets.append(ret)
    return ret

  @memoizedproperty
  def textReaderHelpDialog(self):
    import help
    ret = help.TextReaderHelpDialog(self.topWindow)
    self.widgets.append(ret)
    return ret

  @memoizedproperty
  def commentHelpDialog(self):
    import help
    ret = help.CommentHelpDialog(self.topWindow)
    self.widgets.append(ret)
    return ret

  @memoizedproperty
  def referenceHelpDialog(self):
    import help
    ret = help.ReferenceHelpDialog(self.normalWindow)
    self.widgets.append(ret)
    return ret

  @memoizedproperty
  def voiceHelpDialog(self):
    import help
    ret = help.VoiceHelpDialog(self.topWindow)
    self.widgets.append(ret)
    return ret

  @memoizedproperty
  def textPrefsDialog(self):
    import textprefs
    ret = textprefs.TextPrefsDialog(self.topWindow)
    self.widgets.append(ret)

    self.textHook.processDetached.connect(ret.hide)

    gm = self.gameManager
    ret.languageChanged.connect(gm.setLanguage)
    ret.removesRepeatTextChanged.connect(gm.setRemovesRepeat)
    ret.ignoresRepeatTextChanged.connect(gm.setIgnoresRepeat)
    ret.keepsSpaceChanged.connect(gm.setKeepsSpace)
    ret.keepsThreadsChanged.connect(gm.setThreadKept)
    ret.scenarioThreadChanged.connect(gm.setCurrentThread)
    ret.hookChanged.connect(gm.setCurrentHook)
    #ret.launchPathChanged.connect(gm.setLaunchPath)
    #ret.loaderChanged.connect(gm.setLoader)
    gm.processChanged.connect(ret.updateEnabled)

    ret.nameThreadChanged.connect(gm.setNameThread)
    ret.nameThreadDisabled.connect(gm.disableNameThread)
    ret.otherThreadsChanged.connect(gm.setOtherThreads)

    tm = self.textManager
    tm.cleared.connect(ret.clear)
    return ret

  @memoizedproperty
  def embeddedTextPrefsDialog(self):
    import embedprefs
    ret = embedprefs.TextPrefsDialog(self.topWindow)
    self.widgets.append(ret)

    agent = self.gameAgent
    agent.processDetached.connect(ret.hide)
    ret.visibleChanged.connect(agent.setExtractsAllTexts)

    gm = self.gameManager
    ret.languageChanged.connect(gm.setLanguage)
    #ret.removesRepeatTextChanged.connect(gm.setRemovesRepeat)
    #ret.ignoresRepeatTextChanged.connect(gm.setIgnoresRepeat)
    #ret.keepsSpaceChanged.connect(gm.setKeepsSpace)
    #ret.keepsThreadsChanged.connect(gm.setThreadKept)
    ret.scenarioThreadChanged.connect(gm.setCurrentThread)
    #ret.hookChanged.connect(gm.setCurrentHook)
    #ret.launchPathChanged.connect(gm.setLaunchPath)
    #ret.loaderChanged.connect(gm.setLoader)

    #gm.processChanged.connect(ret.updateEnabled)

    ret.nameThreadChanged.connect(gm.setNameThread)
    ret.nameThreadDisabled.connect(gm.disableNameThread)
    #ret.otherThreadsChanged.connect(gm.setOtherThreads)

    tm = self.textManager
    tm.cleared.connect(ret.clear)
    return ret

  # This function could take lots of time depending on how many games you have
  @memoizedproperty
  def springBoardDialog(self):
    try:
      if self.springBoardDialogLocked:
        dwarn("springboard locked")
        return
    except AttributeError:
      self.springBoardDialogLocked = True

    dprint("enter")
    import spring
    ret = spring.SpringBoard(self.normalWindow)
    self.widgets.append(ret)
    assert ret.rootObject(), "unless fail to load springboard.qml"

    # Hide springboard after open window
    gm = self.gameManager
    gm.processChanged.connect(ret.hide)
    gm.openingGame.connect(ret.hide)
    gm.openGameFailed.connect(ret.show)
    dprint("leave")

    self.springBoardDialogLocked = False
    return ret

  #@memoizedproperty
  def getCommentChartDialog(self, comments, md5=None):
    """
    @param  comments [Comment]
    @param* md5  unicode
    @return QWidget or None
    """
    try:
      w = self._commentChartDialog
      if not w.isReady():
        growl.notify(my.tr("Analyzing data ... patient!") + "&gt;&lt;")
        return

      if w.dataLength == len(comments) and w.md5 == md5:
        return w
      if w.isVisible(): w.hide()
      self.widgets.remove(w)
      w.setParent(None)
    except AttributeError: pass
    import chart
    ret = self._commentChartDialog = chart.CommentChartDialog()
    ret.init(comments, parent=self.topWindow)
    self.widgets.append(ret)
    ret.dataLength = len(comments)
    ret.md5 = md5
    return ret

  @memoizedproperty
  def termChartDialog(self):
    import chart
    ret = chart.TermChartDialog(self.dataManager.terms(),
        parent=self.normalWindow)
    self.widgets.append(ret)
    return ret

  ## Actions ##

  @debugmethod
  def exit(self, exitCode):
    """
    @param  exitCode  int
    """
    global EXITED
    if EXITED:
      return

    EXITED = True

    dprint("shutdown rpc server")
    self.rpcServer.stop()

    # Already stopped while quit
    #dprint("stop comets")
    #qmldialog.Kagami.instance.stopComets()

    import curtheme
    curtheme.unload()

    #self.cometManager.unsubscribeAll()
    #self.cometManager.waitall()

    if self.textHook.isActive():
      dprint("detach active process")
      self.textHook.detachProcess()

    # wait for for done or kill all threads
    if QThreadPool.globalInstance().activeThreadCount():
      dwarn("warning: wait for active threads")
      QThreadPool.globalInstance().waitForDone(config.QT_THREAD_TIMEOUT)
      dprint("leave qthread pool")

    dprint("quit qApp")
    qApp = QCoreApplication.instance()

    # Make sure settings.sync is the last signal conneced with aboutToQuit
    #qApp.aboutToQuit.connect(self.settings.sync)

    #skevents.runlater(qApp.quit)

    self.topWindow.setCanClose(True)
    self.normalWindow.setCanClose(True)

    # Make sure that sync is invoked at the end of about to quit
    ss = settings.global_()
    qApp.aboutToQuit.connect(ss.sync)

    qApp.exit(exitCode)

    #dprint("close root window")
    #skevents.runlater(self.topWindow.close)

    # wait for for done or kill all threads
    if QThreadPool.globalInstance().activeThreadCount():
      dwarn("active threads exist")
      #from sakurakit import skos
      #skos.kill_my_process()

  ## Game detection ##

  @memoizedproperty
  def gameDetectionTimer(self):
    ret = QTimer(self.q)
    ret.setInterval(5000) # 5 seconds
    ret.timeout.connect(lambda:
        settings.global_().isGameDetectionEnabled() and
        self._detectRunningGame())
    return ret

  def _detectRunningGame(self):
    if (not self.isGameWizardVisible() and
        not self.gameManager.currentGame() and
        not self.gameManager.isOpening() and
        not QThreadPool.globalInstance().activeThreadCount()):
      self.q.openRunningGame(verbose=False)

  @staticmethod
  def showWindow(w):
    """
    @param  w  QWidget
    """
    if w:
      if w.isMaximized() and w.isMinimized():
        w.showMaximized()
      elif w.isMinimized():
        w.showNormal()
      else:
        w.show()
      if not features.WINE:
        w.raise_()
        winutil.set_foreground_widget(w)

  @staticmethod
  def showQmlWindow(w):
    """
    @param  w  QDeclarativeView
    """
    if w:
      w.show()
      if w.isMaximized() and w.isMinimized():
        w.showMaximized()
      elif w.isMinimized():
        w.showNormal()
      if not features.WINE:
        w.raise_()
        winutil.set_foreground_widget(w)

  #def updateDialogParent(self, w):
  #  """
  #  @param  w  QWidget
  #  Set dialog parent to topWindow if fullScreen or normalWindow otherwise
  #  """
  #  #if not w.isVisible():
  #  parent = self.topWindow
  #  if parent is not w.parent():
  #    w.setParent(parent)

  # For debugging only
  #def dump(self):
  #  with open('dump.jichi', 'w') as f:
  #    for it in self.dataManager.getGameInfo():
  #      if not it.trailers:
  #        f.write("%s\n" % it.itemId)
  #    return
  #  data = self.dataManager.iterReferenceDigests()
  #  #import dataman
  #  #digs = [dataman.ReferenceDigest(type='amazon' if kw['key'].startswith('B') else 'dmm',
  #  #    **kw) for kw in data]
  #  with open('dump.jichi', 'w') as f:
  #    for it in data:
  #      if it.type != 'getchu':
  #        kw = self.referenceManager.queryOne(key=it.key,type=it.type)
  #        f.write('update game_ref set ref_brand="%s" where ref_id=%s;\n' % (kw.get('brand') if kw else 'nokw', it.id))

def manager(): return MainObject.instance

class MainObject(QObject):
  """Root of most objects
  """
  instance = None

  def __init__(self, parent=None):
    dprint('enter')
    super(MainObject, self).__init__(parent)
    self.__d = _MainObject(self)
    MainObject.instance = self

    dprint('leave')

  hideWindowRequested = Signal()

  #termViewVisibleChanged = Signal(bool)

  def topWindow(self): return self.__d.topWindow
  def normalWindow(self): return self.__d.normalWindow

  ## Actions ##

  def openRunningGame(self, verbose=True):
    d = self.__d
    gm = d.gameManager
    #if gm.currentGame():
    #  growl.warn(my.tr("Please close the current game first before opening new games"))
    #  return
    g = gm.findRunningGame()
    if g:
      dprint("find running game")
      growl.msg(my.tr("Found running game") + ":" "<br/>" + g.name)
      skevents.runlater(partial(
          gm.openGame, game=g),
          200)
    else:
      path = None
      if d.dataManager.hasGameFiles():
        path = gm.findRunningGamePathByMd5()
      if path:
        dprint("find running new game")
        growl.msg(my.tr("Found new game") + ":" "<br/>" + path)
        #if self.isOnline():
        skevents.runlater(partial(
            gm.openNewGame, path=path),
            200)
        #else:
        #  #growl.warn(my.tr("Because you are offline, please manually add game using Game Wizard"))
        #  #self.showGameWizard(path=path)
        #  self.addGame(path)
      else:
        if verbose:
          t = my.tr(
"""Unknown running game. You could try:
1. Update game database
2. Drag game lnk/exe to Spring Board
3. Reopen VNR as admin
4. Add the game using Game Wizard"""
) if not features.WINE else my.tr(
"""Unknown running game. You could try:
1. Update game database
2. Add the game using Game Wizard""")
          growl.warn(t.replace('\n', '<br/>'))
        #self.showGameWizard()

  def openGame(self, path=None, gameId=None):
    d = self.__d
    if not path:
      g = d.dataManager.queryGame(id=gameId)
      if not g or not g.path:
        dwarn("missing game path")
        return
      path = g.path
    from PySide.QtCore import QDir
    path = QDir.toNativeSeparators(path)
    linkName = ''
    if path.lower().endswith('.lnk'):
      linkName = os.path.splitext(os.path.basename(path))[0]
      path = winutil.resolve_link(path)
      if not path:
        return
    if not os.path.exists(path):
      growl.error(my.tr("File does not exist {0}").format(path))
      return
    import osutil
    np = osutil.normalize_path(path)
    import hashutil
    md5 = hashutil.md5sum(np)

    game = d.dataManager.queryGame(md5=md5, online=True)
    if game:
      d.gameManager.openGame(game=game, path=path,
          linkName=linkName)
    else:
      #if d.gameManager.containsGameMd5(md5) and self.isOnline():
      d.gameManager.openNewGame(path=path, md5=md5,
          linkName=linkName)
      #  else:
      #    growl.warn(my.tr("Because you are offline, please manually add game using Game Wizard"))
      #else:
      #  growl.notify(my.tr("It seems to be an unknown game. Please add it using Game Wizard"))
      #self.showGameWizard(path=path)
      #self.addGame(path)

  def addGame(self, path):
    if not path:
      return
    from PySide.QtCore import QDir
    path = QDir.toNativeSeparators(path)
    if path.lower().endswith('.lnk'):
      path = winutil.resolve_link(path)
      if not path:
        return
    if not os.path.exists(path):
      growl.error(my.tr("File does not exist {0}").format(path))
      return
    import osutil
    np = osutil.normalize_path(path)
    #import hashutil
    #md5 = hashutil.md5sum(np)

    self.__d.dataManager.addGame(path=path)

    #d = self.__d
    #if d.dataManager.containsGameMd5(md5, online=False):
    #  growl.notify(my.tr("The game already exists"))
    #  #if not d.dataManager.containsGamePath(path, online=False):
    #  return

      #if not d.dataManager.containsGameMd5(md5):
      #  growl.notify("<br/>".join((
      #      my.tr("It seems to be an unknown game."),
      #      my.tr("Please manually adjust Text Settings after launching the game."))))
      #elif not d.networkManager.isOnline():
      #  growl.notify("<br/>".join((
      #      my.tr("It seems you are offline.")
      #      my.tr("Please manually adjust Text Settings after launching the game."))))

  #def isDebug(self): return self.__d.debug

  def init(self):
    dprint("enter")
    d = self.__d

    dprint("show top window")
    d.topWindow.show()

    dprint("show non-top window")
    d.normalWindow.show()

    dprint("show tray icon")
    d.trayIcon.show()

    d.textHook # must be after topwindow show up and have a valid winId
    d.proxyManager
    d.networkManager
    #d.cometManager
    d.coffeeBeanManager
    d.kagamiWindow
    #d.subtitleMakerDialog

    online = self.isOnline()
    dprint("online = %s" % online)

    dm = d.dataManager
    tm = d.textManager
    gm = d.gameManager
    d.gameAgent

    d.chineseManager
    d.termManager
    #d.translationScriptManager
    #d.tahScriptManager
    d.translatorManager
    d.hanziManager
    #d.translationCacheManager
    d.dictionaryManager
    d.meCabManager
    #d.caboChaManager
    #d.jlpManager
    #d.nameManager
    d.referenceManager
    d.trailersManager
    d.dmmManager
    d.tokutenManager
    d.amazonManager
    d.getchuManager
    d.gyuttoManager
    d.scapeManager
    d.cacheManager
    #d.holysealManager
    #d.cacheManager.updateAvatar("AQKI6jsmz")
    d.subtitleEditorManager
    #d.postInputorManager
    #d.postEditorManager
    d.hotkeyManager
    d.ttsManager
    d.speechRecognitionManager

    #d.ocrManager
    skevents.runlater(d.initializeOCR, 3000) # delay start OCR

    #dprint("warm up tts")
    #d.ttsManager.warmup() # warm up zunko on the startup

    #if settings.global_().isEdictEnabled():
    #  dprint("warm up edict")
    #  import dicts
    #  dicts.edict()

    # Lingoes dictionaries
    #if settings.global_().isLingoesJaZhEnabled():
    #  dprint("warm up lingoes ja-zh")
    #  rc.lingoes_dict('ja-zh')

    #if settings.global_().isLingoesJaKoEnabled():
    #  dprint("warm up lingoes ja-ko")
    #  rc.lingoes_dict('ja-ko')

    #if settings.global_().isLingoesJaViEnabled():
    #  dprint("warm up lingoes ja-vi")
    #  rc.lingoes_dict('ja-vi')

    #dprint("create plugin manager")
    #d.pluginManager

    dprint("load data")
    dm.reloadGames()
    dm.reloadGameFiles() # Must after reloading games, so that I can fix the gameID on startup
    dm.reloadGameItems()
    #dm.reloadReferenceDigests()
    dm.reloadUsers()
    dm.reloadTerms()

    #if online and features.TEXT_TO_SPEECH:
    #  dprint("warm up google tts engine")
    #  d.googleTtsEngine.warmup()

    #if dm.hasTerms():
    #  dprint("warm up dictionary terms")
    #  d.termManager.warmup()

    dprint("enter")

  def run(self, args):
    """Starting point for the entire app
    @param  args  [unicode]  QCoreApplication.arguments()
    """
    dprint("enter: args =", args)

    d = self.__d
    dm = d.dataManager
    gm = d.gameManager

    online = self.isOnline()

    dprint("schedule to login later")

    user = dm.user()
    # Force broadcast user on startup
    if user and user.isLoginable() and not user.isGuest():
      dm.loginChanged.emit(user.name, user.password)
    skevents.runlater(dm.reloadUser)

    if online:
      if not dm.hasGameFiles():
        dprint("update game digest later")
        skevents.runlater(dm.updateGameFiles)

      if not dm.hasGameItems():
        dprint("update item digest later")
        skevents.runlater(dm.updateGameItems)

      #if not dm.hasReferenceDigests():
      #  dprint("update reference digest later")
      #  skevents.runlater(dm.updateReferenceDigests)

      if not dm.hasUsers():
        dprint("update user digest later")
        skevents.runlater(dm.updateUsers)

      if not dm.hasTerms():
        dprint("update terms later")
        skevents.runlater(dm.updateTerms)

      #if d.translationScriptManager.isEmpty() and settings.global_().isAnyTranslationScriptEnabled():
      #  dprint("update translate scripts later")
      #  skevents.runlater(dm.updateTranslationScripts)

    #self.showReferenceView()
    #return

    #dprint("warm up translators")
    #d.translatorManager.warmup()
    dprint("schedule to warm up translators")
    lang =  settings.global_().userLanguage()
    skevents.runlater(partial(
        d.translatorManager.warmup, to=lang)
        , 1000) # warm up after 1 seconds to avoid blocking on the startup

    dprint("start rpc server")
    d.rpcServer.start()

    #self.showTermChart()

    dprint("parse command line arguments")
    kwargs = _parseargs(args)
    dprint("args =", kwargs)

    opt_pid = kwargs.get('pid') or 0
    opt_minimize = bool(kwargs.get('minimize'))
    opt_nosplash = bool(kwargs.get('nosplash'))
    delayDisplayKagami = False

    dprint("search for running game")
    g = gm.findRunningGame(pid=opt_pid)
    if g:
      foundGame = True
      dprint("find running game")
      growl.msg(my.tr("Found running game") + ":" "<br/>" + g.name)
      skevents.runlater(partial(
          gm.openGame, game=g, pid=opt_pid),
          500)
    else:
      path = None
      if dm.hasGameFiles() and settings.global_().isGameDetectionEnabled():
        path = gm.findRunningGamePathByMd5(pid=opt_pid)
      if path:
        dprint("find running new game")
        growl.msg(my.tr("Found new game") + ":" "<br/>" + path)
        if online:
          skevents.runlater(partial(
              gm.openNewGame, path=path, pid=opt_pid),
              500)
        else:
          d.springBoardDialog
          skevents.runlater(self.showSpringBoard, 300)
          #skevents.runlater(self.showGameWizard, 400)
          #growl.warn(my.tr("Because you are offline, please manually add game using Game Wizard"))
      else:
        #self.showSpringBoard()
        if not opt_minimize:
          d.springBoardDialog
          skevents.runlater(self.showSpringBoard, 300)
        elif opt_nosplash:
          delayDisplayKagami = True

        #if not dm.hasGames():
        #  #self.showGameWizard()
        #  skevents.runlater(self.showGameWizard)
        #  pass

        if online:
          #skevents.runlater(self.checkQuickTime)
          skevents.runlater(partial(self.checkUpdate, force=False), 1000)

        # Greetings are disabled
        #skevents.runlater(self.checkGreeting, 7000)

    #if settings.global_().isAnyTranslationScriptEnabled():
    #  skevents.runlater(self.checkTranslationScripts, 60000) # 1min
    skevents.runlater(self.checkDigests, 90000) # 1.5min
    skevents.runlater(self.checkTerms, 120000) # 2min

    #if dm.hasTerms():
    #  dprint("warm up dictionary terms")
    #  d.termManager.warmup(async=True, interval=1000) # warm up after 1 second

    t = 10000 if delayDisplayKagami else 0
    if t:
      dprint("delay displaying kagami")
    else:
      dprint("show kagami at once")
    skevents.runlater(self.showKagami, t)

    dprint("start game detection")
    d.gameDetectionTimer.start()

    #if features.WINE:
    #  dprint("show dummy top window on wine")
    #  d.topWindowHolder.show()

    dprint("leave")

    #skevents.runlater(d.ocrManager.start, 5000) # 5 seconds
    #  import jsonapi
    #  jsonapi.gameinfo()
    #  d.dump()
    #  self.showGameBoard()

  def isOnline(self): return self.__d.networkManager.isOnline()

  ## Widgets ##

  def showKagami(self): self.__d.kagamiWindow.show()

  def showTextReader(self):
    if features.WINE:
      growl.warn(my.tr("The feature is not available on Wine"))
      return
    d = self.__d
    dprint("load text spy")
    d.textSpy
    d.kagamiWindow.setMirageVisible(True)
    d.mirage.show()

  def showTermView(self, search=None):
    """
    @param  seach  dict
    """
    d = self.__d
    #if d.termManager.isLocked():
    #  growl.msg(my.tr("Processing Shared Dictionary ... Please try later"));
    #else:
    d.dataManager.setTermsEditable(True)
    if search:
      import termview
      termview.search(**search)
    skevents.runlater(partial(_MainObject.showQmlWindow, d.termView))

  def searchTermView(self, **kwargs):
    if kwargs:
      import termview
      termview.search(**kwargs)
    self.showTermView()

  def showTerm(self, id): # long ->
    import termview
    termview.showterm(id=id)

  def showSpringBoard(self):
    skevents.runlater(partial(_MainObject.showQmlWindow, self.__d.springBoardDialog))
  def showVoiceSettings(self):
    skevents.runlater(partial(_MainObject.showQmlWindow, self.__d.voiceView))
  def showSubtitleMaker(self):
    skevents.runlater(partial(_MainObject.showQmlWindow, self.__d.subtitleMakerDialog))

  def showSubtitleView(self, game=None, gameId=0):
    """
    @param* game  dataman.GameObject
    @param* gameId  long
    """
    import dataman
    if dataman.CommentModel.locked:
      growl.notify(my.tr("Loading comment ... patient!") + "&gt;&lt;")
      return
    if not game:
      dm = self.__d.dataManager
      if gameId:
        game = dm.queryGameObject(id=gameId, digest=True)
      else:
        game = dm.currentGameObject()
    w = self.__d.subtitleView
    w.setGame(game)
    skevents.runlater(partial(_MainObject.showQmlWindow, w))

  def showReferenceView(self, gameId=0):
    """
    @param  gameId  dataman.GameObject or None
    """
    dm = self.__d.dataManager
    if not gameId:
      gameId = dm.currentGameId()
    if gameId:
      w = self.__d.referenceView
      w.setGameId(gameId)
      skevents.runlater(partial(_MainObject.showQmlWindow, w))
      return

  def showGameDiscussion(self, itemId=None):
    d = self.__d
    if not itemId:
      itemId = d.dataManager.currentGameItemId()
    if not itemId:
      growl.notify(my.tr("Unknown game. Please try editing the game information."))
    else:
      import osutil
      osutil.open_url("http://sakuradite.com/game/%s" % itemId)

  def showChatView(self, topicId):
    self.__d.topicsViewManager.show(topicId=topicId)
  def isChatViewVisible(self, topicId):
    return self.__d.topicsViewManager.isViewVisible(topicId=topicId)

  def showGameTopics(self, itemId):
    self.__d.topicsViewManager.show(subjectId=itemId)

  def showGameNames(self, itemId=0, tokenId=0, info=None): # long, long, GameInfo ->
    self.__d.nameInputManager.showGame(itemId=itemId, tokenId=tokenId, info=info)

  def showTopic(self, topicId):
    self.__d.topicViewManager.show(topicId)

  def showSubtitleEditor(self, comment): # dataman.Comment
    self.__d.subtitleEditorManager.showComment(comment)

  def showGameView(self, gameId=None, itemId=None): # long, long ->
    d = self.__d
    if itemId:
      d.gameViewManager.showItem(itemId)
    else:
      if not gameId:
        gameId = d.dataManager.currentGameId()
      if not gameId:
        growl.notify(my.tr("Unknown game. Please try updating the database."))
      else:
        d.gameViewManager.showGame(gameId)

  def showUserView(self, *args, **kwargs):
    """
    @param* id  long
    @param* hash  IP hash
    @param* name  unicode
    """
    self.__d.userViewManager.showUser(*args, **kwargs)

  def showTermInput(self, pattern='', text='', comment='', type='', language='', tokenId=0):
    w = self.__d.termInputDialog
    if not pattern:
      pattern = text
    if not text:
      text = pattern
    if pattern:
      w.setPattern(pattern)
    if text:
      w.setText(text)
    if comment:
      w.setComment(comment)
    if type:
      w.setType(type)
    if language:
      w.setLanguage(language)

    w.setTokenId(tokenId)
    _MainObject.showWindow(w)

  def showTextSettings(self):
    if self.__d.textHook.isAttached():
      _MainObject.showWindow(self.__d.textPrefsDialog)
    elif self.__d.gameAgent.engine():
      _MainObject.showWindow(self.__d.embeddedTextPrefsDialog)
    else:
      growl.notify(my.tr("Unknown game engine"))
    #  growl.notify(my.tr("I am sorry that this feature has not been implemented yet."))

  def searchGameBoard(self, text):
    """
    @param  text  unicode
    """
    self.showGameBoard()
    self.__d.gameBoardDialog.search(text)

  def showGameBoard(self): _MainObject.showWindow(self.__d.gameBoardDialog)
  def showYouTubeInput(self): _MainObject.showWindow(self.__d.youTubeInputDialog)
  def showDictionaryTester(self): _MainObject.showWindow(self.__d.dictionaryTesterDialog)
  def showMachineTranslationTester(self): _MainObject.showWindow(self.__d.machineTranslationTesterDialog)
  def showSpeechRecognitionTester(self): _MainObject.showWindow(self.__d.speechRecognitionTesterDialog)
  def showJapaneseSyntaxTester(self): _MainObject.showWindow(self.__d.syntaxTesterDialog)
  def showBBCodeTester(self): _MainObject.showWindow(self.__d.bbcodeTesterDialog)
  def showRegExpTester(self): _MainObject.showWindow(self.__d.regExpTesterDialog)
  def showGameFinder(self): _MainObject.showWindow(self.__d.gameFinderDialog)
  def showPreferences(self): _MainObject.showWindow(self.__d.prefsDialog)
  def showAbout(self): _MainObject.showWindow(self.__d.aboutDialog)
  def showHelp(self): _MainObject.showWindow(self.__d.appHelpDialog)

  def showTermHelp(self): _MainObject.showWindow(self.__d.termHelpDialog)
  def showTextReaderHelp(self): _MainObject.showWindow(self.__d.textReaderHelpDialog)
  def showCommentHelp(self): _MainObject.showWindow(self.__d.commentHelpDialog)
  def showReferenceHelp(self): _MainObject.showWindow(self.__d.referenceHelpDialog)
  def showVoiceHelp(self): _MainObject.showWindow(self.__d.voiceHelpDialog)

  def lookupDictionaryTester(self, text): # unicode ->
    self.showDictionaryTester()
    self.__d.dictionaryTesterDialog.lookup(text)

  def showTermCache(self):
    growl.msg(my.tr("Browse current enabled terms"))
    import osutil
    osutil.open_location(rc.DIR_TMP_TERM)

  def showGameWizard(self, path=None):
    w = self.__d.gameWizardDialog
    _MainObject.showWindow(w)
    if path:
      w.restartWithGameLocation(path)

  ## Actions ##

  help = showHelp
  about = showAbout

  def openWiki(self, text, language=''):
    """
    @param  text  unicode
    @param* language  str
    """
    if not language:
      language = self.__d.dataManager.user().language
    import osutil
    url = rc.wiki_url(text, language=language)
    osutil.open_url(url)

  def showCredits(self):
    self.openWiki('VNR/Credits', 'en')
    #_MainObject.showWindow(self.__d.creditsDialog)

  # Show comments online
  #def liveEdit(self):
  #  dm = self.__d.dataManager
  #  gameId = dm.currentGameId()
  #  if not gameId:
  #    growl.warn(my.tr("No running game"))
  #    return
  #  userName = dm.user().name
  #  password = dm.user().password

  #  import urllib
  #  url = ("http://sakuradite.com/?action=show/comment&gameid=%i&login=%s&password=%s"
  #      % (gameId,
  #        urllib.quote_plus(userName) if userName else '',
  #        urllib.quote_plus(password) if password else ''))
  #  growl.msg(my.tr("Opening web browser") + " ...")
  #  import osutil
  #  osutil.open_url(url)

  #def checkQuickTime(self):
  #  if settings.global_().isQuickTimeEnabled() and not libman.quicktime().exists():
  #    self.__d.quickTimeDialog.exec_()

  def checkUpdate(self, force=True):
    if not self.isOnline():
      if force:
        growl.notify(my.tr("Update requires Internet access"))
      return
    ss = settings.global_()
    d = self.__d
    now = skdatetime.current_unixtime()
    if not force and now < ss.updateTime() + config.APP_UPDATE_INTERVAL:
      return
    ss.setUpdateTime(now)
    current = config.VERSION_TIMESTAMP

    latest = self.__d.networkManager.queryVersion()
    if not latest or latest <= current:
      if force:
        growl.notify(my.tr("You are using the latest app"))
      return

    msg = self.__d.networkManager.getUpdateMessage(ss.userLanguage())

    growl.notify(my.tr("Update released"))

    # TTS
    #f = [
    #  u"ソフトを更新しますか？姉さま？",
    #  u"ソフトを更新しますか？姉うえ？",
    #]
    #m = [
    #  u"ソフトを更新しますか？ニー様？",
    #  u"ソフトを更新しますか？お兄ちゃん？",
    #]
    #if d.dataManager.user().isFemale():
    #  t = f[now % len(f)]
    #elif d.dataManager.user().gender:
    #  t = m[now % len(m)]
    #else:
    #  t = (f+m)[now % (len(f)+len(m))]
    #d.ttsManager.speak(t, verbose=False)

    if msg:
      ss.setUpdateTime(0)
      from Qt5.QtWidgets import QMessageBox
      parentWindow = d.topWindow
      QMessageBox.information(parentWindow,
          my.tr("Critical update message"),
          msg)

    self.showUpdate()

  def showUpdate(self):
    _MainObject.showWindow(self.__d.updateDialog)

  def confirmUpdateGameDatabase(self):
    if prompt.confirmUpdateGameFiles():
      self.__d.dataManager.updateGameDatabase()

  def checkDigests(self):
    if not self.isOnline():
      return
    dprint("enter")
    d = self.__d
    ss = settings.global_()
    now = skdatetime.current_unixtime()
    ts = min(ss.gameFilesTime(), ss.gameFilesTime(), ss.userDigestsTime())
    if now > ts + config.APP_UPDATE_GAMES_INTERVAL:
      d.dataManager.updateGameDatabase()
    dprint("leave")

  def checkTerms(self):
    dprint("enter")
    if not self.isOnline():
      return
    now = skdatetime.current_unixtime()
    if now < settings.global_().termsTime() + config.APP_UPDATE_TERMS_INTERVAL:
      dprint("leave: ignore")
      return
    self.__d.dataManager.updateTerms()
    dprint("leave")

  #def checkTranslationScripts(self):
  #  dprint("enter")
  #  if not self.isOnline():
  #    return
  #  now = skdatetime.current_unixtime()
  #  if now < settings.global_().translationScriptTime() + config.APP_UPDATE_TAH_INTERVAL:
  #    dprint("leave: ignore")
  #    return
  #  self.__d.dataManager.updateTranslationScripts()
  #  dprint("leave")

  def checkGreeting(self):
    if not self.isOnline():
      return
    now = skdatetime.current_unixtime()
    if now < settings.global_().greetingTime() + config.APP_GREETING_INTERVAL:
      return
    settings.global_().setGreetingTime(now)
    self.showGreeting()

  def showGreeting(self):
    if not self.isOnline():
      return
    from datetime import datetime
    import messages
    d = self.__d
    now = datetime.now()
    random = now.second
    greetings = (
      messages.GREETINGS_MORNING if now.hour >= 6 and now.hour <= 10 else
      messages.GREETINGS_DAY if now.hour >= 11 and now.hour <= 16 else
      messages.GREETINGS_EVENING
    )
    gender = d.dataManager.user().gender
    if gender == 'f':
      g = greetings['female'] + greetings['any']
    elif gender == 'm':
      g = greetings['male'] + greetings['any']
    else:
      g = greetings['any']

    text = g[random % len(g)]
    d.ttsManager.speak(text, verbose=False)

  ## Show ##

  def activate(self):
    """Supposed to show and raise the main window"""
    self.showSpringBoard()

  #def showCommentAnalytics(self):
  #  self.__d.dataMiner.showCommentAnalytics()
  #  dprint("pass")

  #def showCommentCredits(self):
  #  d = self.__d
  #  if not d.dataManager.hasComments():
  #    growl.msg(self.tr("No subtitles"))
  #  else:
  #    d.omajinai.clear()
  #    d.omajinai.append(self.tr("Subtitle Credits:"))
  #    for userName, count in d.dataMiner.commentUserCounts().iteritems():
  #      d.omajinai.append("* %s (%i)" % (userName, count), 'en')
  #  dprint("pass")

  def showTermChart(self):
    if not self.__d.dataManager.hasTerms():
      growl.warn(my.tr(
        "The dictionary is empty. Please refresh it when you are online."
      ))
    else: _MainObject.showWindow(self.__d.termChartDialog)
    dprint("pass")

  def showWebBrowser(self):
    from scripts import browser
    browser.open()

  def showCommentChart(self, comments, md5=None):
    """
    @param  comments  [dataman.Comment]
    @param* md5  str
    """
    #if not md5:
    #  return
    #d = self.__d
    #dm = d.gameManager
    #l = dm.queryComments(md5=md5)  if md5 else dm.comments()
    if not comments:
      growl.warn(my.tr("There are no user-contributed subtitles"))
    else:
      w = self.__d.getCommentChartDialog(comments, md5)
      if w: _MainObject.showWindow(w)
    dprint("pass")

  ## Quit ##

  def quit(self): self.exit(defs.EXIT_SUCCEED)
  def restart(self): self.exit(defs.EXIT_RESTART)

  def confirmQuit(self):
    if prompt.confirmQuit():
      self.quit()
  def confirmRestart(self):
    if prompt.confirmRestart():
      self.restart()

  def exit(self, exitCode, interval=200):
    dprint("enter: interval = %i" % interval)
    if EXITED:
      dprint("leave: has quit")
      return

    d = self.__d

    dprint("stop hot keys")
    d.hotkeyManager.setEnabled(False)

    dprint("hide all windows")
    d.trayIcon.hide()
    d.normalWindow.hide()
    d.topWindow.hide()

    for w in d.widgets:
      if w.isVisible():
        w.hide()

    for p in (
        'subtitleEditorManager',
        'nameInputManager',
        'gameEditorManager',
        'gameViewManager',
        'userViewManager',
        'topicViewManager',
        'topicsViewManager',
      ):
      if hasmemoizedproperty(self, p):
        getattr(self, p).hide()

    self.hideWindowRequested.emit()

    #dprint("stop google tts engine")
    #d.googleTtsEngine.stop()

    dprint("save local changes")
    d.dataManager.submitDirtyComments()

    # Stop earlier to give them time to send stop messages
    dprint("stop comets")
    qmldialog.Kagami.instance.stopComets()

    #if d.gameManager.isWindowHookConnected:
    #  d.rpcServer.disableAgent()
    d.gameAgent.quit()

    skevents.runlater(partial(d.exit, exitCode), interval)
    dprint("leave")

  def openExistingGame(self, path, launchPath=''): # unicode, unicode ->
    self.__d.gameManager.openExecutable(path, launchPath=launchPath)

#@QmlObject
class MainObjectProxy(QObject):
  def __init__(self, parent=None):
    super(MainObjectProxy, self).__init__(parent)

  @Slot()
  def showWebBrowser(self): manager().showWebBrowser()

  #@Slot()
  #def showOmajinai(self): manager().showOmajinai()
  @Slot()
  def showSpringBoard(self): manager().showSpringBoard()
  @Slot()
  def showGameDiscussion(self): manager().showGameDiscussion()
  @Slot()
  def showGameBoard(self): manager().showGameBoard()
  @Slot()
  def showSubtitleMaker(self): manager().showSubtitleMaker()
  @Slot()
  def showSubtitleView(self): manager().showSubtitleView()
  @Slot()
  def showTextSettings(self): manager().showTextSettings()
  @Slot()
  def showGameWizard(self): manager().showGameWizard()
  @Slot()
  def showPreferences(self): manager().showPreferences()
  @Slot()
  def showTermInput(self): manager().showTermInput()
  @Slot()
  def showYouTubeInput(self): manager().showYouTubeInput()
  @Slot()
  def showDictionaryTester(self): manager().showDictionaryTester()
  @Slot(unicode)
  def lookupDictionaryTester(self, text): manager().lookupDictionaryTester(text)
  @Slot()
  def showMachineTranslationTester(self): manager().showMachineTranslationTester()
  @Slot()
  def showSpeechRecognitionTester(self): manager().showSpeechRecognitionTester()
  @Slot()
  def showJapaneseSyntaxTester(self): manager().showJapaneseSyntaxTester()
  @Slot()
  def showBBCodeTester(self): manager().showBBCodeTester()
  @Slot()
  def showRegExpTester(self): manager().showRegExpTester()
  @Slot()
  def showTermChart(self): manager().showTermChart()
  #@Slot()
  #def showCommentAnalytics(self): manager().showCommentAnalytics()
  @Slot()
  def showCommentCredits(self): manager().showCommentCredits()
  #@Slot(int)
  #def showReferenceView(self, gameId): manager().showReferenceView(gameId=gameId)
  @Slot()
  def liveEdit(self): manager().liveEdit()
  @Slot()
  def help(self): manager().help()
  @Slot()
  def about(self): manager().about()
  @Slot()
  def quit(self): manager().quit()
  @Slot()
  def restart(self): manager().restart()
  @Slot()
  def update(self): manager().showUpdate()
  @Slot()
  def checkUpdate(self): manager().checkUpdate()
  @Slot()
  def openRunningGame(self): manager().openRunningGame()
  #@Slot()
  #def showTermView(self): manager().showTermView()
  @Slot()
  def showDictionary(self): manager().showTermView() # alias
  @Slot(unicode, unicode)
  def searchDictionary(self, text, col): manager().searchTermView(text=text, col=col)
  @Slot()
  def showGameFinder(self): manager().showGameFinder()
  @Slot()
  def showCredits(self): manager().showCredits()
  @Slot()
  def showVoiceSettings(self): manager().showVoiceSettings()
  @Slot()
  def showTermHelp(self): manager().showTermHelp()
  @Slot()
  def showTermCache(self): manager().showTermCache()
  @Slot()
  def showCommentHelp(self): manager().showCommentHelp()
  @Slot()
  def showReferenceHelp(self): manager().showReferenceHelp()
  @Slot()
  def showVoiceHelp(self): manager().showVoiceHelp()
  @Slot()
  def confirmQuit(self): manager().confirmQuit()
  @Slot()
  def confirmUpdateGameDatabase(self): manager().confirmUpdateGameDatabase()
  @Slot()
  def confirmRestart(self): manager().confirmRestart()
  @Slot()
  def showTextReader(self): manager().showTextReader()
  @Slot()
  def showTextReaderHelp(self): manager().showTextReaderHelp()
  @Slot()
  def showCurrentGameView(self): manager().showGameView()
  @Slot(int)
  def showGameView(self, gameId): manager().showGameView(gameId)
  @Slot(int)
  def showGameNames(self, itemId): manager().showGameNames(itemId=itemId)
  @Slot(QObject) # dataman.Comment
  def showSubtitleEditor(self, comment): manager().showSubtitleEditor(comment)

  @Slot()
  def showGlobalChatView(self): manager().showChatView(config.GLOBAL_TOPIC_ID)
  @Slot(result=bool)
  def isGlobalChatViewVisible(self): return manager().isChatViewVisible(config.GLOBAL_TOPIC_ID)

  @Slot(long)
  def showTopic(self, topicId): manager().showTopic(topicId)
  @Slot(long)
  def showGameTopics(self, gameId): manager().showGameTopics(gameId)

  #@Slot(long, long, unicode)
  #def showUserView(self, id, hash, name): manager().showUserView(id, hash, name)
  @Slot(unicode)
  def showUser(self, name): manager().showUserView(name=name) # use name by default
  @Slot(unicode)
  def showUserWithName(self, name): manager().showUserView(name=name)
  @Slot(long)
  def showUserWithId(self, id): manager().showUserView(id=id)
  @Slot(long, long)
  def showUserWithHash(self, id, hash): manager().showUserView(id=id, hash=hash)

  @Slot(long)
  def showTermWithId(self, id): manager().showTerm(id=id)

  @Slot(QObject) # dataman.GameObject
  def showGameObjectSubtitles(self, g): manager().showSubtitleView(game=g)

  @Slot(unicode, unicode, unicode)
  def showNewTerm(self, pattern, type, language):
    manager().showTermInput(pattern, type=type, language=language)

  @Slot(unicode)
  def openWiki(self, text): manager().openWiki(text)

  @Slot(unicode)
  def launchGameWithPath(self, path): manager().openExistingGame(path)
  @Slot(unicode, unicode)
  def launchGameWithLaunchPath(self, path, launchPath): manager().openExistingGame(path, launchPath=launchPath)

  #@Slot(int)
  #def showGameSubtitles(self, gameId): manager().showSubtitleView(gameId=gameId)

  #@Slot(str) # md5
  #def showCommentChart(self, md5): manager().showCommentChart(md5)

  def setWindowRefreshInterval(self, value):
    if value != self.windowRefreshInterval:
      manager().topWindow().setRefreshInterval(value)
      self.windowRefreshIntervalChanged.emit(value)
  windowRefreshIntervalChanged = Signal(int)
  windowRefreshInterval = Property(int,
      lambda _: manager().topWindow().refreshInterval(),
      setWindowRefreshInterval,
      notify=windowRefreshIntervalChanged)

# EOF
