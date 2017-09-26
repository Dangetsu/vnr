# coding: utf8
# termman.py
# 10/8/2012 jichi
#
# Terminology:
# - data: raw game text byte code
# - text: original game text
# - translation: machine translation
# - comment: user's subtitle or comment

from sakurakit.skprof import SkProfiler

import os, string, re
#from collections import OrderedDict
from functools import partial
from time import time
from PySide.QtCore import Signal, QObject, QTimer, QMutex, Qt
#from rbmt import api as rbmt
from sakurakit import skfileio, skthreads
from sakurakit.skclass import memoized, Q_Q
from sakurakit.skdebug import dprint, dwarn
from mytr import my
import config, dataman, defs, growl, rc
import _termman

@memoized
def manager(): return TermManager()

TERM_TRYLOCK_INTERVAL = 10 # 0.01 second

# One QMutex is attached to all returned object
# Apply terms will cause tryLock
# Save/clear terms will cause lock
#
# Mutex is used instead of read/write lock, since the term object has internal cache
# This might cause thread contention when multiple translators are used
def _make_script_interpreter(type): # str -> Object
  if type == 'trans':
    from pytrcodec import TranslationCoder
    ret = TranslationCoder()
  elif type == 'output_syntax':
    from pytroscript import TranslationOutputScriptPerformer
    ret = TranslationOutputScriptPerformer()
  else:
    from pytrscript import TranslationScriptPerformer
    ret = TranslationScriptPerformer()
  # 11/15/2015: QMutex for script removed which might crash VNR
  #ret.rwlock = QReadWriteLock()
  #ret.mutex = QMutex()
  return ret

DELEGATE_DISABLED_LANGUAGES = 'el', # languages where user-defined delegation is disabled

@Q_Q
class _TermManager:

  instance = None # _TermManager  needed for updateTime

  def __init__(self, q):
    _TermManager.instance = self

    #self.convertsChinese = False
    self.enabled = True # bool
    self.hentai = False # bool
    self.marked = False # bool
    self.rubyEnabled = False # bool
    self.chineseRubyEnabled = False # bool
    self.koreanRubyEnabled = False # bool
    self.vietnameseRubyEnabled = False # bool
    #self.syntax = False # bool

    # For saving terms
    self.updateTime = 0 # float

    self.targetLanguage = 'ja' # str  targetLanguage

    self.saveMutex = QMutex()

    self.scripts = {} # {(str type, str fr, str to):TranslationScriptPerformer or ScriptCoder}
    self.scriptLocks = {} #  {(str lang, str fr, str to):bool}
    self.scriptTimes = {} # [(str lang, str fr, str to):float time]
    self.proxies = {} # {(str fr, str to):TranslationProxy}

    #self.rbmt = {} # {str language:rbmt.api.Translator}
    #self.rbmtTimes = {} # [str language:float time]

    t = self.saveTimer = QTimer(q)
    t.setSingleShot(True)
    t.setInterval(2000) # wait for 2 seconds for rebuilding
    t.timeout.connect(self.saveTerms)

    q.invalidateCacheRequested.connect(t.start, Qt.QueuedConnection)
    q.cacheChangedRequested.connect(q.cacheChanged, Qt.QueuedConnection)

  def rebuildCacheLater(self, queued=False):
    if queued:
      self.q.invalidateCacheRequested.emit()
    else:
      self.saveTimer.start()

  def saveTerms(self):
    if not self.scriptTimes:
      return
    if not self.saveMutex.tryLock():
      dwarn("retry later due to thread contention")
      self.rebuildCacheLater(queued=True)
      return

    saveTime = time()
    skthreads.runsync(partial(
        self._saveTerms, saveTime))
    self.saveMutex.unlock()

  def _saveTerms(self, createTime):
    """Invoked async
    @param  createTime  float
    """
    #for lang,ts in self.targetLanguages.iteritems():
    scriptTimes = self.scriptTimes
    #rbmtTimes = self.rbmtTimes
    if not scriptTimes or createTime < self.updateTime:
      return

    dprint("enter")

    if scriptTimes and createTime >= self.updateTime:
      self._saveScriptTerms(createTime=createTime, times=scriptTimes)

    if createTime >= self.updateTime:
      dprint("cache changed")
      self.q.cacheChangedRequested.emit()
    dprint("leave")

  def _saveScriptTerms(self, createTime, times):
    """
    @param  createTime  float
    @param  times  {str key:float time}
    """
    dprint("enter")

    dm = dataman.manager()
    gameIds = dm.currentGameIds()
    dprint("current series gameIds = %s" % gameIds)
    if gameIds:
      gameIds = set(gameIds) # in case it is changed during iteration

    l = [t.d for t in dm.terms() if not t.d.disabled and not t.d.deleted and t.d.pattern] # filtered
    _termman.sort_terms(l)
    w = _termman.TermWriter(
      termData=l,
      gameIds=gameIds,
      hentai=self.hentai,
      createTime=createTime,
      parent=self,
      rubyEnabled=self.rubyEnabled,
      chineseRubyEnabled=self.rubyEnabled and self.chineseRubyEnabled,
      koreanRubyEnabled=self.rubyEnabled and self.koreanRubyEnabled,
      vietnameseRubyEnabled=self.rubyEnabled and self.vietnameseRubyEnabled,
    )

    #for scriptKey,ts in times.iteritems():
    for scriptKey,ts in times.items(): # back up items
      if ts < self.updateTime: # skip language that does not out of date
        type, to, fr = scriptKey
        macros = w.queryMacros(to, fr)

        if w.isOutdated():
          dwarn("leave: cancel saving out-of-date terms")
          return

        path = rc.term_path(type, to=to, fr=fr) # unicode
        dir = os.path.dirname(path) # unicode path
        if not os.path.exists(dir):
          skfileio.makedirs(dir)

        scriptKey = type, to, fr
        if self.scriptLocks.get(scriptKey):
          raise Exception("cancel saving locked terms")
        self.scriptLocks[scriptKey] = True

        man = self.scripts.get(scriptKey)
        if not man:
          man = self.scripts[scriptKey] = _make_script_interpreter(type)
        #elif not man.isEmpty():
        #  man.clear()
        else:
          #man.mutex.lock()
          if not man.isEmpty():
            man.clear()
          #man.mutex.unlock()
        try:
          if type == 'trans':
            proxies = self.proxies.get((to, fr))
            if proxies:
              del proxies[:]

          if w.saveTerms(path, type, to, fr, macros):
            #man.mutex.lock()
            ok = man.loadScript(path)
            #man.mutex.unlock()
            if ok and type == 'trans':
              self.proxies[(to, fr)] = w.queryProxies(to, fr)
            dprint("type = %s, to = %s, fr = %s, count = %s" % (type, to, fr, man.size()))
        except:
          self.scriptLocks[scriptKey] = False
          raise

        self.scriptLocks[scriptKey] = False
        times[scriptKey] = createTime
    dprint("leave")

  def applyTerms(self, text, type, to, fr, context='', host='', mark=False, ignoreIfNotReady=False):
    """
    @param  text  unicode
    @param  type  str
    @param  to  str  language
    @param* fr  str  language
    @param* context  str
    @param* host  str
    @param* mark  bool or None
    @param* ignoreIfNotReady  bool
    """
    if mark is None:
      mark = self.marked
    if type in ('encode', 'decode'):
      key = 'trans', to, fr # share the same manager
    else:
      key = type, to, fr
    man = self.scripts.get(key)
    if man is None:
      self.scriptTimes[key] = 0
      self.rebuildCacheLater()
      if ignoreIfNotReady:
        dwarn("ignore text while processing shared dictionary")
        growl.notify(my.tr("Processing Shared Dictionary") + "...")
        return ''
    if self.scriptLocks.get(key):
      dwarn("skip applying locked script")
      if ignoreIfNotReady:
        dwarn("ignore text while processing shared dictionary")
        growl.notify(my.tr("Processing Shared Dictionary") + "...")
        return ''
      return text

    if not man: #or man.isEmpty():
      return text

    #if not man.mutex.tryLock(TERM_TRYLOCK_INTERVAL):
    #  dwarn("try lock timeout")
    #  return text

    ret = text
    if not man.isEmpty():
      category = _termman.make_category(context=context, host=host)
      if type == 'encode':
        ret = man.encode(text, category)
      elif type == 'decode':
        ret = man.decode(text, category, mark)
      else:
        ret = man.transform(text, category, mark)
    #man.mutex.unlock()
    return ret

  def warmupTerms(self, type, to, fr):
    """
    @param  type  str
    @param  to  str  language
    @param* fr  str  language
    """
    if type in ('encode', 'decode'):
      key = 'trans', to, fr # share the same manager
    else:
      key = type, to, fr
    if key not in self.scripts:
      self.scriptTimes[key] = 0
      self.rebuildCacheLater()

  _rx_delegate = re.compile(
    r"{{"
      r"([a-zA-Z0-9,_$]+)" # TR_RE_TOKEN
      r"<[-0-9<>]+>"
    r"}}"
  )
  def delegateTranslation(self, text, to, fr, context, host, proxies, proxyDigit):
    """
    @param  text  unicode
    @param  to  str  language
    @param  fr  str  language
    @param  context  str
    @param  host  str
    @param  proxies  {unicode input:unicode output}
    @param  proxyDigit  proxy using letters or digits
    @return  unicode
    """
    if '{{' not in text or '}}' not in text:
      return text

    if to in DELEGATE_DISABLED_LANGUAGES:
      unused_proxies = None # disabled
    else:
      unused_proxies = self.proxies.get((to, fr)) # [TranslationProxy]

    used_proxy_input = set() # [unicode]
    used_proxy_output = set() # [unicode]

    category = _termman.make_category(context=context, host=host)

    def fn(m): # re.match -> unicode
      matched_text = m.group()
      role = m.group(1)
      ret = None
      if unused_proxies:
        for proxy in unused_proxies:
          if (proxy.match_category(category) and proxy.match_role(role)
              and proxy.input not in used_proxy_input and proxy.output not in used_proxy_output
              and proxy.input not in text and proxy.output not in text):
            used_proxy_input.add(proxy.input)
            used_proxy_output.add(proxy.output)
            proxies[proxy.output] = matched_text
            return proxy.input
      index = len(proxies)
      ret = defs.term_role_proxy(role, index, proxyDigit=proxyDigit)
      proxies[ret] = matched_text
      return ret
    return self._rx_delegate.sub(fn, text)

  _rx_undelegate_latin = re.compile(r"Z[A-Y]+Z")
  _rx_undelegate_digit = re.compile(r"9[0-8]+9")
  def undelegateTranslation(self, text, to, fr, proxies, proxyDigit=False):
    """
    @param  text  unicode
    @param  to  str  language
    @param  fr  str  language
    @param* proxies  {unicode input:unicode output}
    @param* proxyDigit  proxy using letters or digits
    @return  unicode
    """
    if not proxies:
      return text
    rx = None
    if proxyDigit:
      if '9' in text:
        rx = self._rx_undelegate_digit
    else:
      if 'Z' in text:
        rx = self._rx_undelegate_latin
    if rx:
      def fn(m): # re.match -> unicode
        matched_text = m.group()
        try: return proxies.pop(matched_text)
        except KeyError: return matched_text
      text = rx.sub(fn, text)
    if proxies:
      #to_latin = config.is_latin_language(to)
      for k,v in proxies.iteritems():
        text = text.replace(k, v)
    return text

class TermManager(QObject):

  ## Construction ##

  def __init__(self, parent=None):
    super(TermManager, self).__init__(parent)
    self.__d = _TermManager(self)

  cacheChanged = Signal()

  cacheChangedRequested = Signal() # private euse
  invalidateCacheRequested = Signal() # private use

  ## Properties ##

  #def isLocked(self): return self.__d.locked

  #def getRuleBasedTranslator(self, language):
  #  """
  #  @param  language  str
  #  @return rbmt.api.Translator or None
  #  """
  #  d = self.__d
  #  if not d.syntax or not d.enabled or not language:
  #    return
  #  ret = d.rbmt.get(language)
  #  if ret:
  #    return ret if ret.ruleCount() else None
  #  cabocha = cabochaman.cabochaparser()
  #  if not cabocha:
  #    dwarn("failed to create cabocha parser")
  #  else:
  #    ret = d.rbmt[language] = TermTranslator(cabocha, language, underline=d.marked)
  #    d.rbmtTimes[language] = 0
  #    d.rebuildCacheLater()

  def setTargetLanguage(self, v):
    d = self.__d
    if v and v != d.targetLanguage:
      d.targetLanguage = v
      # Reset translation scripts
      d.scripts = {}
      d.scriptTimes = {}
      d.proxies = {}
      # Reset rule-based translator
      #d.rbmt = {}
      #d.rbmtTimes = {}

  def isEnabled(self): return self.__d.enabled
  def setEnabled(self, value): self.__d.enabled = value

  def isHentaiEnabled(self): return self.__d.hentai
  def setHentaiEnabled(self, t):
    dprint(t)
    self.__d.hentai = t

  #def isSyntaxEnabled(self): return self.__d.syntax
  #def setSyntaxEnabled(self, value):
  #  dprint(value)
  #  self.__d.syntax = value

  def isMarked(self): return self.__d.marked
  def setMarked(self, t): self.__d.marked = t
    #d = self.__d
    #if d.marked != t:
    #  d.marked = t
    #  for key,man in d.scripts.iteritems():
    #    type = key[0]
    #    marked = t and type in ('output', 'trans_output')
    #    man.setLinkEnabled(marked)

    #  for it in d.rbmt.itervalues():
    #    it.setUnderline(t and it.isEscape())

  def isRubyEnabled(self): return self.__d.rubyEnabled
  def setRubyEnabled(self, t): self.__d.rubyEnabled = t

  def isChineseRubyEnabled(self, t): return self.__d.chineseRubyEnabled
  def setChineseRubyEnabled(self, t): self.__d.chineseRubyEnabled = t

  def isKoreanRubyEnabled(self, t): return self.__d.koreanRubyEnabled
  def setKoreanRubyEnabled(self, t): self.__d.koreanRubyEnabled = t

  def isVietnameseRubyEnabled(self, t): return self.__d.vietnameseRubyEnabled
  def setVietnameseRubyEnabled(self, t): self.__d.vietnameseRubyEnabled = t

  ## Marks ##

  #def clearMarkCache(self): # invoked on escapeMarked changes in settings
  #  for term in dataman.manager().iterEscapeTerms():
  #    term.applyReplace = None

  #def markEscapeText(self, text): # unicode -> unicode
  #  return _mark_text(text) if text and self.__d.marked else text

  #def removeMarks(self, text): # unicode -> unicode
  #  return textutil.remove_html_tags(text) if self.__d.marked else text

  #def convertsChinese(self): return self.__d.convertsChinese
  #def setConvertsChinese(self, value): self.__d.convertsChinese = value

  ## Cache ##

  def invalidateCache(self):
    d = self.__d
    d.updateTime = time()
    d.rebuildCacheLater()

  def warmup(self, async=True, interval=0): # bool, int
    d = self.__d
    if not d.enabled:
      return
    fr = dataman.manager().currentGameLanguage()
    dprint("fr = %s" % fr)
    if not fr:
      return

    import gameagent, settings
    t = not settings.global_().isGameAgentEnabled() or not gameagent.global_().isConnected()
    dprint("game = %s" % t)
    if t:
      d.warmupTerms('game', d.targetLanguage, fr)

    import trman
    tos = trman.manager().getTranslationTargetLanguages()
    if not tos:
      return

    dprint("to = %s" % tos)
    for to in tos:
      for type in 'input', 'trans', 'output_nosyntax': #'output_syntax':
        d.warmupTerms(type, to, fr)

  #  task = partial(d.warmup,
  #      terms=dm.terms(),
  #      hasTitles=dm.hasTermTitles(),
  #      hentai=d.hentai,
  #      language=d.language)

  #  if not async:
  #    apply(task)
  #  else:
  #    d.locked = True
  #    if interval:
  #      skthreads.runasynclater(task, interval)
  #    else:
  #      skthreads.runasync(task)
  #  dprint("leave")

  ## Queries ##

  #def filterTerms(self, terms, language):
  #  """
  #  @param  terms  iterable dataman.Term
  #  @param  language  unicode
  #  @yield  Term
  #  """
  #  return self.__d.iterTerms(terms, language)

  def applyGameTerms(self, text, to=None, fr=None, context='', ignoreIfNotReady=False):
    """
    @param  text  unicode
    @param* to  str
    @param* fr  str
    @param* context  str
    @param* ignoreIfNotReady  bool
    @return  unicode
    """
    d = self.__d
    # 9/25/2014: Qt 3e-05 seconds
    # 9/26/2014: Boost 4e-05 seconds
    #with SkProfiler():
    if not d.enabled or not text:
      return text
    return d.applyTerms(text, 'game', to or d.targetLanguage, fr or 'ja', context=context, ignoreIfNotReady=ignoreIfNotReady)
    #return self.__d.applyTerms(dataman.manager().iterOriginTerms(), text, language)

  #def applyNameTerms(self, text, language):
  #  """
  #  @param  text  unicode
  #  @param  language  unicode
  #  @return  unicode
  #  """
  #  return self.__d.applyTerms(dataman.manager().iterNameTerms(), text, language)

  def applyTtsTerms(self, text, language=None):
    """
    @param  text  unicode
    @param* language  str
    @return  unicode
    """
    d = self.__d
    if not d.enabled or not text:
      return text
    return d.applyTerms(text, 'tts', 'ja', language or d.targetLanguage)

  def applyOcrTerms(self, text, language=None):
    """
    @param  text  unicode
    @param* language  str
    @return  unicode
    """
    d = self.__d
    if not d.enabled or not text:
      return text
    return d.applyTerms(text, 'ocr', 'ja', language or 'ja')

  def applyPlainOutputTerms(self, text, to, fr, context='', host='', mark=None):
    """
    @param  text  unicode
    @param  to  str  language
    @param  fr  str  language
    @param* host  str
    @param* mark  bool or None
    @return  unicode
    """
    d = self.__d
    if not d.enabled or not text:
      return text
    # 9/25/2014: Qt 0.0003 seconds
    # 9/26/2014: Boost 0.0005 seconds, underline = True
    # 3/11/2015: 0.01 seconds new trscript
    #with SkProfiler("output term"):
    return d.applyTerms(text, 'output_nosyntax', to, fr, context=context, host=host, mark=mark)
    #if d.marked and language.startswith('zh'):
    #  ret = ret.replace('> ', '>')
    #return self.__d.applyTerms(dataman.manager().iterTargetTerms(),
    #    text, language, convertsChinese=True, marksChanges=self.__d.marked)

  def applySyntacticOutputTerms(self, text, to, fr, context='', host='', mark=None):
    """
    @param  text  unicode
    @param  to  str  language
    @param  fr  str  language
    @param* host  str
    @param* mark  bool or None
    @return  unicode
    """
    d = self.__d
    if not d.enabled or not text:
      return text
    return d.applyTerms(text, 'output_syntax', to, fr, context=context, host=host, mark=mark)

  def applyPlainInputTerms(self, text, to, fr, context='', host=''):
    """
    @param  text  unicode
    @param  to  str  language
    @param  fr  str  language
    @param* host  str
    @return  unicode
    """
    d = self.__d
    if not d.enabled or not text:
      return text
    # 9/25/2014: Qt 0.0005 seconds
    # 9/26/2014: Boost 0.001 seconds
    # 3/11/2015: 0.002 seconds new trscript
    #with SkProfiler("input term"):
    return d.applyTerms(text, 'input', to, fr, context=context, host=host)
    #dm = dataman.manager()
    #d = self.__d
    #text = d.applyTerms(dm.iterSourceTerms(), text, language)
    #if text and dm.hasNameItems() and config.is_latin_language(d.targetLanguage):
    #  try:
    #    for name in dm.iterNameItems():
    #      if name.translation:
    #        text = name.replace(text)
    #  except Exception, e: dwarn(e)
    #  text = text.rstrip() # remove trailing spaces

  def encodeTranslation(self, text, to, fr, context='', host=''):
    """
    @param  text  unicode
    @param  to  str  language
    @param  fr  str  language
    @param* host  str
    @return  unicode
    """
    d = self.__d
    if not d.enabled or not text: #or not ESCAPE_ALL and not config.is_kanji_language(language):
      return text
    # 9/25/2014: Qt 0.01 seconds
    # 9/26/2014: Boost 0.033 seconds, underline = True
    # 9/27/2014: Boost 0.007 seconds, by delay rendering underline
    # 3/11/2015: 0.003 seconds with codec
    #with SkProfiler("encode trans"): # 1/8/2015: 0.048 for Chinese, increase to 0.7 if no caching
    return d.applyTerms(text, 'encode', to, fr, context=context, host=host)

  _rx_decode_open = re.compile(r'(?<=[,.?!]|\w){{', re.UNICODE)
  _rx_decode_close = re.compile(r'}}(?=\w)', re.UNICODE)
  def decodeTranslation(self, text, to, fr, context='', host='', mark=None):
    """
    @param  text  unicode
    @param  to  str  language
    @param  fr  str  language
    @param* host  str
    @param* mark  bool or None
    @return  unicode
    """
    d = self.__d
    if not d.enabled or not text or '{{' not in text or '}}' not in text:
      return text
    if config.language_word_has_space(to): # insert spaces after replacement
      ret = self._rx_decode_open.sub(" {{", text)
      ret = self._rx_decode_close.sub("}} ", text)
    # 9/25/2014: Qt 0.009 seconds
    # 9/26/2014: Boost 0.05 seconds, underline = True
    # 9/27/2014: Boost 0.01 seconds, by delaying rendering underline
    # 3/11/2015: 0.00016 seconds with codec
    #with SkProfiler("decode trans"): # 1/8/2015: 0.051 for Chinese, increase to 0.7 if no caching
    return d.applyTerms(text, 'decode', to, fr, context=context, host=host, mark=mark)

  def delegateTranslation(self, text, to, fr, context='', host='', proxies={}, proxyDigit=False):
    """
    @param  text  unicode
    @param  to  str  language
    @param  fr  str  language
    @param* host  str
    @param* proxies  {unicode input:unicode output}
    @param* proxyDigit  proxy using letters or digits
    @return  unicode
    """
    d = self.__d
    if not d.enabled or not text: #or not ESCAPE_ALL and not config.is_kanji_language(language):
      return text
    # 3/11/2015: 5e-5 seconds with codec
    #with SkProfiler("delegate term"):
    return d.delegateTranslation(text, to, fr, context, host, proxies, proxyDigit=proxyDigit)

  def undelegateTranslation(self, text, to, fr, context='', host='', proxies={}, proxyDigit=False):
    """
    @param  text  unicode
    @param  to  str  language
    @param  fr  str  language
    @param* context  str  not used
    @param* host  str  not used
    @param* proxies  {unicode input:unicode output}
    @param* proxyDigit  proxy using letters or digits
    @return  unicode
    """
    d = self.__d
    if not d.enabled or not text: #or not ESCAPE_ALL and not config.is_kanji_language(language):
      return text
    # 3/11/2015: 4e-5 seconds with codec
    #with SkProfiler("undelegate term"):
    return d.undelegateTranslation(text, to, fr, proxies, proxyDigit=proxyDigit)

# EOF
