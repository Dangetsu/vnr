# coding: utf8
# _trman.py
# 10/8/2012 jichi
#
# Terminology:
# - data: raw game text byte code
# - text: original game text
# - translation: machine translation
# - comment: user's subtitle or comment

import os, re
import requests
from functools import partial
from itertools import ifilter, imap
from time import time
from PySide.QtCore import QMutex
from opencc.opencc import zhs2zht, zht2zhs
from sakurakit import skthreads
from sakurakit.skclass import memoizedproperty
from sakurakit.skdebug import dwarn
from i18n import i18n
import config, growl, textutil, trman
from unitraits.uniconv import wide2thin, wide2thin_digit

#from sakurakit.skprof import SkProfiler

__NO_DELIM = '' # no deliminators
_NO_SET = frozenset()
_NO_RE = re.compile('')

__PARAGRAPH_DELIM = u"【】「」♪" # machine translation of sentence deliminator
_PARAGRAPH_SET = frozenset(__PARAGRAPH_DELIM)
_PARAGRAPH_RE = re.compile(r"([%s])" % ''.join(_PARAGRAPH_SET))

#__SENTENCE_DELIM = u"\n【】「」。♪" #…！？# machine translation of sentence deliminator
#_SENTENCE_SET = frozenset(__SENTENCE_DELIM)
_SENTENCE_RE = re.compile(ur"([。？！」\n])(?![。！？）」\n]|$)")

class TranslationCache:
  def __init__(self, maxSize=1000, shrinkSize=300): # a much larger cache size than reader
    """
    @param  maxSize  max data size
    @param  shrinkSize  data to delete when oversize
    """
    self.maxSize = maxSize
    self.shrinkSize = shrinkSize
    self.data = {} # {unicode text:[unicode sub, long timestamp]}

  def clear(self):
    if self.data:
      self.data = {}

  def get(self, key): # unicode -> unicode
    t = self.data.get(key)
    if t:
      t[1] = self._now()
      return t[0]

  def update(self, key, value): # unicode, unicode -> unicode
    self.data[key] = [value, self._now()]
    if len(self.data) > self.maxSize:
      self._shrink()
    return value

  @staticmethod
  def _now(): return long(time()) # -> long  msecs

  def _shrink(self):
    l = sorted(self.data.iteritems(), key=lambda it:it[1][1])
    self.data = {k:v for k,v in l[self.shrinkSize:]}

## Translators

class Translator(object):
  key = 'tr' # str

  def clearCache(self): pass

  def warmup(self): pass

  def translate(self, text, to='en', fr='ja', async=False):
    """
    @param  text  unicode
    @param  to  str
    @param* fr  str
    @param* async  bool
    @return  (unicode sub or None, str lang or None, self.name or None)
    """
    return None, to, self.key

class HanVietTranslator(Translator):
  key = 'hanviet' # override

  def translate(self, text, to='vi', fr='zhs', async=False):
    """
    @param  text  unicode
    @param* fr  unicode
    @param* async  bool  ignored, always sync
    @return  unicode sub, unicode lang, unicode provider
    """
    if fr == 'zht':
      text = zht2zhs(text)
    #tm = termman.manager()
    #text = tm.applySourceTerms(text, 'zhs')
    from hanviet.hanviet import han2viet
    sub = han2viet(text)
    #if sub:
    #  sub = textutil.beautify_subtitle(sub)
    return sub, 'vi', self.key

# Machine translators

class MachineTranslator(Translator):

  splitsSentences = False # bool

  #_CACHE_LENGTH = 10 # length of the translation to cache

  #_DELIM_SET = _PARAGRAPH_SET # set of deliminators
  #_DELIM_RE = _PARAGRAPH_RE   # rx of deliminators

  def __init__(self, abortSignal=None):
    super(MachineTranslator, self).__init__()
    self.cache = TranslationCache()  # public overall translation cache
    self._cache = TranslationCache() # private translation cache for internal translation
    self.abortSignal = abortSignal # QtCore.Signal abort translation

  def clearCache(self):
    """@reimp"""
    self.cache.clear()
    self._cache.clear()

  def __cachedtr(self, text, async, tr, **kwargs):
    """
    @param  text  unicode
    @param  async  bool
    @param  tr  function(unicode text, str to, str fr)
    @return  unicode or None
    """
    #if len(text) > self._CACHE_LENGTH:
    #  return skthreads.runsync(partial(
    #       tr, text, **kwargs),
    #       abortSignal=self.abortSignal,
    #       parent=self.parent) if async else tr(text, **kwargs)
    return self._cache.get(text) or (self._cache.update(text,
        skthreads.runsync(partial(
          tr, text, **kwargs),
          abortSignal=self.abortSignal,
        ) if async else tr(text, **kwargs)))

  def __tr(self, text, *args, **kwargs):
    """
    @param  t  unicode
    @return  unicode or None
    """
    # Current max length of escaped char is 12
    return ('' if not text else
        text if len(text) == 1 and text in _PARAGRAPH_SET else #or len(text) <= 12 and sktypes.is_float(text) else
        self.__cachedtr(text, *args, **kwargs))

  def _itertexts(self, text):
    """
    @param  text  unicode
    @yield  unicode
    """
    for line in ifilter(textutil.skipemptyline,
        (it.strip() for it in _PARAGRAPH_RE.split(text))):
      if not self.splitsSentences:
        yield line
      else:
        for sentence in _SENTENCE_RE.sub(r"\1\n", line).split("\n"):
          yield sentence

  def _itertranslate(self, text, tr, async=False, **kwargs):
    """
    @param  text  unicode
    @param  tr  function(text, to, fr)
    @param  async  bool
    @param  kwargs  arguments passed to tr
    @yield  unicode
    """
    for line in self._itertexts(text):
      t = self.__tr(line,
          async, tr, # *args
          **kwargs)
      if t is None:
        dwarn("translation failed or aborted using '%s'" % self.key)
        break
      yield t # 10/10/2013: maybe, using generator instead would be faster?

  def _translate(self, *args, **kwargs):
    """
    @param  emit  bool
    @param  text  unicode
    @param  tr  function(text, to, fr)
    @param  async  bool
    @param  kwargs  arguments passed to tr
    @return  unicode
    """
    return ''.join(self._itertranslate(*args, **kwargs))

  def _escapeText(self, text, to):
    """
    @param  text  unicode
    @param  to  str  language
    @param* emit  bool
    @return  unicode
    """
    #tm = termman.manager()
    #text = tm.applySourceTerms(text, to)
    #text = tm.prepareEscapeTerms(text, to)
    return text

  def _unescapeTranslation(self, text, to):
    """
    @param  text  unicode
    @param  to  str  language
    @return  unicode
    """
    #tm = termman.manager()
    #text = tm.applyEscapeTerms(text, to)
    #text = tm.applyTargetTerms(text, to)
    #text = textutil.beautify_subtitle(text)
    return text

OnlineMachineTranslator = MachineTranslator
OfflineMachineTranslator = MachineTranslator

## Offline

# Note:
# There are trailing spaces after each translation for Atlas.
# But there are no trailing spaces for LEC.
class AtlasTranslator(OfflineMachineTranslator):
  key = 'atlas' # override
  splitsSentences = True
  #_DELIM_SET = _SENTENCE_SET # override
  #_DELIM_RE = _SENTENCE_RE # override

  def __init__(self, **kwargs):
    super(AtlasTranslator, self).__init__(**kwargs)
    self.engine = self.createengine()
    self._warned = False # bool

  @staticmethod
  def createengine():
    from atlas import atlas
    ret = atlas.create_engine()
    ok = ret.load()
    #import atexit
    #atexit.register(ret.destroy)
    if ok:
      growl.msg(i18n.tr("ATLAS translator is loaded"))
    else:
      growl.error(i18n.tr("Cannot load {0} for machine translation. Please check Preferences/Location").format(i18n.tr("ATLAS")))
    return ret

  # This would cause issue?
  def warmup(self):
    """@reimp"""
    self.engine.warmup()

  def translate(self, text, to='en', fr='ja', async=False):
    """@reimp"""
    to = 'en'
    if fr != 'ja':
      return None, None, None
    repl = self.cache.get(text)
    if repl:
      return repl, to, self.key
    repl = self._escapeText(text, to=to)
    if repl:
      try:
        repl = self._translate(repl, self.engine.translate, async=async)
        if repl:
          # ATLAS always try to append period at the end
          repl = wide2thin(repl) #.replace(u". 。", ". ").replace(u"。", ". ").replace(u" 」", u"」").rstrip()
          repl = self._unescapeTranslation(repl, to=to)
          repl = repl.replace(u" 」", u"」") # remove the trailing space
          self.cache.update(text, repl)
          return repl, to, self.key
      #except RuntimeError, e:
      except Exception, e:
        if not self._warned:
          self._warned = True
          dwarn(e)
          if not async:
            growl.error(i18n.tr("Cannot load {0} for machine translation. Please check Preferences/Location").format(i18n.tr("ATLAS")),
                async=async)
    return None, None, None

class LecTranslator(OfflineMachineTranslator):
  key = 'lec' # override
  splitsSentences = True
  #_DELIM_SET = _SENTENCE_SET # override
  #_DELIM_RE = _SENTENCE_RE # override

  def __init__(self, **kwargs):
    super(LecTranslator, self).__init__(**kwargs)
    self.engine = self.createengine()
    self._warned = False # bool

  @staticmethod
  def createengine():
    from lec import powertrans
    ret = powertrans.create_engine()
    ok = ret.load()
    #import atexit
    #atexit.register(ret.destroy)
    if ok:
      growl.msg(i18n.tr("LEC translator is loaded"))
    else:
      growl.error(i18n.tr("Cannot load {0} for machine translation. Please check Preferences/Location").format(i18n.tr("LEC")))
    return ret

  # This would cause issue?
  def warmup(self):
    """@reimp"""
    self.engine.warmup()

  def translate(self, text, to='en', fr='ja', async=False):
    """@reimp"""
    to = 'en'
    if fr != 'ja':
      return None, None, None
    repl = self.cache.get(text)
    if repl:
      return repl, to, self.key
    repl = self._escapeText(text, to=to)
    if repl:
      try:
        repl = self._translate(repl, self.engine.translate, async=async)
        if repl:
          repl = wide2thin(repl) #.replace(u"。", ". ").replace(u" 」", u"」").rstrip()
          repl = self._unescapeTranslation(repl, to=to)
          self.cache.update(text, repl)
          return repl, to, self.key
      #except RuntimeError, e:
      except Exception, e:
        if not self._warned:
          self._warned = True
          dwarn(e)
          if not async:
            growl.error(i18n.tr("Cannot load {0} for machine translation. Please check Preferences/Location").format(i18n.tr("LEC")),
                async=async)
    return None, None, None

class EzTranslator(OfflineMachineTranslator):
  key = 'eztrans' # override

  def __init__(self, **kwargs):
    super(EzTranslator, self).__init__(**kwargs)
    self.engine = self.createengine()
    self._warned = False # bool

  @staticmethod
  def createengine():
    from eztrans import eztrans
    ret = eztrans.create_engine()
    ok = ret.load()
    #import atexit
    #atexit.register(ret.destroy) # not needed by eztrans
    if ok:
      growl.msg(i18n.tr("ezTrans XP is loaded"))
    else:
      growl.error(i18n.tr("Cannot load {0} for machine translation. Please check Preferences/Location").format(i18n.tr("ezTrans XP")))
    return ret

  def warmup(self):
    """@reimp"""
    self.engine.warmup()

  def translate(self, text, to='ko', fr='ja', async=False):
    """@reimp"""
    to = 'ko'
    if fr != 'ja':
      return None, None, None
    repl = self.cache.get(text)
    if repl:
      return repl, to, self.key
    repl = self._escapeText(text, to=to)
    if repl:
      try:
        repl = self._translate(repl, self.engine.translate, async=async)
        if repl:
          repl = self._unescapeTranslation(repl, to=to)
          self.cache.update(text, repl)
          return repl, to, self.key
      #except RuntimeError, e:
      except Exception, e:
        if not self._warned:
          self._warned = True
          dwarn(e)
          if not async:
            growl.error(i18n.tr("Cannot load {0} for machine translation. Please check Preferences/Location").format(i18n.tr("ezTrans XP")),
                async=async)
    return None, None, None

class JBeijingTranslator(OfflineMachineTranslator):
  key = 'jbeijing' # override

  def __init__(self, **kwargs):
    super(JBeijingTranslator, self).__init__(**kwargs)
    self.engine = self.createengine()
    self._warned = False # bool

  @staticmethod
  def createengine():
    from jbeijing import jbeijing
    ret = jbeijing.create_engine()
    ok = ret.load()
    #import atexit
    #atexit.register(ret.destroy)
    if ok:
      growl.msg(i18n.tr("JBeijing translator is loaded"))

      def _filter(path): return bool(path) and os.path.exists(path + '.dic')
      paths = jbeijing.userdic()
      paths.extend(config.JCUSERDIC_LOCATIONS)
      paths = filter(_filter, paths)
      paths = paths[:3] # at most 3 dictionaries

      ok = ret.setUserDic(paths)

      def _tidy(path):
        path = os.path.dirname(path)
        d = os.path.basename(path)
        path = os.path.dirname(path)
        dd = os.path.basename(path)
        path = os.path.dirname(path)
        ddd = os.path.basename(path)
        return "* " + '/'.join((ddd, dd))
      if ok:
        dics = '<br/>'.join(imap(_tidy, paths))
        #dics = dics.replace('@Goodboyye','@goodboyye').replace('@Hdgdyl','@好大個的鴨梨').replace('@Zhugeqiu', '@諸葛秋')
        growl.msg('<br/>'.join((
          i18n.tr("Load user-defined dictionaries") + ":",
          dics
        )))
      else:
        dics = '<br/>'.join(imap(_tidy, jbeijing.userdic()))
        growl.error('<br/>'.join((
          i18n.tr("Failed to load user-defined dictionaries") + ":",
          dics
        )))
    else:
      growl.error(i18n.tr("Cannot load {0} for machine translation. Please check Preferences/Location").format(i18n.tr("JBeijing")))
    return ret

  def warmup(self):
    """@reimp"""
    self.engine.warmup()

  def translate(self, text, to='zhs', fr='ja', async=False):
    """@reimp"""
    if fr != 'ja':
      return None, None, None
    simplified = to == 'zhs'
    to = 'zhs' if simplified else 'zht'
    repl = self.cache.get(text)
    if repl:
      return repl, to, self.key
    #with SkProfiler():
    repl = self._escapeText(text, to=to)
    if repl:
      repl = repl.replace('\n', ' ') # JBeijing cannot handle multiple lines
      try:
        #with SkProfiler():
        repl = self._translate(repl, self.engine.translate, async=async, simplified=simplified)
        if repl:
          repl = wide2thin_digit(repl) # convert wide digits to thin digits
          #with SkProfiler():
          repl = self._unescapeTranslation(repl, to=to)
          self.cache.update(text, repl)
          return repl, to, self.key
      #except RuntimeError, e:
      except Exception, e:
        if self._warned:
          self._warned = True
          dwarn(e)
          if not async:
            growl.error(i18n.tr("Cannot load {0} for machine translation. Please check Preferences/Location").format(i18n.tr("JBeijing")),
                async=async)
    return None, None, None

class FastAITTranslator(OfflineMachineTranslator):
  key = 'fastait' # override

  def __init__(self, **kwargs):
    super(FastAITTranslator, self).__init__(**kwargs)
    self._warned = False # bool
    self._mutex = QMutex()

  @memoizedproperty
  def jazhsEngine(self):
    from kingsoft import fastait
    ret = fastait.create_engine(fr='ja', to='zhs')
    ok = ret.load()
    #import atexit
    #atexit.register(ret.destroy)
    if ok:
      growl.msg(i18n.tr("FastAIT Japanese-Chinese translator is loaded"))
    else:
      growl.error(i18n.tr("Cannot load {0} for machine translation. Please check Preferences/Location").format(mytr_("FastAIT")))
    return ret

  @memoizedproperty
  def jazhtEngine(self):
    from kingsoft import fastait
    ret = fastait.create_engine(fr='ja', to='zht')
    ok = ret.load()
    #import atexit
    #atexit.register(ret.destroy)
    if ok:
      growl.msg(i18n.tr("FastAIT Japanese-Chinese translator is loaded"))
    else:
      growl.error(i18n.tr("Cannot load {0} for machine translation. Please check Preferences/Location").format(mytr_("FastAIT")))
    return ret

  @memoizedproperty
  def enzhsEngine(self):
    from kingsoft import fastait
    ret = fastait.create_engine(fr='en', to='zhs')
    ok = ret.load()
    #import atexit
    #atexit.register(ret.destroy)
    if ok:
      growl.msg(i18n.tr("FastAIT English-Chinese translator is loaded"))
    else:
      growl.error(i18n.tr("Cannot load {0} for machine translation. Please check Preferences/Location").format(mytr_("FastAIT")))
    return ret

  @memoizedproperty
  def enzhtEngine(self):
    from kingsoft import fastait
    ret = fastait.create_engine(fr='en', to='zht')
    ok = ret.load()
    #import atexit
    #atexit.register(ret.destroy)
    if ok:
      growl.msg(i18n.tr("FastAIT English-Chinese translator is loaded"))
    else:
      growl.error(i18n.tr("Cannot load {0} for machine translation. Please check Preferences/Location").format(mytr_("FastAIT")))
    return ret

  @memoizedproperty
  def zhsenEngine(self):
    from kingsoft import fastait
    ret = fastait.create_engine(fr='zhs', to='en')
    ok = ret.load()
    #import atexit
    #atexit.register(ret.destroy)
    if ok:
      growl.msg(i18n.tr("FastAIT Chinese-English translator is loaded"))
    else:
      growl.error(i18n.tr("Cannot load {0} for machine translation. Please check Preferences/Location").format(mytr_("FastAIT")))
    return ret

  @memoizedproperty
  def zhtenEngine(self):
    from kingsoft import fastait
    ret = fastait.create_engine(fr='zht', to='en')
    ok = ret.load()
    #import atexit
    #atexit.register(ret.destroy)
    if ok:
      growl.msg(i18n.tr("FastAIT Chinese-English translator is loaded"))
    else:
      growl.error(i18n.tr("Cannot load {0} for machine translation. Please check Preferences/Location").format(mytr_("FastAIT")))
    return ret

  def getEngine(self, fr, to):
    langs = fr + to
    if langs == 'jazhs':
      return self.jazhsEngine
    elif langs == 'jazht':
      return self.jazhtEngine
    elif langs == 'enzhs':
      return self.enzhsEngine
    elif langs == 'enzht':
      return self.enzhtEngine
    elif langs == 'zhsen':
      return self.zhsenEngine
    elif langs == 'zhten':
      return self.zhtenEngine

  # Ignored
  #def warmup(self):
  #  """@reimp"""
  #  self.ecEngine.warmup()
  #  self.jcEngine.warmup()

  #__fastait_repl_after = staticmethod(skstr.multireplacer({
  #  '[': u'【',
  #  ' ]': u'】',
  #}))
  def translate(self, text, to='zhs', fr='ja', async=False):
    """@reimp"""
    #async = True # force async
    repl = self.cache.get(text)
    if repl:
      return repl, to, self.key
    engine = self.getEngine(fr=fr, to=to)
    if engine:
      repl = self._escapeText(text, to=to)
      if repl:
        try:
          repl = self._translate(repl, partial(self._synchronizedTranslate, engine.translate),
              async=async, to=to, fr=fr)
          if repl:
            #sub = self._applySentenceTransformation(sub)
            #sub = self.__fastait_repl_after(sub)
            #sub = sub.replace(']', u'】')
            repl = self._unescapeTranslation(repl, to=to)
            self.cache.update(text, repl)
            return repl, to, self.key
        #except RuntimeError, e:
        except Exception, e:
          if not self._warned:
            self._warned = True
            dwarn(e) # This might crash colorama TT
            if not async:
              growl.error(i18n.tr("Cannot load {0} for machine translation. Please check Preferences/Location").format(i18n.tr("FastAIT")),
                  async=async)
    return None, None, None

  def _synchronizedTranslate(self, tr, *args, **kwargs):
    self._mutex.lock()
    ret = tr(*args, **kwargs)
    self._mutex.unlock()
    return ret

class DreyeTranslator(OfflineMachineTranslator):
  key = 'dreye' # override

  def __init__(self, **kwargs):
    super(DreyeTranslator, self).__init__(**kwargs)
    self._warned = False # bool

  @memoizedproperty
  def jcEngine(self):
    from dreye import dreyemt
    ret = dreyemt.create_engine('ja')
    ok = ret.load()
    #import atexit
    #atexit.register(ret.destroy)
    if ok:
      growl.msg(i18n.tr("Dr.eye Japanese-Chinese translator is loaded"))
    else:
      growl.error(i18n.tr("Cannot load {0} for machine translation. Please check Preferences/Location").format(i18n.tr("Dr.eye")))
    return ret

  @memoizedproperty
  def ecEngine(self):
    from dreye import dreyemt
    ret = dreyemt.create_engine('en')
    ok = ret.load()
    #import atexit
    #atexit.register(ret.destroy)
    if ok:
      growl.msg(i18n.tr("Dr.eye English-Chinese translator is loaded"))
    else:
      growl.error(i18n.tr("Cannot load {0} for machine translation. Please check Preferences/Location").format(i18n.tr("Dr.eye")))
    return ret

  # Ignored
  #def warmup(self):
  #  """@reimp"""
  #  self.ecEngine.warmup()
  #  self.jcEngine.warmup()

  #__dreye_repl_after = staticmethod(skstr.multireplacer({
  #  '[': u'【',
  #  ' ]': u'】',
  #}))
  def translate(self, text, to='zhs', fr='ja', async=False):
    """@reimp"""
    if fr == 'zht':
      text = zht2zhs(text)
    engine = self.jcEngine if fr == 'ja' else self.ecEngine
    repl = self.cache.get(text)
    if repl:
      return repl, to, self.key
    repl = self._escapeText(text, to=to)
    if repl:
      try:
        repl = self._translate(repl, engine.translate, async=async, to=to, fr=fr)
        if repl:
          if to != 'zhs':
            repl = zhs2zht(repl)
          #sub = self._applySentenceTransformation(sub)
          #sub = self.__dreye_repl_after(sub)
          #sub = sub.replace(']', u'】')
          repl = self._unescapeTranslation(repl, to=to)
          self.cache.update(text, repl)
          return repl, to, self.key
      #except RuntimeError, e:
      except Exception, e:
        if not self._warned:
          self._warned = True
          dwarn(e) # This might crash colorama TT
          if not async:
            growl.error(i18n.tr("Cannot load {0} for machine translation. Please check Preferences/Location").format(i18n.tr("Dr.eye")),
                async=async)
    return None, None, None

## Online

class InfoseekTranslator(OnlineMachineTranslator):
  key = 'infoseek' # override

  def __init__(self, **kwargs):
    super(InfoseekTranslator, self).__init__(**kwargs)
    from transer import infoseek
    infoseek.session = requests.Session()
    self.engine = infoseek

  #__infoseek_repl_after = staticmethod(skstr.multireplacer({
  #  '[': u'【',
  #  ']\n': u'】',
  #}))
  def translate(self, text, to='en', fr='ja', async=False):
    """@reimp"""
    if fr != 'ja':
      return None, None, None
    to = 'en' if to in ('ms', 'ar', 'ru', 'nl', 'pl') else to
    repl = self.cache.get(text)
    if repl:
      return repl, to, self.key
    repl = self._escapeText(text, to=to)
    if repl:
      repl = self._translate(repl, self.engine.translate,
          to=to, fr=fr, async=async)
      if repl:
        repl = self._unescapeTranslation(repl, to=to)
        self.cache.update(text, repl)
    return repl, to, self.key

class ExciteTranslator(OnlineMachineTranslator):
  key = 'excite' # override

  def __init__(self, **kwargs):
    super(ExciteTranslator, self).__init__(**kwargs)
    from excite import worldtrans
    #worldtrans.session = session or requests.Session() # Session is disabled otherwise it will get blocked
    self.engine = worldtrans

  #__excite_repl_after = staticmethod(skstr.multireplacer({
  #  '[': u'【',
  #  ']\n': u'】',
  #}))
  def translate(self, text, to='en', fr='ja', async=False):
    """@reimp"""
    if fr != 'ja':
      return None, None, None
    if to in ('ms', 'id', 'th', 'vi', 'ar', 'nl', 'pl'):
      to = 'en'
    repl = self.cache.get(text)
    if repl:
      return repl, to, self.key
    repl = self._escapeText(text, to=to)
    if repl:
      repl = self._translate(repl, self.engine.translate,
          to=to, fr=fr, async=async)
      if repl:
        repl = self._unescapeTranslation(repl, to=to)
        self.cache.update(text, repl)
    return repl, to, self.key

class LecOnlineTranslator(OnlineMachineTranslator):
  key = 'lecol' # override

  def __init__(self, **kwargs):
    super(LecOnlineTranslator, self).__init__(**kwargs)

    from lec import leconline
    leconline.session = requests.Session()
    self.engine = leconline

  def translate(self, text, to='en', fr='ja', async=False):
    """@reimp"""
    to = 'en' if to in ('ms', 'th', 'vi') else to
    repl = self.cache.get(text)
    if repl:
      return repl, to, self.key
    repl = self._escapeText(text, to=to)
    if repl:
      repl = self._translate(repl, self.engine.translate,
          to=to, fr=fr, async=async)
      if repl:
        repl = self._unescapeTranslation(repl, to=to)
        self.cache.update(text, repl)
    return repl, to, self.key

class TransruTranslator(OnlineMachineTranslator):
  key = 'transru' # override

  def __init__(self, **kwargs):
    super(TransruTranslator, self).__init__(**kwargs)

    from promt import transru
    transru.session = requests.Session()
    self.engine = transru

  def translate(self, text, to='en', fr='ja', async=False):
    """@reimp"""
    to = 'en' if to not in ('ja', 'en', 'ru', 'it', 'fr', 'de', 'pt', 'es') else to
    repl = self.cache.get(text)
    if repl:
      return repl, to, self.key
    repl = self._escapeText(text, to=to)
    if repl:
      repl = self._translate(repl, self.engine.translate,
          to=to, fr=fr, async=async)
      if repl:
        repl = self._unescapeTranslation(repl, to=to)
        self.cache.update(text, repl)
    return repl, to, self.key

class GoogleTranslator(OnlineMachineTranslator):
  key = 'google' # override

  def __init__(self, **kwargs):
    super(GoogleTranslator, self).__init__(**kwargs)

    import googleman
    # Not sure if using session could get blocked by Google
    googleman.setsession(requests.Session())
    self.engine = googleman.manager()

  #__google_repl_after = staticmethod(skstr.multireplacer({
  #  '...': u'…',
  #}))
  def translate(self, text, to='en', fr='ja', async=False):
    """@reimp"""
    repl = self.cache.get(text)
    if repl:
      return repl, to, self.key
    repl = self._escapeText(text, to=to)
    if repl:
      repl = self._translate(repl, self.engine.translate,
          to=to, fr=fr, async=async)
      if repl:
        repl = self._unescapeTranslation(repl, to=to)
        if to.startswith('zh'):
          repl = repl.replace("...", u'…')
        self.cache.update(text, repl)
    return repl, to, self.key

class BingTranslator(OnlineMachineTranslator):
  key = 'bing' # override

  def __init__(self, **kwargs):
    super(BingTranslator, self).__init__(**kwargs)

    # It is dangerous to create engine here, which is async
    from microsoft import bingtrans
    bingtrans.session = requests.Session()

    import bingman
    self.engine = bingman.manager() # time-limited

  #@memoizedproperty
  #def engine(self):
  #  from microsoft import bingtrans
  #  bingtrans.session = requests.Session()
  #  return bingtrans.create_engine()

  #__bing_repl_after = staticmethod(skstr.multireplacer({
  #  '[': u'【',
  #  ']\n': u'】',
  #}))
  __fix_escape = re.compile(r'(?<=[0-9]),(?=[0-9])') # replace ',' between digits with '.'
  def translate(self, text, to='en', fr='ja', async=False):
    """@reimp"""
    #if fr != 'ja':
    #  return None, None, None
    repl = self.cache.get(text)
    if repl:
      return repl, to, self.key
    repl = self._escapeText(text, to=to)
    if repl:
      repl = self._translate(repl, self.engine.translate,
          to=to, fr=fr, async=async)
      if repl:
        #repl = self.__fix_escape.sub('.', repl) # only needed by Shared Dictionary
        repl = self._unescapeTranslation(repl, to=to)
        self.cache.update(text, repl)
    return repl, to, self.key

class BaiduTranslator(OnlineMachineTranslator):
  key = 'baidu' # override

  def __init__(self, **kwargs):
    super(BaiduTranslator, self).__init__(**kwargs)
    from baidu import baidufanyi
    baidufanyi.session = requests.Session()
    self.engine = baidufanyi

  #__baidu_repl_before = staticmethod(skstr.multireplacer({
  #  #u'【': u'‘', # open single quote
  #  #u'】': u'’：', # close single quote
  #  u'「': u'‘“', # open single double quote
  #  u'」': u'”’', # close double single quote
  #  u'『': u'“‘', # open double single quote
  #  u'』': u'’”', # close single double quote

  #}))
  #__baidu_repl_after = staticmethod(skstr.multireplacer({
  #  #u'‘': u'【', # open single quote
  #  #u'’：': u'】', # close single quote
  #  u'‘“': u'「', # open single double quote
  #  u'”’': u'」', # close double single quote
  #  u'“‘': u'『', # open double single quote
  #  u'’”': u'』', # close single double quote
  #}))
  def translate(self, text, to='zhs', fr='ja', async=False):
    """@reimp"""
    #if fr not in ('ja', 'en', 'zhs', 'zht'):
    #  return None, None, None
    #if lang not in ('zhs', 'zht', 'ja', 'en'):
    #  return None, None, None
    repl = self.cache.get(text)
    if repl:
      return repl, to, self.key
    repl = self._escapeText(text, to=to)
    if repl:
      #repl = self.__baidu_repl_before(repl)
      repl = self._translate(repl, self.engine.translate,
          to=to, fr=fr, async=async)
      if repl:
        #if to == 'zht':
        #  repl = zhs2zht(repl)
        #repl = self.__baidu_repl_after(repl)
        repl = self._unescapeTranslation(repl, to=to)
        self.cache.update(text, repl)
    return repl, to, self.key

# EOF
