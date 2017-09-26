# coding: utf8
# textman.py
# 10/8/2012 jichi
#
# Terminology:
# - data: raw game text byte code
# - text: original game text
# - translation: machine translation
# - comment: user's subtitle or comment

from sakurakit.skprof import SkProfiler

from ctypes import c_longlong
from functools import partial
from PySide.QtCore import Signal, Slot, Property, QObject, QTimer
from sakurakit import skclip, skdatetime, skevents
from sakurakit.skclass import Q_Q, memoized
from sakurakit.skdebug import dwarn
#from sakurakit.skqml import QmlObject
#from sakurakit.skunicode import u
from memcache.container import SizeLimitedList
from convutil import zhs2zht
from janovp import janovdef, janovutil
from mytr import my
from texthook import texthook
import config, dataman, defs, features, growl, hashutil, i18n, settings, termman, textutil, trman, ttsman

from sakurakit import skos
DEBUG = skos.MAC

# Must be consistent with the server-side (SUPER_USER_IDS in api/views.py)
SUPER_USER_IDS = frozenset((
  2,
))

FIX_OLD_SUBS = False # whether fix the hashes and contexts for old annotations

## Helpers ##

IGNORED_THREAD_TYPE = defs.UNKNOWN_TEXT_ROLE
SCENARIO_THREAD_TYPE = defs.SCENARIO_TEXT_ROLE
NAME_THREAD_TYPE = defs.NAME_TEXT_ROLE
OTHER_THREAD_TYPE = defs.OTHER_TEXT_ROLE

class TextThread:
  MAX_DATA_COUNT = 5 # number of data to keep

  def __init__(self, signature=0, name="", data=None, type=IGNORED_THREAD_TYPE):
    """
    @param  signature  long
    @param  name  str
    @param  type  int
    @param  data  [bytearray] or None
    """
    self.name = name            # str
    self.type = type            # int
    self.signature = signature  # long
    self.data = data if data is not None else [] # [bytearray] not None

  def appendData(self, data):
    if len(self.data) >= TextThread.MAX_DATA_COUNT:
      self.data = self.data[1:]
    self.data.append(data)

CONTEXT_CAPACITY = 4 # max number of context to hash

@Q_Q
class _TextManager(object):

  def __init__(self, q):
    t = self._flushAgentScenarioTimer = QTimer(q)
    t.setSingleShot(True)
    t.timeout.connect(self._flushAgentScenario)

    #t = self._flushAgentNameTimer = QTimer(q)
    #t.setSingleShot(True)
    #t.timeout.connect(self._flushAgentName)

    t = self._speakTextTimer = QTimer(q)
    t.setSingleShot(True)
    t.timeout.connect(self._speakText)

    t = self._speakSubtitleTimer = QTimer(q)
    t.setSingleShot(True)
    t.timeout.connect(self._speakSubtitle)

    self.gameTextCapacity = 100 # int

    self.online = False
    self.enabled = True
    self.language = 'en' # str, user language
    self.gameLanguage = 'ja' # str, game language
    #self.locked = False
    self.encoding = 'shift-jis' # str
    self.contextSizeHint = 0 # int

    self.reset()

    #q.rawTextReceived.connect(self._updateTtsText)
    q.nameTextReceived.connect(self._updateTtsName)

    self.blockedLanguages = '' # str

  def reset(self):
    self.agentScenarioBuffer = [] # [unicode scenario text]
    self.agentNameBuffer = '' # unicode

    self.ttsName = "" # unicode not None, character name
    self.ttsNameForSubtitle = "" # unicode, ttsName for subtitle
    self.ttsText = "" # unicode, game text, might be reset
    self.lastTtsText = "" # unicode, current game text
    self.ttsSubtitle = "" # unicode not None, either subtitle or translation
    self.ttsSubtitleLanguage = "" # str not None
    self.lastTtsSubtitle = "" # unicode, current translation
    self.lastTtsSubtitleLanguage = "" # str not None

    self.removesRepeat = False # bool
    self.keepsThreads = False # bool

    self.threads = {} # {long signature:TextThread}, threads history indexed by signature
    self.scenarioSignature = 0
    self.scenarioThreadName = "" # str
    self.nameSignature = 0
    self.otherSignatures = set() # [long signature]
    self.resetTexts()
    self.resetHashes()
    self.resetWindowTexts()
    self.resetWindowTranslation()

  def resetTexts(self):
    #self.texts = [] # [string], list of recent text only from current thread
    if hasattr(self, 'texts'):
      del self.texts[:] # keep the references
    else:
      self.texts = SizeLimitedList()
      self.texts.maxsize = 30

  def resetHashes(self):
    self.hashes = [0] * CONTEXT_CAPACITY # [long], context hashes, no more than CONTEXT_CAPACITY
    self.hashes2 = [0] * CONTEXT_CAPACITY # [long], context hashes, no more than CONTEXT_CAPACITY
    if FIX_OLD_SUBS:
      self.oldHashes = [0] * CONTEXT_CAPACITY

  def resetWindowTexts(self):
    self.windowTexts = {} # {long hash:unicode text}

  def resetWindowTranslation(self):
    self.windowTranslation = {} # {long hash:unicode text}

  def updateThread(self, signature, name, type=IGNORED_THREAD_TYPE):
    try:
      t = self.threads[signature]
      t.type = type
      if not t.name:
        t.name = name
    except KeyError:
      self.threads[signature] = TextThread(name=name, signature=signature, type=type)

  def _iterThreadSignature(self):
    """
    @yield  int  signature
    """
    if self.scenarioSignature:
      yield self.scenarioSignature
    if self.nameSignature:
      yield self.nameSignature
    if self.otherSignatures:
      for it in self.otherSignatures:
        yield it

  def invalidWhitelist(self):
    texthook.global_().setWhitelist(
        list(self._iterThreadSignature()))

  def suggestedContextSize(self):
    """
    @return  0 or 1 or 2 or 3 or 4  Find the first text in the context who has no less than 30 characters
    """
    THRESHOLD = 14
    n = len(self.texts)
    if n == 0:
      return 0
    if n == 1 or len(self.texts[-1]) >= THRESHOLD:
      return 1
    if n == 2 or len(self.texts[-2]) >= THRESHOLD:
      return 2 if len(self.texts[-2]) < defs.MAX_TEXT_LENGTH else 1
    #if n == 3 or len(self.texts[-3]) >= THRESHOLD:
    #  return 3 if len(self.texts[-3]) < defs.MAX_TEXT_LENGTH else 2
    #return 4 if len(self.texts[-4]) < defs.MAX_TEXT_LENGTH else 3
    return 3 if len(self.texts[-3]) < defs.MAX_TEXT_LENGTH else 2

  def currentContextSize(self):
    """
    @return  0 or 1 or 2 or 3 or 4
    """
    return (self.suggestedContextSize() if not self.contextSizeHint else
        min(len(self.texts), self.contextSizeHint))

  def _updateTtsSubtitle(self, text, language):
    ss = settings.global_()
    if not ss.speaksGameText() or not ss.isSubtitleVoiceEnabled():
      return
    # Speak only the first subtitle, and the language must be matched
    if self.ttsSubtitle or language[:2] != self.language[:2]:
      return
    self.lastTtsSubtitle = self.ttsSubtitle = text
    self.lastTtsSubtitleLanguage = self.ttsSubtitleLanguage = language
    if text and self.ttsNameForSubtitle:
      self._speakSubtitleTimer.start(0)
    else:
      t = 500 if self.nameSignature else 0
      self._speakSubtitleTimer.start(t)

  def _updateTtsText(self, text):
    self.lastTtsText = self.ttsText = text
    ss = settings.global_()
    if not ss.speaksGameText(): #or ss.isSubtitleVoiceEnabled(): subtitle still need tts text to guess character names
      return
    if text and self.ttsName:
      self._speakTextTimer.start(0)
    else:
      t = 500 if self.nameSignature else 0
      self._speakTextTimer.start(t)

  def _updateTtsName(self, text):
    ss = settings.global_()
    if not ss.speaksGameText() or not ss.isVoiceCharacterEnabled():
      return
    self.ttsName = self.ttsNameForSubtitle = text
    #if ss.isSubtitleVoiceEnabled():
    #  if text and self.ttsSubtitle:
    #    self._speakSubtitleTimer.start(0)
    #  else:
    #    self._speakSubtitleTimer.start(1000)
    #else:
    if text and self.ttsText:
      self._speakTextTimer.start(0)
      if ss.isSubtitleVoiceEnabled():
        self._speakSubtitleTimer.start(0)
    else:
      timeout = 1000 # online machine translation latency is lone
      self._speakTextTimer.start(timeout)
      if ss.isSubtitleVoiceEnabled():
        self._speakSubtitleTimer.start(timeout)

  def speakLastTextOrSubtitle(self):
    tm = ttsman.manager()
    lang = tm.defaultEngineLanguage()
    if lang:
      if lang == '*' or lang[:2] == self.gameLanguage[:2]:
        t = self.lastTtsText
        if t:
          tm.stop()
          tm.speak(t, termEnabled=True, language=self.gameLanguage)
          return
      elif lang[:2] == self.lastTtsSubtitleLanguage[:2]:
        t = self.lastTtsSubtitle
        if t:
          tm.stop()
          tm.speak(t, termEnabled=False, language=lang)
          return
    tm.stop()
    #else:
    #  growl.warn(my.tr("No game text"))

  @staticmethod
  def _guessTtsName(text):
    """
    @param  text  unicode
    @return  unicode
    """
    if text:
      ret = janovutil.guess_text_name(text)
      if ret:
        return ret
      if len(text) > 2:
        for q in janovdef.NAME_QUOTES:
          if text[0] == q[0] and text[-1] == q[-1]:
            return '?'

  def _speakText(self):
    text = self.ttsText
    #text = textutil.remove_html_tags(text)
    tm = ttsman.manager()
    ss = settings.global_()
    if text: #and self.gameLanguage == 'ja':
      if not settings.global_().isVoiceCharacterEnabled():
        if not ss.isSubtitleVoiceEnabled():
          lang = tm.defaultEngineLanguage()
          if lang == '*' or lang and lang[:2] == self.gameLanguage[:2]:
            tm.speak(text, termEnabled=True, language=self.gameLanguage)
      else:
        dm = dataman.manager()
        name = self.ttsName
        if not name: #and not self.nameSignature:
          name = self._guessTtsName(text)
        if name:
          name = self._repairText(name) # terms are disabled as language is None
          if name:
            dm.addCharacter(name)
            self.ttsNameForSubtitle = name
        if not ss.isSubtitleVoiceEnabled():
          tm.stop() # this requires that ttsSubtitle always comes after ttsText
          c = dm.queryCharacter(name)
          if c:
            cd = c.d
            if cd.ttsEnabled:
              #lang = tm.getEngineLanguage(eng) # always speak TTS subtitle
              #if lang and (lang == '*' or lang[:2] == self.gameLanguage[:2]) and (name or
              #if (name
              #    #or not text.startswith(u"「") and not text.endswith(u"」")
              #    or dm.currentGame() and dm.currentGame().voiceDefaultEnabled # http://sakuradite.com/topic/170
              #  ): # do not speak if no character name is detected
              eng = cd.ttsEngine or tm.defaultEngine()
              tm.speak(text, termEnabled=True, language=self.gameLanguage, engine=eng, gender=cd.gender)
        #else:
        #  tm.stop()
    self.ttsText = self.ttsName = ""

  def _speakSubtitle(self):
    tm = ttsman.manager()
    text = textutil.remove_html_tags(self.ttsSubtitle)
    if text: #and self.gameLanguage == 'ja':
      if not settings.global_().isVoiceCharacterEnabled():
        lang = tm.defaultEngineLanguage()
        if lang == '*' or lang and lang[:2] == self.ttsSubtitleLanguage[:2]:
          tm.speak(text, termEnabled=True, language=lang)
      else:
        tm.stop()
        dm = dataman.manager()
        name = self.ttsNameForSubtitle
        c = dm.queryCharacter(name)
        if c:
          cd = c.d
          if cd.ttsEnabled:
            #lang = tm.getEngineLanguage(eng) # always speak
            #if lang and (lang == '*' or lang[:2] == self.ttsSubtitleLanguage[:2]) and (name or
            #if (name
            #    #or not text.startswith(u"「") and not text.endswith(u"」")
            #    or dm.currentGame() and dm.currentGame().voiceDefaultEnabled # http://sakuradite.com/topic/170
            #  ): # do not speak if no character name is detected
            eng = cd.ttsEngine or tm.defaultEngine()
            tm.speak(text, termEnabled=True, language=self.ttsSubtitleLanguage, engine=eng, gender=cd.gender)
    self.ttsSubtitle = self.ttsSubtitleLanguage = self.ttsNameForSubtitle = ""

  def _repairText(self, text, to=None, fr=None, context=''):
    """
    @param  text  unicode
    @param  to  unicode
    @param  fr  unicode
    @return  unicode
    """
    # Remove illegal characters before repetition removal.
    text = textutil.remove_illegal_text(text)
    if not text:
      return ''
    if self.removesRepeat:
      text = textutil.remove_repeat_text(text)
      #size = len(text)
      #nochange = len(text) == size
    if fr or to:
      #with SkProfiler(): # 0.046 seconds
      text = termman.manager().applyGameTerms(text, to=to, fr=fr,
          context=context, ignoreIfNotReady=True)
      if not text:
        return ''
    if self.removesRepeat and text: # and nochange:
      t = textutil.remove_repeat_text(text)
      delta = len(text) - len(t)
      if delta > max(1, len(text)/4): # enable only if remove significant repetition
        text = t
    return textutil.remove_repeat_spaces(text).strip()

  def _decodeText(self, data):
    #return qunicode(data, self.encoding)
    return textutil.to_unicode(data, self.encoding)

  def _translateTextAndShow(self, text, time, context=''):
    trman.manager().translateApply(self._showTranslation,
        text, self.gameLanguage, context=context,
        time=time)

  def _showComment(self, c):
    """
    @param  c  datamanComment
    """
    if not self.blockedLanguages or c.d.language[:2] not in self.blockedLanguages:
      c.init()
      self.q.commentReceived.emit(c)

  def _showSubtitle(self, s):
    """
    @param  s  Subtitle
    """
    if not self.blockedLanguages or s.subLang[:2] not in self.blockedLanguages:
      self.q.subtitleReceived.emit(s.getObject())

  def _showTranslation(self, sub, language, provider, align, time=0):
    """
    @param  sub  unicode
    @param  language  unicode
    @param  provider  unicode
    @param  align  list
    @param* long  time
    """
    #sub = userplugin.revise_translation(sub, language)
    if sub:
      self._onGameSubtitle(sub, language)
      self.q.translationReceived.emit(sub, language, provider, align, time)
      self._updateTtsSubtitle(sub, language)

  def _onGameSubtitle(self, sub, language=''):
    """
    @param  sub  unicode
    @param* language  str
    """
    if settings.global_().copiesGameSubtitle():
      sub = textutil.remove_html_tags(sub)
      if sub:
        skclip.settext(sub)

  #def _maximumDataSize(self):
  #  return defs.MAX_REPEAT_DATA_LENGTH if self.removesRepeat else defs.MAX_DATA_LENGTH

  def _flushAgentScenario(self):
    self._flushAgentScenarioTimer.stop()

    if self.agentNameBuffer:
       self._flushAgentName()

    if self.agentScenarioBuffer:
      text = ''.join(self.agentScenarioBuffer)
      self.agentScenarioBuffer = []
      self.showScenarioText(text=text, agent=True)

  def _cancelAgentScenario(self):
    self._flushAgentScenarioTimer.stop()
    self.agentNameBuffer = ''
    self.agentScenarioBuffer = []

  def _flushAgentName(self):
    #self._flushAgentNameTimer.stop()
    if self.agentNameBuffer:
      self.showNameText(text=self.agentNameBuffer, agent=True)
      self.agentNameBuffer = ''

  #def _cancelAgentName(self):
  #  self._flushAgentNameTimer.stop()
  #  self.agentNameBuffer = ''

  def stopAgentScenarioTimer(self):
    if self._flushAgentScenarioTimer.isActive():
      self._flushAgentScenarioTimer.stop()

  def addAgentText(self, text, role, needsTranslation=False):
    """
    @param  text  unicode
    @param  role  int
    @param* needsTranslation  bool
    """
    text = textutil.remove_illegal_text(text)
    if role == SCENARIO_THREAD_TYPE:
      #if self.agentNameBuffer:
      #  self._flushAgentName()
      self.agentScenarioBuffer.append(text)
      if sum(map(len, self.agentScenarioBuffer)) > self.gameTextCapacity:
        self._cancelAgentScenario()
      else:
        waitTime = 50 if not needsTranslation else settings.global_().embeddedTranslationWaitTime() / 4
        self._flushAgentScenarioTimer.start(waitTime)
    else:
      # I assumes the name will come before scenario
      # This assumption might hold true for all games.
      if self.agentScenarioBuffer:
        self._flushAgentScenario()
      if role == NAME_THREAD_TYPE:
        #self.showNameText(text=text, agent=True)
        if len(text) > defs.MAX_NAME_THREAD_LENGTH:
          self.agentNameBuffer = ''
        else:
          self.agentNameBuffer = text
        #if len(self.agentNameBuffer) > defs.MAX_NAME_THREAD_LENGTH:
        #  self._cancelAgentName()
        #else:
        #  waitTime = 50 if not needsTranslation else settings.global_().embeddedTranslationWaitTime() * 3 # must be the same as the scenario
        #  self._flushAgentNameTimer.start(waitTime)
    #elif role == OTHER_THREAD_TYPE:
    #  pass

  def querySharedTranslation(self, hash=0, text=''):
    """
    @param* hash  long
    @param* text  unicode
    @return  unicode or None
    """
    dm = dataman.manager()
    if not dm.hasComments():
      return

    lang2 = self.language[:2]

    if text:
      if dm.hasSubtitles():
        h = hashutil.hashcontext(text) #textutil.remove_text_name(text))
        l = dm.querySubtitles(hash=h)
        if l:
          if len(l) > 1:
            for it in l:
              if it.subLang.startswith(lang2):
                return it.text
          return l[0].text

      # Calculate hash2
      h = hashutil.hashcontext(text)
      hashes2 = [h]
      for h in self.hashes2:
        if h:
          hashes2.append(hashutil.hashcontext(text, h))
        else:
          break

      # Hash2 as back up
      for h in hashes2:
        if not h: break
        for c in dm.queryComments(hash2=h):
          cd = c.d
          if not cd.deleted and not cd.disabled and cd.type == 'subtitle' and cd.language.startswith(lang2):
            return cd.text

    rawData = None
    if text and self.encoding:
      try: rawData = textutil.from_unicode(text, self.encoding, errors='strict')
      except UnicodeEncodeError:
        dwarn("cannot extract raw data from text")

    if not rawData and hash:
      for c in dm.queryComments(hash=hash):
        cd = c.d
        if not cd.deleted and not cd.disabled and cd.type == 'subtitle' and cd.language.startswith(lang2):
          return cd.text

    if rawData:
      hashes = [hashutil.strhash(rawData)]
      for h in self.hashes:
        if h:
          hashes.append(hashutil.strhash(rawData, h))
        else:
          break

      for h in hashes:
        if not h: break
        for c in dm.queryComments(hash=h):
          cd = c.d # For performance reason
          if not cd.deleted and not cd.disabled and cd.type == 'subtitle' and cd.language.startswith(lang2): #language_compatible_to(cd.language, lang)
            return cd.text

  def showScenarioText(self, rawData=None, renderedData=None, text=None, agent=True):
    """
    @param* rawData  bytearray
    @param* renderedData  bytearray
    @param* text  unicode
    @param* agent  bool
    """
    if not rawData and text and self.encoding:
      rawData = textutil.from_unicode(text, self.encoding)
    if not rawData:
      growl.warn("%s (%s):<br/>%s" % (
        my.tr("Failed to encode text"), self.encoding, text))
      return
    if renderedData is None:
      renderedData = rawData
    dataSize = len(renderedData)
    if dataSize >= self.gameTextCapacity:
      self.resetHashes()
      dwarn("ignore long text, size = %i" % dataSize)
      growl.msg(my.tr("Game text is ignored for being too long")
          + u" (&gt;%s)" % int(self.gameTextCapacity/2))
      return

    q = self.q

    # Profiler: 1e-5 seconds

    #with SkProfiler():
    if not text:
      text = self._decodeText(renderedData).strip()
    #text = u"「ほら、早く質問に答えないとツンツンしちゃうぞ」"
    #text = u"常人ならば正気を失う魔星の威圧に、しかし怯まず、なお堂々と。"
    #text = u"ゴメン"
    #text = u"オリジナル"
    #text = u"御免なさい"
    #text = u"「ともかく、不信の目は避けねばならん。出来るな？」"
    #text = u"サディステック"
    #text = u"「なにこれ」"
    #text = u"めばえちゃん"
    #text = u"ツナ缶"
    #text = u"秀隆"
    #text = u"ヒミコ様！"
    #text = u"んふふっ♪　そうねー。頑張りましょう"
    #text = u"で、でも"
    #text = u"じゃあ、よろしくね～"
    #text = u"な～に、よろしくね～"
    #text = u"「うん……それにしても、湊の向上心は思ったより高かったんだな。随分とデザインに対してアクティブじゃないか」"
    #text = u"「るみちゃん、めでたい結婚を機にさ、名前変えたら」"
    #text = u"【爽】「悠真くんを攻略すれば２１０円か。なるほどなぁ…」"
    #text += text;
    #text += text;

    if not text:
      return
    if not agent: # only repair text for ITH
      text = self._repairText(text, to=self.language, fr=self.gameLanguage, context='scene')
    if not text:
      #dprint("ignore text")
      return

    if FIX_OLD_SUBS:
      self.oldHashes[1:CONTEXT_CAPACITY] = [
          hashutil.strhash_old_vnr(rawData, h) if h else 0
            for h in self.oldHashes[:CONTEXT_CAPACITY-1]]
      self.oldHashes[0] = hashutil.strhash_old_vnr(rawData)

    # Calculate hash1
    self.hashes[1:CONTEXT_CAPACITY] = [
        hashutil.strhash(rawData, h) if h else 0
          for h in self.hashes[:CONTEXT_CAPACITY-1]]
    self.hashes[0] = hashutil.strhash(rawData)

    # Calculate hash2
    self.hashes2[1:CONTEXT_CAPACITY] = [
        hashutil.hashcontext(text, h) if h else 0
          for h in self.hashes2[:CONTEXT_CAPACITY-1]]
    self.hashes2[0] = hashutil.hashcontext(text)

    self.texts.append(text)
    dm = dataman.manager()
    cur_sz = self.suggestedContextSize()
    if cur_sz:
      cur_hash = self.hashes[cur_sz - 1]
      cur_ctx = defs.CONTEXT_SEP.join(self.texts[-cur_sz:])
      dm.updateContext(cur_hash, cur_ctx)
    else:
      cur_hash = 0

    timestamp = skdatetime.current_unixtime()

    q.pageBreakReceived.emit()

    self._updateTtsText(text)

    # Profiler: 0.05 seconds because of origin term

    #improved_text = self._correctText(text)
    q.textReceived.emit(textutil.beautify_text(text), self.gameLanguage, timestamp)
    sz = self.currentContextSize()
    if sz == cur_sz:
      q.rawTextReceived.emit(text, self.gameLanguage, cur_hash, cur_sz)
    else:
      h = self.hashes[sz - 1]
      ctx = defs.CONTEXT_SEP.join(self.texts[-sz:])
      dm.updateContext(h, ctx)
      q.rawTextReceived.emit(text, self.gameLanguage, h, sz)

    q.contextChanged.emit()

    matched_sub = None # dataman.Subtitle or None
    matched_sub_texts = set() # [unicode]

    #with SkProfiler("query subs"): # jichi 1/11/2015: 0.0007 sec for MuvLuv
    if dm.hasSubtitles():
      h = hashutil.hashcontext(text) #textutil.remove_text_name(text))
      s = dm.queryBestSubtitle(hash=h)
      if s:
        matched_sub = s
        matched_sub_texts.add(s.sub)
        self._showSubtitle(s)
        self._onGameSubtitle(s.text, s.subLang)
        self._updateTtsSubtitle(s.text, s.subLang)

    # Profiler: 1e-4

    #with SkProfiler("query comments"): # jichi 1/11/2015: 0.0003 sec for MuvLuv
    userId = dm.user().id
    if dm.hasComments():
      hitCommentIds = set() # comments that have been shown
      # Hash1 as back up
      for h in self.hashes:
        if not h: break
        for c in dm.queryComments(hash=h):
          cd = c.d # For performance reason
          # 10/1/2013: Automatically recover lost context
          if not cd.context and self.online: #and (cd.userId == userId or userId in SUPER_USER_IDS):
            context = dm.queryContext(h)
            if context:
              c.init()
              c.context = context
            elif cur_sz and (cd.userId == userId or userId in SUPER_USER_IDS):
              c.init()
              c.contextSize = cur_sz
              c.hash = cur_hash
              c.context = cur_ctx
          #if c.contextSize >= h_index +1: # saved context size is larger
          if not cd.deleted and not cd.disabled:
            hitCommentIds.add(cd.id)
            if cd.type == 'subtitle':
              if cd.text in matched_sub_texts or matched_sub and matched_sub.equalSub(cd.text, exact=False):
                continue
              matched_sub_texts.add(cd.text)
            self._showComment(c)
            if cd.type == 'subtitle':
              self._onGameSubtitle(cd.text, cd.language)
              self._updateTtsSubtitle(cd.text, cd.language)

      # Hash2 as back up
      for i,h in enumerate(self.hashes2):
        if not h: break
        for c in dm.queryComments(hash2=h):
          cd = c.d
          if not cd.deleted and not cd.disabled and cd.id not in hitCommentIds:
            hitCommentIds.add(cd.id)
            if cd.type == 'subtitle':
              if cd.text in matched_sub_texts or matched_sub and matched_sub.equalSub(cd.text, exact=False):
                continue
              matched_sub_texts.add(cd.text)
            self._showComment(c)
            if cd.type == 'subtitle':
              self._onGameSubtitle(cd.text, cd.language)
              self._updateTtsSubtitle(cd.text, cd.language)

      if FIX_OLD_SUBS:
        for h_index, h in enumerate(self.oldHashes):
          if h != self.hashes[h_index]:
            for c in dm.queryComments(hash=h):
              if (c.userId == userId or userId in SUPER_USER_IDS) and self.online:
                c.init()
                c.hash = self.hashes[h_index]
                if not c.context:
                  context = dm.queryContext(c.hash)
                  if context:
                    c.context = context
              self._showComment(c)

        h = hashutil.strhash_old_ap(rawData)
        if h != self.oldHashes[0]:
          for c in dm.queryComments(hash=h):
            if (c.d.userId == userId or userId in SUPER_USER_IDS) and self.online:
              c.init()
              c.hash = self.hashes[0]
              if not c.context:
                c.context = text
                #dm.updateContext(c.hash, c.context)
            self._showComment(c)

    # Profiler: 1e-4

    if text:
      if settings.global_().copiesGameText():
        skclip.settext(text)
      # Profiler: 0.35 seconds because of the machine translation
      #with SkProfiler():
      self._translateTextAndShow(text, timestamp, context='scene')

  def showNameText(self, data=None, text=None, agent=True):
    """
    @param* data  bytearray
    @param* text  unicode
    @param* agent  bool
    """
    if not text and data:
      dataSize = len(data)
      if dataSize > defs.MAX_NAME_THREAD_LENGTH:
        dwarn("ignore long name text, size = %i" % dataSize)
        return
      text = self._decodeText(data).strip()
    if not text:
      return
    if not agent:
      text = self._repairText(text, to=self.language, fr=self.gameLanguage, context='name')
      if not text:
        return
    text = textutil.normalize_name(text)
    if not text:
      return

    self.q.nameTextReceived.emit(text, self.gameLanguage)
    self._translateNameAndShow(text)

  def _translateNameAndShow(self, text):
    # Disable translation script for name
    sub, lang, provider = trman.manager().translateOne(text,
        self.gameLanguage, context='name', scriptEnabled=False)
    if sub:
      self.q.nameTranslationReceived.emit(sub, lang, provider)

  def showOtherText(self, data, agent=True):
    """
    @param  data  bytearray
    @param* agent  bool
    """
    dataSize = len(data)
    if dataSize > self.gameTextCapacity:
      dwarn("ignore long text, size = %i" % dataSize)
      return
    q = self.q

    text = self._decodeText(data).strip()
    if text: #and not agent: # always repair text for other text
      text = self._repairText(text, to=self.language, fr=self.gameLanguage, context='other')
    if not text:
      #dprint("no text")
      return

    q.pageBreakReceived.emit()

    dm = dataman.manager()

    h = hashutil.strhash(data)
    timestamp = skdatetime.current_unixtime()
    self._updateTtsText(text)
    #improved_text = self._correctText(text)
    q.textReceived.emit(textutil.beautify_text(text), self.gameLanguage, timestamp)
    dm.updateContext(h, text)
    q.rawTextReceived.emit(text, self.gameLanguage, h, 1) # context size is 1

    if dm.hasSubtitles():
      subs = set()
      h = hashutil.hashcontext(text) #textutil.remove_text_name(text))
      l = dm.querySubtitles(hash=h)
      if l:
        for s in l:
          if s.sub not in subs:
            subs.add(s.sub)
            self._showSubtitle(s)

    if dm.hasComments():
      for c in dm.queryComments(hash=h):
        self._showComment(c)

    if text:
      if settings.global_().copiesGameText():
        skclip.settext(text)
      self._translateTextAndShow(text, timestamp, context='other')

  def showRecognizedText(self, text):
    """
    @param  text  unicode
    """
    if len(text) > self.gameTextCapacity:
      dwarn("ignore long text, size = %i" % dataSize)
      return
    q = self.q

    lang = self.gameLanguage or 'ja'
    #text = self._repairText(text, fr=self.gameLanguage, to=self.language)
    text = termman.manager().applyGameTerms(text, fr=lang)
    if not text:
      return
    text = termman.manager().applyOcrTerms(text, lang)
    if not text:
      return

    q.pageBreakReceived.emit()

    dm = dataman.manager()

    timestamp = skdatetime.current_unixtime()
    self._updateTtsText(text)
    #improved_text = self._correctText(text)
    q.textReceived.emit(textutil.beautify_text(text), lang, timestamp)

    # Making subtitle is currently disabled
    #h = hashutil.strhash(data)
    #dm.updateContext(h, text)
    #q.rawTextReceived.emit(text, self.gameLanguage, h, 1) # context size is 1
    #
    #if dm.hasComments():
    #  for c in dm.queryComments(hash=h):
    #    self._showComment(c)

    #if text
    if settings.global_().copiesGameText():
      skclip.settext(text)
    self._translateTextAndShow(text, timestamp)

  ## Window translation ##

  def updateWindowTranslation(self, verbose=False): # do not growl by default
    if not self.windowTexts:
      return
    if verbose:
      growl.msg(my.tr("Translating window text ..."))
    #if not features.MACHINE_TRANSLATION:
    #  #growl.msg(my.tr("You have disabled machine translation"))
    #  return
    #if not self._hasOfflineTranslator():
    #  #growl.msg(my.tr("You don't have an offline translator enabled. It might take up to five minutes to get the translations T_T"))
    #  pass
    translateOne = trman.manager().translateOne
    changedTranslation = {} # {long hash: unicode text}
    try:
      for h, context in self.windowTexts.iteritems():
        if not h in self.windowTranslation:
          context = textutil.remove_illegal_text(context)
          sub, lang, provider = translateOne(context, self.gameLanguage,
              async=True, online=True, mark=False, rubyEnabled=False, context='window')
          if sub:
            changedTranslation[h] = sub
      if changedTranslation:
        if verbose:
          growl.msg(my.tr("Updating window text ..."))
        self.windowTranslation.update(changedTranslation)
        self.q.windowTranslationChanged.emit(changedTranslation)
      elif verbose:
        growl.msg(my.tr("Not found machine translation"))
    except Exception, e: # this function could raise if the windowTexts is changed by another thread
      dwarn(e)

  #def adjustWindowTranslation(self, trs):
  #  """
  #  @param[in]  trs  {long contextHash:unicode trText}
  #  @return  type(trs)
  #  """
  #  #if not settings.global_().isWindowTextVisible():
  #  #  return trs
  #  ret = {}
  #  for h, t in trs.iteritems():
  #    try:
  #      context = self.windowTexts[h]
  #      if context == t:
  #        ret[h] = context
  #      else:
  #        ret[h] = context + "<" + t
  #    except (KeyError, TypeError):
  #      ret[h] = t
  #  return ret

class TextManager(QObject):

  ## Construction ##

  def __init__(self, parent=None):
    super(TextManager, self).__init__(parent)
    self.__d = _TextManager(self)

  enabledChanged = Signal(bool)
  cleared = Signal()
  pageBreakReceived = Signal()
  contextChanged = Signal()

  textReceived = Signal(unicode, unicode, long)   # text, lang, timestamp
  rawTextReceived = Signal(unicode, unicode, c_longlong, int)   # text, lang, context hash, context size
  translationReceived = Signal(unicode, unicode, unicode, object, long) # text, language, provider, align, timestamp

  commentReceived = Signal(QObject)  # dataman.Comment
  subtitleReceived = Signal(QObject)  # dataman.SubtitleObject

  nameTextReceived = Signal(unicode, unicode)  # text, lang
  nameTranslationReceived = Signal(unicode, unicode, unicode)  # text, lang, provider

  agentTranslationProcessed = Signal(unicode, str, int, str) # text, hash, role, language
  agentTranslationCancelled = Signal(unicode, str, int) # text, hash, role

  #def setMachineTranslator(self, value):
  #  self.__d.preferredMT = value

  def isEnabled(self): return self.__d.enabled
  def setEnabled(self, value):
    d = self.__d
    if d.enabled != value:
      d.enabled = value
      self.enabledChanged.emit(value)

  def userLanguage(self): return self.__d.language
  def setUserLanguage(self, value): self.__d.language = value

  def gameLanguage(self): return self.__d.gameLanguage
  def setGameLanguage(self, value): self.__d.gameLanguage = value

  def gameTextCapacity(self): return self.__d.gameTextCapacity
  def setGameTextCapacity(self, value): self.__d.gameTextCapacity = value

  def blockedLanguages(self): return self.__d.blockedLanguages
  def setBlockedLanguages(self, value): self.__d.blockedLanguages = value

  def isOnline(self): return self.__d.online
  def setOnline(self, value): self.__d.online = value

  def removesRepeatText(self):
    """
    @return  bool
    """
    return self.__d.removesRepeat

  def setRemovesRepeatText(self, value):
    """
    @param  value  bool
    """
    self.__d.removesRepeat = value
    if value:
      growl.notify(my.tr("Eliminate finite repetition in the text"))

  def keepsThreads(self):
    """
    @return  bool
    """
    return self.__d.keepsThreads

  def setKeepsThreads(self, value):
    """
    @param  value  bool
    """
    d = self.__d
    d.keepsThreads = value
    name = d.scenarioThreadName if value else ""
    texthook.global_().setKeptThreadName(name)
    if value and name:
      growl.notify(my.tr("Keep all text threads generated from {0}").format(name))

  def speakCurrentText(self): self.__d.speakLastTextOrSubtitle()

  def recentTexts(self):
    """
    @return  [unicode]  in reverse order
    """
    return self.__d.texts

  def contextSizeHint(self):
    """
    @return  int
    """
    return self.__d.contextSizeHint

  def setContextSizeHint(self, value):
    """
    @param  value  int
    """
    self.__d.contextSizeHint = max(0, min(4, value))

  def contextSize(self):
    """
    @return  int
    """
    return self.__d.currentContextSize()

  def addRecognizedText(self, text):
    """OCR or speech recognition
    @param  text  string
    """
    d = self.__d
    if not d.enabled:
      return
    d.showRecognizedText(text)

  def addIthText(self, rawData, renderedData, signature, name):
    """
    @param  rawData  bytearray
    @param  renderedData  bytearray
    @param  signature  long
    @param  name  str
    """
    d = self.__d
    if not d.enabled:
      return
    #if d.locked:
    #  derror("warning: locked!") # this should never happen
    #  return
    #d.locked = True
    try: thread = d.threads[signature]
    except KeyError:
      if signature == d.scenarioSignature:
        tt = SCENARIO_THREAD_TYPE
      elif d.otherSignatures and signature in d.otherSignatures:
        tt = OTHER_THREAD_TYPE
      else:
        tt = IGNORED_THREAD_TYPE
      thread = d.threads[signature] = TextThread(name=name, signature=signature, type=tt)

    thread.appendData(renderedData)

    if signature == d.nameSignature:
      d.showNameText(data=renderedData, agent=False)
    elif d.otherSignatures and signature in d.otherSignatures:
      d.showOtherText(renderedData, agent=False)
    elif signature == d.scenarioSignature or d.keepsThreads and name == d.scenarioThreadName:
      #with SkProfiler(): # 0.3 seconds
      d.showScenarioText(rawData=rawData, renderedData=renderedData, agent=False)
    #d.locked = False

  def addAgentText(self, text, rawHash, sig, role, needsTranslation):
    """
    @param  text  unicode
    @param  rawHash  str
    @param  sig  long  ITH signature, currently not used
    @param  role  int
    @param  needsTranslation  bool
    """
    d = self.__d
    if not d.enabled:
      return

    if needsTranslation:
      d.stopAgentScenarioTimer()

      sub = None
      if role == SCENARIO_THREAD_TYPE:
        hash = long(rawHash)
        sub = d.querySharedTranslation(hash=hash, text=text)
      lang = d.language
      if not sub:
        async = role == OTHER_THREAD_TYPE
        rubyEnabled = role == SCENARIO_THREAD_TYPE
        engine = settings.global_().embeddedScenarioTranslator() if role == SCENARIO_THREAD_TYPE else ''
        context = defs.thread_role_context(role)
        sub, lang, provider = trman.manager().translateOne(text, d.gameLanguage,
            async=async, online=True, mark=False, keepsNewLine=True, rubyEnabled=rubyEnabled, context=context, engine=engine)
      if sub:
        if lang.startswith('zh'):
          convertsKanji = settings.global_().gameAgentConvertsKanji()
          # Enforce Traditional Chinese encoding
          if convertsKanji:
            if lang == 'zhs':
              sub = zhs2zht(sub)
            from kanjiconv.zhja import zht2ja # this is the only place this library is used
            sub = zht2ja(sub)
        #elif lang == 'zhs' and lang.startswith('zh'):
        #  sub = zht2zhs(sub)
        sub = textutil.remove_html_tags(sub)
        if config.is_reversed_language(lang):
          sub = sub[::-1]
        self.agentTranslationProcessed.emit(sub, rawHash, role, lang)
      else:
        self.agentTranslationCancelled.emit(text, rawHash, role)

    d.addAgentText(text, role, needsTranslation=needsTranslation)

  def encoding(self): return self.__d.encoding
  def setEncoding(self, encoding):
    if encoding:
      self.__d.encoding = encoding
      # Assume this is the only place to modify text encoding in texthook
      texthook.global_().setEncoding(encoding)

  def scenarioThreadSignature(self): return self.__d.scenarioSignature
  def nameThreadSignature(self): return self.__d.nameSignature

  def setScenarioThread(self, signature, name):
    """
    @param  signature  long  non-zero
    @param  name  unicode
    """
    d = self.__d
    if d.scenarioSignature != signature:
      if d.scenarioSignature:
        t = d.threads[d.scenarioSignature]
        if t.type == SCENARIO_THREAD_TYPE:
          t.type = IGNORED_THREAD_TYPE
      d.scenarioSignature = signature
      d.scenarioThreadName = name
      d.updateThread(name=name, signature=signature, type=SCENARIO_THREAD_TYPE)
      if d.keepsThreads:
        texthook.global_().setKeptThreadName(name)

    if d.otherSignatures:
      try: d.otherSignatures.remove(signature)
      except KeyError: pass
    if d.nameSignature == signature:
      t = d.threads[signature]
      if t.type == NAME_THREAD_TYPE:
        t.type = IGNORED_THREAD_TYPE
    d.invalidWhitelist()

  def clearNameThread(self):
    self.setNameThread(0, None)

  def setNameThread(self, signature, name):
    """
    @param  signature  long  could be zero
    @param  name  unicode or None
    """
    d = self.__d
    if d.nameSignature != signature:
      if d.nameSignature:
        t = d.threads[d.nameSignature]
        if t.type == NAME_THREAD_TYPE:
          t.type = IGNORED_THREAD_TYPE
      d.nameSignature = signature
      if signature:
        d.updateThread(name=name, signature=signature, type=NAME_THREAD_TYPE)

    if signature:
      if d.otherSignatures:
        try: d.otherSignatures.remove(signature)
        except KeyError: pass
      if d.scenarioSignature == signature:
        t = d.threads[signature]
        if t.type == SCENE_THREAD_TYPE:
          t.type = IGNORED_THREAD_TYPE
    d.invalidWhitelist()

  def setOtherThreads(self, threads):
    """
    @param  threads  {long signature:str name}
    """
    d = self.__d
    if d.otherSignatures:
      for sig in d.otherSignatures:
        d.threads[sig].type = IGNORED_THREAD_TYPE
      d.otherSignatures.clear()
    for sig, name in threads.iteritems():
      if sig == d.scenarioSignature:
        d.scenarioSignature = 0
      if sig == d.nameSignature:
        d.nameSignature = 0
      d.otherSignatures.add(sig)
      d.updateThread(name=name, signature=sig, type=OTHER_THREAD_TYPE)
    d.invalidWhitelist()

  def scenarioSignature(self):
    """
    @return  long
    """
    return self.__d.scenarioSignature

  def nameSignature(self):
    """
    @return  long
    """
    return self.__d.nameSignature

  def otherSignatures(self):
    """
    @return  set(long signature)
    """
    return self.__d.otherSignatures

  def hasThreads(self):
    return bool(self.__d.threads)

  def threadsBySignature(self):
    """All threads
    @return  {signature:TextThread}
    """
    return self.__d.threads

  def threads(self):
    """
    @yield  TextThread
    """
    return self.__d.threads.itervalues()

  def removeIgnoredThreads(self):
    d = self.__d
    d.threads = {it.signature:it
        for it in d.threads.itervalues()
        if it.type != IGNORED_THREAD_TYPE}

  def clear(self):
    self.__d.reset()
    self.cleared.emit()

  def reload(self):
    growl.msg(my.tr("Reload user-contributed comments"))
    self.cleared.emit()
    self.__d.resetTexts()
    self.__d.resetHashes()

    dm = dataman.manager()
    skevents.runlater(dm.submitDirtyComments, 200)
    skevents.runlater(dm.reloadComments, 500)

    # Secretly update game references
    #skevents.runlater(dm.updateReferences, 1000)

  def confirmReload(self):
    import prompt
    g = dataman.manager().currentGame()
    if prompt.confirmUpdateComments(g):
      self.reload()

  def canSubmit(self):
    return self.__d.currentContextSize() > 0

  def submitComment(self, text, type, locked=False):
    """
    @param  text  unicode
    @param  type  str
    @param  locked  bool
    """
    if not text or not type:
      return
    text = text.strip()
    if not text:
      return
    d = self.__d
    sz = d.currentContextSize()
    if not sz and not DEBUG:
      return

    dm = dataman.manager()

    c = dataman.Comment(
        text = text,
        type = type,
        locked = locked,
        hash = d.hashes[sz-1],
        context = defs.CONTEXT_SEP.join(d.texts[-sz:]),
        contextSize = sz,

        gameId = dm.currentGameId(),
        gameMd5 = dm.currentGameMd5(),
        userId = dm.user().id,
        language = dm.user().language,
        timestamp = skdatetime.current_unixtime())

    dm.updateContext(c.d.hash, c.d.context)

    ok = dataman.manager().submitComment(c)
    if ok or DEBUG:
      self.commentReceived.emit(c)

  ## Window translation ##

  windowTranslationChanged = Signal(dict) # {long hash, unicode text}

  translationCacheCleared = Signal()

  def addWindowTexts(self, texts):
    """
    @param  texts  {long hash, unicode text}
    """
    if not features.MACHINE_TRANSLATION:
      return
    self.__d.windowTexts.update(texts)
    self.__d.updateWindowTranslation()

  def clearWindowTexts(self):
    if not features.MACHINE_TRANSLATION:
      return
    self.__d.resetWindowTexts()
    self.__d.resetWindowTranslation()

  def hasWindowTexts(self):
    return bool(self.__d.windowTexts)

  def clearTranslationCache(self):
    self.__d.resetWindowTranslation()

    self.translationCacheCleared.emit()

  #def refreshWindowTranslation(self):
  #  #self.windowTranslationCleared.emit()
  #  if self.__d.windowTranslation:
  #    self.windowTranslationChanged.emit(self.__d.windowTranslation)

@memoized
def manager(): return TextManager()

## QML plugin ##

@Q_Q
class _TextManagerProxy(object):
  def __init__(self, q):
    q.contextSizeHintChanged.connect(self._updateContextSize)
    manager().textReceived.connect(self._updateContextSize)

  def _updateContextSize(self):
    self.q.contextSizeChanged.emit(
        manager().contextSize())

#@QmlObject
class TextManagerProxy(QObject):
  def __init__(self, parent=None):
    super(TextManagerProxy, self).__init__(parent)
    self.__d = _TextManagerProxy(self)
    manager().enabledChanged.connect(self.enabledChanged)

  enabledChanged = Signal(bool)
  enabled = Property(bool,
      lambda _: manager().isEnabled(),
      lambda _, value: manager().setEnabled(value),
      notify=enabledChanged)

  contextSizeChanged = Signal(int)
  contextSize = Property(int,
      lambda _: manager().contextSize(),
      notify=contextSizeChanged)

  def setContextSizeHint(self, value):
    if value != manager().contextSizeHint():
      manager().setContextSizeHint(value)
      self.contextSizeHintChanged.emit(value)
  contextSizeHintChanged = Signal(int)
  contextSizeHint = Property(int,
      lambda _: manager().contextSizeHint(),
      setContextSizeHint,
      notify=contextSizeHintChanged)

  @Slot(unicode, unicode, bool, result=bool) # text, type
  def submitComment(self, text, type, locked):
    ok = manager().canSubmit() or DEBUG
    if ok:
      skevents.runlater(partial(
        manager().submitComment, text, type=type, locked=locked))
      #skevents.runlater(partial(
      #  manager().submitComment, text, type=type))
    else:
      growl.warn(my.tr("No game text received yet"))
    return ok

  @Slot()
  def reload(self): manager().confirmReload()

  @Slot()
  def speakCurrentText(self): manager().speakCurrentText()

# EOF
