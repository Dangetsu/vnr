# coding: utf8
# trman.py
# 10/8/2012 jichi
#
# Terminology:
# - data: raw game text byte code
# - text: original game text
# - translation: machine translation
# - comment: user's subtitle or comment

import itertools
from functools import partial
from PySide.QtCore import QObject, Signal, Slot, Qt
from sakurakit import skthreads
from sakurakit.skclass import memoized, memoizedproperty
from sakurakit.skdebug import dprint, dwarn
import textutil
import _trman

#@Q_Q
class _TranslatorManager(object):

  def __init__(self, abortSignal):
    self.abortSignal = abortSignal # Signal

    #self.convertsChinese = False
    #self.enabled = True
    self.online = True

    self.infoseekEnabled = \
    self.exciteEnabled = \
    self.bingEnabled = \
    self.googleEnabled = \
    self.baiduEnabled = \
    self.lecOnlineEnabled = \
    self.transruEnabled = \
    self.hanVietEnabled = \
    self.jbeijingEnabled = \
    self.fastaitEnabled = \
    self.dreyeEnabled = \
    self.ezTransEnabled = \
    self.atlasEnabled = \
    self.lecEnabled = \
    True # bool

  normalizeText = staticmethod(textutil.normalizepunct)

  @memoizedproperty
  def hanVietTranslator(self): return _trman.HanVietTranslator()

  @memoizedproperty
  def atlasTranslator(self): return _trman.AtlasTranslator()

  @memoizedproperty
  def lecTranslator(self): return _trman.LecTranslator()

  @memoizedproperty
  def ezTranslator(self): return _trman.EzTranslator()

  @memoizedproperty
  def fastaitTranslator(self): return _trman.FastAITTranslator()

  @memoizedproperty
  def dreyeTranslator(self): return _trman.DreyeTranslator()

  @memoizedproperty
  def jbeijingTranslator(self): return _trman.JBeijingTranslator()

  @memoizedproperty
  def baiduTranslator(self):
    return _trman.BaiduTranslator(abortSignal=self.abortSignal)

  @memoizedproperty
  def googleTranslator(self):
    return _trman.GoogleTranslator(abortSignal=self.abortSignal)

  @memoizedproperty
  def bingTranslator(self):
    return _trman.BingTranslator(abortSignal=self.abortSignal)

  @memoizedproperty
  def lecOnlineTranslator(self):
    return _trman.LecOnlineTranslator(abortSignal=self.abortSignal)

  @memoizedproperty
  def transruTranslator(self):
    return _trman.TransruTranslator(abortSignal=self.abortSignal)

  @memoizedproperty
  def infoseekTranslator(self):
    return _trman.InfoseekTranslator(abortSignal=self.abortSignal)

  @memoizedproperty
  def exciteTranslator(self):
    return _trman.ExciteTranslator(abortSignal=self.abortSignal)

  def getTranslator(self, key):
    """
    @param  key  str
    @return  TranslatorEngine or None
    """
    if key == 'eztrans':
      return self.ezTranslator
    if key == 'lecol':
      return self.lecOnlineTranslator
    if key == 'transru':
      return self.transruTranslator
    if key == 'hanviet':
      return self.hanVietTranslator
    try: return getattr(self, key + 'Translator')
    except AttributeError: pass

  def iterOfflineTranslators(self):
    """
    @yield  Translator
    """
    if self.jbeijingEnabled: yield self.jbeijingTranslator
    if self.fastaitEnabled: yield self.fastaitTranslator
    if self.dreyeEnabled: yield self.dreyeTranslator
    if self.ezTransEnabled: yield self.ezTranslator
    if self.hanVietEnabled: yield self.hanVietTranslator
    if self.lecEnabled: yield self.lecTranslator
    if self.atlasEnabled: yield self.atlasTranslator

  def iterOnlineTranslators(self):
    """Iterate reversely
    @yield  Translator
    """
    if self.online:
      if self.baiduEnabled: yield self.baiduTranslator
      if self.bingEnabled: yield self.bingTranslator
      if self.googleEnabled: yield self.googleTranslator
      if self.transruEnabled: yield self.transruTranslator
      if self.lecOnlineEnabled: yield self.lecOnlineTranslator
      if self.exciteEnabled: yield self.exciteTranslator
      if self.infoseekEnabled: yield self.infoseekTranslator

  def iterTranslators(self):
    """
    @yield  Translator
    """
    return itertools.chain(self.iterOfflineTranslators(), self.iterOnlineTranslators())

class TranslatorManager(QObject):

  ## Construction ##

  def __init__(self, parent=None):
    super(TranslatorManager, self).__init__(parent)
    self.__d = _TranslatorManager(abortSignal=self.onlineAbortionRequested)

  ## Signals ##

  onlineAbortionRequested = Signal()
  #infoseekAbortionRequested = Signal()
  #bingAbortionRequested = Signal()
  #baiduAbortionRequested = Signal()

  def abortOnline(self):
    self.onlineAbortionRequested.emit()
    #for sig in self.infoseekAbortionRequested, self.bingAbortionRequested, self.baiduAbortionRequested:
    #  sig.emit()

  def clearCache(self):
    for it in self.__d.iterTranslators():
      it.clearCache()
    dprint("pass")

  ## Properties ##

  #def isEnabled(self): return self.__d.enabled
  #def setEnabled(self, t): self.__d.enabled = t

  def language(self): return self.__d.language
  def setLanguage(self, value): self.__d.language = value

  def isOnline(self): return self.__d.online
  def setOnline(self, value): self.__d.online = value

  def isInfoseekEnabled(self): return self.__d.infoseekEnabled
  def setInfoseekEnabled(self, value): self.__d.infoseekEnabled = value

  def isExciteEnabled(self): return self.__d.exciteEnabled
  def setExciteEnabled(self, value): self.__d.exciteEnabled = value

  def isGoogleEnabled(self): return self.__d.googleEnabled
  def setGoogleEnabled(self, value): self.__d.googleEnabled = value

  def isBingEnabled(self): return self.__d.bingEnabled
  def setBingEnabled(self, value): self.__d.bingEnabled = value

  def isBaiduEnabled(self): return self.__d.baiduEnabled
  def setBaiduEnabled(self, value): self.__d.baiduEnabled = value

  def isLecOnlineEnabled(self): return self.__d.lecOnlineEnabled
  def setLecOnlineEnabled(self, value): self.__d.lecOnlineEnabled = value

  def isTransruEnabled(self): return self.__d.transruEnabled
  def setTransruEnabled(self, value): self.__d.transruEnabled = value

  def isHanVietEnabled(self): return self.__d.hanVietEnabled
  def setHanVietEnabled(self, value): self.__d.hanVietEnabled = value

  def isJBeijingEnabled(self): return self.__d.jbeijingEnabled
  def setJBeijingEnabled(self, value): self.__d.jbeijingEnabled = value

  def isDreyeEnabled(self): return self.__d.dreyeEnabled
  def setDreyeEnabled(self, value): self.__d.dreyeEnabled = value

  def isFastaitEnabled(self): return self.__d.fastaitEnabled
  def setFastaitEnabled(self, value): self.__d.fastaitEnabled = value

  def isEzTransEnabled(self): return self.__d.ezTransEnabled
  def setEzTransEnabled(self, value): self.__d.ezTransEnabled = value

  def isLecEnabled(self): return self.__d.lecEnabled
  def setLecEnabled(self, value): self.__d.lecEnabled = value

  def isAtlasEnabled(self): return self.__d.atlasEnabled
  def setAtlasEnabled(self, value): self.__d.atlasEnabled = value

  ## Queries ##

  def warmup(self):
    for it in self.__d.iterOfflineTranslators():
      dprint("warm up %s" % it.key)
      it.warmup()

  def hasOnlineTranslators(self):
    """
    @return  bool
    """
    d = self.__d
    return any((
      d.baiduEnabled,
      d.googleEnabled,
      d.bingEnabled,
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
      d.hanVietEnabled,
      d.jbeijingEnabled,
      d.fastaitEnabled,
      d.dreyeEnabled,
      d.ezTransEnabled,
      d.lecEnabled,
      d.atlasEnabled,
    ))

  def hasTranslators(self):
    """
    @return  bool
    """
    return self.hasOnlineTranslators() or self.hasOfflineTranslators()

  #def isAvailable(self): return self.hasTranslators()
  def isAvailable(self): return True # always available

  def enabledEngines(self): # -> [str]
    d = self.__d
    r = []
    if d.hanVietEnabled: r.append('hanviet')
    if d.jbeijingEnabled: r.append('jbeijing')
    if d.fastaitEnabled: r.append('fastait')
    if d.dreyeEnabled: r.append('dreye')
    if d.ezTransEnabled: r.append('eztrans')
    if d.lecEnabled: r.append('lec')
    if d.atlasEnabled: r.append('atlas')

    if d.baiduEnabled: r.append('baidu')
    if d.googleEnabled: r.append('google')
    if d.bingEnabled: r.append('bing')
    if d.lecOnlineEnabled: r.append('lecol')
    if d.transruEnabled: r.append('transru')
    if d.infoseekEnabled: r.append('infoseek')
    if d.exciteEnabled: r.append('excite')
    return r

  def translate(self, text, fr='ja', to='en', engine='', async=False, cached=True):
    """Translate using any translator
    @param  text  unicode
    @param  fr  unicode  language
    @param  to  unicode  language
    @param  async  bool
    @param  cached  bool  NOT USED, always cached
    @return  unicode sub or None, unicode lang, unicode provider
    """
    d = self.__d
    if not text: # or not d.enabled:
      return None, None, None
    text = d.normalizeText(text)
    if engine:
      e = d.getTranslator(engine)
      if e:
        return e.translate(text, fr=fr, to=to, async=async)
      dwarn("invalid translator: %s" % engine)
    for it in d.iterOfflineTranslators():
      return it.translate(text, fr=fr, to=to, async=async)
    for it in d.iterOnlineTranslators():
      #return it.translate(text, fr=fr, to=to, async=True)
      return skthreads.runsync(partial(
        it.translate, text, fr=fr, to=to, async=False),
        abortSignal=self.onlineAbortionRequested,
      ) or (None, None, None)
    return None, None, None

@memoized
def manager(): return TranslatorManager()

#def translate(*args, **kwargs):
#  return manager().translate(*args, **kwargs)

# EOF

#class YakuCoffeeBean(QObject):
#  def __init__(self, parent=None):
#    super(YakuCoffeeBean, self).__init__(parent)
#
#  @Slot(result=bool)
#  def enabled(self):
#    return manager().isEnabled()
#
#  @Slot(unicode, result=unicode)
#  def yaku(self, t):
#    """
#    @param  t  unicode
#    @return  unicode
#    """
#    return manager().translate(t, async=True)
