# coding: utf8
# trman.py
# 10/8/2012 jichi
#
# Terminology:
# - data: raw game text byte code
# - text: original game text
# - translation: machine translation
# - comment: user's subtitle or comment

#from sakurakit.skprof import SkProfiler

import itertools
from functools import partial
from PySide.QtCore import QObject, Signal, Slot, Qt
from sakurakit import skevents, skthreads
from sakurakit.skclass import  memoized, memoizedproperty, hasmemoizedproperty
from sakurakit.skdebug import dprint, dwarn
from share.mt import mtinfo
import config, features, richutil, settings, textutil
import _trman

_RETRANS_DEFAULT_LANG = 'en'
_RETRANS_DEFAULT_KEY = 'bing'

#@Q_Q
class _TranslatorManager(object):

  def __init__(self, abortSignal):
    self.abortSignal = abortSignal # signal

    self.online = False
    self.language = 'en' # str, user language

    self.convertsAlphabet = False
    self.yueEnabled = False # translate zh to yue

    self.allTranslators = [] # all created translators
    self.marked = False
    self.rubyEnabled = False

    self.romajiEnabled = \
    self.infoseekEnabled = \
    self.exciteEnabled = \
    self.niftyEnabled = \
    self.systranEnabled = \
    self.babylonEnabled = \
    self.bingEnabled = \
    self.googleEnabled = \
    self.naverEnabled = \
    self.vtransEnabled = \
    self.baiduEnabled = \
    self.youdaoEnabled = \
    self.lecOnlineEnabled = \
    self.transruEnabled = \
    self.hanVietEnabled = \
    self.jbeijingEnabled = \
    self.fastaitEnabled = \
    self.dreyeEnabled = \
    self.ezTransEnabled = \
    self.transcatEnabled = \
    self.atlasEnabled = \
    self.lecEnabled = \
    False # bool

    self.ehndEnabled = True

    self.romajiType = 'romaji'

    self.alignEnabled = {} # {str key:bool t}
    self.scriptEnabled = {} # {str key:bool t}

    self.retrans = {} # {str key:_trman.Retranslator}

    # {str key:{'yes':bool,'key':str,'lang':str}}
    self.retransSettings = settings.global_().retranslatorSettings() or {}
    # Example:
    #self.retransSettings = {
    #  'jbeijing': {'yes':True, 'key': 'hanviet', 'lang':'zhs'},
    #}

    from PySide.QtNetwork import QNetworkAccessManager
    nam = QNetworkAccessManager() # parent is not assigned
    from qtrequests import qtrequests
    self.session = qtrequests.Session(nam, abortSignal=self.abortSignal, requestTimeout=config.APP_ONLINE_TRANSLATION_TIMEOUT)

  normalizeText = staticmethod(textutil.normalize_punct)

  def clearCache(self):
    for it in self.allTranslators:
      it.clearCache()
    dprint("pass")

  def getAlignEnabled(self, key): return self.alignEnabled.get(key) or False # str -> bool
  def setAlignEnabled(self, key, t): self.alignEnabled[key] = t # str, bool ->

  def getScriptEnabled(self, key): return self.scriptEnabled.get(key) or False # str -> bool
  def setScriptEnabled(self, key, t): # str, bool ->
    if self.scriptEnabled.get(key) != t:
      self.scriptEnabled[key] = t
      if self.hasTranslator(key):
        mt = self.getTranslator(key)
        dprint("clear cache for %s" % key)
        mt.clearCache()

  def _createDefaultRetransSettings(self, engine):
    """
    @param  engine  str
    @return  kw
    """
    lang = _RETRANS_DEFAULT_LANG
    langs = mtinfo.get_t_langs(engine)
    if langs:
      for it in config.LANGUAGES:
        if it in langs:
          lang = it
          break
    return {'yes': False, 'lang': lang, 'key': _RETRANS_DEFAULT_KEY}

  def updateRetransSettings(self, engine, key, value):
    """
    @param  engine  str
    @param  key  str
    @param  value  any
    """
    if not engine or not key: # this should never happen, or it is a bug in Preferences
      dwarn("missing engine or key")
      return
    try:
      s = self.retransSettings.get(engine)
      if not s:
        s = self._createDefaultRetransSettings(engine)
      if s[key] != value:
        self.retransSettings[engine] = s
        s[key] = value
        settings.global_().setRetranslatorSettings(self.retransSettings)
        #self.clearCache()
    except:
      s = self._createDefaultRetransSettings(engine)
      s[key] = value
      self.retransSettings[engine] = s
      settings.global_().setRetranslatorSettings(self.retransSettings)
      #self.clearCache()

  def postprocessCharacterset(self, text, language):
    if self.yueEnabled and language.startswith('zh') and self.online:
      ret = self.yueTranslator.translate(text, fr=language)
      if ret:
        return ret
    if self.convertsAlphabet:
      text = textutil.convert_html_alphabet(text, language)
    return text

  def _newtr(self, tr):
    """
    @param  tr  _trman.Translator
    """
    self.allTranslators.append(tr)
    return tr

  def getRetranslator(self, key1, key2, language):
    """
    @param  key1  str
    @param  key2  str
    @param  language  str
    """
    ret = self.retrans.get(key1)
    if ret:
      if ret.language != language:
        ret.language = language
      if ret.second.key != key2:
        ret.second = self.getTranslator(key2)
    else:
      ret = self.retrans[key1] = _trman.Retranslator(
          first=self.getTranslator(key1),
          second=self.getTranslator(key2),
          language=language)
    return ret

  @memoizedproperty # no an independent machine translator
  def yueTranslator(self): return _trman.YueTranslator(
      abortSignal=self.abortSignal,
      session=self.session)

  @memoizedproperty
  def romajiTranslator(self): return self._newtr(_trman.RomajiTranslator(rubyType=self.romajiType))

  @memoizedproperty
  def atlasTranslator(self): return self._newtr(_trman.AtlasTranslator())

  @memoizedproperty
  def lecTranslator(self): return self._newtr(_trman.LecTranslator(postprocess=self.postprocessCharacterset))

  @memoizedproperty
  def ezTranslator(self): return self._newtr(_trman.EzTranslator(ehndEnabled=self.ehndEnabled))

  @memoizedproperty
  def transcatTranslator(self): return self._newtr(_trman.TransCATTranslator())

  @memoizedproperty
  def fastaitTranslator(self): return self._newtr(_trman.FastAITTranslator(postprocess=self.postprocessCharacterset))

  @memoizedproperty
  def dreyeTranslator(self): return self._newtr(self._newtr(_trman.DreyeTranslator(postprocess=self.postprocessCharacterset)))

  @memoizedproperty
  def jbeijingTranslator(self): return self._newtr(_trman.JBeijingTranslator(postprocess=self.postprocessCharacterset))

  @memoizedproperty
  def hanVietTranslator(self): return self._newtr(_trman.HanVietTranslator())

  @memoizedproperty
  def vTranslator(self):
    return self._newtr(_trman.VTranslator(
        abortSignal=self.abortSignal,
        session=self.session,
        postprocess=self.postprocessCharacterset))

  @memoizedproperty
  def googleTranslator(self):
    return self._newtr(_trman.GoogleTranslator(
        abortSignal=self.abortSignal,
        session=self.session,
        postprocess=self.postprocessCharacterset))

  @memoizedproperty
  def bingTranslator(self):
    return self._newtr(_trman.BingTranslator(
        abortSignal=self.abortSignal,
        session=self.session,
        postprocess=self.postprocessCharacterset))

  @memoizedproperty
  def baiduTranslator(self):
    return self._newtr(_trman.BaiduTranslator(
        abortSignal=self.abortSignal,
        session=self.session,
        postprocess=self.postprocessCharacterset))

  @memoizedproperty
  def youdaoTranslator(self):
    return self._newtr(_trman.YoudaoTranslator(
        abortSignal=self.abortSignal,
        session=self.session,
        postprocess=self.postprocessCharacterset))

  @memoizedproperty
  def naverTranslator(self):
    return self._newtr(_trman.NaverTranslator(
        abortSignal=self.abortSignal,
        session=self.session,
        postprocess=self.postprocessCharacterset))

  @memoizedproperty
  def lecOnlineTranslator(self):
    return self._newtr(_trman.LecOnlineTranslator(
        abortSignal=self.abortSignal,
        session=self.session,
        postprocess=self.postprocessCharacterset))

  @memoizedproperty
  def transruTranslator(self):
    return self._newtr(_trman.TransruTranslator(
        abortSignal=self.abortSignal,
        session=self.session,
        postprocess=self.postprocessCharacterset))

  @memoizedproperty
  def infoseekTranslator(self):
    return self._newtr(_trman.InfoseekTranslator(
        abortSignal=self.abortSignal,
        session=self.session,
        postprocess=self.postprocessCharacterset))

  @memoizedproperty
  def exciteTranslator(self):
    return self._newtr(_trman.ExciteTranslator(
        abortSignal=self.abortSignal,
        session=self.session,
        postprocess=self.postprocessCharacterset))

  @memoizedproperty
  def babylonTranslator(self):
    return self._newtr(_trman.BabylonTranslator(
        abortSignal=self.abortSignal,
        session=self.session,
        postprocess=self.postprocessCharacterset))

  @memoizedproperty
  def systranTranslator(self):
    return self._newtr(_trman.SystranTranslator(
        abortSignal=self.abortSignal,
        session=self.session,
        postprocess=self.postprocessCharacterset))

  @memoizedproperty
  def niftyTranslator(self):
    return self._newtr(_trman.NiftyTranslator(
        abortSignal=self.abortSignal,
        session=self.session,
        postprocess=self.postprocessCharacterset))

  def translateAndApply(self, func, kw, tr, text, align=None, rubyEnabled=None, **kwargs):
    """
    @param  func  function to apply
    @param  kw  arguments passed to func
    @param  tr  function to translate
    @param  text  unicode  passed to tr
    @param* align  list or None
    @param  **kwargs  passed to tr
    """
    # TODO: I might be able to do runsync here instead of within tr
    #async = kwargs.get('async')
    #if async:
    #  kwargs['async'] = False
    #  r = skthreads.runsync(partial(tr, *args, **kwargs),
    #      abortSignal=self.abortSignal)
    #else:
    r = tr(text, align=align, **kwargs)
    if r and r[0]:
      t = r[0]
      if self.rubyEnabled and rubyEnabled == False:
        t = richutil.removeRuby(t)
      func(t, r[1], r[2], align, **kw)

  def _getTranslatorPropertyName(self, key):
    """
    @param  key  str
    @return  str
    """
    if key == 'eztrans':
      return 'ezTranslator'
    if key == 'lecol':
      return 'lecOnlineTranslator'
    if key == 'transru':
      return 'transruTranslator'
    if key == 'hanviet':
      return 'hanVietTranslator'
    if key == 'vtrans':
      return 'vTranslator'
    return key + 'Translator'

  def getTranslator(self, key):
    """
    @param  key  str
    @return  TranslatorEngine or None
    """
    v = self._getTranslatorPropertyName(key)
    try: return getattr(self, v)
    except AttributeError: pass

  def hasTranslator(self, key):
    """
    @param  key  str
    @return  TranslatorEngine or None
    """
    v = self._getTranslatorPropertyName(key)
    return hasmemoizedproperty(self, v)

  def iterOfflineTranslators(self, reverse=False):
    """
    @yield  Translator
    """
    if reverse:
      if self.atlasEnabled: yield self.atlasTranslator
      if self.lecEnabled: yield self.lecTranslator
      if self.hanVietEnabled: yield self.hanVietTranslator
      if self.transcatEnabled: yield self.transcatTranslator
      if self.ezTransEnabled: yield self.ezTranslator
      if self.dreyeEnabled: yield self.dreyeTranslator
      if self.fastaitEnabled: yield self.fastaitTranslator
      if self.jbeijingEnabled: yield self.jbeijingTranslator
      if self.romajiEnabled: yield self.romajiTranslator
    else:
      if self.romajiEnabled: yield self.romajiTranslator
      if self.jbeijingEnabled: yield self.jbeijingTranslator
      if self.fastaitEnabled: yield self.fastaitTranslator
      if self.dreyeEnabled: yield self.dreyeTranslator
      if self.ezTransEnabled: yield self.ezTranslator
      if self.transcatEnabled: yield self.transcatTranslator
      if self.hanVietEnabled: yield self.hanVietTranslator
      if self.lecEnabled: yield self.lecTranslator
      if self.atlasEnabled: yield self.atlasTranslator

  def iterOnlineTranslators(self, reverse=False):
    """
    @param* reverse  bool
    @yield  Translator
    """
    if self.online:
      if reverse:
        if self.infoseekEnabled: yield self.infoseekTranslator
        if self.exciteEnabled: yield self.exciteTranslator
        if self.lecOnlineEnabled: yield self.lecOnlineTranslator
        if self.transruEnabled: yield self.transruTranslator
        if self.systranEnabled: yield self.systranTranslator
        if self.googleEnabled: yield self.googleTranslator
        if self.bingEnabled: yield self.bingTranslator
        if self.babylonEnabled: yield self.babylonTranslator
        if self.niftyEnabled: yield self.niftyTranslator
        if self.naverEnabled: yield self.naverTranslator
        if self.vtransEnabled: yield self.vTranslator
        if self.youdaoEnabled: yield self.youdaoTranslator
        if self.baiduEnabled: yield self.baiduTranslator
      else:
        if self.baiduEnabled: yield self.baiduTranslator
        if self.youdaoEnabled: yield self.youdaoTranslator
        if self.vtransEnabled: yield self.vTranslator
        if self.naverEnabled: yield self.naverTranslator
        if self.niftyEnabled: yield self.niftyTranslator
        if self.babylonEnabled: yield self.babylonTranslator
        if self.bingEnabled: yield self.bingTranslator
        if self.googleEnabled: yield self.googleTranslator
        if self.systranEnabled: yield self.systranTranslator
        if self.transruEnabled: yield self.transruTranslator
        if self.lecOnlineEnabled: yield self.lecOnlineTranslator
        if self.exciteEnabled: yield self.exciteTranslator
        if self.infoseekEnabled: yield self.infoseekTranslator

  def iterTranslators(self):
    """@yield  Translator"""
    return itertools.chain(
        self.iterOfflineTranslators(),
        self.iterOnlineTranslators())

  def findTranslator(self, engine=''):
    """
    @param* engine  str
    @return  Translator or None
    """
    if engine:
      it = self.getTranslator(engine)
      if it:
        return it
    for it in self.iterTranslators():
      return it

  def findRetranslator(self, eng, to, fr):
    """
    @param  eng  _trman.Translator
    @param  to  str  language
    @param  fr  str  language
    @return  _trman.Retranslator or _trman.Translator or None
    """
    if not eng or not to or not fr:
      return
    key = eng.key
    conf = self.retransSettings.get(key)
    if not conf or not conf.get('yes'):
      return
    key2 = conf.get('key')
    if not key2:
      return
    fr2 = fr[:2]
    to2 = to[:2]
    if fr2 == to2:
      return
    #if mtinfo.test_lang(key, to=to, fr=fr): # test not performaned
    #  return eng
    lang = conf.get('lang') or 'en'
    lang2 = lang[:2]
    if lang2 == fr2:
      return self.getTranslator(key2)
    #if lang2 == to2: # disable checking to language
    #  return eng
    #if not mtinfo.test_lang(key, to=lang, fr=fr):
    if not mtinfo.test_lang(key, to=lang): # fr not used
      return
    if not mtinfo.test_lang(key2, fr=lang):
      return
    return self.getRetranslator(key, key2, lang)

class TranslatorManager(QObject):

  ## Construction ##

  def __init__(self, parent=None):
    super(TranslatorManager, self).__init__(parent)
    self.__d = _TranslatorManager(abortSignal=self.abortionRequested)

    self.clearCacheRequested.connect(self.clearCache, Qt.QueuedConnection)

  ## Signals ##

  abortionRequested = Signal()
  #infoseekAbortionRequested = Signal()
  #bingAbortionRequested = Signal()
  #baiduAbortionRequested = Signal()

  # Logs
  languagesReceived = Signal(unicode, unicode) # fr, to
  normalizedTextReceived = Signal(unicode) # text after applying translation replacement scripts
  inputTextReceived = Signal(unicode) # text after applying source terms
  encodedTextReceived = Signal(unicode) # text after preparing escaped terms
  delegateTextReceived = Signal(unicode) # text after applying proxied terms
  splitTextsReceived = Signal(list)  # texts after splitting
  splitTranslationsReceived = Signal(list)  # translations after applying translation
  jointTranslationReceived = Signal(unicode)  # translation before applying terms
  delegateTranslationReceived = Signal(unicode) # text after recovering proxied terms
  decodedTranslationReceived = Signal(unicode)  # translation after unescaping terms
  outputTranslationReceived = Signal(unicode)  # translation after applying target terms
  outputSyntacticTranslationReceived = Signal(unicode)  # translation after applying toutput terms before decoded

  clearCacheRequested = Signal() # async

  def abort(self):
    self.abortionRequested.emit()
    #for sig in self.infoseekAbortionRequested, self.bingAbortionRequested, self.baiduAbortionRequested:
    #  sig.emit()

  def clearCache(self):
    self.__d.clearCache()

  ## Properties ##

  def isMarked(self): return self.__d.marked
  def setMarked(self, t): self.__d.marked = t

  def isRubyEnabled(self): return self.__d.rubyEnabled
  def setRubyEnabled(self, t): self.__d.rubyEnabled = t

  def language(self): return self.__d.language
  def setLanguage(self, t): self.__d.language = t

  def isOnline(self): return self.__d.online
  def setOnline(self, t): self.__d.online = t

  def convertsAlphabet(self): return self.__d.convertsAlphabet
  def setConvertsAlphabet(self, t):
    dprint(t)
    self.__d.convertsAlphabet = t

  ## Translators ##

  def isYueEnabled(self): return self.__d.yueEnabled
  def setYueEnabled(self, value): self.__d.yueEnabled = value

  def isInfoseekEnabled(self): return self.__d.infoseekEnabled
  def setInfoseekEnabled(self, value): self.__d.infoseekEnabled = value

  def isExciteEnabled(self): return self.__d.exciteEnabled
  def setExciteEnabled(self, value): self.__d.exciteEnabled = value

  def isSystranEnabled(self): return self.__d.systranEnabled
  def setSystranEnabled(self, value): self.__d.systranEnabled = value

  def isNiftyEnabled(self): return self.__d.niftyEnabled
  def setNiftyEnabled(self, value): self.__d.niftyEnabled = value

  def isBabylonEnabled(self): return self.__d.babylonEnabled
  def setBabylonEnabled(self, value): self.__d.babylonEnabled = value

  def isGoogleEnabled(self): return self.__d.googleEnabled
  def setGoogleEnabled(self, value): self.__d.googleEnabled = value

  def isVTransEnabled(self): return self.__d.vtransEnabled
  def setVTransEnabled(self, value): self.__d.vtransEnabled = value

  def isBingEnabled(self): return self.__d.bingEnabled
  def setBingEnabled(self, value): self.__d.bingEnabled = value

  def isBaiduEnabled(self): return self.__d.baiduEnabled
  def setBaiduEnabled(self, value): self.__d.baiduEnabled = value

  def isYoudaoEnabled(self): return self.__d.youdaoEnabled
  def setYoudaoEnabled(self, value): self.__d.youdaoEnabled = value

  def isNaverEnabled(self): return self.__d.naverEnabled
  def setNaverEnabled(self, value): self.__d.naverEnabled = value

  def isLecOnlineEnabled(self): return self.__d.lecOnlineEnabled
  def setLecOnlineEnabled(self, value): self.__d.lecOnlineEnabled = value

  def isTransruEnabled(self): return self.__d.transruEnabled
  def setTransruEnabled(self, value): self.__d.transruEnabled = value

  def isHanVietEnabled(self): return self.__d.hanVietEnabled
  def setHanVietEnabled(self, value): self.__d.hanVietEnabled = value

  def isRomajiEnabled(self): return self.__d.romajiEnabled
  def setRomajiEnabled(self, value): self.__d.romajiEnabled = value

  def isRomajiType(self): return self.__d.romajiType
  def setRomajiType(self, value):
    d = self.__d
    if d.romajiType != value:
      d.romajiType = value
      if d.hasTranslator('romaji'):
        d.romajiTranslator.setRubyType(value)

  def isJBeijingEnabled(self): return self.__d.jbeijingEnabled
  def setJBeijingEnabled(self, value): self.__d.jbeijingEnabled = value

  def isFastaitEnabled(self): return self.__d.fastaitEnabled
  def setFastaitEnabled(self, value): self.__d.fastaitEnabled = value

  def isDreyeEnabled(self): return self.__d.dreyeEnabled
  def setDreyeEnabled(self, value): self.__d.dreyeEnabled = value

  def isEzTransEnabled(self): return self.__d.ezTransEnabled
  def setEzTransEnabled(self, value): self.__d.ezTransEnabled = value
  def isEhndEnabled(self): return self.__d.ehndEnabled
  def setEhndEnabled(self, value): self.__d.ehndEnabled = value

  def isTranscatEnabled(self): return self.__d.transcatEnabled
  def setTranscatEnabled(self, value): self.__d.transcatEnabled = value

  def isLecEnabled(self): return self.__d.lecEnabled
  def setLecEnabled(self, value): self.__d.lecEnabled = value

  def isAtlasEnabled(self): return self.__d.atlasEnabled
  def setAtlasEnabled(self, value): self.__d.atlasEnabled = value

  # Script

  def isAtlasScriptEnabled(self): return self.__d.getScriptEnabled('atlas')
  def setAtlasScriptEnabled(self, t): self.__d.setScriptEnabled('atlas', t)

  def isLecScriptEnabled(self): return self.__d.getScriptEnabled('lec')
  def setLecScriptEnabled(self, t): self.__d.setScriptEnabled('lec', t)

  def isLecOnlineScriptEnabled(self): return self.__d.getScriptEnabled('lecol')
  def setLecOnlineScriptEnabled(self, t): self.__d.setScriptEnabled('lecol', t)

  def isBingScriptEnabled(self): return self.__d.getScriptEnabled('bing')
  def setBingScriptEnabled(self, t): self.__d.setScriptEnabled('bing', t)

  def isGoogleScriptEnabled(self): return self.__d.getScriptEnabled('google')
  def setGoogleScriptEnabled(self, t): self.__d.setScriptEnabled('google', t)

  def isInfoseekScriptEnabled(self): return self.__d.getScriptEnabled('infoseek')
  def setInfoseekScriptEnabled(self, t): self.__d.setScriptEnabled('infoseek', t)

  def isExciteScriptEnabled(self): return self.__d.getScriptEnabled('excite')
  def setExciteScriptEnabled(self, t): self.__d.setScriptEnabled('excite', t)

  def isSystranScriptEnabled(self): return self.__d.getScriptEnabled('systran')
  def setSystranScriptEnabled(self, t): self.__d.setScriptEnabled('systran', t)

  def isNiftyScriptEnabled(self): return self.__d.getScriptEnabled('nifty')
  def setNiftyScriptEnabled(self, t): self.__d.setScriptEnabled('nifty', t)

  def isBabylonScriptEnabled(self): return self.__d.getScriptEnabled('babylon')
  def setBabylonScriptEnabled(self, t): self.__d.setScriptEnabled('babylon', t)

  def isTransruScriptEnabled(self): return self.__d.getScriptEnabled('transru')
  def setTransruScriptEnabled(self, t): self.__d.setScriptEnabled('transru', t)

  # Alignment

  def isBingAlignEnabled(self): return self.__d.getAlignEnabled('bing')
  def setBingAlignEnabled(self, t): self.__d.setAlignEnabled('bing', t)

  def isGoogleAlignEnabled(self): return self.__d.getAlignEnabled('google')
  def setGoogleAlignEnabled(self, t): self.__d.setAlignEnabled('google', t)

  def isBaiduAlignEnabled(self): return self.__d.getAlignEnabled('baidu')
  def setBaiduAlignEnabled(self, t): self.__d.setAlignEnabled('baidu', t)

  def isNaverAlignEnabled(self): return self.__d.getAlignEnabled('naver')
  def setNaverAlignEnabled(self, t): self.__d.setAlignEnabled('naver', t)

  def isInfoseekAlignEnabled(self): return self.__d.getAlignEnabled('infoseek')
  def setInfoseekAlignEnabled(self, t): self.__d.setAlignEnabled('infoseek', t)

  def isHanVietAlignEnabled(self): return self.__d.getAlignEnabled('hanviet')
  def setHanVietAlignEnabled(self, t): self.__d.setAlignEnabled('hanviet', t)

  def isRetranslatorEnabled(self, key): # str -> bool
    try: return bool(self.__d.retransSettings[key]['yes'])
    except: return False
  def setRetranslatorEnabled(self, key, t): # str, bool ->
    self.__d.updateRetransSettings(key, 'yes', t)

  def retranslatorLanguage(self, key): # str -> str or None
    try: return self.__d.retransSettings[key]['lang']
    except: pass
  def setRetranslatorLanguage(self, key, v): # str, str ->
    self.__d.updateRetransSettings(key, 'lang', v)

  def retranslatorEngine(self, key): # str -> str or None
    try: return self.__d.retransSettings[key]['key']
    except: pass
  def setRetranslatorEngine(self, key, v): # str, str ->
    self.__d.updateRetransSettings(key, 'key', v)

  ## Queries ##

  def warmup(self, to='', fr='ja'):
    if features.MACHINE_TRANSLATION:
      # 3/1/2015: Do it reversely so that TransCAT is initialized before JBeijing
      for it in self.__d.iterOfflineTranslators(reverse=True):
        dprint("warm up %s" % it.key)
        it.warmup(to=to, fr=fr)

  def hasOnlineTranslators(self):
    """
    @return  bool
    """
    d = self.__d
    return any((
      d.baiduEnabled,
      d.youdaoEnabled,
      d.vtransEnabled,
      d.naverEnabled,
      d.babylon,
      d.googleEnabled,
      d.bingEnabled,
      d.systranEnabled,
      d.niftyEnabled,
      d.lecOnlineEnabled,
      d.transruEnabled,
      d.infoseekEnabled,
      d.exciteEnabled,
    ))

  def hasOfflineTranslators(self):
    """
    @return  bool
    """
    d = self.__d
    return any((
      d.romajiEnabled,
      d.hanVietEnabled,
      d.jbeijingEnabled,
      d.fastaitEnabled,
      d.dreyeEnabled,
      d.ezTransEnabled,
      d.transcatEnabled,
      d.lecEnabled,
      d.atlasEnabled,
    ))

  def hasTranslators(self):
    """
    @return  bool
    """
    return self.hasOnlineTranslators() or self.hasOfflineTranslators()

  def enabledEngines(self, fr=''): # str -> [str]
    d = self.__d
    r = []
    if d.hanVietEnabled and (not fr or fr.startswith('zh')):
      r.append('hanviet')
    if d.jbeijingEnabled and (not fr or fr in ('ja', 'zhs', 'zht')):
      r.append('jbeijing')

    if d.fastaitEnabled: r.append('fastait')
    if d.dreyeEnabled: r.append('dreye')
    if d.ezTransEnabled: r.append('eztrans')
    if d.transcatEnabled: r.append('transcat')
    if d.lecEnabled: r.append('lec')
    if d.atlasEnabled: r.append('atlas')

    if d.baiduEnabled: r.append('baidu')
    if d.youdaoEnabled: r.append('youdao')
    if d.vtransEnabled: r.append('vtrans')
    if d.naverEnabled: r.append('naver')
    if d.babylonEnabled: r.append('babylon')
    if d.googleEnabled: r.append('google')
    if d.bingEnabled: r.append('bing')
    if d.niftyEnabled: r.append('nifty')
    if d.systranEnabled: r.append('systran')
    if d.lecOnlineEnabled: r.append('lecol')
    if d.transruEnabled: r.append('transru')
    if d.infoseekEnabled: r.append('infoseek')
    if d.exciteEnabled: r.append('excite')

    if d.romajiEnabled: r.append('romaji')
    return r

  def isEnabled(self):
    """
    @return  bool
    """
    return features.MACHINE_TRANSLATION and self.hasTranslators()

  #def guessTranslationLanguage(self): # -> str
  #  if not self.isEnabled():
  #    return ''
  #  d = self.__d
  #  if d.hanVietEnabled:
  #    return 'vi'
  #  if d.jbeijingEnabled or d.baiduEnabled or d.fastaitEnabled or d.dreyeEnabled:
  #    return 'zhs' if d.language == 'zhs' else 'zht'
  #  if d.ezTransEnabled or d.naverEnabled:
  #    return 'ko'
  #  if (d.atlasEnabled or d.lecEnabled) and not any((
  #      d.infoseekEnabled,
  #      d.transruEnabled,
  #      d.exciteEnabled,
  #      d.bingEnabled,
  #      d.googleEnabled,
  #      d.lecOnlineEnabled,
  #    )):
  #    return 'en'
  #  return d.language

  def getTranslationTargetLanguages(self): # -> [str]
    ret = []
    if not features.MACHINE_TRANSLATION:
      return ret

    d = self.__d

    if d.jbeijingEnabled or d.fastaitEnabled or d.youdaoEnabled: #or d.vtransEnabled
      if d.language in ('zhs', 'vi'):
        ret.append(d.language)
      else:
        ret.append('zht')

    if d.ezTransEnabled or d.transcatEnabled or d.naverEnabled:
      ret.append('ko')

    if d.hanVietEnabled:
      ret.append('vi')

    if d.atlasEnabled or d.lecEnabled:
      ret.append('en')

    if (d.bingEnabled
        or d.googleEnabled
        or d.baiduEnabled
        or d.infoseekEnabled
        or d.exciteEnabled
        or d.niftyEnabled
        or d.systranEnabled
        or d.babylonEnabled
        or d.lecOnlineEnabled
        or d.transruEnabled
      ):
      if d.language not in ret:
        ret.append(d.language)

    if 'ja' in ret:
      ret.remove('ja')

    return ret

  def translate(self, *args, **kwargs):
    """
    @return  unicode
    """
    return self.translateOne(*args, **kwargs)[0]

  def translateTest(self, text, fr='ja', to='', engine='', ehndEnabled=None, async=False):
    """
    @param  text  unicode
    @param* fr  unicode  language
    @param* to  unicode  language
    @param* async  bool
    @return  unicode or None
    """
    #if not features.MACHINE_TRANSLATION or not text:
    if not text:
      return ''
    d = self.__d
    #text = d.normalizeText(text)
    it = d.findTranslator(engine)
    if it:
      if not to:
        to = d.language
      kw = {
        'fr': fr,
        'to': to,
        'async': async,
      }
      it = d.findRetranslator(it, to=to, fr=fr) or it
      if it.key == 'eztrans':
        kw['ehndEnabled'] = ehndEnabled if ehndEnabled is not None else d.ehndEnabled
      return it.translateTest(text, **kw)

  def translateOne(self, text, fr='ja', to='', engine='', mark=None, online=True, async=False, cached=True, emit=False, keepsNewLine=None, scriptEnabled=None, ehndEnabled=None, rubyEnabled=None, context=''):
    """Translate using any translator
    @param  text  unicode
    @param* fr  unicode  language
    @param* to  unicode  language
    @param* mark  bool or None
    @param* async  bool
    @param* online  bool
    @param* emit  bool  whether emit intermediate results
    @param* scriptEnabled  bool or None  whether enable the translation script
    @param* cached  bool  NOT USED, always cached
    @return  unicode sub or None, unicode lang, unicode provider
    """
    if not features.MACHINE_TRANSLATION or not text:
      return None, None, None
    ret = None
    d = self.__d
    it = d.findTranslator(engine)
    if it:
      text = d.normalizeText(text)
      if not to:
        to = d.language
      kw = {
        'fr': fr,
        'to': to,
        'mark': mark,
        'async': async,
        'emit': emit,
        'keepsNewLine': keepsNewLine,
        'context': context,
      }
      it = d.findRetranslator(it, to=to, fr=fr) or it
      if it.key == 'eztrans':
        kw['ehndEnabled'] = ehndEnabled if ehndEnabled is not None else d.ehndEnabled
      if scriptEnabled != False:
        if it.key == 'retr':
          kw['scriptEnabled1'] = scriptEnabled or d.getScriptEnabled(it.first.key)
          kw['scriptEnabled2'] = scriptEnabled or d.getScriptEnabled(it.second.key)
        else:
          kw['scriptEnabled'] = scriptEnabled or d.getScriptEnabled(it.key)
      if emit or not it.onlineRequired or not it.asyncSupported:
        ret = it.translate(text, **kw)
      else: # not emit and asyncSupported
        kw['async'] = False # force using single thread
        ret = skthreads.runsync(partial(it.translate, text, **kw),
          abortSignal=self.abortionRequested,
        )
    if ret and ret[0] and d.rubyEnabled and rubyEnabled == False:
      t = richutil.removeRuby(ret[0])
      ret = t, ret[1], ret[2]
    return ret or (None, None, None)

  def translateApply(self, func, text, fr='ja', to='', keepsNewLine=None, mark=None, scriptEnabled=None, ehndEnabled=None, rubyEnabled=None, context='', **kwargs):
    """Specialized for textman
    @param  func  function(unicode sub, unicode lang, unicode provider)
    @param  text  unicode
    @param* fr  unicode  language
    @param* mark  bool or None
    @param* kwargs  pass to func
    """
    if not features.MACHINE_TRANSLATION or not text:
      return
    d = self.__d
    if not to:
      to = d.language

    text = d.normalizeText(text)
    if mark is None:
      mark = d.marked

    #translators = d.iterTranslators(reverseOnline=True)
    translators = itertools.chain(
      d.iterOfflineTranslators(),
      d.iterOnlineTranslators(reverse=True),
    )
    for it in translators:
      kw = {'fr':fr, 'to':to, 'mark':mark, 'async':False, 'keepsNewLine':keepsNewLine, 'context':context}
      it = d.findRetranslator(it, to=to, fr=fr) or it

      align = None
      if it.alignSupported:
        if it.key == 'retr':
          if d.getAlignEnabled(it.second.key):
            align = []
        else:
          if d.getAlignEnabled(it.key):
            align = []
      kw['align'] = align

      if align is not None:
        kw['mark'] = False

      thisRubyEnabled = rubyEnabled if align is None else False

      if scriptEnabled != False:
        if it.key == 'retr':
          kw['scriptEnabled1'] = scriptEnabled or d.getScriptEnabled(it.first.key)
          kw['scriptEnabled2'] = scriptEnabled or d.getScriptEnabled(it.second.key)
        else:
          kw['scriptEnabled'] = scriptEnabled or d.getScriptEnabled(it.key)

      if it.key == 'eztrans':
        kw['ehndEnabled'] = ehndEnabled if ehndEnabled is not None else d.ehndEnabled
      if it.onlineRequired: #or it.parallelEnabled: # rush offline translation speed
        skevents.runlater(partial(d.translateAndApply,
            func, kwargs, it.translate, text, rubyEnabled=thisRubyEnabled, **kw))
      else:
        r = it.translate(text, **kw)
        if r and r[0]:
          t = r[0]
          if d.rubyEnabled and thisRubyEnabled == False:
            t = richutil.removeRuby(t)
          func(t, r[1], r[2], align, **kwargs)

@memoized
def manager(): return TranslatorManager()

#def translate(*args, **kwargs):
#  return manager().translate(*args, **kwargs)

class TranslatorCoffeeBean(QObject):
  def __init__(self, parent=None):
    super(TranslatorCoffeeBean, self).__init__(parent)

  @Slot(result=unicode)
  def translators(self): # -> [str translator_name]
    return ','.join(manager().enabledEngines())

  @Slot(unicode, unicode, result=unicode)
  def translate(self, text, engine):
    # I should not hardcode fr = 'ja' here
    # Force async
    # Translate direct to disable Shared Dictionary
    return manager().translateTest(text, engine=engine, async=True) or ''

class TranslatorQmlBean(QObject):
  def __init__(self, parent=None):
    super(TranslatorQmlBean, self).__init__(parent)

  @Slot(unicode, result=unicode)
  def translators(self, language): # str -> [str translator_name]
    return ','.join(manager().enabledEngines(language))

  @Slot(unicode, unicode, unicode, result=unicode)
  def translate(self, text, language, engine):
    # I should not hardcode fr = 'ja' here
    # Force async
    return manager().translate(text, engine=engine, fr=language, mark=False, async=True, scriptEnabled=False, rubyEnabled=False) or ''

# EOF
